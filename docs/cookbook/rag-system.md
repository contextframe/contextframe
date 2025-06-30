# Building a RAG System

Build a complete Retrieval-Augmented Generation (RAG) system using ContextFrame for document storage and retrieval, combined with LLMs for answer generation.

## Problem Statement

Organizations need to build AI systems that can answer questions based on their internal documentation, knowledge bases, and data sources. A RAG system combines semantic search with LLM generation to provide accurate, grounded responses.

## Solution Overview

We'll build a RAG system that:
1. Ingests documents from multiple sources
2. Generates embeddings for semantic search
3. Retrieves relevant context for queries
4. Uses an LLM to generate answers based on retrieved context
5. Provides citations and confidence scores

## Complete Code

```python
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from contextframe import (
    FrameDataset, 
    FrameRecord, 
    create_metadata,
    generate_uuid
)
from contextframe.connectors import (
    GitHubConnector,
    NotionConnector,
    GoogleDriveConnector
)

class RAGSystem:
    """Complete RAG system built on ContextFrame."""
    
    def __init__(self, dataset_path: str = "rag_knowledge.lance"):
        """Initialize RAG system with dataset."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        self.openai_client = openai.OpenAI()
        
    def ingest_github_docs(self, owner: str, repo: str, token: str):
        """Ingest documentation from GitHub repository."""
        print(f"Ingesting GitHub docs from {owner}/{repo}...")
        
        connector = GitHubConnector(token=token)
        
        # Get README and wiki pages
        files = connector.sync_files(
            owner=owner,
            repo=repo,
            path_patterns=["*.md", "docs/*.md", "README*"]
        )
        
        records = []
        for file in files:
            record = connector.map_to_frame_record(file)
            # Add source context
            record.metadata.update({
                "source_type": "github",
                "repository": f"{owner}/{repo}",
                "file_path": file.get("path")
            })
            records.append(record)
        
        # Batch add with embeddings
        self.dataset.add_batch(records, generate_embeddings=True)
        print(f"Added {len(records)} GitHub documents")
        
    def ingest_notion_pages(self, api_key: str, database_id: Optional[str] = None):
        """Ingest pages from Notion."""
        print("Ingesting Notion pages...")
        
        connector = NotionConnector(api_key=api_key)
        
        if database_id:
            # Specific database
            pages = connector.sync_database(database_id)
        else:
            # All accessible pages
            pages = connector.sync_pages()
        
        records = []
        for page in pages:
            record = connector.map_to_frame_record(page)
            record.metadata.update({
                "source_type": "notion",
                "page_url": page.get("url"),
                "last_edited": page.get("last_edited_time")
            })
            records.append(record)
        
        self.dataset.add_batch(records, generate_embeddings=True)
        print(f"Added {len(records)} Notion pages")
        
    def ingest_google_drive(self, folder_id: str, credentials_path: str):
        """Ingest documents from Google Drive."""
        print(f"Ingesting Google Drive folder {folder_id}...")
        
        connector = GoogleDriveConnector(
            service_account_file=credentials_path
        )
        
        # Sync documents
        documents = connector.sync_documents(
            folder_id=folder_id,
            recursive=True,
            mime_types=[
                "application/vnd.google-apps.document",
                "application/pdf",
                "text/plain"
            ]
        )
        
        records = []
        for doc in documents:
            record = connector.map_to_frame_record(doc)
            record.metadata.update({
                "source_type": "google_drive",
                "mime_type": doc.get("mimeType"),
                "drive_url": doc.get("webViewLink")
            })
            records.append(record)
        
        self.dataset.add_batch(records, generate_embeddings=True)
        print(f"Added {len(records)} Google Drive documents")
    
    def retrieve_context(self, query: str, k: int = 5, 
                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant context for a query."""
        # Build filter string if provided
        filter_str = None
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(f"metadata.{key} = '{value}'")
                else:
                    conditions.append(f"metadata.{key} = {value}")
            filter_str = " AND ".join(conditions)
        
        # Semantic search
        results = self.dataset.search(
            query=query,
            limit=k,
            filter=filter_str
        )
        
        # Format context
        contexts = []
        for result in results:
            contexts.append({
                "content": result.text_content,
                "metadata": result.metadata,
                "score": result.score,
                "unique_id": result.unique_id
            })
        
        return contexts
    
    def generate_answer(self, query: str, contexts: List[Dict[str, Any]], 
                       model: str = "gpt-4-turbo-preview") -> Dict[str, Any]:
        """Generate answer using retrieved context."""
        # Prepare context for prompt
        context_text = "\n\n---\n\n".join([
            f"Source: {ctx['metadata'].get('title', 'Unknown')}\n"
            f"Type: {ctx['metadata'].get('source_type', 'Unknown')}\n"
            f"Content: {ctx['content'][:1000]}..."  # Truncate long content
            for ctx in contexts
        ])
        
        # System prompt
        system_prompt = """You are a helpful AI assistant that answers questions based on provided context.
        Always cite your sources and indicate confidence level.
        If the context doesn't contain enough information, say so clearly."""
        
        # User prompt
        user_prompt = f"""Based on the following context, please answer this question: {query}

Context:
{context_text}

Please provide:
1. A clear answer to the question
2. Citations to specific sources used
3. A confidence level (high/medium/low) based on context relevance"""

        # Generate response
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        # Parse citations from answer (simple regex approach)
        import re
        citations = []
        for ctx in contexts:
            title = ctx['metadata'].get('title', '')
            if title and title in answer:
                citations.append({
                    "title": title,
                    "source_type": ctx['metadata'].get('source_type'),
                    "unique_id": ctx['unique_id'],
                    "relevance_score": ctx['score']
                })
        
        return {
            "query": query,
            "answer": answer,
            "contexts_used": len(contexts),
            "citations": citations,
            "model": model,
            "timestamp": datetime.now().isoformat()
        }
    
    def ask(self, question: str, k: int = 5, 
            filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Complete RAG pipeline: retrieve context and generate answer."""
        # Retrieve relevant context
        contexts = self.retrieve_context(question, k=k, filters=filters)
        
        if not contexts:
            return {
                "query": question,
                "answer": "I couldn't find any relevant information to answer your question.",
                "contexts_used": 0,
                "citations": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Generate answer
        result = self.generate_answer(question, contexts)
        
        # Store the Q&A pair for future reference
        qa_record = FrameRecord(
            text_content=f"Q: {question}\nA: {result['answer']}",
            metadata=create_metadata(
                title=f"Q&A: {question[:50]}...",
                source="rag_system",
                question=question,
                answer_summary=result['answer'][:200],
                contexts_used=result['contexts_used'],
                citations=result['citations']
            ),
            record_type="document",
            context={
                "qa_type": "generated",
                "model": result['model'],
                "timestamp": result['timestamp']
            }
        )
        self.dataset.add(qa_record)
        
        return result
    
    def update_knowledge(self, feedback: Dict[str, Any]):
        """Update knowledge base based on user feedback."""
        # Find the Q&A record
        qa_records = self.dataset.sql_filter(
            f"metadata.question = '{feedback['question']}'",
            limit=1
        )
        
        if qa_records:
            record = qa_records[0]
            # Update with feedback
            record.metadata.update({
                "user_feedback": feedback.get('rating'),
                "feedback_comment": feedback.get('comment'),
                "feedback_timestamp": datetime.now().isoformat()
            })
            
            # Update in dataset
            self.dataset.update(
                record.unique_id,
                metadata=record.metadata
            )
    
    def get_usage_analytics(self) -> Dict[str, Any]:
        """Get analytics on RAG system usage."""
        # Query Q&A records
        qa_records = self.dataset.sql_filter(
            "metadata.source = 'rag_system'",
            limit=1000
        )
        
        if not qa_records:
            return {"total_questions": 0}
        
        # Analyze patterns
        questions = [r.metadata.get('question', '') for r in qa_records]
        sources_used = []
        for r in qa_records:
            citations = r.metadata.get('citations', [])
            sources_used.extend([c['source_type'] for c in citations])
        
        # Count by source type
        from collections import Counter
        source_counts = Counter(sources_used)
        
        # Average contexts used
        contexts_counts = [r.metadata.get('contexts_used', 0) for r in qa_records]
        avg_contexts = sum(contexts_counts) / len(contexts_counts) if contexts_counts else 0
        
        return {
            "total_questions": len(qa_records),
            "unique_questions": len(set(questions)),
            "sources_usage": dict(source_counts),
            "average_contexts_per_answer": avg_contexts,
            "total_documents": len(self.dataset)
        }

# Example usage
if __name__ == "__main__":
    # Initialize RAG system
    rag = RAGSystem("company_knowledge.lance")
    
    # Ingest from multiple sources
    rag.ingest_github_docs(
        owner="mycompany",
        repo="documentation",
        token=os.getenv("GITHUB_TOKEN")
    )
    
    rag.ingest_notion_pages(
        api_key=os.getenv("NOTION_API_KEY"),
        database_id="your_database_id"
    )
    
    rag.ingest_google_drive(
        folder_id="your_folder_id",
        credentials_path="service-account.json"
    )
    
    # Ask questions
    result = rag.ask(
        "What is our deployment process?",
        filters={"source_type": "github"}  # Only search GitHub docs
    )
    
    print(f"Question: {result['query']}")
    print(f"Answer: {result['answer']}")
    print(f"Used {result['contexts_used']} contexts")
    print(f"Citations: {len(result['citations'])}")
    
    # Get analytics
    analytics = rag.get_usage_analytics()
    print(f"\nRAG System Analytics:")
    print(f"Total questions: {analytics['total_questions']}")
    print(f"Document sources: {analytics['sources_usage']}")
```

