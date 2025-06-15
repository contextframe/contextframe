"""Template for research and academic documents."""

import re
from ..frame import FrameDataset
from .base import (
    CollectionDefinition,
    ContextTemplate,
    EnrichmentSuggestion,
    FileMapping,
)
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ResearchTemplate(ContextTemplate):
    """Template for research papers and academic documents.
    
    Handles:
    - Research papers (PDF, LaTeX, Markdown)
    - Literature reviews and citations
    - Data files and notebooks
    - Presentation slides
    - Author information
    
    Automatically:
    - Extracts paper metadata (title, authors, abstract)
    - Creates citation relationships
    - Groups papers by topic/category
    - Suggests academic enrichments
    """
    
    # Document patterns
    PAPER_EXTENSIONS = {".pdf", ".tex", ".md", ".docx", ".doc"}
    DATA_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".parquet", ".h5", ".hdf5"}
    NOTEBOOK_EXTENSIONS = {".ipynb", ".rmd"}
    PRESENTATION_EXTENSIONS = {".pptx", ".ppt", ".key", ".odp"}
    
    # Common research directories
    PAPERS_DIRS = {"papers", "articles", "publications", "manuscripts"}
    DATA_DIRS = {"data", "datasets", "raw_data", "processed_data"}
    FIGURES_DIRS = {"figures", "plots", "images", "graphics"}
    RESULTS_DIRS = {"results", "output", "analysis"}
    
    def __init__(self):
        """Initialize the research template."""
        super().__init__(
            name="research",
            description="Template for research papers, academic documents, and scientific data"
        )
        
    def scan(self, source_path: str | Path) -> list[FileMapping]:
        """Scan research directory and map documents."""
        source_path = self.validate_source(source_path)
        mappings = []
        seen_paths = set()
        
        # Look for common research structures
        self._scan_papers_directory(source_path, mappings, seen_paths)
        self._scan_data_directory(source_path, mappings, seen_paths)
        self._scan_notebooks(source_path, mappings, seen_paths)
        self._scan_bibliography(source_path, mappings, seen_paths)
        
        # Scan root for additional papers
        for file_path in source_path.iterdir():
            if file_path.is_file() and file_path not in seen_paths:
                if file_path.suffix in self.PAPER_EXTENSIONS:
                    mappings.append(self._create_paper_mapping(file_path))
                    seen_paths.add(file_path)
                elif file_path.suffix in self.PRESENTATION_EXTENSIONS:
                    mappings.append(self._create_presentation_mapping(file_path))
                    seen_paths.add(file_path)
                    
        return mappings
        
    def _scan_papers_directory(self, base_path: Path, mappings: list[FileMapping], seen_paths: set):
        """Scan for research papers."""
        for dir_name in self.PAPERS_DIRS:
            papers_dir = base_path / dir_name
            if papers_dir.exists() and papers_dir.is_dir():
                for file_path in papers_dir.rglob("*"):
                    if file_path.is_file() and file_path not in seen_paths:
                        if file_path.suffix in self.PAPER_EXTENSIONS:
                            mapping = self._create_paper_mapping(file_path)
                            
                            # Try to categorize by subdirectory
                            rel_path = file_path.relative_to(papers_dir)
                            if len(rel_path.parts) > 1:
                                category = rel_path.parts[0]
                                mapping.collection = f"papers/{category}"
                                mapping.tags.append(category.lower())
                            else:
                                mapping.collection = "papers"
                                
                            mappings.append(mapping)
                            seen_paths.add(file_path)
                            
    def _scan_data_directory(self, base_path: Path, mappings: list[FileMapping], seen_paths: set):
        """Scan for data files."""
        for dir_name in self.DATA_DIRS:
            data_dir = base_path / dir_name
            if data_dir.exists() and data_dir.is_dir():
                for file_path in data_dir.rglob("*"):
                    if file_path.is_file() and file_path not in seen_paths:
                        if file_path.suffix in self.DATA_EXTENSIONS:
                            mappings.append(FileMapping(
                                path=file_path,
                                title=f"Dataset - {file_path.stem}",
                                collection="data",
                                tags=["data", "dataset", file_path.suffix[1:]],
                                custom_metadata={
                                    "data_type": file_path.suffix[1:],
                                    "data_category": self._categorize_data(file_path.name)
                                }
                            ))
                            seen_paths.add(file_path)
                            
    def _scan_notebooks(self, base_path: Path, mappings: list[FileMapping], seen_paths: set):
        """Scan for computational notebooks."""
        for file_path in base_path.rglob("*"):
            if file_path.is_file() and file_path not in seen_paths:
                if file_path.suffix in self.NOTEBOOK_EXTENSIONS:
                    # Determine notebook type
                    notebook_type = "analysis"
                    name_lower = file_path.stem.lower()
                    if "experiment" in name_lower:
                        notebook_type = "experiment"
                    elif "explore" in name_lower or "eda" in name_lower:
                        notebook_type = "exploration"
                    elif "model" in name_lower or "train" in name_lower:
                        notebook_type = "modeling"
                        
                    mappings.append(FileMapping(
                        path=file_path,
                        title=f"Notebook - {file_path.stem}",
                        collection="notebooks",
                        tags=["notebook", notebook_type, "computational"],
                        custom_metadata={
                            "notebook_type": notebook_type,
                            "format": file_path.suffix[1:]
                        }
                    ))
                    seen_paths.add(file_path)
                    
    def _scan_bibliography(self, base_path: Path, mappings: list[FileMapping], seen_paths: set):
        """Scan for bibliography files."""
        bib_patterns = ["*.bib", "*.bibtex", "references.*", "bibliography.*", "citations.*"]
        
        for pattern in bib_patterns:
            for file_path in base_path.rglob(pattern):
                if file_path.is_file() and file_path not in seen_paths:
                    mappings.append(FileMapping(
                        path=file_path,
                        title=f"Bibliography - {file_path.name}",
                        tags=["bibliography", "references", "citations"],
                        custom_metadata={
                            "bib_type": "bibtex" if file_path.suffix in [".bib", ".bibtex"] else "other",
                            "priority": "high"
                        }
                    ))
                    seen_paths.add(file_path)
                    
    def _create_paper_mapping(self, file_path: Path) -> FileMapping:
        """Create mapping for a research paper."""
        # Try to extract metadata from filename
        tags = ["paper", "research", file_path.suffix[1:]]
        custom_meta = {"document_type": "paper"}
        
        # Common filename patterns
        name = file_path.stem
        year_match = re.search(r'(\d{4})', name)
        if year_match:
            custom_meta["year"] = year_match.group(1)
            tags.append(f"year:{year_match.group(1)}")
            
        # Check for common paper types in filename
        name_lower = name.lower()
        if "review" in name_lower:
            tags.append("review")
            custom_meta["paper_type"] = "review"
        elif "survey" in name_lower:
            tags.append("survey") 
            custom_meta["paper_type"] = "survey"
        elif "thesis" in name_lower:
            tags.append("thesis")
            custom_meta["paper_type"] = "thesis"
        elif "dissertation" in name_lower:
            tags.append("dissertation")
            custom_meta["paper_type"] = "dissertation"
            
        return FileMapping(
            path=file_path,
            title=f"Paper - {name}",
            tags=tags,
            custom_metadata=custom_meta
        )
        
    def _create_presentation_mapping(self, file_path: Path) -> FileMapping:
        """Create mapping for a presentation."""
        tags = ["presentation", "slides", file_path.suffix[1:]]
        
        # Check for presentation type
        name_lower = file_path.stem.lower()
        if "poster" in name_lower:
            tags.append("poster")
            pres_type = "poster"
        elif "talk" in name_lower or "presentation" in name_lower:
            tags.append("talk")
            pres_type = "talk"
        elif "defense" in name_lower:
            tags.append("defense")
            pres_type = "defense"
        else:
            pres_type = "general"
            
        return FileMapping(
            path=file_path,
            title=f"Presentation - {file_path.stem}",
            collection="presentations",
            tags=tags,
            custom_metadata={
                "presentation_type": pres_type,
                "format": file_path.suffix[1:]
            }
        )
        
    def define_collections(self, file_mappings: list[FileMapping]) -> list[CollectionDefinition]:
        """Define collections for research documents."""
        collections = []
        seen_collections = set()
        
        # Core research collections
        collection_defs = [
            ("papers", "Research Papers", "Published and draft research papers", ["papers", "research"]),
            ("data", "Datasets", "Research data and datasets", ["data", "datasets"]),
            ("notebooks", "Computational Notebooks", "Analysis notebooks and experiments", ["notebooks", "analysis"]),
            ("presentations", "Presentations", "Slides and poster presentations", ["presentations", "slides"]),
            ("bibliography", "References", "Bibliography and citations", ["references", "citations"])
        ]
        
        position = 0
        for name, title, desc, tags in collection_defs:
            if any(m.collection and m.collection.startswith(name) for m in file_mappings):
                collections.append(CollectionDefinition(
                    name=name,
                    title=title,
                    description=desc,
                    tags=tags,
                    position=position
                ))
                seen_collections.add(name)
                position += 10
                
        # Add sub-collections for paper categories
        paper_subcollections = set()
        for mapping in file_mappings:
            if mapping.collection and mapping.collection.startswith("papers/"):
                parts = mapping.collection.split("/")
                if len(parts) > 1:
                    paper_subcollections.add(parts[1])
                    
        for subcoll in sorted(paper_subcollections):
            coll_name = f"papers/{subcoll}"
            if coll_name not in seen_collections:
                collections.append(CollectionDefinition(
                    name=coll_name,
                    title=f"Papers - {subcoll.title()}",
                    description=f"Research papers in {subcoll} category",
                    tags=["papers", subcoll.lower()],
                    parent="papers",
                    position=position
                ))
                position += 1
                
        return collections
        
    def discover_relationships(
        self,
        file_mappings: list[FileMapping],
        dataset: FrameDataset
    ) -> list[dict[str, Any]]:
        """Discover citation and authorship relationships."""
        relationships = []
        
        # Find bibliography files
        bib_files = [m for m in file_mappings if "bibliography" in m.tags]
        
        # Find papers
        papers = [m for m in file_mappings if "paper" in m.tags]
        
        # Create relationships between papers and bibliography
        for paper in papers:
            for bib in bib_files:
                # Check if they're in the same directory area
                if paper.path.parent == bib.path.parent:
                    relationships.append({
                        "source": str(paper.path),
                        "target": str(bib.path),
                        "type": "references",
                        "description": "Paper references bibliography"
                    })
                    
        # Find related notebooks and data
        notebooks = [m for m in file_mappings if "notebook" in m.tags]
        data_files = [m for m in file_mappings if "data" in m.tags]
        
        # Match notebooks to data files by name similarity
        for notebook in notebooks:
            nb_stem = notebook.path.stem.lower()
            for data in data_files:
                data_stem = data.path.stem.lower()
                # Simple matching - could be improved
                if data_stem in nb_stem or nb_stem in data_stem:
                    relationships.append({
                        "source": str(notebook.path),
                        "target": str(data.path), 
                        "type": "uses",
                        "description": "Notebook analyzes dataset"
                    })
                    
        return relationships
        
    def suggest_enrichments(self, file_mappings: list[FileMapping]) -> list[EnrichmentSuggestion]:
        """Suggest research-specific enrichments."""
        suggestions = []
        
        # Paper enrichments
        suggestions.append(EnrichmentSuggestion(
            file_pattern="**/*.pdf",
            enhancement_config={
                "enhancements": {
                    "context": "research_context",
                    "tags": "Extract: authors, keywords, research area, methodology",
                    "custom_metadata": "research_metadata"
                }
            },
            priority=10
        ))
        
        # Notebook enrichments
        suggestions.append(EnrichmentSuggestion(
            file_pattern="**/*.ipynb",
            enhancement_config={
                "enhancements": {
                    "context": "Summarize the analysis performed and key findings",
                    "custom_metadata": {
                        "libraries_used": "List main Python/R libraries used",
                        "analysis_type": "Type of analysis (statistical, ML, visualization)",
                        "key_findings": "Main results or insights"
                    }
                }
            },
            priority=8
        ))
        
        # Data file enrichments
        suggestions.append(EnrichmentSuggestion(
            file_pattern="**/*.csv",
            enhancement_config={
                "enhancements": {
                    "context": "Describe the dataset structure and content",
                    "custom_metadata": {
                        "columns": "List main columns/features",
                        "row_count": "Number of records",
                        "data_source": "Origin of the data"
                    }
                }
            },
            priority=5
        ))
        
        # Bibliography enrichments
        suggestions.append(EnrichmentSuggestion(
            file_pattern="**/*.bib",
            enhancement_config={
                "enhancements": {
                    "context": "Summarize the types of references and research areas covered",
                    "custom_metadata": {
                        "entry_count": "Number of bibliography entries",
                        "publication_years": "Range of publication years",
                        "key_authors": "Most frequently cited authors"
                    }
                }
            },
            priority=7
        ))
        
        return suggestions
        
    def _categorize_data(self, filename: str) -> str:
        """Categorize data files."""
        name_lower = filename.lower()
        if "raw" in name_lower:
            return "raw"
        elif "processed" in name_lower or "clean" in name_lower:
            return "processed"
        elif "results" in name_lower or "output" in name_lower:
            return "results"
        elif "meta" in name_lower:
            return "metadata"
        else:
            return "general"