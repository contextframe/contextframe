# Slack Connector

The Slack connector enables importing messages, threads, files, and channel history from Slack workspaces into ContextFrame. This guide covers authentication, usage patterns, and best practices for preserving conversation context.

## Overview

The Slack connector can import:
- Channel messages and threads
- Direct messages (with permissions)
- File attachments and snippets
- User profiles and metadata
- Reactions and emoji
- Message edits and deletions
- Channel topics and purposes
- Workspace analytics

## Installation

The Slack connector requires the Slack SDK:

```bash
pip install "contextframe[connectors]"
# Or specifically
pip install slack-sdk
```

```python
from contextframe.connectors import SlackConnector
```

## Authentication

### OAuth Token (Recommended)

For workspace-wide access:

```python
connector = SlackConnector(
    token="xoxb-your-bot-token",
    # Optional: for user-specific actions
    user_token="xoxp-your-user-token"
)
```

### Setting Up Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Choose app name and workspace
4. Navigate to "OAuth & Permissions"
5. Add Bot Token Scopes:
   - `channels:history` - Read public channel messages
   - `channels:read` - List channels
   - `groups:history` - Read private channel messages
   - `groups:read` - List private channels
   - `im:history` - Read direct messages
   - `im:read` - List direct messages
   - `users:read` - Access user information
   - `files:read` - Download files
   - `reactions:read` - Read reactions

6. Install app to workspace
7. Copy Bot User OAuth Token

### Environment Variables

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_USER_TOKEN="xoxp-your-user-token"  # Optional
```

```python
import os

connector = SlackConnector(
    token=os.getenv("SLACK_BOT_TOKEN"),
    user_token=os.getenv("SLACK_USER_TOKEN")
)
```

## Basic Usage

### Import Channel Messages

```python
from contextframe import FrameDataset
from contextframe.connectors import SlackConnector

# Create dataset
dataset = FrameDataset.create("slack_archive.lance")

# Setup connector
connector = SlackConnector(
    token="your-bot-token"
)

# Authenticate
connector.authenticate()

# List channels
channels = connector.list_channels()
for channel in channels:
    print(f"#{channel['name']} ({channel['id']})")

# Import messages from specific channel
channel_id = "C1234567890"
messages = connector.sync_channel_messages(
    channel_id=channel_id,
    limit=1000  # Number of messages to fetch
)

# Convert to FrameRecords
for message in messages:
    record = connector.map_to_frame_record(message)
    dataset.add(record)

print(f"Imported {len(messages)} messages")
```

### Import with Time Range

```python
from datetime import datetime, timedelta

# Import last 30 days
start_date = datetime.now() - timedelta(days=30)
end_date = datetime.now()

messages = connector.sync_channel_messages(
    channel_id="C1234567890",
    start_time=start_date.timestamp(),
    end_time=end_date.timestamp()
)

# Process messages
for message in messages:
    record = connector.map_to_frame_record(message)
    
    # Add channel context
    record.metadata['collection'] = f"slack-{channel['name']}"
    record.metadata['tags'].append(f"channel:{channel['name']}")
    
    dataset.add(record)
```

### Import Threads

```python
def import_channel_with_threads(connector, dataset, channel_id):
    """Import channel messages including thread replies."""
    
    # Get channel info
    channel = connector.get_channel_info(channel_id)
    
    # Get messages
    messages = connector.sync_channel_messages(channel_id)
    
    for message in messages:
        # Create main message record
        message_record = connector.map_to_frame_record(message)
        message_record.metadata['collection'] = f"slack-{channel['name']}"
        dataset.add(message_record)
        
        # Check for thread
        if message.get('thread_ts') == message.get('ts') and message.get('reply_count', 0) > 0:
            # This is a thread parent, get replies
            thread_messages = connector.get_thread_replies(
                channel_id=channel_id,
                thread_ts=message['ts']
            )
            
            for reply in thread_messages:
                if reply['ts'] != message['ts']:  # Skip parent
                    reply_record = connector.map_to_frame_record(reply)
                    
                    # Link to parent
                    reply_record.add_relationship(
                        message_record.uuid,
                        "child",
                        title="Thread reply"
                    )
                    
                    dataset.add(reply_record)
