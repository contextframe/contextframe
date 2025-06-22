"""Query, usage, and relationship analysis for ContextFrame datasets."""

import asyncio
import numpy as np
import pyarrow.compute as pc
import time
from collections import defaultdict, deque
from contextframe.frame import FrameDataset
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Deque, Dict, List, Optional, Set, Tuple


@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""

    query_type: str  # "vector", "text", "hybrid", "filter"
    query_text: str | None = None
    filter_expression: str | None = None
    duration_ms: float = 0.0
    rows_scanned: int = 0
    rows_returned: int = 0
    index_used: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.query_type,
            "query": self.query_text,
            "filter": self.filter_expression,
            "duration_ms": round(self.duration_ms, 2),
            "rows_scanned": self.rows_scanned,
            "rows_returned": self.rows_returned,
            "index_used": self.index_used,
            "timestamp": self.timestamp.isoformat(),
        }


class QueryAnalyzer:
    """Analyzes query patterns and performance."""

    def __init__(self, dataset: FrameDataset, max_history: int = 10000):
        """Initialize query analyzer.

        Args:
            dataset: The dataset to analyze
            max_history: Maximum query history to maintain
        """
        self.dataset = dataset
        self.max_history = max_history
        self.query_history: deque[QueryMetrics] = deque(maxlen=max_history)
        self._query_cache: dict[str, list[QueryMetrics]] = defaultdict(list)

    def record_query(self, metrics: QueryMetrics) -> None:
        """Record a query execution."""
        self.query_history.append(metrics)
        self._query_cache[metrics.query_type].append(metrics)

    async def analyze_performance(
        self,
        time_range: timedelta | None = None,
        query_type: str | None = None,
        min_duration_ms: float = 0.0,
    ) -> dict[str, Any]:
        """Analyze query performance.

        Args:
            time_range: Analyze queries within this time range
            query_type: Filter by query type
            min_duration_ms: Only include queries slower than this

        Returns:
            Performance analysis results
        """
        # Filter queries
        queries = list(self.query_history)

        if time_range:
            cutoff = datetime.now() - time_range
            queries = [q for q in queries if q.timestamp >= cutoff]

        if query_type:
            queries = [q for q in queries if q.query_type == query_type]

        if min_duration_ms > 0:
            queries = [q for q in queries if q.duration_ms >= min_duration_ms]

        if not queries:
            return {"message": "No queries match the criteria"}

        # Calculate statistics
        durations = [q.duration_ms for q in queries]
        rows_scanned = [q.rows_scanned for q in queries]

        # Group by query type
        by_type = defaultdict(list)
        for q in queries:
            by_type[q.query_type].append(q)

        # Find slow queries
        slow_queries = sorted(queries, key=lambda q: q.duration_ms, reverse=True)[:10]

        # Identify patterns
        filter_patterns = defaultdict(int)
        for q in queries:
            if q.filter_expression:
                # Simple pattern extraction (could be enhanced)
                if "=" in q.filter_expression:
                    field = q.filter_expression.split("=")[0].strip()
                    filter_patterns[field] += 1

        return {
            "summary": {
                "total_queries": len(queries),
                "avg_duration_ms": round(np.mean(durations), 2),
                "p50_duration_ms": round(np.percentile(durations, 50), 2),
                "p90_duration_ms": round(np.percentile(durations, 90), 2),
                "p99_duration_ms": round(np.percentile(durations, 99), 2),
                "max_duration_ms": round(max(durations), 2),
                "avg_rows_scanned": round(np.mean(rows_scanned), 0),
            },
            "by_type": {
                qtype: {
                    "count": len(queries),
                    "avg_duration_ms": round(
                        np.mean([q.duration_ms for q in queries]), 2
                    ),
                    "index_usage_rate": sum(1 for q in queries if q.index_used)
                    / len(queries),
                }
                for qtype, queries in by_type.items()
            },
            "slow_queries": [
                {
                    "query": q.to_dict(),
                    "optimization_hints": self._get_optimization_hints(q),
                }
                for q in slow_queries
            ],
            "filter_patterns": dict(filter_patterns),
        }

    def _get_optimization_hints(self, query: QueryMetrics) -> list[str]:
        """Generate optimization hints for a query."""
        hints = []

        # Check index usage
        if not query.index_used and query.query_type in ["vector", "text"]:
            hints.append(f"Consider creating a {query.query_type} index")

        # Check scan efficiency
        if query.rows_scanned > 0 and query.rows_returned > 0:
            selectivity = query.rows_returned / query.rows_scanned
            if selectivity < 0.01:  # Less than 1% selectivity
                hints.append("Very low selectivity - consider more specific filters")

        # Check duration
        if query.duration_ms > 1000:
            hints.append("Query taking over 1 second - review query complexity")

        # Filter suggestions
        if query.filter_expression and "OR" in query.filter_expression:
            hints.append("OR conditions can be slow - consider using IN operator")

        return hints


