# Linear Connector

The Linear connector enables importing issues, projects, documents, and team data from Linear into ContextFrame. This guide covers setup, authentication, and usage patterns for the Linear integration.

## Overview

The Linear connector can import:
- Issues (with comments and attachments)
- Projects and milestones
- Documents and pages
- Team and user information
- Labels and workflows
- Comments and discussions

## Installation

The Linear connector is included with ContextFrame:

```python
from contextframe.connectors import LinearConnector
```

## Authentication

### API Key Setup

1. Go to Linear Settings → API → Personal API keys
2. Click "Create key"
3. Give it a descriptive name
4. Copy the key (starts with `lin_api_`)

```python
connector = LinearConnector(
    api_key="lin_api_xxxxxxxxxxxx"
)
```

### Environment Variables

```bash
export LINEAR_API_KEY="lin_api_xxxxxxxxxxxx"
```

```python
import os

connector = LinearConnector(
    api_key=os.getenv("LINEAR_API_KEY")
)
```

## Basic Usage

### Import Issues

```python
from contextframe import FrameDataset
from contextframe.connectors import LinearConnector

# Create dataset
dataset = FrameDataset.create("linear_issues.lance")

# Setup connector
connector = LinearConnector(
    api_key="your-api-key"
)

# Authenticate
connector.authenticate()

# Sync all issues
issues = connector.sync_issues()

# Convert to FrameRecords and import
for issue in issues:
    record = connector.map_to_frame_record(issue)
    dataset.add(record)

print(f"Imported {len(issues)} issues")
```

### Import Specific Team's Issues

```python
# Get team ID first
teams = connector.get_teams()
for team in teams:
    print(f"Team: {team.name} (ID: {team.id})")

# Sync issues for specific team
team_id = "TEAM-xxx"
issues = connector.sync_issues(
    team_id=team_id,
    state_filter=["In Progress", "Done"],
    label_filter=["bug", "feature"]
)

# Import with team context
records = []
for issue in issues:
    record = connector.map_to_frame_record(issue)
    record.metadata['collection'] = f"linear-{team.key.lower()}"
    records.append(record)

dataset.add_many(records)
```

### Import Projects

```python
# Sync all projects
projects = connector.sync_projects()

for project in projects:
    # Create project header
    project_record = FrameRecord.create(
        title=project.name,
        content=project.description or "",
        record_type="collection_header",
        collection=f"linear-project-{project.id[:8]}",
        author=project.lead.name if project.lead else "Unknown",
        status="active" if project.state == "started" else project.state,
        custom_metadata={
            "linear_project_id": project.id,
            "linear_project_key": project.key,
            "linear_project_state": project.state,
            "linear_project_progress": project.progress,
            "linear_target_date": project.targetDate.isoformat() if project.targetDate else None,
            "linear_start_date": project.startDate.isoformat() if project.startDate else None
        }
    )
    dataset.add(project_record)
    
    # Import project issues
    project_issues = connector.sync_issues(project_id=project.id)
    for issue in project_issues:
        record = connector.map_to_frame_record(issue)
        record.metadata['collection'] = f"linear-project-{project.id[:8]}"
        record.add_relationship(
            project_record.uuid,
            "member_of",
            title=f"Part of {project.name}"
        )
        dataset.add(record)
```

## Advanced Features

### Issue Comments and History

```python
def import_issue_with_comments(connector, dataset, issue):
    """Import issue with full comment history."""
    
    # Create main issue record
    issue_record = connector.map_to_frame_record(issue)
    dataset.add(issue_record)
    
    # Get comments
    comments = connector.get_issue_comments(issue.id)
    
    for comment in comments:
        comment_record = FrameRecord.create(
            title=f"Comment on {issue.identifier}: {issue.title[:50]}",
            content=comment.body,
            author=comment.user.name,
            created_at=comment.createdAt.isoformat(),
            source_type="linear",
            custom_metadata={
                "linear_comment_id": comment.id,
                "linear_issue_id": issue.id,
                "linear_issue_identifier": issue.identifier,
                "comment_type": "issue_comment"
            }
        )
        
        # Link to parent issue
        comment_record.add_relationship(
            issue_record.uuid,
            "child",
            title="Comment on issue"
        )
        
        dataset.add(comment_record)
    
    return len(comments) + 1
```

