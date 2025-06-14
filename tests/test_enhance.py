"""Tests for the enhancement module."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from contextframe import FrameRecord, FrameDataset
from contextframe.enhance import (
    ContextEnhancer,
    EnhancementResult,
    EnhancementTools,
    get_prompt_template,
    list_available_prompts,
    build_enhancement_prompt,
)


class TestContextEnhancer:
    """Test the ContextEnhancer class."""
    
    @patch('contextframe.enhance.base.llm.call')
    def test_enhance_context(self, mock_llm_call):
        """Test enhancing context field with structured output."""
        # Create a mock function that simulates the decorator behavior
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    # Return a mock response with the expected structure
                    mock_response = Mock()
                    mock_response.context = "This document explains RAG architecture."
                    return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        enhancer = ContextEnhancer(provider="openai", model="gpt-4o-mini")
        result = enhancer.enhance_context(
            content="RAG combines LLMs with retrieval...",
            purpose="understanding AI systems"
        )
        
        assert result == "This document explains RAG architecture."
    
    @patch('contextframe.enhance.base.llm.call')
    def test_enhance_tags(self, mock_llm_call):
        """Test extracting tags with structured output."""
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    mock_response = Mock()
                    mock_response.tags = ["RAG", "LLM", "retrieval", "embeddings"]
                    return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        enhancer = ContextEnhancer()
        result = enhancer.enhance_tags(
            content="RAG architecture combines retrieval with LLM generation",
            tag_types="technologies",
            max_tags=5
        )
        
        assert isinstance(result, list)
        assert len(result) == 4
        assert "RAG" in result
        assert "LLM" in result
    
    @patch('contextframe.enhance.base.llm.call')
    def test_enhance_custom_metadata(self, mock_llm_call):
        """Test extracting custom metadata with structured output."""
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    mock_response = Mock()
                    mock_response.metadata = {"complexity": 3, "topics": ["RAG", "LLM"]}
                    return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        enhancer = ContextEnhancer()
        result = enhancer.enhance_custom_metadata(
            content="RAG architecture guide",
            schema_prompt="Extract complexity level and main topics"
        )
        
        assert isinstance(result, dict)
        assert result["complexity"] == 3
        assert "RAG" in result["topics"]
    
    @patch('contextframe.enhance.base.llm.call')  
    def test_enhance_relationships(self, mock_llm_call):
        """Test finding relationships with structured output."""
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    mock_response = Mock()
                    # Create mock relationship objects
                    rel1 = Mock()
                    rel1.type = Mock(value="related")
                    rel1.title = "Advanced RAG"
                    rel1.description = "Builds on basic concepts"
                    rel1.target_id = "123"
                    mock_response.relationships = [rel1]
                    return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        enhancer = ContextEnhancer()
        relationships = enhancer.enhance_relationships(
            source_content="Basic RAG introduction",
            source_title="Basic RAG",
            candidates=[
                {"title": "Advanced RAG", "summary": "Advanced techniques"}
            ],
            max_relationships=5
        )
        
        assert len(relationships) == 1
        assert relationships[0]["type"] == "related"
        assert relationships[0]["title"] == "Advanced RAG"
        assert relationships[0]["description"] == "Builds on basic concepts"
    
    @patch('contextframe.enhance.base.llm.call')
    def test_enhance_field_generic(self, mock_llm_call):
        """Test generic field enhancement."""
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    # Return different responses based on response_model
                    if response_model.__name__ == "ContextResponse":
                        mock_response = Mock()
                        mock_response.context = "Enhanced context"
                        return mock_response
                    elif response_model.__name__ == "TagsResponse":
                        mock_response = Mock()
                        mock_response.tags = ["tag1", "tag2"]
                        return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        enhancer = ContextEnhancer()
        
        # Test context field
        result = enhancer.enhance_field(
            content="Test content",
            field_name="context",
            prompt="Add context"
        )
        assert result == "Enhanced context"
        
        # Test tags field
        result = enhancer.enhance_field(
            content="Test content",
            field_name="tags",
            prompt="Extract tags"
        )
        assert result == ["tag1", "tag2"]
    
    @patch('contextframe.enhance.base.llm.call')
    def test_enhance_document(self, mock_llm_call):
        """Test enhancing a full document."""
        call_count = 0
        
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:  # First call for context
                        mock_response = Mock()
                        mock_response.context = "A guide to RAG architecture"
                        return mock_response
                    else:  # Second call for tags
                        mock_response = Mock() 
                        mock_response.tags = ["RAG", "LLM", "retrieval"]
                        return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        frame = FrameRecord.create(
            title="RAG Guide",
            content="Content about RAG...",
            uri="test.md"
        )
        
        enhancer = ContextEnhancer()
        enhanced = enhancer.enhance_document(
            frame,
            enhancements={
                "context": "Summarize the document",
                "tags": "Extract key topics"
            }
        )
        
        assert enhanced.metadata.get("context") == "A guide to RAG architecture"
        assert enhanced.metadata.get("tags") == ["RAG", "LLM", "retrieval"]
    
    def test_field_has_value(self):
        """Test checking if fields have values."""
        enhancer = ContextEnhancer()
        
        frame = FrameRecord.create(title="Test", uri="test.md")
        assert not enhancer._field_has_value(frame, "context")
        
        frame.metadata["context"] = "Some context"
        assert enhancer._field_has_value(frame, "context")
        
        frame.metadata["tags"] = []
        assert not enhancer._field_has_value(frame, "tags")
        
        frame.metadata["tags"] = ["tag1"]
        assert enhancer._field_has_value(frame, "tags")


class TestEnhancementTools:
    """Test the MCP-compatible tools."""
    
    @patch('contextframe.enhance.base.llm.call')
    def test_enhance_context_tool(self, mock_llm_call):
        """Test the enhance_context tool."""
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    mock_response = Mock()
                    mock_response.context = "Document about testing frameworks"
                    return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        enhancer = ContextEnhancer()
        tools = EnhancementTools(enhancer)
        
        result = tools.enhance_context(
            content="pytest is a testing framework...",
            purpose="understanding Python testing"
        )
        
        assert result == "Document about testing frameworks"
    
    @patch('contextframe.enhance.base.llm.call')
    def test_extract_metadata_tool(self, mock_llm_call):
        """Test the extract_metadata tool."""
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    mock_response = Mock()
                    mock_response.metadata = {"language": "python", "framework": "pytest"}
                    return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        enhancer = ContextEnhancer()
        tools = EnhancementTools(enhancer)
        
        result = tools.extract_metadata(
            content="pytest tutorial...",
            schema="Extract language and framework"
        )
        
        assert result["language"] == "python"
        assert result["framework"] == "pytest"
    
    @patch('contextframe.enhance.base.llm.call')
    def test_generate_tags_tool(self, mock_llm_call):
        """Test the generate_tags tool."""
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    mock_response = Mock()
                    mock_response.tags = ["python", "testing", "pytest", "TDD"]
                    return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        enhancer = ContextEnhancer()
        tools = EnhancementTools(enhancer)
        
        result = tools.generate_tags(
            content="Test-driven development with pytest",
            tag_types="technologies and methodologies",
            max_tags=5
        )
        
        assert len(result) == 4
        assert "python" in result
        assert "pytest" in result


class TestPromptTemplates:
    """Test prompt template functionality."""
    
    def test_get_prompt_template(self):
        """Test retrieving prompt templates."""
        template = get_prompt_template("context", "technical_summary")
        assert "technical problem" in template
        assert "{content}" in template
        
        template = get_prompt_template("tags", "technical_tags")
        assert "Programming languages" in template
        assert "{content}" in template
    
    def test_list_available_prompts(self):
        """Test listing available prompts."""
        prompts = list_available_prompts()
        
        assert isinstance(prompts, dict)
        assert "context" in prompts
        assert "tags" in prompts
        assert "metadata" in prompts
        assert "relationships" in prompts
        
        assert "technical_summary" in prompts["context"]
        assert "technical_tags" in prompts["tags"]
    
    def test_build_enhancement_prompt(self):
        """Test building custom prompts."""
        prompt = build_enhancement_prompt(
            task="Extract key information",
            fields=["summary", "technologies"],
            context="For a technical blog",
            examples="summary: Brief overview\ntechnologies: Python, FastAPI"
        )
        
        assert "Extract key information" in prompt
        assert "- summary" in prompt
        assert "- technologies" in prompt
        assert "For a technical blog" in prompt
        assert "Examples:" in prompt
        assert "{content}" in prompt


class TestFrameDatasetEnhance:
    """Test FrameDataset.enhance() integration."""
    
    @patch('contextframe.enhance.base.llm.call')
    def test_dataset_enhance_method(self, mock_llm_call):
        """Test the convenience enhance method on FrameDataset."""
        import shutil
        from pathlib import Path
        
        # Clean up any existing test dataset
        test_path = Path("test_enhance.lance")
        if test_path.exists():
            shutil.rmtree(test_path)
        
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    mock_response = Mock()
                    mock_response.context = "Test context"
                    return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        # Create dataset with test data
        dataset = FrameDataset.create("test_enhance.lance", overwrite=True)
        frame = FrameRecord.create(
            title="Test Document",
            content="Test content",
            uri="test.md"
        )
        dataset.add(frame)
        
        # Use the enhance method
        results = dataset.enhance({
            "context": "Add a test context"
        })
        
        # Check that enhancement results show success
        assert len(results) == 1
        assert results[0].success
        assert results[0].field_name == "context"
        assert results[0].value == "Test context"
        
        # Verify enhancement by reading back from dataset
        # Since we're using Lance's update method, we need to re-read the record
        enhanced_record = dataset.get_by_uuid(frame.uuid)
        assert enhanced_record is not None
        assert enhanced_record.metadata.get("context") == "Test context"
        
        # Cleanup
        import shutil
        shutil.rmtree("test_enhance.lance")


class TestEnhancementIntegration:
    """Integration tests with mocked LLM."""
    
    @patch('contextframe.enhance.base.llm.call')
    def test_full_enhancement_workflow(self, mock_llm_call):
        """Test complete enhancement workflow."""
        import shutil
        from pathlib import Path
        
        # Clean up any existing test dataset
        test_path = Path("integration_test.lance")
        if test_path.exists():
            shutil.rmtree(test_path)
            
        call_count = 0
        
        def mock_decorator(provider, model, response_model, **kwargs):
            def decorator(func):
                def wrapper(messages):
                    nonlocal call_count
                    call_count += 1
                    
                    if response_model.__name__ == "ContextResponse":
                        mock_response = Mock()
                        mock_response.context = "This document teaches RAG architecture"
                        return mock_response
                    elif response_model.__name__ == "TagsResponse":
                        mock_response = Mock()
                        mock_response.tags = ["RAG", "embeddings", "retrieval", "LLM"]
                        return mock_response
                    elif response_model.__name__ == "CustomMetadataResponse":
                        mock_response = Mock()
                        mock_response.metadata = {"complexity": 4, "audience": "developers"}
                        return mock_response
                return wrapper
            return decorator
        
        mock_llm_call.side_effect = mock_decorator
        
        # Create dataset
        dataset = FrameDataset.create("integration_test.lance", overwrite=True)
        frames = [
            FrameRecord.create(
                title="RAG Basics",
                content="Introduction to RAG...",
                uri="doc1.md"
            ),
        ]
        dataset.add_many(frames)
        
        # Enhance
        enhancer = ContextEnhancer()
        enhancer.enhance_dataset(
            dataset,
            enhancements={
                "context": "Explain what this teaches",
                "tags": "Extract topics",
                "custom_metadata": "Extract complexity and audience as JSON"
            }
        )
        
        # Verify by reading back the enhanced record
        enhanced_record = dataset.get_by_uuid(frames[0].uuid)
        assert enhanced_record is not None
        
        assert enhanced_record.metadata.get("context") == "This document teaches RAG architecture"
        
        tags = enhanced_record.metadata.get("tags", [])
        assert "RAG" in tags
        
        # Custom metadata should be a dict with string values
        custom_meta = enhanced_record.metadata.get("custom_metadata", {})
        assert custom_meta["complexity"] == "4"
        assert custom_meta["audience"] == "developers"
        
        # Cleanup
        import shutil
        shutil.rmtree("integration_test.lance")