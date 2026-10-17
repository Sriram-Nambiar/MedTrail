import logging
from typing import List, Dict, Any, Optional
from app.db.neo4j import neo4j_conn

logger = logging.getLogger(__name__)

def get_graph_overview() -> Dict[str, Any]:
    """Retrieve node counts, edge counts, and summary metrics."""
    with neo4j_conn.get_session() as session:
        node_counts = session.run("""
            MATCH (n)
            RETURN labels(n)[0] AS label, count(n) AS count
            ORDER BY count DESC
        """).data()

        rel_counts = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) AS rel_type, count(r) AS count
            ORDER BY count DESC
        """).data()

        total_nodes = sum(item["count"] for item in node_counts)
        total_rels = sum(item["count"] for item in rel_counts)

        return {
            "total_nodes": total_nodes,
            "total_relationships": total_rels,
            "nodes_by_label": {item["label"]: item["count"] for item in node_counts},
            "relationships_by_type": {item["rel_type"]: item["count"] for item in rel_counts}
        }

def find_evidence_paths(disease_id: str = "DIS:IPF", drug_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Traverse multi-hop paths from Disease -> Pathway -> Protein -> Drug -> Study/Paper -> Evidence.
    Preserves exact provenance, evidence direction, and tier.
    """
    with neo4j_conn.get_session() as session:
        query = """
            MATCH (d:Disease {id: $disease_id})
            MATCH (d)-[:ASSOCIATED_WITH]->(g:Gene)-[:ENCODES]->(p:Protein)-[:PARTICIPATES_IN]->(pw:Pathway)
            MATCH (dr:Drug)-[t:TARGETS]->(p)
            WHERE $drug_name IS NULL OR toLower(dr.name) = toLower($drug_name)
            OPTIONAL MATCH (dr)-[:INVESTIGATED_IN]->(cs:ClinicalStudy)-[:REPORTS]->(ev:Evidence)-[:ABOUT]->(d)
            OPTIONAL MATCH (rp:ResearchPaper)-[:SUPPORTS_OR_REPORTS]->(ev)
            RETURN 
                d.name AS disease_name,
                pw.name AS pathway_name,
                g.symbol AS gene_symbol,
                p.accession AS protein_accession,
                p.name AS protein_name,
                dr.name AS drug_name,
                dr.approval_status AS drug_approval,
                t.action_type AS target_action,
                t.affinity_nm AS affinity_nm,
                cs.nct_id AS study_nct_id,
                cs.title AS study_title,
                cs.phase AS study_phase,
                ev.id AS evidence_id,
                ev.tier AS evidence_tier,
                ev.direction AS evidence_direction,
                ev.summary AS evidence_summary,
                ev.limitations AS evidence_limitations,
                rp.pmid AS paper_pmid,
                rp.title AS paper_title
            ORDER BY ev.tier ASC, dr.name ASC
        """
        results = session.run(query, disease_id=disease_id, drug_name=drug_name).data()
        return results

