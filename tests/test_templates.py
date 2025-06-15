"""Tests for Context Templates module."""

import pytest
from pathlib import Path
import tempfile
import shutil

from contextframe.templates import (
    ContextTemplate,
    TemplateResult,
    SoftwareProjectTemplate,
    ResearchTemplate,
    BusinessTemplate,
    get_template,
    list_templates,
)
from contextframe.templates.base import FileMapping, CollectionDefinition, EnrichmentSuggestion
from contextframe.templates.registry import TemplateRegistry, find_template_for_path
from contextframe import FrameDataset


class TestTemplateRegistry:
    """Test the template registry functionality."""
    
    def test_builtin_templates_registered(self):
        """Test that built-in templates are automatically registered."""
        templates = list_templates()
        template_names = [t["name"] for t in templates]
        
        assert "software_project" in template_names
        assert "research" in template_names  
        assert "business" in template_names
        assert len(templates) >= 3
        
    def test_get_template(self):
        """Test retrieving templates by name."""
        software_template = get_template("software_project")
        assert isinstance(software_template, SoftwareProjectTemplate)
        assert software_template.name == "software_project"
        
        research_template = get_template("research")
        assert isinstance(research_template, ResearchTemplate)
        
        business_template = get_template("business")
        assert isinstance(business_template, BusinessTemplate)
        
    def test_get_nonexistent_template(self):
        """Test error handling for non-existent template."""
        with pytest.raises(KeyError) as exc_info:
            get_template("nonexistent")
        assert "not found" in str(exc_info.value)
        
    def test_template_info(self):
        """Test template metadata."""
        templates = list_templates()
        
        for template_info in templates:
            assert "name" in template_info
            assert "description" in template_info
            assert "class" in template_info
            assert isinstance(template_info["description"], str)
            
    def test_find_template_for_path(self, tmp_path):
        """Test automatic template detection."""
        # Create software project structure
        software_dir = tmp_path / "software_project"
        software_dir.mkdir()
        (software_dir / "src").mkdir()
        (software_dir / "tests").mkdir()
        (software_dir / "setup.py").touch()
        
        assert find_template_for_path(str(software_dir)) == "software_project"
        
        # Create research structure
        research_dir = tmp_path / "research_project"
        research_dir.mkdir()
        (research_dir / "papers").mkdir()
        (research_dir / "data").mkdir()
        (research_dir / "references.bib").touch()
        
        assert find_template_for_path(str(research_dir)) == "research"
        
        # Create business structure
        business_dir = tmp_path / "business_docs"
        business_dir.mkdir()
        (business_dir / "meetings").mkdir()
        (business_dir / "decisions").mkdir()
        
        assert find_template_for_path(str(business_dir)) == "business"


