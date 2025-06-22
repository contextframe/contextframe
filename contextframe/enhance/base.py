"""Base enhancer for LLM-powered document enhancement using Mirascope."""

import datetime
from contextframe import FrameDataset, FrameRecord
from dataclasses import dataclass
from enum import Enum
from mirascope import llm
from mirascope.core import BaseMessageParam
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Optional


@dataclass
class EnhancementResult:
    """Result of an enhancement operation."""

    field_name: str
    value: Any
    success: bool
    error: str | None = None


# Schema-aligned response models
class ContextResponse(BaseModel):
    """Response model for context field enhancement."""

    context: str = Field(description="2-3 sentence context description")


class TagsResponse(BaseModel):
    """Response model for tags field enhancement."""

    tags: list[str] = Field(description="List of relevant tags")


class TitleResponse(BaseModel):
    """Response model for title field enhancement."""

    title: str = Field(description="Document title")


class StatusResponse(BaseModel):
    """Response model for status field enhancement."""

    status: str = Field(
        description="Document status", pattern="^(draft|review|published|archived)$"
    )


class CustomMetadataResponse(BaseModel):
    """Response model for custom metadata enhancement."""

    metadata: dict[str, Any] = Field(description="Custom metadata fields")


class RelationshipType(str, Enum):
    """Valid relationship types from schema."""

    PARENT = "parent"
    CHILD = "child"
    RELATED = "related"
    REFERENCE = "reference"
    CONTAINS = "contains"


class RelationshipResponse(BaseModel):
    """Response model for a single relationship."""

    type: RelationshipType
    title: str = Field(description="Title of the related document")
    description: str | None = Field(
        default=None, description="Brief description of the relationship"
    )
    target_id: str | None = Field(
        default=None, description="ID of the target document if known"
    )


class RelationshipsResponse(BaseModel):
    """Response model for relationships field enhancement."""

    relationships: list[RelationshipResponse] = Field(
        description="List of document relationships"
    )


