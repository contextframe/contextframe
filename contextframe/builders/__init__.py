"""
ContextFrame Builders Module

Provides optional functionality for document extraction, enrichment, analysis,
templates, and serving. Each sub-module is lazily loaded to minimize dependencies.
"""

import importlib
from typing import Any, Dict, Optional


class LazyLoader:
    """Lazy loader for optional modules with clear error messages."""

    def __init__(self, module_name: str, package: str, extras_name: str):
        self.module_name = module_name
        self.package = package
        self.extras_name = extras_name
        self._module: Any | None = None

    def __getattr__(self, name: str) -> Any:
        if self._module is None:
            try:
                self._module = importlib.import_module(
                    f".{self.module_name}", package=self.package
                )
            except ImportError as e:
                raise ImportError(
                    f"\nThe '{self.module_name}' module requires additional dependencies.\n"
                    f"Please install with: pip install \"contextframe[{self.extras_name}]\"\n"
                    f"Or for all optional features: pip install \"contextframe[all]\"\n"
                    f"\nOriginal error: {e}"
                )
        return getattr(self._module, name)


# Lazy loading of optional modules
extract = LazyLoader("extract", __package__, "extract")
embed = LazyLoader("embed", __package__, "embed")
enhance = LazyLoader("enhance", __package__, "enhance")
encode = LazyLoader("encode", __package__, "encode")
serve = LazyLoader("serve", __package__, "serve")


__all__ = ["extract", "embed", "enhance", "encode", "serve"]
