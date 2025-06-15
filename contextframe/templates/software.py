"""Template for software projects."""

import re
from ..frame import FrameDataset
from .base import (
    CollectionDefinition,
    ContextTemplate,
    EnrichmentSuggestion,
    FileMapping,
)
from pathlib import Path
from typing import Any, Dict, List, Union


class SoftwareProjectTemplate(ContextTemplate):
    """Template for software development projects.
    
    Recognizes common project structures:
    - Source code (src/, lib/, app/)
    - Tests (tests/, test/, spec/)
    - Documentation (docs/, doc/)
    - Configuration files
    - Build/deployment files
    
    Automatically:
    - Groups files by module/package
    - Links tests to source files
    - Identifies dependencies
    - Suggests code-specific enrichments
    """
    
    # Common source directories
    SOURCE_DIRS = {"src", "lib", "app", "source", "sources"}
    TEST_DIRS = {"tests", "test", "spec", "specs", "__tests__"}
    DOC_DIRS = {"docs", "doc", "documentation"}
    
    # File patterns
    CODE_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", 
        ".hpp", ".cs", ".rb", ".go", ".rs", ".swift", ".kt", ".scala",
        ".php", ".r", ".m", ".mm", ".f90", ".jl", ".lua", ".dart"
    }
    
    CONFIG_FILES = {
        "package.json", "requirements.txt", "setup.py", "pyproject.toml",
        "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "CMakeLists.txt",
        "Makefile", "Dockerfile", ".gitignore", ".dockerignore"
    }
    
    DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}
    
    def __init__(self):
        """Initialize the software project template."""
        super().__init__(
            name="software_project",
            description="Template for software development projects with source code, tests, and documentation"
        )
        
    def scan(self, source_path: str | Path) -> list[FileMapping]:
        """Scan project directory and map files."""
        source_path = self.validate_source(source_path)
        mappings = []
        
        # Track seen files to avoid duplicates
        seen_paths = set()
        
        # Scan for README first (project overview)
        for readme in ["README.md", "README.rst", "README.txt", "readme.md"]:
            readme_path = source_path / readme
            if readme_path.exists() and readme_path not in seen_paths:
                mappings.append(FileMapping(
                    path=readme_path,
                    title=f"Project Overview - {source_path.name}",
                    tags=["readme", "overview", "documentation"],
                    custom_metadata={"priority": "high"}
                ))
                seen_paths.add(readme_path)
                
        # Scan source directories
        for dir_name in self.SOURCE_DIRS:
            src_dir = source_path / dir_name
            if src_dir.exists() and src_dir.is_dir():
                mappings.extend(self._scan_code_directory(src_dir, "source", seen_paths))
                
        # Scan test directories
        for dir_name in self.TEST_DIRS:
            test_dir = source_path / dir_name
            if test_dir.exists() and test_dir.is_dir():
                mappings.extend(self._scan_code_directory(test_dir, "test", seen_paths))
                
        # Scan documentation
        for dir_name in self.DOC_DIRS:
            doc_dir = source_path / dir_name
            if doc_dir.exists() and doc_dir.is_dir():
                mappings.extend(self._scan_doc_directory(doc_dir, seen_paths))
                
        # Scan root-level config files
        for config_file in self.CONFIG_FILES:
            config_path = source_path / config_file
            if config_path.exists() and config_path not in seen_paths:
                mappings.append(FileMapping(
                    path=config_path,
                    title=f"Configuration - {config_file}",
                    tags=["configuration", self._get_config_type(config_file)],
                    custom_metadata={"config_type": self._get_config_type(config_file)}
                ))
                seen_paths.add(config_path)
                
        # Scan for other code files in root
        for file_path in source_path.iterdir():
            if file_path.is_file() and file_path.suffix in self.CODE_EXTENSIONS:
                if file_path not in seen_paths:
                    mappings.append(FileMapping(
                        path=file_path,
                        title=f"Code - {file_path.name}",
                        collection="root",
                        tags=["code", self._get_language_tag(file_path.suffix)],
                        custom_metadata={"code_type": "script"}
                    ))
                    seen_paths.add(file_path)
                    
        return mappings
        
    def _scan_code_directory(self, directory: Path, category: str, seen_paths: set) -> list[FileMapping]:
        """Scan a code directory recursively."""
        mappings = []
        
        for file_path in directory.rglob("*"):
            if file_path in seen_paths or not file_path.is_file():
                continue
                
            # Skip hidden files and __pycache__
            if any(part.startswith(".") or part == "__pycache__" for part in file_path.parts):
                continue
                
            if file_path.suffix in self.CODE_EXTENSIONS:
                # Determine module/package structure
                rel_path = file_path.relative_to(directory)
                module_parts = list(rel_path.parts[:-1])
                
                # Create collection name from module path
                collection = None
                if module_parts:
                    collection = "/".join(module_parts)
                    
                # Determine if it's a test file
                is_test = (category == "test" or 
                          any(part in file_path.name.lower() for part in ["test", "spec"]))
                
                mappings.append(FileMapping(
                    path=file_path,
                    title=f"{'Test' if is_test else 'Code'} - {file_path.stem}",
                    collection=collection,
                    tags=[
                        category,
                        self._get_language_tag(file_path.suffix),
                        "test" if is_test else "implementation"
                    ],
                    custom_metadata={
                        "module": "/".join(module_parts) if module_parts else "root",
                        "language": self._get_language_tag(file_path.suffix),
                        "file_type": "test" if is_test else "source"
                    }
                ))
                seen_paths.add(file_path)
                
        return mappings
        
    def _scan_doc_directory(self, directory: Path, seen_paths: set) -> list[FileMapping]:
        """Scan documentation directory."""
        mappings = []
        
        for file_path in directory.rglob("*"):
            if file_path in seen_paths or not file_path.is_file():
                continue
                
            if file_path.suffix in self.DOC_EXTENSIONS:
                rel_path = file_path.relative_to(directory)
                
                mappings.append(FileMapping(
                    path=file_path,
                    title=f"Documentation - {file_path.stem}",
                    collection="documentation",
                    tags=["documentation", file_path.suffix[1:]],
                    custom_metadata={
                        "doc_path": str(rel_path),
                        "doc_type": self._categorize_doc(file_path.name)
                    }
                ))
                seen_paths.add(file_path)
                
        return mappings
        
    def define_collections(self, file_mappings: list[FileMapping]) -> list[CollectionDefinition]:
        """Define collections based on project structure."""
        collections = []
        seen_collections = set()
        
        # Main project collection
        collections.append(CollectionDefinition(
            name="project",
            title="Project Overview",
            description="Top-level project information and configuration",
            tags=["project", "overview"],
            position=0
        ))
        
        # Extract unique collections from mappings
        for mapping in file_mappings:
            if mapping.collection and mapping.collection not in seen_collections:
                # Determine collection type
                if mapping.collection == "documentation":
                    collections.append(CollectionDefinition(
                        name="documentation",
                        title="Documentation",
                        description="Project documentation and guides",
                        tags=["documentation"],
                        position=1
                    ))
                elif "/" in mapping.collection:
                    # Module/package collection
                    parts = mapping.collection.split("/")
                    parent = None
                    
                    # Create nested collections for module hierarchy
                    for i, part in enumerate(parts):
                        coll_name = "/".join(parts[:i+1])
                        if coll_name not in seen_collections:
                            collections.append(CollectionDefinition(
                                name=coll_name,
                                title=f"Module: {part}",
                                description=f"Code module {coll_name}",
                                tags=["module", "code"],
                                parent=parent,
                                position=10 + i
                            ))
                            seen_collections.add(coll_name)
                        parent = coll_name
                        
                seen_collections.add(mapping.collection)
                
        # Add test collection if we have tests
        if any("test" in m.tags for m in file_mappings):
            collections.append(CollectionDefinition(
                name="tests",
                title="Test Suite",
                description="Project test files and specifications",
                tags=["tests", "quality"],
                position=20
            ))
            
        return collections
        
    def discover_relationships(
        self, 
        file_mappings: list[FileMapping],
        dataset: FrameDataset
    ) -> list[dict[str, Any]]:
        """Discover relationships between source files and tests."""
        relationships = []
        
        # Create lookup maps
        source_files = {}
        test_files = {}
        
        for mapping in file_mappings:
            if "test" in mapping.tags:
                test_files[mapping.path.stem] = mapping
            elif "implementation" in mapping.custom_metadata.get("file_type", ""):
                source_files[mapping.path.stem] = mapping
                
        # Match tests to source files
        for test_name, test_mapping in test_files.items():
            # Common patterns: test_foo.py -> foo.py, foo_test.py -> foo.py
            source_name = None
            if test_name.startswith("test_"):
                source_name = test_name[5:]
            elif test_name.endswith("_test"):
                source_name = test_name[:-5]
            elif test_name.endswith("Test") or test_name.endswith("Spec"):
                source_name = test_name[:-4]
                
            if source_name and source_name in source_files:
                relationships.append({
                    "source": str(test_mapping.path),
                    "target": str(source_files[source_name].path),
                    "type": "tests",
                    "description": f"Tests for {source_name}"
                })
                
        # Discover import relationships (simplified - would need AST parsing)
        # This is a placeholder for more sophisticated analysis
        
        return relationships
        
    def suggest_enrichments(self, file_mappings: list[FileMapping]) -> list[EnrichmentSuggestion]:
        """Suggest code-specific enrichments."""
        suggestions = []
        
        # Source code enrichments
        suggestions.append(EnrichmentSuggestion(
            file_pattern="**/*.py",
            enhancement_config={
                "enhancements": {
                    "context": "technical_summary",
                    "tags": "technical_tags", 
                    "custom_metadata": "code_metadata"
                }
            },
            priority=10
        ))
        
        # Test file enrichments
        suggestions.append(EnrichmentSuggestion(
            file_pattern="**/test_*.py",
            enhancement_config={
                "enhancements": {
                    "context": "Explain what this test validates and why it's important",
                    "custom_metadata": {
                        "test_type": "Identify test type: unit, integration, or e2e",
                        "coverage": "What code areas does this test cover?"
                    }
                }
            },
            priority=8
        ))
        
        # Documentation enrichments
        suggestions.append(EnrichmentSuggestion(
            file_pattern="**/*.md",
            enhancement_config={
                "enhancements": {
                    "context": "tutorial_context",
                    "tags": "topic_tags"
                }
            },
            priority=5
        ))
        
        # Config file enrichments
        suggestions.append(EnrichmentSuggestion(
            file_pattern="**/package.json",
            enhancement_config={
                "enhancements": {
                    "custom_metadata": {
                        "dependencies": "List key dependencies",
                        "scripts": "List available npm scripts"
                    }
                }
            },
            priority=3
        ))
        
        return suggestions
        
    def _get_language_tag(self, extension: str) -> str:
        """Map file extension to language tag."""
        lang_map = {
            ".py": "python",
            ".js": "javascript", 
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
            ".jl": "julia"
        }
        return lang_map.get(extension, extension[1:])
        
    def _get_config_type(self, filename: str) -> str:
        """Categorize configuration file."""
        config_types = {
            "package.json": "npm",
            "requirements.txt": "pip",
            "setup.py": "python",
            "pyproject.toml": "python",
            "Cargo.toml": "cargo",
            "go.mod": "go",
            "pom.xml": "maven",
            "build.gradle": "gradle",
            "CMakeLists.txt": "cmake",
            "Makefile": "make",
            "Dockerfile": "docker"
        }
        return config_types.get(filename, "config")
        
    def _categorize_doc(self, filename: str) -> str:
        """Categorize documentation file."""
        name_lower = filename.lower()
        if "api" in name_lower:
            return "api"
        elif "guide" in name_lower or "tutorial" in name_lower:
            return "guide"
        elif "reference" in name_lower:
            return "reference"
        elif "changelog" in name_lower or "history" in name_lower:
            return "changelog"
        elif "contributing" in name_lower:
            return "contributing"
        else:
            return "general"