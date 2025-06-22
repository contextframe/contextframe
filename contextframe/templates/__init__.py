"""Context Templates for common document organization patterns.

Templates provide pre-configured patterns for importing and structuring
documents into ContextFrame datasets. They handle:

- Document discovery and categorization
- Automatic relationship creation
- Collection organization
- Domain-specific metadata
- Enrichment suggestions

Example:
    >>> from contextframe import FrameDataset
    >>> from contextframe.templates import SoftwareProjectTemplate
    >>>
    >>> template = SoftwareProjectTemplate()
    >>> dataset = FrameDataset.create("my-project.lance")
    >>>
    >>> # Apply template to import project
    >>> results = template.apply(
    ...     source_path="~/my-project",
    ...     dataset=dataset,
    ...     auto_enhance=True
    ... )
"""

from .base import ContextTemplate, TemplateResult
from .business import BusinessTemplate
from .registry import TemplateRegistry, get_template, list_templates
from .research import ResearchTemplate
from .software import SoftwareProjectTemplate

__all__ = [
    "ContextTemplate",
    "TemplateResult",
    "TemplateRegistry",
    "get_template",
    "list_templates",
    "SoftwareProjectTemplate",
    "ResearchTemplate",
    "BusinessTemplate",
]
