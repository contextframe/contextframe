"""Storage optimization, index recommendations, and performance benchmarking."""

import asyncio
import numpy as np
import time
from contextframe.frame import FrameDataset
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class OptimizationResult:
    """Result of an optimization operation."""

    operation: str
    success: bool
    metrics: dict[str, Any]
    duration_seconds: float
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "success": self.success,
            "metrics": self.metrics,
            "duration_seconds": round(self.duration_seconds, 2),
            "timestamp": self.timestamp.isoformat(),
        }


class StorageOptimizer:
    """Optimizes Lance dataset storage using native capabilities."""

    def __init__(self, dataset: FrameDataset):
        """Initialize storage optimizer."""
        self.dataset = dataset
        self._optimization_history: list[OptimizationResult] = []

    async def optimize_storage(
        self,
        operations: list[str] = ["compact", "vacuum"],
        dry_run: bool = False,
        target_version: int | None = None,
    ) -> dict[str, Any]:
        """Optimize dataset storage.

        Args:
            operations: List of operations to perform
            dry_run: Preview changes without applying
            target_version: Optimize to specific version

        Returns:
            Optimization results
        """
        results = {
            "operations": [],
            "total_space_saved_mb": 0.0,
            "total_duration_seconds": 0.0,
        }

        # Get initial stats
        initial_stats = self.dataset.get_dataset_stats()

        for operation in operations:
            start_time = time.time()

            if operation == "compact":
                result = await self._compact_files(dry_run)
            elif operation == "vacuum":
                result = await self._vacuum_old_versions(dry_run, target_version)
            elif operation == "reindex":
                result = await self._optimize_indices(dry_run)
            else:
                result = {
                    "error": f"Unknown operation: {operation}",
                    "success": False,
                }

            duration = time.time() - start_time

            # Record result
            opt_result = OptimizationResult(
                operation=operation,
                success=result.get("success", False),
                metrics=result,
                duration_seconds=duration,
                timestamp=datetime.now(),
            )
            self._optimization_history.append(opt_result)

            results["operations"].append(opt_result.to_dict())
            results["total_duration_seconds"] += duration

            if "space_saved_mb" in result:
                results["total_space_saved_mb"] += result["space_saved_mb"]

        # Get final stats
        if not dry_run:
            final_stats = self.dataset.get_dataset_stats()
            results["before"] = initial_stats
            results["after"] = final_stats

        return results

    async def _compact_files(self, dry_run: bool) -> dict[str, Any]:
        """Compact dataset files."""
        try:
            if dry_run:
                # Preview compaction
                fragments = self.dataset.get_fragment_stats()
                small_fragments = [f for f in fragments if f["num_rows"] < 10000]

                return {
                    "success": True,
                    "preview": True,
                    "fragments_to_compact": len(small_fragments),
                    "estimated_fragments_after": max(
                        1, len(fragments) - len(small_fragments) + 1
                    ),
                }
            else:
                # Perform compaction
                result = self.dataset.compact_files()

                return {
                    "success": True,
                    "fragments_compacted": result.get("fragments_compacted", 0),
                    "files_removed": result.get("files_removed", 0),
                    "files_added": result.get("files_added", 0),
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _vacuum_old_versions(
        self, dry_run: bool, target_version: int | None = None
    ) -> dict[str, Any]:
        """Clean up old dataset versions."""
        try:
            # Calculate age threshold
            if target_version is not None:
                current_version = self.dataset._dataset.version
                versions_to_keep = current_version - target_version
                older_than = timedelta(days=versions_to_keep)  # Rough estimate
            else:
                older_than = timedelta(days=7)  # Default: keep last week

            if dry_run:
                # Estimate cleanup
                version_history = self.dataset.get_version_history()
                old_versions = [
                    v
                    for v in version_history
                    if v["version"] < (target_version or len(version_history) - 10)
                ]

                return {
                    "success": True,
                    "preview": True,
                    "versions_to_remove": len(old_versions),
                    "estimated_space_mb": len(old_versions) * 10,  # Rough estimate
                }
            else:
                # Perform cleanup
                result = self.dataset.cleanup_old_versions(older_than=older_than)

                return {
                    "success": True,
                    "bytes_removed": result.get("bytes_removed", 0),
                    "space_saved_mb": result.get("bytes_removed", 0) / (1024 * 1024),
                    "old_versions_removed": result.get("old_versions_removed", 0),
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _optimize_indices(self, dry_run: bool) -> dict[str, Any]:
        """Optimize dataset indices."""
        try:
            indices = self.dataset.list_indices()

            if dry_run:
                return {
                    "success": True,
                    "preview": True,
                    "indices_to_optimize": len(indices),
                    "index_names": [idx["name"] for idx in indices],
                }
            else:
                # Perform optimization
                result = self.dataset.optimize_indices()

                return {
                    "success": True,
                    "indices_optimized": result.get("indices_optimized", 0),
                    "status": result.get("status", "completed"),
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_optimization_history(self) -> list[dict[str, Any]]:
        """Get history of optimization operations."""
        return [opt.to_dict() for opt in self._optimization_history]


class IndexAdvisor:
    """Provides index recommendations based on query patterns."""

    def __init__(self, dataset: FrameDataset):
        """Initialize index advisor."""
        self.dataset = dataset
        self._query_patterns: dict[str, int] = {}
        self._field_usage: dict[str, int] = {}

    def record_query_pattern(self, filter_expr: str, fields: list[str]) -> None:
        """Record a query pattern for analysis."""
        self._query_patterns[filter_expr] = self._query_patterns.get(filter_expr, 0) + 1
        for field in fields:
            self._field_usage[field] = self._field_usage.get(field, 0) + 1

    async def get_recommendations(
        self, analyze_queries: bool = True, workload_type: str = "mixed"
    ) -> dict[str, Any]:
        """Get index recommendations.

        Args:
            analyze_queries: Analyze recent query patterns
            workload_type: Type of workload (search, analytics, mixed)

        Returns:
            Index recommendations
        """
        # Get current indices
        current_indices = self.dataset.list_indices()
        indexed_fields = set()

        for idx in current_indices:
            indexed_fields.update(idx.get("fields", []))

        # Analyze schema
        schema_fields = self._analyze_schema()

        # Generate recommendations
        recommendations = []

        # Vector index recommendations
        if "embedding" not in indexed_fields and workload_type in ["search", "mixed"]:
            recommendations.append(
                {
                    "type": "vector",
                    "field": "embedding",
                    "reason": "No vector index found for embedding field",
                    "priority": "high",
                    "estimated_benefit": "10-100x faster similarity search",
                    "command": "dataset.create_vector_index('embedding', metric='cosine', num_partitions=256)",
                }
            )

        # Scalar index recommendations
        scalar_candidates = self._identify_scalar_candidates(
            schema_fields, indexed_fields
        )

        for field, info in scalar_candidates.items():
            recommendations.append(
                {
                    "type": "scalar",
                    "field": field,
                    "reason": info["reason"],
                    "priority": info["priority"],
                    "estimated_benefit": f"{info['benefit']}x faster filtering",
                    "command": f"dataset.create_scalar_index('{field}')",
                }
            )

        # Full-text search index
        if "content" not in indexed_fields and workload_type in ["search", "mixed"]:
            recommendations.append(
                {
                    "type": "fts",
                    "field": "content",
                    "reason": "No full-text search index for content field",
                    "priority": "medium",
                    "estimated_benefit": "Enable text search capabilities",
                    "command": "dataset.create_scalar_index('content')",
                }
            )

        # Analyze redundant indices
        redundant = self._find_redundant_indices(current_indices)

        # Usage statistics
        usage_stats = await self._analyze_index_usage(current_indices)

        return {
            "current_indices": [
                {
                    "name": idx["name"],
                    "type": idx["type"],
                    "fields": idx["fields"],
                    "usage": usage_stats.get(idx["name"], "unknown"),
                }
                for idx in current_indices
            ],
            "recommendations": sorted(
                recommendations,
                key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3),
            ),
            "redundant_indices": redundant,
            "index_coverage": {
                "total_fields": len(schema_fields),
                "indexed_fields": len(indexed_fields),
                "coverage_percent": round(
                    len(indexed_fields) / len(schema_fields) * 100, 1
                ),
            },
        }

    def _analyze_schema(self) -> dict[str, dict[str, Any]]:
        """Analyze dataset schema for indexable fields."""
        schema = self.dataset._dataset.schema
        fields = {}

        for field in schema:
            field_type = str(field.type)
            fields[field.name] = {
                "type": field_type,
                "nullable": field.nullable,
                "metadata": dict(field.metadata) if field.metadata else {},
            }

        return fields

    def _identify_scalar_candidates(
        self, schema_fields: dict[str, dict[str, Any]], indexed_fields: set[str]
    ) -> dict[str, dict[str, Any]]:
        """Identify fields that would benefit from scalar indices."""
        candidates = {}

        # High-value fields for indexing
        high_value_fields = {
            "id": ("Primary key field", "high", 100),
            "record_type": ("Frequently filtered field", "high", 50),
            "created_at": ("Temporal queries", "medium", 20),
            "updated_at": ("Temporal queries", "medium", 20),
            "source_type": ("Content filtering", "medium", 10),
        }

        for field, (reason, priority, benefit) in high_value_fields.items():
            if field in schema_fields and field not in indexed_fields:
                candidates[field] = {
                    "reason": reason,
                    "priority": priority,
                    "benefit": benefit,
                }

        # Check field usage patterns
        for field, usage_count in self._field_usage.items():
            if field not in indexed_fields and usage_count > 10:
                if field not in candidates:
                    candidates[field] = {
                        "reason": f"Frequently queried field ({usage_count} times)",
                        "priority": "medium" if usage_count > 50 else "low",
                        "benefit": min(usage_count, 50),
                    }

        return candidates

    def _find_redundant_indices(
        self, current_indices: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Find potentially redundant indices."""
        redundant = []

        # Check for duplicate indices on same fields
        field_indices = {}
        for idx in current_indices:
            fields_key = tuple(sorted(idx.get("fields", [])))
            if fields_key in field_indices:
                redundant.append(
                    {
                        "index": idx["name"],
                        "reason": f"Duplicate of {field_indices[fields_key]}",
                        "action": "Consider removing",
                    }
                )
            else:
                field_indices[fields_key] = idx["name"]

        return redundant

    async def _analyze_index_usage(
        self, indices: list[dict[str, Any]]
    ) -> dict[str, str]:
        """Analyze index usage (simplified)."""
        usage = {}

        for idx in indices:
            # In a real implementation, this would query Lance statistics
            # For now, return estimated usage based on field
            if idx["type"] == "vector" or idx["fields"][0] in ["id", "record_type"]:
                usage[idx["name"]] = "high"
            else:
                usage[idx["name"]] = "medium"

        return usage


class PerformanceBenchmark:
    """Benchmarks dataset operations for performance analysis."""

    def __init__(self, dataset: FrameDataset):
        """Initialize performance benchmark."""
        self.dataset = dataset
        self._results: list[dict[str, Any]] = []

    async def benchmark_operations(
        self,
        operations: list[str] = ["search", "insert", "update", "scan"],
        sample_size: int = 100,
        concurrency: int = 1,
    ) -> dict[str, Any]:
        """Benchmark key dataset operations.

        Args:
            operations: Operations to benchmark
            sample_size: Number of operations per benchmark
            concurrency: Number of concurrent operations

        Returns:
            Benchmark results
        """
        results = {
            "configuration": {
                "sample_size": sample_size,
                "concurrency": concurrency,
                "timestamp": datetime.now().isoformat(),
            },
            "operations": {},
            "summary": {},
        }

        for operation in operations:
            if operation == "search":
                op_results = await self._benchmark_search(sample_size, concurrency)
            elif operation == "insert":
                op_results = await self._benchmark_insert(sample_size, concurrency)
            elif operation == "update":
                op_results = await self._benchmark_update(sample_size, concurrency)
            elif operation == "scan":
                op_results = await self._benchmark_scan(sample_size, concurrency)
            else:
                continue

            results["operations"][operation] = op_results
            self._results.append(
                {
                    "operation": operation,
                    "results": op_results,
                    "timestamp": datetime.now(),
                }
            )

        # Calculate summary
        results["summary"] = self._calculate_summary(results["operations"])

        return results

    async def _benchmark_search(
        self, sample_size: int, concurrency: int
    ) -> dict[str, Any]:
        """Benchmark search operations."""
        latencies = []

        # Get sample documents for queries
        sample_docs = []
        scanner = self.dataset.scanner(
            columns=["id", "embedding"],
            filter="embedding IS NOT NULL",
            limit=min(10, sample_size),
        )

        for batch in scanner.to_batches():
            ids = batch.column("id").to_pylist()
            embeddings = batch.column("embedding").to_pylist()
            for doc_id, emb in zip(ids, embeddings, strict=False):
                if emb:
                    sample_docs.append((doc_id, emb))

        if not sample_docs:
            return {"error": "No documents with embeddings found"}

        # Run search benchmarks
        async def run_search():
            _, emb = sample_docs[np.random.randint(0, len(sample_docs))]
            start = time.time()
            try:
                results = self.dataset.knn_search(query_vector=emb, k=10, filter=None)
                duration = (time.time() - start) * 1000  # ms
                return duration, len(results)
            except Exception as e:
                return None, str(e)

        # Run concurrent searches
        for _ in range(0, sample_size, concurrency):
            batch_tasks = [
                run_search()
                for _ in range(min(concurrency, sample_size - len(latencies)))
            ]
            batch_results = await asyncio.gather(*batch_tasks)

            for duration, result in batch_results:
                if duration is not None:
                    latencies.append(duration)

        if not latencies:
            return {"error": "No successful search operations"}

        return self._calculate_latency_stats(latencies, "search")

    async def _benchmark_insert(
        self, sample_size: int, concurrency: int
    ) -> dict[str, Any]:
        """Benchmark insert operations."""
        # For safety, we'll simulate inserts rather than actually inserting
        # In production, this would create test documents

        latencies = []

        # Simulate insert timing based on dataset characteristics
        base_latency = 10.0  # ms
        variance = 5.0

        for _ in range(sample_size):
            simulated_latency = base_latency + np.random.normal(0, variance)
            latencies.append(max(0.1, simulated_latency))

        return self._calculate_latency_stats(latencies, "insert (simulated)")

    async def _benchmark_update(
        self, sample_size: int, concurrency: int
    ) -> dict[str, Any]:
        """Benchmark update operations."""
        # Similar to insert, simulate for safety
        latencies = []

        base_latency = 15.0  # ms (updates typically slower)
        variance = 7.0

        for _ in range(sample_size):
            simulated_latency = base_latency + np.random.normal(0, variance)
            latencies.append(max(0.1, simulated_latency))

        return self._calculate_latency_stats(latencies, "update (simulated)")

    async def _benchmark_scan(
        self, sample_size: int, concurrency: int
    ) -> dict[str, Any]:
        """Benchmark scan operations."""
        latencies = []

        # Test different scan sizes
        scan_sizes = [10, 100, 1000]

        for size in scan_sizes:
            for _ in range(sample_size // len(scan_sizes)):
                start = time.time()
                try:
                    scanner = self.dataset.scanner(limit=size)
                    count = 0
                    for batch in scanner.to_batches():
                        count += len(batch)
                    duration = (time.time() - start) * 1000  # ms
                    latencies.append(duration)
                except Exception:
                    continue

        if not latencies:
            return {"error": "No successful scan operations"}

        return self._calculate_latency_stats(latencies, "scan")

    def _calculate_latency_stats(
        self, latencies: list[float], operation: str
    ) -> dict[str, Any]:
        """Calculate latency statistics."""
        return {
            "operation": operation,
            "sample_count": len(latencies),
            "latency_ms": {
                "min": round(min(latencies), 2),
                "p50": round(np.percentile(latencies, 50), 2),
                "p90": round(np.percentile(latencies, 90), 2),
                "p99": round(np.percentile(latencies, 99), 2),
                "max": round(max(latencies), 2),
                "mean": round(np.mean(latencies), 2),
                "std": round(np.std(latencies), 2),
            },
            "throughput_ops_per_sec": round(1000 / np.mean(latencies), 1),
        }

    def _calculate_summary(self, operations: dict[str, Any]) -> dict[str, Any]:
        """Calculate summary statistics across operations."""
        summary = {
            "fastest_operation": None,
            "slowest_operation": None,
            "performance_score": 0.0,
        }

        mean_latencies = {}
        for op_name, op_data in operations.items():
            if "latency_ms" in op_data:
                mean_latencies[op_name] = op_data["latency_ms"]["mean"]

        if mean_latencies:
            summary["fastest_operation"] = min(
                mean_latencies.items(), key=lambda x: x[1]
            )
            summary["slowest_operation"] = max(
                mean_latencies.items(), key=lambda x: x[1]
            )

            # Simple performance score (lower is better)
            summary["performance_score"] = round(
                sum(mean_latencies.values()) / len(mean_latencies), 2
            )

        return summary

    def get_benchmark_history(self) -> list[dict[str, Any]]:
        """Get history of benchmark results."""
        return [
            {
                "operation": r["operation"],
                "timestamp": r["timestamp"].isoformat(),
                "mean_latency_ms": r["results"].get("latency_ms", {}).get("mean"),
            }
            for r in self._results
        ]
