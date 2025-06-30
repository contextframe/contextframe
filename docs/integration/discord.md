# Discord Connector

The Discord connector enables importing messages, threads, attachments, and server activity from Discord servers into ContextFrame. This guide covers bot setup, authentication, and best practices for preserving community discussions.

## Overview

The Discord connector can import:
- Server channels and categories
- Text messages and embeds
- Voice channel activity logs
- Threads and forum posts
- Direct messages (with permissions)
- Attachments and media
- User profiles and roles
- Reactions and interactions
- Server events and audit logs

## Installation

The Discord connector requires discord.py:

```bash
pip install "contextframe[connectors]"
# Or specifically
pip install discord.py
```

```python
from contextframe.connectors import DiscordConnector
```

## Authentication

### Bot Token Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" section
4. Click "Add Bot"
5. Under "Privileged Gateway Intents", enable:
   - Server Members Intent (to get user info)
   - Message Content Intent (to read messages)
   - Presence Intent (optional, for user status)
6. Copy the bot token

### Bot Permissions

Generate invite link with required permissions:
- Read Messages/View Channels
- Read Message History
- Read Members
- Read Roles
- Download Attachments (Files)

```python
connector = DiscordConnector(
    token="your-bot-token"
)
```

### Environment Variables

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
```

```python
import os

connector = DiscordConnector(
    token=os.getenv("DISCORD_BOT_TOKEN")
)
```

## Basic Usage

### Import Server Messages

```python
from contextframe import FrameDataset
from contextframe.connectors import DiscordConnector

# Create dataset
dataset = FrameDataset.create("discord_archive.lance")

# Setup connector
connector = DiscordConnector(
    token="your-bot-token"
)

# Authenticate and connect
connector.authenticate()

# List servers (guilds)
guilds = connector.list_guilds()
for guild in guilds:
    print(f"{guild.name} (ID: {guild.id})")

# Import messages from specific channel
channel_id = 123456789012345678
messages = connector.sync_channel_messages(
    channel_id=channel_id,
    limit=1000
)

# Convert to FrameRecords
for message in messages:
    record = connector.map_to_frame_record(message)
    dataset.add(record)

print(f"Imported {len(messages)} messages")
```

### Import Entire Server

```python
def import_discord_server(connector, dataset, guild_id):
    """Import all channels from a Discord server."""
    
    # Get guild info
    guild = connector.get_guild(guild_id)
    
    # Create guild collection header
    guild_record = FrameRecord.create(
        title=f"Discord Server: {guild.name}",
        content=f"Server: {guild.name}\nMembers: {guild.member_count}\nCreated: {guild.created_at}",
        record_type="collection_header",
        collection=f"discord-{guild.name.lower().replace(' ', '-')}",
        source_type="discord",
        tags=["discord-server"],
        custom_metadata={
            "discord_guild_id": str(guild.id),
            "discord_guild_name": guild.name,
            "discord_guild_owner": str(guild.owner_id),
            "discord_guild_created": guild.created_at.isoformat(),
            "discord_member_count": guild.member_count
        }
    )
    dataset.add(guild_record)
    
    # Import categories and channels
    for category in guild.categories:
        for channel in category.channels:
            if channel.type == discord.ChannelType.text:
                print(f"Importing #{channel.name}...")
                
                messages = connector.sync_channel_messages(
                    channel_id=channel.id,
                    limit=None  # Get all messages
                )
                
                for message in messages:
                    record = connector.map_to_frame_record(message)
                    record.metadata['collection'] = f"discord-{guild.name.lower().replace(' ', '-')}"
                    record.metadata['tags'].extend([
                        f"category:{category.name}",
                        f"channel:{channel.name}"
                    ])
                    
                    # Link to guild
                    record.add_relationship(
                        guild_record.uuid,
                        "member_of",
                        title=f"Message in {guild.name}"
                    )
                    
                    dataset.add(record)
```

### Import Threads

```python
def import_channel_threads(connector, dataset, channel_id):
    """Import threads from a channel."""
    
    channel = connector.get_channel(channel_id)
    
    # Get active threads
    threads = connector.get_active_threads(channel_id)
    
    # Get archived threads
    archived = connector.get_archived_threads(channel_id)
    threads.extend(archived)
    
    for thread in threads:
        # Create thread header
        thread_record = FrameRecord.create(
            title=f"Thread: {thread.name}",
            content=f"Thread in #{channel.name}",
            record_type="collection_header",
            collection=f"discord-thread-{thread.id}",
            source_type="discord",
            tags=["discord-thread"],
            custom_metadata={
                "discord_thread_id": str(thread.id),
                "discord_thread_name": thread.name,
                "discord_parent_channel": str(channel.id),
                "discord_archived": thread.archived,
                "discord_locked": thread.locked
            }
        )
        dataset.add(thread_record)
        
        # Import thread messages
        messages = connector.sync_thread_messages(thread.id)
        
        for message in messages:
            record = connector.map_to_frame_record(message)
            record.metadata['collection'] = f"discord-thread-{thread.id}"
            
            # Link to thread
            record.add_relationship(
                thread_record.uuid,
                "child",
                title="Message in thread"
            )
            
            dataset.add(record)
