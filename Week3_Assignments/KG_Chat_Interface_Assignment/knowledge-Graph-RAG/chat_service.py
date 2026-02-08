# chat_service.py

"""
Knowledge-graph guided reasoning service.
Uses KG as source of truth, LLM for explanation.
"""

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -----------------------------
# Retrieve KG edges
# -----------------------------
async def get_kg_edges(kg_system, question: str):
    if hasattr(kg_system, "query"):
        result = await kg_system.query(question)
    elif hasattr(kg_system, "ask"):
        result = await kg_system.ask(question)
    else:
        return []

    if isinstance(result, list):
        return result

    if isinstance(result, dict) and "edges" in result:
        return result["edges"]

    return []


# -----------------------------
# Convert edges to facts
# -----------------------------
def edges_to_facts(edges):
    facts = []

    for edge in edges[:20]:
        if hasattr(edge, "source_name"):
            facts.append(
                f"{edge.source_name} {edge.name.replace('_', ' ')} {edge.target_name}"
            )
        else:
            facts.append(str(edge))

    return facts


# -----------------------------
# Confidence score
# -----------------------------
def compute_confidence(edge_count):
    if edge_count == 0:
        return 0.4
    if edge_count < 3:
        return 0.6
    if edge_count < 6:
        return 0.75
    return 0.9


# -----------------------------
# Main reasoning function
# -----------------------------
async def ask_kg_question(kg_system, question: str):
    edges = await get_kg_edges(kg_system, question)
    facts = edges_to_facts(edges)

    # Fallback: use architecture text if KG retrieval fails
    if not facts and hasattr(kg_system, "architecture_text"):
        context = kg_system.architecture_text
        confidence = 0.5
    else:
        context = "\n".join(facts)
        confidence = compute_confidence(len(edges))

    if not context:
        return {
            "answer": "I could not find enough information in the architecture.",
            "confidence": 0.0,
        }

    prompt = f"""
You are an architecture assistant.

Answer the user's question using the information below.
The information comes from a knowledge graph built from the architecture.

Do not invent components.
If something is not mentioned, say it is not specified.

Architecture information:
{context}

User question:
{question}

Explain in simple, clear language suitable for non-technical users.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "confidence": confidence,
    }


# -----------------------------
# Architecture validation
# -----------------------------
async def validate_architecture(kg_system):
    edges = await get_kg_edges(kg_system, "architecture")
    facts = edges_to_facts(edges)

    if not facts and hasattr(kg_system, "architecture_text"):
        context = kg_system.architecture_text
    else:
        context = "\n".join(facts)

    if not context:
        return "No architecture data available."

    prompt = f"""
You are a cloud architecture reviewer.

Based on the architecture information below, identify any missing or recommended components.

Focus on:
- Authentication
- Monitoring/logging
- Caching
- Load balancing
- Security layers

Architecture:
{context}

Provide short, practical suggestions.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content