class ContextEnhancer:
    """LLM-powered enhancer using Mirascope for structured outputs.

    This enhancer uses Mirascope to ensure LLM responses match ContextFrame
    schema field types, providing type safety and validation.

    Example:
        >>> enhancer = ContextEnhancer(provider="openai", model="gpt-4o-mini")
        >>> context = enhancer.enhance_context(
        ...     content="This document explains RAG architecture...",
        ...     purpose="building AI applications"
        ... )
    """

    # Map field names to response models
    FIELD_MODELS = {
        "context": ContextResponse,
        "tags": TagsResponse,
        "title": TitleResponse,
        "status": StatusResponse,
        "custom_metadata": CustomMetadataResponse,
        "relationships": RelationshipsResponse,
    }

    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini", **kwargs):
        """Initialize the enhancer.

        Args:
            provider: LLM provider (openai, anthropic, etc.)
            model: Model name
            **kwargs: Additional provider-specific arguments
        """
        self.provider = provider
        self.model = model
        self.kwargs = kwargs

    def enhance_context(
        self,
        content: str,
        purpose: str | None = None,
        current_context: str | None = None,
    ) -> str:
        """Enhance the context field with a description."""

        @llm.call(
            provider=self.provider,
            model=self.model,
            response_model=ContextResponse,
            **self.kwargs,
        )
        def generate_context(
            messages: list[BaseMessageParam],
        ) -> list[BaseMessageParam]:
            return messages

        prompt = f"""Analyze this document and write a brief context description (2-3 sentences).
{f'Focus on: {purpose}' if purpose else 'Explain what this document is about and why it matters.'}
{f'Current context: {current_context}' if current_context else ''}

Document content:
{content}"""

        response = generate_context(
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that enhances documents with meaningful context.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        return response.context

    def enhance_tags(
        self, content: str, tag_types: str | None = None, max_tags: int = 5
    ) -> list[str]:
        """Extract tags from document content."""

        @llm.call(
            provider=self.provider,
            model=self.model,
            response_model=TagsResponse,
            **self.kwargs,
        )
        def extract_tags(messages: list[BaseMessageParam]) -> list[BaseMessageParam]:
            return messages

        prompt = f"""Extract up to {max_tags} relevant tags from this document.
{f'Focus on: {tag_types}' if tag_types else 'Include topics, technologies, concepts, and categories.'}

Document content:
{content}"""

        response = extract_tags(
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts relevant tags from documents.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        return response.tags[:max_tags]

    def enhance_custom_metadata(
        self, content: str, schema_prompt: str
    ) -> dict[str, Any]:
        """Extract custom metadata based on user prompt."""

        @llm.call(
            provider=self.provider,
            model=self.model,
            response_model=CustomMetadataResponse,
            **self.kwargs,
        )
        def extract_metadata(
            messages: list[BaseMessageParam],
        ) -> list[BaseMessageParam]:
            return messages

        prompt = f"""Extract the following metadata from the document:
{schema_prompt}

Document content:
{content}"""

        response = extract_metadata(
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts structured metadata from documents.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        return response.metadata

    def enhance_relationships(
        self,
        source_content: str,
        source_title: str,
        candidates: list[dict[str, str]],
        max_relationships: int = 5,
    ) -> list[dict[str, Any]]:
        """Find relationships between documents."""

        @llm.call(
            provider=self.provider,
            model=self.model,
            response_model=RelationshipsResponse,
            **self.kwargs,
        )
        def find_relationships(
            messages: list[BaseMessageParam],
        ) -> list[BaseMessageParam]:
            return messages

        candidates_text = "\n".join(
            [
                f"{i + 1}. {c.get('title', 'Untitled')}: {c.get('summary', '')}"
                for i, c in enumerate(candidates[:10])
            ]
        )

        prompt = f"""Analyze the source document and identify relationships with the candidate documents.
Only include clear, meaningful relationships.

Source document:
Title: {source_title}
Content: {source_content}

Candidate documents:
{candidates_text}

Return up to {max_relationships} relationships."""

        response = find_relationships(
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that identifies relationships between documents.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        # Convert to schema format
        relationships = []
        for rel in response.relationships[:max_relationships]:
            rel_dict = {
                "type": rel.type.value,
                "title": rel.title,
            }
            if rel.description:
                rel_dict["description"] = rel.description
            if rel.target_id:
                rel_dict["id"] = rel.target_id
            relationships.append(rel_dict)

        return relationships

    def enhance_field(
        self,
        content: str,
        field_name: str,
        prompt: str,
        current_metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Enhance a single field using a custom prompt.

        This method allows flexible enhancement with user-defined prompts
        while still enforcing schema types.
        """
        # Get the appropriate response model
        response_model = self.FIELD_MODELS.get(field_name)
        if not response_model:
            raise ValueError(
                f"Unknown field: {field_name}. Valid fields: {list(self.FIELD_MODELS.keys())}"
            )

        # Build dynamic enhancement function
        @llm.call(
            provider=self.provider,
            model=self.model,
            response_model=response_model,
            **self.kwargs,
        )
        def enhance(messages: list[BaseMessageParam]) -> list[BaseMessageParam]:
            return messages

        # Build full prompt with template variables
        full_prompt = self._build_prompt(content, prompt, current_metadata)

        response = enhance(
            [
                {
                    "role": "system",
                    "content": f"You are a helpful assistant that enhances documents by extracting {field_name}.",
                },
                {"role": "user", "content": full_prompt},
            ]
        )

        # Extract the field value from response
        if field_name == "context":
            return response.context
        elif field_name == "tags":
            return response.tags
        elif field_name == "title":
            return response.title
        elif field_name == "status":
            return response.status
        elif field_name == "custom_metadata":
            return response.metadata
        elif field_name == "relationships":
            return [rel.model_dump(exclude_none=True) for rel in response.relationships]

        return response

    def enhance_document(
        self,
        frame: FrameRecord,
        enhancements: dict[str, str | dict[str, Any]],
        skip_existing: bool = True,
    ) -> FrameRecord:
        """Apply multiple enhancements to a document.

        Args:
            frame: Document to enhance
            enhancements: Map of field_name -> prompt or config dict
            skip_existing: Whether to skip fields that already have values

        Returns:
            Updated FrameRecord with enhanced fields
        """
        for field_name, config in enhancements.items():
            # Skip if field already has value and skip_existing is True
            if skip_existing and self._field_has_value(frame, field_name):
                continue

            # Parse enhancement config
            prompt = config if isinstance(config, str) else config.get("prompt", "")

            try:
                # Use specific enhancement methods when available
                if field_name == "context" and isinstance(config, str):
                    value = self.enhance_context(
                        frame.text_content or "", purpose=config
                    )
                elif field_name == "tags" and isinstance(config, str):
                    value = self.enhance_tags(frame.text_content or "")
                else:
                    # Fall back to flexible field enhancement
                    value = self.enhance_field(
                        content=frame.text_content or "",
                        field_name=field_name,
                        prompt=prompt,
                        current_metadata=self._get_frame_metadata(frame),
                    )

                # Update the frame
                self._update_frame_field(frame, field_name, value)

            except Exception as e:
                # Log error but continue with other fields
                print(f"Failed to enhance {field_name}: {e}")

        return frame

    def enhance_dataset(
        self,
        dataset: FrameDataset,
        enhancements: dict[str, str | dict[str, Any]],
        filter: str | None = None,
        batch_size: int = 10,
        skip_existing: bool = True,
        show_progress: bool = True,
    ) -> list[EnhancementResult]:
        """Enhance multiple documents in a dataset.

        Args:
            dataset: FrameDataset to enhance
            enhancements: Map of field_name -> prompt or config
            filter: Optional Lance SQL filter
            batch_size: Number of documents to process at once
            skip_existing: Whether to skip already-enhanced fields
            show_progress: Whether to show progress bar

        Returns:
            List of enhancement results
        """
        from contextframe.frame import FrameRecord

        # Get non-blob columns for scanning
        non_blob_columns = dataset._non_blob_columns
        if non_blob_columns is None:
            # If no blob columns, scan all columns
            scanner = dataset._dataset.scanner(batch_size=batch_size)
        else:
            # Exclude blob columns from scan
            scanner = dataset._dataset.scanner(
                columns=non_blob_columns, batch_size=batch_size
            )

        if filter:
            scanner = scanner.filter(filter)

        # Process in batches
        results = []
        total_processed = 0
        rows_updated = 0

        # Get total count for progress bar
        if show_progress:
            try:
                from tqdm import tqdm

                try:
                    total_count = dataset.count_rows(filter=filter)
                    pbar = tqdm(total=total_count, desc="Enhancing documents")
                except Exception:
                    # Fallback to indeterminate progress bar
                    pbar = tqdm(desc="Enhancing documents")
            except ImportError:
                show_progress = False
                pbar = None
        else:
            pbar = None

        for batch in scanner.to_batches():
            # Process each record in the batch
            for i in range(len(batch)):
                # Get single row as a table
                row_table = batch.slice(i, 1)
                frame = FrameRecord.from_arrow(
                    row_table, dataset_path=Path(dataset._dataset.uri)
                )

                # Track updates for this record
                updates = {}

                # Process each enhancement
                for field_name, config in enhancements.items():
                    # Skip if field already has value and skip_existing is True
                    if skip_existing and self._field_has_value(frame, field_name):
                        continue

                    # Parse enhancement config
                    prompt = (
                        config if isinstance(config, str) else config.get("prompt", "")
                    )

                    try:
                        # Enhance the specific field
                        value = self.enhance_field(
                            content=frame.text_content or "",
                            field_name=field_name,
                            prompt=prompt,
                            current_metadata=self._get_frame_metadata(frame),
                        )

                        # Add to updates
                        updates[field_name] = value

                        # Track result
                        results.append(EnhancementResult(field_name, value, True))

                    except Exception as e:
                        # Log error but continue
                        results.append(
                            EnhancementResult(field_name, None, False, str(e))
                        )

                # If we have updates, update the record in the dataset
                if updates:
                    # Update the frame's metadata with new values
                    for field_name, value in updates.items():
                        self._update_frame_field(frame, field_name, value)

                    # Update the updated_at timestamp
                    frame.metadata["updated_at"] = datetime.date.today().isoformat()

                    # Use the dataset's update_record method which does delete + add
                    try:
                        dataset.update_record(frame)
                        rows_updated += 1
                    except Exception as e:
                        print(f"Failed to update record {frame.uuid}: {e}")
                        # Continue with other records

            # Update progress
            if pbar is not None:
                pbar.update(len(batch))
            total_processed += len(batch)

        if pbar is not None:
            pbar.close()

        # Log summary
        if show_progress:
            print(f"Enhanced {rows_updated} records out of {total_processed} processed")

        return results

    def find_relationships(
        self,
        source_doc: FrameRecord,
        candidate_docs: list[FrameRecord],
        prompt: str | None = None,
        max_relationships: int = 5,
    ) -> list[dict[str, Any]]:
        """Find relationships between documents.

        This method matches the original API for compatibility.
        """
        candidates = [
            {
                "title": doc.title,
                "summary": (doc.text_content or "")[:200] + "..."
                if doc.text_content
                else "",
            }
            for doc in candidate_docs
        ]

        relationships = self.enhance_relationships(
            source_content=(source_doc.text_content or "")[:500],
            source_title=source_doc.title,
            candidates=candidates,
            max_relationships=max_relationships,
        )

        # Add UUIDs where we have matching documents
        for rel in relationships:
            matching_doc = next(
                (doc for doc in candidate_docs if doc.title == rel.get("title")), None
            )
            if matching_doc and "id" not in rel:
                rel["id"] = matching_doc.uuid

        return relationships

    # Helper methods

    def _build_prompt(
        self, content: str, prompt: str, metadata: dict | None = None
    ) -> str:
        """Build full prompt with template variables."""
        # Available template variables
        variables = {
            "content": content,
            "title": metadata.get("title", "") if metadata else "",
            "author": metadata.get("author", "") if metadata else "",
            "tags": ", ".join(metadata.get("tags", [])) if metadata else "",
            "context": metadata.get("context", "") if metadata else "",
            "uri": metadata.get("uri", "") if metadata else "",
        }

        # Simple template substitution
        filled_prompt = prompt
        for key, value in variables.items():
            filled_prompt = filled_prompt.replace(f"{{{key}}}", str(value))

        return filled_prompt

    def _field_has_value(self, frame: FrameRecord, field_name: str) -> bool:
        """Check if a field already has a value."""
        # Most fields are in metadata dict, not direct attributes
        if field_name == "text_content":
            value = frame.text_content
        elif field_name == "vector":
            value = frame.vector
        elif field_name in ["raw_data", "raw_data_type"]:
            value = getattr(frame, field_name, None)
        else:
            # Most fields are in metadata
            value = frame.metadata.get(field_name)

        if value is None:
            return False
        if isinstance(value, list | dict):
            return bool(value)
        if isinstance(value, str):
            return bool(value.strip())
        return True

    def _get_frame_metadata(self, frame: FrameRecord) -> dict[str, Any]:
        """Extract metadata from frame for context."""
        return {
            "title": frame.metadata.get("title", ""),
            "author": frame.metadata.get("author", ""),
            "tags": frame.metadata.get("tags", []),
            "context": frame.metadata.get("context", ""),
            "uri": frame.metadata.get("uri", ""),
            "collection": frame.metadata.get("collection", ""),
            "status": frame.metadata.get("status", ""),
        }

    def _update_frame_field(
        self, frame: FrameRecord, field_name: str, value: Any
    ) -> None:
        """Update a field on the frame."""
        if field_name == "text_content":
            frame.text_content = value
        elif field_name == "vector":
            frame.vector = value
        elif field_name in ["raw_data", "raw_data_type"]:
            setattr(frame, field_name, value)
        elif field_name == "custom_metadata" and isinstance(value, dict):
            # Convert all values to strings as required by schema
            string_metadata = {k: str(v) for k, v in value.items()}
            # Merge with existing custom metadata
            existing = frame.metadata.get("custom_metadata", {})
            if existing:
                existing.update(string_metadata)
                frame.metadata["custom_metadata"] = existing
            else:
                frame.metadata["custom_metadata"] = string_metadata
        else:
            # Most fields go in metadata
            frame.metadata[field_name] = value