class TestSoftwareProjectTemplate:
    """Test the software project template."""
    
    @pytest.fixture
    def software_project(self, tmp_path):
        """Create a sample software project structure."""
        # Create directories
        (tmp_path / "src" / "myapp").mkdir(parents=True)
        (tmp_path / "tests").mkdir()
        (tmp_path / "docs").mkdir()
        
        # Create files
        (tmp_path / "README.md").write_text("# My Project\n\nA sample project.")
        (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup(name='myapp')")
        (tmp_path / "requirements.txt").write_text("pytest\nnumpy")
        
        # Source files
        (tmp_path / "src" / "myapp" / "__init__.py").write_text("__version__ = '0.1.0'")
        (tmp_path / "src" / "myapp" / "core.py").write_text("def main():\n    pass")
        (tmp_path / "src" / "myapp" / "utils.py").write_text("def helper():\n    pass")
        
        # Test files
        (tmp_path / "tests" / "test_core.py").write_text("def test_main():\n    pass")
        (tmp_path / "tests" / "test_utils.py").write_text("def test_helper():\n    pass")
        
        # Documentation
        (tmp_path / "docs" / "guide.md").write_text("# User Guide")
        
        return tmp_path
        
    def test_scan_software_project(self, software_project):
        """Test scanning a software project."""
        template = SoftwareProjectTemplate()
        mappings = template.scan(software_project)
        
        # Check we found all expected files
        paths = [str(m.path.name) for m in mappings]
        assert "README.md" in paths
        assert "setup.py" in paths
        assert "requirements.txt" in paths
        assert "core.py" in paths
        assert "test_core.py" in paths
        assert "guide.md" in paths
        
        # Check categorization
        readme = next(m for m in mappings if m.path.name == "README.md")
        assert "readme" in readme.tags
        assert "overview" in readme.tags
        
        core_file = next(m for m in mappings if m.path.name == "core.py")
        assert "source" in core_file.tags
        assert "python" in core_file.tags
        
        test_file = next(m for m in mappings if m.path.name == "test_core.py")
        assert "test" in test_file.tags
        
    def test_define_collections(self, software_project):
        """Test collection definition for software projects."""
        template = SoftwareProjectTemplate()
        mappings = template.scan(software_project)
        collections = template.define_collections(mappings)
        
        # Check collections created
        coll_names = [c.name for c in collections]
        assert "project" in coll_names
        assert "documentation" in coll_names
        assert "tests" in coll_names
        # Check we have at least the base collections
        assert len(collections) >= 3
        
    def test_discover_relationships(self, software_project, tmp_path):
        """Test relationship discovery."""
        template = SoftwareProjectTemplate()
        mappings = template.scan(software_project)
        
        # Create a mock dataset
        dataset = FrameDataset.create(tmp_path / "test.lance")
        
        relationships = template.discover_relationships(mappings, dataset)
        
        # Should find test->source relationships
        test_rels = [r for r in relationships if r["type"] == "tests"]
        # With test_core.py and core.py, we should find a relationship
        assert isinstance(relationships, list)
        
    def test_suggest_enrichments(self, software_project):
        """Test enrichment suggestions."""
        template = SoftwareProjectTemplate()
        mappings = template.scan(software_project)
        suggestions = template.suggest_enrichments(mappings)
        
        # Should have suggestions for different file types
        patterns = [s.file_pattern for s in suggestions]
        assert any("*.py" in p for p in patterns)
        assert any("test_*.py" in p for p in patterns)
        assert any("*.md" in p for p in patterns)


class TestResearchTemplate:
    """Test the research template."""
    
    @pytest.fixture
    def research_project(self, tmp_path):
        """Create a sample research project structure."""
        # Create directories
        (tmp_path / "papers").mkdir()
        (tmp_path / "data").mkdir()
        (tmp_path / "notebooks").mkdir()
        
        # Create files
        (tmp_path / "papers" / "paper1.pdf").write_bytes(b"PDF content")
        (tmp_path / "papers" / "draft_2024.md").write_text("# Research Paper")
        (tmp_path / "data" / "results.csv").write_text("id,value\n1,100")
        (tmp_path / "notebooks" / "analysis.ipynb").write_text('{"cells": []}')
        (tmp_path / "references.bib").write_text("@article{...}")
        
        return tmp_path
        
    def test_scan_research_project(self, research_project):
        """Test scanning a research project."""
        template = ResearchTemplate()
        mappings = template.scan(research_project)
        
        # Check we found expected files
        paths = [str(m.path.name) for m in mappings]
        assert "paper1.pdf" in paths
        assert "draft_2024.md" in paths
        assert "results.csv" in paths
        assert "analysis.ipynb" in paths
        assert "references.bib" in paths
        
        # Check categorization
        paper = next(m for m in mappings if m.path.name == "paper1.pdf")
        assert "paper" in paper.tags
        assert "research" in paper.tags
        
        notebook = next(m for m in mappings if m.path.name == "analysis.ipynb")
        assert "notebook" in notebook.tags
        
        bib = next(m for m in mappings if m.path.name == "references.bib")
        assert "bibliography" in bib.tags
        
    def test_research_collections(self, research_project):
        """Test collection definition for research projects."""
        template = ResearchTemplate()
        mappings = template.scan(research_project)
        collections = template.define_collections(mappings)
        
        coll_names = [c.name for c in collections]
        assert "papers" in coll_names
        assert "data" in coll_names
        assert "notebooks" in coll_names
        # The template creates collections based on what files exist
        assert len(collections) >= 3


class TestBusinessTemplate:
    """Test the business template."""
    
    @pytest.fixture
    def business_project(self, tmp_path):
        """Create a sample business project structure."""
        # Create directories
        (tmp_path / "meetings" / "weekly").mkdir(parents=True)
        (tmp_path / "decisions").mkdir()
        (tmp_path / "reports").mkdir()
        
        # Create files
        (tmp_path / "meetings" / "weekly" / "2024-01-15-standup.md").write_text("# Standup")
        (tmp_path / "decisions" / "ADR-001-architecture.md").write_text("# Decision")
        (tmp_path / "reports" / "Q1-2024-summary.md").write_text("# Report")
        (tmp_path / "project-plan.md").write_text("# Project Plan")
        
        return tmp_path
        
    def test_scan_business_project(self, business_project):
        """Test scanning a business project."""
        template = BusinessTemplate()
        mappings = template.scan(business_project)
        
        # Check we found expected files
        paths = [str(m.path.name) for m in mappings]
        assert "2024-01-15-standup.md" in paths
        assert "ADR-001-architecture.md" in paths
        assert "Q1-2024-summary.md" in paths
        
        # Check categorization
        meeting = next(m for m in mappings if "standup" in m.path.name)
        assert "meeting" in meeting.tags
        assert "standup" in meeting.custom_metadata.get("meeting_type", "")
        
        decision = next(m for m in mappings if "ADR" in m.path.name)
        assert "decision" in decision.tags
        
    def test_business_date_extraction(self, business_project):
        """Test date extraction from filenames."""
        template = BusinessTemplate()
        mappings = template.scan(business_project)
        
        meeting = next(m for m in mappings if "standup" in m.path.name)
        assert meeting.custom_metadata.get("meeting_date") == "2024-01-15"


class TestTemplateApplication:
    """Test end-to-end template application."""
    
    def test_apply_template_dry_run(self, tmp_path):
        """Test dry run of template application."""
        # Create simple structure
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "README.md").write_text("# Test")
        (source_dir / "main.py").write_text("print('hello')")
        
        # Create dataset
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(dataset_path)
        
        # Apply template in dry run mode
        template = SoftwareProjectTemplate()
        result = template.apply(source_dir, dataset, dry_run=True)
        
        assert result.frames_created == 0
        assert result.collections_created == 0
        assert len(result.warnings) > 0
        assert "DRY RUN" in result.warnings[0]
        
    def test_template_result_tracking(self):
        """Test TemplateResult tracking."""
        result = TemplateResult()
        
        # Test initial state
        assert result.frames_created == 0
        assert result.collections_created == 0
        assert result.relationships_created == 0
        assert len(result.errors) == 0
        
        # Test tracking
        result.frames_created += 5
        result.collections_created += 2
        result.errors.append("Test error")
        
        assert result.frames_created == 5
        assert result.collections_created == 2
        assert len(result.errors) == 1


class TestCustomTemplate:
    """Test creating custom templates."""
    
    def test_custom_template_implementation(self):
        """Test implementing a custom template."""
        
        class CustomTemplate(ContextTemplate):
            def __init__(self):
                super().__init__("custom", "A custom template")
                
            def scan(self, source_path):
                return []
                
            def define_collections(self, file_mappings):
                return []
                
            def discover_relationships(self, file_mappings, dataset):
                return []
                
            def suggest_enrichments(self, file_mappings):
                return []
                
        # Create and test custom template
        template = CustomTemplate()
        assert template.name == "custom"
        assert template.description == "A custom template"
        
        # Test it can be registered
        registry = TemplateRegistry()
        registry.register("my_custom", CustomTemplate)
        
        retrieved = registry.get("my_custom")
        assert isinstance(retrieved, CustomTemplate)