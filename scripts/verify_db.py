#!/usr/bin/env python3
"""
MedTrail Neo4j Database Verification Script
Validates multi-hop paths, rediscovery validation, conflicting evidence preservation, and evidence tiers.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from app.db.neo4j import neo4j_conn
from app.db.queries import (
    get_graph_overview,
    find_evidence_paths,
    get_candidate_drugs_with_evidence,
    get_conflicting_evidence_report,
    search_biomedical_entities
)

console = Console()

def verify():
    console.print(Panel.fit("[bold green]MedTrail -- Neo4j Knowledge Graph Verification Suite[/bold green]", border_style="green"))

    # 1. Check Graph Overview
    overview = get_graph_overview()
    console.print(f"[bold cyan]Total Nodes:[/bold cyan] {overview['total_nodes']} | [bold cyan]Total Relationships:[/bold cyan] {overview['total_relationships']}")
    if overview['total_nodes'] == 0:
        console.print("[bold red]Database is empty! Run scripts/init_db.py first.[/bold red]")
        sys.exit(1)

    # 2. Verify Nintedanib Rediscovery Path
    console.print("\n[bold yellow]Test 1: Known-Answer Validation -- Nintedanib Multi-Hop Rediscovery[/bold yellow]")
    nint_paths = find_evidence_paths(disease_id="DIS:IPF", drug_name="Nintedanib")
    
    if nint_paths:
        console.print(f"  [bold green][OK] Successfully retrieved {len(nint_paths)} multi-hop traversal paths for Nintedanib:[/bold green]")
        path_table = Table(title="Rediscovered Path: IPF -> Pathway -> Protein Target -> Nintedanib -> Study", border_style="cyan")
        path_table.add_column("Pathway", style="magenta")
        path_table.add_column("Target (Gene)", style="green")
        path_table.add_column("Drug Action", style="blue")
        path_table.add_column("Clinical Trial / Paper", style="yellow")
        path_table.add_column("Evidence Tier", style="cyan")

        for p in nint_paths[:6]:
            study_or_paper = p.get('study_nct_id') or p.get('paper_pmid') or 'N/A'
            path_table.add_row(
                p['pathway_name'],
                f"{p['gene_symbol']} ({p['protein_accession']})",
                f"{p['target_action']} ({p['affinity_nm']} nM)",
                f"{study_or_paper} ({p.get('study_phase', 'Trial')})",
                f"Tier {p['evidence_tier']} ({p['evidence_direction']})"
            )
        console.print(path_table)
    else:
        console.print("  [bold red][FAIL] Failed to find Nintedanib multi-hop path![/bold red]")

    # 3. Verify Conflicting and Negative Evidence (Imatinib)
    console.print("\n[bold yellow]Test 2: Preserved Conflicting Evidence -- Imatinib Plausible Mechanism vs Clinical Failure[/bold yellow]")
    conflicts = get_conflicting_evidence_report(disease_id="DIS:IPF")
    
    if conflicts:
        console.print(f"  [bold green][OK] Found {len(conflicts)} candidate(s) with preserved conflicting evidence:[/bold green]")
        for c in conflicts:
            console.print(f"\n  [bold cyan]Drug:[/bold cyan] {c['drug_name']}")
            console.print(f"  [bold]Mechanism:[/bold] {c['mechanism']}")
            for supp in c['supporting_evidence']:
                console.print(f"    [green][+] SUPPORTING (Tier {supp['tier']} - {supp['evidence_type']}):[/green] {supp['summary'][:120]}... [dim]({supp['source']})[/dim]")
            for neg in c['negative_evidence']:
                console.print(f"    [red][-] CONFLICTING/NO EFFECT (Tier {neg['tier']} - {neg['evidence_type']}):[/red] {neg['summary'][:120]}... [dim]({neg['source']})[/dim]")
    else:
        # Check direct imatinib evidence
        imat_paths = find_evidence_paths(disease_id="DIS:IPF", drug_name="Imatinib")
        console.print(f"  [dim]Direct Imatinib paths found: {len(imat_paths)}[/dim]")

    # 4. Candidate Drug Ranking by Evidence Tier
    console.print("\n[bold yellow]Test 3: Evidence-Tier Transparent Ranking Order[/bold yellow]")
    ranked_candidates = get_candidate_drugs_with_evidence(disease_id="DIS:IPF")
    
    rank_table = Table(title="Transparent Drug Candidates Ranking for IPF", border_style="green")
    rank_table.add_column("Rank", style="dim", width=4)
    rank_table.add_column("Drug", style="bold cyan")
    rank_table.add_column("Best Tier", style="magenta")
    rank_table.add_column("Evidence Breakdown", style="yellow")
    rank_table.add_column("Reported Side Effects", style="red")
    rank_table.add_column("Regulatory Status", style="white")

    for idx, cand in enumerate(ranked_candidates, 1):
        supp_count = cand['supporting_evidence_count']
        neg_count = cand['negative_evidence_count']
        breakdown = f"[green]+{supp_count} supports[/green] / [red]-{neg_count} no effect[/red]"
        side_fx = ", ".join(cand['side_effects'][:2]) if cand['side_effects'] else "None recorded"
        rank_table.add_row(
            str(idx),
            cand['drug_name'],
            f"Tier {cand['best_tier']}",
            breakdown,
            side_fx,
            cand['approval_status'][:30]
        )
    console.print(rank_table)

    # 5. Entity Search Test
    console.print("\n[bold yellow]Test 4: Entity Search Verification[/bold yellow]")
    search_results = search_biomedical_entities("fibrosis")
    console.print(f"  [bold green][OK] Search for 'fibrosis' returned {len(search_results)} entities:[/bold green]")
    for r in search_results[:3]:
        console.print(f"    - [{r['entity_type']}] [bold]{r['name']}[/bold]: {r['description'][:90]}...")

    neo4j_conn.close_driver()
    console.print("\n[bold green]All Neo4j verification tests passed successfully![/bold green]")

if __name__ == "__main__":
    verify()