```

## Advanced Features

### Rich Message Content

```python
class DiscordContentExtractor:
    """Extract and format Discord message content."""
    
    def __init__(self, connector):
        self.connector = connector
    
    def format_message(self, message):
        """Format Discord message with all components."""
        formatted = ""
        
        # Main content
        if message.content:
            formatted += self.format_content(message.content)
        
        # Embeds
        if message.embeds:
            formatted += "\n\n" + self.format_embeds(message.embeds)
        
        # Attachments
        if message.attachments:
            formatted += "\n\n" + self.format_attachments(message.attachments)
        
        # Stickers
        if message.stickers:
            formatted += "\n\n" + self.format_stickers(message.stickers)
        
        # Reactions
        if message.reactions:
            formatted += "\n\n" + self.format_reactions(message.reactions)
        
        # Reply context
        if message.reference:
            formatted = self.add_reply_context(message, formatted)
        
        return formatted
    
    def format_content(self, content):
        """Convert Discord formatting to markdown."""
        import re
        
        # Convert user mentions
        def replace_user_mention(match):
            user_id = match.group(1)
            user = self.connector.get_user(int(user_id))
            return f"@{user.name if user else user_id}"
        
        content = re.sub(r'<@!?(\d+)>', replace_user_mention, content)
        
        # Convert channel mentions
        def replace_channel_mention(match):
            channel_id = match.group(1)
            channel = self.connector.get_channel(int(channel_id))
            return f"#{channel.name if channel else channel_id}"
        
        content = re.sub(r'<#(\d+)>', replace_channel_mention, content)
        
        # Convert role mentions
        def replace_role_mention(match):
            role_id = match.group(1)
            # Note: Would need guild context to resolve role names
            return f"@role:{role_id}"
        
        content = re.sub(r'<@&(\d+)>', replace_role_mention, content)
        
        # Convert custom emojis
        content = re.sub(r'<:(\w+):(\d+)>', r':\1:', content)
        content = re.sub(r'<a:(\w+):(\d+)>', r':\1: (animated)', content)
        
        # Discord uses markdown already, just clean up
        return content
    
    def format_embeds(self, embeds):
        """Format Discord embeds."""
        formatted_embeds = []
        
        for embed in embeds:
            embed_text = "**[Embed]**\n"
            
            if embed.title:
                embed_text += f"**{embed.title}**\n"
            
            if embed.description:
                embed_text += f"{embed.description}\n"
            
            if embed.fields:
                for field in embed.fields:
                    if field.inline:
                        embed_text += f"**{field.name}**: {field.value} | "
                    else:
                        embed_text += f"\n**{field.name}**\n{field.value}\n"
            
            if embed.footer:
                embed_text += f"\n_{embed.footer.text}_"
            
            if embed.url:
                embed_text += f"\n[Link]({embed.url})"
            
            formatted_embeds.append(embed_text)
        
        return "\n---\n".join(formatted_embeds)
    
    def format_attachments(self, attachments):
        """Format attachment information."""
        att_text = "**Attachments:**\n"
        
        for att in attachments:
            att_text += f"- [{att.filename}]({att.url}) ({att.size} bytes)\n"
            
            # Add preview for images
            if att.content_type and att.content_type.startswith('image/'):
                att_text += f"  ![{att.filename}]({att.url})\n"
        
        return att_text
    
    def format_reactions(self, reactions):
        """Format reactions."""
        reaction_parts = []
        
        for reaction in reactions:
            emoji = reaction.emoji
            count = reaction.count
            
            if hasattr(emoji, 'name'):
                reaction_parts.append(f"{emoji.name} ({count})")
            else:
                reaction_parts.append(f"{emoji} ({count})")
        
        return "Reactions: " + " | ".join(reaction_parts)
    
    def add_reply_context(self, message, formatted_content):
        """Add reply context to message."""
        if message.reference and message.reference.message_id:
            try:
                replied_to = self.connector.get_message(
                    message.channel.id,
                    message.reference.message_id
                )
                
                reply_preview = replied_to.content[:100] + "..." if len(replied_to.content) > 100 else replied_to.content
                reply_context = f"> **Reply to {replied_to.author.name}**: {reply_preview}\n\n"
                
                return reply_context + formatted_content
            except:
                return formatted_content
        
        return formatted_content
