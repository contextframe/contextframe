"""
Document Enrichment Demo

This example demonstrates how to use ContextFrame's LLM-powered enrichment
to automatically populate schema fields with meaningful metadata.

Requirements:
    pip install contextframe[embed,extract]
    export OPENAI_API_KEY="your-key"  # Or use any LiteLLM-supported model
"""

import os
from pathlib import Path
from contextframe import FrameDataset, FrameRecord
from contextframe.enrich import (
    ContextEnricher,
    get_prompt_template,
    list_available_prompts,
)
from contextframe.embed import embed_frames


def basic_enrichment_example():
    """Show basic enrichment of context and tags."""
    print("\n=== Basic Enrichment Example ===\n")
    
    # Create sample documents
    frames = [
        FrameRecord(
            uri="rag_guide.md",
            title="Building RAG Applications",
            text_content="""
            Retrieval-Augmented Generation (RAG) combines the power of large language models
            with external knowledge retrieval. Key components include:
            - Document chunking and embedding
            - Vector database for similarity search
            - Prompt engineering for context injection
            - Response generation with citations
            """,
        ),
        FrameRecord(
            uri="vector_search.py",
            title="Vector Search Implementation",
            text_content="""
            def cosine_similarity(vec1, vec2):
                dot_product = np.dot(vec1, vec2)
                norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
                return dot_product / norm_product
            
            class VectorIndex:
                def search(self, query_vec, k=10):
                    similarities = [cosine_similarity(query_vec, doc_vec) 
                                  for doc_vec in self.vectors]
                    return sorted(similarities, reverse=True)[:k]
            """,
        ),
    ]
    
    # Create dataset
    dataset = FrameDataset.create("enrichment_demo.lance", exist_ok=True)
    
    # Add frames with embeddings
    embedded_frames = embed_frames(frames, model="openai/text-embedding-3-small")
    dataset.add_many(embedded_frames)
    
    # Enrich with context and tags
    dataset.enrich({
        "context": "Explain in 2-3 sentences what this document teaches and why it matters for AI developers",
        "tags": "Extract 5-7 technical tags covering languages, concepts, and tools mentioned",
    })
    
    # Show results
    for frame in dataset.iter_records():
        print(f"Document: {frame.title}")
        print(f"Context: {frame.context}")
        print(f"Tags: {', '.join(frame.tags or [])}")
        print()


def custom_metadata_example():
    """Show extraction of custom metadata using prompts."""
    print("\n=== Custom Metadata Extraction ===\n")
    
    # Create a code documentation frame
    frame = FrameRecord(
        uri="api_docs.md",
        title="Authentication API Reference",
        text_content="""
        ## POST /api/auth/login
        
        Authenticates a user and returns a JWT token.
        
        **Rate Limit:** 5 requests per minute per IP
        
        **Request Body:**
        ```json
        {
            "email": "user@example.com",
            "password": "secure_password"
        }
        ```
        
        **Response:**
        ```json
        {
            "token": "eyJ...",
            "expires_in": 3600,
            "user": {
                "id": "123",
                "email": "user@example.com",
                "role": "user"
            }
        }
        ```
        
        **Error Codes:**
        - 401: Invalid credentials
        - 429: Rate limit exceeded
        - 500: Server error
        """,
    )
    
    dataset = FrameDataset.create("metadata_demo.lance", exist_ok=True)
    embedded = embed_frames([frame], model="openai/text-embedding-3-small")[0]
    dataset.add(embedded)
    
    # Extract API metadata
    enricher = ContextEnricher()
    enricher.enrich_dataset(
        dataset,
        enrichments={
            "custom_metadata": {
                "prompt": """
                Extract the following API information as JSON:
                - endpoint (URL path)
                - method (HTTP method)
                - rate_limit (as string)
                - authentication_type
                - response_fields (list of field names in response)
                - error_codes (object mapping code to description)
                """,
                "format": "json"
            }
        }
    )
    
    # Show extracted metadata
    record = list(dataset.iter_records())[0]
    print(f"Document: {record.title}")
    print("Extracted Metadata:")
    for key, value in (record.custom_metadata or {}).items():
        print(f"  {key}: {value}")


def relationship_discovery_example():
    """Show how to find relationships between documents."""
    print("\n=== Relationship Discovery ===\n")
    
    # Create related documents
    frames = [
        FrameRecord(
            uri="llm_basics.md",
            title="Introduction to Large Language Models",
            text_content="LLMs are neural networks trained on vast text corpora...",
        ),
        FrameRecord(
            uri="fine_tuning.md",
            title="Fine-Tuning LLMs for Specific Tasks",
            text_content="Fine-tuning adapts pre-trained LLMs to specific domains...",
        ),
        FrameRecord(
            uri="prompt_engineering.md",
            title="Prompt Engineering Best Practices",
            text_content="Effective prompts are crucial for LLM performance...",
        ),
    ]
    
    dataset = FrameDataset.create("relationships_demo.lance", exist_ok=True)
    embedded = embed_frames(frames, model="openai/text-embedding-3-small")
    dataset.add_many(embedded)
    
    enricher = ContextEnricher()
    
    # Find relationships between documents
    for i, source in enumerate(embedded):
        # Get other documents as candidates
        candidates = [f for j, f in enumerate(embedded) if i != j]
        
        relationships = enricher.find_relationships(
            source_doc=source,
            candidate_docs=candidates,
            prompt=get_prompt_template("relationships", "topic_relationships")
        )
        
        # Update the frame with relationships
        source.relationships = relationships
        dataset.update_record(source)
    
    # Display relationships
    for frame in dataset.iter_records():
        print(f"\nDocument: {frame.title}")
        if frame.relationships:
            print("Relationships:")
            for rel in frame.relationships:
                print(f"  - {rel['type']}: {rel['title']}")
                print(f"    {rel.get('description', '')}")


