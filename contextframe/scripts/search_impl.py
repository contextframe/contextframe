#!/usr/bin/env python3
"""Implementation of contextframe-search command."""

import argparse
import sys
from pathlib import Path
from typing import Optional

import numpy as np

from contextframe.frame import FrameDataset
from contextframe.embed import LiteLLMProvider


def search_hybrid(dataset: FrameDataset, query: str, limit: int, filter_expr: Optional[str] = None) -> list:
    """Perform hybrid search using both vector and text search."""
    # Try vector search first if embeddings are available
    try:
        # Get embedding configuration from environment or use defaults
        import os
        model = os.environ.get("CONTEXTFRAME_EMBED_MODEL", "text-embedding-ada-002")
        
        # Create embedding provider
        provider = LiteLLMProvider(model)
        
        # Generate query embedding
        result = provider.embed(query)
        query_vector = np.array(result.embeddings[0], dtype=np.float32)
        
        # Perform vector search
        vector_results = dataset.knn_search(
            query_vector=query_vector,
            k=limit,
            filter=filter_expr
        )
        
        # If we got results, return them
        if vector_results:
            return vector_results
            
    except Exception as e:
        # Fall back to text search if vector search fails
        print(f"Vector search unavailable: {e}", file=sys.stderr)
    
    # Fall back to text search
    return dataset.full_text_search(
        query=query,
        limit=limit,
        filter=filter_expr
    )


def search_vector(dataset: FrameDataset, query: str, limit: int, filter_expr: Optional[str] = None) -> list:
    """Perform vector search using embeddings."""
    # Get embedding configuration from environment or use defaults
    import os
    model = os.environ.get("CONTEXTFRAME_EMBED_MODEL", "text-embedding-ada-002")
    api_key = os.environ.get("OPENAI_API_KEY")  # or other provider keys
    
    # Create embedding provider
    provider = LiteLLMProvider(model, api_key=api_key)
    
    # Generate query embedding
    try:
        result = provider.embed(query)
        query_vector = np.array(result.embeddings[0], dtype=np.float32)
    except Exception as e:
        print(f"Error generating embedding: {e}", file=sys.stderr)
        print("Make sure you have set up API credentials for your embedding provider.", file=sys.stderr)
        print("For OpenAI: export OPENAI_API_KEY='your-key'", file=sys.stderr)
        print("For other providers, see: https://docs.litellm.ai/docs/providers", file=sys.stderr)
        sys.exit(1)
    
    # Perform vector search
    return dataset.knn_search(
        query_vector=query_vector,
        k=limit,
        filter=filter_expr
    )


def search_text(dataset: FrameDataset, query: str, limit: int, filter_expr: Optional[str] = None) -> list:
    """Perform text search."""
    return dataset.full_text_search(
        query=query,
        limit=limit,
        filter=filter_expr
    )


def format_result(record, index: int):
    """Format a single search result for display."""
    print(f"\n{'='*60}")
    print(f"Result {index + 1}:")
    print(f"ID: {record.metadata.get('identifier', 'N/A')}")
    print(f"Type: {record.metadata.get('record_type', 'document')}")
    
    # Show title if available
    if 'title' in record.metadata:
        print(f"Title: {record.metadata['title']}")
    
    # Show collection if part of one
    relationships = record.metadata.get('relationships', [])
    for rel in relationships:
        if rel.get('relationship_type') == 'member_of' and rel.get('target_type') == 'collection':
            print(f"Collection: {rel.get('target_identifier', 'Unknown')}")
    
    # Show snippet of content
    content = record.text_content
    if len(content) > 200:
        content = content[:200] + "..."
    print(f"\nContent:\n{content}")
    
    # Show custom metadata if present
    if 'custom_metadata' in record.metadata and record.metadata['custom_metadata']:
        print(f"\nCustom Metadata:")
        for key, value in record.metadata['custom_metadata'].items():
            print(f"  {key}: {value}")


def main():
    """Main entry point for search command."""
    parser = argparse.ArgumentParser(description='Search documents in a ContextFrame dataset')
    parser.add_argument('dataset', help='Path to the dataset')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--limit', type=int, default=10, help='Number of results to return')
    parser.add_argument('--type', choices=['vector', 'text', 'hybrid'], default='hybrid',
                        help='Search type')
    parser.add_argument('--filter', dest='filter_expr', help='Lance SQL filter expression')
    
    args = parser.parse_args()
    
    # Open the dataset
    try:
        dataset = FrameDataset.open(args.dataset)
    except Exception as e:
        print(f"Error opening dataset: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Perform search based on type
    try:
        if args.type == 'vector':
            results = search_vector(dataset, args.query, args.limit, args.filter_expr)
        elif args.type == 'text':
            results = search_text(dataset, args.query, args.limit, args.filter_expr)
        else:  # hybrid
            results = search_hybrid(dataset, args.query, args.limit, args.filter_expr)
    except Exception as e:
        print(f"Error performing search: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Display results
    if not results:
        print("No results found.")
    else:
        print(f"Found {len(results)} results:")
        for i, record in enumerate(results):
            format_result(record, i)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())