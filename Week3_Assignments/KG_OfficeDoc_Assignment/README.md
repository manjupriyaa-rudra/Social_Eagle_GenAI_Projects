# Architecture Knowledge Graph Chat Assistant

An interactive Streamlit-based chat application that converts architecture diagrams into a Knowledge Graph and allows users to ask questions about system flow, dependencies, and components.

## Overview
===========

This project transforms architecture diagrams into a **Knowledge Graph** and enables conversational querying using a chat interface.

### Key Capabilities
====================

- Upload any architecture diagram
- Automatically extract components and relationships
- Build a Knowledge Graph in Neo4j
- Ask natural language questions about the architecture
- Get answers grounded in graph relationships

## Architecture Flow
=======================

User uploads diagram
        ↓
Vision Model → Extract architecture text
        ↓
Knowledge Graph Builder (Graphiti)
        ↓
Neo4j Graph Database
        ↓
Streamlit Chat Interface
        ↓
KG-grounded answers


## Core Components
=====================

| Component | Purpose |
|----------|--------|
| `streamlit_app.py` | Chat interface |
| `diagram_to_text.py` | Image → architecture text |
| `ingest_diagram.py` | Text → Knowledge Graph |
| `chat_service.py` | KG reasoning and answers |
| `knowledge_graph/` | Graph pipeline logic |

## Prerequisites
================

   - Python 3.9+
   - Docker (for Neo4j)
   - OpenAI API key

## Installation
==================

# 1. Clone the project
```bash
cd knowledge-Graph-RAG


#2. Create virtual environment
python -m venv kgenv
kgenv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Neo4j
docker-compose up -d

# 5. Configure environment variables

Edit .env:

OPENAI_API_KEY=your_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# 6. Running the Chat Interface
streamlit run streamlit_app.py

Then open: http://localhost:8501


How It Works
==============

1. Upload an architecture diagram
2. System extracts components and relationships
3. Builds Knowledge Graph
4. Ask questions like:

 - “What does the datastore store?”

 - “How does authentication work?”

 - “Which services communicate with the backend?”

Example Questions
=====================

 - What is this architecture about?

 - Which services interact with the database?

 - What is the data flow from client to storage?

 - What components are missing?

Key Advantages
================

Understands relationships, not just text

Supports multi-hop reasoning

Explains architecture flows

Non-technical users can explore systems