```

## Advanced Features

### Message Context Preservation

```python
class SlackContextPreserver:
    """Preserve Slack message context and formatting."""
    
    def __init__(self, connector):
        self.connector = connector
        self.user_cache = {}
        self.channel_cache = {}
    
    def enrich_message(self, message, channel_id):
        """Enrich message with full context."""
        enriched = message.copy()
        
        # Add channel info
        channel = self.get_channel(channel_id)
        enriched['channel_name'] = channel['name']
        enriched['channel_purpose'] = channel.get('purpose', {}).get('value', '')
        
        # Resolve user mentions
        enriched['text_formatted'] = self.format_message_text(message['text'])
        
        # Add user info
        user_id = message.get('user')
        if user_id:
            user = self.get_user(user_id)
            enriched['user_name'] = user.get('real_name', user.get('name', 'Unknown'))
            enriched['user_title'] = user.get('profile', {}).get('title', '')
            enriched['user_email'] = user.get('profile', {}).get('email', '')
        
        # Process attachments
        if 'attachments' in message:
            enriched['attachments_formatted'] = self.format_attachments(message['attachments'])
        
        # Process reactions
        if 'reactions' in message:
            enriched['reactions_formatted'] = self.format_reactions(message['reactions'])
        
        return enriched
    
    def format_message_text(self, text):
        """Convert Slack formatting to markdown."""
        import re
        
        # Format user mentions
        def replace_user_mention(match):
            user_id = match.group(1)
            user = self.get_user(user_id)
            return f"@{user.get('real_name', user.get('name', user_id))}"
        
        text = re.sub(r'<@([A-Z0-9]+)>', replace_user_mention, text)
        
        # Format channel mentions
        def replace_channel_mention(match):
            channel_id = match.group(1)
            channel = self.get_channel(channel_id)
            return f"#{channel.get('name', channel_id)}"
        
        text = re.sub(r'<#([A-Z0-9]+)(?:\|[^>]+)?>', replace_channel_mention, text)
        
        # Format links
        text = re.sub(r'<(https?://[^|>]+)\|([^>]+)>', r'[\2](\1)', text)
        text = re.sub(r'<(https?://[^>]+)>', r'\1', text)
        
        # Format code
        text = re.sub(r'```([^`]+)```', r'```\n\1\n```', text)
        
        # Format bold/italic
        text = re.sub(r'\*([^*]+)\*', r'**\1**', text)  # Bold
        text = re.sub(r'_([^_]+)_', r'*\1*', text)  # Italic
        
        return text
    
    def format_attachments(self, attachments):
        """Format attachments for storage."""
        formatted = []
        
        for attachment in attachments:
            att_text = ""
            
            # Title
            if attachment.get('title'):
                att_text += f"### {attachment['title']}\n"
                if attachment.get('title_link'):
                    att_text += f"Link: {attachment['title_link']}\n"
            
            # Text content
            if attachment.get('text'):
                att_text += f"{attachment['text']}\n"
            
            # Fields
            if attachment.get('fields'):
                for field in attachment['fields']:
                    att_text += f"**{field['title']}**: {field['value']}\n"
            
            # Images
            if attachment.get('image_url'):
                att_text += f"\n![Image]({attachment['image_url']})\n"
            
            formatted.append(att_text)
        
        return "\n---\n".join(formatted)
    
    def format_reactions(self, reactions):
        """Format reactions for display."""
        reaction_text = []
        
        for reaction in reactions:
            emoji = reaction['name']
            users = [self.get_user(u).get('real_name', u) for u in reaction['users']]
            count = reaction['count']
            
            reaction_text.append(f":{emoji}: {count} ({', '.join(users[:3])}{'...' if count > 3 else ''})")
        
        return " | ".join(reaction_text)
    
    def get_user(self, user_id):
        """Get user info with caching."""
        if user_id not in self.user_cache:
            try:
                self.user_cache[user_id] = self.connector.get_user_info(user_id)
            except:
                self.user_cache[user_id] = {'name': user_id}
        
        return self.user_cache[user_id]
    
    def get_channel(self, channel_id):
        """Get channel info with caching."""
        if channel_id not in self.channel_cache:
            try:
                self.channel_cache[channel_id] = self.connector.get_channel_info(channel_id)
            except:
                self.channel_cache[channel_id] = {'name': channel_id}
        
        return self.channel_cache[channel_id]
