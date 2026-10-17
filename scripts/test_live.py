import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.neo4j import neo4j_conn

def inspect_live_neo4j():
    with neo4j_conn.get_session() as session:
        # Check node count
        total_nodes = session.run("MATCH (n) RETURN count(n) AS cnt").single()["cnt"]
        total_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS cnt").single()["cnt"]
        print(f"Connected to Neo4j Aura instance: {neo4j_conn.check_connection()['uri']}")
        print(f"Database: {neo4j_conn.check_connection()['database']}")
        print(f"Total Nodes: {total_nodes}")
        print(f"Total Relationships: {total_rels}")
        print("-" * 50)

        # Labels
        labels = session.run("CALL db.labels()").value()
        print("Existing Labels:", labels)
        print("-" * 50)

        # Research papers
        papers = session.run("MATCH (p:ResearchPaper) RETURN p.pmid AS pmid, p.title AS title, p.journal AS journal").data()
        print(f"Research Papers in Neo4j ({len(papers)}):")
        for p in papers:
            print(f"  • PMID {p['pmid']}: {p['title']} [{p['journal']}]")
        print("-" * 50)

        # Multi-hop Cypher paths
        print("Sample Cypher Multi-Hop Query:")
        cypher = """
            MATCH path = (d:Disease {name: 'Idiopathic Pulmonary Fibrosis'})-[:ASSOCIATED_WITH]->(g:Gene)
                         -[:ENCODES]->(p:Protein)-[:PARTICIPATES_IN]->(pw:Pathway)
                         <-[:PARTICIPATES_IN]-(p)<-[:TARGETS]-(dr:Drug {name: 'Nintedanib'})
            RETURN g.symbol AS gene, p.name AS protein, pw.name AS pathway, dr.name AS drug
            LIMIT 3
        """
        results = session.run(cypher).data()
        for r in results:
            print(f"  Path: IPF -> {r['pathway']} -> {r['gene']} -> {r['drug']}")

if __name__ == "__main__":
    inspect_live_neo4j()
