# Mirascope & Lilypad Best Practices

This document outlines best practices for using Mirascope (LLM framework) and Lilypad (observability) in the Funcn project.

## Mirascope Core Principles

1. **Colocation**: Keep prompts, parameters, and logic together
2. **Type Safety**: Use Pydantic models and type hints everywhere
3. **Provider Agnostic**: Write once, run with any provider
4. **Pythonic**: Follow Python conventions, avoid complex abstractions
5. **Error Resilient**: Implement retries and proper error handling

## Mirascope Best Practices

### 1. Decorator Usage

#### Use @llm.call for All LLM Interactions

```python
from mirascope import llm

# GOOD: Clear, simple, provider-agnostic
@llm.call(provider="{{provider}}", model="{{model}}")
async def analyze_text(text: str) -> str:
    """Analyze the following text: {text}"""
    ...

# BAD: Direct provider SDK usage
import openai
client = openai.OpenAI()
response = client.chat.completions.create(...)
```

#### Use @prompt_template for Reusable Prompts

```python
from mirascope import prompt_template

# GOOD: Reusable across multiple functions
@prompt_template("""
You are an expert {domain} assistant.
Task: {task}
Context: {context}
""")
def expert_prompt(domain: str, task: str, context: str):
    ...

# Use with multiple providers
@llm.call(provider="openai", model="gpt-4")
async def openai_expert(domain: str, task: str, context: str) -> str:
    return expert_prompt(domain, task, context)

@llm.call(provider="anthropic", model="claude-3-5-sonnet")
async def anthropic_expert(domain: str, task: str, context: str) -> str:
    return expert_prompt(domain, task, context)
```

### 2. Structured Outputs with Response Models

#### Always Use Pydantic Models for Structured Data

```python
from pydantic import BaseModel, Field
from mirascope import llm

# GOOD: Well-documented, validated response model
class AnalysisResult(BaseModel):
    """Structured analysis output."""
    
    summary: str = Field(..., description="Brief summary of findings")
    key_points: list[str] = Field(..., description="Main points identified")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    recommendations: list[str] = Field(default_factory=list)

@llm.call(
    provider="{{provider}}", 
    model="{{model}}",
    response_model=AnalysisResult,
    json_mode=True  # Enable for better reliability
)
async def analyze_document(document: str) -> str:
    """Analyze this document and provide structured findings: {document}"""
    ...
```

#### Use Field Descriptions for Better Results

```python
# GOOD: Detailed field descriptions guide the LLM
class Entity(BaseModel):
    name: str = Field(..., description="Full name of the entity")
    type: str = Field(..., description="Entity type: person, organization, location")
    context: str = Field(..., description="Brief context about the entity's relevance")

# BAD: No descriptions
class Entity(BaseModel):
    name: str
    type: str
    context: str
```

### 3. Tool Implementation Patterns

#### Tools Should Be Simple Functions

```python
# GOOD: Simple, focused, well-typed function
def search_documents(
    query: str,
    limit: int = 10,
    file_type: str = "all"
) -> list[dict[str, str]]:
    """Search documents matching the query.
    
    Args:
        query: Search query string
        limit: Maximum results to return
        file_type: Filter by file type (all, pdf, txt, md)
        
    Returns:
        List of documents with title and content
    """
    # Implementation
    return results[:limit]

# BAD: Complex class-based tool
class DocumentSearcher(BaseTool):
    def __init__(self, config):
        self.config = config
    
    def search(self, query):
        # Complex implementation
```

#### Always Handle Errors in Tools

```python
def fetch_data(url: str) -> dict[str, Any]:
    """Fetch data from URL with proper error handling."""
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        return {"error": "Request timed out", "url": url}
    except httpx.HTTPError as e:
        return {"error": f"HTTP error: {e}", "url": url}
    except Exception as e:
        return {"error": f"Unexpected error: {e}", "url": url}
```

### 4. Multi-Provider Support

#### Design Provider-Agnostic Components

```python
# GOOD: Works with any provider via template variables
@llm.call(provider="{{provider}}", model="{{model}}")
async def universal_agent(query: str) -> str:
    """Process the query: {query}"""
    ...

# Support runtime provider switching
from mirascope import llm

async def process_with_fallback(query: str) -> str:
    """Process with automatic fallback."""
    try:
        # Try primary provider
        return await universal_agent(query)
    except Exception:
        # Fallback to alternative
        with llm.override(provider="anthropic", model="claude-3-5-sonnet"):
            return await universal_agent(query)
```

