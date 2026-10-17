"""LLM synthesis for evidence already retrieved from Neo4j.

The model is grounded strictly on facts retrieved from the Neo4j knowledge graph.
"""
from typing import Any, Dict, List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_research_chat_response(
    question: str,
    matched_drug: Optional[str] = None,
    paths: Optional[List[Dict[str, Any]]] = None,
    papers: Optional[List[Dict[str, Any]]] = None,
    candidates: Optional[List[Dict[str, Any]]] = None,
    memory_messages: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Generates an intelligent, conversational response grounded in Neo4j graph facts."""
    if not settings.GROQ_API_KEY:
        return {
            "text": "Groq API key is not configured. Please add GROQ_API_KEY to your .env file.",
            "mode": "extractive_fallback"
        }

    from groq import Groq

    # Build graph context
    context_parts = []
    
    if matched_drug:
        context_parts.append(f"Target Candidate Drug: {matched_drug}")
    
    if candidates:
        cand_summaries = [
            f"- {c['drug_name']} ({c['approval_status']}): Targets [{', '.join(c.get('targets', []))}], "
            f"Evidence tier: {c.get('best_tier')}, {c.get('supporting_evidence_count', 0)} supporting, "
            f"{c.get('negative_evidence_count', 0)} negative/no-effect records."
            for c in candidates[:5]
        ]
        context_parts.append("Candidate Drugs in Neo4j Graph:\n" + "\n".join(cand_summaries))

    if paths:
        path_summaries = [
            f"- Path: Disease({p['disease_name']}) -> Pathway({p['pathway_name']}) -> Gene({p['gene_symbol']}) "
            f"-> Drug({p['drug_name']}) -> Trial({p.get('study_nct_id', 'N/A')}) [Tier {p.get('evidence_tier')}: {p.get('evidence_direction')}]"
            for p in paths[:5]
        ]
        context_parts.append("Key Multi-Hop Traversal Paths:\n" + "\n".join(path_summaries))

    if papers:
        paper_summaries = [
            f"- [PMID {p['pmid']}] {p['title']} ({p['journal']}, {p['pub_date']}): {p['abstract'][:200]}..."
            for p in papers[:4]
        ]
        context_parts.append("Retrieved Research Papers from Neo4j:\n" + "\n".join(paper_summaries))

    graph_context = "\n\n".join(context_parts) if context_parts else "General IPF knowledge graph available."

    system_prompt = (
        "You are MedTrail's intelligent biomedical research copilot specialized in Idiopathic Pulmonary Fibrosis (IPF). "
        "You help biomedical researchers understand drug repurposing, multi-hop biological pathways, clinical trial results, "
        "and literature findings.\n\n"
        "GUIDELINES:\n"
        "1. GROUNDING: Ground your answers in the provided Neo4j knowledge graph data (drugs, targets, clinical trials, and papers).\n"
        "2. CONFLICTING EVIDENCE: Always preserve and highlight conflicting evidence (e.g. Imatinib showed promise in mice [Tier 3] but FAILED in human Phase 2 trials [Tier 1, NCT00130520]).\n"
        "3. CITATIONS: Whenever mentioning a trial or paper, cite the PMID or NCT ID if available.\n"
        "4. UNCLEAR INPUT: If the user query is very short, typo-ridden, or ambiguous (e.g. 'hgk', 'test'), politely state that you did not understand and suggest 2-3 specific topics they can investigate (e.g. Nintedanib discovery, Imatinib failure, or Pirfenidone mechanisms).\n"
        "5. TONE: Professional, concise, scientific, and clear. Format using clean Markdown with bullet points where appropriate."
    )

    user_prompt = f"""Researcher Question: {question}

Context retrieved from Neo4j Knowledge Graph:
{graph_context}
"""

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            temperature=0.2,
            max_tokens=600,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        answer = completion.choices[0].message.content.strip()
        return {"text": answer, "mode": "groq_grounded"}
    except Exception as e:
        logger.error(f"Groq chat completion failed: {e}")
        return {
            "text": f"Knowledge graph retrieved {len(paths or [])} path(s). (Groq LLM synthesis encountered an issue: {str(e)})",
            "mode": "extractive_fallback"
        }


def synthesize_paper_summary(question: str, papers: List[Dict[str, Any]], memory_messages: List[Dict[str, Any]]) -> Dict[str, str]:
    if not settings.GROQ_API_KEY:
        return {"text": "LLM synthesis is not configured; showing the graph-grounded extractive summary instead.", "mode": "extractive_fallback"}

    from groq import Groq
    source_context = "\n\n".join(
        f"[PMID {paper['pmid']}] {paper['title']} | {paper['journal']} | tier {paper.get('tier', 1)} | {paper.get('direction', 'supports')}\n"
        f"Abstract: {paper['abstract']}\nGraph evidence: {paper.get('evidence_summary', 'Supported by clinical trial/literature')}"
        for paper in papers
    )
    recent_questions = "\n".join(message["content"] for message in memory_messages if message.get("role") == "user")
    prompt = f"""You are MedTrail's biomedical research synthesis assistant.
Answer only from the supplied graph-retrieved papers. Do not introduce facts, studies, quantities, or citations not in the context. Preserve conflicts and explicitly say when a human clinical result is negative. This is research support, never treatment advice. Cite every sentence with [PMID ...] from the supplied context. Use 3 concise bullets: finding, evidence quality/conflict, caveat.

Researcher question: {question}
Prior session questions (context only): {recent_questions or 'None'}

Retrieved sources:
{source_context}"""
    try:
        completion = Groq(api_key=settings.GROQ_API_KEY).chat.completions.create(
            model=settings.GROQ_MODEL,
            temperature=0.1,
            max_tokens=500,
            messages=[
                {"role": "system", "content": "You produce source-bounded biomedical research summaries."},
                {"role": "user", "content": prompt},
            ],
        )
        text = completion.choices[0].message.content
        if not text or not text.strip():
            return {"text": "The LLM returned no readable text; showing the graph-grounded extractive summary instead.", "mode": "extractive_fallback"}
        return {"text": text.strip(), "mode": "groq_grounded"}
    except Exception as e:
        logger.error(f"Groq paper summary failed: {e}")
        return {"text": f"The LLM request encountered an error ({str(e)}); showing graph records instead.", "mode": "extractive_fallback"}
