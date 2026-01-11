from neo4j import GraphDatabase


class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def test_connection(self):
        try:
            self.driver.verify_connectivity()
            return True, "连接成功"
        except Exception as e:
            return False, str(e)

    def execute_cypher(self, queries):
        """
        执行一系列 Cypher 语句
        """
        if not queries:
            return

        with self.driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    print(f"Cypher Error: {e} | Query: {query}")