### 5. Error Handling and Validation

#### Implement Retry Logic with Tenacity

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field, validator
from mirascope import llm

class ValidatedOutput(BaseModel):
    """Output with validation rules."""
    result: str = Field(..., min_length=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    @validator('result')
    def validate_content(cls, v):
        if "error" in v.lower():
            raise ValueError("Result contains error")
        return v

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
@llm.call(
    provider="{{provider}}", 
    model="{{model}}",
    response_model=ValidatedOutput
)
async def reliable_generation(prompt: str) -> str:
    """Generate validated output with retry logic.
    
    Prompt: {prompt}
    
    Provide a detailed response with confidence score.
    """
    ...

# The retry decorator will:
# 1. Catch validation errors from Pydantic
# 2. Retry up to 3 times with exponential backoff
# 3. Re-insert validation errors into the prompt for learning
```

#### Production Retry Pattern with Lilypad

```python
import lilypad
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from mirascope import llm
from pydantic import BaseModel

lilypad.configure(auto_llm=True)

class AnalysisResult(BaseModel):
    summary: str
    key_points: list[str]
    confidence: float

@lilypad.trace(versioning="automatic")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ValidationError, TimeoutError))
)
@llm.call(
    provider="{{provider}}",
    model="{{model}}",
    response_model=AnalysisResult
)
async def production_analysis(document: str) -> str:
    """Analyze document with automatic retry on failures.
    
    Document: {document}
    
    Provide comprehensive analysis with key points.
    """
    ...

# With Lilypad + Tenacity:
# - All retry attempts are tracked
# - You can see which prompts fail validation
# - Cost of retries is automatically calculated
# - Success rate after retries is visible
```

### 6. Async Best Practices

#### Always Use Async for LLM Calls

```python
# GOOD: Async for concurrent operations
@llm.call(provider="{{provider}}", model="{{model}}")
async def process_item(item: str) -> str:
    """Process: {item}"""
    ...

async def process_batch(items: list[str]) -> list[str]:
    """Process multiple items concurrently."""
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)

# BAD: Synchronous blocking calls
def process_item_sync(item: str) -> str:
    # Blocks event loop
    return llm_call_sync(item)
```

#### Handle Streaming Properly

```python
@llm.call(provider="{{provider}}", model="{{model}}", stream=True)
async def stream_story(topic: str) -> str:
    """Tell a story about: {topic}"""
    ...

async def print_stream():
    """Handle streaming response."""
    stream = await stream_story("space exploration")
    async for chunk, _ in stream:
        print(chunk.content, end="", flush=True)
```

## Lilypad Observability Best Practices

Lilypad creates a "data flywheel" for LLM development by tracking versions, observability data, and enabling systematic optimization.

### 1. Enable Auto-Instrumentation

```python
# In your main application file
import lilypad

# Enable automatic LLM instrumentation
lilypad.configure(auto_llm=True)
```

### 2. Development Workflow with Lilypad

Follow Lilypad's 6-step iterative process:

1. **Prototype**: Initial LLM function development
2. **Vibe Check**: Test outputs informally
3. **Annotate**: Add tracking and metadata
4. **Analyze**: Review performance and outputs
5. **Optimize**: Improve based on data
6. **Iterate**: Repeat the cycle

### 3. Use Automatic Versioning

```python
import lilypad
from mirascope import llm

# Automatic versioning tracks all prompt changes
@lilypad.trace(versioning="automatic")
@llm.call(provider="{{provider}}", model="{{model}}")
async def production_agent(query: str) -> str:
    """Production-ready agent with full observability.
    
    Query: {query}
    """
    ...
```

### 4. Track Performance Metrics

Lilypad automatically tracks:

- **Cost**: Token usage and associated costs
- **Latency**: Response times
- **Inputs/Outputs**: Full conversation context
- **Errors**: Failed calls and error messages

```python
@lilypad.trace(versioning="automatic")
@llm.call(provider="{{provider}}", model="{{model}}")
async def tracked_agent(query: str) -> str:
    """Agent with automatic performance tracking.
    
    Lilypad will track:
    - Token usage and cost
    - Response latency
    - Full input/output
    - Any errors
    """
    return f"Process: {query}"