## Key Concepts

### 1. Multi-Source Ingestion
- Connects to GitHub, Notion, and Google Drive
- Preserves source metadata for filtering
- Batch processes with automatic embedding generation

### 2. Semantic Search
- Uses embeddings for relevant context retrieval
- Supports metadata filtering for source-specific search
- Returns scored results for relevance ranking

### 3. Context-Aware Generation
- Formats retrieved context for LLM consumption
- Includes source attribution in prompts
- Manages token limits through truncation

### 4. Citation Tracking
- Extracts citations from generated answers
- Links back to source documents
- Provides relevance scores

### 5. Feedback Loop
- Stores Q&A pairs for analysis
- Updates based on user feedback
- Tracks usage analytics

## Extensions

### 1. Advanced Retrieval
```python
def hybrid_retrieve(self, query: str, k: int = 5):
    """Combine semantic and keyword search."""
    # Semantic search
    semantic_results = self.dataset.search(query, limit=k)
    
    # Full-text search
    keyword_results = self.dataset.full_text_search(
        query, 
        columns=["text_content", "metadata.title"],
        limit=k
    )
    
    # Merge and re-rank
    all_results = self._merge_results(semantic_results, keyword_results)
    return all_results[:k]
```

### 2. Conversation Memory
```python
class ConversationalRAG(RAGSystem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_history = []
    
    def ask_conversational(self, question: str):
        # Include conversation history in context
        history_context = "\n".join([
            f"User: {turn['user']}\nAssistant: {turn['assistant']}"
            for turn in self.conversation_history[-3:]  # Last 3 turns
        ])
        
        # Modify question with history
        contextualized_question = f"{history_context}\n\nUser: {question}"
        
        # Get answer
        result = self.ask(contextualized_question)
        
        # Update history
        self.conversation_history.append({
            "user": question,
            "assistant": result['answer']
        })
        
        return result
```

