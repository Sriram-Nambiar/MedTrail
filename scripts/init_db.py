#!/usr/bin/env python3
"""
MedTrail Neo4j Database Initialization Script
Initializes constraints, indexes, and populates the curated Idiopathic Pulmonary Fibrosis (IPF) knowledge graph.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from app.db.neo4j import neo4j_conn
from app.db.schema import init_schema, get_schema_summary
from app.db.seed_ipf import seed_ipf_dataset, clear_existing_data
from app.db.queries import get_graph_overview

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("init_db")
console = Console()

def main():
    console.print(Panel.fit("[bold cyan]MedTrail -- Neo4j Knowledge Graph Initializer[/bold cyan]", border_style="cyan"))

    # 1. Test Connection
    try:
        conn_info = neo4j_conn.check_connection()
        console.print(f"[bold green][OK] Connected to Neo4j[/bold green]")
        console.print(f"  URI: [dim]{conn_info.get('uri')}[/dim]")
        console.print(f"  Edition: [yellow]{conn_info.get('server_name', 'Neo4j')} {conn_info.get('version', '')} ({conn_info.get('edition', '')})[/yellow]")
        console.print(f"  Database: [cyan]{conn_info.get('database')}[/cyan]\n")
    except Exception as e:
        console.print(f"[bold red][FAIL] Failed to connect to Neo4j:[/bold red] {e}")
        sys.exit(1)

    # 2. Initialize Constraints and Indexes
    console.print("[bold yellow]Step 1: Setting up Constraints & Indexes...[/bold yellow]")
    try:
        schema_res = init_schema()
        console.print(f"  [green][OK][/green] Constraints verified: {len(schema_res['constraints'])}")
        console.print(f"  [green][OK][/green] Indexes verified: {len(schema_res['indexes'])}")
        console.print(f"  [green][OK][/green] Fulltext indexes verified: {len(schema_res['fulltext_indexes'])}\n")
    except Exception as e:
        console.print(f"[bold red][FAIL] Error creating schema:[/bold red] {e}\n")

    # 3. Clean and Seed Dataset
    console.print("[bold yellow]Step 2: Populating Curated IPF Biomedical Graph...[/bold yellow]")
    try:
        # Clear out existing demo or movie nodes so MedTrail has a clean database
        clear_existing_data(clear_all=True)
        seed_result = seed_ipf_dataset()
        console.print("[bold green][OK] Ingestion complete![/bold green]\n")
    except Exception as e:
        console.print(f"[bold red][FAIL] Error during data seeding:[/bold red] {e}")
        neo4j_conn.close_driver()
        sys.exit(1)

    # 4. Display Summary Metrics
    console.print("[bold yellow]Step 3: Database Metrics Summary[/bold yellow]")
    overview = get_graph_overview()

    node_table = Table(title="Knowledge Graph Nodes by Label", border_style="blue")
    node_table.add_column("Node Label", style="cyan", no_wrap=True)
    node_table.add_column("Count", justify="right", style="green")

    for label, count in overview["nodes_by_label"].items():
        node_table.add_row(label, str(count))
    node_table.add_section()
    node_table.add_row("[bold]Total Nodes[/bold]", f"[bold]{overview['total_nodes']}[/bold]")
    console.print(node_table)

    rel_table = Table(title="Relationships by Type", border_style="magenta")
    rel_table.add_column("Relationship Type", style="magenta", no_wrap=True)
    rel_table.add_column("Count", justify="right", style="green")

    for rel_type, count in overview["relationships_by_type"].items():
        rel_table.add_row(rel_type, str(count))
    rel_table.add_section()
    rel_table.add_row("[bold]Total Relationships[/bold]", f"[bold]{overview['total_relationships']}[/bold]")
    console.print(rel_table)

    neo4j_conn.close_driver()
    console.print("\n[bold green][OK] MedTrail Neo4j database is ready for exploration and queries![/bold green]")

if __name__ == "__main__":
    main()
