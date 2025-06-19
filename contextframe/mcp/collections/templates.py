"""Collection template system for pre-configured collection structures."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CollectionTemplate(BaseModel):
    """Defines a collection template structure."""
    
    name: str = Field(..., description="Template identifier")
    display_name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template description")
    structure: Dict[str, Any] = Field(..., description="Hierarchical structure definition")
    default_metadata: Dict[str, Any] = Field(default_factory=dict, description="Default metadata for collections")
    naming_pattern: Optional[str] = Field(None, description="Naming pattern for collections")
    auto_organize_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Auto-organization rules")
    icon: Optional[str] = Field(None, description="Icon identifier for UI")


class TemplateRegistry:
    """Registry for collection templates."""
    
    def __init__(self):
        """Initialize with built-in templates."""
        self.templates: Dict[str, CollectionTemplate] = {}
        self._register_builtin_templates()
    
    def register_template(self, template: CollectionTemplate) -> None:
        """Register a new template."""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[CollectionTemplate]:
        """Get template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {
                "name": template.name,
                "display_name": template.display_name,
                "description": template.description,
                "icon": template.icon
            }
            for template in self.templates.values()
        ]
    
    def _register_builtin_templates(self) -> None:
        """Register built-in templates."""
        
        # Project template
        self.register_template(CollectionTemplate(
            name="project",
            display_name="Software Project",
            description="Organize software project documentation, code, and resources",
            structure={
                "root": {
                    "name": "{project_name}",
                    "description": "Project root collection",
                    "subcollections": {
                        "docs": {
                            "name": "Documentation",
                            "description": "Project documentation",
                            "metadata": {"x_category": "documentation"}
                        },
                        "src": {
                            "name": "Source Code",
                            "description": "Implementation files",
                            "metadata": {"x_category": "implementation"}
                        },
                        "tests": {
                            "name": "Tests",
                            "description": "Test files and fixtures",
                            "metadata": {"x_category": "testing"}
                        },
                        "examples": {
                            "name": "Examples",
                            "description": "Usage examples and tutorials",
                            "metadata": {"x_category": "examples"}
                        }
                    }
                }
            },
            default_metadata={
                "x_template": "project",
                "x_domain": "software"
            },
            naming_pattern="{name}-{category}",
            auto_organize_rules=[
                {
                    "pattern": "*.md",
                    "target": "docs",
                    "exclude": ["README.md", "CHANGELOG.md"]
                },
                {
                    "pattern": "src/**/*",
                    "target": "src"
                },
                {
                    "pattern": "test*/**/*",
                    "target": "tests"
                },
                {
                    "pattern": "example*/**/*",
                    "target": "examples"
                }
            ],
            icon="folder-code"
        ))
        
        # Research template
        self.register_template(CollectionTemplate(
            name="research",
            display_name="Research Papers",
            description="Organize academic papers, citations, and research materials",
            structure={
                "root": {
                    "name": "{research_topic}",
                    "description": "Research collection",
                    "subcollections": {
                        "by_year": {
                            "name": "Papers by Year",
                            "description": "Organized by publication year",
                            "dynamic": True,
                            "pattern": "{year}"
                        },
                        "by_topic": {
                            "name": "Papers by Topic",
                            "description": "Organized by research topic",
                            "dynamic": True,
                            "pattern": "{topic}"
                        },
                        "by_author": {
                            "name": "Papers by Author",
                            "description": "Organized by primary author",
                            "dynamic": True,
                            "pattern": "{author_lastname}"
                        },
                        "citations": {
                            "name": "Citation Network",
                            "description": "Citation relationships",
                            "metadata": {"x_type": "citations"}
                        },
                        "notes": {
                            "name": "Research Notes",
                            "description": "Personal notes and summaries",
                            "metadata": {"x_type": "notes"}
                        }
                    }
                }
            },
            default_metadata={
                "x_template": "research",
                "x_domain": "academic"
            },
            naming_pattern="{year}-{authors}-{title}",
            auto_organize_rules=[
                {
                    "metadata_field": "year",
                    "target": "by_year/{value}"
                },
                {
                    "metadata_field": "primary_topic",
                    "target": "by_topic/{value}"
                },
                {
                    "metadata_field": "first_author_lastname",
                    "target": "by_author/{value}"
                }
            ],
            icon="academic-cap"
        ))
        
        # Knowledge base template
        self.register_template(CollectionTemplate(
            name="knowledge_base",
            display_name="Knowledge Base",
            description="Hierarchical organization for documentation and guides",
            structure={
                "root": {
                    "name": "{kb_name} Knowledge Base",
                    "description": "Knowledge base root",
                    "subcollections": {
                        "getting_started": {
                            "name": "Getting Started",
                            "description": "Introduction and quick start guides",
                            "metadata": {"x_priority": "high"}
                        },
                        "tutorials": {
                            "name": "Tutorials",
                            "description": "Step-by-step tutorials",
                            "metadata": {"x_difficulty": "intermediate"}
                        },
                        "reference": {
                            "name": "Reference",
                            "description": "API and reference documentation",
                            "metadata": {"x_type": "reference"}
                        },
                        "troubleshooting": {
                            "name": "Troubleshooting",
                            "description": "Common issues and solutions",
                            "metadata": {"x_type": "troubleshooting"}
                        },
                        "faq": {
                            "name": "FAQ",
                            "description": "Frequently asked questions",
                            "metadata": {"x_type": "faq"}
                        }
                    }
                }
            },
            default_metadata={
                "x_template": "knowledge_base",
                "x_domain": "documentation",
                "x_searchable": True
            },
            naming_pattern="{category}-{title}",
            auto_organize_rules=[
                {
                    "content_pattern": "getting started|quick start|introduction",
                    "target": "getting_started"
                },
                {
                    "content_pattern": "tutorial|how to|step by step",
                    "target": "tutorials"
                },
                {
                    "content_pattern": "api|reference|specification",
                    "target": "reference"
                },
                {
                    "content_pattern": "error|issue|problem|fix",
                    "target": "troubleshooting"
                },
                {
                    "content_pattern": "frequently asked|faq|common question",
                    "target": "faq"
                }
            ],
            icon="book-open"
        ))
        
        # Dataset template
        self.register_template(CollectionTemplate(
            name="dataset",
            display_name="Training Dataset",
            description="Organize datasets for machine learning and AI training",
            structure={
                "root": {
                    "name": "{dataset_name}",
                    "description": "Dataset collection",
                    "subcollections": {
                        "train": {
                            "name": "Training Set",
                            "description": "Training data",
                            "metadata": {"x_split": "train", "x_ratio": 0.8}
                        },
                        "validation": {
                            "name": "Validation Set",
                            "description": "Validation data",
                            "metadata": {"x_split": "validation", "x_ratio": 0.1}
                        },
                        "test": {
                            "name": "Test Set",
                            "description": "Test data",
                            "metadata": {"x_split": "test", "x_ratio": 0.1}
                        },
                        "raw": {
                            "name": "Raw Data",
                            "description": "Unprocessed source data",
                            "metadata": {"x_processed": False}
                        },
                        "metadata": {
                            "name": "Dataset Metadata",
                            "description": "Labels, annotations, and dataset info",
                            "metadata": {"x_type": "metadata"}
                        }
                    }
                }
            },
            default_metadata={
                "x_template": "dataset",
                "x_domain": "ml",
                "x_version": "1.0"
            },
            naming_pattern="{split}-{index:06d}",
            auto_organize_rules=[
                {
                    "random_split": True,
                    "ratios": {
                        "train": 0.8,
                        "validation": 0.1,
                        "test": 0.1
                    }
                }
            ],
            icon="database"
        ))
        
        # Legal template
        self.register_template(CollectionTemplate(
            name="legal",
            display_name="Legal Documents",
            description="Organize contracts, agreements, and legal documents",
            structure={
                "root": {
                    "name": "{case_or_matter_name}",
                    "description": "Legal matter collection",
                    "subcollections": {
                        "contracts": {
                            "name": "Contracts & Agreements",
                            "description": "Executed contracts and agreements",
                            "metadata": {"x_type": "contract", "x_confidential": True}
                        },
                        "correspondence": {
                            "name": "Correspondence",
                            "description": "Letters, emails, and communications",
                            "metadata": {"x_type": "correspondence"}
                        },
                        "filings": {
                            "name": "Court Filings",
                            "description": "Court documents and filings",
                            "metadata": {"x_type": "filing"}
                        },
                        "research": {
                            "name": "Legal Research",
                            "description": "Case law, statutes, and research",
                            "metadata": {"x_type": "research"}
                        },
                        "internal": {
                            "name": "Internal Documents",
                            "description": "Internal memos and work product",
                            "metadata": {"x_type": "internal", "x_privileged": True}
                        }
                    }
                }
            },
            default_metadata={
                "x_template": "legal",
                "x_domain": "legal",
                "x_access_control": "restricted"
            },
            naming_pattern="{date}-{type}-{party}",
            auto_organize_rules=[
                {
                    "metadata_field": "document_type",
                    "mapping": {
                        "contract": "contracts",
                        "agreement": "contracts",
                        "letter": "correspondence",
                        "email": "correspondence",
                        "motion": "filings",
                        "brief": "filings",
                        "memo": "internal"
                    }
                }
            ],
            icon="scale"
        ))


def apply_template(
    template: CollectionTemplate,
    params: Dict[str, Any],
    parent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Apply a template to create collection structure.
    
    Args:
        template: The template to apply
        params: Parameters for template variables
        parent_id: Parent collection ID if creating under existing collection
        
    Returns:
        Dictionary describing the collection structure to create
    """
    # Replace template variables in structure
    structure = _replace_template_vars(template.structure, params)
    
    # Add template metadata
    if parent_id:
        structure["root"]["parent_id"] = parent_id
    
    structure["root"]["metadata"] = {
        **template.default_metadata,
        **structure["root"].get("metadata", {}),
        "x_created_from_template": template.name
    }
    
    return structure


def _replace_template_vars(obj: Any, params: Dict[str, str]) -> Any:
    """Recursively replace template variables in structure."""
    if isinstance(obj, str):
        for key, value in params.items():
            obj = obj.replace(f"{{{key}}}", str(value))
        return obj
    elif isinstance(obj, dict):
        return {k: _replace_template_vars(v, params) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_template_vars(item, params) for item in obj]
    else:
        return obj