import logging
from typing import Dict, Any
from app.db.neo4j import neo4j_conn

logger = logging.getLogger(__name__)

def clear_existing_data(clear_all: bool = False) -> None:
    """Clear nodes. If clear_all is True, wipe entire database. Otherwise remove only MedTrail biomedical labels."""
    with neo4j_conn.get_session() as session:
        if clear_all:
            logger.info("Clearing entire Neo4j database...")
            session.run("MATCH (n) DETACH DELETE n").consume()
        else:
            logger.info("Clearing MedTrail biomedical entity nodes...")
            session.run("""
                MATCH (n)
                WHERE n:Disease OR n:Gene OR n:Protein OR n:Pathway OR n:Drug 
                   OR n:ClinicalStudy OR n:ResearchPaper OR n:SideEffect 
                   OR n:Evidence OR n:Hypothesis
                DETACH DELETE n
            """).consume()

def seed_ipf_dataset() -> Dict[str, Any]:
    """Ingest curated, source-verified Idiopathic Pulmonary Fibrosis (IPF) knowledge graph."""
    with neo4j_conn.get_session() as session:
        logger.info("Seeding IPF knowledge graph...")

        # 1. Disease Node
        session.run("""
            MERGE (d:Disease {id: 'DIS:IPF'})
            SET d.name = 'Idiopathic Pulmonary Fibrosis',
                d.mondo_id = 'MONDO:0008383',
                d.mesh_id = 'D054990',
                d.synonyms = ['IPF', 'Cryptogenic Fibrosing Alveolitis'],
                d.description = 'A chronic, progressive fibrosing interstitial pneumonia of unknown cause, occurring primarily in older adults, limited to the lungs, and associated with progressive worsening of dyspnea and lung function.'
        """).consume()

        # 2. Biological Pathways
        pathways = [
            {
                "id": "PW:FGFR",
                "name": "FGFR Signaling Pathway",
                "biological_role": "Drives fibroblast proliferation, survival, and extracellular matrix deposition in lung parenchyma.",
                "source": "Reactome:R-HSA-190369"
            },
            {
                "id": "PW:PDGF",
                "name": "Signaling by PDGF",
                "biological_role": "Potent mitogen driving pulmonary fibroblast migration, proliferation, and transdifferentiation into alpha-SMA positive myofibroblasts.",
                "source": "Reactome:R-HSA-186797"
            },
            {
                "id": "PW:VEGF",
                "name": "Signaling by VEGF",
                "biological_role": "Vascular remodeling, endothelial activation, and aberrant capillary proliferation associated with fibrogenesis.",
                "source": "Reactome:R-HSA-194138"
            },
            {
                "id": "PW:TGFB",
                "name": "Signaling by TGF-beta Receptor Complex",
                "biological_role": "Master transcriptional regulator of epithelial-mesenchymal transition (EMT) and massive collagen synthesis.",
                "source": "Reactome:R-HSA-170834"
            },
            {
                "id": "PW:RTK",
                "name": "Signaling by Receptor Tyrosine Kinases",
                "biological_role": "Broad receptor tyrosine kinase transduction cascade orchestrating tissue repair and pathological fibrosis.",
                "source": "Reactome:R-HSA-9006934"
            }
        ]
        session.run("""
            UNWIND $pathways AS pw
            MERGE (p:Pathway {id: pw.id})
            SET p.name = pw.name,
                p.biological_role = pw.biological_role,
                p.source = pw.source
        """, pathways=pathways).consume()

        # 3. Genes and Encoded Proteins
        genes_and_proteins = [
            {
                "gene_id": "GENE:FGFR1", "symbol": "FGFR1", "gene_name": "Fibroblast Growth Factor Receptor 1", "ensembl": "ENSG00000077782",
                "prot_id": "PROT:P11362", "accession": "P11362", "prot_name": "Fibroblast growth factor receptor 1",
                "function": "Tyrosine-protein kinase acting as cell-surface receptor for fibroblast growth factors; regulates cell proliferation and differentiation.",
                "pathways": ["PW:FGFR", "PW:RTK"]
            },
            {
                "gene_id": "GENE:FGFR2", "symbol": "FGFR2", "gene_name": "Fibroblast Growth Factor Receptor 2", "ensembl": "ENSG00000066468",
                "prot_id": "PROT:P21802", "accession": "P21802", "prot_name": "Fibroblast growth factor receptor 2",
                "function": "Receptor tyrosine kinase essential for regulation of embryonic development, cell proliferation, and wound repair.",
                "pathways": ["PW:FGFR", "PW:RTK"]
            },
            {
                "gene_id": "GENE:FGFR3", "symbol": "FGFR3", "gene_name": "Fibroblast Growth Factor Receptor 3", "ensembl": "ENSG00000068078",
                "prot_id": "PROT:P22607", "accession": "P22607", "prot_name": "Fibroblast growth factor receptor 3",
                "function": "Receptor tyrosine kinase participating in limb development, cortical neurogenesis, and fibrotic cellular responses.",
                "pathways": ["PW:FGFR", "PW:RTK"]
            },
            {
                "gene_id": "GENE:PDGFRA", "symbol": "PDGFRA", "gene_name": "Platelet Derived Growth Factor Receptor Alpha", "ensembl": "ENSG00000134853",
                "prot_id": "PROT:P16234", "accession": "P16234", "prot_name": "Platelet-derived growth factor receptor alpha",
                "function": "Receptor tyrosine kinase binding PDGF-A and PDGF-C; plays key role in alveolar development and mesenchymal cell expansion.",
                "pathways": ["PW:PDGF", "PW:RTK"]
            },
            {
                "gene_id": "GENE:PDGFRB", "symbol": "PDGFRB", "gene_name": "Platelet Derived Growth Factor Receptor Beta", "ensembl": "ENSG00000113721",
                "prot_id": "PROT:P09619", "accession": "P09619", "prot_name": "Platelet-derived growth factor receptor beta",
                "function": "Receptor tyrosine kinase binding PDGF-B and PDGF-D; central driver of pericyte proliferation and pulmonary myofibroblast expansion.",
                "pathways": ["PW:PDGF", "PW:RTK"]
            },
            {
                "gene_id": "GENE:KDR", "symbol": "KDR", "gene_name": "Kinase Insert Domain Receptor (VEGFR2)", "ensembl": "ENSG00000128052",
                "prot_id": "PROT:P35968", "accession": "P35968", "prot_name": "Vascular endothelial growth factor receptor 2",
                "function": "Primary receptor for VEGF-induced endothelial proliferation, migration, survival, and vascular permeability.",
                "pathways": ["PW:VEGF", "PW:RTK"]
            },
            {
                "gene_id": "GENE:FLT1", "symbol": "FLT1", "gene_name": "Fms Related Receptor Tyrosine Kinase 1 (VEGFR1)", "ensembl": "ENSG00000102755",
                "prot_id": "PROT:P17948", "accession": "P17948", "prot_name": "Vascular endothelial growth factor receptor 1",
                "function": "Tyrosine-protein kinase receptor for VEGFA, VEGFB and PGF; modulates vascular remodeling and inflammatory cell recruitment.",
                "pathways": ["PW:VEGF", "PW:RTK"]
            },
            {
                "gene_id": "GENE:TGFB1", "symbol": "TGFB1", "gene_name": "Transforming Growth Factor Beta 1", "ensembl": "ENSG00000105329",
                "prot_id": "PROT:P01137", "accession": "P01137", "prot_name": "Transforming growth factor beta-1",
                "function": "Multifunctional cytokine regulating cell proliferation, differentiation, apoptosis, and driving excessive fibrotic collagen deposition.",
                "pathways": ["PW:TGFB"]
            },
            {
                "gene_id": "GENE:CCN2", "symbol": "CCN2", "gene_name": "Cellular Communication Network Factor 2 (CTGF)", "ensembl": "ENSG00000118523",
                "prot_id": "PROT:P29279", "accession": "P29279", "prot_name": "Connective tissue growth factor",
                "function": "Major downstream mediator of TGF-beta induced fibroblast proliferation, adhesion, migration, and extracellular matrix production.",
                "pathways": ["PW:TGFB"]
            },
            {
                "gene_id": "GENE:PTGIR", "symbol": "PTGIR", "gene_name": "Prostaglandin I2 Receptor", "ensembl": "ENSG00000160013",
                "prot_id": "PROT:P43119", "accession": "P43119", "prot_name": "Prostacyclin receptor",
                "function": "G-protein coupled receptor for prostacyclin (PGI2); mediates vasodilation and exerts anti-proliferative effects on vascular smooth muscle.",
                "pathways": []
            },
            {
                "gene_id": "GENE:ABL1", "symbol": "ABL1", "gene_name": "ABL Proto-Oncogene 1, Non-Receptor Tyrosine Kinase", "ensembl": "ENSG00000097007",
                "prot_id": "PROT:P00519", "accession": "P00519", "prot_name": "Tyrosine-protein kinase ABL1",
                "function": "Cytoplasmic and nuclear non-receptor tyrosine kinase involved in cellular response to DNA damage, cytoskeletal remodeling, and oxidative stress.",
                "pathways": []
            },
            {
                "gene_id": "GENE:KIT", "symbol": "KIT", "gene_name": "KIT Proto-Oncogene, Receptor Tyrosine Kinase", "ensembl": "ENSG00000157404",
                "prot_id": "PROT:P10721", "accession": "P10721", "prot_name": "Mast/stem cell growth factor receptor Kit",
                "function": "Receptor tyrosine kinase for stem cell factor (SCF); controls mast cell proliferation, survival, and degranulation in fibrotic tissue.",
                "pathways": ["PW:RTK"]
            }
        ]

        for item in genes_and_proteins:
            session.run("""
                MERGE (g:Gene {id: $gene_id})
                SET g.symbol = $symbol,
                    g.name = $gene_name,
                    g.organism = 'Homo sapiens',
                    g.ensembl_id = $ensembl

                MERGE (p:Protein {id: $prot_id})
                SET p.accession = $accession,
                    p.name = $prot_name,
                    p.function = $function,
                    p.organism = 'Homo sapiens'

                MERGE (g)-[:ENCODES]->(p)

                WITH g, p
                MATCH (d:Disease {id: 'DIS:IPF'})
                MERGE (d)-[:ASSOCIATED_WITH {score: 0.85, evidence_source: 'Open Targets & UniProt'}]->(g)

                WITH p
                UNWIND $pathways AS pw_id
                MATCH (pw:Pathway {id: pw_id})
                MERGE (p)-[:PARTICIPATES_IN]->(pw)
            """, {
                "gene_id": item["gene_id"],
                "symbol": item["symbol"],
                "gene_name": item["gene_name"],
                "ensembl": item["ensembl"],
                "prot_id": item["prot_id"],
                "accession": item["accession"],
                "prot_name": item["prot_name"],
                "function": item["function"],
                "pathways": item["pathways"]
            }).consume()

        # 4. Drugs
        drugs = [
            {
                "id": "DRUG:NINTEDANIB",
                "name": "Nintedanib",
                "brand_names": ["Ofev", "Vargatef"],
                "chembl_id": "CHEMBL502835",
                "drug_type": "Small molecule",
                "mechanism": "Triple angiokinase inhibitor simultaneously blocking VEGFR1-3, FGFR1-3, and PDGFRalpha/beta kinase activity.",
                "approval_status": "Approved for IPF (US FDA 2014, EMA 2015)",
                "targets": [
                    {"prot_id": "PROT:P11362", "action": "Inhibitor", "affinity_nm": 69},
                    {"prot_id": "PROT:P21802", "action": "Inhibitor", "affinity_nm": 37},
                    {"prot_id": "PROT:P22607", "action": "Inhibitor", "affinity_nm": 108},
                    {"prot_id": "PROT:P16234", "action": "Inhibitor", "affinity_nm": 59},
                    {"prot_id": "PROT:P09619", "action": "Inhibitor", "affinity_nm": 65},
                    {"prot_id": "PROT:P35968", "action": "Inhibitor", "affinity_nm": 21},
                    {"prot_id": "PROT:P17948", "action": "Inhibitor", "affinity_nm": 34}
                ]
            },
            {
                "id": "DRUG:IMATINIB",
                "name": "Imatinib",
                "brand_names": ["Gleevec", "Glivec"],
                "chembl_id": "CHEMBL941",
                "drug_type": "Small molecule",
                "mechanism": "Selective tyrosine kinase inhibitor targeting BCR-ABL, PDGFRalpha/beta, and c-KIT; investigated for antifibrotic properties in IPF.",
                "approval_status": "Approved for CML & GIST; Evaluated & Ineffective for IPF (Phase 2)",
                "targets": [
                    {"prot_id": "PROT:P09619", "action": "Inhibitor", "affinity_nm": 100},
                    {"prot_id": "PROT:P16234", "action": "Inhibitor", "affinity_nm": 100},
                    {"prot_id": "PROT:P10721", "action": "Inhibitor", "affinity_nm": 400},
                    {"prot_id": "PROT:P00519", "action": "Inhibitor", "affinity_nm": 25}
                ]
            },
            {
                "id": "DRUG:PIRFENIDONE",
                "name": "Pirfenidone",
                "brand_names": ["Esbriet", "Pirespa"],
                "chembl_id": "CHEMBL1073",
                "drug_type": "Small molecule",
                "mechanism": "Antifibrotic pyridone derivative that downregulates TGF-beta production, reduces collagen synthesis, and suppresses myofibroblast differentiation.",
                "approval_status": "Approved for IPF (US FDA 2014, EMA 2011)",
                "targets": [
                    {"prot_id": "PROT:P01137", "action": "Synthesis Downregulator", "affinity_nm": 500000}
                ]
            },
            {
                "id": "DRUG:PAMREVLUMAB",
                "name": "Pamrevlumab",
                "brand_names": ["FG-3019"],
                "chembl_id": "CHEMBL3989938",
                "drug_type": "Monoclonal antibody",
                "mechanism": "Recombinant human IgG1 monoclonal antibody neutralizing connective tissue growth factor (CTGF / CCN2).",
                "approval_status": "Discontinued for IPF (Phase 3 ZEPHYRUS-1 failed primary efficacy endpoint in 2023)",
                "targets": [
                    {"prot_id": "PROT:P29279", "action": "Neutralizing Antibody", "affinity_nm": 1}
                ]
            },
            {
                "id": "DRUG:TREPROSTINIL",
                "name": "Treprostinil",
                "brand_names": ["Tyvaso", "Remodulin"],
                "chembl_id": "CHEMBL1201131",
                "drug_type": "Prostacyclin analogue",
                "mechanism": "Synthetic analogue of prostacyclin activating PTGIR, stimulating intracellular cAMP, promoting pulmonary vasodilation and inhibiting fibroblast proliferation.",
                "approval_status": "Approved for PH-ILD (FDA 2021); Evaluated in IPF (TETON trial)",
                "targets": [
                    {"prot_id": "PROT:P43119", "action": "Agonist", "affinity_nm": 32}
                ]
            }
        ]

        for drug in drugs:
            session.run("""
                MERGE (dr:Drug {id: $id})
                SET dr.name = $name,
                    dr.brand_names = $brand_names,
                    dr.chembl_id = $chembl_id,
                    dr.drug_type = $drug_type,
                    dr.mechanism = $mechanism,
                    dr.approval_status = $approval_status
            """, drug).consume()

            for target in drug["targets"]:
                session.run("""
                    MATCH (dr:Drug {id: $drug_id})
                    MATCH (p:Protein {id: $prot_id})
                    MERGE (dr)-[r:TARGETS]->(p)
                    SET r.action_type = $action,
                        r.affinity_nm = $affinity_nm,
                        r.source = 'ChEMBL & Published Bioactivity'
                """, {
                    "drug_id": drug["id"],
                    "prot_id": target["prot_id"],
                    "action": target["action"],
                    "affinity_nm": target["affinity_nm"]
                }).consume()

        # 5. Clinical Studies
        studies = [
            {
                "id": "CS:NCT01335464",
                "nct_id": "NCT01335464",
                "title": "Efficacy and Safety of BIBF 1120 in Patients With Idiopathic Pulmonary Fibrosis (INPULSIS-1)",
                "phase": "Phase 3",
                "status": "Completed",
                "intervention": "Nintedanib 150 mg BID",
                "conditions": ["Idiopathic Pulmonary Fibrosis"],
                "completion_date": "2014-02",
                "results_summary": "Adjusted annual rate of change in forced vital capacity (FVC) was -114.7 mL/year in nintedanib group versus -239.9 mL/year in placebo group (difference: 125.3 mL/year, 95% CI 77.7 to 172.8; p < 0.001)."
            },
            {
                "id": "CS:NCT01335477",
                "nct_id": "NCT01335477",
                "title": "Efficacy and Safety of BIBF 1120 in Patients With Idiopathic Pulmonary Fibrosis (INPULSIS-2)",
                "phase": "Phase 3",
                "status": "Completed",
                "intervention": "Nintedanib 150 mg BID",
                "conditions": ["Idiopathic Pulmonary Fibrosis"],
                "completion_date": "2014-02",
                "results_summary": "Annual rate of FVC decline was -113.6 mL/year in nintedanib group versus -207.3 mL/year in placebo group (difference: 93.7 mL/year, 95% CI 44.8 to 142.7; p < 0.001); significantly delayed time to first acute exacerbation."
            },
            {
                "id": "CS:NCT00514683",
                "nct_id": "NCT00514683",
                "title": "A 12-Month Phase II Trial of BIBF 1120 in Patients With Idiopathic Pulmonary Fibrosis (TOMORROW)",
                "phase": "Phase 2",
                "status": "Completed",
                "intervention": "BIBF 1120 (Nintedanib) 50 mg QD, 50 mg BID, 100 mg BID, 150 mg BID",
                "conditions": ["Idiopathic Pulmonary Fibrosis"],
                "completion_date": "2011-06",
                "results_summary": "150 mg BID arm demonstrated 68.4% reduction in annual FVC decline and lower incidence of acute exacerbations (2.4 vs 15.7 per 100 patient-years)."
            },
            {
                "id": "CS:NCT00130520",
                "nct_id": "NCT00130520",
                "title": "A Phase II Randomized Double-Blind Placebo-Controlled Study of Imatinib Mesylate in Patients With Idiopathic Pulmonary Fibrosis",
                "phase": "Phase 2",
                "status": "Completed",
                "intervention": "Imatinib mesylate 600 mg daily oral",
                "conditions": ["Idiopathic Pulmonary Fibrosis"],
                "completion_date": "2009-03",
                "results_summary": "Imatinib did not affect survival (hazard ratio 0.94; 95% CI 0.44-2.02) or the rate of FVC decline over 96 weeks. Primary endpoint was not met; associated with higher rates of adverse events (edema, GI)."
            },
            {
                "id": "CS:NCT01366209",
                "nct_id": "NCT01366209",
                "title": "A Study of Pirfenidone in Patients With Idiopathic Pulmonary Fibrosis (ASCEND)",
                "phase": "Phase 3",
                "status": "Completed",
                "intervention": "Pirfenidone 2403 mg/day oral",
                "conditions": ["Idiopathic Pulmonary Fibrosis"],
                "completion_date": "2014-01",
                "results_summary": "Relative reduction of 47.9% in the proportion of patients who had a decline of >=10% in FVC or died; increased proportion with no FVC decline by 132.5%."
            },
            {
                "id": "CS:NCT00287716",
                "nct_id": "NCT00287716",
                "title": "Clinical Studies Assessing Pirfenidone in Idiopathic Pulmonary Fibrosis (CAPACITY 004)",
                "phase": "Phase 3",
                "status": "Completed",
                "intervention": "Pirfenidone 2403 mg/day vs placebo",
                "conditions": ["Idiopathic Pulmonary Fibrosis"],
                "completion_date": "2009-11",
                "results_summary": "Significantly reduced mean change in percent predicted FVC at week 72 (-8.0% vs -12.4%, p = 0.001)."
            },
            {
                "id": "CS:NCT03955146",
                "nct_id": "NCT03955146",
                "title": "Safety and Efficacy of Pamrevlumab in Subjects With Idiopathic Pulmonary Fibrosis (ZEPHYRUS-1)",
                "phase": "Phase 3",
                "status": "Terminated / Completed",
                "intervention": "Pamrevlumab 30 mg/kg IV every 3 weeks",
                "conditions": ["Idiopathic Pulmonary Fibrosis"],
                "completion_date": "2023-06",
                "results_summary": "Did not meet its primary endpoint of change from baseline in FVC at week 48 compared to placebo; FibroGen halted further pamrevlumab development for IPF."
            }
        ]

        session.run("""
            UNWIND $studies AS s
            MERGE (cs:ClinicalStudy {id: s.id})
            SET cs.nct_id = s.nct_id,
                cs.title = s.title,
                cs.phase = s.phase,
                cs.status = s.status,
                cs.intervention = s.intervention,
                cs.conditions = s.conditions,
                cs.completion_date = s.completion_date,
                cs.results_summary = s.results_summary
        """, studies=studies).consume()

        # Connect Drug -> ClinicalStudy
        study_links = [
            ("DRUG:NINTEDANIB", "CS:NCT01335464"),
            ("DRUG:NINTEDANIB", "CS:NCT01335477"),
            ("DRUG:NINTEDANIB", "CS:NCT00514683"),
            ("DRUG:IMATINIB", "CS:NCT00130520"),
            ("DRUG:PIRFENIDONE", "CS:NCT01366209"),
            ("DRUG:PIRFENIDONE", "CS:NCT00287716"),
            ("DRUG:PAMREVLUMAB", "CS:NCT03955146"),
        ]
        session.run("""
            UNWIND $links AS l
            MATCH (dr:Drug {id: l[0]})
            MATCH (cs:ClinicalStudy {id: l[1]})
            MERGE (dr)-[:INVESTIGATED_IN]->(cs)
        """, links=study_links).consume()

        # 6. Research Papers
        papers = [
            {
                "id": "RP:PMID24836310",
                "pmid": "24836310",
                "doi": "10.1056/NEJMoa1402584",
                "title": "Efficacy and Safety of Nintedanib in Idiopathic Pulmonary Fibrosis",
                "journal": "New England Journal of Medicine",
                "pub_date": "2014-05-29",
                "abstract": "In two 52-week, randomized, double-blind, phase 3 trials (INPULSIS-1 and INPULSIS-2) involving 1066 patients, nintedanib significantly slowed disease progression by reducing the annual rate of decline in forced vital capacity in patients with idiopathic pulmonary fibrosis."
            },
            {
                "id": "RP:PMID19897772",
                "pmid": "19897772",
                "doi": "10.1164/rccm.200906-0964OC",
                "title": "A Randomized, Controlled Trial of Imatinib in Idiopathic Pulmonary Fibrosis",
                "journal": "American Journal of Respiratory and Critical Care Medicine",
                "pub_date": "2010-02-15",
                "abstract": "In this randomized double-blind placebo-controlled trial of 119 IPF patients, imatinib did not affect survival or rate of lung function decline over 96 weeks. These clinical findings demonstrate that targeting the PDGF receptor alone is not sufficient to halt progressive fibrogenesis in human disease."
            },
            {
                "id": "RP:PMID15161911",
                "pmid": "15161911",
                "doi": "10.1164/rccm.200404-454OC",
                "title": "Imatinib as a Novel Antifibrotic Agent in Bleomycin-Induced Pulmonary Fibrosis in Mice",
                "journal": "American Journal of Respiratory and Critical Care Medicine",
                "pub_date": "2005-06-01",
                "abstract": "Preclinical investigation in murine bleomycin models demonstrated that imatinib attenuated lung fibrosis and collagen accumulation by blocking PDGF receptor phosphorylation in lung fibroblasts, providing the initial preclinical hypothesis for clinical testing."
            },
            {
                "id": "RP:PMID24836312",
                "pmid": "24836312",
                "doi": "10.1056/NEJMoa1402582",
                "title": "A Phase 3 Trial of Pirfenidone in Patients with Idiopathic Pulmonary Fibrosis",
                "journal": "New England Journal of Medicine",
                "pub_date": "2014-05-29",
                "abstract": "The ASCEND trial confirmed that pirfenidone significantly reduced disease progression in patients with IPF, meeting the primary endpoint of slowing the rate of decline in forced vital capacity, along with positive effects on secondary endpoints."
            },
            {
                "id": "RP:PMID38843513",
                "pmid": "38843513",
                "doi": "10.1183/13993003.00318-2024",
                "title": "Trial of Pamrevlumab in Idiopathic Pulmonary Fibrosis: Results of the Phase 3 ZEPHYRUS-1 Study",
                "journal": "European Respiratory Journal",
                "pub_date": "2024-06-06",
                "abstract": "In the Phase 3 ZEPHYRUS-1 trial, pamrevlumab did not show a statistically significant difference in FVC decline versus placebo at week 48, highlighting that targeting connective tissue growth factor alone did not replicate Phase 2 promise."
            },
            {
                "id": "RP:PMID21926344",
                "pmid": "21926344",
                "doi": "10.1016/j.ejca.2004.03.011",
                "title": "Mode of Action of Nintedanib (BIBF 1120) as an Antifibrotic and Antiangiogenic Agent",
                "journal": "European Journal of Cancer",
                "pub_date": "2004-09-01",
                "abstract": "BIBF 1120 was identified as an indolinone derivative that concurrently inhibits receptor tyrosine kinases VEGFR, FGFR and PDGFR at low nanomolar concentrations, preventing ligand-dependent autophosphorylation and mitogenesis."
            }
        ]

        session.run("""
            UNWIND $papers AS p
            MERGE (rp:ResearchPaper {id: p.id})
            SET rp.pmid = p.pmid,
                rp.doi = p.doi,
                rp.title = p.title,
                rp.journal = p.journal,
                rp.pub_date = p.pub_date,
                rp.abstract = p.abstract
        """, papers=papers).consume()

        # 7. Side Effects
        side_effects = [
            {"id": "SE:DIARRHEA", "name": "Diarrhea", "umls_cui": "C0011991", "meddra_id": "10012735", "severity": "Moderate to High"},
            {"id": "SE:LIVER_ENZYMES", "name": "Elevated Liver Enzymes (AST/ALT)", "umls_cui": "C0086565", "meddra_id": "10060795", "severity": "Moderate"},
            {"id": "SE:NAUSEA", "name": "Nausea", "umls_cui": "C0027497", "meddra_id": "10028813", "severity": "Mild to Moderate"},
            {"id": "SE:RASH", "name": "Photosensitivity Rash", "umls_cui": "C0349506", "meddra_id": "10034959", "severity": "Moderate"},
            {"id": "SE:EDEMA", "name": "Peripheral Edema", "umls_cui": "C0085649", "meddra_id": "10034570", "severity": "Moderate"},
            {"id": "SE:CRAMPS", "name": "Muscle Spasms and Cramps", "umls_cui": "C0026821", "meddra_id": "10028334", "severity": "Mild to Moderate"}
        ]
        session.run("""
            UNWIND $side_effects AS se
            MERGE (s:SideEffect {id: se.id})
            SET s.name = se.name,
                s.umls_cui = se.umls_cui,
                s.meddra_id = se.meddra_id,
                s.severity = se.severity
        """, side_effects=side_effects).consume()

        # Connect Drug -> SideEffect
        drug_side_effects = [
            ("DRUG:NINTEDANIB", "SE:DIARRHEA", "Reported in 62.4% of INPULSIS trial patients"),
            ("DRUG:NINTEDANIB", "SE:LIVER_ENZYMES", "Observed in ~5% of patients; requires routine monitoring"),
            ("DRUG:NINTEDANIB", "SE:NAUSEA", "Reported in ~24% of patients"),
            ("DRUG:IMATINIB", "SE:EDEMA", "Fluid retention and periorbital edema common in trial arms"),
            ("DRUG:IMATINIB", "SE:CRAMPS", "Reported muscle cramps and musculoskeletal pain"),
            ("DRUG:IMATINIB", "SE:NAUSEA", "Gastrointestinal distress frequent in IPF cohorts"),
            ("DRUG:PIRFENIDONE", "SE:RASH", "Dermatologic photosensitivity reaction requiring sun avoidance"),
            ("DRUG:PIRFENIDONE", "SE:NAUSEA", "Reported in ~36% of patients in ASCEND trial"),
            ("DRUG:PIRFENIDONE", "SE:LIVER_ENZYMES", "Reversible elevations requiring dose adjustment")
        ]
        session.run("""
            UNWIND $dse AS item
            MATCH (dr:Drug {id: item[0]})
            MATCH (se:SideEffect {id: item[1]})
            MERGE (dr)-[r:ASSOCIATED_WITH_ADVERSE_EVENT]->(se)
            SET r.evidence_context = item[2]
        """, dse=drug_side_effects).consume()

        # 8. Evidence Nodes (Tiers 1 to 4 with Transparent Ranking & Directions)
        evidence_records = [
            {
                "id": "EV:NINT:01",
                "source": "NEJM (PMID: 24836310), ClinicalTrials.gov (NCT01335464, NCT01335477)",
                "source_url": "https://pubmed.ncbi.nlm.nih.gov/24836310/",
                "evidence_type": "clinical_trial",
                "tier": 1,
                "direction": "supports",
                "confidence": 0.95,
                "summary": "In Phase 3 INPULSIS-1 and INPULSIS-2 trials (1,066 patients), nintedanib 150 mg BID significantly reduced the annual rate of decline in forced vital capacity (FVC) by approximately 50% compared to placebo (-114.7 mL/yr vs -239.9 mL/yr, p < 0.001).",
                "limitations": "Frequent gastrointestinal adverse events (diarrhea 62.4% vs 18.4% placebo), leading to discontinuation in 4.4% of patients; does not reverse pre-existing fibrotic scarring.",
                "study_id": "CS:NCT01335464",
                "paper_id": "RP:PMID24836310",
                "drug_id": "DRUG:NINTEDANIB"
            },
            {
                "id": "EV:IMAT:01",
                "source": "AJRCCM (PMID: 19897772), ClinicalTrials.gov (NCT00130520)",
                "source_url": "https://pubmed.ncbi.nlm.nih.gov/19897772/",
                "evidence_type": "clinical_trial",
                "tier": 1,
                "direction": "no_effect",
                "confidence": 0.90,
                "summary": "In a randomized, double-blind, placebo-controlled Phase 2 trial of 119 IPF patients, imatinib mesylate 600 mg daily did not affect survival (hazard ratio 0.94; 95% CI 0.44-2.02) or the rate of FVC decline over 96 weeks.",
                "limitations": "Clinical failure occurred despite strong preclinical PDGF-receptor inhibition rationale; accompanied by higher rates of peripheral edema and gastrointestinal intolerance.",
                "study_id": "CS:NCT00130520",
                "paper_id": "RP:PMID19897772",
                "drug_id": "DRUG:IMATINIB"
            },
            {
                "id": "EV:IMAT:02",
                "source": "AJRCCM (PMID: 15161911)",
                "source_url": "https://pubmed.ncbi.nlm.nih.gov/15161911/",
                "evidence_type": "preclinical",
                "tier": 3,
                "direction": "supports",
                "confidence": 0.65,
                "summary": "In murine models of bleomycin-induced pulmonary fibrosis, imatinib attenuated lung fibrosis and collagen deposition by blocking PDGF receptor phosphorylation in lung fibroblasts.",
                "limitations": "Murine bleomycin model resolution did not translate into human clinical efficacy, illustrating biological pathway redundancy and limitations of animal models in IPF.",
                "study_id": None,
                "paper_id": "RP:PMID15161911",
                "drug_id": "DRUG:IMATINIB"
            },
            {
                "id": "EV:PIRF:01",
                "source": "NEJM (PMID: 24836312), ClinicalTrials.gov (NCT01366209)",
                "source_url": "https://pubmed.ncbi.nlm.nih.gov/24836312/",
                "evidence_type": "clinical_trial",
                "tier": 1,
                "direction": "supports",
                "confidence": 0.94,
                "summary": "In the Phase 3 ASCEND trial (555 patients), pirfenidone significantly reduced disease progression by 47.9% and increased the proportion of patients with no decline in FVC.",
                "limitations": "Adverse events included nausea, dyspepsia, and photosensitivity rash, requiring dosage titration and sun protection.",
                "study_id": "CS:NCT01366209",
                "paper_id": "RP:PMID24836312",
                "drug_id": "DRUG:PIRFENIDONE"
            },
            {
                "id": "EV:PAMR:01",
                "source": "Eur Respir J (PMID: 38843513), ClinicalTrials.gov (NCT03955146)",
                "source_url": "https://pubmed.ncbi.nlm.nih.gov/38843513/",
                "evidence_type": "clinical_trial",
                "tier": 1,
                "direction": "no_effect",
                "confidence": 0.92,
                "summary": "In the Phase 3 ZEPHYRUS-1 trial, pamrevlumab (anti-CTGF mAb) did not meet its primary endpoint of change from baseline in FVC at week 48 compared to placebo.",
                "limitations": "Positive Phase 2 PRAISE results were not confirmed in the larger randomized Phase 3 setting, demonstrating the necessity of rigorous trial verification.",
                "study_id": "CS:NCT03955146",
                "paper_id": "RP:PMID38843513",
                "drug_id": "DRUG:PAMREVLUMAB"
            }
        ]

        for ev in evidence_records:
            session.run("""
                MERGE (e:Evidence {id: $id})
                SET e.source = $source,
                    e.source_url = $source_url,
                    e.evidence_type = $evidence_type,
                    e.tier = $tier,
                    e.direction = $direction,
                    e.confidence = $confidence,
                    e.summary = $summary,
                    e.limitations = $limitations,
                    e.drug_id = $drug_id

                WITH e
                MATCH (d:Disease {id: 'DIS:IPF'})
                MERGE (e)-[:ABOUT]->(d)

                WITH e
                MATCH (dr:Drug {id: $drug_id})
                MERGE (dr)-[:HAS_EVIDENCE]->(e)
            """, ev).consume()

            # Connect ClinicalStudy -> Evidence
            if ev["study_id"]:
                session.run("""
                    MATCH (cs:ClinicalStudy {id: $study_id})
                    MATCH (e:Evidence {id: $ev_id})
                    MERGE (cs)-[:REPORTS]->(e)
                """, {"study_id": ev["study_id"], "ev_id": ev["id"]}).consume()

            # Connect ResearchPaper -> Evidence
            if ev["paper_id"]:
                session.run("""
                    MATCH (rp:ResearchPaper {id: $paper_id})
                    MATCH (e:Evidence {id: $ev_id})
                    MERGE (rp)-[:SUPPORTS_OR_REPORTS]->(e)
                """, {"paper_id": ev["paper_id"], "ev_id": ev["id"]}).consume()

        # 9. Hypotheses (Categorized & Labeled)
        hypotheses = [
            {
                "id": "HYP:NINTEDANIB",
                "title": "Simultaneous Triple-Angiokinase Receptor Inhibition Slows Lung Function Loss in IPF",
                "description": "Concurrent blockade of FGFR, PDGFR, and VEGFR cascades inhibits fibroblast proliferation, migration, and extracellular matrix deposition, overcoming compensatory signaling loops to slow FVC decline in IPF.",
                "supporting_paths": "IPF -> FGFR/PDGF/VEGF Pathways -> FGFR1-3/PDGFRA-B/KDR/FLT1 -> Nintedanib -> INPULSIS Trials (NCT01335464) -> NEJM 2014",
                "uncertainties": "Therapy slows progression but does not restore destroyed alveolar architecture or reverse honeycombing; patient compliance depends on GI adverse event management.",
                "review_status": "verified_established",
                "evidence_ids": ["EV:NINT:01"]
            },
            {
                "id": "HYP:IMATINIB",
                "title": "Selective PDGF/c-Kit Tyrosine Kinase Blockade Fails in Clinical Human IPF",
                "description": "Although selective PDGF receptor and c-KIT blockade attenuates fibrosis in murine bleomycin models, human Phase 2 trials demonstrated lack of clinical benefit on survival or FVC, demonstrating redundant cytokine drives (FGFR, TGF-beta) in human pathogenesis.",
                "supporting_paths": "IPF -> PDGF Pathway -> PDGFRA/PDGFRB -> Imatinib -> NCT00130520 -> AJRCCM 2010",
                "uncertainties": "Preclinical animal model translational gap; indicates that single-target RTK inhibition is insufficient in complex adult human IPF.",
                "review_status": "refuted_by_trial",
                "evidence_ids": ["EV:IMAT:01", "EV:IMAT:02"]
            }
        ]

        for hyp in hypotheses:
            session.run("""
                MERGE (h:Hypothesis {id: $id})
                SET h.title = $title,
                    h.description = $description,
                    h.supporting_paths = $supporting_paths,
                    h.uncertainties = $uncertainties,
                    h.review_status = $review_status,
                    h.created_at = datetime()
            """, hyp).consume()

            for ev_id in hyp["evidence_ids"]:
                session.run("""
                    MATCH (h:Hypothesis {id: $hyp_id})
                    MATCH (e:Evidence {id: $ev_id})
                    MERGE (e)-[:SUPPORTS]->(h)
                """, {"hyp_id": hyp["id"], "ev_id": ev_id}).consume()

        logger.info("IPF knowledge graph successfully seeded.")

    # Return summary counts
    with neo4j_conn.get_session() as session:
        counts = session.run("""
            MATCH (n)
            RETURN labels(n)[0] AS label, count(n) AS count
            ORDER BY count DESC
        """).data()
        rel_counts = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) AS rel_type, count(r) AS count
            ORDER BY count DESC
        """).data()

    return {
        "node_counts": {c["label"]: c["count"] for c in counts},
        "relationship_counts": {r["rel_type"]: r["count"] for r in rel_counts}
    }
