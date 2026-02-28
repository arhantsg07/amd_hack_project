"""
NexusGraph - Work Graph Engine
Performs entity resolution and builds the unified Work Graph.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
from fuzzywuzzy import fuzz
from models.schemas import (
    GraphNode, GraphEdge, WorkGraph, NodeType, EdgeType,
    SlackMessage, JiraTicket, GitHubPR
)
from data.mock_data import mock_store, USERS


# ============================================================================
# ENTITY RESOLUTION
# ============================================================================

class EntityResolver:
    """
    Resolves entities across different tools using fuzzy matching and pattern recognition.
    Links Slack messages mentioning "Ticket-123" to Jira tickets and GitHub PRs.
    """
    
    # Patterns for ticket ID extraction
    TICKET_PATTERNS = [
        r'\b([A-Z]+-\d+)\b',  # PROJ-123
        r'#(\d+)',             # #123
        r'ticket[:\s]+(\d+)',  # ticket: 123 or ticket 123
        r'issue[:\s]+(\d+)',   # issue: 123
    ]
    
    def __init__(self):
        self.ticket_index: Dict[str, JiraTicket] = {}
        self.pr_index: Dict[str, GitHubPR] = {}
        self.user_index: Dict[str, dict] = {}
        
    def build_indices(
        self,
        tickets: List[JiraTicket],
        prs: List[GitHubPR]
    ):
        """Build lookup indices for fast resolution."""
        self.ticket_index = {t.ticket_id.upper(): t for t in tickets}
        self.pr_index = {p.pr_id: p for p in prs}
        self.user_index = {u["id"]: u for u in USERS}
    
    def extract_ticket_references(self, text: str) -> List[str]:
        """Extract all ticket references from text."""
        references = []
        for pattern in self.TICKET_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)
        return list(set(references))
    
    def fuzzy_match_ticket(
        self,
        text: str,
        threshold: int = 70
    ) -> Optional[JiraTicket]:
        """Find ticket using fuzzy matching on title."""
        best_match = None
        best_score = 0
        
        for ticket in self.ticket_index.values():
            # Check title similarity
            score = fuzz.partial_ratio(text.lower(), ticket.title.lower())
            if score > best_score and score >= threshold:
                best_score = score
                best_match = ticket
        
        return best_match
    
    def resolve_message_to_ticket(
        self,
        message: SlackMessage
    ) -> Optional[JiraTicket]:
        """Resolve a Slack message to a Jira ticket."""
        # First try exact pattern matching
        refs = self.extract_ticket_references(message.message)
        for ref in refs:
            ticket_id = ref.upper()
            if ticket_id in self.ticket_index:
                return self.ticket_index[ticket_id]
            # Try with common project prefixes
            for project in ["NEXUS", "AUTH", "API", "UI", "INFRA"]:
                full_id = f"{project}-{ref}"
                if full_id in self.ticket_index:
                    return self.ticket_index[full_id]
        
        # Fall back to fuzzy matching
        return self.fuzzy_match_ticket(message.message)
    
    def resolve_pr_to_ticket(self, pr: GitHubPR) -> Optional[JiraTicket]:
        """Resolve a GitHub PR to a Jira ticket."""
        # Direct link
        if pr.linked_ticket:
            return self.ticket_index.get(pr.linked_ticket.upper())
        
        # Extract from title
        refs = self.extract_ticket_references(pr.title)
        for ref in refs:
            ticket_id = ref.upper()
            if ticket_id in self.ticket_index:
                return self.ticket_index[ticket_id]
        
        # Fuzzy match on title
        return self.fuzzy_match_ticket(pr.title, threshold=60)


# ============================================================================
# WORK GRAPH BUILDER
# ============================================================================

class WorkGraphBuilder:
    """Builds the unified Work Graph from multi-source data."""
    
    # Node colors by type
    NODE_COLORS = {
        NodeType.PERSON: "#00F0FF",    # Electric cyan
        NodeType.TASK: "#FFB800",      # Neon amber
        NodeType.PR: "#FF6B6B",        # Coral red
        NodeType.MESSAGE: "#9D4EDD",   # Purple
        NodeType.CHANNEL: "#06D6A0",   # Green
    }
    
    def __init__(self):
        self.resolver = EntityResolver()
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.edge_set: Set[Tuple[str, str, str]] = set()
    
    def _add_node(
        self,
        node_id: str,
        node_type: NodeType,
        label: str,
        metadata: dict = None,
        activity_level: float = 0.5
    ) -> GraphNode:
        """Add a node to the graph if it doesn't exist."""
        if node_id not in self.nodes:
            node = GraphNode(
                id=node_id,
                type=node_type,
                label=label,
                metadata=metadata or {},
                activity_level=activity_level,
                color=self.NODE_COLORS.get(node_type, "#FFFFFF"),
                size=self._calculate_node_size(node_type, activity_level),
            )
            self.nodes[node_id] = node
        return self.nodes[node_id]
    
    def _calculate_node_size(
        self,
        node_type: NodeType,
        activity_level: float
    ) -> float:
        """Calculate node size based on type and activity."""
        base_sizes = {
            NodeType.PERSON: 12,
            NodeType.TASK: 10,
            NodeType.PR: 8,
            NodeType.MESSAGE: 4,
            NodeType.CHANNEL: 6,
        }
        base = base_sizes.get(node_type, 6)
        return base * (0.5 + activity_level)
    
    def _add_edge(
        self,
        source: str,
        target: str,
        relationship: EdgeType,
        animated: bool = False,
        metadata: dict = None
    ):
        """Add an edge to the graph if it doesn't exist."""
        edge_key = (source, target, relationship.value)
        if edge_key not in self.edge_set:
            edge = GraphEdge(
                id=f"edge-{len(self.edges)}",
                source=source,
                target=target,
                relationship=relationship,
                animated=animated,
                metadata=metadata or {},
            )
            self.edges.append(edge)
            self.edge_set.add(edge_key)
    
    def build_graph(
        self,
        tickets: List[JiraTicket],
        prs: List[GitHubPR],
        messages: List[SlackMessage]
    ) -> WorkGraph:
        """Build the complete Work Graph."""
        self.nodes.clear()
        self.edges.clear()
        self.edge_set.clear()
        
        # Build resolver indices
        self.resolver.build_indices(tickets, prs)
        
        # Add person nodes
        self._add_person_nodes(tickets, prs, messages)
        
        # Add task nodes and relationships
        self._add_task_nodes(tickets)
        
        # Add PR nodes and relationships
        self._add_pr_nodes(prs)
        
        # Add message relationships
        self._add_message_relationships(messages)
        
        return WorkGraph(
            nodes=list(self.nodes.values()),
            edges=self.edges,
            last_updated=datetime.now(),
        )
    
    def _add_person_nodes(
        self,
        tickets: List[JiraTicket],
        prs: List[GitHubPR],
        messages: List[SlackMessage]
    ):
        """Add person nodes for all users involved."""
        person_activity: Dict[str, int] = {}
        
        # Count activity per person
        for ticket in tickets:
            if ticket.assignee:
                person_activity[ticket.assignee] = person_activity.get(ticket.assignee, 0) + 2
        
        for pr in prs:
            person_activity[pr.author] = person_activity.get(pr.author, 0) + 3
        
        for msg in messages:
            person_activity[msg.user] = person_activity.get(msg.user, 0) + 1
        
        # Normalize activity
        max_activity = max(person_activity.values()) if person_activity else 1
        
        for user in USERS:
            activity = person_activity.get(user["id"], 0) / max_activity
            self._add_node(
                node_id=f"person-{user['id']}",
                node_type=NodeType.PERSON,
                label=user["name"],
                metadata={"avatar": user["avatar"], "user_id": user["id"]},
                activity_level=activity,
            )
    
    def _add_task_nodes(self, tickets: List[JiraTicket]):
        """Add task nodes and their relationships."""
        for ticket in tickets:
            is_active = ticket.status in ["in_progress", "review"]
            activity = 0.9 if is_active else (0.3 if ticket.status == "open" else 0.1)
            
            self._add_node(
                node_id=f"task-{ticket.ticket_id}",
                node_type=NodeType.TASK,
                label=ticket.ticket_id,
                metadata={
                    "title": ticket.title,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "project": ticket.project,
                },
                activity_level=activity,
            )
            
            # ASSIGNED_TO relationship
            if ticket.assignee:
                self._add_edge(
                    source=f"task-{ticket.ticket_id}",
                    target=f"person-{ticket.assignee}",
                    relationship=EdgeType.ASSIGNED_TO,
                    animated=is_active,
                )
            
            # BLOCKED_BY relationships
            for dep in ticket.dependencies:
                self._add_edge(
                    source=f"task-{ticket.ticket_id}",
                    target=f"task-{dep}",
                    relationship=EdgeType.BLOCKED_BY,
                    animated=True,
                    metadata={"blocking": True},
                )
    
    def _add_pr_nodes(self, prs: List[GitHubPR]):
        """Add PR nodes and their relationships."""
        for pr in prs:
            is_active = pr.status == "open"
            activity = 0.9 if is_active else (0.5 if pr.status == "merged" else 0.2)
            
            self._add_node(
                node_id=f"pr-{pr.pr_id}",
                node_type=NodeType.PR,
                label=pr.pr_id,
                metadata={
                    "title": pr.title,
                    "status": pr.status,
                    "repo": pr.repo,
                    "branch": pr.branch,
                    "additions": pr.additions,
                    "deletions": pr.deletions,
                },
                activity_level=activity,
            )
            
            # COMMITTED_BY relationship
            self._add_edge(
                source=f"pr-{pr.pr_id}",
                target=f"person-{pr.author}",
                relationship=EdgeType.COMMITTED_BY,
                animated=is_active,
            )
            
            # LINKED_TO relationship with ticket
            linked_ticket = self.resolver.resolve_pr_to_ticket(pr)
            if linked_ticket:
                self._add_edge(
                    source=f"pr-{pr.pr_id}",
                    target=f"task-{linked_ticket.ticket_id}",
                    relationship=EdgeType.LINKED_TO,
                    animated=pr.status == "open",
                )
    
    def _add_message_relationships(self, messages: List[SlackMessage]):
        """Add relationships from Slack messages."""
        # Group messages by thread
        threads: Dict[str, List[SlackMessage]] = {}
        for msg in messages:
            if msg.thread_id:
                if msg.thread_id not in threads:
                    threads[msg.thread_id] = []
                threads[msg.thread_id].append(msg)
        
        # Create DISCUSSING relationships for threaded discussions
        for thread_id, thread_msgs in threads.items():
            if len(thread_msgs) < 3:
                continue
            
            # Find ticket references in thread
            for msg in thread_msgs:
                ticket = self.resolver.resolve_message_to_ticket(msg)
                if ticket:
                    # Create discussing edge from person to task
                    self._add_edge(
                        source=f"person-{msg.user}",
                        target=f"task-{ticket.ticket_id}",
                        relationship=EdgeType.DISCUSSING,
                        metadata={"message_id": msg.id, "thread_id": thread_id},
                    )


