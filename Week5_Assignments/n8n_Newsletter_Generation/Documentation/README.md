# 🦅 Social Eagle — AI Newsletter Automation System

An end-to-end automated newsletter generation and delivery system built on **n8n**. Triggered by a Slack message, it researches live news, generates AI-written newsletters, applies dynamic visual design, converts to PDF, and delivers to Slack and/or Gmail — fully automated.

---

## 🚀 How It Works

```
Slack Message
     ↓
Parse Topic + Platforms + Email
     ↓
[Sub-Workflow 1] Info Research & Filtering
  → NewsAPI fetch → Filter Recency → Quality Filter → Remove Duplicates
     ↓
[Sub-Workflow 2] Newsletter Generation & Sending
  → Claude AI generates content
  → JavaScript applies dynamic theme + design
  → PDFShift converts HTML → PDF
  → Routes to Slack and/or Gmail (with PDF attachment)
```

---

## 📁 Repository Structure

```
Social_Eagle/
  ├── workflows/
  │     ├── main-trigger-workflow.json           # Slack trigger + orchestrator
  │     ├── phase2-info-research-filtering.json  # News fetching & filtering
  │     └── phase4-newsletter-generation-sending.json  # AI generation & delivery
  ├── outputs/
  │     ├── sample-newsletter.html               # Sample generated newsletter
  │     └── sample-newsletter.pdf               # Sample PDF output
  ├── docs/
  │     └── project-blueprint.docx              # Full technical blueprint
  └── README.md
```

---

## ⚡ Trigger Format

Send this message in your configured Slack channel:

```
Topic: AI in Real Estate | Platforms: slack, email | Email: user@example.com
```

| Field | Required | Description |
|-------|----------|-------------|
| `Topic` | ✅ | The newsletter subject (e.g. "AI in Healthcare") |
| `Platforms` | ✅ | `slack`, `email`, or `slack, email` |
| `Email` | ✅ if email | Recipient email address |

---

## 🧩 Workflow Details

### Main Workflow
| Node | Purpose |
|------|---------|
| Slack Trigger | Listens for incoming messages |
| Parse Slack Message | Extracts topic, platforms, email |
| Info Research & Filtering | Calls Sub-Workflow 1 |
| Newsletter Generation & Sending | Calls Sub-Workflow 2 |

### Sub-Workflow 1 — Info Research & Filtering
| Node | Purpose |
|------|---------|
| Validate Required Fields | Stops if topic/email/platforms missing |
| NewsAPI | Fetches live articles by topic |
| Filter Recency | Removes outdated articles |
| Quality Filter | Scores and keeps relevant articles |
| Remove Duplicates | Deduplicates by URL/title |
| Merge + Code (JS) | Formats final output with `_meta` stats |

### Sub-Workflow 2 — Newsletter Generation & Sending
| Node | Purpose |
|------|---------|
| Message a Model (Claude) | Generates email HTML + Slack plain text |
| Code in JavaScript (v5.1) | Dynamic theming, images, insight cards |
| HTTP Request (PDFShift) | Converts HTML → PDF binary |
| Platform Categorization | Identifies target platforms |
| Switch | Routes to Slack or Gmail |
| Send a message (Slack) | Posts to Slack channel |
| Merge1 + Gmail | Sends HTML email + PDF attachment |

---

## 🛠️ Tech Stack

| Service | Role |
|---------|------|
| n8n (Self-Hosted v2.8.3) | Workflow automation engine |
| Slack | Trigger + delivery |
| Anthropic Claude | AI content generation |
| NewsAPI | Live news articles |
| PDFShift v3 | HTML to PDF conversion |
| Gmail (OAuth2) | Email delivery |
| Unsplash CDN | Dynamic hero images |

---

## 🔧 Setup & Import

1. Clone this repository
2. Open your n8n instance
3. Go to **Workflows → Import from file**
4. Import in this order:
   - `phase2-info-research-filtering.json`
   - `phase4-newsletter-generation-sending.json`
   - `main-trigger-workflow.json`
5. Set up credentials:
   - Slack Bot Token
   - Anthropic API Key
   - NewsAPI Key
   - PDFShift API Key (Header Auth)
   - Gmail OAuth2
6. Update the Sub-Workflow IDs in the main workflow to match your imported workflows
7. Activate all three workflows
8. Test by sending a trigger message in Slack

---

## 📋 Environment & Credentials Needed

```
SLACK_BOT_TOKEN        → Slack Bot credential in n8n
ANTHROPIC_API_KEY      → Claude AI credential
NEWSAPI_KEY            → NewsAPI credential
PDFSHIFT_API_KEY       → Header Auth credential (key: Authorization)
GMAIL_OAUTH2           → Gmail credential (myGmail)
```

---

## 🐛 Known Issues & Fixes

| Issue | Fix Applied |
|-------|-------------|
| `/tmp` not writable in Docker | Removed file system nodes entirely |
| PDF binary lost after Switch node | Added Merge1 to combine JSON + binary before Gmail |
| No file found on disk read | Eliminated Read/Write File nodes; use binary directly from HTTP Request |

---

## 🔮 Planned Enhancements

- [ ] Multi-topic batching from a single Slack message
- [ ] Google Sheets subscriber list integration
- [ ] Cron-based auto-scheduling (daily/weekly)
- [ ] Analytics tracking with UTM links
- [ ] Custom hero image generation (DALL·E)
- [ ] Multi-language newsletter support

---

## 📄 Documentation

Full technical architecture, data flow diagrams, and node-by-node breakdown available in [`docs/project-blueprint.docx`](docs/project-blueprint.docx)

---

*Built with ❤️ using n8n + Claude AI*
