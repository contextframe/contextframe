"""Linear connector for importing teams, projects, and issues into ContextFrame."""

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


class LinearConnector(SourceConnector):
    """Connector for importing Linear workspace data."""

    def __init__(self, config: ConnectorConfig, dataset):
        """Initialize Linear connector.

        Args:
            config: Connector configuration with Linear-specific settings
            dataset: Target FrameDataset
        """
        super().__init__(config, dataset)

        # Configuration options
        self.sync_teams = config.sync_config.get("sync_teams", True)
        self.sync_projects = config.sync_config.get("sync_projects", True)
        self.sync_issues = config.sync_config.get("sync_issues", True)
        self.team_ids = config.sync_config.get("team_ids", [])  # Empty = all teams
        self.project_ids = config.sync_config.get(
            "project_ids", []
        )  # Empty = all projects
        self.issue_states = config.sync_config.get(
            "issue_states", []
        )  # Empty = all states
        self.include_archived = config.sync_config.get("include_archived", False)
        self.include_comments = config.sync_config.get("include_comments", True)

        # Set up Linear API client
        self._setup_client()

    def _setup_client(self):
        """Set up Linear API client."""
        try:
            from linear import LinearClient
        except ImportError:
            raise ImportError(
                "linear-python is required for Linear connector. Install with: pip install linear-python"
            )

        # Initialize client based on auth type
        if self.config.auth_type == AuthType.API_KEY:
            api_key = self.config.auth_config.get("api_key")
            if not api_key:
                raise ValueError("Linear API key required for authentication")
            self.client = LinearClient(api_key)
        else:
            raise ValueError("Linear connector requires API key authentication")

    def validate_connection(self) -> bool:
        """Validate Linear connection."""
        try:
            # Try to get viewer info
            viewer = self.client.viewer
            self.logger.info(f"Connected to Linear as: {viewer.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to validate Linear connection: {e}")
            return False

    def discover_content(self) -> dict[str, Any]:
        """Discover Linear workspace structure."""
        discovery = {
            "workspace": {
                "viewer": {},
                "organization": {},
            },
            "teams": [],
            "projects": [],
            "issue_stats": {
                "total": 0,
                "by_state": {},
                "by_priority": {},
                "by_team": {},
            },
        }

        try:
            # Get viewer info
            viewer = self.client.viewer
            discovery["workspace"]["viewer"] = {
                "id": viewer.id,
                "name": viewer.name,
                "email": viewer.email,
            }

            # Get organization info
            org = self.client.organization
            discovery["workspace"]["organization"] = {
                "id": org.id,
                "name": org.name,
                "url_key": org.url_key,
            }

            # Discover teams
            teams = self.client.teams(include_archived=self.include_archived)
            for team in teams:
                if not self.team_ids or team.id in self.team_ids:
                    discovery["teams"].append(
                        {
                            "id": team.id,
                            "name": team.name,
                            "key": team.key,
                            "description": team.description,
                        }
                    )

            # Discover projects
            projects = self.client.projects(include_archived=self.include_archived)
            for project in projects:
                if not self.project_ids or project.id in self.project_ids:
                    discovery["projects"].append(
                        {
                            "id": project.id,
                            "name": project.name,
                            "description": project.description,
                            "state": project.state,
                            "team_ids": [team.id for team in project.teams],
                        }
                    )

            # Get issue statistics
            issues = self.client.issues(include_archived=self.include_archived)
            for issue in issues:
                discovery["issue_stats"]["total"] += 1

                # By state
                state_name = issue.state.name if issue.state else "No State"
                discovery["issue_stats"]["by_state"][state_name] = (
                    discovery["issue_stats"]["by_state"].get(state_name, 0) + 1
                )

                # By priority
                priority = issue.priority or 0
                discovery["issue_stats"]["by_priority"][priority] = (
                    discovery["issue_stats"]["by_priority"].get(priority, 0) + 1
                )

                # By team
                team_name = issue.team.name if issue.team else "No Team"
                discovery["issue_stats"]["by_team"][team_name] = (
                    discovery["issue_stats"]["by_team"].get(team_name, 0) + 1
                )

        except Exception as e:
            self.logger.error(f"Failed to discover Linear content: {e}")
            discovery["error"] = str(e)

        return discovery

    def sync(self, incremental: bool = True) -> SyncResult:
        """Sync Linear data to ContextFrame."""
        result = SyncResult(success=True)

        # Get last sync state if incremental
        last_sync_state = None
        if incremental:
            last_sync_state = self.get_last_sync_state()

        # Create main collection for Linear data
        main_collection_id = self.create_collection(
            "Linear Workspace", "Linear teams, projects, and issues"
        )

        # Track what we've synced
        synced_data = {
            "teams": {},
            "projects": {},
            "issues": set(),
        }

        # Sync teams
        if self.sync_teams:
            self._sync_teams(main_collection_id, result, last_sync_state, synced_data)

        # Sync projects
        if self.sync_projects:
            self._sync_projects(
                main_collection_id, result, last_sync_state, synced_data
            )

        # Sync issues
        if self.sync_issues:
            self._sync_issues(main_collection_id, result, last_sync_state, synced_data)

        # Save sync state
        if result.success:
            new_state = {
                "last_sync": datetime.now().isoformat(),
                "synced_teams": list(synced_data["teams"].keys()),
                "synced_projects": list(synced_data["projects"].keys()),
                "synced_issues": len(synced_data["issues"]),
            }
            self.save_sync_state(new_state)

        result.complete()
        return result

    def _sync_teams(
        self,
        parent_collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        synced_data: dict[str, Any],
    ):
        """Sync Linear teams."""
        try:
            teams = self.client.teams(include_archived=self.include_archived)

            for team in teams:
                if self.team_ids and team.id not in self.team_ids:
                    continue

                # Check if needs update
                if incremental and last_sync_state:
                    if team.updated_at <= datetime.fromisoformat(
                        last_sync_state["last_sync"]
                    ):
                        continue

                # Create team collection
                team_collection_id = self.create_collection(
                    f"Team: {team.name}", team.description or f"Linear team {team.key}"
                )

                # Create team frame
                frame = self._map_team_to_frame(
                    team, parent_collection_id, team_collection_id
                )
                if frame:
                    try:
                        existing = self.dataset.search(
                            f"source_url:'https://linear.app/team/{team.id}'", limit=1
                        )

                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1

                        synced_data["teams"][team.id] = team_collection_id

                    except Exception as e:
                        result.frames_failed += 1
                        result.add_error(f"Failed to sync team {team.name}: {e}")

        except Exception as e:
            result.add_error(f"Failed to sync teams: {e}")
            result.success = False

    def _sync_projects(
        self,
        parent_collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        synced_data: dict[str, Any],
    ):
        """Sync Linear projects."""
        try:
            projects = self.client.projects(include_archived=self.include_archived)

            for project in projects:
                if self.project_ids and project.id not in self.project_ids:
                    continue

                # Check if needs update
                if incremental and last_sync_state:
                    if project.updated_at <= datetime.fromisoformat(
                        last_sync_state["last_sync"]
                    ):
                        continue

                # Create project collection
                project_collection_id = self.create_collection(
                    f"Project: {project.name}", project.description or "Linear project"
                )

                # Create project frame
                frame = self._map_project_to_frame(
                    project, parent_collection_id, project_collection_id
                )
                if frame:
                    # Add team relationships
                    for team in project.teams:
                        if team.id in synced_data["teams"]:
                            frame.add_relationship(
                                "member_of", id=synced_data["teams"][team.id]
                            )

                    try:
                        existing = self.dataset.search(
                            f"source_url:'https://linear.app/project/{project.id}'",
                            limit=1,
                        )

                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1

                        synced_data["projects"][project.id] = project_collection_id

                    except Exception as e:
                        result.frames_failed += 1
                        result.add_error(f"Failed to sync project {project.name}: {e}")

        except Exception as e:
            result.add_error(f"Failed to sync projects: {e}")
            result.success = False

    def _sync_issues(
        self,
        parent_collection_id: str,
        result: SyncResult,
        last_sync_state: dict[str, Any] | None,
        synced_data: dict[str, Any],
    ):
        """Sync Linear issues."""
        try:
            # Build filter for issues
            filters = {}
            if self.team_ids:
                filters["team"] = {"id": {"in": self.team_ids}}
            if self.project_ids:
                filters["project"] = {"id": {"in": self.project_ids}}
            if self.issue_states:
                filters["state"] = {"name": {"in": self.issue_states}}

            issues = self.client.issues(
                filter=filters if filters else None,
                include_archived=self.include_archived,
            )

            for issue in issues:
                # Check if needs update
                if incremental and last_sync_state:
                    if issue.updated_at <= datetime.fromisoformat(
                        last_sync_state["last_sync"]
                    ):
                        continue

                # Determine collection
                collection_id = parent_collection_id
                if issue.project and issue.project.id in synced_data["projects"]:
                    collection_id = synced_data["projects"][issue.project.id]
                elif issue.team and issue.team.id in synced_data["teams"]:
                    collection_id = synced_data["teams"][issue.team.id]

                # Create issue frame
                frame = self._map_issue_to_frame(issue, collection_id)
                if frame:
                    # Add relationships
                    if issue.parent:
                        frame.add_relationship("child_of", id=issue.parent.id)
                    if issue.related_issues:
                        for related in issue.related_issues:
                            frame.add_relationship("related", id=related.id)

                    try:
                        existing = self.dataset.search(
                            f"source_url:'https://linear.app/issue/{issue.identifier}'",
                            limit=1,
                        )

                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1

                        synced_data["issues"].add(issue.id)

                        # Sync comments if enabled
                        if self.include_comments:
                            self._sync_issue_comments(issue, collection_id, result)

                    except Exception as e:
                        result.frames_failed += 1
                        result.add_error(
                            f"Failed to sync issue {issue.identifier}: {e}"
                        )

        except Exception as e:
            result.add_error(f"Failed to sync issues: {e}")
            result.success = False

    def _sync_issue_comments(self, issue: Any, collection_id: str, result: SyncResult):
        """Sync comments for an issue."""
        try:
            comments = issue.comments
            for comment in comments:
                frame = self._map_comment_to_frame(comment, issue, collection_id)
                if frame:
                    try:
                        existing = self.dataset.search(
                            f"source_url:'https://linear.app/comment/{comment.id}'",
                            limit=1,
                        )

                        if existing:
                            self.dataset.update(existing[0].metadata["uuid"], frame)
                            result.frames_updated += 1
                        else:
                            self.dataset.add(frame)
                            result.frames_created += 1

                    except Exception as e:
                        # Don't fail the whole sync for comment errors
                        result.add_warning(
                            f"Failed to sync comment on {issue.identifier}: {e}"
                        )

        except Exception as e:
            result.add_warning(f"Failed to sync comments for {issue.identifier}: {e}")

    def map_to_frame(self, source_data: dict[str, Any]) -> FrameRecord | None:
        """Generic mapping - delegates to specific mappers."""
        data_type = source_data.get("_type")

        if data_type == "team":
            return self._map_team_to_frame(source_data, "", "")
        elif data_type == "project":
            return self._map_project_to_frame(source_data, "", "")
        elif data_type == "issue":
            return self._map_issue_to_frame(source_data, "")
        elif data_type == "comment":
            return self._map_comment_to_frame(source_data, None, "")
        else:
            self.logger.warning(f"Unknown Linear data type: {data_type}")
            return None

    def _map_team_to_frame(
        self, team: Any, parent_collection_id: str, team_collection_id: str
    ) -> FrameRecord | None:
        """Map Linear team to FrameRecord."""
        try:
            metadata = {
                "title": f"Team: {team.name}",
                "record_type": RecordType.COLLECTION_HEADER,
                "source_type": "linear_team",
                "source_url": f"https://linear.app/team/{team.id}",
                "collection": parent_collection_id,
                "collection_id": parent_collection_id,
                "custom_metadata": {
                    "x_linear_id": team.id,
                    "x_linear_key": team.key,
                    "x_team_collection": team_collection_id,
                },
            }

            content = f"# {team.name}\n\n"
            content += f"**Key:** {team.key}\n\n"
            if team.description:
                content += f"## Description\n\n{team.description}\n\n"

            return FrameRecord(
                text_content=content,
                metadata=metadata,
                context=team.description or f"Linear team {team.key}",
            )

        except Exception as e:
            self.logger.error(f"Failed to map team {team.name}: {e}")
            return None

    def _map_project_to_frame(
        self, project: Any, parent_collection_id: str, project_collection_id: str
    ) -> FrameRecord | None:
        """Map Linear project to FrameRecord."""
        try:
            metadata = {
                "title": f"Project: {project.name}",
                "record_type": RecordType.COLLECTION_HEADER,
                "source_type": "linear_project",
                "source_url": f"https://linear.app/project/{project.id}",
                "collection": parent_collection_id,
                "collection_id": parent_collection_id,
                "status": project.state,
                "custom_metadata": {
                    "x_linear_id": project.id,
                    "x_project_collection": project_collection_id,
                    "x_project_state": project.state,
                },
            }

            content = f"# {project.name}\n\n"
            content += f"**State:** {project.state}\n\n"
            if project.description:
                content += f"## Description\n\n{project.description}\n\n"
            if project.start_date:
                content += f"**Start Date:** {project.start_date}\n"
            if project.target_date:
                content += f"**Target Date:** {project.target_date}\n"

            return FrameRecord(
                text_content=content,
                metadata=metadata,
                context=project.description or "Linear project",
            )

        except Exception as e:
            self.logger.error(f"Failed to map project {project.name}: {e}")
            return None

    def _map_issue_to_frame(self, issue: Any, collection_id: str) -> FrameRecord | None:
        """Map Linear issue to FrameRecord."""
        try:
            # Build metadata
            metadata = {
                "title": f"{issue.identifier}: {issue.title}",
                "record_type": RecordType.DOCUMENT,
                "source_type": "linear_issue",
                "source_url": f"https://linear.app/issue/{issue.identifier}",
                "collection": collection_id,
                "collection_id": collection_id,
                "status": issue.state.name if issue.state else "Unknown",
                "created_at": issue.created_at.isoformat()
                if issue.created_at
                else None,
                "updated_at": issue.updated_at.isoformat()
                if issue.updated_at
                else None,
                "custom_metadata": {
                    "x_linear_id": issue.id,
                    "x_linear_identifier": issue.identifier,
                    "x_linear_priority": str(issue.priority or 0),
                },
            }

            # Add assignee if present
            if issue.assignee:
                metadata["author"] = issue.assignee.name
                metadata["custom_metadata"]["x_linear_assignee_id"] = issue.assignee.id

            # Add labels as tags
            if issue.labels:
                metadata["tags"] = [label.name for label in issue.labels]

            # Build content
            content = f"# {issue.identifier}: {issue.title}\n\n"
            content += f"**State:** {issue.state.name if issue.state else 'Unknown'}\n"
            content += f"**Priority:** {self._priority_name(issue.priority)}\n"

            if issue.assignee:
                content += f"**Assignee:** {issue.assignee.name}\n"
            if issue.team:
                content += f"**Team:** {issue.team.name}\n"
            if issue.project:
                content += f"**Project:** {issue.project.name}\n"

            content += "\n"

            if issue.description:
                content += f"## Description\n\n{issue.description}\n\n"

            # Create frame
            return FrameRecord(
                text_content=content,
                metadata=metadata,
                context=issue.description or issue.title,
            )

        except Exception as e:
            self.logger.error(f"Failed to map issue {issue.identifier}: {e}")
            return None

    def _map_comment_to_frame(
        self, comment: Any, issue: Any, collection_id: str
    ) -> FrameRecord | None:
        """Map Linear comment to FrameRecord."""
        try:
            metadata = {
                "title": f"Comment on {issue.identifier}",
                "record_type": RecordType.DOCUMENT,
                "source_type": "linear_comment",
                "source_url": f"https://linear.app/comment/{comment.id}",
                "collection": collection_id,
                "collection_id": collection_id,
                "author": comment.user.name if comment.user else "Unknown",
                "created_at": comment.created_at.isoformat()
                if comment.created_at
                else None,
                "custom_metadata": {
                    "x_linear_id": comment.id,
                    "x_linear_issue_id": issue.id,
                    "x_linear_issue_identifier": issue.identifier,
                },
            }

            content = f"# Comment on {issue.identifier}\n\n"
            content += f"**By:** {comment.user.name if comment.user else 'Unknown'}\n"
            content += f"**Date:** {comment.created_at}\n\n"
            content += comment.body or ""

            frame = FrameRecord(
                text_content=content,
                metadata=metadata,
            )

            # Add relationship to issue
            frame.add_relationship("comment_on", id=issue.id)

            return frame

        except Exception as e:
            self.logger.error(f"Failed to map comment: {e}")
            return None

    def _priority_name(self, priority: int | None) -> str:
        """Convert Linear priority number to name."""
        if priority is None:
            return "None"
        priority_map = {
            0: "None",
            1: "Urgent",
            2: "High",
            3: "Normal",
            4: "Low",
        }
        return priority_map.get(priority, f"Priority {priority}")