### 3. Streaming Responses
```python
def ask_streaming(self, question: str):
    """Stream responses token by token."""
    contexts = self.retrieve_context(question)
    
    # Stream from OpenAI
    stream = self.openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=self._build_messages(question, contexts),
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### 4. Multi-Modal RAG
```python
def ingest_images(self, image_paths: List[str]):
    """Ingest images with generated descriptions."""
    for path in image_paths:
        # Generate description using vision model
        description = self._generate_image_description(path)
        
        # Create record
        with open(path, 'rb') as f:
            image_data = f.read()
        
        record = FrameRecord(
            text_content=description,
            raw_data=image_data,
            metadata=create_metadata(
                title=os.path.basename(path),
                source="image",
                mime_type="image/jpeg"
            )
        )
        
        self.dataset.add(record, generate_embedding=True)
```

### 5. Performance Optimization
```python
# Create indexes for faster retrieval
rag.dataset.create_index(
    vector_column="vector",
    metric="cosine",
    index_type="IVF_PQ"
)

# Cache frequent queries
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_retrieve(self, query_hash: str):
    return self.retrieve_context(query_hash)
```

## Best Practices

1. **Document Quality**: Ensure ingested documents are clean and well-structured
2. **Embedding Model**: Use consistent embedding model across all documents
3. **Context Window**: Manage LLM context window limits carefully
4. **Source Attribution**: Always provide clear citations
5. **Feedback Integration**: Use feedback to improve retrieval and generation
6. **Security**: Implement access controls for sensitive documents
7. **Monitoring**: Track performance metrics and user satisfaction

## See Also

- [Multi-Source Search](multi-source-search.md) - Advanced search techniques
- [Document Processing Pipeline](document-pipeline.md) - Pre-processing documents
- [API Reference](../api/overview.md) - Detailed API documentation
- [Embeddings Module](../modules/embeddings.md) - Understanding embeddings