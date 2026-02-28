"""
NexusGraph - Mock Data Simulation Layer
Generates realistic inter-linked test data for Slack, Jira, and GitHub.
"""

import random
from datetime import datetime, timedelta
from typing import List, Tuple
from models.schemas import SlackMessage, JiraTicket, GitHubPR


# ============================================================================
# MOCK USER DATA
# ============================================================================

USERS = [
    {"id": "U001", "name": "Alex Chen", "avatar": "alex"},
    {"id": "U002", "name": "Sarah Johnson", "avatar": "sarah"},
    {"id": "U003", "name": "Mike Rodriguez", "avatar": "mike"},
    {"id": "U004", "name": "Emily Park", "avatar": "emily"},
    {"id": "U005", "name": "James Wilson", "avatar": "james"},
    {"id": "U006", "name": "Lisa Thompson", "avatar": "lisa"},
]

CHANNELS = [
    {"id": "C001", "name": "engineering"},
    {"id": "C002", "name": "frontend-team"},
    {"id": "C003", "name": "backend-team"},
    {"id": "C004", "name": "devops"},
    {"id": "C005", "name": "general"},
]

PROJECTS = ["NEXUS", "AUTH", "API", "UI", "INFRA"]

REPOS = ["nexusgraph-core", "nexusgraph-ui", "nexusgraph-api", "auth-service", "infra-tools"]


# ============================================================================
# TIME HELPERS
# ============================================================================

def random_time_in_range(start_hours_ago: int, end_hours_ago: int) -> datetime:
    """Generate a random datetime within a range of hours ago."""
    now = datetime.now()
    start = now - timedelta(hours=start_hours_ago)
    end = now - timedelta(hours=end_hours_ago)
    
    # Ensure start is before end
    if start > end:
        start, end = end, start
    
    delta = end - start
    total_seconds = int(delta.total_seconds())
    
    if total_seconds <= 0:
        return end
    
    random_seconds = random.randint(0, total_seconds)
    return start + timedelta(seconds=random_seconds)


# ============================================================================
# JIRA TICKET GENERATOR
# ============================================================================

TICKET_TEMPLATES = [
    ("Implement user authentication flow", "auth"),
    ("Fix login page styling issues", "ui"),
    ("Optimize database query performance", "perf"),
    ("Add rate limiting to API endpoints", "api"),
    ("Update dependency versions", "deps"),
    ("Refactor payment processing module", "refactor"),
    ("Add unit tests for graph engine", "test"),
    ("Fix memory leak in worker process", "bug"),
    ("Implement real-time notifications", "feature"),
    ("Update API documentation", "docs"),
    ("Fix cross-browser compatibility issues", "bug"),
    ("Implement dark mode toggle", "ui"),
    ("Add caching layer for API responses", "perf"),
    ("Fix security vulnerability in auth", "security"),
    ("Implement export to CSV feature", "feature"),
]


def generate_jira_tickets(count: int = 15) -> List[JiraTicket]:
    """Generate mock Jira tickets with dependencies."""
    tickets = []
    statuses = ["open", "in_progress", "review", "blocked", "closed"]
    priorities = ["critical", "high", "medium", "low"]
    
    for i in range(count):
        template = TICKET_TEMPLATES[i % len(TICKET_TEMPLATES)]
        project = random.choice(PROJECTS)
        ticket_id = f"{project}-{100 + i}"
        assignee = random.choice(USERS) if random.random() > 0.2 else None
        reporter = random.choice(USERS)
        
        # Generate dependencies (some tickets block others)
        dependencies = []
        if i > 2 and random.random() > 0.6:
            dep_idx = random.randint(0, i - 1)
            dep_project = PROJECTS[dep_idx % len(PROJECTS)]
            dependencies.append(f"{dep_project}-{100 + dep_idx}")
        
        status = random.choice(statuses)
        created = random_time_in_range(168, 24)  # 1 week to 1 day ago
        updated = random_time_in_range(72, 0) if status != "closed" else random_time_in_range(48, 12)
        
        tickets.append(JiraTicket(
            ticket_id=ticket_id,
            title=template[0],
            description=f"Implementation task for {template[1]} functionality",
            status=status,
            assignee=assignee["id"] if assignee else None,
            assignee_name=assignee["name"] if assignee else None,
            reporter=reporter["id"],
            priority=random.choice(priorities),
            dependencies=dependencies,
            project=project,
            created_at=created,
            updated_at=updated,
        ))
    
    return tickets


# ============================================================================
# GITHUB PR GENERATOR
# ============================================================================

def generate_github_prs(tickets: List[JiraTicket], count: int = 12) -> List[GitHubPR]:
    """Generate mock GitHub PRs, some linked to Jira tickets."""
    prs = []
    pr_statuses = ["open", "merged", "closed", "draft"]
    review_statuses = ["pending", "approved", "changes_requested"]
    
    # Create PRs linked to tickets
    linked_tickets = random.sample(tickets, min(count - 3, len(tickets)))
    
    for i, ticket in enumerate(linked_tickets):
        author = random.choice(USERS)
        status = random.choice(pr_statuses)
        
        prs.append(GitHubPR(
            pr_id=f"PR-{200 + i}",
            title=f"Fix for {ticket.ticket_id}: {ticket.title[:30]}...",
            author=author["id"],
            author_name=author["name"],
            linked_ticket=ticket.ticket_id,
            status=status,
            repo=random.choice(REPOS),
            branch=f"feature/{ticket.ticket_id.lower()}-fix",
            last_commit_date=random_time_in_range(96, 0),
            additions=random.randint(10, 500),
            deletions=random.randint(5, 200),
            review_status=random.choice(review_statuses) if status == "open" else None,
        ))
    
    # Create some unlinked PRs
    for i in range(3):
        author = random.choice(USERS)
        prs.append(GitHubPR(
            pr_id=f"PR-{300 + i}",
            title=random.choice([
                "Refactor: Clean up legacy code",
                "Chore: Update dependencies",
                "Docs: Improve README",
            ]),
            author=author["id"],
            author_name=author["name"],
            linked_ticket=None,
            status=random.choice(pr_statuses),
            repo=random.choice(REPOS),
            branch=f"misc/cleanup-{i}",
            last_commit_date=random_time_in_range(72, 0),
            additions=random.randint(5, 100),
            deletions=random.randint(5, 50),
            review_status=None,
        ))
    
    return prs


