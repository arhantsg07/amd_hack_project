"""
NexusGraph - API Routes
REST endpoints for the Cross-Tool Intelligence Layer.
"""

from fastapi import APIRouter, HTTPException
from models.schemas import (
    WorkGraph, InsightsReport, PulseStatus, ToolPulse, ToolStatus,
    ChatQuery, ChatResponse, ActivityBrief,
    Bottleneck, OverloadScore, RiskItem, ShadowTask
)
from graph.work_graph import graph_service
from analysis.intelligence import intelligence_service
from analysis.chat_engine import ai_engine
from data.mock_data import mock_store
from datetime import datetime
from typing import List


router = APIRouter(prefix="/api", tags=["NexusGraph"])


# ============================================================================
# GRAPH ENDPOINTS
# ============================================================================

@router.get("/graph", response_model=WorkGraph)
async def get_work_graph(refresh: bool = False):
    """
    Get the complete Work Graph with all nodes and edges.
    
    - **refresh**: If true, regenerates the graph from source data
    """
    try:
        graph = graph_service.get_graph(refresh=refresh)
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build graph: {str(e)}")


@router.get("/graph/search")
async def search_graph(query: str):
    """
    Search nodes in the Work Graph by label or metadata.
    """
    if not query or len(query) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    results = graph_service.search_nodes(query)
    return {"results": results, "count": len(results)}


@router.get("/graph/node/{node_id}")
async def get_node(node_id: str):
    """
    Get a specific node and its connections.
    """
    node = graph_service.get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    
    connected = graph_service.get_connected_nodes(node_id)
    return {"node": node, "connected": connected}


# ============================================================================
# INSIGHTS ENDPOINTS
# ============================================================================

@router.get("/insights", response_model=InsightsReport)
async def get_full_insights():
    """
    Get complete insights report including bottlenecks, overloads, risks, and shadow tasks.
    """
    return intelligence_service.get_full_insights()


@router.get("/insights/bottlenecks", response_model=List[Bottleneck])
async def get_bottlenecks():
    """
    Get detected bottlenecks where PRs are open but Slack activity is stale.
    """
    return intelligence_service.get_bottlenecks()


@router.get("/insights/overload", response_model=List[OverloadScore])
async def get_overload_scores():
    """
    Get overload scores for team members (task-to-activity ratio).
    """
    return intelligence_service.get_overload_scores()


@router.get("/insights/risks", response_model=List[RiskItem])
async def get_risks():
    """
    Get workflow risks (merged PRs without closed tickets, etc.).
    """
    return intelligence_service.get_risks()


@router.get("/insights/shadow-tasks", response_model=List[ShadowTask])
async def get_shadow_tasks():
    """
    Get shadow tasks (untracked Slack discussions with high activity).
    """
    return intelligence_service.get_shadow_tasks()


@router.get("/insights/brief", response_model=ActivityBrief)
async def get_activity_brief():
    """
    Get 24-hour activity brief summary.
    """
    return intelligence_service.get_24h_brief()


# ============================================================================
# PULSE STATUS ENDPOINT
# ============================================================================

@router.get("/pulse", response_model=PulseStatus)
async def get_pulse_status():
    """
    Get live status summary for all connected tools.
    """
    tickets, prs, messages = mock_store.get_all_data()
    
    # Calculate metrics
    open_prs = sum(1 for p in prs if p.status == "open")
    blocked_tasks = sum(1 for t in tickets if t.status == "blocked")
    
    # Count "hot" threads (with recent activity)
    thread_ids = set()
    for msg in messages:
        if msg.thread_id and msg.reply_count > 5:
            thread_ids.add(msg.thread_id)
    hot_threads = len(thread_ids)
    
    return PulseStatus(
        github=ToolPulse(
            name="GitHub",
            status=ToolStatus.ACTIVE,
            metric="Open PRs",
            metric_value=open_prs,
        ),
        jira=ToolPulse(
            name="Jira",
            status=ToolStatus.ACTIVE,
            metric="Blocked",
            metric_value=blocked_tasks,
        ),
        slack=ToolPulse(
            name="Slack",
            status=ToolStatus.ACTIVE,
            metric="Hot Threads",
            metric_value=hot_threads,
        ),
        last_sync=datetime.now(),
    )


# ============================================================================
# CHAT ENDPOINT
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_graph(query: ChatQuery):
    """
    Ask natural language questions about the Work Graph.
    
    Examples:
    - "What is blocking NEXUS-100?"
    - "Who is overloaded?"
    - "Show me bottlenecks"
    """
    if not query.query or len(query.query) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    return ai_engine.query(query)


# ============================================================================
# DATA MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/data/regenerate")
async def regenerate_mock_data():
    """
    Regenerate all mock data. Useful for testing different scenarios.
    """
    mock_store.regenerate()
    graph_service.get_graph(refresh=True)
    return {"status": "success", "message": "Mock data regenerated", "timestamp": datetime.now()}


@router.get("/data/stats")
async def get_data_stats():
    """
    Get statistics about the current data.
    """
    tickets, prs, messages = mock_store.get_all_data()
    graph = graph_service.get_graph()
    
    return {
        "tickets": len(tickets),
        "prs": len(prs),
        "messages": len(messages),
        "graph_nodes": len(graph.nodes),
        "graph_edges": len(graph.edges),
        "last_generated": mock_store.last_generated,
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "service": "NexusGraph", "timestamp": datetime.now()}
