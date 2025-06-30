# Multi-Source Search

Build a unified search interface that queries multiple data sources simultaneously, ranks results intelligently, and provides faceted search capabilities across diverse content types.

## Problem Statement

Organizations have information scattered across multiple systems - documentation in GitHub, tasks in Linear, files in Google Drive, conversations in Slack. Users need a single search interface that can find information regardless of where it's stored.

## Solution Overview

We'll build a multi-source search system that:
1. Queries multiple ContextFrame datasets in parallel
2. Implements intelligent result ranking
3. Provides faceted search and filtering
4. Offers search analytics and suggestions
5. Handles different content types appropriately

## Complete Code

```python
import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

from contextframe import FrameDataset, FrameRecord
from contextframe.connectors import (
    GitHubConnector,
    LinearConnector,
    SlackConnector,
    NotionConnector,
    GoogleDriveConnector
)

@dataclass
class SearchResult:
    """Unified search result structure."""
    content: str
    title: str
    source: str
    source_type: str
    url: Optional[str]
    score: float
    metadata: Dict[str, Any]
    snippet: str
    unique_id: str
    timestamp: str

class MultiSourceSearch:
    """Unified search across multiple data sources."""
    
    def __init__(self):
        """Initialize search system with multiple datasets."""
        self.sources = {
            "github": {
                "dataset": FrameDataset("github_data.lance"),
                "weight": 1.0,
                "display_name": "GitHub"
            },
            "linear": {
                "dataset": FrameDataset("linear_data.lance"),
                "weight": 1.2,  # Boost current tasks
                "display_name": "Linear"
            },
            "slack": {
                "dataset": FrameDataset("slack_data.lance"),
                "weight": 0.8,
                "display_name": "Slack"
            },
            "notion": {
                "dataset": FrameDataset("notion_data.lance"),
                "weight": 1.1,
                "display_name": "Notion"
            },
            "gdrive": {
                "dataset": FrameDataset("gdrive_data.lance"),
                "weight": 1.0,
                "display_name": "Google Drive"
            }
        }
        
        # Search history for suggestions
        self.search_history = []
        self.click_history = defaultdict(int)
        
    def search(self, 
               query: str,
               sources: Optional[List[str]] = None,
               filters: Optional[Dict[str, Any]] = None,
               limit: int = 20,
               offset: int = 0) -> Dict[str, Any]:
        """Perform multi-source search."""
        
        # Use all sources if none specified
        if not sources:
            sources = list(self.sources.keys())
        
        # Search each source in parallel
        all_results = self._parallel_search(query, sources, filters)
        
        # Rank results
        ranked_results = self._rank_results(all_results, query)
        
        # Apply pagination
        paginated = ranked_results[offset:offset + limit]
        
        # Generate facets
        facets = self._generate_facets(ranked_results)
        
        # Track search
        self._track_search(query, len(ranked_results))
        
        # Format response
        return {
            "query": query,
            "total": len(ranked_results),
            "results": [self._format_result(r) for r in paginated],
            "facets": facets,
            "suggestions": self._get_suggestions(query),
            "offset": offset,
            "limit": limit
        }
    
    def _parallel_search(self, 
                        query: str,
                        sources: List[str],
                        filters: Optional[Dict[str, Any]]) -> List[Tuple[Any, str, float]]:
        """Search multiple sources in parallel."""
        all_results = []
        
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            futures = {}
            
            for source in sources:
                if source in self.sources:
                    future = executor.submit(
                        self._search_source,
                        source,
                        query,
                        filters
                    )
                    futures[future] = source
            
            for future in as_completed(futures):
                source = futures[future]
                try:
                    results = future.result()
                    weight = self.sources[source]["weight"]
                    
                    # Add source info and apply weight
                    for result in results:
                        all_results.append((result, source, weight))
                        
                except Exception as e:
                    print(f"Error searching {source}: {e}")
        
        return all_results
    
    def _search_source(self,
                      source: str,
                      query: str,
                      filters: Optional[Dict[str, Any]]) -> List[Any]:
        """Search a single source."""
        dataset = self.sources[source]["dataset"]
        
        # Build source-specific filter
        filter_str = self._build_filter(source, filters) if filters else None
        
        # Perform search
        results = dataset.search(
            query=query,
            limit=50,  # Get more for better ranking
            filter=filter_str
        )
        
        return results
    
    def _build_filter(self, source: str, filters: Dict[str, Any]) -> str:
        """Build source-specific filter string."""
        conditions = []
        
        # Common filters
        if "date_from" in filters:
            conditions.append(f"metadata.created_at >= '{filters['date_from']}'")
        
        if "date_to" in filters:
            conditions.append(f"metadata.created_at <= '{filters['date_to']}'")
        
        # Source-specific filters
        if source == "github":
            if "repo" in filters:
                conditions.append(f"metadata.repository = '{filters['repo']}'")
            if "type" in filters:
                conditions.append(f"metadata.type = '{filters['type']}'")
                
        elif source == "linear":
            if "status" in filters:
                conditions.append(f"metadata.state = '{filters['status']}'")
            if "assignee" in filters:
                conditions.append(f"metadata.assignee = '{filters['assignee']}'")
                
        elif source == "slack":
            if "channel" in filters:
                conditions.append(f"metadata.channel = '{filters['channel']}'")
            if "user" in filters:
                conditions.append(f"metadata.user = '{filters['user']}'")
        
        return " AND ".join(conditions) if conditions else None
    
    def _rank_results(self, 
                     results: List[Tuple[Any, str, float]], 
                     query: str) -> List[Tuple[Any, str, float]]:
        """Rank results using multiple signals."""
        scored_results = []
        
        for result, source, weight in results:
            # Base score from vector similarity
            base_score = result.score
            
            # Apply source weight
            score = base_score * weight
            
            # Boost exact matches
            if query.lower() in result.text_content.lower():
                score *= 1.5
            
            # Boost title matches
            title = result.metadata.get("title", "")
            if query.lower() in title.lower():
                score *= 2.0
            
            # Recency boost
            timestamp = result.metadata.get("created_at", result.timestamp)
            if timestamp:
                try:
                    created = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    age_days = (datetime.now() - created).days
                    recency_boost = 1.0 / (1.0 + age_days / 30)  # Decay over 30 days
                    score *= (1 + recency_boost * 0.3)  # Up to 30% boost
                except:
                    pass
            
            # Click-through rate boost
            ctr_boost = self.click_history.get(result.unique_id, 0) * 0.1
            score *= (1 + ctr_boost)
            
            scored_results.append((result, source, score))
        
        # Sort by score descending
        scored_results.sort(key=lambda x: x[2], reverse=True)
        
        # Remove near-duplicates
        filtered = self._remove_duplicates(scored_results)
        
        return filtered
    
    def _remove_duplicates(self, 
                          results: List[Tuple[Any, str, float]],
                          threshold: float = 0.9) -> List[Tuple[Any, str, float]]:
        """Remove near-duplicate results."""
        filtered = []
        seen_content = []
        
        for result, source, score in results:
            # Simple duplicate detection using content similarity
            is_duplicate = False
            
            for seen in seen_content:
                similarity = self._text_similarity(
                    result.text_content[:500],
                    seen[:500]
                )
                if similarity > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append((result, source, score))
                seen_content.append(result.text_content)
        
        return filtered
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        # Tokenize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0
    
    def _generate_facets(self, results: List[Tuple[Any, str, float]]) -> Dict[str, Any]:
        """Generate search facets for filtering."""
        facets = {
            "sources": defaultdict(int),
            "types": defaultdict(int),
            "dates": defaultdict(int),
            "authors": defaultdict(int),
            "tags": defaultdict(int)
        }
        
        for result, source, _ in results:
            # Source facet
            facets["sources"][self.sources[source]["display_name"]] += 1
            
            # Type facet
            doc_type = result.metadata.get("type") or result.record_type
            facets["types"][doc_type] += 1
            
            # Date facet (by month)
            timestamp = result.metadata.get("created_at", result.timestamp)
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    month_key = date.strftime("%Y-%m")
                    facets["dates"][month_key] += 1
                except:
                    pass
            
            # Author facet
            author = result.metadata.get("author") or result.metadata.get("user")
            if author:
                facets["authors"][author] += 1
            
            # Tags facet
            tags = result.metadata.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    facets["tags"][tag] += 1
        
        # Convert to sorted lists
        return {
            facet: sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for facet, counts in facets.items()
        }
    
    def _format_result(self, result_tuple: Tuple[Any, str, float]) -> Dict[str, Any]:
        """Format result for API response."""
        result, source, score = result_tuple
        
        # Generate snippet
        snippet = self._generate_snippet(result.text_content, self.last_query)
        
        # Build URL
        url = self._build_url(result, source)
        
        return {
            "title": result.metadata.get("title", "Untitled"),
            "content": result.text_content[:500],
            "snippet": snippet,
            "source": self.sources[source]["display_name"],
            "source_type": source,
            "url": url,
            "score": float(score),
            "metadata": {
                k: v for k, v in result.metadata.items()
                if not k.startswith("_") and isinstance(v, (str, int, float, bool))
            },
            "unique_id": result.unique_id,
            "timestamp": result.timestamp
        }
    
    def _generate_snippet(self, content: str, query: str, context_chars: int = 150) -> str:
        """Generate snippet with query highlighting."""
        # Find query in content (case-insensitive)
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        match = pattern.search(content)
        
        if match:
            start = max(0, match.start() - context_chars)
            end = min(len(content), match.end() + context_chars)
            snippet = content[start:end]
            
            # Add ellipsis
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
            
            # Highlight query
            snippet = pattern.sub(f"**{match.group()}**", snippet)
            
            return snippet
        else:
            # Return beginning of content
            return content[:context_chars * 2] + "..."
    
    def _build_url(self, result: Any, source: str) -> Optional[str]:
        """Build source-specific URL."""
        if source == "github":
            repo = result.metadata.get("repository")
            if repo and result.metadata.get("number"):
                return f"https://github.com/{repo}/issues/{result.metadata['number']}"
                
        elif source == "linear":
            return result.metadata.get("url")
            
        elif source == "slack":
            return result.metadata.get("permalink")
            
        elif source == "notion":
            return result.metadata.get("url")
            
        elif source == "gdrive":
            return result.metadata.get("webViewLink")
        
        return None
    
    def _track_search(self, query: str, result_count: int):
        """Track search for analytics."""
        self.search_history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "result_count": result_count
        })
        self.last_query = query
        
        # Keep last 1000 searches
        if len(self.search_history) > 1000:
            self.search_history = self.search_history[-1000:]
    
    def track_click(self, unique_id: str):
        """Track click on result."""
        self.click_history[unique_id] += 1
    
    def _get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions."""
        suggestions = []
        
        # Previous queries that start with current query
        query_lower = query.lower()
        for history in self.search_history[-100:]:
            hist_query = history["query"]
            if hist_query.lower().startswith(query_lower) and hist_query != query:
                suggestions.append(hist_query)
        
        # Most common queries containing the terms
        query_terms = set(query.lower().split())
        related = []
        
        for history in self.search_history[-200:]:
            hist_terms = set(history["query"].lower().split())
            if query_terms & hist_terms and history["query"] != query:
                related.append(history["query"])
        
        # Combine and deduplicate
        all_suggestions = list(dict.fromkeys(suggestions + related))
        
        return all_suggestions[:5]
    
    def get_trending(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get trending search terms."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_queries = [
            h["query"] for h in self.search_history
            if datetime.fromisoformat(h["timestamp"]) > cutoff
        ]
        
        # Count query frequency
        query_counts = Counter(recent_queries)
        
        # Get top trends
        trends = []
        for query, count in query_counts.most_common(10):
            trends.append({
                "query": query,
                "count": count,
                "trend": self._calculate_trend(query)
            })
        
        return trends
    
    def _calculate_trend(self, query: str) -> float:
        """Calculate trend direction for a query."""
        # Compare last 24h to previous 24h
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        
        recent_count = sum(
            1 for h in self.search_history
            if h["query"] == query and 
            datetime.fromisoformat(h["timestamp"]) > day_ago
        )
        
        previous_count = sum(
            1 for h in self.search_history
            if h["query"] == query and 
            two_days_ago < datetime.fromisoformat(h["timestamp"]) <= day_ago
        )
        
        if previous_count == 0:
            return 1.0 if recent_count > 0 else 0.0
        
        return (recent_count - previous_count) / previous_count

# Advanced search features
class AdvancedSearch(MultiSourceSearch):
    """Extended search with advanced features."""
    
    def semantic_search(self, 
                       query: str,
                       context: Optional[str] = None,
                       **kwargs) -> Dict[str, Any]:
        """Semantic search with context understanding."""
        # Expand query with context
        if context:
            expanded_query = f"{context} {query}"
        else:
            expanded_query = query
        
        # Perform search
        results = self.search(expanded_query, **kwargs)
        
        # Re-rank based on semantic similarity
        if results["results"]:
            reranked = self._semantic_rerank(
                query,
                results["results"],
                context
            )
            results["results"] = reranked
        
        return results
    
    def _semantic_rerank(self,
                        query: str,
                        results: List[Dict[str, Any]],
                        context: Optional[str]) -> List[Dict[str, Any]]:
        """Re-rank using semantic similarity."""
        # This would use a more sophisticated model
        # For now, simple keyword boosting
        
        context_terms = set(context.lower().split()) if context else set()
        
        for result in results:
            content_terms = set(result["content"].lower().split())
            
            # Boost results that contain context terms
            context_overlap = len(context_terms & content_terms)
            result["score"] *= (1 + context_overlap * 0.1)
        
        # Re-sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def federated_search(self, 
                        queries: List[str],
                        operator: str = "AND",
                        **kwargs) -> Dict[str, Any]:
        """Search with multiple queries."""
        all_results = []
        
        # Execute each query
        for query in queries:
            results = self.search(query, **kwargs)
            all_results.append(set(r["unique_id"] for r in results["results"]))
        
        # Combine based on operator
        if operator == "AND":
            matching_ids = set.intersection(*all_results) if all_results else set()
        elif operator == "OR":
            matching_ids = set.union(*all_results) if all_results else set()
        else:
            raise ValueError(f"Unknown operator: {operator}")
        
        # Filter original results
        final_results = self.search(queries[0], **kwargs)
        final_results["results"] = [
            r for r in final_results["results"]
            if r["unique_id"] in matching_ids
        ]
        final_results["total"] = len(final_results["results"])
        
        return final_results

# Example usage
if __name__ == "__main__":
    # Initialize search system
    search = AdvancedSearch()
    
    # Basic search
    results = search.search(
        "kubernetes deployment",
        sources=["github", "notion"],
        limit=10
    )
    
    print(f"Found {results['total']} results")
    for result in results["results"]:
        print(f"- {result['title']} ({result['source']}) - Score: {result['score']:.2f}")
    
    # Filtered search
    filtered = search.search(
        "bug fix",
        sources=["github", "linear"],
        filters={
            "date_from": "2024-01-01",
            "type": "issue"
        }
    )
    
    # Semantic search with context
    semantic = search.semantic_search(
        "deployment",
        context="We use kubernetes for container orchestration",
        sources=["notion", "gdrive"]
    )
    
    # Track click
    if results["results"]:
        search.track_click(results["results"][0]["unique_id"])
    
    # Get trending searches
    trends = search.get_trending(hours=24)
    print("\nTrending searches:")
    for trend in trends:
        print(f"- {trend['query']}: {trend['count']} searches (trend: {trend['trend']:+.1%})")
    
    # Faceted results
    print("\nFacets:")
    for facet_name, facet_values in results["facets"].items():
        print(f"\n{facet_name}:")
        for value, count in facet_values[:5]:
            print(f"  - {value}: {count}")
```

