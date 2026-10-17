"""Persistent, auditable research-session memory stored alongside the knowledge graph.

The model follows Neo4j Agent Memory's three layers: short-term messages,
long-term entity links, and application-recorded reasoning/tool traces. It is kept
dependency-free so the MVP works without an embedding-provider API key.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from app.db.neo4j import neo4j_conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_research_turn(session_id: str, question: str, answer: str, entity_ids: List[str], paper_ids: List[str]) -> None:
    """Persist an input, answer, entity mentions, and the visible retrieval trace."""
    user_message_id, assistant_message_id, trace_id, step_id, tool_call_id = [str(uuid4()) for _ in range(5)]
    timestamp = _now()
    with neo4j_conn.get_session() as session:
        session.run("""
            MERGE (c:Conversation {id: $session_id})
            ON CREATE SET c.created_at = $timestamp
            SET c.updated_at = $timestamp
            CREATE (u:Message {id: $user_id, role: 'user', content: $question, created_at: $timestamp})
            CREATE (a:Message {id: $assistant_id, role: 'assistant', content: $answer, created_at: $timestamp})
            MERGE (c)-[:HAS_MESSAGE]->(u)
            MERGE (c)-[:HAS_MESSAGE]->(a)
            CREATE (t:ReasoningTrace {id: $trace_id, kind: 'graph_grounded_research', created_at: $timestamp})
            CREATE (s:ReasoningStep {id: $step_id, order: 1, description: 'Retrieved connected paper and evidence records from the IPF graph.'})
            CREATE (call:ToolCall {id: $call_id, name: 'neo4j_graph_retrieval', result: 'completed'})
            MERGE (t)-[:INITIATED_BY]->(u)
            MERGE (t)-[:HAS_STEP]->(s)
            MERGE (s)-[:USES_TOOL]->(call)
        """, session_id=session_id, timestamp=timestamp, user_id=user_message_id,
             assistant_id=assistant_message_id, question=question, answer=answer,
             trace_id=trace_id, step_id=step_id, call_id=tool_call_id).consume()
        session.run("""
            MATCH (u:Message {id: $user_id}), (a:Message {id: $assistant_id}), (s:ReasoningStep {id: $step_id})
            UNWIND $entity_ids AS entity_id
            MATCH (entity {id: entity_id})
            MERGE (u)-[:MENTIONS]->(entity)
            MERGE (a)-[:MENTIONS]->(entity)
            MERGE (s)-[:TOUCHED]->(entity)
        """, user_id=user_message_id, assistant_id=assistant_message_id, step_id=step_id,
             entity_ids=entity_ids).consume()
        session.run("""
            MATCH (a:Message {id: $assistant_id})
            UNWIND $paper_ids AS paper_id
            MATCH (paper:ResearchPaper {id: paper_id})
            MERGE (a)-[:CITES]->(paper)
        """, assistant_id=assistant_message_id, paper_ids=paper_ids).consume()


def get_research_memory(session_id: str) -> Dict[str, Any]:
    with neo4j_conn.get_session() as session:
        messages = session.run("""
            MATCH (:Conversation {id: $session_id})-[:HAS_MESSAGE]->(m:Message)
            RETURN m.role AS role, m.content AS content, m.created_at AS created_at
            ORDER BY m.created_at DESC LIMIT 6
        """, session_id=session_id).data()
        entities = session.run("""
            MATCH (:Conversation {id: $session_id})-[:HAS_MESSAGE]->(:Message)-[:MENTIONS]->(e)
            RETURN DISTINCT coalesce(e.name, e.title, e.symbol, e.id) AS name, labels(e)[0] AS type
            LIMIT 12
        """, session_id=session_id).data()
        traces = session.run("""
            MATCH (t:ReasoningTrace)-[:INITIATED_BY]->(:Message)<-[:HAS_MESSAGE]-(:Conversation {id: $session_id})
            RETURN count(t) AS count
        """, session_id=session_id).single()["count"]
    return {"session_id": session_id, "messages": messages, "entities": entities, "reasoning_traces": traces}
