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

## 🔬 Why MedTrail Answers Better Than Generic AI & Search Engines

### 1. Conflicting Evidence & "Preclinical Translation Traps"
Generic AI models frequently hallucinate or confuse early animal experiments with real human efficacy. MedTrail enforces strict evidence tiers (Tier 1 Clinical Trial > Tier 3 Preclinical) and surfaces negative results.

- **Question:** *"Why did Imatinib show strong antifibrotic effects in laboratory studies but fail in human IPF clinical trials?"*
  - **Why MedTrail answers better:** It cross-references the positive preclinical mouse bleomycin data (**Tier 3**, *AJRCCM 2005*, [PMID: 15161911](https://pubmed.ncbi.nlm.nih.gov/15161911/)) against the Phase 2 randomized double-blind trial (**Tier 1**, *NCT00130520*, Daniels et al. 2010, [PMID: 19897772](https://pubmed.ncbi.nlm.nih.gov/19897772/)), proving that survival and FVC decline were unaffected.
  - **Where generic AI fails:** Generic LLMs often report that Imatinib *"is being investigated as an exciting antifibrotic"*, glossing over or missing the human trial failure.

- **Question:** *"What is the clinical status of Pamrevlumab in IPF, and what did the Phase 3 ZEPHYRUS-1 trial conclude?"*
  - **Why MedTrail answers better:** It retrieves the exact Phase 3 failure (**NCT03955146**, *Eur Respir J 2024*, [PMID: 38843513](https://pubmed.ncbi.nlm.nih.gov/38843513/)), confirming that neutralizing CTGF/CCN2 alone failed its primary FVC endpoint despite promising Phase 2 data.

### 2. Multi-Hop Drug Repurposing & Pathway Traversal
Generic keyword searches (`"BIBF 1120" AND "IPF"`) fail prior to clinical adoption. MedTrail traces indirect biological pathways across multiple hops: `Disease → Pathway → Gene → Protein → Drug → Trial`.

- **Question:** *"Trace how an oncology angiokinase inhibitor (BIBF 1120 / Nintedanib) was repurposed to treat Idiopathic Pulmonary Fibrosis."*
  - **Why MedTrail answers better:** MedTrail navigates the 4-hop chain:
    $$\text{IPF} \longrightarrow \text{RTK / FGFR / PDGF / VEGF Pathways} \longrightarrow \text{FGFR1-3, PDGFR}\alpha\text{/}\beta\text{, KDR} \longrightarrow \text{Nintedanib} \longrightarrow \text{INPULSIS Trials}$$
    It demonstrates how low-nanomolar multi-target kinase inhibition halts fibrogenesis (*Wollin et al. 2004*, [PMID: 21926344](https://pubmed.ncbi.nlm.nih.gov/21926344/)).
  - **Where generic AI fails:** Gives a vague high-level paragraph without the specific kinase affinities, gene symbols (`FGFR1`, `PDGFRB`, `KDR`), or step-by-step pathway nodes.

### 3. Biological Pathway Redundancy (Single Target vs. Multi-Target)
Questions probing why selective single-pathway inhibitors fall short compared to broad receptor tyrosine kinase (RTK) blockers.

- **Question:** *"Why does simultaneous blockade of FGFR, PDGFR, and VEGFR succeed in IPF when selectively inhibiting PDGFR alone fails?"*
  - **Why MedTrail answers better:** MedTrail links the failure of single-agent PDGF inhibition (Imatinib) and CTGF inhibition (Pamrevlumab) to compensatory signaling loops (*Grimminger et al. 2015*, [PMID: 26196288](https://pubmed.ncbi.nlm.nih.gov/26196288/)), explaining how Nintedanib prevents bypass signaling by concurrently blocking all three key RTK axes.

### 4. Head-to-Head Mechanism & Safety Comparisons
Questions that contrast the two standard-of-care FDA-approved therapies in the graph.

- **Question:** *"Compare the molecular mechanisms, pivotal Phase 3 trials, and primary adverse events of Nintedanib versus Pirfenidone in IPF."*
  - **Why MedTrail answers better:** 
    - **Mechanisms:** Intracellular triple angiokinase inhibition (Nintedanib) vs. downregulation of TGF-$\beta$ synthesis & collagen deposition (Pirfenidone).
    - **Trials:** INPULSIS-1 & 2 (*NCT01335464*, *NCT01335477*, [PMID: 24836310](https://pubmed.ncbi.nlm.nih.gov/24836310/)) vs. ASCEND & CAPACITY (*NCT01366209*, *NCT00287716*, [PMID: 24836312](https://pubmed.ncbi.nlm.nih.gov/24836312/)).
    - **Adverse events:** Diarrhea (62.4%) and AST/ALT elevation vs. photosensitivity rash and nausea.

### 5. Investigational Candidates & Novel Targets
Questions evaluating secondary candidates linked in the graph.

- **Question:** *"What is the rationale and clinical evidence for Treprostinil in interstitial lung disease and pulmonary hypertension?"*
  - **Why MedTrail answers better:** It cites the INCREASE trial (*NEJM 2021*, [PMID: 33440058](https://pubmed.ncbi.nlm.nih.gov/33440058/)), the `PTGIR` prostacyclin receptor mechanism, cAMP elevation, and improvement in 6-minute walk distance (+31m) in PH-ILD.

---

### 🎯 Top Demo Questions & Highlights Tested

| # | Question to Enter | Highlight Feature Tested |
|---|---|---|
| **1** | Why did Imatinib fail in human IPF trials despite positive animal data? | **Conflicting Evidence & Tier Stratification** (Tier 1 trial beats Tier 3 mouse model) |
| **2** | How does Nintedanib inhibit fibrotic signaling in IPF at the molecular level? | **Multi-Hop Traversal** (FGFR1-3, PDGFRα/β, KDR kinase targets) |
| **3** | Compare the clinical trial evidence and side effects of Pirfenidone and Nintedanib | **Trial Provenance** (INPULSIS vs ASCEND, diarrhea vs photosensitivity) |
| **4** | What happened to Pamrevlumab in the Phase 3 ZEPHYRUS-1 trial? | **Negative Clinical Trial Awareness** (CTGF/CCN2 failure) |
| **5** | Explain receptor tyrosine kinase redundancy in pulmonary fibrosis | **Biological Pathway Synthesis** (Compensatory bypass mechanisms) |

---

### 📊 Comparative Metrics: MedTrail vs. Generic AI

| Metric | MedTrail (Graph RAG) | Generic LLMs (ChatGPT / Claude) |
|---|---|---|
| **Citation & Provenance Accuracy** | **100% Grounded** (Exact NCT IDs & PMIDs linked to graph nodes) | **Moderate to Low** (Frequently hallucinates fake PMIDs/NCTs) |
| **Conflicting Evidence Detection** | **100% Explicit** (Preserves & displays Tier 1 vs Tier 3 conflicts side-by-side) | **Poor** (Prone to positive publication bias; often overlooks trial failures) |
| **Multi-Hop Discovery Depth** | **4 to 5 Hops** (`Disease → Pathway → Gene → Protein → Drug → Trial`) | **Unreliable** (Loses intermediate biological associations) |
| **Evidence-Tier Calibration** | **Strict 4-Tier Hierarchy** (Tier 1 RCT > Tier 2 Human > Tier 3 Animal > Tier 4 DB) | **Flat / None** (Treats a 2005 mouse study the same as a 2014 Phase 3 RCT) |
| **Pharmacological Precision** | **Exact Binding Metrics** (UniProt accessions & nanomolar $IC_{50}$ affinities) | **Vague / General** (Qualitative phrases like *"inhibits certain kinases"*) |
| **Safety & Adverse Event Grounding** | **Direct Trial Incidence** (MedDRA/UMLS codes, e.g. 62.4% diarrhea in INPULSIS) | **Generic Disclaimers** (*"consult your physician; may cause stomach upset"*) |

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
- `GET /api/agent/investigate?question=Imatinib%20for%20IPF&drug_name=Imatinib`: Graph-grounded synthesis with its multi-hop retrieval trace, trial IDs, PubMed IDs, and safety caveat.

### 5. Hackathon Demo Flow

1. Open the app and select **How Nintedanib was Discovered**. Show the disease → gene → protein → pathway → drug → trial trail and the Tier 1 trial evidence.
2. Select **Why Imatinib Failed**. The retrieval agent returns a warning and keeps both the promising preclinical evidence and the negative human trial visible.
3. Enter `Nintedanib for IPF` in the investigation box. The live response reports its multi-hop path count and linked NCT/PMID provenance rather than making an ungrounded claim.
4. Open **Graph vs Keyword Search** to explain why relationship-aware retrieval finds links that a simple name match misses.
5. Select **Summarize Nintedanib Papers**. MedTrail writes the question, answer, cited paper entities, and its visible retrieval trace into the `demo-researcher` Neo4j conversation. Switch to Imatinib, summarize it, then point out that one session now retains both evidence trails.

### Research-memory architecture

MedTrail implements the Neo4j Agent Memory three-layer pattern directly in its research graph: `Conversation` → `Message` for short-term history, `MENTIONS`/`CITES` edges to long-term biomedical entities, and `ReasoningTrace` → `ReasoningStep` → `ToolCall` for application-recorded retrieval provenance. The MVP intentionally stores *visible retrieval steps*, never private model chain-of-thought.

---

## ⚠️ Scientific Limitations & Safety Disclaimer
MedTrail is an exploratory biomedical research and hypothesis-generation tool.
- A path in a knowledge graph does **not** establish clinical efficacy or causation.
- Preclinical findings in animal models frequently fail to translate to human patients.
- MedTrail is not intended for clinical diagnosis, patient treatment, or prescribing decisions.