```

### Voice Channel Events

```python
def import_voice_events(connector, dataset, guild_id, days=30):
    """Import voice channel activity from audit logs."""
    
    guild = connector.get_guild(guild_id)
    
    # Get audit logs
    after = datetime.now() - timedelta(days=days)
    
    voice_events = []
    
    async for entry in guild.audit_logs(
        after=after,
        action=discord.AuditLogAction.member_voice_move
    ):
        event_record = FrameRecord.create(
            title=f"Voice: {entry.user.name} → {entry.extra.channel.name}",
            content=f"{entry.user.name} joined voice channel {entry.extra.channel.name}",
            author=entry.user.name,
            created_at=entry.created_at.isoformat(),
            source_type="discord",
            tags=["discord-voice", "voice-activity"],
            custom_metadata={
                "discord_event_type": "voice_join",
                "discord_user_id": str(entry.user.id),
                "discord_channel_id": str(entry.extra.channel.id),
                "discord_channel_name": entry.extra.channel.name
            }
        )
        dataset.add(event_record)
```

### Forum Channels

```python
def import_forum_channel(connector, dataset, forum_id):
    """Import Discord forum channel with posts."""
    
    forum = connector.get_channel(forum_id)
    
    # Get all threads (forum posts)
    threads = forum.threads
    
    for thread in threads:
        # Get initial post
        starter_message = None
        async for message in thread.history(oldest_first=True, limit=1):
            starter_message = message
            break
        
        if not starter_message:
            continue
        
        # Create forum post record
        post_record = FrameRecord.create(
            title=thread.name,
            content=starter_message.content if starter_message else "",
            author=starter_message.author.name if starter_message else "Unknown",
            created_at=thread.created_at.isoformat(),
            source_type="discord",
            record_type="collection_header",
            collection=f"discord-forum-{thread.id}",
            tags=["discord-forum", "forum-post"],
            custom_metadata={
                "discord_thread_id": str(thread.id),
                "discord_forum_id": str(forum_id),
                "discord_forum_name": forum.name,
                "discord_tags": [tag.name for tag in thread.applied_tags]
            }
        )
        dataset.add(post_record)
        
        # Import replies
        messages = connector.sync_thread_messages(thread.id)
        
        for i, message in enumerate(messages[1:], 1):  # Skip starter
            reply_record = connector.map_to_frame_record(message)
            reply_record.metadata['tags'].append("forum-reply")
            
            # Link to post
            reply_record.add_relationship(
                post_record.uuid,
                "child",
                title=f"Reply #{i}"
            )
            
            dataset.add(reply_record)
```

### Member Analytics

```python
def analyze_member_activity(connector, dataset, guild_id):
    """Analyze member activity in a Discord server."""
    
    guild = connector.get_guild(guild_id)
    
    member_stats = {}
    
    # Analyze all text channels
    for channel in guild.text_channels:
        messages = connector.sync_channel_messages(channel.id, limit=10000)
        
        for message in messages:
            author_id = str(message.author.id)
            
            if author_id not in member_stats:
                member_stats[author_id] = {
                    'name': message.author.name,
                    'display_name': message.author.display_name,
                    'total_messages': 0,
                    'channels_active': set(),
                    'first_message': message.created_at,
                    'last_message': message.created_at,
                    'roles': [],
                    'reactions_given': 0,
                    'reactions_received': 0
                }
            
            stats = member_stats[author_id]
            stats['total_messages'] += 1
            stats['channels_active'].add(channel.name)
            stats['first_message'] = min(stats['first_message'], message.created_at)
            stats['last_message'] = max(stats['last_message'], message.created_at)
            stats['reactions_received'] += sum(r.count for r in message.reactions)
    
    # Get member roles
    for member in guild.members:
        member_id = str(member.id)
        if member_id in member_stats:
            member_stats[member_id]['roles'] = [role.name for role in member.roles if role.name != "@everyone"]
    
    # Create analytics records
    for member_id, stats in member_stats.items():
        analytics_record = FrameRecord.create(
            title=f"Member Analytics: {stats['name']}",
            content=f"""
# Discord Member: {stats['display_name']}

## Activity Summary
- Total Messages: {stats['total_messages']}
- Active Channels: {len(stats['channels_active'])}
- First Message: {stats['first_message']}
- Last Message: {stats['last_message']}
- Days Active: {(stats['last_message'] - stats['first_message']).days}

## Roles
{', '.join(stats['roles']) if stats['roles'] else 'No special roles'}

## Engagement
- Reactions Received: {stats['reactions_received']}
- Average Reactions per Message: {stats['reactions_received'] / stats['total_messages']:.2f}
""",
            author="System",
            source_type="discord",
            record_type="analytics",
            tags=["discord-analytics", "member-stats"],
            custom_metadata={
                "discord_member_id": member_id,
                "discord_guild_id": str(guild_id),
                "member_stats": stats
            }
        )
        dataset.add(analytics_record)