```

### File Handling

```python
def import_channel_files(connector, dataset, channel_id):
    """Import files shared in a channel."""
    
    # Get files
    files = connector.list_files(channel_id=channel_id)
    
    for file in files:
        # Create file record
        file_record = FrameRecord.create(
            title=file['title'] or file['name'],
            content=f"File: {file['name']}\n\n{file.get('preview', '')}",
            author=connector.get_user_info(file['user']).get('real_name', 'Unknown'),
            created_at=datetime.fromtimestamp(file['timestamp']),
            source_type="slack",
            source_url=file.get('permalink'),
            tags=["slack-file", file['mimetype'].split('/')[0]],
            custom_metadata={
                "slack_file_id": file['id'],
                "slack_file_type": file['mimetype'],
                "slack_file_size": file['size'],
                "slack_file_url": file.get('url_private'),
                "slack_channel_id": channel_id,
                "slack_user_id": file['user']
            }
        )
        
        # Download file content if text-based
        if file['mimetype'].startswith('text/') or file['name'].endswith(('.txt', '.md', '.py', '.js')):
            try:
                content = connector.download_file(file['id'])
                file_record.text_content = content
            except:
                pass
        
        dataset.add(file_record)
```

### Direct Messages

```python
def import_direct_messages(connector, dataset, user_id=None):
    """Import direct message conversations."""
    
    # Get DM channels
    conversations = connector.list_conversations(types="im")
    
    for conv in conversations:
        # Get other user
        other_user_id = conv['user']
        
        # Filter by user if specified
        if user_id and other_user_id != user_id:
            continue
        
        # Get user info
        other_user = connector.get_user_info(other_user_id)
        
        # Create collection for conversation
        collection_name = f"slack-dm-{other_user['name']}"
        
        # Get messages
        messages = connector.sync_channel_messages(conv['id'])
        
        for message in messages:
            record = connector.map_to_frame_record(message)
            record.metadata['collection'] = collection_name
            record.metadata['tags'].append("direct-message")
            record.metadata['custom_metadata']['conversation_with'] = other_user['real_name']
            
            dataset.add(record)
```

### Search Integration

```python
def search_slack_history(connector, query, channels=None):
    """Search Slack message history."""
    
    # Use Slack search API
    results = connector.search_messages(
        query=query,
        sort="timestamp",
        sort_dir="desc",
        count=100
    )
    
    messages = results['messages']['matches']
    
    # Filter by channels if specified
    if channels:
        messages = [m for m in messages if m['channel']['id'] in channels]
    
    return messages

def import_search_results(connector, dataset, query):
    """Import messages matching search query."""
    
    messages = search_slack_history(connector, query)
    
    # Group by channel for context
    by_channel = {}
    for message in messages:
        channel_id = message['channel']['id']
        if channel_id not in by_channel:
            by_channel[channel_id] = []
        by_channel[channel_id].append(message)
    
    # Import with context
    for channel_id, channel_messages in by_channel.items():
        channel = connector.get_channel_info(channel_id)
        
        for message in channel_messages:
            record = connector.map_to_frame_record(message)
            record.metadata['collection'] = f"slack-search-{query[:20]}"
            record.metadata['tags'].extend(['search-result', f"channel:{channel['name']}"])
            record.metadata['custom_metadata']['search_query'] = query
            
            dataset.add(record)
```

## Data Mapping

### Message to FrameRecord

```python
def map_to_frame_record(self, slack_message):
    """Map Slack message to FrameRecord."""
    
    # Get formatted content
    context_preserver = SlackContextPreserver(self)
    enriched = context_preserver.enrich_message(
        slack_message, 
        slack_message.get('channel')
    )
    
    # Build content
    content = enriched['text_formatted']
    
    # Add attachments
    if enriched.get('attachments_formatted'):
        content += f"\n\n{enriched['attachments_formatted']}"
    
    # Add reactions
    if enriched.get('reactions_formatted'):
        content += f"\n\nReactions: {enriched['reactions_formatted']}"
    
    # Extract metadata
    metadata = {
        "slack_message_ts": slack_message['ts'],
        "slack_channel_id": slack_message.get('channel'),
        "slack_channel_name": enriched.get('channel_name'),
        "slack_user_id": slack_message.get('user'),
        "slack_user_name": enriched.get('user_name'),
        "slack_type": slack_message['type'],
        "slack_subtype": slack_message.get('subtype'),
        "slack_thread_ts": slack_message.get('thread_ts'),
        "slack_reply_count": slack_message.get('reply_count', 0),
        "slack_reactions": slack_message.get('reactions', []),
        "slack_edited": slack_message.get('edited', {})
    }
    
    # Handle special message types
    if slack_message.get('subtype') == 'file_share':
        metadata['slack_files'] = slack_message.get('files', [])
    
    # Generate tags
    tags = ["slack-message"]
    
    if slack_message.get('thread_ts'):
        tags.append("threaded")
    
    if slack_message.get('subtype'):
        tags.append(f"subtype:{slack_message['subtype']}")
    
    if enriched.get('channel_name'):
        tags.append(f"channel:{enriched['channel_name']}")
    
    # Create record
    return FrameRecord.create(
        title=self.generate_message_title(enriched),
        content=content,
        author=enriched.get('user_name', 'Unknown'),
        created_at=datetime.fromtimestamp(float(slack_message['ts'])),
        source_type="slack",
        source_url=self.generate_message_url(slack_message),
        tags=tags,
        custom_metadata=metadata
    )

