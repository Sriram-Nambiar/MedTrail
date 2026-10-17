from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any

from app.core.config import settings
from app.db.neo4j import neo4j_conn
from app.db.queries import (
    get_graph_overview,
    find_evidence_paths,
    get_candidate_drugs_with_evidence,
    get_conflicting_evidence_report,
    search_biomedical_entities,
    get_subgraph,
    get_keyword_vs_graph_comparison,
    get_ingested_papers,
    investigate_with_graph,
    summarize_research_papers,
)
from app.memory import get_research_memory

app = FastAPI(
    title=settings.APP_NAME,
    description="MedTrail: Graph-Powered Biomedical Research Discovery API with Neo4j Knowledge Graph",
    version="1.0.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
assets_dir = frontend_dist / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

@app.get("/")
def serve_frontend():
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "message": "Frontend build not detected. Please run 'npm run build' in frontend/."
    }

@app.get("/api")
def api_root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "description": "Graph-Powered Biomedical Research Discovery API",
        "endpoints": {
            "health": "/health",
            "overview": "/api/graph/overview",
            "paths": "/api/graph/paths?drug_name=Nintedanib",
            "candidates": "/api/graph/candidates?disease_id=DIS:IPF",
            "conflicts": "/api/graph/conflicts?disease_id=DIS:IPF",
            "search": "/api/graph/search?q=fibrosis",
            "subgraph": "/api/graph/subgraph?drug_name=Nintedanib",
            "comparison": "/api/graph/comparison"
        }
    }

@app.get("/health")
def health_check():
    try:
        conn = neo4j_conn.check_connection()
        return {
            "status": "healthy",
            "database": conn
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/api/graph/overview")
def graph_overview():
    try:
        return get_graph_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/subgraph")
def graph_subgraph(
    drug_name: Optional[str] = Query(default=None, description="Drug name for targeted path, or 'all'"),
    disease_id: str = Query(default="DIS:IPF", description="Disease ID")
):
    try:
        return get_subgraph(drug_name=drug_name, disease_id=disease_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/comparison")
def graph_comparison():
    try:
        return get_keyword_vs_graph_comparison()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/papers")
def graph_papers(
    drug_name: Optional[str] = Query(default=None, description="Filter papers by drug name")
):
    try:
        papers = get_ingested_papers(drug_name=drug_name)
        return {
            "papers_count": len(papers),
            "papers": papers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/paths")
def graph_paths(
    disease_id: str = Query(default="DIS:IPF", description="Disease entity ID"),
    drug_name: Optional[str] = Query(default=None, description="Filter paths by drug name (e.g. Nintedanib, Imatinib)")
):
    try:
        paths = find_evidence_paths(disease_id=disease_id, drug_name=drug_name)
        return {
            "disease_id": disease_id,
            "drug_name": drug_name,
            "paths_count": len(paths),
            "paths": paths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/candidates")
def candidate_drugs(
    disease_id: str = Query(default="DIS:IPF", description="Disease entity ID")
):
    try:
        candidates = get_candidate_drugs_with_evidence(disease_id=disease_id)
        return {
            "disease_id": disease_id,
            "candidates_count": len(candidates),
            "candidates": candidates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/conflicts")
def conflicting_evidence(
    disease_id: str = Query(default="DIS:IPF", description="Disease entity ID")
):
    try:
        conflicts = get_conflicting_evidence_report(disease_id=disease_id)
        return {
            "disease_id": disease_id,
            "conflicts_count": len(conflicts),
            "conflicts": conflicts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/search")
def search_entities(
    q: str = Query(..., min_length=1, description="Search term for disease, drug, gene, or pathway")
):
    try:
        results = search_biomedical_entities(q)
        return {
            "query": q,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/investigate")
def agent_investigate(
    question: str = Query(..., min_length=2, description="Research question or candidate medicine"),
    drug_name: Optional[str] = Query(default=None, description="Optional candidate medicine to investigate"),
    session_id: Optional[str] = Query(default=None, description="Persistent research session identifier"),
):
    """Return a graph-grounded research synthesis with its retrieval trace."""
    try:
        return investigate_with_graph(question=question, drug_name=drug_name, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/summarize-papers")
def summarize_papers(
    question: str = Query(..., min_length=2),
    drug_name: str = Query(..., min_length=2),
    session_id: str = Query(default="demo-researcher", min_length=2),
):
    try:
        return summarize_research_papers(question, drug_name, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/memory")
def research_memory(session_id: str = Query(default="demo-researcher", min_length=2)):
    try:
        return get_research_memory(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    neo4j_conn.close_driver()