```

## Data Mapping

### Message to FrameRecord

```python
def map_to_frame_record(self, discord_message):
    """Map Discord message to FrameRecord."""
    
    # Extract formatted content
    extractor = DiscordContentExtractor(self)
    formatted_content = extractor.format_message(discord_message)
    
    # Build metadata
    metadata = {
        "discord_message_id": str(discord_message.id),
        "discord_channel_id": str(discord_message.channel.id),
        "discord_channel_name": discord_message.channel.name,
        "discord_guild_id": str(discord_message.guild.id) if discord_message.guild else None,
        "discord_guild_name": discord_message.guild.name if discord_message.guild else None,
        "discord_author_id": str(discord_message.author.id),
        "discord_author_name": discord_message.author.name,
        "discord_author_discriminator": discord_message.author.discriminator,
        "discord_author_bot": discord_message.author.bot,
        "discord_edited_at": discord_message.edited_at.isoformat() if discord_message.edited_at else None,
        "discord_pinned": discord_message.pinned,
        "discord_type": str(discord_message.type),
        "discord_jump_url": discord_message.jump_url
    }
    
    # Add reply context
    if discord_message.reference:
        metadata['discord_reply_to'] = str(discord_message.reference.message_id)
    
    # Add thread info
    if hasattr(discord_message.channel, 'parent'):
        metadata['discord_thread_parent'] = str(discord_message.channel.parent.id)
    
    # Generate tags
    tags = ["discord-message"]
    
    if discord_message.author.bot:
        tags.append("bot-message")
    
    if discord_message.pinned:
        tags.append("pinned")
    
    if discord_message.mentions:
        tags.append("has-mentions")
    
    if discord_message.attachments:
        tags.append("has-attachments")
    
    if isinstance(discord_message.channel, discord.Thread):
        tags.append("thread-message")
    
    # Channel type tags
    channel_type = str(discord_message.channel.type)
    tags.append(f"channel-type:{channel_type}")
    
    return FrameRecord.create(
        title=self.generate_message_title(discord_message),
        content=formatted_content,
        author=discord_message.author.display_name,
        created_at=discord_message.created_at.isoformat(),
        updated_at=discord_message.edited_at.isoformat() if discord_message.edited_at else None,
        source_type="discord",
        source_url=discord_message.jump_url,
        tags=tags,
        custom_metadata=metadata
    )

def generate_message_title(self, message):
    """Generate descriptive title for message."""
    content = message.content or "[No text content]"
    
    # Handle special message types
    if message.type == discord.MessageType.thread_created:
        return f"Thread created: {message.content}"
    elif message.type == discord.MessageType.pins_add:
        return "Message pinned"
    elif message.attachments:
        return f"File: {message.attachments[0].filename}"
    
    # Truncate content for title
    title = content.split('\n')[0][:100]
    
    if len(title) < 20:
        return f"{message.author.display_name} in #{message.channel.name}: {title}"
    
    return title
```

### Server Structure Mapping

```python
class DiscordServerMapper:
    """Map Discord server structure to collections."""
    
    def map_server_hierarchy(self, connector, guild_id):
        """Create hierarchical representation of server."""
        guild = connector.get_guild(guild_id)
        
        hierarchy = {
            'guild': {
                'id': str(guild.id),
                'name': guild.name,
                'categories': []
            }
        }
        
        # Map categories and channels
        for category in guild.categories:
            cat_data = {
                'id': str(category.id),
                'name': category.name,
                'position': category.position,
                'channels': []
            }
            
            for channel in category.channels:
                channel_data = {
                    'id': str(channel.id),
                    'name': channel.name,
                    'type': str(channel.type),
                    'position': channel.position
                }
                
                if isinstance(channel, discord.TextChannel):
                    channel_data['topic'] = channel.topic
                    channel_data['nsfw'] = channel.nsfw
                    channel_data['slowmode'] = channel.slowmode_delay
                elif isinstance(channel, discord.VoiceChannel):
                    channel_data['bitrate'] = channel.bitrate
                    channel_data['user_limit'] = channel.user_limit
                
                cat_data['channels'].append(channel_data)
            
            hierarchy['guild']['categories'].append(cat_data)
        
        # Add uncategorized channels
        uncategorized = []
        for channel in guild.channels:
            if channel.category is None:
                uncategorized.append({
                    'id': str(channel.id),
                    'name': channel.name,
                    'type': str(channel.type)
                })
        
        if uncategorized:
            hierarchy['guild']['uncategorized'] = uncategorized
        
        return hierarchy