def mcp_tool_example():
    """Show how agents can use enrichment as tools."""
    print("\n=== MCP Tool Interface Example ===\n")
    
    from contextframe.enrich import EnrichmentTools, list_available_tools
    
    # Create enricher and tools
    enricher = ContextEnricher()
    tools = EnrichmentTools(enricher)
    
    # Show available tools
    print("Available enrichment tools:")
    for tool_name in list_available_tools():
        print(f"  - {tool_name}")
    
    # Example: Agent using the enrich_context tool
    content = """
    FastAPI is a modern web framework for building APIs with Python 3.7+
    based on standard Python type hints. It's designed to be easy to use
    while providing high performance through Starlette and Pydantic.
    """
    
    # Agent calls the tool
    context = tools.enrich_context(
        content=content,
        purpose="building REST APIs with Python"
    )
    
    print(f"\nGenerated context: {context}")
    
    # Extract metadata tool
    metadata = tools.extract_metadata(
        content=content,
        schema="Extract: framework_name, python_version, key_dependencies, main_features"
    )
    
    print(f"\nExtracted metadata: {metadata}")


def template_showcase():
    """Show available prompt templates."""
    print("\n=== Available Prompt Templates ===\n")
    
    templates = list_available_prompts()
    
    for category, template_names in templates.items():
        print(f"{category.upper()}:")
        for name in template_names:
            print(f"  - {name}")
    
    # Example using a template
    print("\n\nExample template (technical_context):")
    template = get_prompt_template("context", "technical_context")
    print(template[:200] + "...")


def purpose_driven_enrichment():
    """Show enrichment for specific purposes."""
    print("\n=== Purpose-Driven Enrichment ===\n")
    
    # Document about testing
    frame = FrameRecord(
        uri="testing_guide.md",
        title="Python Testing with pytest",
        text_content="""
        pytest is a testing framework that makes it easy to write small,
        readable tests, and can scale to support complex functional testing.
        
        Key features:
        - Simple assertion syntax
        - Fixture support for setup/teardown
        - Parametrized testing
        - Plugin architecture
        
        Example test:
        def test_addition():
            assert 1 + 1 == 2
        """,
    )
    
    dataset = FrameDataset.create("purpose_demo.lance", exist_ok=True)
    embedded = embed_frames([frame], model="openai/text-embedding-3-small")[0]
    dataset.add(embedded)
    
    # Enrich for different purposes
    enricher = ContextEnricher()
    
    # For RAG system
    rag_prompt = get_prompt_template("purpose", "rag_optimization")
    enricher.enrich_dataset(
        dataset,
        enrichments={
            "context": rag_prompt.split("CONTEXT:")[1].split("2.")[0].strip(),
            "tags": rag_prompt.split("TAGS:")[1].split("3.")[0].strip(),
            "custom_metadata": {
                "prompt": rag_prompt.split("METADATA:")[1].strip(),
                "format": "json"
            }
        }
    )
    
    # Show enriched document
    record = list(dataset.iter_records())[0]
    print(f"Document: {record.title}")
    print(f"RAG Context: {record.context}")
    print(f"Tags: {', '.join(record.tags or [])}")
    print(f"Metadata: {record.custom_metadata}")


def main():
    """Run all examples."""
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        print("Or modify examples to use a different model (e.g., ollama/mistral)")
        return
    
    examples = [
        ("Basic Enrichment", basic_enrichment_example),
        ("Custom Metadata", custom_metadata_example),
        ("Relationship Discovery", relationship_discovery_example),
        ("MCP Tool Interface", mcp_tool_example),
        ("Template Showcase", template_showcase),
        ("Purpose-Driven", purpose_driven_enrichment),
    ]
    
    for name, func in examples:
        print(f"\n{'='*60}")
        print(f" {name}")
        print(f"{'='*60}")
        try:
            func()
        except Exception as e:
            print(f"Error in {name}: {e}")
    
    # Cleanup
    print("\n\nCleaning up demo datasets...")
    for lance_dir in Path(".").glob("*_demo.lance"):
        import shutil
        shutil.rmtree(lance_dir)
    
    print("\nDemo complete!")


if __name__ == "__main__":
    main()