from neo4j import GraphDatabase
import config
import sys
from pathlib import Path

# Add the config directory to sys.path to import the config module
config_dir = Path(__file__).parent.parent / 'config'
sys.path.insert(0, str(config_dir))
from config import get_config

class Neo4jWrapper:
    def __init__(self, uri=None, user=None, password=None):
        # Use centralized config for default values
        self._config = get_config()
        self.uri = uri or self._config.get("neo4j_uri")
        self.user = user or "neo4j"  # Default Neo4j user
        self.password = password or "password"  # Should be overridden via config/env
        self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None, db=None):
        #config.logger.debug(f"Query: {query}")
        assert db is None, "This wrapper does not support multiple databases."
        with self._driver.session(database=db) as session:
            results = list(session.run(query, parameters))
        return results

