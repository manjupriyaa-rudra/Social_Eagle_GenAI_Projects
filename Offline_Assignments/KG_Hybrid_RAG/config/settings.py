import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")

    # Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "test1234")

    # App
    MAX_CONTEXT_DOCS = int(os.getenv("MAX_CONTEXT_DOCS", 5))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))


settings = Settings()