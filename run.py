#!/usr/bin/env python3
"""
MedTrail Application Launcher
Starts the FastAPI backend (and serves the frontend visualizer at http://localhost:8000).
"""

import sys
import uvicorn
from app.core.config import settings

def main():
    print("=" * 60)
    print("  MedTrail — Graph-Powered Biomedical Discovery")
    print("  Knowledge Graph: Neo4j Aura (Idiopathic Pulmonary Fibrosis)")
    print(f"  Web Interface & API: http://localhost:{settings.API_PORT}")
    print(f"  Interactive API Docs: http://localhost:{settings.API_PORT}/docs")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )

if __name__ == "__main__":
    main()
