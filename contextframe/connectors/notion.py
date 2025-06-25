"""Notion connector for importing pages and databases into ContextFrame."""

import json
from contextframe import FrameRecord
from contextframe.connectors.base import (
    AuthType,
    ConnectorConfig,
    SourceConnector,
    SyncResult,
)
from contextframe.schema import RecordType
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


class NotionConnector(SourceConnector):
    """Connector for importing Notion workspace content."""

    def __init__(self, config: ConnectorConfig, dataset):
        """Initialize Notion connector.

        Args:
            config: Connector configuration with Notion-specific settings
            dataset: Target FrameDataset
        """
        super().__init__(config, dataset)

        # Configuration options
        self.workspace_ids = config.sync_config.get("workspace_ids", [])
        self.database_ids = config.sync_config.get("database_ids", [])
        self.page_ids = config.sync_config.get("page_ids", [])
        self.include_archived = config.sync_config.get("include_archived", False)
        self.sync_databases = config.sync_config.get("sync_databases", True)
        self.sync_pages = config.sync_config.get("sync_pages", True)
        self.include_comments = config.sync_config.get("include_comments", True)
        
        # Set up Notion API client
        self._setup_client()

    def _setup_client(self):
        """Set up Notion API client."""
        try:
            from notion_client import Client
        except ImportError:
            raise ImportError(
                "notion-client is required for Notion connector. "
                "Install with: pip install notion-client"
            )

        # Initialize client based on auth type
        if self.config.auth_type == AuthType.TOKEN:
            token = self.config.auth_config.get("token")
            if not token:
                raise ValueError("Notion integration token required for authentication")
            self.client = Client(auth=token)
        else:
            raise ValueError("Notion connector requires token authentication")

    def validate_connection(self) -> bool:
        """Validate Notion connection."""
        try:
            # Try to get user info
            users = self.client.users.list()
            self.logger.info(f"Connected to Notion workspace with {len(users['results'])} users")
            return True
        except Exception as e:
            self.logger.error(f"Failed to validate Notion connection: {e}")
            return False

    def discover_content(self) -> dict[str, Any]:
        """Discover Notion workspace structure."""
        discovery = {
            "workspace": {
                "users": [],
                "bot_info": {},
            },
            "databases": [],
            "pages": [],
            "stats": {
                "total_databases": 0,
                "total_pages": 0,
                "page_types": {},
            }
        }

        try:
            # Get bot info
            bot = self.client.users.me()
            discovery["workspace"]["bot_info"] = {
                "id": bot["id"],
                "name": bot.get("name", "Notion Integration"),
                "type": bot["type"],
            }

            # Get users
            users = self.client.users.list()
            for user in users["results"]:
                discovery["workspace"]["users"].append({
                    "id": user["id"],
                    "name": user.get("name", "Unknown"),
                    "type": user["type"],
                })

            # Search for all content
            cursor = None
            while True:
                results = self.client.search(
                    filter={"property": "object", "value": "page"},
                    start_cursor=cursor,
                    page_size=100
                )

                for item in results["results"]:
                    if item["object"] == "database":
                        discovery["databases"].append({
                            "id": item["id"],
                            "title": self._get_title(item),
                            "url": item["url"],
                            "archived": item.get("archived", False),
                        })
                        discovery["stats"]["total_databases"] += 1
                    else:  # page
                        page_type = "child_page" if item.get("parent", {}).get("type") == "page_id" else "root_page"
                        discovery["pages"].append({
                            "id": item["id"],
                            "title": self._get_title(item),
                            "url": item["url"],
                            "archived": item.get("archived", False),
                            "type": page_type,
                        })
                        discovery["stats"]["total_pages"] += 1
                        discovery["stats"]["page_types"][page_type] = \
                            discovery["stats"]["page_types"].get(page_type, 0) + 1

                if not results["has_more"]:
                    break
                cursor = results["next_cursor"]

        except Exception as e:
            self.logger.error(f"Failed to discover Notion content: {e}")
            discovery["error"] = str(e)

        return discovery

    def sync(self, incremental: bool = True) -> SyncResult:
        """Sync Notion content to ContextFrame."""
        result = SyncResult(success=True)

        # Get last sync state if incremental
        last_sync_state = None
        if incremental:
            last_sync_state = self.get_last_sync_state()

        # Create main collection
        collection_id = self.create_collection(
            "Notion Workspace",
            "Pages and databases from Notion"
        )

        # Track processed items
        processed_items: set[str] = set()

        # Sync databases
        if self.sync_databases:
            self._sync_databases(collection_id, result, last_sync_state, processed_items)

        # Sync pages
        if self.sync_pages:
            self._sync_pages(collection_id, result, last_sync_state, processed_items)

        # Save sync state
        if result.success:
            new_state = {
                "last_sync": datetime.now().isoformat(),
                "processed_items": list(processed_items),
            }
            self.save_sync_state(new_state)

        result.complete()
        return result

    def _sync_databases(
        self,
        parent_collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_items: set[str]
    ):
        """Sync Notion databases."""
        try:
            # Search for databases
            cursor = None
            while True:
                results = self.client.search(
                    filter={"property": "object", "value": "database"},
                    start_cursor=cursor,
                    page_size=100
                )

                for database in results["results"]:
                    if not self.include_archived and database.get("archived", False):
                        continue

                    # Check if specific databases requested
                    if self.database_ids and database["id"] not in self.database_ids:
                        continue

                    # Check if needs update
                    if incremental and last_sync_state:
                        last_sync = datetime.fromisoformat(last_sync_state["last_sync"])
                        last_edited = datetime.fromisoformat(
                            database["last_edited_time"].replace("Z", "+00:00")
                        )
                        if last_edited <= last_sync:
                            continue

                    # Create collection for database
                    db_title = self._get_title(database)
                    db_collection_id = self.create_collection(
                        f"Database: {db_title}",
                        f"Notion database: {db_title}"
                    )

                    # Create database frame
                    frame = self._map_database_to_frame(database, parent_collection_id)
                    if frame:
                        try:
                            existing = self.dataset.search(
                                f"source_url:'{database['url']}'",
                                limit=1
                            )

                            if existing:
                                self.dataset.update(existing[0].metadata["uuid"], frame)
                                result.frames_updated += 1
                            else:
                                self.dataset.add(frame)
                                result.frames_created += 1

                            processed_items.add(database["id"])

                            # Sync database entries
                            self._sync_database_entries(
                                database["id"],
                                db_collection_id,
                                result,
                                last_sync_state,
                                processed_items
                            )

                        except Exception as e:
                            result.frames_failed += 1
                            result.add_error(f"Failed to sync database {db_title}: {e}")

                if not results["has_more"]:
                    break
                cursor = results["next_cursor"]

        except Exception as e:
            result.add_error(f"Failed to sync databases: {e}")
            result.success = False

    def _sync_database_entries(
        self,
        database_id: str,
        collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_items: set[str]
    ):
        """Sync entries from a Notion database."""
        try:
            cursor = None
            while True:
                results = self.client.databases.query(
                    database_id=database_id,
                    start_cursor=cursor,
                    page_size=100
                )

                for entry in results["results"]:
                    if not self.include_archived and entry.get("archived", False):
                        continue

                    # Map and save entry
                    frame = self._map_page_to_frame(entry, collection_id)
                    if frame:
                        try:
                            existing = self.dataset.search(
                                f"source_url:'{entry['url']}'",
                                limit=1
                            )

                            if existing:
                                self.dataset.update(existing[0].metadata["uuid"], frame)
                                result.frames_updated += 1
                            else:
                                self.dataset.add(frame)
                                result.frames_created += 1

                            processed_items.add(entry["id"])

                        except Exception as e:
                            result.frames_failed += 1
                            result.add_error(f"Failed to sync database entry: {e}")

                if not results["has_more"]:
                    break
                cursor = results["next_cursor"]

        except Exception as e:
            result.add_warning(f"Failed to sync database entries for {database_id}: {e}")

    def _sync_pages(
        self,
        parent_collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        processed_items: set[str]
    ):
        """Sync Notion pages."""
        try:
            # Search for pages
            cursor = None
            while True:
                results = self.client.search(
                    filter={"property": "object", "value": "page"},
                    start_cursor=cursor,
                    page_size=100
                )

                for page in results["results"]:
                    # Skip databases (they're handled separately)
                    if page["object"] == "database":
                        continue

                    if not self.include_archived and page.get("archived", False):
                        continue

                    # Check if specific pages requested
                    if self.page_ids and page["id"] not in self.page_ids:
                        continue

                    # Check if needs update
                    if incremental and last_sync_state:
                        last_sync = datetime.fromisoformat(last_sync_state["last_sync"])
                        last_edited = datetime.fromisoformat(
                            page["last_edited_time"].replace("Z", "+00:00")
                        )
                        if last_edited <= last_sync:
                            continue

                    # Process page
                    frame = self._map_page_to_frame(page, parent_collection_id)
                    if frame:
                        try:
                            existing = self.dataset.search(
                                f"source_url:'{page['url']}'",
                                limit=1
                            )

                            if existing:
                                self.dataset.update(existing[0].metadata["uuid"], frame)
                                result.frames_updated += 1
                            else:
                                self.dataset.add(frame)
                                result.frames_created += 1

                            processed_items.add(page["id"])

                            # Sync comments if enabled
                            if self.include_comments:
                                self._sync_page_comments(page["id"], parent_collection_id, result)

                        except Exception as e:
                            result.frames_failed += 1
                            result.add_error(f"Failed to sync page {self._get_title(page)}: {e}")

                if not results["has_more"]:
                    break
                cursor = results["next_cursor"]

        except Exception as e:
            result.add_error(f"Failed to sync pages: {e}")
            result.success = False

    def _sync_page_comments(self, page_id: str, collection_id: str, result: SyncResult):
        """Sync comments for a page."""
        try:
            comments = self.client.comments.list(block_id=page_id)
            
            for comment in comments["results"]:
                frame = self._map_comment_to_frame(comment, page_id, collection_id)
                if frame:
                    try:
                        existing = self.dataset.search(
                            f"custom_metadata.x_notion_comment_id:'{comment['id']}'",
                            limit=1
                        )

                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1

                    except Exception as e:
                        result.add_warning(f"Failed to sync comment: {e}")

        except Exception as e:
            # Comments API might not be available for all integrations
            result.add_warning(f"Failed to sync comments for page {page_id}: {e}")

    def map_to_frame(self, source_data: dict[str, Any]) -> FrameRecord | None:
        """Map Notion data to FrameRecord."""
        object_type = source_data.get("object")
        
        if object_type == "database":
            return self._map_database_to_frame(source_data, "")
        elif object_type == "page":
            return self._map_page_to_frame(source_data, "")
        else:
            self.logger.warning(f"Unknown Notion object type: {object_type}")
            return None

    def _map_database_to_frame(
        self, database: dict[str, Any], collection_id: str
    ) -> FrameRecord | None:
        """Map Notion database to FrameRecord."""
        try:
            title = self._get_title(database)
            
            metadata = {
                "title": f"Database: {title}",
                "record_type": RecordType.COLLECTION_HEADER,
                "source_type": "notion_database",
                "source_url": database["url"],
                "collection": collection_id,
                "collection_id": collection_id,
                "created_at": database.get("created_time"),
                "updated_at": database.get("last_edited_time"),
                "custom_metadata": {
                    "x_notion_id": database["id"],
                    "x_notion_archived": database.get("archived", False),
                }
            }

            # Build content with database schema
            content = f"# {title}\n\n"
            content += "## Database Properties\n\n"
            
            if "properties" in database:
                for prop_name, prop_config in database["properties"].items():
                    content += f"- **{prop_name}** ({prop_config['type']})\n"

            return FrameRecord(
                text_content=content,
                metadata=metadata,
                context=f"Notion database: {title}",
            )

        except Exception as e:
            self.logger.error(f"Failed to map database: {e}")
            return None

    def _map_page_to_frame(
        self, page: dict[str, Any], collection_id: str
    ) -> FrameRecord | None:
        """Map Notion page to FrameRecord."""
        try:
            title = self._get_title(page)
            
            metadata = {
                "title": title,
                "record_type": RecordType.DOCUMENT,
                "source_type": "notion_page",
                "source_url": page["url"],
                "collection": collection_id,
                "collection_id": collection_id,
                "created_at": page.get("created_time"),
                "updated_at": page.get("last_edited_time"),
                "custom_metadata": {
                    "x_notion_id": page["id"],
                    "x_notion_archived": page.get("archived", False),
                    "x_notion_parent_type": page.get("parent", {}).get("type"),
                    "x_notion_parent_id": self._get_parent_id(page),
                }
            }

            # Get page content
            content = f"# {title}\n\n"
            
            # Get page blocks (content)
            try:
                blocks = self._get_page_blocks(page["id"])
                content += self._blocks_to_markdown(blocks)
            except Exception as e:
                self.logger.warning(f"Failed to get page content: {e}")
                content += f"_Content unavailable: {e}_\n"

            # Add properties if it's a database entry
            if "properties" in page:
                content += "\n## Properties\n\n"
                for prop_name, prop_value in page["properties"].items():
                    value = self._extract_property_value(prop_value)
                    if value:
                        content += f"**{prop_name}**: {value}\n"

            return FrameRecord(
                text_content=content,
                metadata=metadata,
                context=title,
            )

        except Exception as e:
            self.logger.error(f"Failed to map page: {e}")
            return None

    def _map_comment_to_frame(
        self, comment: dict[str, Any], page_id: str, collection_id: str
    ) -> FrameRecord | None:
        """Map Notion comment to FrameRecord."""
        try:
            metadata = {
                "title": "Comment on page",
                "record_type": RecordType.DOCUMENT,
                "source_type": "notion_comment",
                "collection": collection_id,
                "collection_id": collection_id,
                "created_at": comment.get("created_time"),
                "custom_metadata": {
                    "x_notion_comment_id": comment["id"],
                    "x_notion_page_id": page_id,
                }
            }

            # Extract comment text
            content = "## Comment\n\n"
            for text_block in comment.get("rich_text", []):
                content += text_block.get("plain_text", "")

            frame = FrameRecord(
                text_content=content,
                metadata=metadata,
            )

            # Add relationship to page
            frame.add_relationship("comment_on", id=page_id)

            return frame

        except Exception as e:
            self.logger.error(f"Failed to map comment: {e}")
            return None

    def _get_page_blocks(self, page_id: str) -> list[dict[str, Any]]:
        """Get all blocks from a page."""
        blocks = []
        cursor = None
        
        while True:
            results = self.client.blocks.children.list(
                block_id=page_id,
                start_cursor=cursor,
                page_size=100
            )
            
            blocks.extend(results["results"])
            
            if not results["has_more"]:
                break
            cursor = results["next_cursor"]
        
        return blocks

    def _blocks_to_markdown(self, blocks: list[dict[str, Any]]) -> str:
        """Convert Notion blocks to markdown."""
        markdown = ""
        
        for block in blocks:
            block_type = block["type"]
            
            if block_type == "paragraph":
                text = self._extract_rich_text(block[block_type].get("rich_text", []))
                markdown += f"{text}\n\n"
                
            elif block_type in ["heading_1", "heading_2", "heading_3"]:
                level = int(block_type[-1])
                text = self._extract_rich_text(block[block_type].get("rich_text", []))
                markdown += f"{'#' * level} {text}\n\n"
                
            elif block_type == "bulleted_list_item":
                text = self._extract_rich_text(block[block_type].get("rich_text", []))
                markdown += f"- {text}\n"
                
            elif block_type == "numbered_list_item":
                text = self._extract_rich_text(block[block_type].get("rich_text", []))
                markdown += f"1. {text}\n"
                
            elif block_type == "code":
                code = self._extract_rich_text(block[block_type].get("rich_text", []))
                language = block[block_type].get("language", "")
                markdown += f"```{language}\n{code}\n```\n\n"
                
            elif block_type == "quote":
                text = self._extract_rich_text(block[block_type].get("rich_text", []))
                markdown += f"> {text}\n\n"
                
            elif block_type == "divider":
                markdown += "---\n\n"
                
            # Handle nested blocks
            if block.get("has_children"):
                children = self._get_page_blocks(block["id"])
                markdown += self._blocks_to_markdown(children)
        
        return markdown

    def _extract_rich_text(self, rich_text: list[dict[str, Any]]) -> str:
        """Extract plain text from Notion rich text."""
        text = ""
        for segment in rich_text:
            text += segment.get("plain_text", "")
        return text

    def _extract_property_value(self, prop: dict[str, Any]) -> str:
        """Extract value from a Notion property."""
        prop_type = prop["type"]
        
        if prop_type == "title":
            return self._extract_rich_text(prop.get("title", []))
        elif prop_type == "rich_text":
            return self._extract_rich_text(prop.get("rich_text", []))
        elif prop_type == "number":
            return str(prop.get("number", ""))
        elif prop_type == "select":
            return prop.get("select", {}).get("name", "")
        elif prop_type == "multi_select":
            return ", ".join([s["name"] for s in prop.get("multi_select", [])])
        elif prop_type == "date":
            date = prop.get("date", {})
            if date:
                return f"{date.get('start', '')} - {date.get('end', '')}" if date.get('end') else date.get('start', '')
        elif prop_type == "checkbox":
            return "✓" if prop.get("checkbox") else "✗"
        elif prop_type == "url":
            return prop.get("url", "")
        elif prop_type == "email":
            return prop.get("email", "")
        elif prop_type == "phone_number":
            return prop.get("phone_number", "")
        else:
            return ""

    def _get_title(self, item: dict[str, Any]) -> str:
        """Extract title from a Notion page or database."""
        if "title" in item:
            # Database title
            return self._extract_rich_text(item["title"])
        elif "properties" in item:
            # Page title (usually in a property named "Name" or "Title")
            for prop_name in ["Title", "Name", "title", "name"]:
                if prop_name in item["properties"]:
                    prop = item["properties"][prop_name]
                    if prop["type"] == "title":
                        return self._extract_rich_text(prop.get("title", []))
        
        return "Untitled"

    def _get_parent_id(self, page: dict[str, Any]) -> str | None:
        """Get parent ID from a page."""
        parent = page.get("parent", {})
        parent_type = parent.get("type")
        
        if parent_type == "page_id":
            return parent.get("page_id")
        elif parent_type == "database_id":
            return parent.get("database_id")
        elif parent_type == "workspace":
            return "workspace"
        
        return None