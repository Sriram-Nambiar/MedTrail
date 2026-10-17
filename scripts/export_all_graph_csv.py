import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.db.neo4j import neo4j_conn

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "import_files"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def export_all():
    with neo4j_conn.get_session() as session:
        # 1. Fetch all nodes
        nodes = session.run("""
            MATCH (n)
            RETURN 
                n.id AS id,
                labels(n)[0] AS label,
                coalesce(n.name, n.symbol, n.title, n.id) AS name,
                coalesce(n.description, n.mechanism, n.abstract, '') AS description
            ORDER BY label, id
        """).data()
        
        nodes_path = DATA_DIR / "all_ipf_nodes.csv"
        with open(nodes_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "label", "name", "description"])
            writer.writeheader()
            for n in nodes:
                writer.writerow(n)
        print(f"Exported {len(nodes)} nodes to {nodes_path}")

        # 2. Fetch all relationships
        rels = session.run("""
            MATCH (a)-[r]->(b)
            WHERE a.id IS NOT NULL AND b.id IS NOT NULL
            RETURN 
                a.id AS source_id,
                labels(a)[0] AS source_label,
                type(r) AS relationship_type,
                b.id AS target_id,
                labels(b)[0] AS target_label
            ORDER BY relationship_type, source_id
        """).data()
        
        rels_path = DATA_DIR / "all_ipf_relationships.csv"
        with open(rels_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["source_id", "source_label", "relationship_type", "target_id", "target_label"])
            writer.writeheader()
            for r in rels:
                writer.writerow(r)
        print(f"Exported {len(rels)} relationships to {rels_path}")

if __name__ == "__main__":
    export_all()