```

## Sync Strategies

### Incremental Message Sync

```python
def incremental_sync_discord(connector, dataset, guild_id, last_sync_time=None):
    """Incrementally sync Discord messages."""
    
    guild = connector.get_guild(guild_id)
    
    sync_stats = {
        'new_messages': 0,
        'updated_messages': 0,
        'channels_synced': 0
    }
    
    for channel in guild.text_channels:
        print(f"Syncing #{channel.name}...")
        
        # Get messages since last sync
        if last_sync_time:
            messages = connector.get_messages_after(
                channel.id,
                after=last_sync_time
            )
        else:
            # Full sync
            messages = connector.sync_channel_messages(channel.id)
        
        for message in messages:
            # Check if exists
            existing = dataset.scanner(
                filter=f"custom_metadata.discord_message_id = '{message.id}'"
            ).to_table().to_pylist()
            
            record = connector.map_to_frame_record(message)
            
            if existing:
                # Check if edited
                if message.edited_at:
                    dataset.update_record(existing[0]['uuid'], record)
                    sync_stats['updated_messages'] += 1
            else:
                dataset.add(record)
                sync_stats['new_messages'] += 1
        
        sync_stats['channels_synced'] += 1
    
    return sync_stats
```

### Real-time Event Sync

```python
import asyncio
import discord

class DiscordEventSync(discord.Client):
    """Real-time Discord event synchronization."""
    
    def __init__(self, connector, dataset, **kwargs):
        super().__init__(**kwargs)
        self.connector = connector
        self.dataset = dataset
    
    async def on_ready(self):
        """Bot is ready."""
        print(f'Logged in as {self.user}')
        print(f'Monitoring {len(self.guilds)} servers')
    
    async def on_message(self, message):
        """Handle new messages."""
        # Skip DMs if not configured
        if not message.guild:
            return
        
        # Map and store
        record = self.connector.map_to_frame_record(message)
        self.dataset.add(record)
        
        print(f"New message in #{message.channel.name}")
    
    async def on_message_edit(self, before, after):
        """Handle message edits."""
        # Find existing record
        existing = self.dataset.scanner(
            filter=f"custom_metadata.discord_message_id = '{after.id}'"
        ).to_table().to_pylist()
        
        if existing:
            record = self.connector.map_to_frame_record(after)
            self.dataset.update_record(existing[0]['uuid'], record)
            print(f"Updated message in #{after.channel.name}")
    
    async def on_message_delete(self, message):
        """Handle message deletion."""
        # Mark as deleted
        existing = self.dataset.scanner(
            filter=f"custom_metadata.discord_message_id = '{message.id}'"
        ).to_table().to_pylist()
        
        if existing:
            record = self.dataset.get(existing[0]['uuid'])
            record.metadata['status'] = 'deleted'
            record.metadata['custom_metadata']['discord_deleted_at'] = datetime.now().isoformat()
            self.dataset.update_record(existing[0]['uuid'], record)
    
    async def on_thread_create(self, thread):
        """Handle thread creation."""
        thread_record = FrameRecord.create(
            title=f"Thread: {thread.name}",
            content=f"New thread created in #{thread.parent.name}",
            author=thread.owner.name if thread.owner else "Unknown",
            created_at=thread.created_at.isoformat(),
            source_type="discord",
            tags=["discord-thread", "thread-created"],
            custom_metadata={
                "discord_thread_id": str(thread.id),
                "discord_parent_id": str(thread.parent.id),
                "discord_thread_type": str(thread.type)
            }
        )
        self.dataset.add(thread_record)

