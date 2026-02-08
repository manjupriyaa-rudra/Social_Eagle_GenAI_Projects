# Quick Start Guide
-------------------

Get the architecture chat assistant running in under 5 minutes.

---

## Prerequisites
================

Make sure you have:

- Python 3.9 or higher
- Docker installed
- An OpenAI API key

---

## Step 1: Start Neo4j

From the project root:

```bash
docker-compose up -d

# 2. Verify Neo4j is running:

docker ps


# 3. Neo4j should be available at:

Browser: http://localhost:7474

Bolt: localhost:7687

# 4. Step 2: Set Up Python Environment

Create and activate a virtual environment:

python -m venv kgenv
kgenv\Scripts\activate   # Windows


# 5. Install dependencies:

pip install -r requirements.txt

# 6. Step 3: Configure Environment Variables

Edit the .env file in the project root:

OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# 7. Step 4: Launch the Chat Interface

Run the Streamlit app: 
streamlit run streamlit_app.py

Open your browser and go to:
http://localhost:8501

First Run Workflow
Upload an architecture diagram
Enter a diagram name
Click Process Diagram
Wait 30–60 seconds for graph creation
Start chatting with the architecture

Example Questions
===================

Try asking:

      - What is this architecture about?
      - What does the datastore store?
      - Which services depend on authentication?
      - How does data flow from client to backend?
      - What components might be missing?

Stopping the System
====================

Stop Streamlit:
Ctrl + C


Stop Neo4j:
docker-compose down

Troubleshooting
=================
Neo4j not connecting -
   Check if the container is running:
   docker ps

OpenAI API error -   
   Make sure .env contains a valid API key.

Streamlit not loading - 
   Restart the app:
   streamlit run streamlit_app.py