## Key Concepts

### 1. Parallel Search
- Searches multiple datasets concurrently
- Thread pool for optimal performance
- Graceful handling of source failures

### 2. Intelligent Ranking
- Source-specific weights
- Exact match boosting
- Recency factors
- Click-through rate learning
- Duplicate detection

### 3. Faceted Search
- Dynamic facet generation
- Source, type, date, author filters
- Tag-based navigation
- Result counts per facet

### 4. Search Analytics
- Query tracking
- Click tracking
- Trending searches
- Suggestion generation

### 5. Result Formatting
- Unified result structure
- Snippet generation with highlighting
- Source-specific URL building
- Metadata preservation

## Extensions

### 1. Query Understanding
```python
class QueryParser:
    """Parse and understand search queries."""
    
    def parse(self, query: str) -> Dict[str, Any]:
        # Extract filters from query
        filters = {}
        clean_query = query
        
        # Date filters
        date_match = re.search(r'after:(\d{4}-\d{2}-\d{2})', query)
        if date_match:
            filters['date_from'] = date_match.group(1)
            clean_query = clean_query.replace(date_match.group(0), '')
        
        # Source filters
        source_match = re.search(r'source:(\w+)', query)
        if source_match:
            filters['source'] = source_match.group(1)
            clean_query = clean_query.replace(source_match.group(0), '')
        
        # Type filters
        type_match = re.search(r'type:(\w+)', query)
        if type_match:
            filters['type'] = type_match.group(1)
            clean_query = clean_query.replace(type_match.group(0), '')
        
        return {
            'query': clean_query.strip(),
            'filters': filters,
            'original': query
        }
```

