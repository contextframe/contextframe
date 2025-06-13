"""Context enhancement module for ContextFrame.

This module provides LLM-powered enhancement capabilities for documents,
allowing AI agents and users to automatically populate ContextFrame
schema fields with meaningful metadata, relationships, and context.

Key Features:
- User-driven enhancement through custom prompts
- MCP-compatible tool interface for agent integration  
- Direct schema field population (context, tags, relationships, etc.)
- Example prompts for common enhancement patterns
- Batch processing with progress tracking
"""

from contextframe.enhance.base import (
    ContextEnhancer,
    EnhancementResult,
)
from contextframe.enhance.tools import (
    EnhancementTools,
    create_enhancement_tool,
    get_tool_schema,
    list_available_tools,
    ENHANCEMENT_TOOLS,
)
from contextframe.enhance.prompts import (
    get_prompt_template,
    list_available_prompts,
    build_enhancement_prompt,
)

__all__ = [
    # Core enhancer
    "ContextEnhancer",
    "EnhancementResult",
    
    # MCP tools
    "EnhancementTools",
    "create_enhancement_tool",
    "get_tool_schema",
    "list_available_tools",
    "ENHANCEMENT_TOOLS",
    
    # Prompt templates
    "get_prompt_template",
    "list_available_prompts",
    "build_enhancement_prompt",
]