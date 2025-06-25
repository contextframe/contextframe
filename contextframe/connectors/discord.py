"""Discord connector for importing server messages into ContextFrame."""

import json
from contextframe import FrameRecord
from contextframe.connectors.base import (
    AuthType,
    ConnectorConfig,
    SourceConnector,
    SyncResult,
)
from contextframe.schema import RecordType
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set


class DiscordConnector(SourceConnector):
    """Connector for importing Discord server content."""

    def __init__(self, config: ConnectorConfig, dataset):
        """Initialize Discord connector.

        Args:
            config: Connector configuration with Discord-specific settings
            dataset: Target FrameDataset
        """
        super().__init__(config, dataset)

        # Configuration options
        self.guild_ids = config.sync_config.get("guild_ids", [])
        self.channel_ids = config.sync_config.get("channel_ids", [])
        self.channel_names = config.sync_config.get("channel_names", [])
        self.include_threads = config.sync_config.get("include_threads", True)
        self.include_forum_posts = config.sync_config.get("include_forum_posts", True)
        self.include_voice_text = config.sync_config.get("include_voice_text", False)
        self.days_to_sync = config.sync_config.get("days_to_sync", 30)
        self.user_ids = config.sync_config.get("user_ids", [])
        self.include_reactions = config.sync_config.get("include_reactions", True)
        self.include_attachments = config.sync_config.get("include_attachments", True)
        
        # Set up Discord API client
        self._setup_client()

    def _setup_client(self):
        """Set up Discord API client."""
        try:
            import discord
            self.discord = discord
            
            # Configure intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            intents.guilds = True
            
            self.intents = intents
        except ImportError:
            raise ImportError(
                "discord.py is required for Discord connector. "
                "Install with: pip install discord.py"
            )

        # We'll create the client when needed since it requires async
        self.client = None
        self._bot_token = None

        # Initialize based on auth type
        if self.config.auth_type == AuthType.TOKEN:
            self._bot_token = self.config.auth_config.get("bot_token")
            if not self._bot_token:
                raise ValueError("Discord bot token required for authentication")
        else:
            raise ValueError("Discord connector requires bot token authentication")

    def validate_connection(self) -> bool:
        """Validate Discord connection."""
        # Discord.py requires async operations, so we'll validate during sync
        # For now, just check that we have a token
        return bool(self._bot_token)

    def discover_content(self) -> dict[str, Any]:
        """Discover Discord server structure."""
        # This would require async operations, so we'll discover during sync
        return {
            "note": "Discord discovery happens during sync due to async requirements",
            "configured_guilds": self.guild_ids,
            "configured_channels": self.channel_ids,
        }

    def sync(self, incremental: bool = True) -> SyncResult:
        """Sync Discord content to ContextFrame."""
        # Discord.py requires async operations, so we'll use a sync wrapper
        import asyncio
        
        try:
            # Use existing event loop if available, otherwise create new one
            try:
                loop = asyncio.get_running_loop()
                # If we're already in an async context, we can't use run_until_complete
                # This is a limitation of the sync interface with async Discord.py
                result = SyncResult(success=False)
                result.add_error(
                    "Discord connector requires async execution. "
                    "Consider using the async version or running from a sync context."
                )
                return result
            except RuntimeError:
                # No running loop, we can create one
                return asyncio.run(self._async_sync(incremental))
        except Exception as e:
            result = SyncResult(success=False)
            result.add_error(f"Failed to sync Discord: {e}")
            result.complete()
            return result

    async def _async_sync(self, incremental: bool) -> SyncResult:
        """Async implementation of sync."""
        result = SyncResult(success=True)
        
        # Get last sync state if incremental
        last_sync_state = None
        if incremental:
            last_sync_state = self.get_last_sync_state()

        # Create Discord client
        client = self.discord.Client(intents=self.intents)
        
        # Store sync data
        sync_data = {
            "result": result,
            "last_sync_state": last_sync_state,
            "processed_messages": set(),
            "synced_channels": {},
        }

        @client.event
        async def on_ready():
            """Called when Discord client is ready."""
            self.logger.info(f"Connected to Discord as {client.user}")
            
            # Create main collection
            collection_id = self.create_collection(
                "Discord Servers",
                "Messages and threads from Discord"
            )
            
            # Process guilds
            for guild in client.guilds:
                if self.guild_ids and guild.id not in self.guild_ids:
                    continue
                    
                await self._sync_guild(
                    guild,
                    collection_id,
                    sync_data
                )
            
            # Close client
            await client.close()

        # Run client
        try:
            await client.start(self._bot_token)
        except Exception as e:
            result.add_error(f"Discord client error: {e}")
            result.success = False

        # Save sync state
        if result.success:
            new_state = {
                "last_sync": datetime.now().isoformat(),
                "processed_messages": list(sync_data["processed_messages"]),
                "synced_channels": sync_data["synced_channels"],
            }
            self.save_sync_state(new_state)

        result.complete()
        return result

    async def _sync_guild(
        self,
        guild: Any,
        parent_collection_id: str,
        sync_data: dict[str, Any]
    ):
        """Sync a Discord guild (server)."""
        result = sync_data["result"]
        
        try:
            # Create collection for guild
            guild_collection_id = self.create_collection(
                f"Server: {guild.name}",
                f"Discord server: {guild.name}"
            )
            
            # Sync channels
            for channel in guild.channels:
                # Skip voice channels unless include_voice_text is True
                if channel.type == self.discord.ChannelType.voice and not self.include_voice_text:
                    continue
                
                # Check if specific channels requested
                if self.channel_ids and channel.id not in self.channel_ids:
                    continue
                if self.channel_names and channel.name not in self.channel_names:
                    continue
                
                # Only sync text-based channels
                if hasattr(channel, 'history'):
                    await self._sync_channel(
                        channel,
                        guild_collection_id,
                        sync_data
                    )
                    
        except Exception as e:
            result.add_error(f"Failed to sync guild {guild.name}: {e}")

    async def _sync_channel(
        self,
        channel: Any,
        parent_collection_id: str,
        sync_data: dict[str, Any]
    ):
        """Sync a Discord channel."""
        result = sync_data["result"]
        last_sync_state = sync_data["last_sync_state"]
        processed_messages = sync_data["processed_messages"]
        
        try:
            # Create collection for channel
            channel_desc = channel.topic if hasattr(channel, 'topic') and channel.topic else f"Discord channel #{channel.name}"
            channel_collection_id = self.create_collection(
                f"#{channel.name}",
                channel_desc
            )
            
            sync_data["synced_channels"][str(channel.id)] = channel_collection_id
            
            # Calculate time range
            after = None
            if self.days_to_sync > 0:
                after = datetime.now(UTC) - timedelta(days=self.days_to_sync)
            
            if incremental and last_sync_state:
                # Use last sync time
                after = datetime.fromisoformat(last_sync_state["last_sync"])
                # Discord expects timezone-aware datetime
                if after.tzinfo is None:
                    after = after.replace(tzinfo=UTC)
            
            # Get messages
            message_count = 0
            async for message in channel.history(limit=None, after=after, oldest_first=True):
                # Filter by user if specified
                if self.user_ids and message.author.id not in self.user_ids:
                    continue
                
                # Skip bot messages unless specifically included
                if message.author.bot and not self.config.sync_config.get("include_bots", False):
                    continue
                
                # Process message
                frame = await self._map_message_to_frame(message, channel, channel_collection_id)
                if frame:
                    try:
                        message_id = f"{channel.id}:{message.id}"
                        
                        existing = self.dataset.search(
                            f"custom_metadata.x_discord_message_id:'{message_id}'",
                            limit=1
                        )
                        
                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1
                        
                        processed_messages.add(message_id)
                        message_count += 1
                        
                    except Exception as e:
                        result.frames_failed += 1
                        result.add_error(f"Failed to sync message: {e}")
            
            # Sync threads if enabled
            if self.include_threads and hasattr(channel, 'threads'):
                for thread in channel.threads:
                    await self._sync_thread(thread, channel_collection_id, sync_data)
            
            # Sync forum posts if enabled
            if self.include_forum_posts and channel.type == self.discord.ChannelType.forum:
                async for thread in channel.archived_threads(limit=100):
                    await self._sync_thread(thread, channel_collection_id, sync_data)
                    
            self.logger.info(f"Synced {message_count} messages from #{channel.name}")
                    
        except Exception as e:
            result.add_error(f"Failed to sync channel #{channel.name}: {e}")

    async def _sync_thread(
        self,
        thread: Any,
        parent_collection_id: str,
        sync_data: dict[str, Any]
    ):
        """Sync a Discord thread."""
        result = sync_data["result"]
        processed_messages = sync_data["processed_messages"]
        
        try:
            # Create collection for thread
            thread_collection_id = self.create_collection(
                f"Thread: {thread.name}",
                f"Discord thread in #{thread.parent.name}"
            )
            
            # Get messages
            async for message in thread.history(limit=None, oldest_first=True):
                frame = await self._map_message_to_frame(message, thread, thread_collection_id, is_thread=True)
                if frame:
                    try:
                        message_id = f"{thread.id}:{message.id}"
                        
                        existing = self.dataset.search(
                            f"custom_metadata.x_discord_message_id:'{message_id}'",
                            limit=1
                        )
                        
                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1
                        
                        processed_messages.add(message_id)
                        
                    except Exception as e:
                        result.add_warning(f"Failed to sync thread message: {e}")
                        
        except Exception as e:
            result.add_warning(f"Failed to sync thread {thread.name}: {e}")

    def map_to_frame(self, source_data: dict[str, Any]) -> FrameRecord | None:
        """Map Discord data to FrameRecord."""
        # This is a sync method, but Discord operations are async
        # Return None for the base implementation
        return None

    async def _map_message_to_frame(
        self,
        message: Any,
        channel: Any,
        collection_id: str,
        is_thread: bool = False
    ) -> FrameRecord | None:
        """Map Discord message to FrameRecord."""
        try:
            # Build author name
            author = message.author.display_name or message.author.name
            if message.author.discriminator != "0":
                author = f"{author}#{message.author.discriminator}"
            
            # Build title
            title = f"Message from {author}"
            if is_thread:
                title = f"Thread message from {author}"
            
            metadata = {
                "title": title,
                "record_type": RecordType.DOCUMENT,
                "source_type": "discord_message",
                "source_url": message.jump_url,
                "collection": collection_id,
                "collection_id": collection_id,
                "author": author,
                "created_at": message.created_at.isoformat(),
                "custom_metadata": {
                    "x_discord_message_id": f"{channel.id}:{message.id}",
                    "x_discord_channel_id": str(channel.id),
                    "x_discord_channel_name": channel.name,
                    "x_discord_author_id": str(message.author.id),
                    "x_discord_guild_id": str(channel.guild.id) if hasattr(channel, 'guild') else None,
                }
            }
            
            # Add edited timestamp if edited
            if message.edited_at:
                metadata["updated_at"] = message.edited_at.isoformat()
            
            # Build content
            content = f"**{author}** - {message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            content += message.content or ""
            
            # Add embeds
            if message.embeds:
                content += "\n\n**Embeds:**\n"
                for embed in message.embeds:
                    if embed.title:
                        content += f"\n### {embed.title}\n"
                    if embed.description:
                        content += f"{embed.description}\n"
                    if embed.url:
                        content += f"URL: {embed.url}\n"
                    if embed.fields:
                        for field in embed.fields:
                            content += f"\n**{field.name}**: {field.value}\n"
            
            # Add reactions
            if self.include_reactions and message.reactions:
                content += "\n\n**Reactions:**\n"
                for reaction in message.reactions:
                    emoji = str(reaction.emoji)
                    content += f"{emoji} ({reaction.count}) "
                content += "\n"
            
            # Add attachments
            if self.include_attachments and message.attachments:
                content += "\n\n**Attachments:**\n"
                for attachment in message.attachments:
                    content += f"- [{attachment.filename}]({attachment.url})"
                    if attachment.content_type:
                        content += f" ({attachment.content_type})"
                    content += "\n"
            
            # Add reply reference
            if message.reference and message.reference.message_id:
                metadata["custom_metadata"]["x_discord_reply_to"] = str(message.reference.message_id)
            
            frame = FrameRecord(
                text_content=content,
                metadata=metadata,
                context=message.content[:200] if message.content else "",
            )
            
            # Add relationships
            if message.reference and message.reference.message_id:
                frame.add_relationship(
                    "reply_to",
                    id=f"{message.reference.channel_id}:{message.reference.message_id}"
                )
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Failed to map message: {e}")
            return None