### Document Import

```python
# Import Linear documents (project docs, wikis)
documents = connector.sync_documents()

for doc in documents:
    record = FrameRecord.create(
        title=doc.title,
        content=doc.content,  # Markdown content
        author=doc.creator.name if doc.creator else "Unknown",
        created_at=doc.createdAt.isoformat(),
        updated_at=doc.updatedAt.isoformat(),
        source_type="linear",
        source_url=doc.url,
        tags=["linear-doc", "documentation"],
        custom_metadata={
            "linear_document_id": doc.id,
            "linear_document_slug": doc.slug,
            "linear_project_id": doc.project.id if doc.project else None
        }
    )
    
    # Handle document hierarchy
    if doc.parent:
        parent_record = find_document_record(dataset, doc.parent.id)
        if parent_record:
            record.add_relationship(
                parent_record['uuid'],
                "child",
                title=f"Subdocument of {doc.parent.title}"
            )
    
    dataset.add(record)
```

### Workflow States

```python
def import_with_workflow_context(connector, dataset):
    """Import issues with workflow state information."""
    
    # Get workflow states for better context
    teams = connector.get_teams()
    
    for team in teams:
        # Get team's workflow states
        states = connector.get_workflow_states(team.id)
        state_map = {state.id: state for state in states}
        
        # Get issues with state context
        issues = connector.sync_issues(team_id=team.id)
        
        for issue in issues:
            record = connector.map_to_frame_record(issue)
            
            # Add workflow context
            state = state_map.get(issue.state.id)
            if state:
                record.metadata['custom_metadata'].update({
                    'workflow_state_name': state.name,
                    'workflow_state_type': state.type,  # backlog, unstarted, started, completed, canceled
                    'workflow_state_color': state.color,
                    'workflow_position': state.position
                })
                
                # Add semantic tags based on state type
                if state.type == "completed":
                    record.metadata['tags'].append("completed")
                elif state.type == "started":
                    record.metadata['tags'].append("in-progress")
                elif state.type == "backlog":
                    record.metadata['tags'].append("backlog")
            
            dataset.add(record)
```

## Data Mapping

### Default Issue Mapping

```python
def map_to_frame_record(self, issue):
    """Map Linear issue to FrameRecord."""
    
    # Build content with rich context
    content = f"""# {issue.title}

**Identifier**: {issue.identifier}
**State**: {issue.state.name}
**Priority**: {self.priority_label(issue.priority)}
**Assignee**: {issue.assignee.name if issue.assignee else "Unassigned"}

## Description
{issue.description or "No description provided"}

## Details
- **Created**: {issue.createdAt}
- **Updated**: {issue.updatedAt}
- **Due Date**: {issue.dueDate or "Not set"}
- **Estimate**: {issue.estimate or "Not estimated"}
"""
    
    # Add labels
    if issue.labels:
        content += "\n## Labels\n"
        content += ", ".join([label.name for label in issue.labels])
    
    return FrameRecord.create(
        title=f"{issue.identifier}: {issue.title}",
        content=content,
        author=issue.creator.name if issue.creator else "Unknown",
        status=self.map_status(issue.state.type),
        source_url=issue.url,
        source_type="linear",
        tags=self.generate_tags(issue),
        custom_metadata={
            "linear_issue_id": issue.id,
            "linear_issue_number": issue.number,
            "linear_issue_identifier": issue.identifier,
            "linear_team_id": issue.team.id,
            "linear_team_key": issue.team.key,
            "linear_project_id": issue.project.id if issue.project else None,
            "linear_priority": issue.priority,
            "linear_estimate": issue.estimate,
            "linear_state": issue.state.name,
            "linear_state_type": issue.state.type,
            "linear_assignee": issue.assignee.email if issue.assignee else None,
            "linear_labels": [label.name for label in issue.labels],
            "linear_due_date": issue.dueDate.isoformat() if issue.dueDate else None
        }
    )

def priority_label(self, priority):
    """Convert priority number to label."""
    priority_map = {
        0: "No priority",
        1: "Urgent",
        2: "High",
        3: "Medium",
        4: "Low"
    }
    return priority_map.get(priority, "Unknown")

def map_status(self, state_type):
    """Map Linear state type to FrameRecord status."""
    status_map = {
        "backlog": "draft",
        "unstarted": "draft",
        "started": "published",
        "completed": "archived",
        "canceled": "deleted"
    }
    return status_map.get(state_type, "published")
```

