import asyncio
from datetime import datetime
from graphiti_core import Graphiti
from config.settings import settings


class KnowledgeGraphRAG:
    def __init__(self):
        self.graphiti = Graphiti(
            settings.NEO4J_URI,
            settings.NEO4J_USERNAME,
            settings.NEO4J_PASSWORD
        )

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    # -------------------------
    # Ingest diagram text
    # -------------------------
    def ingest(self, text: str):
        async def _ingest():
            print("[DEBUG] Ingesting architecture text...")
            await self.graphiti.add_episode(
                name="architecture",
                episode_body=text,
                source_description="uploaded diagram",
                reference_time=datetime.utcnow()
            )
            print("[DEBUG] Ingestion complete.")
            print("--------------------------------------------------")

        self.loop.run_until_complete(_ingest())

    # -------------------------
    # Query KG
    # -------------------------
    def query(self, question: str):
        async def _query():
            print(f"[DEBUG] KG Query: {question}")
            results = await self.graphiti.search(question, num_results=10)
            return results

        results = self.loop.run_until_complete(_query())

        # Convert results to readable text
        cleaned = []
        for r in results:
            try:
                if hasattr(r, "text") and r.text:
                    cleaned.append(r.text.strip())
                elif hasattr(r, "name") and r.name:
                    cleaned.append(str(r.name).strip())
                elif hasattr(r, "content") and r.content:
                    cleaned.append(str(r.content).strip())
            except:
                continue

        print("[DEBUG] Cleaned KG Results:")
        for c in cleaned:
            print("  -", c)
        print("--------------------------------------------------")

        # -------------------------
        # Remove relation-only outputs
        # (like IMPORTS, USES, CREATES)
        # -------------------------
        cleaned = [
            c for c in cleaned
            if len(c.split()) > 2   # keep only meaningful sentences
        ]

        # -------------------------
        # Intelligent filtering
        # -------------------------
        filtered = []
        q = question.lower()

        for r in cleaned:
            rl = r.lower()

            # flow/sending questions
            if any(k in q for k in ["send", "flow", "source", "from"]):
                if any(k in rl for k in ["send", "flow", "import", "create"]):
                    filtered.append(r)

            # creation questions
            elif "create" in q:
                if "create" in rl:
                    filtered.append(r)

            # fallback: keep result
            else:
                filtered.append(r)

        print("[DEBUG] Filtered KG Results:")
        for f in filtered:
            print("  -", f)
        print("--------------------------------------------------")

        return filtered