def run_event_sync(connector, dataset, token):
    """Run real-time event sync."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    client = DiscordEventSync(
        connector=connector,
        dataset=dataset,
        intents=intents
    )
    
    client.run(token)
```

### Scheduled Archive

```python
def schedule_discord_archive(connector, dataset, guild_ids, interval_hours=24):
    """Schedule regular Discord archives."""
    
    import schedule
    import time
    
    def archive_guild(guild_id):
        """Archive a single guild."""
        print(f"\n[{datetime.now()}] Starting archive for guild {guild_id}")
        
        try:
            stats = incremental_sync_discord(
                connector,
                dataset,
                guild_id,
                last_sync_time=datetime.now() - timedelta(hours=interval_hours)
            )
            
            print(f"Archive complete: {stats}")
            
        except Exception as e:
            print(f"Archive failed: {e}")
    
    # Schedule archives
    for guild_id in guild_ids:
        schedule.every(interval_hours).hours.do(archive_guild, guild_id)
    
    print(f"Scheduled archives for {len(guild_ids)} guilds every {interval_hours} hours")
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
```

## Search and Analytics

### Message Search

```python
def search_discord_messages(dataset, query, guild=None, channel=None, author=None):
    """Search Discord messages with filters."""
    
    # Build filter
    filters = ["source_type = 'discord'"]
    
    if guild:
        filters.append(f"custom_metadata.discord_guild_name = '{guild}'")
    
    if channel:
        filters.append(f"custom_metadata.discord_channel_name = '{channel}'")
    
    if author:
        filters.append(f"author = '{author}' OR custom_metadata.discord_author_name = '{author}'")
    
    filter_str = " AND ".join(filters)
    
    # Search
    results = dataset.full_text_search(
        query,
        filter=filter_str,
        limit=100
    )
    
    return results.to_pylist()
```

### Channel Analytics

```python
def analyze_channel_activity(dataset, channel_name):
    """Analyze activity in a specific channel."""
    
    # Get messages
    messages = dataset.scanner(
        filter=f"custom_metadata.discord_channel_name = '{channel_name}'"
    ).to_table().to_pylist()
    
    if not messages:
        return None
    
    analytics = {
        'total_messages': len(messages),
        'unique_authors': set(),
        'message_types': {},
        'hourly_distribution': {h: 0 for h in range(24)},
        'daily_distribution': {},
        'top_participants': {},
        'thread_count': 0,
        'attachment_count': 0,
        'reaction_count': 0
    }
    
    for msg in messages:
        metadata = msg['custom_metadata']
        
        # Authors
        author = metadata.get('discord_author_name', 'Unknown')
        analytics['unique_authors'].add(author)
        analytics['top_participants'][author] = analytics['top_participants'].get(author, 0) + 1
        
        # Message types
        msg_type = metadata.get('discord_type', 'default')
        analytics['message_types'][msg_type] = analytics['message_types'].get(msg_type, 0) + 1
        
        # Time distribution
        created = datetime.fromisoformat(msg['created_at'])
        analytics['hourly_distribution'][created.hour] += 1
        
        date_key = created.date().isoformat()
        analytics['daily_distribution'][date_key] = analytics['daily_distribution'].get(date_key, 0) + 1
        
        # Features
        if 'thread-message' in msg.get('tags', []):
            analytics['thread_count'] += 1
        
        if 'has-attachments' in msg.get('tags', []):
            analytics['attachment_count'] += 1
        
        reactions = metadata.get('discord_reactions', [])
        analytics['reaction_count'] += sum(r.get('count', 0) for r in reactions)
    
    # Calculate averages
    analytics['unique_authors'] = len(analytics['unique_authors'])
    analytics['avg_messages_per_day'] = len(messages) / len(analytics['daily_distribution']) if analytics['daily_distribution'] else 0
    analytics['top_participants'] = dict(sorted(
        analytics['top_participants'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10])
    
    return analytics
```

### Role-based Analysis

```python
def analyze_role_activity(connector, dataset, guild_id):
    """Analyze activity by Discord roles."""
    
    guild = connector.get_guild(guild_id)
    
    role_stats = {}
    
    # Get all roles
    for role in guild.roles:
        if role.name == "@everyone":
            continue
        
        role_stats[role.name] = {
            'member_count': len(role.members),
            'message_count': 0,
            'active_members': set(),
            'channels_used': set()
        }
    
    # Analyze messages
    messages = dataset.scanner(
        filter=f"custom_metadata.discord_guild_id = '{guild_id}'"
    ).to_table().to_pylist()
    
    for msg in messages:
        author_id = int(msg['custom_metadata']['discord_author_id'])
        
        # Get member
        try:
            member = guild.get_member(author_id)
            if member:
                for role in member.roles:
                    if role.name != "@everyone":
                        stats = role_stats.get(role.name, {})
                        stats['message_count'] = stats.get('message_count', 0) + 1
                        stats.setdefault('active_members', set()).add(member.name)
                        stats.setdefault('channels_used', set()).add(
                            msg['custom_metadata']['discord_channel_name']
                        )
        except:
            pass
    
    # Convert sets for serialization
    for role, stats in role_stats.items():
        stats['active_members'] = len(stats.get('active_members', set()))
        stats['channels_used'] = len(stats.get('channels_used', set()))
        
        if stats['member_count'] > 0:
            stats['activity_rate'] = stats['active_members'] / stats['member_count']
    
    return role_stats
```

## Integration Patterns

### Discord + GitHub Integration

```python
def link_discord_github_activity(discord_connector, github_connector, dataset):
    """Link Discord discussions to GitHub commits/PRs."""
    
    # Search for GitHub links in Discord
    github_pattern = r'github\.com/([^/]+)/([^/]+)/(commit|pull|issues)/([a-f0-9]+|\d+)'
    
    messages = dataset.scanner(
        filter="source_type = 'discord' AND text_content LIKE '%github.com%'"
    ).to_table().to_pylist()
    
    for message in messages:
        import re
        matches = re.findall(github_pattern, message['text_content'])
        
        for owner, repo, type, identifier in matches:
            # Create relationship
            github_filter = ""
            
            if type == 'commit':
                github_filter = f"custom_metadata.github_sha LIKE '{identifier}%'"
            elif type == 'pull':
                github_filter = f"custom_metadata.github_pr_number = {identifier}"
            elif type == 'issues':
                github_filter = f"custom_metadata.github_issue_number = {identifier}"
            
            github_records = dataset.scanner(filter=github_filter).to_table().to_pylist()
            
            if github_records:
                # Link Discord message to GitHub item
                msg_record = dataset.get(message['uuid'])
                msg_record.add_relationship(
                    github_records[0]['uuid'],
                    'reference',
                    title=f"Discussed in Discord"
                )
                dataset.update_record(message['uuid'], msg_record)
```

### Community Insights Export

```python
def export_community_insights(dataset, guild_name, output_dir):
    """Export Discord community insights."""
    
    from pathlib import Path
    import json
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all guild messages
    messages = dataset.scanner(
        filter=f"custom_metadata.discord_guild_name = '{guild_name}'"
    ).to_table().to_pylist()
    
    # Channel activity
    channel_activity = {}
    for msg in messages:
        channel = msg['custom_metadata']['discord_channel_name']
        channel_activity[channel] = channel_activity.get(channel, 0) + 1
    
    # Top contributors
    contributors = {}
    for msg in messages:
        if not msg['custom_metadata'].get('discord_author_bot'):
            author = msg['author']
            contributors[author] = contributors.get(author, 0) + 1
    
    top_contributors = sorted(contributors.items(), key=lambda x: x[1], reverse=True)[:50]
    
    # Export insights
    insights = {
        'guild': guild_name,
        'period': {
            'start': min(msg['created_at'] for msg in messages),
            'end': max(msg['created_at'] for msg in messages)
        },
        'statistics': {
            'total_messages': len(messages),
            'unique_contributors': len(set(msg['author'] for msg in messages)),
            'channels_active': len(channel_activity),
            'avg_messages_per_contributor': len(messages) / len(contributors) if contributors else 0
        },
        'channel_activity': dict(sorted(channel_activity.items(), key=lambda x: x[1], reverse=True)),
        'top_contributors': [
            {'name': name, 'messages': count} for name, count in top_contributors
        ]
    }
    
    # Save insights
    with open(output_path / 'community_insights.json', 'w') as f:
        json.dump(insights, f, indent=2)
    
    # Export timeline
    timeline_data = []
    for msg in sorted(messages, key=lambda x: x['created_at']):
        timeline_data.append({
            'timestamp': msg['created_at'],
            'author': msg['author'],
            'channel': msg['custom_metadata']['discord_channel_name'],
            'preview': msg['text_content'][:100] if msg.get('text_content') else '[No content]'
        })
    
    with open(output_path / 'timeline.jsonl', 'w') as f:
        for entry in timeline_data:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Exported insights to {output_path}")
```

## Performance Optimization

### Batch Message Processing

```python
async def batch_process_messages(connector, channel_ids, batch_size=100):
    """Process messages in batches for performance."""
    
    all_messages = []
    
    async def fetch_channel_batch(channel_id):
        messages = []
        async for message in connector.get_channel(channel_id).history(limit=None):
            messages.append(message)
            
            if len(messages) >= batch_size:
                yield messages
                messages = []
        
        if messages:
            yield messages
    
    # Process channels concurrently
    import asyncio
    
    tasks = []
    for channel_id in channel_ids:
        channel = connector.get_channel(channel_id)
        if channel:
            async for batch in fetch_channel_batch(channel_id):
                all_messages.extend(batch)
    
    return all_messages
```

### Message Caching

```python
class CachedDiscordConnector(DiscordConnector):
    """Discord connector with message caching."""
    
    def __init__(self, cache_ttl=3600, **kwargs):
        super().__init__(**kwargs)
        self.message_cache = {}
        self.user_cache = {}
        self.channel_cache = {}
        self.cache_ttl = cache_ttl
    
    def get_message(self, channel_id, message_id):
        """Get message with caching."""
        cache_key = f"{channel_id}:{message_id}"
        
        if cache_key in self.message_cache:
            cached, timestamp = self.message_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached
        
        # Fetch from Discord
        message = super().get_message(channel_id, message_id)
        
        # Cache
        self.message_cache[cache_key] = (message, time.time())
        
        return message
    
    def get_user(self, user_id):
        """Get user with caching."""
        if user_id in self.user_cache:
            return self.user_cache[user_id]
        
        user = super().get_user(user_id)
        self.user_cache[user_id] = user
        
        return user
```

## Error Handling

### Rate Limit Management

```python
import asyncio
from discord import HTTPException

async def handle_rate_limits(coro):
    """Handle Discord rate limits gracefully."""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            return await coro
        except HTTPException as e:
            if e.status == 429:  # Rate limited
                retry_after = e.response.headers.get('X-RateLimit-Reset-After', 60)
                print(f"Rate limited. Waiting {retry_after} seconds...")
                await asyncio.sleep(float(retry_after))
                retry_count += 1
            else:
                raise
    
    raise Exception("Max retries exceeded for rate limit")
```

### Permission Handling

```python
def check_channel_permissions(connector, channel_id):
    """Check bot permissions for a channel."""
    
    channel = connector.get_channel(channel_id)
    if not channel:
        return {"error": "Channel not found"}
    
    me = channel.guild.me
    permissions = channel.permissions_for(me)
    
    required_perms = {
        'read_messages': permissions.read_messages,
        'read_message_history': permissions.read_message_history,
        'view_channel': permissions.view_channel,
        'attach_files': permissions.attach_files,
        'embed_links': permissions.embed_links
    }
    
    missing = [perm for perm, has in required_perms.items() if not has]
    
    return {
        'has_access': len(missing) == 0,
        'permissions': required_perms,
        'missing': missing
    }
```

## Best Practices

### 1. Bot Token Security

```python
# Use environment variables
token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
    raise ValueError("DISCORD_BOT_TOKEN not set")

# For production, use secret management
from your_secret_manager import get_secret
token = get_secret("discord/bot_token")
```

### 2. Efficient Message Fetching

```python
# Good - use built-in filtering
messages = await channel.history(
    after=datetime.now() - timedelta(days=7),
    limit=None
).flatten()

# Bad - fetch all then filter
all_messages = await channel.history(limit=None).flatten()
recent = [m for m in all_messages if m.created_at > datetime.now() - timedelta(days=7)]
```

### 3. Respect Discord Limits

```python
class RespectfulDiscordConnector(DiscordConnector):
    """Connector that respects Discord's limits."""
    
    async def sync_channel_messages(self, channel_id, **kwargs):
        """Sync with reasonable limits."""
        # Discord recommends max 100 messages per request
        messages = []
        async for message in channel.history(limit=None):
            messages.append(message)
            
            # Yield control periodically
            if len(messages) % 100 == 0:
                await asyncio.sleep(0.1)
        
        return messages
