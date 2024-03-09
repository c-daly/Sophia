from neo4j import GraphDatabase

class Neo4jWrapper:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None, db=None):
        assert db is None, "This wrapper does not support multiple databases."
        with self._driver.session(database=db) as session:
            results = list(session.run(query, parameters))
        return results