### Custom Field Mapping

```python
class CustomLinearConnector(LinearConnector):
    """Linear connector with custom field mapping."""
    
    def __init__(self, custom_field_mappings=None, **kwargs):
        super().__init__(**kwargs)
        self.custom_field_mappings = custom_field_mappings or {}
    
    def map_to_frame_record(self, issue):
        """Enhanced mapping with custom fields."""
        record = super().map_to_frame_record(issue)
        
        # Process custom fields
        if hasattr(issue, 'customFields'):
            for field in issue.customFields:
                field_name = self.custom_field_mappings.get(
                    field.id, 
                    f"custom_{field.name.lower().replace(' ', '_')}"
                )
                
                # Handle different field types
                if field.type == "text":
                    value = field.value
                elif field.type == "number":
                    value = float(field.value) if field.value else None
                elif field.type == "date":
                    value = field.value.isoformat() if field.value else None
                elif field.type == "select":
                    value = field.value.name if field.value else None
                else:
                    value = str(field.value) if field.value else None
                
                record.metadata['custom_metadata'][field_name] = value
        
        # Add computed fields
        record.metadata['custom_metadata']['days_since_update'] = (
            datetime.now() - issue.updatedAt
        ).days
        
        # Cycle time calculation
        if issue.startedAt and issue.completedAt:
            cycle_time = (issue.completedAt - issue.startedAt).days
            record.metadata['custom_metadata']['cycle_time_days'] = cycle_time
        
        return record
```

## Sync Strategies

### Smart Incremental Sync

```python
def smart_sync(connector, dataset, sync_state_file=".linear_sync_state.json"):
    """Intelligent incremental sync with state tracking."""
    
    # Load previous sync state
    sync_state = {}
    if os.path.exists(sync_state_file):
        with open(sync_state_file, 'r') as f:
            sync_state = json.load(f)
    
    last_sync = sync_state.get('last_sync')
    known_issues = set(sync_state.get('known_issues', []))
    
    # Get updated issues
    if last_sync:
        # Convert to datetime
        last_sync_dt = datetime.fromisoformat(last_sync)
        updated_issues = connector.sync_issues(
            updated_after=last_sync_dt
        )
    else:
        # First sync - get all
        updated_issues = connector.sync_issues()
    
    # Process updates
    new_count = 0
    update_count = 0
    
    for issue in updated_issues:
        record = connector.map_to_frame_record(issue)
        
        if issue.id in known_issues:
            # Update existing
            existing = dataset.scanner(
                filter=f"custom_metadata.linear_issue_id = '{issue.id}'"
            ).to_table().to_pylist()
            
            if existing:
                dataset.update_record(existing[0]['uuid'], record)
                update_count += 1
        else:
            # Add new
            dataset.add(record)
            known_issues.add(issue.id)
            new_count += 1
    
    # Save sync state
    sync_state = {
        'last_sync': datetime.now().isoformat(),
        'known_issues': list(known_issues),
        'total_issues': len(known_issues)
    }
    
    with open(sync_state_file, 'w') as f:
        json.dump(sync_state, f)
    
    print(f"Sync complete: {new_count} new, {update_count} updated")
    return new_count, update_count
```

### Real-time Sync with Webhooks

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