def generate_message_title(self, enriched_message):
    """Generate descriptive title for message."""
    text = enriched_message.get('text_formatted', '')
    
    # Truncate and clean
    title = text.split('\n')[0][:100]
    
    # Add context
    channel = enriched_message.get('channel_name', 'unknown')
    user = enriched_message.get('user_name', 'Unknown')
    
    if len(title) < 20:
        return f"{user} in #{channel}: {title}"
    else:
        return title

def generate_message_url(self, message):
    """Generate Slack archive URL for message."""
    team = self.get_team_info()
    domain = team.get('domain', 'workspace')
    
    channel = message.get('channel', 'unknown')
    ts = message['ts'].replace('.', '')
    
    return f"https://{domain}.slack.com/archives/{channel}/p{ts}"
```

### Thread Mapping

```python
class SlackThreadMapper:
    """Map Slack threads to hierarchical records."""
    
    def map_thread_to_records(self, connector, thread_messages):
        """Map a complete thread to related FrameRecords."""
        records = []
        message_map = {}  # ts -> record mapping
        
        # Sort by timestamp
        thread_messages.sort(key=lambda m: float(m['ts']))
        
        # Process parent first
        parent = thread_messages[0]
        parent_record = connector.map_to_frame_record(parent)
        parent_record.metadata['tags'].append('thread-parent')
        parent_record.metadata['custom_metadata']['thread_reply_count'] = len(thread_messages) - 1
        
        records.append(parent_record)
        message_map[parent['ts']] = parent_record
        
        # Process replies
        for reply in thread_messages[1:]:
            reply_record = connector.map_to_frame_record(reply)
            reply_record.metadata['tags'].append('thread-reply')
            
            # Link to parent
            reply_record.add_relationship(
                parent_record.uuid,
                "child",
                title="Reply in thread"
            )
            
            # Link to previous message if mentions
            mentioned_users = self.extract_mentions(reply['text'])
            for ts, record in message_map.items():
                if record.metadata['custom_metadata'].get('slack_user_id') in mentioned_users:
                    reply_record.add_relationship(
                        record.uuid,
                        "reference",
                        title="Mentions user"
                    )
            
            records.append(reply_record)
            message_map[reply['ts']] = reply_record
        
        return records
    
    def extract_mentions(self, text):
        """Extract user mentions from message text."""
        import re
        mentions = re.findall(r'<@([A-Z0-9]+)>', text)
        return mentions
```

## Sync Strategies

### Incremental Sync

```python
def incremental_sync_channel(connector, dataset, channel_id, last_sync_ts=None):
    """Sync only new messages since last sync."""
    
    # Get channel info
    channel = connector.get_channel_info(channel_id)
    
    # Build query parameters
    params = {
        'channel': channel_id,
        'limit': 1000
    }
    
    if last_sync_ts:
        params['oldest'] = last_sync_ts
    
    # Get messages
    messages = connector.get_channel_history(**params)
    
    # Track stats
    new_messages = 0
    updated_messages = 0
    
    for message in messages:
        # Check if exists
        existing = dataset.scanner(
            filter=f"custom_metadata.slack_message_ts = '{message['ts']}'"
        ).to_table().to_pylist()
        
        record = connector.map_to_frame_record(message)
        
        if existing:
            # Check if edited
            if message.get('edited'):
                dataset.update_record(existing[0]['uuid'], record)
                updated_messages += 1
        else:
            dataset.add(record)
            new_messages += 1
    
    print(f"Channel #{channel['name']}: {new_messages} new, {updated_messages} updated")
    
    return new_messages, updated_messages
