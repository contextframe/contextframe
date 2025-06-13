"""
Semantic Chunking Demo

This example demonstrates the benefits of using semantic-text-splitter
over simple character-based chunking.

Requirements:
    pip install contextframe[extract]
"""

from contextframe.extract.chunking import semantic_splitter, ChunkingMixin


def compare_chunking_methods():
    """Compare different chunking approaches."""
    
    # Sample markdown text with structure
    markdown_text = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on building applications that learn from data and improve their accuracy over time without being programmed to do so.

## Types of Machine Learning

There are three main types of machine learning:

### Supervised Learning
In supervised learning, the algorithm learns from labeled training data. Each training example consists of an input and the desired output. Common algorithms include:
- Linear Regression
- Decision Trees
- Support Vector Machines

### Unsupervised Learning
Unsupervised learning works with unlabeled data. The algorithm tries to find patterns and relationships in the data without explicit guidance. Examples include:
- K-means clustering
- Principal Component Analysis
- Autoencoders

### Reinforcement Learning
In reinforcement learning, an agent learns to make decisions by performing actions and receiving rewards or penalties. This approach is used in:
- Game playing (Chess, Go)
- Robotics
- Autonomous vehicles

## Conclusion

Machine learning continues to evolve and find new applications across industries."""

    print("=" * 80)
    print("SEMANTIC CHUNKING DEMO")
    print("=" * 80)
    
    # 1. Character-based chunking
    print("\n1. CHARACTER-BASED CHUNKING (300 chars)")
    print("-" * 40)
    
    char_chunks = semantic_splitter(
        [markdown_text],
        chunk_size=300,
        splitter_type="text",  # Plain text mode
    )
    
    for i, (_, chunk) in enumerate(char_chunks):
        print(f"\nChunk {i + 1}:")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)
    
    # 2. Semantic markdown chunking
    print("\n\n2. SEMANTIC MARKDOWN CHUNKING (300 chars)")
    print("-" * 40)
    
    md_chunks = semantic_splitter(
        [markdown_text],
        chunk_size=300,
        splitter_type="markdown",  # Markdown-aware
    )
    
    for i, (_, chunk) in enumerate(md_chunks):
        print(f"\nChunk {i + 1}:")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)
    
    # Show the difference
    print("\n\n" + "=" * 80)
    print("KEY DIFFERENCES:")
    print("- Character-based: Splits mid-sentence, loses structure")
    print("- Semantic markdown: Preserves headers, lists, paragraphs")
    print("- Semantic chunking maintains context and readability")


def token_based_chunking_example():
    """Demonstrate token-based chunking for LLM compatibility."""
    
    text = """
    Natural language processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and humans through natural language. The ultimate objective of NLP is to enable computers to understand, interpret, and generate human language in a way that is both meaningful and useful.
    
    Key applications of NLP include:
    - Machine translation: Converting text from one language to another
    - Sentiment analysis: Determining the emotional tone of text
    - Named entity recognition: Identifying people, places, and organizations
    - Text summarization: Creating concise summaries of longer documents
    """
    
    print("\n\n" + "=" * 80)
    print("TOKEN-BASED CHUNKING (for LLMs)")
    print("=" * 80)
    
    # Token-based chunking with GPT tokenizer
    token_chunks = semantic_splitter(
        [text],
        chunk_size=50,  # 50 tokens
        tokenizer_model="gpt-3.5-turbo",
    )
    
    print(f"\nUsing GPT-3.5 tokenizer (50 tokens per chunk):")
    for i, (_, chunk) in enumerate(token_chunks):
        print(f"\nChunk {i + 1}:")
        print(chunk)


def code_splitting_example():
    """Demonstrate code-aware splitting."""
    
    python_code = '''def process_data(input_file, output_file):
    """Process data from input file and save to output file."""
    # Read the input data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Process each record
    results = []
    for record in data:
        if validate_record(record):
            processed = transform_record(record)
            results.append(processed)
    
    # Save the results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return len(results)


def validate_record(record):
    """Validate a single record."""
    required_fields = ['id', 'name', 'value']
    return all(field in record for field in required_fields)


def transform_record(record):
    """Transform a record to the output format."""
    return {
        'id': record['id'],
        'display_name': record['name'].upper(),
        'normalized_value': record['value'] / 100
    }
'''

    print("\n\n" + "=" * 80)
    print("CODE-AWARE SPLITTING")
    print("=" * 80)
    
    try:
        # This requires tree-sitter-python to be installed
        code_chunks = semantic_splitter(
            [python_code],
            chunk_size=200,
            splitter_type="code",
            language="python",
        )
        
        print(f"\nPython code split into semantic chunks:")
        for i, (_, chunk) in enumerate(code_chunks):
            print(f"\nChunk {i + 1}:")
            print(chunk)
            print("-" * 40)
    except ImportError:
        print("\nCode splitting requires tree-sitter-python:")
        print("pip install tree-sitter-python")
        
        # Fall back to text splitting
        print("\nFalling back to text-based splitting:")
        text_chunks = semantic_splitter(
            [python_code],
            chunk_size=200,
            splitter_type="text",
        )
        
        for i, (_, chunk) in enumerate(text_chunks):
            print(f"\nChunk {i + 1}:")
            print(chunk[:100] + "..." if len(chunk) > 100 else chunk)


def range_based_chunking():
    """Demonstrate range-based chunk sizing."""
    
    text = "This is a sentence. " * 50  # Repetitive text
    
    print("\n\n" + "=" * 80)
    print("RANGE-BASED CHUNKING")
    print("=" * 80)
    
    # Note: semantic-text-splitter supports range-based sizing
    # by creating the splitter with a tuple
    from semantic_text_splitter import TextSplitter
    
    # Chunks will be between 100-200 characters
    splitter = TextSplitter((100, 200))
    chunks = splitter.chunks(text)
    
    print(f"\nChunks sized between 100-200 characters:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1} ({len(chunk)} chars):")
        print(chunk)


if __name__ == "__main__":
    # Run all examples
    compare_chunking_methods()
    token_based_chunking_example()
    code_splitting_example()
    range_based_chunking()
    
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
The semantic-text-splitter provides:
1. Semantic awareness - respects document structure
2. Multiple splitting strategies - text, markdown, code
3. Token-based splitting - for LLM compatibility
4. High performance - Rust implementation
5. Flexible sizing - character, token, or custom callbacks

This results in better chunks for:
- RAG applications
- LLM context windows
- Document processing pipelines
""")