class LinearWebhookHandler:
    """Handle Linear webhooks for real-time updates."""
    
    def __init__(self, dataset, connector, webhook_secret):
        self.dataset = dataset
        self.connector = connector
        self.webhook_secret = webhook_secret
    
    def verify_signature(self, payload, signature):
        """Verify webhook signature."""
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    @app.route('/webhook/linear', methods=['POST'])
    def handle_webhook(self):
        """Process Linear webhook."""
        # Verify signature
        signature = request.headers.get('Linear-Signature')
        if not self.verify_signature(request.data, signature):
            return "Invalid signature", 401
        
        # Parse event
        event = request.json
        event_type = event.get('type')
        data = event.get('data')
        
        if event_type == "Issue":
            self.handle_issue_event(event.get('action'), data)
        elif event_type == "Comment":
            self.handle_comment_event(event.get('action'), data)
        elif event_type == "Project":
            self.handle_project_event(event.get('action'), data)
        
        return "OK", 200
    
    def handle_issue_event(self, action, issue_data):
        """Handle issue create/update/delete."""
        issue_id = issue_data.get('id')
        
        if action == "create" or action == "update":
            # Fetch full issue data
            issue = self.connector.get_issue(issue_id)
            record = self.connector.map_to_frame_record(issue)
            
            if action == "create":
                self.dataset.add(record)
            else:
                # Find and update existing
                existing = self.dataset.scanner(
                    filter=f"custom_metadata.linear_issue_id = '{issue_id}'"
                ).to_table().to_pylist()
                
                if existing:
                    self.dataset.update_record(existing[0]['uuid'], record)
        
        elif action == "remove":
            # Mark as deleted
            existing = self.dataset.scanner(
                filter=f"custom_metadata.linear_issue_id = '{issue_id}'"
            ).to_table().to_pylist()
            
            if existing:
                self.dataset.delete_record(existing[0]['uuid'])
