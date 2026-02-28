"""
NexusGraph - Intelligence Analysis Module
Implements diagnostic functions: Bottleneck Detector, Overload Scorer, Risk Predictor, Shadow Task Detector.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
from models.schemas import (
    Bottleneck, OverloadScore, RiskItem, ShadowTask, InsightsReport,
    SlackMessage, JiraTicket, GitHubPR, ActivityBrief
)
from data.mock_data import mock_store, USERS


# ============================================================================
# BOTTLENECK DETECTOR
# ============================================================================

class BottleneckDetector:
    """
    Identifies Tasks where the linked PR is "Open" but the last Slack 
    message was > 48 hours ago.
    """
    
    STALE_THRESHOLD_HOURS = 48
    
    def detect(
        self,
        tickets: List[JiraTicket],
        prs: List[GitHubPR],
        messages: List[SlackMessage]
    ) -> List[Bottleneck]:
        """Detect bottlenecks in the workflow."""
        bottlenecks = []
        now = datetime.now()
        
        # Index PRs by linked ticket
        pr_by_ticket: Dict[str, GitHubPR] = {}
        for pr in prs:
            if pr.linked_ticket:
                pr_by_ticket[pr.linked_ticket.upper()] = pr
        
        # Index last message time by ticket mention
        message_by_ticket: Dict[str, datetime] = {}
        for msg in messages:
            # Check if message mentions any ticket
            for ticket in tickets:
                if ticket.ticket_id.upper() in msg.message.upper():
                    existing = message_by_ticket.get(ticket.ticket_id)
                    if existing is None or msg.timestamp > existing:
                        message_by_ticket[ticket.ticket_id] = msg.timestamp
        
        # Find bottlenecks
        for ticket in tickets:
            if ticket.status == "closed":
                continue
            
            pr = pr_by_ticket.get(ticket.ticket_id.upper())
            last_message_time = message_by_ticket.get(ticket.ticket_id)
            
            # Check for stale activity with open PR
            if pr and pr.status == "open":
                hours_since_activity = float('inf')
                
                if last_message_time:
                    delta = now - last_message_time
                    hours_since_activity = delta.total_seconds() / 3600
                
                if hours_since_activity > self.STALE_THRESHOLD_HOURS:
                    severity = self._calculate_severity(hours_since_activity, ticket.priority)
                    
                    bottlenecks.append(Bottleneck(
                        task_id=ticket.ticket_id,
                        task_title=ticket.title,
                        pr_id=pr.pr_id,
                        pr_status=pr.status,
                        last_slack_activity=last_message_time,
                        hours_since_activity=hours_since_activity if hours_since_activity != float('inf') else -1,
                        severity=severity,
                        description=self._generate_description(ticket, pr, hours_since_activity),
                    ))
        
        return sorted(bottlenecks, key=lambda b: b.severity == "critical", reverse=True)
    
    def _calculate_severity(self, hours: float, priority: str) -> str:
        """Calculate bottleneck severity."""
        if hours == float('inf'):
            return "critical"
        elif hours > 96 or priority == "critical":
            return "critical"
        elif hours > 72 or priority == "high":
            return "high"
        elif hours > 48:
            return "medium"
        else:
            return "low"
    
    def _generate_description(
        self,
        ticket: JiraTicket,
        pr: GitHubPR,
        hours: float
    ) -> str:
        """Generate human-readable bottleneck description."""
        if hours == float('inf'):
            return f"{ticket.ticket_id} has an open PR ({pr.pr_id}) but no Slack discussion found."
        else:
            return f"{ticket.ticket_id} has an open PR ({pr.pr_id}) with no Slack activity for {int(hours)}+ hours."


# ============================================================================
# OVERLOAD SCORER
# ============================================================================

class OverloadScorer:
    """
    Calculates which "Person" node has the highest ratio of Tasks-to-Activity.
    """
    
    def score(
        self,
        tickets: List[JiraTicket],
        prs: List[GitHubPR],
        messages: List[SlackMessage]
    ) -> List[OverloadScore]:
        """Calculate overload scores for all persons."""
        scores = []
        
        for user in USERS:
            user_id = user["id"]
            
            # Count assigned tasks (not closed)
            task_count = sum(
                1 for t in tickets 
                if t.assignee == user_id and t.status != "closed"
            )
            
            # Count activity (PRs + messages in last 7 days)
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            
            pr_activity = sum(
                1 for p in prs 
                if p.author == user_id and p.last_commit_date > week_ago
            )
            
            message_activity = sum(
                1 for m in messages 
                if m.user == user_id and m.timestamp > week_ago
            )
            
            activity_count = pr_activity + message_activity
            
            # Calculate ratio (higher = more overloaded)
            if activity_count > 0:
                overload_ratio = task_count / activity_count
            else:
                overload_ratio = task_count * 2  # No activity = concerning
            
            risk_level = self._calculate_risk(task_count, overload_ratio)
            
            scores.append(OverloadScore(
                person_id=user_id,
                person_name=user["name"],
                task_count=task_count,
                activity_count=activity_count,
                overload_ratio=round(overload_ratio, 2),
                risk_level=risk_level,
            ))
        
        return sorted(scores, key=lambda s: s.overload_ratio, reverse=True)
    
    def _calculate_risk(self, task_count: int, ratio: float) -> str:
        """Calculate overload risk level."""
        if task_count >= 5 and ratio > 2.0:
            return "critical"
        elif task_count >= 4 or ratio > 1.5:
            return "high"
        elif task_count >= 2 or ratio > 1.0:
            return "medium"
        else:
            return "low"


# ============================================================================
# RISK PREDICTOR
# ============================================================================

class RiskPredictor:
    """
    Flags projects where a "Merged" PR has no corresponding "Closed" Jira ticket.
    """
    
    def predict(
        self,
        tickets: List[JiraTicket],
        prs: List[GitHubPR]
    ) -> List[RiskItem]:
        """Predict risks based on PR/ticket mismatches."""
        risks = []
        
        # Index tickets by ID
        ticket_by_id: Dict[str, JiraTicket] = {
            t.ticket_id.upper(): t for t in tickets
        }
        
        for pr in prs:
            if pr.status != "merged":
                continue
            
            linked_ticket = None
            if pr.linked_ticket:
                linked_ticket = ticket_by_id.get(pr.linked_ticket.upper())
            
            # Risk: Merged PR with open/in-progress ticket
            if linked_ticket and linked_ticket.status not in ["closed", "review"]:
                risks.append(RiskItem(
                    pr_id=pr.pr_id,
                    pr_title=pr.title,
                    ticket_id=linked_ticket.ticket_id,
                    ticket_status=linked_ticket.status,
                    risk_type="MERGED_PR_OPEN_TICKET",
                    description=f"PR {pr.pr_id} was merged but {linked_ticket.ticket_id} is still '{linked_ticket.status}'",
                    severity="high",
                ))
            
            # Risk: Merged PR with no linked ticket
            elif not linked_ticket and pr.linked_ticket:
                risks.append(RiskItem(
                    pr_id=pr.pr_id,
                    pr_title=pr.title,
                    ticket_id=pr.linked_ticket,
                    ticket_status=None,
                    risk_type="ORPHANED_PR",
                    description=f"PR {pr.pr_id} references {pr.linked_ticket} but ticket not found",
                    severity="medium",
                ))
        
        return risks


# ============================================================================
# SHADOW TASK DETECTOR
# ============================================================================

class ShadowTaskDetector:
    """
    Identifies Slack threads with >10 messages but NO linked Jira ticket.
    Flags as "Uncharted Work".
    """
    
    MESSAGE_THRESHOLD = 10
    
    def detect(
        self,
        tickets: List[JiraTicket],
        messages: List[SlackMessage]
    ) -> List[ShadowTask]:
        """Detect shadow tasks from Slack activity."""
        shadow_tasks = []
        
        # Get all ticket IDs for reference check
        ticket_ids = {t.ticket_id.upper() for t in tickets}
        
        # Group messages by thread
        threads: Dict[str, List[SlackMessage]] = defaultdict(list)
        for msg in messages:
            if msg.thread_id:
                threads[msg.thread_id].append(msg)
        
        for thread_id, thread_msgs in threads.items():
            if len(thread_msgs) < self.MESSAGE_THRESHOLD:
                continue
            
            # Check if any message references a ticket
            has_ticket_reference = False
            for msg in thread_msgs:
                if any(tid in msg.message.upper() for tid in ticket_ids):
                    has_ticket_reference = True
                    break
            
            if not has_ticket_reference:
                # Sort by timestamp
                sorted_msgs = sorted(thread_msgs, key=lambda m: m.timestamp)
                participants = list(set(m.user_name for m in thread_msgs))
                
                # Generate suggested title from first message
                first_msg = sorted_msgs[0].message[:50]
                suggested_title = f"Follow-up: {first_msg}..."
                
                shadow_tasks.append(ShadowTask(
                    thread_id=thread_id,
                    channel=sorted_msgs[0].channel_name,
                    message_count=len(thread_msgs),
                    participants=participants,
                    first_message=sorted_msgs[0].timestamp,
                    last_message=sorted_msgs[-1].timestamp,
                    sample_text=sorted_msgs[0].message,
                    suggested_ticket_title=suggested_title,
                ))
        
        return sorted(shadow_tasks, key=lambda s: s.message_count, reverse=True)


# ============================================================================
# CONTEXTUAL BRIEF GENERATOR
# ============================================================================

class BriefGenerator:
    """Generates 30-second briefs of recent activity."""
    
    def generate_24h_brief(
        self,
        tickets: List[JiraTicket],
        prs: List[GitHubPR],
        messages: List[SlackMessage]
    ) -> ActivityBrief:
        """Generate a brief of the last 24 hours."""
        now = datetime.now()
        day_ago = now - timedelta(hours=24)
        
        # Count recent activity
        recent_messages = [m for m in messages if m.timestamp > day_ago]
        recent_prs = [p for p in prs if p.last_commit_date > day_ago]
        
        # Count hot threads (>5 messages in 24h)
        thread_counts: Dict[str, int] = defaultdict(int)
        for msg in recent_messages:
            if msg.thread_id:
                thread_counts[msg.thread_id] += 1
        hot_threads = sum(1 for c in thread_counts.values() if c > 5)
        
        # Count blocked tasks
        blocked_tasks = sum(1 for t in tickets if t.status == "blocked")
        
        # Count merged PRs
        merged_prs = sum(1 for p in recent_prs if p.status == "merged")
        
        # Generate key updates
        key_updates = []
        
        for pr in recent_prs:
            if pr.status == "merged":
                key_updates.append(f"✅ {pr.pr_id} merged by {pr.author_name}")
        
        for ticket in tickets:
            if ticket.status == "blocked":
                key_updates.append(f"🚫 {ticket.ticket_id} is blocked")
        
        # Generate summary
        summary = f"In the last 24 hours: {len(recent_messages)} Slack messages, "
        summary += f"{len(recent_prs)} PR updates, {merged_prs} merges. "
        if blocked_tasks > 0:
            summary += f"⚠️ {blocked_tasks} tasks are currently blocked."
        
        return ActivityBrief(
            summary=summary,
            key_updates=key_updates[:5],  # Top 5 updates
            hot_threads=hot_threads,
            blocked_tasks=blocked_tasks,
            merged_prs=merged_prs,
            period_start=day_ago,
            period_end=now,
        )


# ============================================================================
# INTELLIGENCE SERVICE
# ============================================================================

class IntelligenceService:
    """Main service for all intelligence operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.bottleneck_detector = BottleneckDetector()
        self.overload_scorer = OverloadScorer()
        self.risk_predictor = RiskPredictor()
        self.shadow_detector = ShadowTaskDetector()
        self.brief_generator = BriefGenerator()
        self._initialized = True
    
    def get_full_insights(self) -> InsightsReport:
        """Generate complete insights report."""
        tickets, prs, messages = mock_store.get_all_data()
        
        return InsightsReport(
            bottlenecks=self.bottleneck_detector.detect(tickets, prs, messages),
            overload_scores=self.overload_scorer.score(tickets, prs, messages),
            risks=self.risk_predictor.predict(tickets, prs),
            shadow_tasks=self.shadow_detector.detect(tickets, messages),
            generated_at=datetime.now(),
        )
    
    def get_24h_brief(self) -> ActivityBrief:
        """Get 24-hour activity brief."""
        tickets, prs, messages = mock_store.get_all_data()
        return self.brief_generator.generate_24h_brief(tickets, prs, messages)
    
    def get_bottlenecks(self) -> List[Bottleneck]:
        """Get only bottlenecks."""
        tickets, prs, messages = mock_store.get_all_data()
        return self.bottleneck_detector.detect(tickets, prs, messages)
    
    def get_overload_scores(self) -> List[OverloadScore]:
        """Get only overload scores."""
        tickets, prs, messages = mock_store.get_all_data()
        return self.overload_scorer.score(tickets, prs, messages)
    
    def get_risks(self) -> List[RiskItem]:
        """Get only risks."""
        tickets, prs, messages = mock_store.get_all_data()
        return self.risk_predictor.predict(tickets, prs)
    
    def get_shadow_tasks(self) -> List[ShadowTask]:
        """Get only shadow tasks."""
        tickets, messages = mock_store.tickets, mock_store.messages
        return self.shadow_detector.detect(tickets, messages)


# Singleton instance
intelligence_service = IntelligenceService()
