1. Create folder strcture
2. Update all files:  python , env & requirement files
3. create and acivate virtual environment
4. Prepare you test data
5. Run your docker and check if ne04j is working
6. Install requirements
7. Run streamlit app
8. Drop a architecture image
9. Click on process diagram button
10. After extraction interact.


---------------------------------------------------------------------------------------------------------------------------------
=====================================
Hybrid KG-RAG Architecture Assistant
=====================================

A Hybrid Knowledge Graph + RAG (Retrieval-Augmented Generation) assistant that understands cloud architecture diagrams and answers questions using a combination of:

    - Knowledge Graph reasoning
    - Hybrid search (keyword + semantic)
    - LLM-based responses

This system extracts architecture flows from diagrams, builds a graph, and enables intelligent question answering.

===============
Key Features
===============

    - Upload architecture diagrams (PNG/JPG)
    - Automatic extraction of components and relationships
    - Knowledge Graph construction using Graphiti + Neo4j
    - Hybrid retrieval (KG + semantic search)
    - LLM-powered answers
    - Result logging for validation and debugging


===============
Installation
===============

1. Clone the project
git clone <repo-url>
cd arch_kg_hybrid

2. Create virtual environment
python -m venv venv
venv\Scripts\activate   (Windows)

3. Install dependencies
pip install -r requirements.txt

4. Set environment variables

Create a .env file:

OPENAI_API_KEY=your_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

5. Start Neo4j (if using Docker)
docker run -d \
  --name neo4j \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j

6. Run the app
streamlit run app.py


Open in browser:

http://localhost:8501

===============
How It Works
===============

Step 1 — Upload Diagram

    User uploads architecture image.

Step 2 — Text Extraction

    Vision model extracts:

        - Components
        - Services
        - Relationships

Step 3 — Knowledge Graph Creation

    Architecture flow is ingested into the graph.

Step 4 — Hybrid Retriever Setup

    Text is indexed for semantic + keyword search.

Step 5 — Ask Questions

    User asks architecture-related queries.

Step 6 — Answer Generation

    System:

        - Queries KG
        - Queries hybrid retriever
        - Sends context to LLM
        - Returns concise answer

=================
Example Questions
=================

KG-based questions:

    1. Which service imports the Product Dataset into BigQuery?
    2. What creates the ML Project Dataset?
    3. Which dataset is used for model training?

Hybrid questions:

    4. Explain the full data flow from source to model training.
    5. What is the role of the ML Project Dataset?

Sample Result Log:
    {
    "question": "Which service imports the Product Dataset into BigQuery?",
    "kg_results": [
        "Cloud Composer imports Product Dataset into BigQuery"
    ],
    "hybrid_results": [],
    "llm_raw_answer": "Cloud Composer imports the Product Dataset into BigQuery.",
    "source": "KG"
    }

=================
Technologies Used
=================

Python
Streamlit
OpenAI API
Neo4j
Graphiti
Hybrid Retrieval (BM25 + embeddings)

===============
Use Cases
===============

Architecture understanding
Cloud system documentation
AI-powered diagram assistants
Enterprise architecture Q&A
Technical onboarding tools

===============
Author
===============

Manjupriyaa Rudra
AI/ML Enthusiast | Hybrid RAG Developer