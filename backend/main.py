"""
NexusGraph - Cross-Tool Intelligence Layer
Main FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from datetime import datetime

# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="NexusGraph API",
    description="""
    ## Cross-Tool Intelligence Layer
    
    Aggregates signals from Slack, Jira, and GitHub into a unified Work Graph.
    
    ### Features
    - **Work Graph**: Unified view of all work items and their relationships
    - **Entity Resolution**: Automatically links related items across tools
    - **Intelligence Analysis**: Bottleneck detection, overload scoring, risk prediction
    - **AI Chat**: Natural language queries about your workflow
    
    ### Diagnostic Functions
    1. **Bottleneck Detector**: Finds stale PRs with no recent discussion
    2. **Overload Scorer**: Identifies team members with high task-to-activity ratios
    3. **Risk Predictor**: Flags merged PRs without closed tickets
    4. **Shadow Task Detector**: Finds untracked work in Slack threads
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ROUTES
# ============================================================================

app.include_router(router)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "NexusGraph API",
        "version": "1.0.0",
        "description": "Cross-Tool Intelligence Layer",
        "docs": "/docs",
        "health": "/api/health",
        "timestamp": datetime.now(),
    }


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🚀 NexusGraph API starting...")
    print("📊 Initializing mock data...")
    from data.mock_data import mock_store
    mock_store.regenerate()
    print("🔗 Building initial Work Graph...")
    from graph.work_graph import graph_service
    graph_service.get_graph(refresh=True)
    print("✅ NexusGraph API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 NexusGraph API shutting down...")


# ============================================================================
# RUN WITH UVICORN (for development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