def get_candidate_drugs_with_evidence(disease_id: str = "DIS:IPF") -> List[Dict[str, Any]]:
    """
    Retrieve candidate medicines ranked by transparent evidence-tier ordering rule:
    1. Highest evidence tier (Tier 1 Clinical Trial > Tier 2 Human Observational > Tier 3 Preclinical > Tier 4 Mechanistic)
    2. Conflicting/negative evidence preserved side-by-side
    """
    with neo4j_conn.get_session() as session:
        query = """
            MATCH (d:Disease {id: $disease_id})
            MATCH (dr:Drug)
            OPTIONAL MATCH (dr)-[t:TARGETS]->(p:Protein)<-[:ENCODES]-(g:Gene)<-[:ASSOCIATED_WITH]-(d)
            OPTIONAL MATCH (dr)-[:HAS_EVIDENCE]->(ev:Evidence)-[:ABOUT]->(d)
            OPTIONAL MATCH (dr)-[:ASSOCIATED_WITH_ADVERSE_EVENT]->(se:SideEffect)
            WITH dr, d, 
                 collect(DISTINCT g.symbol) AS targets,
                 collect(DISTINCT {
                     id: ev.id,
                     tier: ev.tier,
                     type: ev.evidence_type,
                     direction: ev.direction,
                     summary: ev.summary,
                     limitations: ev.limitations,
                     source: ev.source
                 }) AS raw_evidence,
                 collect(DISTINCT se.name) AS side_effects
            WHERE size(targets) > 0 OR size(raw_evidence) > 0
            
            // Clean up empty evidence records
            WITH dr, targets, side_effects,
                 [e IN raw_evidence WHERE e.id IS NOT NULL] AS evidence_list
                 
            RETURN 
                dr.id AS drug_id,
                dr.name AS drug_name,
                dr.chembl_id AS chembl_id,
                dr.mechanism AS mechanism,
                dr.approval_status AS approval_status,
                targets,
                side_effects,
                evidence_list,
                size([e IN evidence_list WHERE e.direction = 'supports']) AS supporting_evidence_count,
                size([e IN evidence_list WHERE e.direction = 'no_effect']) AS negative_evidence_count,
                reduce(min_tier = 4, e IN evidence_list | CASE WHEN e.tier < min_tier THEN e.tier ELSE min_tier END) AS best_tier
            ORDER BY best_tier ASC, supporting_evidence_count DESC, dr.name ASC
        """
        results = session.run(query, disease_id=disease_id).data()
        return results

def get_conflicting_evidence_report(disease_id: str = "DIS:IPF") -> List[Dict[str, Any]]:
    """
    Identify drugs with conflicting evidence (e.g. mechanistic/preclinical support vs clinical trial failure).
    """
    with neo4j_conn.get_session() as session:
        query = """
            MATCH (d:Disease {id: $disease_id})
            MATCH (dr:Drug)-[:HAS_EVIDENCE]->(ev:Evidence)-[:ABOUT]->(d)
            WITH dr, collect(ev) AS evidences
            WHERE any(e IN evidences WHERE e.direction = 'supports') 
              AND any(e IN evidences WHERE e.direction IN ['no_effect', 'adverse'])
            RETURN 
                dr.name AS drug_name,
                dr.mechanism AS mechanism,
                [e IN evidences WHERE e.direction = 'supports'] AS supporting_evidence,
                [e IN evidences WHERE e.direction IN ['no_effect', 'adverse']] AS negative_evidence
        """
        results = session.run(query, disease_id=disease_id).data()
        return results

def search_biomedical_entities(search_term: str) -> List[Dict[str, Any]]:
    """Search for entities matching the query term across fulltext indexes and standard names."""
    with neo4j_conn.get_session() as session:
        query = """
            MATCH (n)
            WHERE (n:Disease AND (toLower(n.name) CONTAINS toLower($term) OR any(syn IN n.synonyms WHERE toLower(syn) CONTAINS toLower($term))))
               OR (n:Drug AND (toLower(n.name) CONTAINS toLower($term) OR any(b IN n.brand_names WHERE toLower(b) CONTAINS toLower($term))))
               OR (n:Gene AND (toLower(n.symbol) CONTAINS toLower($term) OR toLower(n.name) CONTAINS toLower($term)))
               OR (n:Pathway AND toLower(n.name) CONTAINS toLower($term))
               OR (n:Protein AND (toLower(n.name) CONTAINS toLower($term) OR toLower(n.accession) CONTAINS toLower($term)))
            RETURN 
                labels(n)[0] AS entity_type,
                n.id AS id,
                coalesce(n.name, n.symbol, n.id) AS name,
                coalesce(n.description, n.mechanism, n.function, n.biological_role, '') AS description
            LIMIT 25
        """
        results = session.run(query, term=search_term).data()
        return results