### 2. Personalization
```python
class PersonalizedSearch(MultiSourceSearch):
    """Search with user personalization."""
    
    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id
        self.user_profile = self._load_user_profile()
    
    def search(self, query: str, **kwargs):
        # Get base results
        results = super().search(query, **kwargs)
        
        # Personalize ranking
        for result in results['results']:
            # Boost based on user interests
            for interest in self.user_profile['interests']:
                if interest.lower() in result['content'].lower():
                    result['score'] *= 1.2
            
            # Boost based on previous interactions
            if result['source_type'] in self.user_profile['preferred_sources']:
                result['score'] *= 1.1
        
        # Re-sort
        results['results'].sort(key=lambda x: x['score'], reverse=True)
        
        return results
```

### 3. Real-time Updates
```python
import asyncio
from typing import AsyncIterator

class RealtimeSearch(MultiSourceSearch):
    """Search with real-time updates."""
    
    async def search_stream(self, 
                          query: str,
                          **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Stream search results as they arrive."""
        
        async def search_source_async(source: str):
            # Simulate async search
            await asyncio.sleep(0.1)
            return self._search_source(source, query, kwargs.get('filters'))
        
        # Create tasks for each source
        tasks = []
        for source in kwargs.get('sources', self.sources.keys()):
            if source in self.sources:
                task = asyncio.create_task(search_source_async(source))
                tasks.append((task, source))
        
        # Yield results as they complete
        for task, source in tasks:
            try:
                results = await task
                for result in results:
                    yield {
                        'result': self._format_result((result, source, result.score)),
                        'source': source,
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                print(f"Error in {source}: {e}")
```

