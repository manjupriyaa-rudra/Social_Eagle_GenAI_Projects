"""Knowledge Graph RAG Pipeline using Graphiti and Neo4j."""

import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI


class KnowledgeGraphRAG:
    """Knowledge Graph-based RAG system using Graphiti."""

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        openai_api_key: str,
        model_name: str = "gpt-4-turbo-preview"
    ):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.openai_api_key = openai_api_key
        self.model_name = model_name

        # Initialize Neo4j driver
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        # Initialize Graphiti
        from graphiti_core.llm_client import OpenAIClient
        from graphiti_core.llm_client.config import LLMConfig

        llm_config = LLMConfig(
            api_key=openai_api_key,
            model=model_name,
            max_tokens=4096
        )
        llm_client = OpenAIClient(config=llm_config)

        self.graphiti = Graphiti(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
            llm_client=llm_client
        )

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=openai_api_key
        )

        print("Knowledge Graph RAG initialized")

    # ---------------------------
    # Confidence Scoring Function
    # ---------------------------
    def calculate_confidence(
        self,
        num_facts: int,
        num_entities: int,
        num_relationships: int,
        answer: str
    ) -> float:
        """
        Confidence scoring that works even when entity extraction is weak.
        """

        confidence = 0.2  # base score

        # Fact strength
        if num_facts >= 8:
            confidence += 0.4
        elif num_facts >= 4:
            confidence += 0.3
        elif num_facts > 0:
            confidence += 0.2

        # Relationship signal
        if num_relationships > 0:
            confidence += 0.2

        # Entity clarity
        if num_entities == 1:
            confidence += 0.2
        elif num_entities > 1:
            confidence += 0.1

        # Clear direct answer pattern
        if "the service" in answer.lower() or "only" in answer.lower():
            confidence += 0.1

        # Clamp
        confidence = max(0.1, min(confidence, 0.95))
        return round(confidence, 2)


    def clear_graph(self) -> None:
        """Clear all nodes and relationships from the graph."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Graph cleared")

    async def add_documents_to_graph(
        self,
        documents: List[str],
        source: str = "api_documentation"
    ) -> None:
        """Add documents to the knowledge graph."""
        print(f"Adding {len(documents)} documents to knowledge graph...")
        start_time = time.time()

        for i, doc in enumerate(documents):
            await self.graphiti.add_episode(
                name=f"{source}_chunk_{i}",
                episode_body=doc,
                source_description=f"Document chunk {i} from {source}",
                reference_time=datetime.now(),
                source=EpisodeType.text
            )

            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(documents)} chunks...")

        build_time = time.time() - start_time
        print(f"Knowledge graph built in {build_time:.2f} seconds")

    async def query(self, question: str, max_facts: int = 10) -> Dict[str, Any]:
        """Query the knowledge graph."""
        print(f"\nQuerying Knowledge Graph: {question}")
        start_time = time.time()

        search_results = await self.graphiti.search(
            query=question,
            num_results=max_facts
        )

        retrieval_time = time.time() - start_time

        facts = []
        entities = []
        relationships = []

        for result in search_results:
            if hasattr(result, 'fact'):
                facts.append(result.fact)
            if hasattr(result, 'content'):
                facts.append(result.content)

            if hasattr(result, 'nodes'):
                for node in result.nodes:
                    if hasattr(node, 'name'):
                        entities.append(node.name)

            if hasattr(result, 'edges'):
                for edge in result.edges:
                    if hasattr(edge, 'fact'):
                        relationships.append(edge.fact)

        context = "\n\n".join(facts) if facts else "No relevant information found."

        # Improved prompt
        generation_start = time.time()
        prompt = f"""You are a knowledge-graph-based assistant answering questions about the system.

Use only the facts below.

Rules:
1. Only use entities and relationships present in the facts.
2. Prefer direct relationships over inferred ones.
3. Do not invent services, databases, or components.
4. If information is missing, say so.

Knowledge Graph Facts:
{context}

Question: {question}

Give a direct answer first, then a short explanation.

Answer:"""

        response = self.llm.invoke(prompt)
        answer = response.content

        generation_time = time.time() - generation_start
        total_time = time.time() - start_time

        num_tokens = len(answer.split())
        num_facts = len(facts)
        num_entities = len(set(entities))
        num_relationships = len(relationships)

        # Calculate confidence
        confidence = self.calculate_confidence(
            num_facts=num_facts,
            num_entities=num_entities,
            num_relationships=num_relationships,
            answer=answer
        )

        print("DEBUG CONFIDENCE:",
            num_facts,
            num_entities,
            num_relationships,
            confidence)



        return {
            "answer": answer,
            "confidence": confidence,
            "facts": facts,
            "entities": list(set(entities)),
            "relationships": relationships,
            "metrics": {
                "query_time": total_time,
                "retrieval_time": retrieval_time,
                "generation_time": generation_time,
                "num_facts": num_facts,
                "num_entities": num_entities,
                "num_relationships": num_relationships,
                "answer_tokens": num_tokens,
                "retrieval_method": "knowledge_graph"
            }
        }

    def get_entity_relationships(self, entity_name: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific entity."""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity {name: $entity_name})-[r]->(target)
            RETURN e.name as source, type(r) as relationship, target.name as target
            UNION
            MATCH (source)-[r]->(e:Entity {name: $entity_name})
            RETURN source.name as source, type(r) as relationship, e.name as target
            """
            result = session.run(query, entity_name=entity_name)
            return [dict(record) for record in result]

    def get_graph_statistics(self) -> Dict[str, int]:
        """Get statistics about the knowledge graph."""
        with self.driver.session() as session:
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            num_nodes = node_result.single()["count"]

            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            num_relationships = rel_result.single()["count"]

            entity_result = session.run("MATCH (n:Entity) RETURN count(n) as count")
            num_entities = entity_result.single()["count"]

            episode_result = session.run("MATCH (n:Episode) RETURN count(n) as count")
            num_episodes = episode_result.single()["count"]

        return {
            "total_nodes": num_nodes,
            "total_relationships": num_relationships,
            "num_entities": num_entities,
            "num_episodes": num_episodes
        }

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        self.driver.close()
        print("Neo4j connection closed")
