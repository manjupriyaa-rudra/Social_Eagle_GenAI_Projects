import re
from neo4j import GraphDatabase
from config.settings import settings


class FlowBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def build_flow_graph(self, text: str):
        """
        Parse relationships and create proper graph edges.
        """

        send_pattern = r"([A-Za-z0-9/\s]+?) sends data to ([A-Za-z0-9/\s]+)"
        create_pattern = r"([A-Za-z0-9/\s]+?) creates ([A-Za-z0-9/\s]+)"

        send_matches = re.findall(send_pattern, text)
        create_matches = re.findall(create_pattern, text)

        with self.driver.session() as session:

            # SENDS_TO edges (data flow)
            for source, target in send_matches:
                source = source.strip()
                target = target.strip().rstrip(".")

                print(f"[FLOW:SENDS_TO] {source} -> {target}")

                session.run(
                    """
                    MERGE (a:Component {name: $source})
                    MERGE (b:Component {name: $target})
                    MERGE (a)-[:SENDS_TO]->(b)
                    """,
                    source=source,
                    target=target,
                )

            # CREATES edges (orchestration)
            for source, target in create_matches:
                source = source.strip()
                target = target.strip().rstrip(".")

                print(f"[FLOW:CREATES] {source} -> {target}")

                session.run(
                    """
                    MERGE (a:Component {name: $source})
                    MERGE (b:Component {name: $target})
                    MERGE (a)-[:CREATES]->(b)
                    """,
                    source=source,
                    target=target,
                )