```

## Troubleshooting

### Bot Connection Issues

```python
# Test bot connection
async def test_connection(token):
    """Test Discord bot connection."""
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"Connected as {client.user}")
        print(f"Guilds: {len(client.guilds)}")
        for guild in client.guilds:
            print(f"  - {guild.name} (ID: {guild.id})")
        await client.close()
    
    try:
        await client.start(token)
    except discord.LoginFailure:
        print("Invalid token")
    except Exception as e:
        print(f"Connection failed: {e}")
```

### Missing Content Issues

```python
def diagnose_missing_content(connector, channel_id):
    """Diagnose why content might be missing."""
    
    issues = []
    
    # Check intents
    if not connector.intents.message_content:
        issues.append("Message Content Intent not enabled")
    
    # Check permissions
    perms = check_channel_permissions(connector, channel_id)
    if not perms['has_access']:
        issues.append(f"Missing permissions: {perms['missing']}")
    
    # Check bot presence
    channel = connector.get_channel(channel_id)
    if channel and channel.guild.me not in channel.members:
        issues.append("Bot not in channel")
    
    return issues
```

## Next Steps

- Explore other connectors:
  - [Slack Connector](slack.md) for workspace conversations
  - [Linear Connector](linear.md) for project management  
  - [Notion Connector](notion.md) for knowledge bases
- Learn about [Custom Connectors](custom.md)
- See [Cookbook Examples](../cookbook/discord-analytics.md)
- Check the [API Reference](../api/connectors.md#discord)