```

### 5. Annotation and Analysis

Use Lilypad to annotate and analyze LLM outputs:

```python
@lilypad.trace(versioning="automatic")
@llm.call(provider="{{provider}}", model="{{model}}")
async def analyzed_agent(query: str) -> str:
    """Agent with output analysis capabilities.
    
    Lilypad enables:
    - Comparing outputs across versions
    - Identifying performance regressions
    - A/B testing different prompts
    - Systematic optimization
    """
    return f"Analyze: {query}"

# After deployment, use Lilypad to:
# 1. Compare v1 vs v2 outputs
# 2. Identify which version performs better
# 3. Track cost/latency improvements
# 4. Make data-driven decisions
```

## Production Deployment Checklist

### Mirascope Components

- [ ] All LLM calls use `@llm.call` decorator
- [ ] Response models use Pydantic with descriptions
- [ ] Tools are simple functions with type hints
- [ ] Error handling with retries implemented
- [ ] Provider-agnostic design (template variables)
- [ ] Async used for all I/O operations
- [ ] Proper timeout handling
- [ ] Rate limiting considered

### Lilypad Observability

- [ ] Auto-instrumentation enabled (`auto_llm=True`)
- [ ] Automatic versioning configured
- [ ] Performance metrics tracked (cost, latency)
- [ ] Input/output tracking active
- [ ] Error tracking enabled
- [ ] Version comparison workflow established
- [ ] Data flywheel process implemented
- [ ] Annotation workflow defined

## Common Patterns

### Simple Example with Full Observability

```python
import lilypad
from mirascope import llm

# One-line configuration
lilypad.configure(auto_llm=True)

@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
def answer_question(question: str) -> str:
    """Answer questions concisely.
    
    Question: {question}
    """
    return "Answer in one word"

# That's it! Lilypad now tracks:
# - All versions of this function
# - Cost per call
# - Response latency
# - Full inputs/outputs
# - Any errors
```

### Production Agent Example

```python
import lilypad
from mirascope import llm
from pydantic import BaseModel
from typing import Any

# Configure Lilypad
lilypad.configure(auto_llm=True)

class AgentOutput(BaseModel):
    """Structured agent response."""
    answer: str
    confidence: float
    sources: list[str] = []

@lilypad.trace(versioning="automatic")
@llm.call(
    provider="{{provider}}",
    model="{{model}}",
    response_model=AgentOutput,
    tools=[search_tool, calculate_tool]
)
async def production_agent(query: str, context: dict[str, Any]) -> str:
    """Production-ready agent with full observability.
    
    Query: {query}
    Context: {context}
    
    Use available tools to provide accurate answers.
    """
    ...

# Lilypad enables:
# 1. Track performance across deployments
# 2. Compare outputs between versions
# 3. Identify cost optimization opportunities
# 4. Debug issues with full context
```

### Testing Mirascope Components

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_agent_with_mock():
    """Test agent without making real LLM calls."""
    with patch("mirascope.openai.call") as mock_call:
        mock_call.return_value = Mock(
            content="Mocked response",
            response_model=AgentOutput(
                answer="Test answer",
                confidence=0.95,
                sources=["test.pdf"]
            )
        )
        
        result = await production_agent("test query", {})
        assert result.confidence > 0.9
        assert "test.pdf" in result.sources
```

## Quick Reference

### Mirascope Imports

```python
from mirascope import llm, prompt_template
from mirascope.core import BaseModel
```

### Lilypad Setup

```python
import lilypad

# One-line setup for automatic LLM tracking
lilypad.configure(auto_llm=True)
```

### Component Template

```python
@lilypad.trace(versioning="automatic")
@llm.call(provider="{{provider}}", model="{{model}}")
async def component_name(input: str) -> str:
    """Component description.
    
    Input: {input}
    """
    ...
```

## Key Takeaways

### Mirascope

- Use `@llm.call` for all LLM interactions
- Implement Pydantic models for structured outputs
- Design provider-agnostic components
- Use async for all I/O operations
- Implement proper error handling with Tenacity

### Lilypad

- Creates a "data flywheel" for LLM development
- One-line setup with `lilypad.configure(auto_llm=True)`
- Automatic versioning tracks all prompt changes
- Tracks cost, latency, inputs/outputs automatically
- Enables systematic comparison and optimization
- Follow the 6-step process: Prototype → Vibe Check → Annotate → Analyze → Optimize → Iterate
