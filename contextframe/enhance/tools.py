"""MCP-compatible tool definitions for document enhancement."""

from typing import Any, Optional

from .base import ContextEnhancer, FrameRecord


# Tool definitions that MCP servers can expose
ENHANCEMENT_TOOLS = {
    "enhance_context": {
        "description": "Add context to explain document relevance",
        "parameters": {
            "content": {"type": "string", "description": "Document content"},
            "purpose": {"type": "string", "description": "What the context should focus on"},
            "current_context": {"type": "string", "description": "Existing context if any", "optional": True}
        },
        "returns": "Context string for the document"
    },
    
    "extract_metadata": {
        "description": "Extract custom metadata from document",
        "parameters": {
            "content": {"type": "string", "description": "Document content"},
            "schema": {"type": "string", "description": "What metadata to extract (as prompt)"},
            "format": {"type": "string", "description": "Output format", "default": "json"}
        },
        "returns": "Dictionary of metadata"
    },
    
    "generate_tags": {
        "description": "Generate relevant tags for a document",
        "parameters": {
            "content": {"type": "string", "description": "Document content"},
            "tag_types": {"type": "string", "description": "Types of tags to generate (topics, technologies, concepts)"},
            "max_tags": {"type": "integer", "description": "Maximum number of tags", "default": 5}
        },
        "returns": "List of tags"
    },
    
    "improve_title": {
        "description": "Generate or improve document title",
        "parameters": {
            "content": {"type": "string", "description": "Document content"},
            "current_title": {"type": "string", "description": "Current title if any", "optional": True},
            "style": {"type": "string", "description": "Title style (descriptive, technical, concise)", "default": "descriptive"}
        },
        "returns": "Improved title string"
    },
    
    "find_relationships": {
        "description": "Identify relationships to other documents",
        "parameters": {
            "source_content": {"type": "string", "description": "Source document content"},
            "source_title": {"type": "string", "description": "Source document title"},
            "candidate_summaries": {"type": "array", "description": "List of candidate document summaries"},
            "relationship_types": {"type": "string", "description": "Types to look for", "default": "parent,child,related,reference"}
        },
        "returns": "List of relationships with type and description"
    },
    
    "enhance_for_purpose": {
        "description": "Enhance document with purpose-specific metadata",
        "parameters": {
            "content": {"type": "string", "description": "Document content"},
            "purpose": {"type": "string", "description": "Purpose or use case for enhancement"},
            "fields": {"type": "array", "description": "Which fields to enhance", "default": ["context", "tags", "custom_metadata"]}
        },
        "returns": "Dictionary with enhanced fields"
    }
}


