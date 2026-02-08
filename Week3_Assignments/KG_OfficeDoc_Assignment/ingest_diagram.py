# ingest_diagram.py
import os
from knowledge_graph import KnowledgeGraphRAG


async def ingest_architecture(text: str):
    kg = KnowledgeGraphRAG(
        neo4j_uri=os.getenv("NEO4J_URI"),
        neo4j_user=os.getenv("NEO4J_USERNAME"),
        neo4j_password=os.getenv("NEO4J_PASSWORD"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-4.1-mini"
    )

    await kg.graphiti.build_indices_and_constraints()
    await kg.add_documents_to_graph([text], source="architecture_diagram")

    # store original text for summaries
    kg.architecture_text = text

    return kg
