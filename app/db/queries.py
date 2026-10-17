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

NODE_COLOR_MAP = {
    "Disease": "#EF4444",       # Red
    "Pathway": "#8B5CF6",       # Purple
    "Gene": "#38BDF8",          # Sky Blue
    "Protein": "#06B6D4",       # Cyan
    "Drug": "#10B981",          # Emerald Green
    "ClinicalStudy": "#F59E0B", # Amber
    "ResearchPaper": "#6366F1", # Indigo
    "Evidence": "#14B8A6",      # Teal
    "SideEffect": "#EC4899",    # Pink
    "Hypothesis": "#F97316",    # Orange
}

NODE_SIZE_MAP = {
    "Disease": 32,
    "Drug": 26,
    "Pathway": 22,
    "Protein": 18,
    "Gene": 16,
    "ClinicalStudy": 18,
    "Evidence": 20,
    "ResearchPaper": 16,
    "SideEffect": 16,
    "Hypothesis": 22,
}

def get_subgraph(drug_name: Optional[str] = None, disease_id: str = "DIS:IPF") -> Dict[str, Any]:
    """
    Retrieve subgraph nodes and links formatted for interactive frontend visualization.
    """
    with neo4j_conn.get_session() as session:
        if drug_name and drug_name.lower() != "all":
            # Targeted subgraph for specific drug exploration path
            query = """
                MATCH (d:Disease {id: $disease_id})
                MATCH (dr:Drug)
                WHERE toLower(dr.name) = toLower($drug_name)
                
                // Targets and pathways
                OPTIONAL MATCH (dr)-[r_tgt:TARGETS]->(p:Protein)<-[r_enc:ENCODES]-(g:Gene)<-[r_assoc:ASSOCIATED_WITH]-(d)
                OPTIONAL MATCH (p)-[r_pw:PARTICIPATES_IN]->(pw:Pathway)
                
                // Studies and Evidence
                OPTIONAL MATCH (dr)-[r_inv:INVESTIGATED_IN]->(cs:ClinicalStudy)-[r_rep:REPORTS]->(ev:Evidence)-[r_abt:ABOUT]->(d)
                OPTIONAL MATCH (dr)-[r_has_ev:HAS_EVIDENCE]->(ev2:Evidence)-[r_abt2:ABOUT]->(d)
                OPTIONAL MATCH (rp:ResearchPaper)-[r_supp:SUPPORTS_OR_REPORTS]->(ev)
                OPTIONAL MATCH (rp2:ResearchPaper)-[r_supp2:SUPPORTS_OR_REPORTS]->(ev2)
                
                // Side effects
                OPTIONAL MATCH (dr)-[r_se:ASSOCIATED_WITH_ADVERSE_EVENT]->(se:SideEffect)
                
                // Hypotheses
                OPTIONAL MATCH (ev)-[r_hyp:SUPPORTS]->(hyp:Hypothesis)
                OPTIONAL MATCH (ev2)-[r_hyp2:SUPPORTS]->(hyp2:Hypothesis)
                
                RETURN 
                    collect(DISTINCT d) AS diseases,
                    collect(DISTINCT dr) AS drugs,
                    collect(DISTINCT p) AS proteins,
                    collect(DISTINCT g) AS genes,
                    collect(DISTINCT pw) AS pathways,
                    collect(DISTINCT cs) AS studies,
                    collect(DISTINCT rp) + collect(DISTINCT rp2) AS papers,
                    collect(DISTINCT ev) + collect(DISTINCT ev2) AS evidences,
                    collect(DISTINCT se) AS side_effects,
                    collect(DISTINCT hyp) + collect(DISTINCT hyp2) AS hypotheses
            """
        else:
            # Full IPF Knowledge Graph
            query = """
                MATCH (d:Disease {id: $disease_id})
                OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(g:Gene)-[:ENCODES]->(p:Protein)-[:PARTICIPATES_IN]->(pw:Pathway)
                OPTIONAL MATCH (dr:Drug)-[:TARGETS]->(p)
                OPTIONAL MATCH (dr)-[:INVESTIGATED_IN]->(cs:ClinicalStudy)-[:REPORTS]->(ev:Evidence)-[:ABOUT]->(d)
                OPTIONAL MATCH (dr)-[:HAS_EVIDENCE]->(ev2:Evidence)-[:ABOUT]->(d)
                OPTIONAL MATCH (rp:ResearchPaper)-[:SUPPORTS_OR_REPORTS]->(ev)
                OPTIONAL MATCH (rp2:ResearchPaper)-[:SUPPORTS_OR_REPORTS]->(ev2)
                OPTIONAL MATCH (dr)-[:ASSOCIATED_WITH_ADVERSE_EVENT]->(se:SideEffect)
                OPTIONAL MATCH (ev)-[:SUPPORTS]->(hyp:Hypothesis)
                OPTIONAL MATCH (ev2)-[:SUPPORTS]->(hyp2:Hypothesis)
                RETURN 
                    collect(DISTINCT d) AS diseases,
                    collect(DISTINCT dr) AS drugs,
                    collect(DISTINCT p) AS proteins,
                    collect(DISTINCT g) AS genes,
                    collect(DISTINCT pw) AS pathways,
                    collect(DISTINCT cs) AS studies,
                    collect(DISTINCT rp) + collect(DISTINCT rp2) AS papers,
                    collect(DISTINCT ev) + collect(DISTINCT ev2) AS evidences,
                    collect(DISTINCT se) AS side_effects,
                    collect(DISTINCT hyp) + collect(DISTINCT hyp2) AS hypotheses
            """

        data = session.run(query, disease_id=disease_id, drug_name=drug_name).single()
        
        nodes_dict = {}
        def add_node(item, label_type):
            if not item or not item.get("id"):
                return
            nid = item["id"]
            if nid not in nodes_dict:
                name = item.get("name") or item.get("symbol") or item.get("title") or nid
                nodes_dict[nid] = {
                    "id": nid,
                    "label": name,
                    "type": label_type,
                    "color": NODE_COLOR_MAP.get(label_type, "#94A3B8"),
                    "size": NODE_SIZE_MAP.get(label_type, 18),
                    "properties": dict(item)
                }

        for d in data["diseases"]: add_node(d, "Disease")
        for dr in data["drugs"]: add_node(dr, "Drug")
        for p in data["proteins"]: add_node(p, "Protein")
        for g in data["genes"]: add_node(g, "Gene")
        for pw in data["pathways"]: add_node(pw, "Pathway")
        for cs in data["studies"]: add_node(cs, "ClinicalStudy")
        for rp in data["papers"]: add_node(rp, "ResearchPaper")
        for ev in data["evidences"]: add_node(ev, "Evidence")
        for se in data["side_effects"]: add_node(se, "SideEffect")
        for hyp in data["hypotheses"]: add_node(hyp, "Hypothesis")

        # Now query all active relationships between these collected nodes
        node_ids = list(nodes_dict.keys())
        rel_query = """
            MATCH (a)-[r]->(b)
            WHERE a.id IN $node_ids AND b.id IN $node_ids
            RETURN DISTINCT 
                elementId(r) AS rel_id,
                a.id AS source,
                b.id AS target,
                type(r) AS type,
                properties(r) AS properties
        """
        rels = session.run(rel_query, node_ids=node_ids).data()
        
        links = []
        for r in rels:
            links.append({
                "id": str(r["rel_id"]),
                "source": r["source"],
                "target": r["target"],
                "type": r["type"],
                "label": r["type"].replace("_", " ").lower(),
                "properties": r["properties"]
            })

        return {
            "nodes": list(nodes_dict.values()),
            "links": links,
            "metrics": {
                "node_count": len(nodes_dict),
                "link_count": len(links),
                "focused_drug": drug_name if drug_name and drug_name.lower() != "all" else "All Candidates"
            }
        }

