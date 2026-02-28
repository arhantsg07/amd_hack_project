"""
NexusGraph - AI Chat Interface
Simulated LLM that queries the graph to answer natural language questions.
"""

from typing import List, Optional
import re
from datetime import datetime
from models.schemas import ChatQuery, ChatResponse, GraphNode
from graph.work_graph import graph_service
from analysis.intelligence import intelligence_service
from data.mock_data import mock_store


class AIQueryEngine:
    """
    Simulated AI engine that understands graph queries and provides insights.
    Uses pattern matching and graph traversal instead of actual LLM.
    """
    
    # Query patterns and handlers
    QUERY_PATTERNS = [
        (r"what is blocking (.+)\??", "blocking"),
        (r"who is working on (.+)\??", "working_on"),
        (r"status of (.+)\??", "status"),
        (r"what.*bottleneck", "bottlenecks"),
        (r"who is overloaded", "overloaded"),
        (r"any risk", "risks"),
        (r"shadow task|untracked", "shadow_tasks"),
        (r"brief|summary|what happened", "brief"),
        (r"help|what can you", "help"),
    ]
    
    def __init__(self):
        self.graph = graph_service
        self.intelligence = intelligence_service
    
    def query(self, user_query: ChatQuery) -> ChatResponse:
        """Process a user query and return AI response."""
        query_text = user_query.query.lower().strip()
        
        for pattern, handler_name in self.QUERY_PATTERNS:
            match = re.search(pattern, query_text)
            if match:
                handler = getattr(self, f"_handle_{handler_name}", None)
                if handler:
                    groups = match.groups() if match.groups() else tuple()
                    return handler(*groups)
        
        # Default response
        return self._handle_unknown(query_text)
    
    def _handle_blocking(self, target: str) -> ChatResponse:
        """Handle queries about blockers."""
        target = target.strip().upper()
        
        # Search for the target in graph
        graph = self.graph.get_graph()
        related_nodes = []
        blocking_info = []
        
        # Find task node
        task_node = None
        for node in graph.nodes:
            if target in node.id.upper() or target in node.label.upper():
                task_node = node
                break
            if node.metadata.get("title") and target in node.metadata["title"].upper():
                task_node = node
                break
        
        if task_node:
            # Find blocking edges
            for edge in graph.edges:
                if edge.target == task_node.id and edge.relationship.value == "BLOCKED_BY":
                    blocking_node = self.graph.get_node_by_id(edge.source)
                    if blocking_node:
                        blocking_info.append(blocking_node.label)
                        related_nodes.append(blocking_node.id)
            
            if blocking_info:
                response = f"🚫 **{task_node.label}** is blocked by:\n"
                for blocker in blocking_info:
                    response += f"  • {blocker}\n"
            else:
                response = f"✅ **{task_node.label}** has no blockers identified."
            
            related_nodes.append(task_node.id)
        else:
            # Check bottlenecks for the project
            bottlenecks = self.intelligence.get_bottlenecks()
            project_bottlenecks = [b for b in bottlenecks if target in b.task_id.upper()]
            
            if project_bottlenecks:
                response = f"⚠️ Found {len(project_bottlenecks)} bottleneck(s) related to '{target}':\n"
                for b in project_bottlenecks[:3]:
                    response += f"  • {b.task_id}: {b.description}\n"
            else:
                response = f"ℹ️ No specific blockers found for '{target}'. Try searching for a specific ticket ID."
        
        return ChatResponse(
            response=response,
            sources=["Work Graph", "Bottleneck Analysis"],
            confidence=0.85 if task_node else 0.5,
            related_nodes=related_nodes,
        )
    
    def _handle_working_on(self, target: str) -> ChatResponse:
        """Handle queries about who is working on something."""
        target = target.strip().upper()
        
        graph = self.graph.get_graph()
        workers = []
        related_nodes = []
        
        # Find task and assigned person
        for node in graph.nodes:
            if target in node.id.upper() or target in node.label.upper():
                related_nodes.append(node.id)
                
                # Find ASSIGNED_TO edges
                for edge in graph.edges:
                    if edge.source == node.id and edge.relationship.value == "ASSIGNED_TO":
                        person_node = self.graph.get_node_by_id(edge.target)
                        if person_node:
                            workers.append(person_node.label)
                            related_nodes.append(person_node.id)
        
        if workers:
            response = f"👤 Working on tasks related to '{target}':\n"
            for worker in set(workers):
                response += f"  • {worker}\n"
        else:
            response = f"ℹ️ No one is currently assigned to '{target}'."
        
        return ChatResponse(
            response=response,
            sources=["Work Graph"],
            confidence=0.8 if workers else 0.4,
            related_nodes=related_nodes,
        )
    
    def _handle_status(self, target: str) -> ChatResponse:
        """Handle status queries."""
        target = target.strip().upper()
        
        # Search in tickets
        ticket = mock_store.get_ticket_by_id(target)
        if not ticket:
            # Try fuzzy search
            for t in mock_store.tickets:
                if target in t.ticket_id.upper() or target in t.title.upper():
                    ticket = t
                    break
        
        if ticket:
            status_emoji = {
                "open": "📋",
                "in_progress": "🔄",
                "review": "👁️",
                "blocked": "🚫",
                "closed": "✅",
            }
            emoji = status_emoji.get(ticket.status, "📌")
            
            response = f"{emoji} **{ticket.ticket_id}**: {ticket.title}\n\n"
            response += f"  • **Status:** {ticket.status.replace('_', ' ').title()}\n"
            response += f"  • **Priority:** {ticket.priority.title()}\n"
            response += f"  • **Assignee:** {ticket.assignee_name or 'Unassigned'}\n"
            
            if ticket.dependencies:
                response += f"  • **Blocked by:** {', '.join(ticket.dependencies)}\n"
            
            return ChatResponse(
                response=response,
                sources=["Jira Data"],
                confidence=0.95,
                related_nodes=[f"task-{ticket.ticket_id}"],
            )
        
        return ChatResponse(
            response=f"ℹ️ Could not find '{target}'. Try a specific ticket ID like NEXUS-100.",
            sources=[],
            confidence=0.3,
            related_nodes=[],
        )
    
    def _handle_bottlenecks(self) -> ChatResponse:
        """Handle bottleneck queries."""
        bottlenecks = self.intelligence.get_bottlenecks()
        
        if bottlenecks:
            response = f"🚨 **{len(bottlenecks)} Bottleneck(s) Detected:**\n\n"
            for b in bottlenecks[:5]:
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                emoji = severity_emoji.get(b.severity, "⚪")
                response += f"{emoji} **{b.task_id}**: {b.description}\n"
        else:
            response = "✅ No bottlenecks detected. Workflow is healthy!"
        
        return ChatResponse(
            response=response,
            sources=["Bottleneck Detector"],
            confidence=0.9,
            related_nodes=[f"task-{b.task_id}" for b in bottlenecks[:5]],
        )
    
    def _handle_overloaded(self) -> ChatResponse:
        """Handle overload queries."""
        scores = self.intelligence.get_overload_scores()
        high_risk = [s for s in scores if s.risk_level in ["high", "critical"]]
        
        if high_risk:
            response = "⚠️ **Team Members at Risk of Overload:**\n\n"
            for s in high_risk[:3]:
                risk_emoji = {"critical": "🔴", "high": "🟠"}
                emoji = risk_emoji.get(s.risk_level, "🟡")
                response += f"{emoji} **{s.person_name}**: {s.task_count} tasks, "
                response += f"{s.activity_count} activities (ratio: {s.overload_ratio})\n"
        else:
            response = "✅ No team members are showing signs of overload."
        
        return ChatResponse(
            response=response,
            sources=["Overload Scorer"],
            confidence=0.85,
            related_nodes=[f"person-{s.person_id}" for s in high_risk],
        )
    
    def _handle_risks(self) -> ChatResponse:
        """Handle risk queries."""
        risks = self.intelligence.get_risks()
        
        if risks:
            response = f"⚠️ **{len(risks)} Risk(s) Identified:**\n\n"
            for r in risks[:5]:
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                emoji = severity_emoji.get(r.severity, "⚪")
                response += f"{emoji} **{r.pr_id}**: {r.description}\n"
        else:
            response = "✅ No workflow risks detected."
        
        return ChatResponse(
            response=response,
            sources=["Risk Predictor"],
            confidence=0.88,
            related_nodes=[f"pr-{r.pr_id}" for r in risks[:5]],
        )
    
    def _handle_shadow_tasks(self) -> ChatResponse:
        """Handle shadow task queries."""
        shadows = self.intelligence.get_shadow_tasks()
        
        if shadows:
            response = f"👻 **{len(shadows)} Shadow Task(s) Detected:**\n\n"
            response += "_These are active Slack discussions without linked Jira tickets._\n\n"
            for s in shadows[:3]:
                response += f"• **#{s.channel}** ({s.message_count} messages)\n"
                response += f"  Participants: {', '.join(s.participants[:3])}\n"
                response += f"  Suggested: _{s.suggested_ticket_title}_\n\n"
        else:
            response = "✅ No untracked work detected. All discussions are linked to tickets."
        
        return ChatResponse(
            response=response,
            sources=["Shadow Task Detector"],
            confidence=0.82,
            related_nodes=[],
        )
    
    def _handle_brief(self) -> ChatResponse:
        """Handle brief/summary queries."""
        brief = self.intelligence.get_24h_brief()
        
        response = f"📊 **24-Hour Activity Brief**\n\n"
        response += f"{brief.summary}\n\n"
        
        if brief.key_updates:
            response += "**Key Updates:**\n"
            for update in brief.key_updates:
                response += f"  {update}\n"
        
        response += f"\n**Metrics:**\n"
        response += f"  • 🔥 Hot Threads: {brief.hot_threads}\n"
        response += f"  • 🚫 Blocked Tasks: {brief.blocked_tasks}\n"
        response += f"  • ✅ Merged PRs: {brief.merged_prs}\n"
        
        return ChatResponse(
            response=response,
            sources=["Activity Monitor"],
            confidence=0.95,
            related_nodes=[],
        )
    
    def _handle_help(self) -> ChatResponse:
        """Handle help queries."""
        response = """🤖 **NexusGraph AI Assistant**

I can help you understand your work graph. Try asking:

• **"What is blocking NEXUS-100?"** - Find blockers for a task
• **"Who is working on authentication?"** - Find assignees
• **"Status of API-102"** - Get task details
• **"Show me bottlenecks"** - Detect workflow issues
• **"Who is overloaded?"** - Find at-risk team members
• **"Any risks?"** - Check for PR/ticket mismatches
• **"Show shadow tasks"** - Find untracked work
• **"Give me a brief"** - 24-hour activity summary

💡 _Tip: Use specific ticket IDs for best results._"""
        
        return ChatResponse(
            response=response,
            sources=[],
            confidence=1.0,
            related_nodes=[],
        )
    
    def _handle_unknown(self, query: str) -> ChatResponse:
        """Handle unknown queries."""
        # Try to search graph
        results = self.graph.search_nodes(query)
        
        if results:
            response = f"ℹ️ Found {len(results)} related items in the graph:\n"
            for node in results[:5]:
                response += f"  • **{node.label}** ({node.type.value})\n"
            response += "\nTry asking about a specific item for more details."
        else:
            response = "🤔 I'm not sure how to answer that. Try asking:\n"
            response += "  • 'What is blocking [project/ticket]?'\n"
            response += "  • 'Show me bottlenecks'\n"
            response += "  • 'Who is overloaded?'\n"
            response += "  • 'help' for more options"
        
        return ChatResponse(
            response=response,
            sources=["Graph Search"],
            confidence=0.4,
            related_nodes=[n.id for n in results[:5]] if results else [],
        )


# Singleton instance
ai_engine = AIQueryEngine()