```

### Real-time Sync

```python
import asyncio
from slack_sdk.rtm_v2 import RTMClient

class SlackRealTimeSync:
    """Real-time message sync using RTM."""
    
    def __init__(self, connector, dataset):
        self.connector = connector
        self.dataset = dataset
        self.rtm = RTMClient(token=connector.token)
    
    async def start(self):
        """Start real-time sync."""
        
        @self.rtm.on("message")
        async def handle_message(client, event):
            """Handle incoming messages."""
            try:
                # Skip bot messages
                if event.get('subtype') == 'bot_message':
                    return
                
                # Map to FrameRecord
                record = self.connector.map_to_frame_record(event)
                
                # Add to dataset
                self.dataset.add(record)
                
                print(f"New message in #{event.get('channel')}")
                
            except Exception as e:
                print(f"Error handling message: {e}")
        
        @self.rtm.on("message_changed")
        async def handle_edit(client, event):
            """Handle message edits."""
            message = event['message']
            
            # Find existing record
            existing = self.dataset.scanner(
                filter=f"custom_metadata.slack_message_ts = '{message['ts']}'"
            ).to_table().to_pylist()
            
            if existing:
                record = self.connector.map_to_frame_record(message)
                self.dataset.update_record(existing[0]['uuid'], record)
                print(f"Updated message in #{event.get('channel')}")
        
        # Start RTM client
        await self.rtm.start()
    
    def run(self):
        """Run real-time sync."""
        asyncio.run(self.start())
```

### Workspace Backup

```python
def backup_workspace(connector, dataset, include_private=False):
    """Complete workspace backup."""
    
    stats = {
        'channels': 0,
        'messages': 0,
        'files': 0,
        'users': 0
    }
    
    # Get all channels
    channel_types = "public_channel"
    if include_private:
        channel_types += ",private_channel"
    
    channels = connector.list_conversations(types=channel_types)
    
    # Process each channel
    for channel in channels:
        print(f"\nProcessing #{channel['name']}...")
        
        # Create channel collection header
        channel_record = FrameRecord.create(
            title=f"#{channel['name']}",
            content=channel.get('purpose', {}).get('value', 'No description'),
            record_type="collection_header",
            collection=f"slack-{channel['name']}",
            source_type="slack",
            tags=["slack-channel"],
            custom_metadata={
                "slack_channel_id": channel['id'],
                "slack_channel_name": channel['name'],
                "slack_channel_created": channel['created'],
                "slack_channel_creator": channel.get('creator'),
                "slack_channel_members": channel.get('num_members', 0),
                "slack_channel_archived": channel.get('is_archived', False)
            }
        )
        dataset.add(channel_record)
        stats['channels'] += 1
        
        # Get all messages
        messages = connector.sync_channel_messages(
            channel_id=channel['id'],
            include_threads=True
        )
        
        for message in messages:
            record = connector.map_to_frame_record(message)
            record.metadata['collection'] = f"slack-{channel['name']}"
            record.add_relationship(
                channel_record.uuid,
                "member_of",
                title=f"Message in #{channel['name']}"
            )
            dataset.add(record)
            stats['messages'] += 1
        
        # Get channel files
        files = connector.list_files(channel_id=channel['id'])
        for file in files:
            # Process file (implementation from earlier)
            stats['files'] += 1
    
    # Get all users
    users = connector.list_users()
    for user in users:
        user_record = FrameRecord.create(
            title=user['real_name'] or user['name'],
            content=f"Slack User: {user['real_name']}\nTitle: {user.get('profile', {}).get('title', 'N/A')}",
            source_type="slack",
            record_type="profile",
            tags=["slack-user"],
            custom_metadata={
                "slack_user_id": user['id'],
                "slack_user_name": user['name'],
                "slack_user_email": user.get('profile', {}).get('email'),
                "slack_user_title": user.get('profile', {}).get('title'),
                "slack_user_timezone": user.get('tz'),
                "slack_user_deleted": user.get('deleted', False)
            }
        )
        dataset.add(user_record)
        stats['users'] += 1
    
    print(f"\nBackup complete:")
    print(f"  Channels: {stats['channels']}")
    print(f"  Messages: {stats['messages']}")
    print(f"  Files: {stats['files']}")
    print(f"  Users: {stats['users']}")
    
    return stats