def get_keyword_vs_graph_comparison() -> Dict[str, Any]:
    """
    Produces the documented comparison between plain keyword lookup and Neo4j multi-hop retrieval.
    """
    return {
        "disease": "Idiopathic Pulmonary Fibrosis (IPF)",
        "scenario_1": {
            "title": "Nintedanib Repurposing Discovery (Oncology -> IPF)",
            "keyword_search": {
                "query": 'PubMed: "Idiopathic Pulmonary Fibrosis" AND "BIBF 1120" (Pre-2008)',
                "direct_results": 0,
                "limitation": "BIBF 1120 was researched as an oncology angiokinase inhibitor. A naive literature keyword search showed no direct co-occurrence with pulmonary fibrosis before clinical development began.",
                "surfaced_path": None
            },
            "graph_retrieval": {
                "query": 'MATCH (d:Disease {name: "IPF"})-[:ASSOCIATED_WITH]->(g)-[:ENCODES]->(p)-[:PARTICIPATES_IN]->(pw)<-[:PARTICIPATES_IN]-(target)<-[:TARGETS]-(dr:Drug)',
                "multi_hop_found": True,
                "hops": 4,
                "chain": [
                    "IPF connects to Receptor Tyrosine Kinase & FGFR/PDGF pathways",
                    "Pathways contain FGFR1, FGFR2, FGFR3, PDGFRA, PDGFRB, and KDR targets",
                    "Nintedanib potently inhibits these exact RTK targets at nanomolar IC50",
                    "Preclinical & Phase 3 INPULSIS trials confirm ~50% slowing of FVC decline"
                ],
                "outcome": "Multi-hop discovery successfully surfaced the indirect biological link through pathway and target intersections that simple keyword matching missed."
            }
        },
        "scenario_2": {
            "title": "Imatinib: Distinguishing Mechanistic Plausibility from Clinical Trial Reality",
            "keyword_search": {
                "query": 'PubMed: "Imatinib" AND "Pulmonary Fibrosis" AND "Antifibrotic"',
                "direct_results": 45,
                "limitation": "Keyword search returns multiple papers calling Imatinib a 'novel antifibrotic agent' based on early mouse models. A chatbot summarizer without evidence hierarchy risks falsely presenting Imatinib as effective.",
                "surfaced_path": "Superficial positive association"
            },
            "graph_retrieval": {
                "query": 'MATCH (dr:Drug {name: "Imatinib"})-[:HAS_EVIDENCE]->(ev:Evidence) RETURN ev.tier, ev.direction',
                "multi_hop_found": True,
                "evidence_stratification": {
                    "preclinical": {
                        "tier": 3,
                        "direction": "supports",
                        "summary": "Murine bleomycin models showed PDGF phosphorylation blockade (Aono et al. 2005)."
                    },
                    "clinical_trial": {
                        "tier": 1,
                        "direction": "no_effect",
                        "summary": "Randomized double-blind Phase 2 trial of 119 patients proved NO benefit on survival or FVC rate of decline (Daniels et al. 2010, NCT00130520)."
                    }
                },
                "outcome": "MedTrail's evidence-tier hierarchy prevents clinical misinformation by displaying the Phase 2 failure (Tier 1) as the governing finding over mouse data (Tier 3)."
            }
        }
    }