class EnhancementTools:
    """MCP-compatible tool implementations for document enhancement.
    
    This class provides tool methods that can be exposed through MCP servers,
    allowing AI agents to call enhancement functions as native tools.
    """
    
    def __init__(self, enhancer: ContextEnhancer):
        """Initialize with a ContextEnhancer instance."""
        self.enhancer = enhancer
    
    def enhance_context(
        self,
        content: str,
        purpose: str,
        current_context: str | None = None
    ) -> str:
        """Add context to explain document relevance.
        
        Tool: enhance_context
        """
        prompt = f"""
        Analyze this document and write a brief context description (2-3 sentences)
        explaining its relevance for: {purpose}
        
        {"Current context: " + current_context if current_context else ""}
        
        Document content:
        {{content}}
        
        Context description:
        """
        
        return self.enhancer.enhance_field(
            content=content,
            field_name="context",
            prompt=prompt
        )
    
    def extract_metadata(
        self,
        content: str,
        schema: str,
        format: str = "json"
    ) -> dict[str, Any]:
        """Extract custom metadata from document.
        
        Tool: extract_metadata
        """
        prompt = f"""
        Extract the following metadata from the document:
        {schema}
        
        Document content:
        {{content}}
        
        Return as {"JSON" if format == "json" else format}:
        """
        
        return self.enhancer.enhance_field(
            content=content,
            field_name="custom_metadata",
            prompt=prompt
        )
    
    def generate_tags(
        self,
        content: str,
        tag_types: str = "topics, technologies, concepts",
        max_tags: int = 5
    ) -> list[str]:
        """Generate relevant tags for a document.
        
        Tool: generate_tags
        """
        prompt = f"""
        Generate up to {max_tags} tags for this document.
        Focus on: {tag_types}
        
        Document content:
        {{content}}
        
        Return tags as a comma-separated list:
        """
        
        return self.enhancer.enhance_field(
            content=content,
            field_name="tags",
            prompt=prompt
        )
    
    def improve_title(
        self,
        content: str,
        current_title: str | None = None,
        style: str = "descriptive"
    ) -> str:
        """Generate or improve document title.
        
        Tool: improve_title
        """
        prompt = f"""
        {"Current title: " + current_title if current_title else "No current title."}
        
        Generate a {style} title for this document.
        The title should be clear and informative.
        
        Document content:
        {{content}}
        
        New title:
        """
        
        return self.enhancer.enhance_field(
            content=content,
            field_name="title",
            prompt=prompt
        )
    
    def find_relationships(
        self,
        source_content: str,
        source_title: str,
        candidate_summaries: list[dict[str, str]],
        relationship_types: str = "parent,child,related,reference"
    ) -> list[dict[str, Any]]:
        """Identify relationships to other documents.
        
        Tool: find_relationships
        """
        candidates_text = "\n".join([
            f"{i+1}. {c.get('title', 'Untitled')}: {c.get('summary', '')}"
            for i, c in enumerate(candidate_summaries)
        ])
        
        prompt = f"""
        Find relationships between the source document and candidates.
        Relationship types to consider: {relationship_types}
        
        Source document:
        Title: {source_title}
        Content: {{content}}
        
        Candidate documents:
        {candidates_text}
        
        Return as JSON array with format:
        [
            {{
                "target_title": "Title of related document",
                "type": "relationship type",
                "description": "Brief explanation"
            }}
        ]
        
        Only include clear relationships, not vague similarities.
        """
        
        return self.enhancer.enhance_field(
            content=source_content,
            field_name="relationships",
            prompt=prompt
        )
    
    def enhance_for_purpose(
        self,
        content: str,
        purpose: str,
        fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Enhance document with purpose-specific metadata.
        
        Tool: enhance_for_purpose
        """
        if fields is None:
            fields = ["context", "tags", "custom_metadata"]
        
        results = {}
        
        if "context" in fields:
            results["context"] = self.enhance_context(content, purpose)
        
        if "tags" in fields:
            results["tags"] = self.generate_tags(
                content,
                f"tags relevant to {purpose}"
            )
        
        if "custom_metadata" in fields:
            prompt = f"""
            Extract metadata relevant to: {purpose}
            
            Consider:
            - Key concepts and entities
            - Relevance scores or ratings
            - Specific attributes for the use case
            
            Document: {{content}}
            
            Return as JSON:
            """
            
            results["custom_metadata"] = self.enhancer.enhance_field(
                content=content,
                field_name="custom_metadata",
                prompt=prompt
            )
        
        return results


def create_enhancement_tool(enhancer: ContextEnhancer, tool_name: str) -> callable:
    """Create MCP-compatible tool from enhancer method.
    
    Args:
        enhancer: ContextEnhancer instance
        tool_name: Name of the tool from ENHANCEMENT_TOOLS
        
    Returns:
        Callable tool function
        
    Raises:
        ValueError: If tool_name is not recognized
    """
    if tool_name not in ENHANCEMENT_TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    tools = EnhancementTools(enhancer)
    return getattr(tools, tool_name)


def get_tool_schema(tool_name: str) -> dict[str, Any]:
    """Get MCP schema for a tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool schema dictionary
    """
    if tool_name not in ENHANCEMENT_TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    return ENHANCEMENT_TOOLS[tool_name]


def list_available_tools() -> list[str]:
    """List all available enhancement tools."""
    return list(ENHANCEMENT_TOOLS.keys())