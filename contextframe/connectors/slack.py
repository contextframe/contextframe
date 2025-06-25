"""Slack connector for importing channel messages into ContextFrame."""

import json
from contextframe import FrameRecord
from contextframe.connectors.base import (
    AuthType,
    ConnectorConfig,
    SourceConnector,
    SyncResult,
)
from contextframe.schema import RecordType
from datetime import UTC, datetime, timezone
from typing import Any, Dict, List, Optional, Set


class SlackConnector(SourceConnector):
    """Connector for importing Slack workspace content."""

    def __init__(self, config: ConnectorConfig, dataset):
        """Initialize Slack connector.

        Args:
            config: Connector configuration with Slack-specific settings
            dataset: Target FrameDataset
        """
        super().__init__(config, dataset)

        # Configuration options
        self.channel_ids = config.sync_config.get("channel_ids", [])
        self.channel_names = config.sync_config.get("channel_names", [])
        self.include_private = config.sync_config.get("include_private", False)
        self.include_archived = config.sync_config.get("include_archived", False)
        self.include_threads = config.sync_config.get("include_threads", True)
        self.include_reactions = config.sync_config.get("include_reactions", True)
        self.days_to_sync = config.sync_config.get("days_to_sync", 30)  # Default 30 days
        self.user_ids = config.sync_config.get("user_ids", [])  # Filter by user
        
        # Set up Slack API client
        self._setup_client()

    def _setup_client(self):
        """Set up Slack API client."""
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
            
            self.SlackApiError = SlackApiError
        except ImportError:
            raise ImportError(
                "slack-sdk is required for Slack connector. "
                "Install with: pip install slack-sdk"
            )

        # Initialize client based on auth type
        if self.config.auth_type == AuthType.TOKEN:
            token = self.config.auth_config.get("token")
            if not token:
                raise ValueError("Slack bot token required for authentication")
            self.client = WebClient(token=token)
        elif self.config.auth_type == AuthType.OAUTH:
            # OAuth token from OAuth flow
            token = self.config.auth_config.get("access_token")
            if not token:
                raise ValueError("Slack OAuth access token required")
            self.client = WebClient(token=token)
        else:
            raise ValueError("Slack connector requires token or OAuth authentication")

        # Cache for user info
        self.user_cache: dict[str, Any] = {}

    def validate_connection(self) -> bool:
        """Validate Slack connection."""
        try:
            # Test authentication
            auth_test = self.client.auth_test()
            self.workspace_info = auth_test
            self.logger.info(
                f"Connected to Slack workspace: {auth_test['team']} as {auth_test['user']}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to validate Slack connection: {e}")
            return False

    def discover_content(self) -> dict[str, Any]:
        """Discover Slack workspace structure."""
        discovery = {
            "workspace": {
                "name": self.workspace_info.get("team", "Unknown"),
                "team_id": self.workspace_info.get("team_id"),
                "user": self.workspace_info.get("user"),
                "user_id": self.workspace_info.get("user_id"),
            },
            "channels": [],
            "users": [],
            "stats": {
                "total_channels": 0,
                "public_channels": 0,
                "private_channels": 0,
                "total_users": 0,
                "active_users": 0,
            }
        }

        try:
            # Get channels
            channels = []
            cursor = None
            
            while True:
                result = self.client.conversations_list(
                    exclude_archived=not self.include_archived,
                    types="public_channel,private_channel" if self.include_private else "public_channel",
                    cursor=cursor,
                    limit=1000
                )
                
                channels.extend(result["channels"])
                
                if not result.get("response_metadata", {}).get("next_cursor"):
                    break
                cursor = result["response_metadata"]["next_cursor"]

            # Process channels
            for channel in channels:
                channel_info = {
                    "id": channel["id"],
                    "name": channel["name"],
                    "is_private": channel.get("is_private", False),
                    "is_archived": channel.get("is_archived", False),
                    "topic": channel.get("topic", {}).get("value", ""),
                    "purpose": channel.get("purpose", {}).get("value", ""),
                    "num_members": channel.get("num_members", 0),
                }
                discovery["channels"].append(channel_info)
                
                discovery["stats"]["total_channels"] += 1
                if channel.get("is_private"):
                    discovery["stats"]["private_channels"] += 1
                else:
                    discovery["stats"]["public_channels"] += 1

            # Get users
            users = self.client.users_list()
            for user in users["members"]:
                if not user.get("deleted", False) and not user.get("is_bot", False):
                    user_info = {
                        "id": user["id"],
                        "name": user.get("real_name", user.get("name", "Unknown")),
                        "display_name": user.get("profile", {}).get("display_name", ""),
                        "is_active": not user.get("deleted", False),
                    }
                    discovery["users"].append(user_info)
                    discovery["stats"]["total_users"] += 1
                    if not user.get("deleted", False):
                        discovery["stats"]["active_users"] += 1

        except Exception as e:
            self.logger.error(f"Failed to discover Slack content: {e}")
            discovery["error"] = str(e)

        return discovery

    def sync(self, incremental: bool = True) -> SyncResult:
        """Sync Slack content to ContextFrame."""
        result = SyncResult(success=True)

        # Get last sync state if incremental
        last_sync_state = None
        if incremental:
            last_sync_state = self.get_last_sync_state()

        # Create main collection
        collection_id = self.create_collection(
            f"Slack: {self.workspace_info.get('team', 'Workspace')}",
            "Messages and threads from Slack workspace"
        )

        # Track processed items
        processed_messages: set[str] = set()
        synced_channels: dict[str, str] = {}

        # Get channels to sync
        channels_to_sync = self._get_channels_to_sync()

        # Sync each channel
        for channel in channels_to_sync:
            channel_collection_id = self._sync_channel(
                channel,
                collection_id,
                result,
                last_sync_state,
                processed_messages
            )
            if channel_collection_id:
                synced_channels[channel["id"]] = channel_collection_id

        # Save sync state
        if result.success:
            new_state = {
                "last_sync": datetime.now().isoformat(),
                "processed_messages": list(processed_messages),
                "synced_channels": synced_channels,
            }
            self.save_sync_state(new_state)

        result.complete()
        return result

    def _get_channels_to_sync(self) -> list[dict[str, Any]]:
        """Get list of channels to sync based on configuration."""
        channels = []
        
        # Get channels by ID
        for channel_id in self.channel_ids:
            try:
                info = self.client.conversations_info(channel=channel_id)
                channels.append(info["channel"])
            except Exception as e:
                self.logger.warning(f"Failed to get channel {channel_id}: {e}")

        # Get channels by name
        if self.channel_names:
            cursor = None
            while True:
                result = self.client.conversations_list(
                    exclude_archived=not self.include_archived,
                    types="public_channel,private_channel" if self.include_private else "public_channel",
                    cursor=cursor
                )
                
                for channel in result["channels"]:
                    if channel["name"] in self.channel_names:
                        channels.append(channel)
                
                if not result.get("response_metadata", {}).get("next_cursor"):
                    break
                cursor = result["response_metadata"]["next_cursor"]

        # If no specific channels requested, get all
        if not self.channel_ids and not self.channel_names:
            cursor = None
            while True:
                result = self.client.conversations_list(
                    exclude_archived=not self.include_archived,
                    types="public_channel,private_channel" if self.include_private else "public_channel",
                    cursor=cursor,
                    limit=100
                )
                
                channels.extend(result["channels"])
                
                if not result.get("response_metadata", {}).get("next_cursor"):
                    break
                cursor = result["response_metadata"]["next_cursor"]

        return channels

    def _sync_channel(
        self,
        channel: dict[str, Any],
        parent_collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_messages: set[str]
    ) -> str | None:
        """Sync a specific Slack channel."""
        try:
            # Create collection for channel
            channel_collection_id = self.create_collection(
                f"#{channel['name']}",
                channel.get("topic", {}).get("value", "") or 
                channel.get("purpose", {}).get("value", "") or
                f"Slack channel #{channel['name']}"
            )

            # Calculate time range
            oldest = None
            if self.days_to_sync > 0:
                oldest = int(
                    (datetime.now(UTC) - 
                     datetime.timedelta(days=self.days_to_sync)).timestamp()
                )
            
            if incremental and last_sync_state:
                # Use last sync time as oldest
                last_sync = datetime.fromisoformat(last_sync_state["last_sync"])
                oldest = int(last_sync.timestamp())

            # Get messages
            cursor = None
            while True:
                try:
                    result = self.client.conversations_history(
                        channel=channel["id"],
                        oldest=str(oldest) if oldest else None,
                        cursor=cursor,
                        limit=1000
                    )
                    
                    messages = result.get("messages", [])
                    
                    for message in messages:
                        # Filter by user if specified
                        if self.user_ids and message.get("user") not in self.user_ids:
                            continue

                        # Skip bot messages unless specifically included
                        if message.get("subtype") == "bot_message" and not self.config.sync_config.get("include_bots", False):
                            continue

                        # Process message
                        frame = self._map_message_to_frame(message, channel, channel_collection_id)
                        if frame:
                            try:
                                # Create unique ID for message
                                message_id = f"{channel['id']}:{message['ts']}"
                                
                                existing = self.dataset.search(
                                    f"custom_metadata.x_slack_message_id:'{message_id}'",
                                    limit=1
                                )

                                if existing:
                                    self.dataset.update(existing[0].metadata["uuid"], frame)
                                    result.frames_updated += 1
                                else:
                                    self.dataset.add(frame)
                                    result.frames_created += 1

                                processed_messages.add(message_id)

                                # Sync thread if it exists
                                if self.include_threads and message.get("thread_ts") == message.get("ts"):
                                    self._sync_thread(
                                        channel["id"],
                                        message["ts"],
                                        channel_collection_id,
                                        result,
                                        processed_messages
                                    )

                            except Exception as e:
                                result.frames_failed += 1
                                result.add_error(f"Failed to sync message: {e}")
                    
                    if not result.get("has_more"):
                        break
                    cursor = result.get("response_metadata", {}).get("next_cursor")
                    
                except self.SlackApiError as e:
                    if e.response["error"] == "not_in_channel":
                        result.add_warning(f"Bot not in channel #{channel['name']}")
                    else:
                        result.add_error(f"Failed to get messages from #{channel['name']}: {e}")
                    break

            return channel_collection_id

        except Exception as e:
            result.add_error(f"Failed to sync channel #{channel['name']}: {e}")
            return None

    def _sync_thread(
        self,
        channel_id: str,
        thread_ts: str,
        collection_id: str,
        result: SyncResult,
        processed_messages: set[str]
    ):
        """Sync thread replies."""
        try:
            cursor = None
            while True:
                thread_result = self.client.conversations_replies(
                    channel=channel_id,
                    ts=thread_ts,
                    cursor=cursor,
                    limit=1000
                )
                
                replies = thread_result.get("messages", [])[1:]  # Skip parent message
                
                for reply in replies:
                    frame = self._map_message_to_frame(reply, {"id": channel_id}, collection_id, is_thread_reply=True)
                    if frame:
                        try:
                            message_id = f"{channel_id}:{reply['ts']}"
                            
                            # Add thread relationship
                            frame.add_relationship("reply_to", id=f"{channel_id}:{thread_ts}")
                            
                            existing = self.dataset.search(
                                f"custom_metadata.x_slack_message_id:'{message_id}'",
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
                            result.add_warning(f"Failed to sync thread reply: {e}")
                
                if not thread_result.get("has_more"):
                    break
                cursor = thread_result.get("response_metadata", {}).get("next_cursor")

        except Exception as e:
            result.add_warning(f"Failed to sync thread {thread_ts}: {e}")

    def map_to_frame(self, source_data: dict[str, Any]) -> FrameRecord | None:
        """Map Slack data to FrameRecord."""
        return self._map_message_to_frame(source_data, {}, "")

    def _map_message_to_frame(
        self,
        message: dict[str, Any],
        channel: dict[str, Any],
        collection_id: str,
        is_thread_reply: bool = False
    ) -> FrameRecord | None:
        """Map Slack message to FrameRecord."""
        try:
            # Get user info
            user_info = self._get_user_info(message.get("user", ""))
            author = user_info.get("real_name", user_info.get("name", "Unknown"))
            
            # Create timestamp
            ts = float(message["ts"])
            created_at = datetime.fromtimestamp(ts, tz=UTC).isoformat()
            
            # Build title
            title = f"Message from {author}"
            if is_thread_reply:
                title = f"Reply from {author}"
            
            metadata = {
                "title": title,
                "record_type": RecordType.DOCUMENT,
                "source_type": "slack_message",
                "source_url": f"https://{self.workspace_info.get('team', 'slack')}.slack.com/archives/{channel.get('id', '')}/p{message['ts'].replace('.', '')}",
                "collection": collection_id,
                "collection_id": collection_id,
                "author": author,
                "created_at": created_at,
                "custom_metadata": {
                    "x_slack_message_id": f"{channel.get('id', '')}:{message['ts']}",
                    "x_slack_channel_id": channel.get("id", ""),
                    "x_slack_user_id": message.get("user", ""),
                    "x_slack_ts": message["ts"],
                }
            }

            # Build content
            content = f"**{author}** - {created_at}\n\n"
            content += message.get("text", "")
            
            # Add reactions if present
            if self.include_reactions and message.get("reactions"):
                content += "\n\n**Reactions:**\n"
                for reaction in message["reactions"]:
                    content += f":{reaction['name']}: ({reaction['count']}) "
                content += "\n"

            # Add attachments info
            if message.get("attachments"):
                content += "\n\n**Attachments:**\n"
                for attachment in message["attachments"]:
                    if attachment.get("title"):
                        content += f"- {attachment['title']}\n"
                    if attachment.get("text"):
                        content += f"  {attachment['text']}\n"

            # Add files info
            if message.get("files"):
                content += "\n\n**Files:**\n"
                for file in message["files"]:
                    content += f"- {file.get('name', 'Unnamed')} ({file.get('mimetype', 'unknown')})\n"

            return FrameRecord(
                text_content=content,
                metadata=metadata,
                context=message.get("text", "")[:200],  # First 200 chars as context
            )

        except Exception as e:
            self.logger.error(f"Failed to map message: {e}")
            return None

    def _get_user_info(self, user_id: str) -> dict[str, Any]:
        """Get user info with caching."""
        if not user_id:
            return {}
            
        if user_id in self.user_cache:
            return self.user_cache[user_id]
        
        try:
            result = self.client.users_info(user=user_id)
            user_info = result["user"]
            self.user_cache[user_id] = user_info
            return user_info
        except Exception as e:
            self.logger.warning(f"Failed to get user info for {user_id}: {e}")
            return {"name": user_id}