# ============================================================================
# GRAPH SERVICE
# ============================================================================

class WorkGraphService:
    """Service layer for Work Graph operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.builder = WorkGraphBuilder()
        self._graph: Optional[WorkGraph] = None
        self._initialized = True
    
    def get_graph(self, refresh: bool = False) -> WorkGraph:
        """Get the current Work Graph, optionally refreshing it."""
        if self._graph is None or refresh:
            tickets, prs, messages = mock_store.get_all_data()
            self._graph = self.builder.build_graph(tickets, prs, messages)
        return self._graph
    
    def get_node_by_id(self, node_id: str) -> Optional[GraphNode]:
        """Get a specific node by ID."""
        graph = self.get_graph()
        return next((n for n in graph.nodes if n.id == node_id), None)
    
    def get_connected_nodes(self, node_id: str) -> List[GraphNode]:
        """Get all nodes connected to a given node."""
        graph = self.get_graph()
        connected_ids = set()
        
        for edge in graph.edges:
            if edge.source == node_id:
                connected_ids.add(edge.target)
            elif edge.target == node_id:
                connected_ids.add(edge.source)
        
        return [n for n in graph.nodes if n.id in connected_ids]
    
    def search_nodes(self, query: str) -> List[GraphNode]:
        """Search nodes by label or metadata."""
        graph = self.get_graph()
        query_lower = query.lower()
        results = []
        
        for node in graph.nodes:
            if query_lower in node.label.lower():
                results.append(node)
            elif any(query_lower in str(v).lower() for v in node.metadata.values()):
                results.append(node)
        
        return results


# Singleton instance
graph_service = WorkGraphService()