```

## Search and Analytics

### Message Analytics

```python
def analyze_slack_activity(dataset):
    """Analyze Slack workspace activity."""
    
    analytics = {
        'total_messages': 0,
        'by_channel': {},
        'by_user': {},
        'by_hour': {},
        'by_day': {},
        'thread_stats': {
            'total_threads': 0,
            'total_replies': 0,
            'avg_thread_length': 0
        },
        'reaction_stats': {}
    }
    
    # Scan Slack messages
    scanner = dataset.scanner(
        filter="source_type = 'slack' AND tags.contains('slack-message')"
    )
    
    threads = {}
    
    for batch in scanner.to_batches():
        for row in batch.to_pylist():
            analytics['total_messages'] += 1
            metadata = row.get('custom_metadata', {})
            
            # Channel distribution
            channel = metadata.get('slack_channel_name', 'unknown')
            analytics['by_channel'][channel] = analytics['by_channel'].get(channel, 0) + 1
            
            # User distribution
            user = row.get('author', 'Unknown')
            analytics['by_user'][user] = analytics['by_user'].get(user, 0) + 1
            
            # Time distribution
            created = row.get('created_at')
            if created:
                dt = datetime.fromisoformat(created)
                hour = dt.hour
                day = dt.strftime('%A')
                
                analytics['by_hour'][hour] = analytics['by_hour'].get(hour, 0) + 1
                analytics['by_day'][day] = analytics['by_day'].get(day, 0) + 1
            
            # Thread analysis
            thread_ts = metadata.get('slack_thread_ts')
            if thread_ts:
                if thread_ts not in threads:
                    threads[thread_ts] = 0
                threads[thread_ts] += 1
            
            # Reaction analysis
            reactions = metadata.get('slack_reactions', [])
            for reaction in reactions:
                emoji = reaction['name']
                analytics['reaction_stats'][emoji] = analytics['reaction_stats'].get(emoji, 0) + reaction['count']
    
    # Calculate thread stats
    if threads:
        analytics['thread_stats']['total_threads'] = len(threads)
        analytics['thread_stats']['total_replies'] = sum(threads.values())
        analytics['thread_stats']['avg_thread_length'] = sum(threads.values()) / len(threads)
    
    # Sort results
    analytics['by_channel'] = dict(sorted(analytics['by_channel'].items(), key=lambda x: x[1], reverse=True))
    analytics['by_user'] = dict(sorted(analytics['by_user'].items(), key=lambda x: x[1], reverse=True)[:20])
    analytics['reaction_stats'] = dict(sorted(analytics['reaction_stats'].items(), key=lambda x: x[1], reverse=True)[:10])
    
    return analytics
```

### Conversation Search

```python
def search_conversations(dataset, query, user=None, channel=None):
    """Search Slack conversations with context."""
    
    # Build filter
    filters = ["source_type = 'slack'"]
    
    if user:
        filters.append(f"author = '{user}' OR custom_metadata.slack_user_name = '{user}'")
    
    if channel:
        filters.append(f"custom_metadata.slack_channel_name = '{channel}'")
    
    filter_str = " AND ".join(filters)
    
    # Search
    results = dataset.full_text_search(
        query,
        filter=filter_str,
        limit=50
    )
    
    # Group by thread for context
    threads = {}
    
    for result in results.to_pylist():
        thread_ts = result['custom_metadata'].get('slack_thread_ts', result['custom_metadata'].get('slack_message_ts'))
        
        if thread_ts not in threads:
            threads[thread_ts] = {
                'messages': [],
                'channel': result['custom_metadata'].get('slack_channel_name'),
                'participants': set()
            }
        
        threads[thread_ts]['messages'].append(result)
        threads[thread_ts]['participants'].add(result['author'])
    
    # Sort threads by relevance
    sorted_threads = sorted(
        threads.items(),
        key=lambda x: len(x[1]['messages']),
        reverse=True
    )
    
    return sorted_threads
