"""Template for business and organizational documents."""

import re
from ..frame import FrameDataset
from .base import (
    CollectionDefinition,
    ContextTemplate,
    EnrichmentSuggestion,
    FileMapping,
)
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union


class BusinessTemplate(ContextTemplate):
    """Template for business documents and organizational content.

    Handles:
    - Meeting notes and minutes
    - Decision documents and proposals
    - Reports and analyses
    - Project documentation
    - Stakeholder communications

    Automatically:
    - Groups by project/initiative
    - Links decisions to related documents
    - Tracks document ownership
    - Suggests business-focused enrichments
    """

    # Document patterns
    MEETING_PATTERNS = [
        "*meeting*",
        "*minutes*",
        "*standup*",
        "*retro*",
        "*retrospective*",
    ]
    DECISION_PATTERNS = ["*decision*", "*proposal*", "*rfc*", "*adr*", "*design*"]
    REPORT_PATTERNS = ["*report*", "*analysis*", "*summary*", "*review*"]
    PROJECT_PATTERNS = ["*project*", "*plan*", "*roadmap*", "*strategy*"]

    # Common business directories
    MEETINGS_DIRS = {"meetings", "notes", "minutes"}
    DECISIONS_DIRS = {"decisions", "proposals", "rfcs", "adrs"}
    REPORTS_DIRS = {"reports", "analyses", "reviews"}
    PROJECTS_DIRS = {"projects", "initiatives", "programs"}

    # File extensions
    DOC_EXTENSIONS = {".md", ".docx", ".doc", ".pdf", ".txt", ".rtf"}
    SPREADSHEET_EXTENSIONS = {".xlsx", ".xls", ".csv", ".ods"}
    PRESENTATION_EXTENSIONS = {".pptx", ".ppt", ".key", ".odp"}

    def __init__(self):
        """Initialize the business template."""
        super().__init__(
            name="business",
            description="Template for business documents, meeting notes, and organizational content",
        )

    def scan(self, source_path: str | Path) -> list[FileMapping]:
        """Scan business directory and map documents."""
        source_path = self.validate_source(source_path)
        mappings = []
        seen_paths = set()

        # Scan structured directories
        self._scan_meetings_directory(source_path, mappings, seen_paths)
        self._scan_decisions_directory(source_path, mappings, seen_paths)
        self._scan_reports_directory(source_path, mappings, seen_paths)
        self._scan_projects_directory(source_path, mappings, seen_paths)

        # Scan root for additional business documents
        for file_path in source_path.iterdir():
            if file_path.is_file() and file_path not in seen_paths:
                if file_path.suffix in self.DOC_EXTENSIONS:
                    mapping = self._categorize_document(file_path)
                    if mapping:
                        mappings.append(mapping)
                        seen_paths.add(file_path)
                elif file_path.suffix in self.SPREADSHEET_EXTENSIONS:
                    mappings.append(self._create_spreadsheet_mapping(file_path))
                    seen_paths.add(file_path)

        return mappings

    def _scan_meetings_directory(
        self, base_path: Path, mappings: list[FileMapping], seen_paths: set
    ):
        """Scan for meeting documents."""
        for dir_name in self.MEETINGS_DIRS:
            meetings_dir = base_path / dir_name
            if meetings_dir.exists() and meetings_dir.is_dir():
                for file_path in meetings_dir.rglob("*"):
                    if file_path.is_file() and file_path not in seen_paths:
                        if file_path.suffix in self.DOC_EXTENSIONS:
                            mapping = self._create_meeting_mapping(file_path)

                            # Try to extract date from path or filename
                            date_match = re.search(
                                r'(\d{4})[-_/](\d{1,2})[-_/](\d{1,2})', str(file_path)
                            )
                            if date_match:
                                year, month, day = date_match.groups()
                                mapping.custom_metadata["meeting_date"] = (
                                    f"{year}-{month:0>2}-{day:0>2}"
                                )
                                mapping.tags.append(f"year:{year}")

                            # Group by subdirectory (e.g., team meetings)
                            rel_path = file_path.relative_to(meetings_dir)
                            if len(rel_path.parts) > 1:
                                team = rel_path.parts[0]
                                mapping.collection = f"meetings/{team}"
                                mapping.custom_metadata["team"] = team
                            else:
                                mapping.collection = "meetings"

                            mappings.append(mapping)
                            seen_paths.add(file_path)

    def _scan_decisions_directory(
        self, base_path: Path, mappings: list[FileMapping], seen_paths: set
    ):
        """Scan for decision documents."""
        for dir_name in self.DECISIONS_DIRS:
            decisions_dir = base_path / dir_name
            if decisions_dir.exists() and decisions_dir.is_dir():
                for file_path in decisions_dir.rglob("*"):
                    if file_path.is_file() and file_path not in seen_paths:
                        if file_path.suffix in self.DOC_EXTENSIONS:
                            mapping = self._create_decision_mapping(file_path)

                            # Extract decision number if present (e.g., ADR-001)
                            num_match = re.search(r'(\d{3,4})', file_path.stem)
                            if num_match:
                                mapping.custom_metadata["decision_number"] = (
                                    num_match.group(1)
                                )

                            mapping.collection = "decisions"
                            mappings.append(mapping)
                            seen_paths.add(file_path)

    def _scan_reports_directory(
        self, base_path: Path, mappings: list[FileMapping], seen_paths: set
    ):
        """Scan for reports and analyses."""
        for dir_name in self.REPORTS_DIRS:
            reports_dir = base_path / dir_name
            if reports_dir.exists() and reports_dir.is_dir():
                for file_path in reports_dir.rglob("*"):
                    if file_path.is_file() and file_path not in seen_paths:
                        if file_path.suffix in self.DOC_EXTENSIONS:
                            mapping = self._create_report_mapping(file_path)

                            # Categorize by report type from subdirectory
                            rel_path = file_path.relative_to(reports_dir)
                            if len(rel_path.parts) > 1:
                                report_type = rel_path.parts[0]
                                mapping.collection = f"reports/{report_type}"
                                mapping.custom_metadata["report_type"] = report_type
                            else:
                                mapping.collection = "reports"

                            mappings.append(mapping)
                            seen_paths.add(file_path)
                        elif file_path.suffix in self.SPREADSHEET_EXTENSIONS:
                            mapping = self._create_spreadsheet_mapping(file_path)
                            mapping.collection = "reports"
                            mapping.tags.append("data-analysis")
                            mappings.append(mapping)
                            seen_paths.add(file_path)

    def _scan_projects_directory(
        self, base_path: Path, mappings: list[FileMapping], seen_paths: set
    ):
        """Scan for project documentation."""
        for dir_name in self.PROJECTS_DIRS:
            projects_dir = base_path / dir_name
            if projects_dir.exists() and projects_dir.is_dir():
                # Each subdirectory is typically a project
                for project_dir in projects_dir.iterdir():
                    if project_dir.is_dir():
                        project_name = project_dir.name

                        for file_path in project_dir.rglob("*"):
                            if file_path.is_file() and file_path not in seen_paths:
                                if file_path.suffix in self.DOC_EXTENSIONS:
                                    mapping = self._categorize_project_document(
                                        file_path, project_name
                                    )
                                    mapping.collection = f"projects/{project_name}"
                                    mappings.append(mapping)
                                    seen_paths.add(file_path)

    def _categorize_document(self, file_path: Path) -> FileMapping:
        """Categorize a business document by its name."""
        name_lower = file_path.stem.lower()

        # Check meeting patterns
        if any(
            pattern.replace("*", "") in name_lower for pattern in self.MEETING_PATTERNS
        ):
            return self._create_meeting_mapping(file_path)

        # Check decision patterns
        if any(
            pattern.replace("*", "") in name_lower for pattern in self.DECISION_PATTERNS
        ):
            return self._create_decision_mapping(file_path)

        # Check report patterns
        if any(
            pattern.replace("*", "") in name_lower for pattern in self.REPORT_PATTERNS
        ):
            return self._create_report_mapping(file_path)

        # Check project patterns
        if any(
            pattern.replace("*", "") in name_lower for pattern in self.PROJECT_PATTERNS
        ):
            return self._create_project_mapping(file_path, "general")

        # Default business document
        return FileMapping(
            path=file_path,
            title=f"Document - {file_path.stem}",
            tags=["business", "document", file_path.suffix[1:]],
            custom_metadata={"document_type": "general"},
        )

    def _create_meeting_mapping(self, file_path: Path) -> FileMapping:
        """Create mapping for a meeting document."""
        meeting_type = "general"
        name_lower = file_path.stem.lower()

        if "standup" in name_lower or "daily" in name_lower:
            meeting_type = "standup"
        elif "retro" in name_lower or "retrospective" in name_lower:
            meeting_type = "retrospective"
        elif "planning" in name_lower:
            meeting_type = "planning"
        elif "review" in name_lower:
            meeting_type = "review"
        elif "1on1" in name_lower or "1-on-1" in name_lower:
            meeting_type = "one-on-one"

        return FileMapping(
            path=file_path,
            title=f"Meeting - {file_path.stem}",
            tags=["meeting", meeting_type, "discussion"],
            custom_metadata={"meeting_type": meeting_type, "document_type": "meeting"},
        )

    def _create_decision_mapping(self, file_path: Path) -> FileMapping:
        """Create mapping for a decision document."""
        decision_type = "general"
        name_lower = file_path.stem.lower()

        if "adr" in name_lower:
            decision_type = "adr"
        elif "rfc" in name_lower:
            decision_type = "rfc"
        elif "proposal" in name_lower:
            decision_type = "proposal"
        elif "design" in name_lower:
            decision_type = "design"

        return FileMapping(
            path=file_path,
            title=f"Decision - {file_path.stem}",
            tags=["decision", decision_type, "strategic"],
            custom_metadata={
                "decision_type": decision_type,
                "document_type": "decision",
                "status": "draft",  # Would be updated during enrichment
            },
        )

    def _create_report_mapping(self, file_path: Path) -> FileMapping:
        """Create mapping for a report."""
        report_type = "general"
        name_lower = file_path.stem.lower()

        if "quarterly" in name_lower or "q1" in name_lower or "q2" in name_lower:
            report_type = "quarterly"
        elif "annual" in name_lower or "yearly" in name_lower:
            report_type = "annual"
        elif "monthly" in name_lower:
            report_type = "monthly"
        elif "analysis" in name_lower:
            report_type = "analysis"
        elif "summary" in name_lower:
            report_type = "summary"

        return FileMapping(
            path=file_path,
            title=f"Report - {file_path.stem}",
            tags=["report", report_type, "analysis"],
            custom_metadata={"report_type": report_type, "document_type": "report"},
        )

    def _create_project_mapping(
        self, file_path: Path, project_name: str
    ) -> FileMapping:
        """Create mapping for a project document."""
        return FileMapping(
            path=file_path,
            title=f"Project - {file_path.stem}",
            tags=["project", project_name.lower(), "planning"],
            custom_metadata={"project_name": project_name, "document_type": "project"},
        )

    def _categorize_project_document(
        self, file_path: Path, project_name: str
    ) -> FileMapping:
        """Categorize a document within a project."""
        mapping = self._categorize_document(file_path)
        mapping.tags.append(project_name.lower())
        mapping.custom_metadata["project_name"] = project_name
        return mapping

    def _create_spreadsheet_mapping(self, file_path: Path) -> FileMapping:
        """Create mapping for spreadsheet files."""
        name_lower = file_path.stem.lower()
        sheet_type = "data"

        if "budget" in name_lower:
            sheet_type = "budget"
        elif "forecast" in name_lower:
            sheet_type = "forecast"
        elif "metrics" in name_lower or "kpi" in name_lower:
            sheet_type = "metrics"
        elif "tracker" in name_lower or "tracking" in name_lower:
            sheet_type = "tracker"

        return FileMapping(
            path=file_path,
            title=f"Spreadsheet - {file_path.stem}",
            tags=["spreadsheet", sheet_type, "data"],
            custom_metadata={
                "spreadsheet_type": sheet_type,
                "format": file_path.suffix[1:],
            },
        )

    def define_collections(
        self, file_mappings: list[FileMapping]
    ) -> list[CollectionDefinition]:
        """Define collections for business documents."""
        collections = []
        seen_collections = set()

        # Core business collections
        collection_defs = [
            (
                "meetings",
                "Meeting Notes",
                "Team meetings and discussions",
                ["meetings", "collaboration"],
            ),
            (
                "decisions",
                "Decisions & Proposals",
                "Strategic decisions and proposals",
                ["decisions", "strategy"],
            ),
            (
                "reports",
                "Reports & Analyses",
                "Business reports and data analysis",
                ["reports", "insights"],
            ),
            (
                "projects",
                "Project Documentation",
                "Project plans and documentation",
                ["projects", "execution"],
            ),
        ]

        position = 0
        for name, title, desc, tags in collection_defs:
            if any(
                m.collection and m.collection.startswith(name) for m in file_mappings
            ):
                collections.append(
                    CollectionDefinition(
                        name=name,
                        title=title,
                        description=desc,
                        tags=tags,
                        position=position,
                    )
                )
                seen_collections.add(name)
                position += 10

        # Add sub-collections
        sub_collections = set()
        for mapping in file_mappings:
            if mapping.collection and "/" in mapping.collection:
                parts = mapping.collection.split("/")
                if len(parts) == 2:
                    parent, child = parts
                    if parent in seen_collections:
                        sub_collections.add((parent, child))

        for parent, child in sorted(sub_collections):
            coll_name = f"{parent}/{child}"
            collections.append(
                CollectionDefinition(
                    name=coll_name,
                    title=f"{child.replace('-', ' ').title()}",
                    description=f"Documents for {child}",
                    tags=[parent, child.lower()],
                    parent=parent,
                    position=position,
                )
            )
            position += 1

        return collections

    def discover_relationships(
        self, file_mappings: list[FileMapping], dataset: FrameDataset
    ) -> list[dict[str, Any]]:
        """Discover relationships between business documents."""
        relationships = []

        # Group documents by project
        project_docs = {}
        for mapping in file_mappings:
            project = mapping.custom_metadata.get("project_name")
            if project:
                if project not in project_docs:
                    project_docs[project] = []
                project_docs[project].append(mapping)

        # Link project documents
        for project, docs in project_docs.items():
            # Find the main project doc
            main_doc = None
            for doc in docs:
                if "plan" in doc.title.lower() or "overview" in doc.title.lower():
                    main_doc = doc
                    break

            if main_doc:
                for doc in docs:
                    if doc != main_doc:
                        relationships.append(
                            {
                                "source": str(main_doc.path),
                                "target": str(doc.path),
                                "type": "contains",
                                "description": f"Project document for {project}",
                            }
                        )

        # Link decisions to related documents
        decisions = [m for m in file_mappings if "decision" in m.tags]
        meetings = [m for m in file_mappings if "meeting" in m.tags]

        # Simple date-based matching for decisions and meetings
        for decision in decisions:
            decision_date = decision.custom_metadata.get("decision_date")
            if decision_date:
                for meeting in meetings:
                    meeting_date = meeting.custom_metadata.get("meeting_date")
                    if (
                        meeting_date
                        and abs(
                            (
                                datetime.fromisoformat(decision_date)
                                - datetime.fromisoformat(meeting_date)
                            ).days
                        )
                        <= 7
                    ):
                        relationships.append(
                            {
                                "source": str(decision.path),
                                "target": str(meeting.path),
                                "type": "discussed_in",
                                "description": "Decision discussed in meeting",
                            }
                        )

        return relationships

    def suggest_enrichments(
        self, file_mappings: list[FileMapping]
    ) -> list[EnrichmentSuggestion]:
        """Suggest business-specific enrichments."""
        suggestions = []

        # Meeting note enrichments
        suggestions.append(
            EnrichmentSuggestion(
                file_pattern="**/meeting*.md",
                enhancement_config={
                    "enhancements": {
                        "context": "business_context",
                        "custom_metadata": "meeting_metadata",
                    }
                },
                priority=10,
            )
        )

        # Decision document enrichments
        suggestions.append(
            EnrichmentSuggestion(
                file_pattern="**/decision*.md",
                enhancement_config={
                    "enhancements": {
                        "context": "Summarize the decision, its rationale, and impact",
                        "tags": "Extract: stakeholders, decision-type, impact-area",
                        "custom_metadata": {
                            "decision_status": "Status: proposed, approved, or rejected",
                            "stakeholders": "List key stakeholders",
                            "impact_assessment": "Business impact assessment",
                        },
                    }
                },
                priority=9,
            )
        )

        # Report enrichments
        suggestions.append(
            EnrichmentSuggestion(
                file_pattern="**/report*.md",
                enhancement_config={
                    "enhancements": {
                        "context": "Summarize key findings and recommendations",
                        "custom_metadata": {
                            "report_period": "Time period covered",
                            "key_metrics": "Main metrics or KPIs discussed",
                            "recommendations": "Key recommendations",
                        },
                    }
                },
                priority=7,
            )
        )

        # Spreadsheet enrichments
        suggestions.append(
            EnrichmentSuggestion(
                file_pattern="**/*.xlsx",
                enhancement_config={
                    "enhancements": {
                        "context": "Describe the data and its business purpose",
                        "custom_metadata": {
                            "data_description": "What data is tracked",
                            "update_frequency": "How often is this updated",
                            "business_use": "How is this data used",
                        },
                    }
                },
                priority=5,
            )
        )

        return suggestions