class UsageAnalyzer:
    """Analyzes dataset usage patterns."""

    def __init__(self, dataset: FrameDataset):
        """Initialize usage analyzer."""
        self.dataset = dataset
        self._access_log: dict[str, list[datetime]] = defaultdict(list)
        self._operation_counts: dict[str, int] = defaultdict(int)

    def record_access(self, document_id: str, operation: str = "read") -> None:
        """Record a document access."""
        self._access_log[document_id].append(datetime.now())
        self._operation_counts[operation] += 1

    async def analyze_usage(
        self,
        time_range: timedelta | None = None,
        group_by: str = "hour",
        include_patterns: bool = True,
    ) -> dict[str, Any]:
        """Analyze usage patterns.

        Args:
            time_range: Period to analyze
            group_by: Grouping period (hour, day, week)
            include_patterns: Include access pattern analysis

        Returns:
            Usage analysis results
        """
        # Filter by time range
        cutoff = None
        if time_range:
            cutoff = datetime.now() - time_range

        # Get document metadata for enrichment
        doc_metadata = await self._get_document_metadata()

        # Analyze access patterns
        access_stats = self._analyze_access_patterns(cutoff)

        # Time-based analysis
        time_stats = self._analyze_temporal_patterns(cutoff, group_by)

        # Collection usage
        collection_stats = await self._analyze_collection_usage(cutoff)

        # Operation statistics
        operation_stats = dict(self._operation_counts)

        results = {
            "summary": {
                "total_accesses": sum(
                    len(accesses) for accesses in self._access_log.values()
                ),
                "unique_documents": len(self._access_log),
                "operations": operation_stats,
            },
            "access_patterns": access_stats,
            "temporal_patterns": time_stats,
            "collection_usage": collection_stats,
        }

        if include_patterns:
            results["recommendations"] = self._generate_usage_recommendations(
                access_stats, collection_stats
            )

        return results

    async def _get_document_metadata(self) -> dict[str, dict[str, Any]]:
        """Get metadata for accessed documents."""
        if not self._access_log:
            return {}

        doc_ids = list(self._access_log.keys())
        metadata = {}

        # Batch fetch metadata
        for batch_start in range(0, len(doc_ids), 100):
            batch_ids = doc_ids[batch_start : batch_start + 100]
            filter_expr = " OR ".join(f"id = '{doc_id}'" for doc_id in batch_ids)

            scanner = self.dataset.scanner(
                columns=["id", "record_type", "context"], filter=filter_expr
            )

            for batch in scanner.to_batches():
                ids = batch.column("id").to_pylist()
                types = batch.column("record_type").to_pylist()
                contexts = batch.column("context").to_pylist()

                for doc_id, doc_type, context in zip(
                    ids, types, contexts, strict=False
                ):
                    metadata[doc_id] = {
                        "type": doc_type,
                        "collection_id": context.get("collection_id")
                        if context
                        else None,
                    }

        return metadata

    def _analyze_access_patterns(self, cutoff: datetime | None) -> dict[str, Any]:
        """Analyze document access patterns."""
        access_counts = {}
        recent_accesses = {}

        for doc_id, accesses in self._access_log.items():
            if cutoff:
                accesses = [a for a in accesses if a >= cutoff]

            if accesses:
                access_counts[doc_id] = len(accesses)
                recent_accesses[doc_id] = max(accesses)

        if not access_counts:
            return {}

        # Find hot documents
        sorted_docs = sorted(access_counts.items(), key=lambda x: x[1], reverse=True)
        hot_documents = sorted_docs[:10]

        # Calculate access distribution
        counts = list(access_counts.values())

        return {
            "hot_documents": [
                {"id": doc_id, "access_count": count} for doc_id, count in hot_documents
            ],
            "access_distribution": {
                "mean": round(np.mean(counts), 2),
                "median": round(np.median(counts), 2),
                "p90": round(np.percentile(counts, 90), 2),
                "max": max(counts),
            },
            "total_accessed": len(access_counts),
        }

    def _analyze_temporal_patterns(
        self, cutoff: datetime | None, group_by: str
    ) -> dict[str, Any]:
        """Analyze temporal access patterns."""
        # Flatten all accesses
        all_accesses = []
        for accesses in self._access_log.values():
            if cutoff:
                all_accesses.extend([a for a in accesses if a >= cutoff])
            else:
                all_accesses.extend(accesses)

        if not all_accesses:
            return {}

        # Group by time period
        time_buckets = defaultdict(int)

        for access_time in all_accesses:
            if group_by == "hour":
                bucket = access_time.replace(minute=0, second=0, microsecond=0)
            elif group_by == "day":
                bucket = access_time.replace(hour=0, minute=0, second=0, microsecond=0)
            elif group_by == "week":
                # Start of week
                days_since_monday = access_time.weekday()
                bucket = access_time.replace(hour=0, minute=0, second=0, microsecond=0)
                bucket -= timedelta(days=days_since_monday)
            else:
                bucket = access_time  # Default to exact time

            time_buckets[bucket] += 1

        # Convert to sorted list
        sorted_buckets = sorted(time_buckets.items())

        return {
            "time_series": [
                {"time": t.isoformat(), "count": count} for t, count in sorted_buckets
            ],
            "peak_period": max(time_buckets.items(), key=lambda x: x[1])[0].isoformat(),
            "total_periods": len(time_buckets),
        }

    async def _analyze_collection_usage(
        self, cutoff: datetime | None
    ) -> dict[str, Any]:
        """Analyze usage by collection."""
        doc_metadata = await self._get_document_metadata()

        collection_accesses = defaultdict(int)
        collection_docs = defaultdict(set)

        for doc_id, accesses in self._access_log.items():
            if cutoff:
                accesses = [a for a in accesses if a >= cutoff]

            if accesses and doc_id in doc_metadata:
                coll_id = doc_metadata[doc_id].get("collection_id")
                if coll_id:
                    collection_accesses[coll_id] += len(accesses)
                    collection_docs[coll_id].add(doc_id)

        if not collection_accesses:
            return {}

        # Sort by access count
        sorted_collections = sorted(
            collection_accesses.items(), key=lambda x: x[1], reverse=True
        )

        return {
            "most_accessed": [
                {
                    "collection_id": coll_id,
                    "access_count": count,
                    "unique_documents": len(collection_docs[coll_id]),
                }
                for coll_id, count in sorted_collections[:10]
            ],
            "total_collections": len(collection_accesses),
        }

    def _generate_usage_recommendations(
        self, access_stats: dict[str, Any], collection_stats: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations based on usage patterns."""
        recommendations = []

        # Hot document caching
        if "hot_documents" in access_stats and access_stats["hot_documents"]:
            top_doc = access_stats["hot_documents"][0]
            if top_doc["access_count"] > 100:
                recommendations.append(
                    f"Consider caching frequently accessed documents "
                    f"(top document accessed {top_doc['access_count']} times)"
                )

        # Access distribution
        if "access_distribution" in access_stats:
            dist = access_stats["access_distribution"]
            if dist["max"] > dist["mean"] * 10:
                recommendations.append(
                    "Highly skewed access pattern detected - "
                    "consider optimizing for hot path"
                )

        # Collection patterns
        if "most_accessed" in collection_stats and collection_stats["most_accessed"]:
            top_coll = collection_stats["most_accessed"][0]
            recommendations.append(
                f"Collection '{top_coll['collection_id']}' is most active - "
                "ensure it has appropriate indices"
            )

        return recommendations


class RelationshipAnalyzer:
    """Analyzes document relationships and graph structure."""

    def __init__(self, dataset: FrameDataset):
        """Initialize relationship analyzer."""
        self.dataset = dataset
        self._graph_cache: dict[str, list[tuple[str, str]]] | None = None

    async def analyze_relationships(
        self,
        max_depth: int = 3,
        relationship_types: list[str] | None = None,
        include_orphans: bool = True,
    ) -> dict[str, Any]:
        """Analyze document relationship graph.

        Args:
            max_depth: Maximum traversal depth
            relationship_types: Types to include (None = all)
            include_orphans: Include unconnected documents

        Returns:
            Relationship analysis results
        """
        # Build relationship graph
        graph = await self._build_relationship_graph(relationship_types)

        # Calculate graph metrics
        metrics = self._calculate_graph_metrics(graph)

        # Find connected components
        components = self._find_connected_components(graph)

        # Analyze relationship patterns
        patterns = self._analyze_relationship_patterns(graph)

        # Find circular dependencies
        cycles = self._find_cycles(graph, max_depth)

        results = {
            "summary": metrics,
            "components": {
                "count": len(components),
                "sizes": [len(c) for c in components[:10]],  # Top 10
                "largest_component": len(components[0]) if components else 0,
            },
            "patterns": patterns,
            "cycles": {
                "found": len(cycles) > 0,
                "count": len(cycles),
                "examples": cycles[:5],  # First 5 cycles
            },
        }

        if include_orphans:
            orphans = await self._find_orphaned_documents(graph)
            results["orphans"] = {
                "count": len(orphans),
                "document_ids": orphans[:20],  # First 20
            }

        return results

    async def _build_relationship_graph(
        self, relationship_types: list[str] | None = None
    ) -> dict[str, list[tuple[str, str]]]:
        """Build document relationship graph."""
        if self._graph_cache is not None:
            return self._graph_cache

        graph = defaultdict(list)

        # Scan relationships
        scanner = self.dataset.scanner(columns=["id", "relationships"])

        for batch in scanner.to_batches():
            ids = batch.column("id").to_pylist()
            relationships_list = batch.column("relationships").to_pylist()

            for doc_id, relationships in zip(ids, relationships_list, strict=False):
                if relationships:
                    for rel in relationships:
                        if isinstance(rel, dict):
                            rel_type = rel.get("type", "unknown")
                            target = rel.get("target")

                            if (
                                relationship_types is None
                                or rel_type in relationship_types
                            ):
                                if target:
                                    graph[doc_id].append((rel_type, target))

        self._graph_cache = dict(graph)
        return self._graph_cache

    def _calculate_graph_metrics(
        self, graph: dict[str, list[tuple[str, str]]]
    ) -> dict[str, Any]:
        """Calculate basic graph metrics."""
        nodes = set(graph.keys())
        all_targets = set()
        edge_count = 0

        for edges in graph.values():
            edge_count += len(edges)
            all_targets.update(target for _, target in edges)

        nodes.update(all_targets)

        # Degree distribution
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)

        for source, edges in graph.items():
            out_degree[source] = len(edges)
            for _, target in edges:
                in_degree[target] += 1

        degrees = list(out_degree.values()) + [0] * (len(nodes) - len(out_degree))

        return {
            "node_count": len(nodes),
            "edge_count": edge_count,
            "avg_degree": round(edge_count / len(nodes) if nodes else 0, 2),
            "max_out_degree": max(out_degree.values()) if out_degree else 0,
            "max_in_degree": max(in_degree.values()) if in_degree else 0,
            "degree_distribution": {
                "mean": round(np.mean(degrees), 2),
                "median": round(np.median(degrees), 2),
                "std": round(np.std(degrees), 2),
            },
        }

    def _find_connected_components(
        self, graph: dict[str, list[tuple[str, str]]]
    ) -> list[set[str]]:
        """Find connected components using DFS."""
        # Build undirected adjacency list
        adjacency = defaultdict(set)
        all_nodes = set(graph.keys())

        for source, edges in graph.items():
            for _, target in edges:
                adjacency[source].add(target)
                adjacency[target].add(source)
                all_nodes.add(target)

        # DFS to find components
        visited = set()
        components = []

        for node in all_nodes:
            if node not in visited:
                component = set()
                stack = [node]

                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.add(current)
                        stack.extend(adjacency[current] - visited)

                components.append(component)

        # Sort by size (largest first)
        components.sort(key=len, reverse=True)

        return components

    def _analyze_relationship_patterns(
        self, graph: dict[str, list[tuple[str, str]]]
    ) -> dict[str, Any]:
        """Analyze patterns in relationships."""
        type_counts = defaultdict(int)
        type_pairs = defaultdict(int)

        for edges in graph.values():
            for rel_type, _ in edges:
                type_counts[rel_type] += 1

            # Count type pairs
            edge_types = [rel_type for rel_type, _ in edges]
            for i, type1 in enumerate(edge_types):
                for type2 in edge_types[i + 1 :]:
                    pair = tuple(sorted([type1, type2]))
                    type_pairs[pair] += 1

        return {
            "type_distribution": dict(type_counts),
            "common_pairs": [
                {"types": list(pair), "count": count}
                for pair, count in sorted(
                    type_pairs.items(), key=lambda x: x[1], reverse=True
                )[:5]
            ],
        }

    def _find_cycles(
        self, graph: dict[str, list[tuple[str, str]]], max_depth: int
    ) -> list[list[str]]:
        """Find cycles in the relationship graph."""
        cycles = []

        def dfs(node: str, path: list[str], visited: set[str]) -> None:
            if len(path) > max_depth:
                return

            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if len(cycle) > 2:  # Ignore self-loops
                    cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for _, target in graph.get(node, []):
                dfs(target, path.copy(), visited.copy())

        # Start DFS from each node
        for start_node in graph:
            dfs(start_node, [], set())
            if len(cycles) >= 10:  # Limit cycles found
                break

        return cycles

    async def _find_orphaned_documents(
        self, graph: dict[str, list[tuple[str, str]]]
    ) -> list[str]:
        """Find documents with no relationships."""
        # Get all documents
        all_docs = set()
        scanner = self.dataset.scanner(columns=["id"], limit=10000)

        for batch in scanner.to_batches():
            all_docs.update(batch.column("id").to_pylist())

        # Find connected documents
        connected = set(graph.keys())
        for edges in graph.values():
            connected.update(target for _, target in edges)

        # Orphans are documents not in the graph
        orphans = list(all_docs - connected)

        return orphans[:100]  # Return first 100
