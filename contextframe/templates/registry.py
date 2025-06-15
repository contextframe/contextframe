"""Template registry for discovering and managing Context Templates."""

from .base import ContextTemplate
from .business import BusinessTemplate
from .research import ResearchTemplate
from .software import SoftwareProjectTemplate
from typing import Dict, List, Optional, Type


class TemplateRegistry:
    """Registry for Context Templates.
    
    Manages built-in and custom templates, providing discovery
    and instantiation capabilities.
    """
    
    def __init__(self):
        """Initialize the template registry."""
        self._templates: dict[str, type[ContextTemplate]] = {}
        self._instances: dict[str, ContextTemplate] = {}
        
        # Register built-in templates
        self._register_builtin_templates()
        
    def _register_builtin_templates(self):
        """Register all built-in templates."""
        builtin_templates = [
            SoftwareProjectTemplate,
            ResearchTemplate,
            BusinessTemplate,
        ]
        
        for template_class in builtin_templates:
            # Create an instance to get name
            instance = template_class()
            self.register(instance.name, template_class)
            
    def register(self, name: str, template_class: type[ContextTemplate]):
        """Register a template class.
        
        Args:
            name: Template name
            template_class: Template class (must inherit from ContextTemplate)
            
        Raises:
            ValueError: If name already registered or invalid class
        """
        if name in self._templates:
            raise ValueError(f"Template '{name}' is already registered")
            
        if not issubclass(template_class, ContextTemplate):
            raise ValueError(
                f"Template class must inherit from ContextTemplate, got {template_class}"
            )
            
        self._templates[name] = template_class
        # Clear cached instance if exists
        self._instances.pop(name, None)
        
    def unregister(self, name: str):
        """Unregister a template.
        
        Args:
            name: Template name to unregister
            
        Raises:
            KeyError: If template not found
        """
        if name not in self._templates:
            raise KeyError(f"Template '{name}' not found")
            
        del self._templates[name]
        self._instances.pop(name, None)
        
    def get(self, name: str) -> ContextTemplate:
        """Get a template instance by name.
        
        Args:
            name: Template name
            
        Returns:
            Template instance
            
        Raises:
            KeyError: If template not found
        """
        if name not in self._templates:
            raise KeyError(
                f"Template '{name}' not found. "
                f"Available templates: {', '.join(self.list_names())}"
            )
            
        # Cache instances for reuse
        if name not in self._instances:
            self._instances[name] = self._templates[name]()
            
        return self._instances[name]
        
    def list_names(self) -> list[str]:
        """List all registered template names.
        
        Returns:
            List of template names
        """
        return sorted(self._templates.keys())
        
    def list_templates(self) -> list[dict[str, str]]:
        """List all registered templates with metadata.
        
        Returns:
            List of template info dictionaries
        """
        templates = []
        for name in self.list_names():
            instance = self.get(name)
            templates.append({
                "name": name,
                "description": instance.description,
                "class": instance.__class__.__name__
            })
        return templates
        
    def find_by_path(self, path: str) -> str | None:
        """Find the best template for a given path.
        
        This method attempts to identify the most appropriate template
        based on directory structure and file patterns.
        
        Args:
            path: Directory path to analyze
            
        Returns:
            Template name if found, None otherwise
        """
        from pathlib import Path
        
        path_obj = Path(path)
        if not path_obj.exists() or not path_obj.is_dir():
            return None
            
        # Check for software project indicators
        software_indicators = [
            "src", "lib", "tests", "test", "package.json", 
            "requirements.txt", "setup.py", "Cargo.toml", "go.mod"
        ]
        if any((path_obj / indicator).exists() for indicator in software_indicators):
            return "software_project"
            
        # Check for research indicators
        research_indicators = [
            "papers", "data", "notebooks", "analysis", 
            "results", "experiments"
        ]
        if any((path_obj / indicator).exists() for indicator in research_indicators):
            # Additional check for .bib files
            if list(path_obj.glob("**/*.bib")) or list(path_obj.glob("**/*.ipynb")):
                return "research"
                
        # Check for business indicators
        business_indicators = [
            "meetings", "decisions", "reports", "projects",
            "proposals", "minutes"
        ]
        if any((path_obj / indicator).exists() for indicator in business_indicators):
            return "business"
            
        # Check file patterns if no directory indicators
        files = list(path_obj.iterdir())
        
        # Count file types
        code_files = sum(1 for f in files if f.suffix in {".py", ".js", ".java", ".cpp"})
        doc_files = sum(1 for f in files if f.suffix in {".md", ".pdf", ".docx"})
        data_files = sum(1 for f in files if f.suffix in {".csv", ".xlsx", ".json"})
        
        # Heuristic based on file types
        if code_files > doc_files and code_files > data_files:
            return "software_project"
        elif data_files > code_files and any(f.suffix == ".ipynb" for f in files):
            return "research"
        elif doc_files > code_files:
            return "business"
            
        return None


# Global registry instance
_registry = TemplateRegistry()


def get_template(name: str) -> ContextTemplate:
    """Get a template by name from the global registry.
    
    Args:
        name: Template name
        
    Returns:
        Template instance
        
    Raises:
        KeyError: If template not found
    """
    return _registry.get(name)


def list_templates() -> list[dict[str, str]]:
    """List all available templates from the global registry.
    
    Returns:
        List of template info dictionaries
    """
    return _registry.list_templates()


def register_template(name: str, template_class: type[ContextTemplate]):
    """Register a custom template in the global registry.
    
    Args:
        name: Template name
        template_class: Template class
    """
    _registry.register(name, template_class)


def find_template_for_path(path: str) -> str | None:
    """Find the best template for a given directory path.
    
    Args:
        path: Directory path
        
    Returns:
        Template name if found, None otherwise
    """
    return _registry.find_by_path(path)