### 4. Search API
```python
from fastapi import FastAPI, Query
from typing import Optional, List

app = FastAPI()
search_engine = MultiSourceSearch()

@app.get("/search")
async def search_api(
    q: str = Query(..., description="Search query"),
    sources: Optional[List[str]] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Multi-source search API."""
    
    filters = {}
    if date_from:
        filters['date_from'] = date_from
    if date_to:
        filters['date_to'] = date_to
    
    results = search_engine.search(
        query=q,
        sources=sources,
        filters=filters,
        limit=limit,
        offset=offset
    )
    
    return results

@app.post("/search/click/{unique_id}")
async def track_click(unique_id: str):
    """Track click on search result."""
    search_engine.track_click(unique_id)
    return {"status": "tracked"}

@app.get("/search/trending")
async def get_trending(hours: int = Query(24, le=168)):
    """Get trending searches."""
    return search_engine.get_trending(hours=hours)

@app.get("/search/suggest")
async def get_suggestions(q: str = Query(..., min_length=2)):
    """Get search suggestions."""
    return search_engine._get_suggestions(q)
```

### 5. Search UI Components
```python
class SearchUI:
    """Generate search UI components."""
    
    @staticmethod
    def generate_search_box() -> str:
        """Generate HTML for search box."""
        return '''
        <div class="search-container">
            <input type="text" 
                   id="search-box" 
                   placeholder="Search across all sources..."
                   autocomplete="off">
            <div id="suggestions" class="suggestions"></div>
            <div class="search-filters">
                <label><input type="checkbox" value="github" checked> GitHub</label>
                <label><input type="checkbox" value="linear" checked> Linear</label>
                <label><input type="checkbox" value="slack" checked> Slack</label>
                <label><input type="checkbox" value="notion" checked> Notion</label>
                <label><input type="checkbox" value="gdrive" checked> Drive</label>
            </div>
        </div>
        '''
    
    @staticmethod
    def generate_results_template() -> str:
        """Generate results display template."""
        return '''
        <div class="search-result">
            <h3><a href="{{ url }}">{{ title }}</a></h3>
            <div class="result-source">{{ source }}</div>
            <div class="result-snippet">{{ snippet }}</div>
            <div class="result-metadata">
                <span class="date">{{ timestamp }}</span>
                <span class="score">Relevance: {{ score }}</span>
            </div>
        </div>
        '''
```

## Best Practices

1. **Performance**: Use parallel search and caching
2. **Ranking**: Continuously refine ranking algorithms
3. **Deduplication**: Remove near-duplicates across sources
4. **Facets**: Generate useful facets dynamically
5. **Analytics**: Track searches to improve results
6. **Error Handling**: Gracefully handle source failures
7. **Security**: Respect source-level permissions

## See Also

- [RAG System](rag-system.md) - Building Q&A on search results
- [GitHub Knowledge Base](github-knowledge-base.md) - Source-specific search
- [API Reference](../api/overview.md) - FrameDataset search methods
- [Search & Query Guide](../modules/search-query.md) - Advanced search techniques