```

## Search and Analytics

### Issue Analytics

```python
def analyze_linear_issues(dataset):
    """Analyze imported Linear issues."""
    
    analytics = {
        'total_issues': 0,
        'by_state': {},
        'by_priority': {},
        'by_assignee': {},
        'by_label': {},
        'cycle_times': []
    }
    
    # Scan all Linear issues
    scanner = dataset.scanner(
        filter="source_type = 'linear' AND custom_metadata.linear_issue_id IS NOT NULL"
    )
    
    for batch in scanner.to_batches():
        for row in batch.to_pylist():
            analytics['total_issues'] += 1
            metadata = row.get('custom_metadata', {})
            
            # State distribution
            state = metadata.get('linear_state', 'Unknown')
            analytics['by_state'][state] = analytics['by_state'].get(state, 0) + 1
            
            # Priority distribution
            priority = metadata.get('linear_priority', 0)
            priority_label = ["No priority", "Urgent", "High", "Medium", "Low"][priority]
            analytics['by_priority'][priority_label] = analytics['by_priority'].get(priority_label, 0) + 1
            
            # Assignee workload
            assignee = metadata.get('linear_assignee', 'Unassigned')
            analytics['by_assignee'][assignee] = analytics['by_assignee'].get(assignee, 0) + 1
            
            # Label usage
            for label in metadata.get('linear_labels', []):
                analytics['by_label'][label] = analytics['by_label'].get(label, 0) + 1
            
            # Cycle time
            if metadata.get('cycle_time_days'):
                analytics['cycle_times'].append(metadata['cycle_time_days'])
    
    # Calculate cycle time stats
    if analytics['cycle_times']:
        analytics['avg_cycle_time'] = sum(analytics['cycle_times']) / len(analytics['cycle_times'])
        analytics['median_cycle_time'] = sorted(analytics['cycle_times'])[len(analytics['cycle_times']) // 2]
    
    return analytics
```

### Cross-Reference Search

```python
def find_related_content(dataset, issue_identifier):
    """Find all content related to a Linear issue."""
    
    # Search by identifier in content
    text_results = dataset.full_text_search(
        issue_identifier,
        filter="source_type != 'linear'"  # Exclude Linear itself
    )
    
    # Search in metadata
    metadata_results = dataset.scanner(
        filter=f"custom_metadata.references CONTAINS '{issue_identifier}'"
    ).to_table()
    
    # Combine and deduplicate
    all_results = {}
    
    for result in text_results.to_pylist():
        all_results[result['uuid']] = {
            'document': result,
            'match_type': 'content',
            'relevance': 'high'
        }
    
    for result in metadata_results.to_pylist():
        if result['uuid'] not in all_results:
            all_results[result['uuid']] = {
                'document': result,
                'match_type': 'metadata',
                'relevance': 'exact'
            }
    
    return list(all_results.values())
```

## Integration Patterns

### Linear + GitHub Integration

```python
def link_issues_to_code(linear_connector, github_connector, dataset):
    """Link Linear issues to GitHub code and PRs."""
    
    # Get Linear issues
    issues = linear_connector.sync_issues()
    
    for issue in issues:
        # Look for GitHub references in issue
        github_refs = extract_github_references(issue.description)
        
        for ref in github_refs:
            if ref['type'] == 'pr':
                # Get PR from GitHub
                pr = github_connector.get_pull_request(ref['number'])
                
                # Create relationship
                issue_record = find_linear_issue(dataset, issue.id)
                pr_record = find_github_pr(dataset, pr.number)
                
                if issue_record and pr_record:
                    issue_record.add_relationship(
                        pr_record['uuid'],
                        'reference',
                        title=f"Implemented in PR #{pr.number}"
                    )

def extract_github_references(text):
    """Extract GitHub references from text."""
    import re
    
    refs = []
    
    # Match PR references
    pr_pattern = r'(?:PR #|#)(\d+)'
    for match in re.finditer(pr_pattern, text):
        refs.append({
            'type': 'pr',
            'number': int(match.group(1))
        })
    
    # Match commit SHAs
    sha_pattern = r'\b[0-9a-f]{40}\b'
    for match in re.finditer(sha_pattern, text):
        refs.append({
            'type': 'commit',
            'sha': match.group(0)
        })
    
    return refs
```

### Project Timeline Visualization

```python
def export_project_timeline(dataset, project_id):
    """Export project data for timeline visualization."""
    
    # Get all issues in project
    issues = dataset.scanner(
        filter=f"custom_metadata.linear_project_id = '{project_id}'"
    ).to_table().to_pylist()
    
    timeline_data = {
        'project_id': project_id,
        'events': []
    }
    
    for issue in issues:
        metadata = issue['custom_metadata']
        
        # Create timeline events
        if issue.get('created_at'):
            timeline_data['events'].append({
                'timestamp': issue['created_at'],
                'type': 'issue_created',
                'title': issue['title'],
                'issue_id': metadata['linear_issue_identifier']
            })
        
        # Add state changes (would need to track history)
        if metadata.get('linear_state_type') == 'completed':
            timeline_data['events'].append({
                'timestamp': issue['updated_at'],
                'type': 'issue_completed',
                'title': issue['title'],
                'issue_id': metadata['linear_issue_identifier']
            })
    
    # Sort by timestamp
    timeline_data['events'].sort(key=lambda x: x['timestamp'])
    
    return timeline_data
```

## Performance Optimization

### Batch Operations

```python
def batch_import_issues(connector, dataset, batch_size=50):
    """Import issues in batches for better performance."""
    
    page = 1
    total_imported = 0
    
    while True:
        # Get batch of issues
        issues = connector.sync_issues(
            page=page,
            per_page=batch_size
        )
        
        if not issues:
            break
        
        # Convert to records
        records = []
        for issue in issues:
            record = connector.map_to_frame_record(issue)
            records.append(record)
        
        # Batch insert
        dataset.add_many(records)
        total_imported += len(records)
        
        print(f"Imported batch {page}: {len(records)} issues (total: {total_imported})")
        page += 1
    
    return total_imported
```

### Caching GraphQL Responses

```python
import hashlib
import json
from datetime import datetime, timedelta

class CachedLinearConnector(LinearConnector):
    """Linear connector with response caching."""
    
    def __init__(self, cache_ttl=3600, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    def _cache_key(self, query, variables):
        """Generate cache key for GraphQL query."""
        key_data = f"{query}:{json.dumps(variables, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def execute_query(self, query, variables=None):
        """Execute GraphQL query with caching."""
        cache_key = self._cache_key(query, variables)
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        # Execute query
        result = super().execute_query(query, variables)
        
        # Cache result
        self.cache[cache_key] = (result, datetime.now())
        
        return result
```

## Error Handling

### Retry Logic

```python
import time
from typing import Optional

def retry_on_error(max_attempts=3, delay=1, backoff=2):
    """Decorator for retry logic."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    
                    print(f"Attempt {attempt} failed: {e}")
                    print(f"Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator

class RobustLinearConnector(LinearConnector):
    """Linear connector with robust error handling."""
    
    @retry_on_error(max_attempts=3)
    def sync_issues(self, **kwargs):
        """Sync issues with retry."""
        try:
            return super().sync_issues(**kwargs)
        except Exception as e:
            if "rate limit" in str(e).lower():
                # Wait longer for rate limits
                time.sleep(60)
                raise
            raise
```

### Partial Sync Recovery

```python
def sync_with_recovery(connector, dataset, checkpoint_file=".linear_checkpoint.json"):
    """Sync with ability to resume from failures."""
    
    # Load checkpoint if exists
    checkpoint = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
    
    last_processed_id = checkpoint.get('last_processed_id')
    processed_ids = set(checkpoint.get('processed_ids', []))
    
    try:
        # Get all issues
        all_issues = connector.sync_issues()
        
        # Sort by ID for consistent ordering
        all_issues.sort(key=lambda x: x.id)
        
        # Find starting point
        start_index = 0
        if last_processed_id:
            for i, issue in enumerate(all_issues):
                if issue.id == last_processed_id:
                    start_index = i + 1
                    break
        
        # Process remaining issues
        for issue in all_issues[start_index:]:
            if issue.id not in processed_ids:
                record = connector.map_to_frame_record(issue)
                dataset.add(record)
                processed_ids.add(issue.id)
                
                # Update checkpoint
                checkpoint = {
                    'last_processed_id': issue.id,
                    'processed_ids': list(processed_ids),
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(checkpoint_file, 'w') as f:
                    json.dump(checkpoint, f)
        
        # Success - remove checkpoint
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            
    except Exception as e:
        print(f"Sync failed at checkpoint: {last_processed_id}")
        print(f"Run again to resume from checkpoint")
        raise
```

## Best Practices

### 1. API Key Security

```python
# Use environment variables
api_key = os.getenv("LINEAR_API_KEY")
if not api_key:
    raise ValueError("LINEAR_API_KEY not set")

# For production, use secret management
from your_secret_manager import get_secret
api_key = get_secret("linear/api_key")
```

### 2. Respect Rate Limits

```python
class RateLimitedLinearConnector(LinearConnector):
    """Connector with rate limit awareness."""
    
    def __init__(self, requests_per_minute=60, **kwargs):
        super().__init__(**kwargs)
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    def _wait_if_needed(self):
        """Wait if approaching rate limit."""
        now = time.time()
        # Remove old requests
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                print(f"Rate limit reached. Waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)
    
    def execute_query(self, query, variables=None):
        """Execute with rate limiting."""
        self._wait_if_needed()
        self.request_times.append(time.time())
        return super().execute_query(query, variables)
```

### 3. Efficient Queries

```python
# Good - request only needed fields
EFFICIENT_ISSUE_QUERY = """
  query GetIssues($filter: IssueFilter) {
    issues(filter: $filter) {
      nodes {
        id
        title
        identifier
        state {
          name
          type
        }
        updatedAt
      }
    }
  }
"""

# Bad - requesting everything
INEFFICIENT_QUERY = """
  query GetIssues {
    issues {
      nodes {
        ... on Issue {
          __typename
          # All 50+ fields
        }
      }
    }
  }
"""
```

## Troubleshooting

### Connection Issues

```python
# Test connection
try:
    connector = LinearConnector(api_key="your-key")
    connector.authenticate()
    user = connector.get_current_user()
    print(f"Connected as: {user.name} ({user.email})")
except Exception as e:
    print(f"Connection failed: {e}")
    print("Check:")
    print("1. API key is valid")
    print("2. Network connectivity")
    print("3. Linear API status")
```

### Data Validation

```python
def validate_linear_issue(issue):
    """Validate Linear issue data."""
    required_fields = ['id', 'title', 'identifier', 'state']
    missing = []
    
    for field in required_fields:
        if not hasattr(issue, field):
            missing.append(field)
    
    if missing:
        raise ValueError(f"Issue missing required fields: {missing}")
    
    # Validate data types
    if not isinstance(issue.title, str):
        raise ValueError("Issue title must be string")
    
    if hasattr(issue, 'priority') and not isinstance(issue.priority, int):
        raise ValueError("Issue priority must be integer")
    
    return True
```

## Next Steps

- Explore other connectors:
  - [Notion Connector](notion.md) for wiki integration
  - [Slack Connector](slack.md) for conversation import
  - [GitHub Connector](github.md) for code integration
- Learn about [Custom Connectors](custom.md)
- See [Cookbook Examples](../cookbook/linear-project-sync.md)
- Check the [API Reference](../api/connectors.md#linear)