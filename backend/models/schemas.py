"""
NexusGraph - Pydantic Models for Cross-Tool Intelligence Layer
Defines all data structures for Slack, Jira, GitHub, and the Work Graph.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class NodeType(str, Enum):
    PERSON = "person"
    TASK = "task"
    PR = "pr"
    MESSAGE = "message"
    CHANNEL = "channel"


class EdgeType(str, Enum):
    BLOCKED_BY = "BLOCKED_BY"
    ASSIGNED_TO = "ASSIGNED_TO"
    DISCUSSING = "DISCUSSING"
    COMMITTED_BY = "COMMITTED_BY"
    MERGED_BY = "MERGED_BY"
    MENTIONS = "MENTIONS"
    LINKED_TO = "LINKED_TO"


class ToolStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


# ============================================================================
# SLACK MODELS
# ============================================================================

class SlackMessage(BaseModel):
    """Represents a Slack message from the Chat tool."""
    id: str = Field(..., description="Unique message identifier")
    user: str = Field(..., description="User ID who sent the message")
    user_name: str = Field(..., description="Display name of the user")
    channel: str = Field(..., description="Channel ID")
    channel_name: str = Field(..., description="Channel display name")
    timestamp: datetime = Field(..., description="Message timestamp")
    message: str = Field(..., description="Message content")
    thread_id: Optional[str] = Field(None, description="Parent thread ID if in a thread")
    reply_count: int = Field(0, description="Number of replies in thread")
    reactions: int = Field(0, description="Number of reactions")


# ============================================================================
# JIRA MODELS
# ============================================================================

class JiraTicket(BaseModel):
    """Represents a Jira ticket from the Tasks tool."""
    ticket_id: str = Field(..., description="Ticket ID (e.g., PROJ-123)")
    title: str = Field(..., description="Ticket title/summary")
    description: Optional[str] = Field(None, description="Ticket description")
    status: Literal["open", "in_progress", "review", "blocked", "closed"] = Field(
        ..., description="Current ticket status"
    )
    assignee: Optional[str] = Field(None, description="Assigned user ID")
    assignee_name: Optional[str] = Field(None, description="Assigned user display name")
    reporter: str = Field(..., description="Reporter user ID")
    priority: Literal["critical", "high", "medium", "low"] = Field(
        "medium", description="Ticket priority"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="List of blocking ticket IDs"
    )
    project: str = Field(..., description="Project key")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# ============================================================================
# GITHUB MODELS
# ============================================================================

class GitHubPR(BaseModel):
    """Represents a GitHub Pull Request from the Code tool."""
    pr_id: str = Field(..., description="Pull request ID/number")
    title: str = Field(..., description="PR title")
    author: str = Field(..., description="Author user ID")
    author_name: str = Field(..., description="Author display name")
    linked_ticket: Optional[str] = Field(None, description="Linked Jira ticket ID")
    status: Literal["open", "merged", "closed", "draft"] = Field(
        ..., description="PR status"
    )
    repo: str = Field(..., description="Repository name")
    branch: str = Field(..., description="Source branch name")
    last_commit_date: datetime = Field(..., description="Last commit timestamp")
    additions: int = Field(0, description="Lines added")
    deletions: int = Field(0, description="Lines deleted")
    review_status: Optional[Literal["pending", "approved", "changes_requested"]] = Field(
        None, description="Review status"
    )


# ============================================================================
# GRAPH MODELS
# ============================================================================

class GraphNode(BaseModel):
    """Represents a node in the Work Graph."""
    id: str = Field(..., description="Unique node identifier")
    type: NodeType = Field(..., description="Node type")
    label: str = Field(..., description="Display label")
    metadata: dict = Field(default_factory=dict, description="Additional node data")
    activity_level: float = Field(0.0, ge=0.0, le=1.0, description="Activity score 0-1")
    color: Optional[str] = Field(None, description="Node color for visualization")
    size: Optional[float] = Field(None, description="Node size for visualization")


class GraphEdge(BaseModel):
    """Represents an edge in the Work Graph."""
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: EdgeType = Field(..., description="Edge relationship type")
    weight: float = Field(1.0, description="Edge weight")
    animated: bool = Field(False, description="Whether edge should be animated")
    metadata: dict = Field(default_factory=dict, description="Additional edge data")


class WorkGraph(BaseModel):
    """The complete Work Graph structure."""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


# ============================================================================
# ANALYSIS MODELS
# ============================================================================

class Bottleneck(BaseModel):
    """A detected bottleneck in the workflow."""
    task_id: str
    task_title: str
    pr_id: Optional[str]
    pr_status: Optional[str]
    last_slack_activity: Optional[datetime]
    hours_since_activity: float
    severity: Literal["low", "medium", "high", "critical"]
    description: str


class OverloadScore(BaseModel):
    """Overload score for a person."""
    person_id: str
    person_name: str
    task_count: int
    activity_count: int
    overload_ratio: float
    risk_level: Literal["low", "medium", "high", "critical"]


class RiskItem(BaseModel):
    """A detected risk in the workflow."""
    pr_id: str
    pr_title: str
    ticket_id: Optional[str]
    ticket_status: Optional[str]
    risk_type: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]


class ShadowTask(BaseModel):
    """An untracked task detected from Slack activity."""
    thread_id: str
    channel: str
    message_count: int
    participants: List[str]
    first_message: datetime
    last_message: datetime
    sample_text: str
    suggested_ticket_title: str


class InsightsReport(BaseModel):
    """Complete analysis report."""
    bottlenecks: List[Bottleneck] = Field(default_factory=list)
    overload_scores: List[OverloadScore] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    shadow_tasks: List[ShadowTask] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# PULSE STATUS MODELS
# ============================================================================

class ToolPulse(BaseModel):
    """Status for a single tool."""
    name: str
    status: ToolStatus
    metric: str
    metric_value: int


class PulseStatus(BaseModel):
    """Complete pulse status for all tools."""
    github: ToolPulse
    jira: ToolPulse
    slack: ToolPulse
    last_sync: datetime


# ============================================================================
# CHAT MODELS
# ============================================================================

class ChatQuery(BaseModel):
    """User query for the AI chat interface."""
    query: str = Field(..., description="User's natural language query")
    context: Optional[str] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    """AI response to a user query."""
    response: str = Field(..., description="AI-generated response")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score")
    related_nodes: List[str] = Field(default_factory=list, description="Related graph node IDs")


# ============================================================================
# 24-HOUR BRIEF MODEL
# ============================================================================

class ActivityBrief(BaseModel):
    """30-second brief of recent activity."""
    summary: str
    key_updates: List[str]
    hot_threads: int
    blocked_tasks: int
    merged_prs: int
    period_start: datetime
    period_end: datetime
