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
)

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

@app.get("/")
def root():
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
            "search": "/api/graph/search?q=fibrosis"
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

@app.on_event("shutdown")
def shutdown_event():
    neo4j_conn.close_driver()
