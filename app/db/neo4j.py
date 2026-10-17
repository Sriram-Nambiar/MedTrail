import logging
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
from neo4j import GraphDatabase, Driver, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

class Neo4jConnection:
    _driver: Optional[Driver] = None

    @classmethod
    def get_driver(cls) -> Driver:
        if cls._driver is None:
            logger.info(f"Connecting to Neo4j at {settings.NEO4J_URI}...")
            cls._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
                max_connection_lifetime=30 * 60,
                max_connection_pool_size=50,
                connection_acquisition_timeout=30,
            )
        return cls._driver

    @classmethod
    def close_driver(cls) -> None:
        if cls._driver is not None:
            logger.info("Closing Neo4j driver connection...")
            cls._driver.close()
            cls._driver = None

    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        driver = cls.get_driver()
        session = driver.session(database=settings.NEO4J_DATABASE)
        try:
            yield session
        finally:
            session.close()

    @classmethod
    def check_connection(cls) -> Dict[str, Any]:
        """Verify Neo4j connectivity and return basic metadata."""
        driver = cls.get_driver()
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            try:
                result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] AS version, edition")
                record = result.single()
                if record:
                    return {
                        "connected": True,
                        "uri": settings.NEO4J_URI,
                        "database": settings.NEO4J_DATABASE,
                        "server_name": record.get("name", "Neo4j"),
                        "version": record.get("version", "5.x"),
                        "edition": record.get("edition", "Enterprise (Aura)")
                    }
            except Exception:
                pass

            session.run("RETURN 1").consume()
            return {
                "connected": True,
                "uri": settings.NEO4J_URI,
                "database": settings.NEO4J_DATABASE,
                "server_name": "Neo4j Aura",
                "version": "Cloud",
                "edition": "AuraDB"
            }

neo4j_conn = Neo4jConnection
