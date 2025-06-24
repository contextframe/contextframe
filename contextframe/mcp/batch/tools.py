"""Batch operation tools for MCP server."""

import asyncio
import json
import logging
from .handler import BatchOperationHandler, execute_parallel
from .transaction import BatchTransaction
from contextframe.frame import FrameDataset, FrameRecord
from contextframe.mcp.core.transport import TransportAdapter

# DocumentTools functionality is in ToolRegistry for now
# ValidationError is in pydantic
from contextframe.mcp.schemas import (
    BatchAddParams,
    BatchDeleteParams,
    BatchEnhanceParams,
    BatchExportParams,
    BatchExtractParams,
    BatchImportParams,
    BatchSearchParams,
    BatchUpdateParams,
)
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

logger = logging.getLogger(__name__)


class BatchTools:
    """Batch operation tools for efficient bulk operations."""

    def __init__(
        self,
        dataset: FrameDataset,
        transport: TransportAdapter,
        document_tools: Any | None = None,
    ):
        """Initialize batch tools.

        Args:
            dataset: The dataset to operate on
            transport: Transport adapter for progress
            document_tools: Existing document tools for reuse
        """
        self.dataset = dataset
        self.transport = transport
        self.handler = BatchOperationHandler(dataset, transport)

        # Reuse document tools if provided
        self.doc_tools = document_tools  # Should be ToolRegistry instance

    def register_tools(self, tool_registry):
        """Register batch tools with the tool registry."""
        tools = [
            ("batch_search", self.batch_search, BatchSearchParams),
            ("batch_add", self.batch_add, BatchAddParams),
            ("batch_update", self.batch_update, BatchUpdateParams),
            ("batch_delete", self.batch_delete, BatchDeleteParams),
            ("batch_enhance", self.batch_enhance, BatchEnhanceParams),
            ("batch_extract", self.batch_extract, BatchExtractParams),
            ("batch_export", self.batch_export, BatchExportParams),
            ("batch_import", self.batch_import, BatchImportParams),
        ]

        for name, handler, schema in tools:
            tool_registry.register_tool(
                name=name,
                handler=handler,
                schema=schema,
                description=schema.__doc__ or f"Batch {name.split('_')[1]} operation",
            )

    async def batch_search(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute multiple searches in parallel.

        Returns results grouped by query with progress tracking.
        """
        validated = BatchSearchParams(**params)
        queries = [q.model_dump() for q in validated.queries]
        max_parallel = validated.max_parallel

        # Create search tasks
        async def search_task(query_params: dict[str, Any]) -> dict[str, Any]:
            try:
                # Call search through tool registry
                search_result = await self.doc_tools.call_tool(
                    "search_documents",
                    {
                        "query": query_params["query"],
                        "search_type": query_params.get("search_type", "hybrid"),
                        "limit": query_params.get("limit", 10),
                        "filter": query_params.get("filter"),
                    },
                )
                results = search_result.get("documents", [])

                return {
                    "query": query_params["query"],
                    "success": True,
                    "results": results,
                    "count": len(results),
                }
            except Exception as e:
                return {
                    "query": query_params["query"],
                    "success": False,
                    "error": str(e),
                    "results": [],
                    "count": 0,
                }

        # Execute searches with controlled parallelism
        tasks = [lambda q=q: search_task(q) for q in queries]

        # Use execute_parallel to properly handle async tasks
        try:
            search_results = await execute_parallel(tasks, max_parallel)
            
            # Count successes and failures
            successful = [r for r in search_results if r.get("success", False)]
            failed = [r for r in search_results if not r.get("success", False)]
            
            return {
                "searches_completed": len(successful),
                "searches_failed": len(failed),
                "results": search_results,
                "errors": [{"query": r["query"], "error": r.get("error")} for r in failed],
            }
        except Exception as e:
            return {
                "searches_completed": 0,
                "searches_failed": len(queries),
                "results": [],
                "errors": [{"error": str(e)}],
            }

    async def batch_add(self, params: dict[str, Any]) -> dict[str, Any]:
        """Add multiple documents efficiently.

        Supports atomic transactions and shared settings.
        """
        validated = BatchAddParams(**params)
        documents = validated.documents
        shared = validated.shared_settings
        atomic = validated.atomic

        # Prepare records
        records = []
        for doc_data in documents:
            # Merge with shared settings
            content = doc_data.content
            metadata = {**shared.metadata, **doc_data.metadata}

            # Create record
            record = FrameRecord(text_content=content, metadata=metadata)
            
            # Apply collection from shared settings if specified
            if shared.collection:
                record.metadata["collection"] = shared.collection

            # Generate embeddings if requested
            if shared.generate_embeddings:
                try:
                    from contextframe.embed.litellm_provider import LiteLLMProvider

                    provider = LiteLLMProvider()
                    # LiteLLMProvider.embed is synchronous
                    result = provider.embed(content)
                    embedding = result.embeddings[0]
                    record.vector = embedding
                except Exception as e:
                    logger.warning(f"Failed to generate embedding: {e}")

            records.append(record)

        # Execute batch add
        if atomic:
            # Use transaction for atomic operation
            transaction = BatchTransaction(self.dataset)
            transaction.add_operation("add", records)

            try:
                await transaction.commit()
                return {
                    "success": True,
                    "documents_added": len(records),
                    "atomic": True,
                    "document_ids": [str(r.metadata["uuid"]) for r in records],
                }
            except Exception as e:
                return {
                    "success": False,
                    "documents_added": 0,
                    "atomic": True,
                    "error": str(e),
                }
        else:
            # Non-atomic batch add
            result = await self.handler.execute_batch(
                operation="batch_add",
                items=records,
                processor=lambda r: self.dataset.add(r),
                max_errors=10,
            )

            return {
                "success": result.total_errors == 0,
                "documents_added": result.total_processed,
                "documents_failed": result.total_errors,
                "atomic": False,
                "errors": result.errors,
            }

    async def batch_update(self, params: dict[str, Any]) -> dict[str, Any]:
        """Update multiple documents by filter or IDs.

        Supports metadata updates and content regeneration.
        """
        validated = BatchUpdateParams(**params)

        # Get documents to update
        if validated.document_ids:
            # Update specific documents
            docs = []
            for doc_id in validated.document_ids:
                try:
                    # Use scanner to get document by uuid
                    scanner = self.dataset.scanner(filter=f"uuid = '{doc_id}'", limit=1)
                    tbl = scanner.to_table()
                    if tbl.num_rows > 0:
                        doc = FrameRecord.from_arrow(tbl.slice(0, 1))
                        docs.append(doc)
                except:
                    pass
        else:
            # Update by filter
            if validated.filter:
                scanner_kwargs = {"filter": validated.filter, "limit": validated.max_documents}
                tbl = self.dataset.scanner(**scanner_kwargs).to_table()
                docs = []
                for i in range(tbl.num_rows):
                    docs.append(FrameRecord.from_arrow(tbl.slice(i, 1)))
            else:
                return {
                    "success": False,
                    "error": "Either document_ids or filter must be provided",
                }

        # Prepare update function
        updates = validated.updates
        
        # Debug: print what we're about to update
        logger.info(f"Updates object: {updates}")
        logger.info(f"Metadata updates: {updates.metadata_updates}")

        async def update_document(doc: FrameRecord) -> dict[str, Any]:
            try:
                # Apply metadata updates
                if updates.metadata_updates:
                    # Separate top-level fields from custom metadata
                    top_level_fields = {
                        "status", "priority", "tags", "title", "context", "version",
                        "author", "collection", "source_file", "source_type", "source_url"
                    }
                    
                    for key, value in updates.metadata_updates.items():
                        if key in top_level_fields:
                            # Update top-level field in metadata
                            doc.metadata[key] = value
                        elif key == "custom_metadata":
                            # Handle custom metadata updates
                            # Don't modify doc.metadata["custom_metadata"] directly
                            # Instead, we'll update the FrameRecord properly below
                            pass
                        else:
                            # Other metadata fields go directly into metadata dict
                            doc.metadata[key] = value

                # Apply content template if provided
                if updates.content_template:
                    # Simple template substitution
                    doc.text_content = updates.content_template.format(
                        content=doc.text_content,
                        title=doc.metadata.get("title", ""),
                        **doc.metadata,
                    )

                # Regenerate embeddings if requested
                if updates.regenerate_embeddings:
                    try:
                        from contextframe.embed.litellm_provider import LiteLLMProvider

                        provider = LiteLLMProvider()
                        result = provider.embed(doc.text_content)
                        doc.vector = result.embeddings[0]
                    except Exception as e:
                        logger.warning(f"Failed to regenerate embedding: {e}")

                # If we have custom_metadata updates, we need to recreate the record
                if updates.metadata_updates and "custom_metadata" in updates.metadata_updates:
                    # Get existing custom metadata as dict
                    existing_custom = {}
                    if isinstance(doc.metadata.get("custom_metadata"), list):
                        for item in doc.metadata["custom_metadata"]:
                            if isinstance(item, dict) and "key" in item and "value" in item:
                                existing_custom[item["key"]] = item["value"]
                    
                    # Merge with updates
                    existing_custom.update(updates.metadata_updates["custom_metadata"])
                    
                    # Create new record with updated metadata
                    updated_metadata = doc.metadata.copy()
                    updated_metadata["custom_metadata"] = existing_custom
                    
                    new_record = FrameRecord(
                        text_content=doc.text_content,
                        metadata=updated_metadata,
                        vector=doc.vector
                    )
                    
                    # Delete old and add new
                    self.dataset.delete_record(doc.metadata['uuid'])
                    self.dataset.add(new_record)
                else:
                    # Update in dataset (delete + add)
                    self.dataset.delete_record(doc.metadata['uuid'])
                    self.dataset.add(doc)

                # Debug: log what was updated
                logger.info(f"Updated doc {doc.metadata['uuid']} - status: {doc.metadata.get('status')}")

                return {"id": str(doc.metadata["uuid"]), "success": True}

            except Exception as e:
                logger.error(f"Error updating doc {doc.metadata.get('uuid')}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return {"id": str(doc.metadata.get("uuid", "unknown")), "success": False, "error": str(e)}

        # Execute batch update
        result = await self.handler.execute_batch(
            operation="batch_update", items=docs, processor=update_document
        )

        # Count actual successes and failures from results
        successful_updates = 0
        failed_updates = 0
        
        for res in result.results:
            if isinstance(res, dict) and res.get("success", False):
                successful_updates += 1
            else:
                failed_updates += 1

        return {
            "documents_updated": successful_updates,
            "documents_failed": failed_updates + result.total_errors,
            "total_documents": len(docs),
            "errors": result.errors,
        }

    async def batch_delete(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete multiple documents with safety checks.

        Supports dry run to preview deletions.
        """
        validated = BatchDeleteParams(**params)

        # Get documents to delete
        if validated.document_ids:
            doc_ids = [UUID(doc_id) for doc_id in validated.document_ids]
        else:
            # Delete by filter
            if validated.filter:
                tbl = self.dataset.scanner(filter=validated.filter).to_table()
                doc_ids = []
                for i in range(tbl.num_rows):
                    record = FrameRecord.from_arrow(tbl.slice(i, 1))
                    doc_ids.append(record.metadata["uuid"])
            else:
                return {
                    "success": False,
                    "error": "Either document_ids or filter must be provided",
                }

        # Check confirm count if provided
        if validated.confirm_count is not None:
            if len(doc_ids) != validated.confirm_count:
                return {
                    "success": False,
                    "error": f"Expected {validated.confirm_count} documents, found {len(doc_ids)}",
                    "dry_run": validated.dry_run,
                    "documents_found": len(doc_ids),
                }

        # Dry run - just return what would be deleted
        if validated.dry_run:
            return {
                "success": True,
                "dry_run": True,
                "documents_to_delete": len(doc_ids),
                "document_ids": [
                    str(doc_id) for doc_id in doc_ids[:100]
                ],  # Limit preview
                "message": f"Dry run - {len(doc_ids)} documents would be deleted",
            }

        # Execute deletion
        result = await self.handler.execute_batch(
            operation="batch_delete",
            items=doc_ids,
            processor=lambda doc_id: self.dataset.delete_record(doc_id),
        )

        return {
            "success": result.total_errors == 0,
            "documents_deleted": result.total_processed,
            "documents_failed": result.total_errors,
            "errors": result.errors,
        }

    async def batch_enhance(self, params: dict[str, Any]) -> dict[str, Any]:
        """Enhance multiple documents with LLM.

        Uses the enhance module to add context, tags, metadata etc.
        """
        validated = BatchEnhanceParams(**params)

        # Get documents to enhance
        if validated.document_ids:
            doc_ids = [UUID(doc_id) for doc_id in validated.document_ids]
        else:
            # Get by filter
            if validated.filter:
                scanner = self.dataset.scanner(filter=validated.filter)
                tbl = scanner.to_table()
                doc_ids = [
                    FrameRecord.from_arrow(tbl.slice(i, 1)).id
                    for i in range(tbl.num_rows)
                ]
            else:
                return {
                    "success": False,
                    "error": "Either document_ids or filter must be provided",
                }

        # Check if enhancement tools are available
        if not hasattr(self.tools, 'enhancement_tools'):
            # Try to initialize enhancement tools
            import os
            from contextframe.enhance import ContextEnhancer
            from contextframe.mcp.enhancement_tools import EnhancementTools

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "error": "No OpenAI API key found. Set OPENAI_API_KEY environment variable.",
                }

            try:
                model = os.environ.get("CONTEXTFRAME_ENHANCE_MODEL", "gpt-4")
                enhancer = ContextEnhancer(model=model, api_key=api_key)
                self.tools.enhancement_tools = EnhancementTools(enhancer)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to initialize enhancement tools: {str(e)}",
                }

        # Prepare enhancement processor
        enhancement_tools = self.tools.enhancement_tools

        async def enhance_document(doc_id: UUID) -> dict[str, Any]:
            # Get document
            record = self.dataset.get(doc_id)
            if not record:
                raise ValueError(f"Document {doc_id} not found")

            result = {"document_id": str(doc_id), "enhancements": {}, "errors": []}

            # Apply each enhancement
            for enhancement in validated.enhancements:
                try:
                    if enhancement == "context":
                        new_context = enhancement_tools.enhance_context(
                            content=record.text_content,
                            purpose=validated.purpose or "general understanding",
                            current_context=record.context,
                        )
                        result["enhancements"]["context"] = new_context

                    elif enhancement == "tags":
                        new_tags = enhancement_tools.generate_tags(
                            content=record.text_content,
                            tag_types="topics, technologies, concepts",
                            max_tags=10,
                        )
                        result["enhancements"]["tags"] = new_tags

                    elif enhancement == "title":
                        new_title = enhancement_tools.improve_title(
                            content=record.text_content,
                            current_title=record.title,
                            style="descriptive",
                        )
                        result["enhancements"]["title"] = new_title

                    elif enhancement == "metadata":
                        new_metadata = enhancement_tools.extract_metadata(
                            content=record.text_content,
                            schema=validated.purpose
                            or "Extract key facts and insights",
                            format="json",
                        )
                        result["enhancements"]["custom_metadata"] = new_metadata

                except Exception as e:
                    result["errors"].append(
                        {"enhancement": enhancement, "error": str(e)}
                    )

            # Update document if we have enhancements
            if result["enhancements"] and not result["errors"]:
                updates = {}
                if "context" in result["enhancements"]:
                    updates["context"] = result["enhancements"]["context"]
                if "tags" in result["enhancements"]:
                    updates["tags"] = result["enhancements"]["tags"]
                if "title" in result["enhancements"]:
                    updates["title"] = result["enhancements"]["title"]
                if "custom_metadata" in result["enhancements"]:
                    # Merge with existing metadata
                    existing_metadata = record.custom_metadata or {}
                    updates["custom_metadata"] = {
                        **existing_metadata,
                        **result["enhancements"]["custom_metadata"],
                    }

                # Update the record
                self.dataset.update(doc_id, **updates)

            return result

        # Process in batches if batch_size is specified
        batch_size = validated.batch_size
        if batch_size and batch_size > 1:
            # Process documents in groups for efficiency
            results = []
            for i in range(0, len(doc_ids), batch_size):
                batch_ids = doc_ids[i : i + batch_size]
                batch_result = await self.handler.execute_batch(
                    operation=f"batch_enhance_{i // batch_size + 1}",
                    items=batch_ids,
                    processor=enhance_document,
                )
                results.extend(batch_result.results)

            # Combine results
            total_processed = sum(1 for r in results if r.get("enhancements"))
            total_errors = sum(1 for r in results if r.get("errors"))

            return {
                "success": total_errors == 0,
                "documents_enhanced": total_processed,
                "documents_failed": total_errors,
                "total_documents": len(doc_ids),
                "results": results,
            }
        else:
            # Process all at once
            result = await self.handler.execute_batch(
                operation="batch_enhance", items=doc_ids, processor=enhance_document
            )

            return {
                "success": result.total_errors == 0,
                "documents_enhanced": result.total_processed,
                "documents_failed": result.total_errors,
                "total_documents": len(doc_ids),
                "results": result.results,
            }

    async def batch_extract(self, params: dict[str, Any]) -> dict[str, Any]:
        """Extract from multiple sources.

        Uses the extract module to process files and URLs.
        """
        validated = BatchExtractParams(**params)

        # Import extractors
        from contextframe.extract import (
            ExtractionResult,
            registry as extractor_registry,
        )

        # Prepare extraction processor
        async def extract_source(source: dict[str, Any]) -> dict[str, Any]:
            result = {
                "source": source,
                "success": False,
                "document_id": None,
                "error": None,
            }

            try:
                # Determine source path
                if source.get("type") == "file" or source.get("path"):
                    source_path = Path(source.get("path"))
                    if not source_path.exists():
                        raise FileNotFoundError(f"File not found: {source_path}")
                elif source.get("type") == "url" or source.get("url"):
                    # For URLs, we'd need to download first
                    # For now, we'll skip URL support
                    raise NotImplementedError("URL extraction not yet implemented")
                else:
                    raise ValueError("Source must have either 'path' or 'url'")

                # Find appropriate extractor
                extractor = extractor_registry.find_extractor(source_path)
                if not extractor:
                    raise ValueError(f"No extractor found for: {source_path}")

                # Extract content
                extraction_result: ExtractionResult = extractor.extract(source_path)

                if extraction_result.error:
                    raise ValueError(extraction_result.error)

                # Convert to FrameRecord if adding to dataset
                if validated.add_to_dataset:
                    record_kwargs = extraction_result.to_frame_record_kwargs()

                    # Add shared metadata
                    if validated.shared_metadata:
                        existing_metadata = record_kwargs.get("custom_metadata", {})
                        # Add x_ prefix to custom metadata fields
                        prefixed_metadata = {
                            f"x_{k}" if not k.startswith("x_") else k: v
                            for k, v in validated.shared_metadata.items()
                        }
                        record_kwargs["custom_metadata"] = {
                            **existing_metadata,
                            **prefixed_metadata,
                        }

                    # Set collection if specified
                    if validated.collection:
                        record_kwargs["metadata"] = record_kwargs.get("metadata", {})
                        record_kwargs["metadata"]["collection"] = validated.collection

                    # Create record
                    record = FrameRecord(**record_kwargs)
                    self.dataset.add(record)

                    result["document_id"] = str(record.id)

                result["success"] = True
                result["content_length"] = len(extraction_result.content)
                result["metadata"] = extraction_result.metadata
                result["format"] = extraction_result.format

                if extraction_result.warnings:
                    result["warnings"] = extraction_result.warnings

            except Exception as e:
                result["error"] = str(e)

                # Check if we should continue on error
                if not validated.continue_on_error:
                    raise

            return result

        # Execute batch extraction
        result = await self.handler.execute_batch(
            operation="batch_extract",
            items=validated.sources,
            processor=extract_source,
            max_errors=None if validated.continue_on_error else 1,
        )

        # Count successes
        successful_extractions = sum(1 for r in result.results if r.get("success"))
        documents_added = sum(1 for r in result.results if r.get("document_id"))

        return {
            "success": result.total_errors == 0,
            "sources_processed": len(validated.sources),
            "sources_extracted": successful_extractions,
            "sources_failed": result.total_errors,
            "documents_added": documents_added if validated.add_to_dataset else 0,
            "results": result.results,
            "errors": result.errors,
        }

    async def batch_export(self, params: dict[str, Any]) -> dict[str, Any]:
        """Export documents in bulk.

        Uses the io.exporter module to export documents in various formats.
        """
        validated = BatchExportParams(**params)

        # Import export utilities
        import csv
        from contextframe.io.formats import ExportFormat

        # Get documents to export
        if validated.document_ids:
            doc_ids = validated.document_ids
            docs = []
            for doc_id in doc_ids:
                scanner = self.dataset.scanner(filter=f"uuid = '{doc_id}'", limit=1)
                tbl = scanner.to_table()
                if tbl.num_rows > 0:
                    doc = FrameRecord.from_arrow(tbl.slice(0, 1))
                    docs.append(doc)
        else:
            # Export by filter or limit
            scanner_kwargs = {}
            if validated.filter:
                scanner_kwargs["filter"] = validated.filter
            if validated.limit:
                scanner_kwargs["limit"] = validated.limit
                
            # If no filter or document_ids, but limit is provided, export up to limit
            if not validated.filter and not validated.document_ids and validated.limit:
                scanner = self.dataset.scanner(**scanner_kwargs)
                tbl = scanner.to_table()
                docs = [
                    FrameRecord.from_arrow(tbl.slice(i, 1)) for i in range(tbl.num_rows)
                ]
            elif validated.filter:
                scanner = self.dataset.scanner(**scanner_kwargs)
                tbl = scanner.to_table()
                docs = [
                    FrameRecord.from_arrow(tbl.slice(i, 1)) for i in range(tbl.num_rows)
                ]
            else:
                return {
                    "success": False,
                    "error": "Either document_ids, filter, or limit must be provided",
                }

        if not docs:
            return {"success": False, "error": "No documents found to export"}

        # Prepare output path
        output_path = Path(validated.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine format
        try:
            format_enum = ExportFormat(validated.format.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Unsupported format: {validated.format}",
            }

        # Process documents based on format
        try:
            if format_enum == ExportFormat.JSON:
                # Export as JSON
                export_data = []
                for doc in docs:
                    doc_dict = {
                        "id": str(doc.metadata["uuid"]),
                        "content": doc.text_content,
                        "metadata": doc.metadata,
                        "title": doc.metadata.get("title", ""),
                        "context": doc.metadata.get("context", ""),
                        "tags": doc.metadata.get("tags", []),
                        "custom_metadata": doc.metadata.get("custom_metadata", []),
                        "created_at": doc.metadata.get("created_at"),
                        "updated_at": doc.metadata.get("updated_at"),
                    }

                    if validated.include_embeddings and doc.vector is not None:
                        doc_dict["embeddings"] = doc.vector.tolist()

                    export_data.append(doc_dict)

                # Handle chunking for large exports
                if validated.chunk_size and len(export_data) > validated.chunk_size:
                    # Export in chunks
                    exported_files = []
                    for i in range(0, len(export_data), validated.chunk_size):
                        chunk = export_data[i : i + validated.chunk_size]
                        chunk_path = (
                            output_path.parent
                            / f"{output_path.stem}_chunk_{i // validated.chunk_size}{output_path.suffix}"
                        )

                        with open(chunk_path, "w") as f:
                            json.dump({"documents": chunk}, f, indent=2)

                        exported_files.append(str(chunk_path))

                    return {
                        "success": True,
                        "format": validated.format,
                        "documents_exported": len(docs),
                        "files_created": len(exported_files),
                        "output_files": exported_files,
                    }
                else:
                    # Export as single file
                    with open(output_path, "w") as f:
                        json.dump({"documents": export_data}, f, indent=2)

            elif format_enum == ExportFormat.JSONL:
                # Export as JSONL (newline-delimited JSON)
                with open(output_path, "w") as f:
                    for doc in docs:
                        doc_dict = {
                            "id": str(doc.metadata["uuid"]),
                            "content": doc.text_content,
                            "metadata": doc.metadata,
                            "title": doc.metadata.get("title", ""),
                            "context": doc.metadata.get("context", ""),
                            "tags": doc.metadata.get("tags", []),
                            "custom_metadata": doc.metadata.get("custom_metadata", []),
                        }

                        if validated.include_embeddings and doc.vector is not None:
                            doc_dict["embeddings"] = doc.vector.tolist()

                        f.write(json.dumps(doc_dict) + "\n")

            elif format_enum == ExportFormat.CSV:
                # Export as CSV
                fieldnames = [
                    "id",
                    "title",
                    "content",
                    "context",
                    "tags",
                    "created_at",
                    "updated_at",
                ]

                # Add custom metadata fields
                all_custom_fields = set()
                for doc in docs:
                    custom_metadata = doc.metadata.get("custom_metadata", [])
                    if custom_metadata:
                        for item in custom_metadata:
                            if isinstance(item, dict) and "key" in item:
                                all_custom_fields.add(item["key"])

                fieldnames.extend(sorted(all_custom_fields))

                with open(output_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for doc in docs:
                        row = {
                            "id": str(doc.metadata["uuid"]),
                            "title": doc.metadata.get("title", ""),
                            "content": doc.text_content,
                            "context": doc.metadata.get("context", ""),
                            "tags": ", ".join(doc.metadata.get("tags", [])),
                            "created_at": doc.metadata.get("created_at", ""),
                            "updated_at": doc.metadata.get("updated_at", ""),
                        }

                        # Add custom metadata
                        custom_metadata = doc.metadata.get("custom_metadata", [])
                        if custom_metadata:
                            for item in custom_metadata:
                                if isinstance(item, dict) and "key" in item and "value" in item:
                                    row[item["key"]] = str(item["value"])

                        writer.writerow(row)

            elif format_enum == ExportFormat.PARQUET:
                # Export as Parquet (requires pyarrow)
                try:
                    import pyarrow as pa
                    import pyarrow.parquet as pq

                    # Convert documents to arrow table
                    table_data = {
                        "id": [str(doc.metadata["uuid"]) for doc in docs],
                        "content": [doc.text_content for doc in docs],
                        "title": [doc.metadata.get("title", "") for doc in docs],
                        "context": [doc.metadata.get("context", "") for doc in docs],
                        "tags": [doc.metadata.get("tags", []) for doc in docs],
                        "created_at": [doc.metadata.get("created_at") for doc in docs],
                        "updated_at": [doc.metadata.get("updated_at") for doc in docs],
                    }

                    if validated.include_embeddings:
                        table_data["embeddings"] = [doc.vector for doc in docs]

                    table = pa.table(table_data)
                    pq.write_table(table, output_path)

                except ImportError:
                    return {
                        "success": False,
                        "error": "Parquet export requires pyarrow. Install with: pip install pyarrow",
                    }
            else:
                return {
                    "success": False,
                    "error": f"Format {format_enum} not yet implemented for batch export",
                }

            return {
                "success": True,
                "format": validated.format,
                "documents_exported": len(docs),
                "output_path": str(output_path),
                "file_size_bytes": output_path.stat().st_size,
            }

        except Exception as e:
            return {"success": False, "error": f"Export failed: {str(e)}"}

    async def batch_import(self, params: dict[str, Any]) -> dict[str, Any]:
        """Import documents from files.

        Uses the io module to import documents from various formats.
        """
        validated = BatchImportParams(**params)

        # Import utilities
        import csv
        from contextframe.io.formats import ExportFormat

        source_path = Path(validated.source_path)
        if not source_path.exists():
            return {"success": False, "error": f"Source path not found: {source_path}"}

        # Determine format
        try:
            format_enum = ExportFormat(validated.format.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Unsupported format: {validated.format}",
            }

        # Prepare validation settings
        max_errors = (
            validated.validation.get("max_errors", 10) if validated.validation else 10
        )
        require_schema_match = (
            validated.validation.get("require_schema_match", False)
            if validated.validation
            else False
        )

        # Track import progress
        import_results = []
        error_count = 0

        async def import_document(doc_data: dict[str, Any]) -> dict[str, Any]:
            result = {
                "success": False,
                "document_id": None,
                "error": None,
                "source_id": doc_data.get("id", "unknown"),
            }

            try:
                # Apply field mapping if provided
                if validated.mapping:
                    mapped_data = {}
                    for source_field, target_field in validated.mapping.items():
                        if source_field in doc_data:
                            mapped_data[target_field] = doc_data[source_field]
                    doc_data.update(mapped_data)

                # Extract fields according to schema
                # Start with base metadata
                metadata = doc_data.get("metadata", {})
                
                # Add title to metadata (required field)
                if "title" in doc_data:
                    metadata["title"] = doc_data["title"]
                elif "title" not in metadata:
                    metadata["title"] = "Imported Document"
                
                # Add other metadata fields
                if "context" in doc_data:
                    metadata["context"] = doc_data["context"]
                if "tags" in doc_data:
                    tags = doc_data["tags"]
                    if isinstance(tags, str):
                        # Handle comma-separated tags
                        metadata["tags"] = [
                            t.strip() for t in tags.split(",") if t.strip()
                        ]
                    else:
                        metadata["tags"] = tags
                
                # Handle custom metadata
                if "custom_metadata" in doc_data:
                    # Ensure x_ prefix for custom metadata
                    custom_metadata = {}
                    for k, v in doc_data["custom_metadata"].items():
                        key = f"x_{k}" if not k.startswith("x_") else k
                        custom_metadata[key] = v
                    metadata["custom_metadata"] = custom_metadata
                
                # Ensure record_type is set
                if "record_type" not in metadata:
                    metadata["record_type"] = "document"
                
                record_kwargs = {
                    "text_content": doc_data.get(
                        "content", doc_data.get("text_content", "")
                    ),
                    "metadata": metadata,
                }

                # Handle embeddings if present
                if "embeddings" in doc_data and not validated.generate_embeddings:
                    record_kwargs["vector"] = doc_data["embeddings"]

                # Create and add record
                record = FrameRecord(**record_kwargs)
                logger.debug(f"Adding record with UUID: {record.metadata['uuid']}")
                
                self.dataset.add(record)
                logger.debug(f"Successfully added record {record.metadata['uuid']}")

                # Generate embeddings if requested
                if validated.generate_embeddings and not record.vector:
                    # Would need to integrate with embed module here
                    pass

                result["success"] = True
                result["document_id"] = str(record.metadata["uuid"])

            except Exception as e:
                result["error"] = str(e)
                if require_schema_match:
                    raise

            return result

        try:
            documents_to_import = []

            if format_enum == ExportFormat.JSON:
                # Import from JSON
                with open(source_path) as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "documents" in data:
                        documents_to_import = data["documents"]
                    elif isinstance(data, list):
                        documents_to_import = data
                    else:
                        documents_to_import = [data]

            elif format_enum == ExportFormat.JSONL:
                # Import from JSONL
                with open(source_path) as f:
                    for line in f:
                        if line.strip():
                            documents_to_import.append(json.loads(line))

            elif format_enum == ExportFormat.CSV:
                # Import from CSV
                with open(source_path, newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Convert CSV row to document format
                        doc = {
                            "content": row.get("content", ""),
                            "title": row.get("title", ""),
                            "context": row.get("context", ""),
                            "tags": row.get("tags", ""),
                        }

                        # Extract custom metadata from remaining fields
                        standard_fields = {
                            "id",
                            "content",
                            "title",
                            "context",
                            "tags",
                            "created_at",
                            "updated_at",
                        }
                        custom_metadata = {}
                        for k, v in row.items():
                            if k not in standard_fields and v:
                                custom_metadata[k] = v

                        if custom_metadata:
                            doc["custom_metadata"] = custom_metadata

                        documents_to_import.append(doc)

            elif format_enum == ExportFormat.PARQUET:
                # Import from Parquet
                try:
                    import pyarrow.parquet as pq

                    table = pq.read_table(source_path)

                    # Convert to list of dicts
                    for i in range(table.num_rows):
                        doc = {}
                        for field in table.schema:
                            value = table[field.name][i].as_py()
                            if value is not None:
                                doc[field.name] = value
                        documents_to_import.append(doc)

                except ImportError:
                    return {
                        "success": False,
                        "error": "Parquet import requires pyarrow. Install with: pip install pyarrow",
                    }
            else:
                return {
                    "success": False,
                    "error": f"Format {format_enum} not yet implemented for batch import",
                }

            # Execute batch import
            logger.info(f"Importing {len(documents_to_import)} documents")
            result = await self.handler.execute_batch(
                operation="batch_import",
                items=documents_to_import,
                processor=import_document,
                max_errors=max_errors,
            )
            logger.info(f"Import result: processed={result.total_processed}, errors={result.total_errors}")
            
            # Debug: check row count
            current_count = self.dataset._dataset.count_rows()
            logger.info(f"Dataset row count after import: {current_count}")

            return {
                "success": result.total_errors == 0,
                "source_path": str(source_path),
                "format": validated.format,
                "documents_found": len(documents_to_import),
                "documents_imported": result.total_processed,
                "documents_failed": result.total_errors,
                "errors": result.errors[:10]
                if result.errors
                else [],  # Limit error details
            }

        except Exception as e:
            return {"success": False, "error": f"Import failed: {str(e)}"}
