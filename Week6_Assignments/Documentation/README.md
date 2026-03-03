# ⚡ PowerGrid AI — Ticket Intelligence & Root Cause Analysis Platform

An enterprise-grade AI Ticket Intelligence Agent for Power & Gas Operations, built with **MCP (Model Context Protocol)**, **RAG (Retrieval-Augmented Generation)**, and **7 autonomous AI tools**.

---

## 🎯 What is PowerGrid AI?

PowerGrid AI is an AI-powered system that analyzes, classifies, and routes support tickets for Power & Gas utility operations in **~15 seconds** with zero manual triage. When a support ticket comes in, the AI Agent autonomously decides which tools to call, performs semantic search against historical tickets, and delivers structured intelligence.

---

## ✨ Key Features

- **AI-Powered Ticket Analysis** — Automatically classifies severity (L1/L2/L3), identifies root cause, and suggests resolution steps
- **MCP Architecture** — 7 specialized tools orchestrated via MCP Server + Client pattern
- **RAG Pipeline** — 50+ historical tickets indexed in Pinecone for semantic similarity search
- **Automated Email Notifications** — Gmail integration sends alerts to recommended teams
- **Google Sheets Logging** — Every analyzed ticket is logged for audit and tracking
- **Regulatory Compliance** — Automatic checks against PHMSA, OSHA, NERC CIP, PUC regulations
- **Enterprise UI** — Professional dark-themed dashboard built with Lovable (React + TypeScript)

---

## 🚀 Quick Start

1. Open the Lovable frontend at the deployed URL
2. Click **"Load Demo Ticket"** or enter your own ticket details
3. Click **"Analyze Ticket"** and wait 15-30 seconds
4. View AI analysis: severity, root cause, resolution steps, similar tickets, recommended team
5. Check your email for automated team notification
6. Check Google Sheets for logged ticket data

---

## 🏗️ Architecture

```
Lovable Frontend (React + TypeScript)
        ↓ POST
n8n Cloud Webhook
        ↓
OpenAI Embeddings (text-embedding-3-small, 1536 dims)
        ↓
Pinecone Vector Search (50+ historical tickets, cosine similarity)
        ↓
AI Agent (GPT-4o-mini) + MCP Client
        ↓
MCP Server Trigger → 7 Tools:
    ├── classify_severity (Code Tool)
    ├── calculate_sla (Code Tool)
    ├── route_escalation (Code Tool)
    ├── check_regulatory_compliance (Code Tool)
    ├── get_current_timestamp (Code Tool)
    ├── Send Team Notification (Gmail)
    └── Logs (Google Sheets)
        ↓
Structured JSON Response → Frontend Display
```

---

## 🛠️ Tech Stack

| Component 		| Technology 					|
|-----------------------|-----------------------------------------------|
| Workflow Engine 	| n8n Cloud (v2.8.3) 				|
| AI Model 		| OpenAI GPT-4o-mini 				|
| Vector Database 	| Pinecone (Serverless, 1536 dims) 		|
| Embeddings 		| OpenAI text-embedding-3-small 		|
| Frontend 		| Lovable (React + TypeScript + Tailwind CSS) 	|
| Email 		| Gmail API via n8n 				|
| Logging 		| Google Sheets API via n8n 			|
| Protocol 		| MCP (Model Context Protocol) Server + Client 	|

---

## 🔧 7 MCP Tools

| # | Tool 				| Type 		| Purpose 									|
|---|-----------------------------------|---------------|-------------------------------------------------------------------------------|
| 1 | `classify_severity` 		| Code Tool 	| Classifies tickets as L1 (Simple), L2 (Technical), or L3 (Critical) 		|
| 2 | `calculate_sla` 			| Code Tool 	| Calculates SLA deadlines: L1=8hrs, L2=24hrs, L3=4hrs 				|
| 3 | `route_escalation` 		| Code Tool 	| Routes to correct team: Engineering, Safety, IT Security, Billing, etc. 	|
| 4 | `check_regulatory_compliance` 	| Code Tool 	| Checks PHMSA, OSHA, NERC CIP, PUC compliance 					|
| 5 | `get_current_timestamp` 		| Code Tool 	| Returns real system timestamp for accurate logging 				|
| 6 | Send Team Notification 		| Gmail Tool 	| Sends HTML email notification to recommended team 				|
| 7 | Logs 				| Google Sheets | Appends ticket data to tracking spreadsheet 					|

---

## 📊 Severity Classification

| Level 		| Description 						| SLA 		| Priority 	|
|-----------------------|-------------------------------------------------------|---------------|---------------|
| **L1** 🟢 		| Known issue, documented fix (billing, config, reset) 	| 8 hours 	| Standard 	|
| **L2** 🟡 		| Requires logs review, configuration analysis 		| 24 hours 	| High 		|
| **L3** 🔴 		| Firmware bug, safety critical, regulatory impact 	| 4 hours 	| Critical 	|
| **Emergency** 🚨 	| Gas leak, explosion, safety incident 			| 1 hour 	| Emergency 	|

---

## 🔍 RAG Pipeline

- **50 historical tickets** indexed in Pinecone vector database
- Each ticket converted to **1536-dimensional vectors** using OpenAI embeddings
- **Cosine similarity** search returns top 5 most relevant historical tickets
- Historical context includes: root cause, resolution steps, severity, category, resolution time
- The AI Agent uses this context to make informed classifications

---

## 🖥️ Frontend (Lovable)

- Dark theme inspired by industrial SCADA/control room interfaces
- Glass-morphism cards with backdrop blur effects
- Real-time KPI dashboard with animated metrics
- Severity color coding with pulse animations
- Circular confidence ring, resolution timeline, similar tickets table
- Fully responsive for mobile and desktop
- https://id-preview--332e398e-4c74-4dee-b876-df949772e4c6.lovable.app/

---

## 📡 MCP (Model Context Protocol)

**MCP Server Trigger** exposes all 7 tools as an MCP-compliant server endpoint. Any MCP-compatible client can discover and call these tools.

**MCP Client** connects the AI Agent to the MCP Server, enabling autonomous tool discovery and execution. The agent decides which tools to call based on ticket context.

This architecture demonstrates true MCP interoperability — the same tools can be consumed by any MCP-compatible AI system.

---

## 📁 Project Structure

```
PowerGrid AI/
├── n8n Workflows/
│   ├── AI Ticket Intelligence Agent (Main workflow)
│   └── power-gas-tickets (Vector DB setup)
├── Pinecone/
│   └── power-gas-tickets index (860+ vectors)
├── Lovable Frontend/
│   └── Power Grid Guardian (React app)
├── Google Sheets/
│   └── PowerGrid AI - Ticket Log
└── Documentation/
    ├── README.md
    └── PowerGrid_AI_Documentation.docx
```

---

## 🔮 Future Enhancements

- Dynamic ticket history upload via frontend
- Predictive maintenance using historical patterns
- SCADA system integration for real-time sensor data
- Slack/Teams notifications
- Auto-resolution for L1 tickets
- Multi-LLM support (GPT-4o, Claude, Gemini)
- White-label SaaS packaging

---

## 👤 Author

**Manjupriyaa** | Social Eagle

---

## 📄 License

This project was built for competition/demonstration purposes.

---

*Powered by AI Ticket Intelligence Agent | n8n + Pinecone + OpenAI | Power & Gas Operations*
