import logging
from typing import List, Dict, Any
from app.db.neo4j import neo4j_conn

logger = logging.getLogger(__name__)

# Primary unique constraints for core entity types
CONSTRAINTS = [
    ("unique_disease_id", "CREATE CONSTRAINT unique_disease_id IF NOT EXISTS FOR (d:Disease) REQUIRE d.id IS UNIQUE"),
    ("unique_gene_id", "CREATE CONSTRAINT unique_gene_id IF NOT EXISTS FOR (g:Gene) REQUIRE g.id IS UNIQUE"),
    ("unique_protein_id", "CREATE CONSTRAINT unique_protein_id IF NOT EXISTS FOR (p:Protein) REQUIRE p.id IS UNIQUE"),
    ("unique_pathway_id", "CREATE CONSTRAINT unique_pathway_id IF NOT EXISTS FOR (pw:Pathway) REQUIRE pw.id IS UNIQUE"),
    ("unique_drug_id", "CREATE CONSTRAINT unique_drug_id IF NOT EXISTS FOR (dr:Drug) REQUIRE dr.id IS UNIQUE"),
    ("unique_clinicalstudy_id", "CREATE CONSTRAINT unique_clinicalstudy_id IF NOT EXISTS FOR (cs:ClinicalStudy) REQUIRE cs.id IS UNIQUE"),
    ("unique_researchpaper_id", "CREATE CONSTRAINT unique_researchpaper_id IF NOT EXISTS FOR (rp:ResearchPaper) REQUIRE rp.id IS UNIQUE"),
    ("unique_sideeffect_id", "CREATE CONSTRAINT unique_sideeffect_id IF NOT EXISTS FOR (se:SideEffect) REQUIRE se.id IS UNIQUE"),
    ("unique_evidence_id", "CREATE CONSTRAINT unique_evidence_id IF NOT EXISTS FOR (ev:Evidence) REQUIRE ev.id IS UNIQUE"),
    ("unique_hypothesis_id", "CREATE CONSTRAINT unique_hypothesis_id IF NOT EXISTS FOR (hyp:Hypothesis) REQUIRE hyp.id IS UNIQUE"),
]

# Lookup indexes on frequent query keys
INDEXES = [
    ("disease_name_idx", "CREATE INDEX disease_name_idx IF NOT EXISTS FOR (d:Disease) ON (d.name)"),
    ("drug_name_idx", "CREATE INDEX drug_name_idx IF NOT EXISTS FOR (d:Drug) ON (d.name)"),
    ("gene_symbol_idx", "CREATE INDEX gene_symbol_idx IF NOT EXISTS FOR (g:Gene) ON (g.symbol)"),
    ("protein_accession_idx", "CREATE INDEX protein_accession_idx IF NOT EXISTS FOR (p:Protein) ON (p.accession)"),
    ("study_nct_idx", "CREATE INDEX study_nct_idx IF NOT EXISTS FOR (cs:ClinicalStudy) ON (cs.nct_id)"),
    ("paper_pmid_idx", "CREATE INDEX paper_pmid_idx IF NOT EXISTS FOR (rp:ResearchPaper) ON (rp.pmid)"),
    ("evidence_tier_idx", "CREATE INDEX evidence_tier_idx IF NOT EXISTS FOR (ev:Evidence) ON (ev.tier)"),
    ("evidence_direction_idx", "CREATE INDEX evidence_direction_idx IF NOT EXISTS FOR (ev:Evidence) ON (ev.direction)"),
]

# Full-text search indexes for entity normalization & fuzzy search
FULLTEXT_INDEXES = [
    ("disease_fulltext", "CREATE FULLTEXT INDEX disease_fulltext IF NOT EXISTS FOR (n:Disease) ON EACH [n.name, n.description]"),
    ("drug_fulltext", "CREATE FULLTEXT INDEX drug_fulltext IF NOT EXISTS FOR (n:Drug) ON EACH [n.name, n.mechanism, n.brand_names]"),
    ("gene_fulltext", "CREATE FULLTEXT INDEX gene_fulltext IF NOT EXISTS FOR (n:Gene) ON EACH [n.symbol, n.name]"),
    ("paper_fulltext", "CREATE FULLTEXT INDEX paper_fulltext IF NOT EXISTS FOR (n:ResearchPaper) ON EACH [n.title, n.abstract]"),
]

def init_schema() -> Dict[str, Any]:
    """Execute schema creation statements against Neo4j."""
    created_constraints = []
    created_indexes = []
    created_fulltext = []

    with neo4j_conn.get_session() as session:
        # Create constraints
        for name, query in CONSTRAINTS:
            try:
                session.run(query).consume()
                created_constraints.append(name)
                logger.info(f"Constraint initialized: {name}")
            except Exception as e:
                logger.warning(f"Constraint {name} note: {e}")

        # Create indexes
        for name, query in INDEXES:
            try:
                session.run(query).consume()
                created_indexes.append(name)
                logger.info(f"Index initialized: {name}")
            except Exception as e:
                logger.warning(f"Index {name} note: {e}")

        # Create fulltext indexes
        for name, query in FULLTEXT_INDEXES:
            try:
                session.run(query).consume()
                created_fulltext.append(name)
                logger.info(f"Fulltext index initialized: {name}")
            except Exception as e:
                logger.warning(f"Fulltext index {name} note: {e}")

    return {
        "constraints": created_constraints,
        "indexes": created_indexes,
        "fulltext_indexes": created_fulltext,
    }

def get_schema_summary() -> Dict[str, Any]:
    """Retrieve existing constraints and indexes."""
    with neo4j_conn.get_session() as session:
        constraints = session.run("SHOW CONSTRAINTS").data()
        indexes = session.run("SHOW INDEXES").data()
        labels = session.run("CALL db.labels()").value()
        rel_types = session.run("CALL db.relationshipTypes()").value()

    return {
        "constraints_count": len(constraints),
        "indexes_count": len(indexes),
        "labels": labels,
        "relationship_types": rel_types,
    }
