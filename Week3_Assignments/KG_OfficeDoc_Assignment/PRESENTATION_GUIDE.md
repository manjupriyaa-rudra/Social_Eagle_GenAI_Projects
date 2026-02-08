=================================================================
# Presentation Guide: Architecture Knowledge Graph Chat Assistant
=================================================================

## Presentation Goal
=====================

Demonstrate how architecture diagrams can be turned into an interactive chat assistant powered by a Knowledge Graph.

---

## Pre-Presentation Setup (10 minutes before)
==============================================

# 1. Start Neo4j
```bash
docker-compose up -d

# 2. Start Streamlit
streamlit run streamlit_app.py

Open: http://localhost:8501


-------------------------------------------------------------------------------------------------------------------
===================================
Presentation Flow (15–20 minutes)
===================================

Part 1: Introduction (2 minutes)
===============================

Talking points:

      - Traditional diagrams are static

      - Hard for non-technical users to understand

      - We convert diagrams into an interactive knowledge graph

      - Users can chat with the architecture

Part 2: Upload Diagram (3 minutes)
==================================

   Steps:

      - Upload architecture diagram
      - Click Process Diagram
      - Wait for graph creation

   Explain:

      - Vision model extracts components
      - Graph builder creates nodes and relationships
      - Stored in Neo4j

Part 3: Live Chat Demo (7 minutes)
==================================

   Ask questions:

      - What is this architecture about?
      - Which services communicate with the backend?
      - What does the datastore store?
      - What components might be missing?

   Explain:

      - Answers come from graph relationships
      - Not from text similarity
      - Shows structural understanding

Part 4: Show Graph Thinking (3 minutes)
========================================

   Explain:

      - Each service = node
      - Each connection = relationship
      - System reasons through paths

   Example:

      Client → API → Auth → Database

Part 5: Audience Questions (5 minutes)
======================================

   Let audience ask:

      - How does authentication work?
      - Where is data stored?
      - What depends on the API?

Key Takeaways
==============

   - Diagram becomes a Knowledge Graph
   - Users can chat with architecture
   - System understands relationships
   - Useful for onboarding and documentation

Backup Plan
==============

   If graph build is slow:

      - Use a preprocessed diagram
      - Show chat responses
      - Explain architecture reasoning


---
