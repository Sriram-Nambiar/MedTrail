# MedTrail — Graph-Powered Biomedical Research Discovery

[![Neo4j Aura](https://img.shields.io/badge/Neo4j-AuraDB%205.x-blue.svg?logo=neo4j)](https://neo4j.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0-green.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-yellow.svg?logo=python)](https://python.org)

**MedTrail** is an AI-assisted biomedical research discovery platform using **Neo4j as its central knowledge graph** to connect diseases, genes, proteins, biological pathways, medicines, clinical studies, side effects, and scientific literature.

---

## 🎯 Hackathon Focus Disease: Idiopathic Pulmonary Fibrosis (IPF)

For the hackathon, MedTrail is scoped to **Idiopathic Pulmonary Fibrosis (IPF)**, a chronic progressive lung-scarring disease with limited therapies.

### Key Demonstrations in the Graph
1. **Known-Answer Validation (Nintedanib Rediscovery):**
   - Traversing the path: `IPF → RTK / FGFR / PDGF / VEGF Signaling Pathways → FGFR1-3 / PDGFRα-β / KDR Kinase Targets → Nintedanib → INPULSIS Phase 3 Trials (NCT01335464) → NEJM 2014 publication`.
   - Rediscovering how an oncology angiokinase inhibitor was repurposed into an FDA-approved antifibrotic.
2. **Preserved Conflicting Evidence (Imatinib):**
   - Plausible mechanism: Potent inhibitor of PDGF receptors (crucial for pulmonary fibroblast migration).
   - Preclinical finding: Murine bleomycin models showed antifibrotic effect (Tier 3 - *AJRCCM 2005*).
   - Clinical trial outcome: Phase 2 randomized double-blind trial showed **no effect** on survival or FVC decline (*AJRCCM 2010*, *NCT00130520*).
   - MedTrail displays both findings side-by-side with transparent badges, never hiding negative clinical evidence.
3. **Transparent Evidence-Tier Ordering:**
   - **Tier 1:** Clinical-trial evidence with reported outcomes
   - **Tier 2:** Observational human evidence
   - **Tier 3:** Preclinical evidence (animal & in vitro models)
   - **Tier 4:** Mechanistic / database association only

---

## 🧬 Knowledge Graph Schema

### Main Node Types
- `(:Disease)`: Primary identifier (e.g. `MONDO:0008383`, `MeSH:D054990`), name, synonyms, clinical description.
- `(:Pathway)`: Reactome pathways (FGFR, PDGF, VEGF, TGF-β, RTK signaling).
- `(:Gene)` & `(:Protein)`: Ensembl and UniProt accessions for therapeutic targets.
- `(:Drug)`: Approved and investigational compounds (ChEMBL IDs, mechanisms, brand names).
- `(:ClinicalStudy)`: Registered clinical trials (ClinicalTrials.gov NCT IDs, phases, completion dates, outcome summaries).
- `(:ResearchPaper)`: PubMed citations (PMID, DOI, abstracts, peer-reviewed journals).
- `(:SideEffect)`: Adverse events with MedDRA and UMLS CUIs (e.g., diarrhea, elevated AST/ALT, peripheral edema).
- `(:Evidence)`: Provenance-tracked evidence with `tier`, `direction` (supports, no_effect), and limitation caveats.
- `(:Hypothesis)`: Research hypotheses categorized by review status (`verified_established`, `refuted_by_trial`).

### Constraints & Indexes
- Unique constraints enforced on `id` across all 10 core entity labels.
- B-Tree property indexes on `name`, `symbol`, `accession`, `nct_id`, `pmid`, `tier`, and `direction`.
- Full-text search indexes on:
  - `disease_fulltext`
  - `drug_fulltext`
  - `gene_fulltext`
  - `paper_fulltext`

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) or standard Python `venv`
- Neo4j database (Neo4j AuraDB instance or local Docker Compose)

### 2. Environment Setup
Clone the repository and install dependencies:
```bash
git clone https://github.com/Sriram-Nambiar/MedTrail.git
cd MedTrail

# Using uv (fastest)
uv venv .venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

Configure your `.env` file (copy from `.env.example`):
```env
NEO4J_URI=neo4j+s://<your-instance>.databases.neo4j.io
NEO4J_USERNAME=7743778d
NEO4J_PASSWORD=<your-password>
NEO4J_DATABASE=7743778d
```

*(Alternatively, run local Neo4j with `docker-compose up -d`)*

### 3. Initialize & Seed Neo4j Database
Run the automated schema and ingestion script:
```bash
python scripts/init_db.py
```
This script:
1. Verifies connectivity to Neo4j Aura.
2. Creates all 10 unique constraints, 8 property indexes, and 4 full-text search indexes.
3. Ingests the curated, source-verified Idiopathic Pulmonary Fibrosis (IPF) knowledge graph.
4. Outputs summary tables of nodes and relationships.

### 4. Run the Verification Suite
Run the test queries to validate multi-hop traversal and evidence calibration:
```bash
python scripts/verify_db.py
```
This tests:
- **Nintedanib multi-hop rediscovery** from IPF to NEJM trial evidence.
- **Imatinib conflicting evidence** (preclinical support vs clinical trial failure).
- **Candidate drug transparent tier ranking**.
- **Full-text entity search**.

### 5. Launch the FastAPI Backend
Start the REST API server:
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation is available at `http://localhost:8000/docs`.

Key Endpoints:
- `GET /health`: Database connection status.
- `GET /api/graph/overview`: Node and relationship statistics.
- `GET /api/graph/paths?drug_name=Nintedanib`: Multi-hop path inspection.
- `GET /api/graph/candidates`: Candidates ranked by evidence tiers.
- `GET /api/graph/conflicts`: Conflicting evidence detection.
- `GET /api/graph/search?q=fibrosis`: Full-text entity search.

---

## ⚠️ Scientific Limitations & Safety Disclaimer
MedTrail is an exploratory biomedical research and hypothesis-generation tool.
- A path in a knowledge graph does **not** establish clinical efficacy or causation.
- Preclinical findings in animal models frequently fail to translate to human patients.
- MedTrail is not intended for clinical diagnosis, patient treatment, or prescribing decisions.