```

## Integration Patterns

### Slack + GitHub Integration

```python
def link_slack_github_activity(slack_connector, github_connector, dataset):
    """Link Slack discussions to GitHub activity."""
    
    # Search for GitHub references in Slack
    github_pattern = r'github\.com/([^/]+)/([^/]+)/(pull|issues)/(\d+)'
    
    messages = dataset.scanner(
        filter="source_type = 'slack' AND text_content LIKE '%github.com%'"
    ).to_table().to_pylist()
    
    for message in messages:
        import re
        matches = re.findall(github_pattern, message['text_content'])
        
        for owner, repo, type, number in matches:
            # Get GitHub item
            if type == 'pull':
                item = github_connector.get_pull_request(owner, repo, int(number))
            else:
                item = github_connector.get_issue(owner, repo, int(number))
            
            # Find GitHub record
            github_records = dataset.scanner(
                filter=f"custom_metadata.github_{type}_number = {number}"
            ).to_table().to_pylist()
            
            if github_records:
                # Create relationship
                message_record = dataset.get(message['uuid'])
                message_record.add_relationship(
                    github_records[0]['uuid'],
                    'reference',
                    title=f"Discussed in Slack"
                )
                dataset.update_record(message['uuid'], message_record)
```

### Export to Markdown

```python
def export_channel_to_markdown(dataset, channel_name, output_file):
    """Export channel history to markdown."""
    
    # Get messages
    messages = dataset.scanner(
        filter=f"custom_metadata.slack_channel_name = '{channel_name}'",
        columns=['created_at', 'author', 'text_content', 'custom_metadata']
    ).to_table().to_pylist()
    
    # Sort by timestamp
    messages.sort(key=lambda m: m['created_at'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Slack Channel: #{channel_name}\n\n")
        
        current_date = None
        
        for message in messages:
            # Add date headers
            message_date = datetime.fromisoformat(message['created_at']).date()
            if message_date != current_date:
                current_date = message_date
                f.write(f"\n## {current_date.strftime('%Y-%m-%d')}\n\n")
            
            # Write message
            timestamp = datetime.fromisoformat(message['created_at']).strftime('%H:%M')
            author = message['author']
            content = message['text_content']
            
            # Handle threads
            thread_indicator = ""
            if message['custom_metadata'].get('slack_reply_count', 0) > 0:
                thread_indicator = f" 🧵 ({message['custom_metadata']['slack_reply_count']} replies)"
            
            f.write(f"**[{timestamp}] {author}**{thread_indicator}\n{content}\n\n")
```

## Performance Optimization

### Batch Message Fetching

```python
def batch_fetch_messages(connector, channel_ids, batch_size=10):
    """Fetch messages from multiple channels efficiently."""
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    all_messages = {}
    
    def fetch_channel(channel_id):
        try:
            messages = connector.sync_channel_messages(
                channel_id=channel_id,
                limit=1000
            )
            return channel_id, messages
        except Exception as e:
            print(f"Error fetching {channel_id}: {e}")
            return channel_id, []
    
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        future_to_channel = {
            executor.submit(fetch_channel, ch_id): ch_id
            for ch_id in channel_ids
        }
        
        for future in as_completed(future_to_channel):
            channel_id, messages = future.result()
            all_messages[channel_id] = messages
            print(f"Fetched {len(messages)} messages from {channel_id}")
    
    return all_messages
```

### Message Caching

```python
class CachedSlackConnector(SlackConnector):
    """Slack connector with message caching."""
    
    def __init__(self, cache_dir=".slack_cache", **kwargs):
        super().__init__(**kwargs)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_channel_history(self, channel, **kwargs):
        """Get channel history with caching."""
        import hashlib
        import pickle
        
        # Create cache key
        cache_key = hashlib.md5(
            f"{channel}:{kwargs}".encode()
        ).hexdigest()
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Check cache
        if cache_file.exists():
            # Cache hit
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                
            # Check if we need newer messages
            if 'oldest' in kwargs:
                # Incremental fetch, use cache as base
                return cached_data
        
        # Fetch from API
        messages = super().get_channel_history(channel, **kwargs)
        
        # Cache results
        with open(cache_file, 'wb') as f:
            pickle.dump(messages, f)
        
        return messages
```

## Error Handling

### Rate Limit Handling

```python
from slack_sdk.errors import SlackApiError
import time

def handle_slack_rate_limits(func):
    """Decorator to handle Slack rate limits."""
    
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except SlackApiError as e:
                if e.response['error'] == 'rate_limited':
                    retry_after = int(e.response.headers.get('Retry-After', 60))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    retry_count += 1
                else:
                    raise
        
        raise Exception("Max retries exceeded for rate limit")
    
    return wrapper

# Usage
@handle_slack_rate_limits
def safe_get_messages(connector, channel_id):
    return connector.get_channel_history(channel_id)
```

### Permission Errors

```python
def handle_permission_errors(connector, channel_id):
    """Handle channel access permission errors."""
    
    try:
        messages = connector.get_channel_history(channel_id)
        return messages
    except SlackApiError as e:
        error = e.response['error']
        
        if error == 'not_in_channel':
            print(f"Bot not in channel {channel_id}. Attempting to join...")
            try:
                connector.join_channel(channel_id)
                return connector.get_channel_history(channel_id)
            except:
                print(f"Cannot join channel {channel_id}")
                return []
        
        elif error == 'channel_not_found':
            print(f"Channel {channel_id} not found or is private")
            return []
        
        elif error == 'missing_scope':
            print(f"Missing required scope: {e.response.get('needed', 'unknown')}")
            return []
        
        else:
            raise
```

## Best Practices

### 1. Token Security

```python
# Use environment variables
token = os.getenv("SLACK_BOT_TOKEN")
if not token:
    raise ValueError("SLACK_BOT_TOKEN not set")

# For production, use secret management
from your_secret_manager import get_secret
token = get_secret("slack/bot_token")
```

### 2. Efficient Message Fetching

```python
# Good - use latest timestamp
def get_new_messages(connector, channel_id, last_message_ts):
    return connector.get_channel_history(
        channel=channel_id,
        oldest=last_message_ts,
        inclusive=False
    )

# Bad - fetching all then filtering
messages = connector.get_channel_history(channel=channel_id)
new_messages = [m for m in messages if float(m['ts']) > last_ts]
```

### 3. Context Preservation

```python
def preserve_message_context(message, channel_info, thread_context=None):
    """Preserve full message context."""
    
    context = {
        'message': message,
        'channel': {
            'name': channel_info['name'],
            'purpose': channel_info.get('purpose', {}).get('value'),
            'topic': channel_info.get('topic', {}).get('value')
        },
        'timestamp': datetime.fromtimestamp(float(message['ts'])),
        'permalink': generate_permalink(message)
    }
    
    if thread_context:
        context['thread'] = {
            'parent_ts': thread_context['parent_ts'],
            'reply_count': thread_context['reply_count'],
            'participants': thread_context['participants']
        }
    
    return context
```

## Troubleshooting

### Connection Issues

```python
# Test authentication
try:
    connector.authenticate()
    # Test API access
    auth_test = connector.client.auth_test()
    print(f"Authenticated as: {auth_test['user']} in team {auth_test['team']}")
    
    # Check scopes
    print(f"Bot scopes: {auth_test.get('bot_scopes', [])}")
    
except SlackApiError as e:
    print(f"Authentication failed: {e.response['error']}")
    print("Check:")
    print("1. Bot token is valid")
    print("2. App is installed to workspace")
    print("3. Required scopes are granted")
```

### Missing Messages

```python
def diagnose_missing_messages(connector, channel_id):
    """Diagnose why messages might be missing."""
    
    issues = []
    
    # Check channel membership
    try:
        info = connector.get_channel_info(channel_id)
        if not info.get('is_member'):
            issues.append("Bot is not a member of this channel")
    except:
        issues.append("Cannot access channel info - might be private")
    
    # Check scopes
    auth = connector.client.auth_test()
    scopes = auth.get('bot_scopes', [])
    
    required_scopes = ['channels:history', 'groups:history']
    missing_scopes = [s for s in required_scopes if s not in scopes]
    
    if missing_scopes:
        issues.append(f"Missing scopes: {missing_scopes}")
    
    # Check time range
    oldest_allowed = datetime.now() - timedelta(days=90)  # Free tier limit
    issues.append(f"Note: Free tier can only access messages from last 90 days")
    
    return issues
```

## Next Steps

- Explore other connectors:
  - [Discord Connector](discord.md) for community discussions
  - [Linear Connector](linear.md) for project management
  - [Notion Connector](notion.md) for knowledge bases
- Learn about [Custom Connectors](custom.md)
- See [Cookbook Examples](../cookbook/slack-analytics.md)
- Check the [API Reference](../api/connectors.md#slack)