# ============================================================================
# SLACK MESSAGE GENERATOR
# ============================================================================

MESSAGE_TEMPLATES = [
    "Hey team, working on {ticket} today. Should be done by EOD.",
    "Anyone available to review {ticket}? Need a second pair of eyes.",
    "Blocked on {ticket} - waiting for API changes to land.",
    "Just pushed a fix for {ticket}. @{user} can you check?",
    "The {ticket} issue is more complex than expected. Need to discuss.",
    "Merged the PR for {ticket}! 🎉",
    "Having trouble with the tests on {ticket}. CI keeps failing.",
    "Quick sync on {ticket}? I have some questions about the requirements.",
    "FYI - {ticket} is now in review. Should ship tomorrow.",
    "📢 {ticket} is live in staging. Please test!",
]

SHADOW_THREAD_MESSAGES = [
    "We should probably track this somewhere...",
    "This is getting complex, should we create a ticket?",
    "Good point, let me add that to the backlog",
    "Can someone document this discussion?",
    "This needs more investigation",
    "Let's loop in the team on this",
    "I'll look into it when I have time",
    "This keeps coming up, we need a proper solution",
    "Adding to my list of things to fix",
    "We've been talking about this for a while now",
]


def generate_slack_messages(
    tickets: List[JiraTicket],
    count: int = 30
) -> List[SlackMessage]:
    """Generate mock Slack messages, some referencing Jira tickets."""
    messages = []
    thread_counter = 0
    
    # Messages mentioning tickets
    for i in range(count - 10):
        user = random.choice(USERS)
        channel = random.choice(CHANNELS)
        ticket = random.choice(tickets) if random.random() > 0.3 else None
        mentioned_user = random.choice([u for u in USERS if u["id"] != user["id"]])
        
        if ticket:
            template = random.choice(MESSAGE_TEMPLATES)
            message_text = template.format(
                ticket=ticket.ticket_id,
                user=mentioned_user["name"]
            )
        else:
            message_text = random.choice([
                "Morning everyone! ☕",
                "Anyone up for a quick sync?",
                "Great work on the release!",
                "Happy Friday! 🎉",
                "Just a heads up - I'll be OOO tomorrow",
            ])
        
        is_thread = random.random() > 0.6
        thread_id = f"thread-{thread_counter}" if is_thread else None
        if is_thread:
            thread_counter += 1
        
        messages.append(SlackMessage(
            id=f"MSG-{1000 + i}",
            user=user["id"],
            user_name=user["name"],
            channel=channel["id"],
            channel_name=channel["name"],
            timestamp=random_time_in_range(72, 0),
            message=message_text,
            thread_id=thread_id,
            reply_count=random.randint(0, 15) if is_thread else 0,
            reactions=random.randint(0, 8),
        ))
    
    # Shadow threads (high activity, no ticket link)
    for i in range(3):
        channel = random.choice(CHANNELS)
        thread_id = f"shadow-thread-{i}"
        base_time = random_time_in_range(48, 24)
        
        # Generate multiple messages in the same thread
        for j in range(random.randint(10, 20)):
            user = random.choice(USERS)
            messages.append(SlackMessage(
                id=f"MSG-SHADOW-{i}-{j}",
                user=user["id"],
                user_name=user["name"],
                channel=channel["id"],
                channel_name=channel["name"],
                timestamp=base_time + timedelta(minutes=j * random.randint(2, 15)),
                message=random.choice(SHADOW_THREAD_MESSAGES),
                thread_id=thread_id,
                reply_count=random.randint(10, 25),
                reactions=random.randint(0, 5),
            ))
    
    return messages


# ============================================================================
# MAIN DATA GENERATOR
# ============================================================================

class MockDataStore:
    """Central store for all mock data with cross-references."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.regenerate()
        self._initialized = True
    
    def regenerate(self):
        """Regenerate all mock data."""
        self.tickets = generate_jira_tickets(15)
        self.prs = generate_github_prs(self.tickets, 12)
        self.messages = generate_slack_messages(self.tickets, 30)
        self.users = USERS
        self.channels = CHANNELS
        self.last_generated = datetime.now()
    
    def get_all_data(self) -> Tuple[List[JiraTicket], List[GitHubPR], List[SlackMessage]]:
        """Get all mock data."""
        return self.tickets, self.prs, self.messages
    
    def get_user_by_id(self, user_id: str) -> dict:
        """Get user info by ID."""
        return next((u for u in self.users if u["id"] == user_id), None)
    
    def get_ticket_by_id(self, ticket_id: str) -> JiraTicket:
        """Get ticket by ID."""
        return next((t for t in self.tickets if t.ticket_id == ticket_id), None)
    
    def get_pr_by_id(self, pr_id: str) -> GitHubPR:
        """Get PR by ID."""
        return next((p for p in self.prs if p.pr_id == pr_id), None)


# Singleton instance
mock_store = MockDataStore()
