# Funcn Code Standards

This file defines the code standards for the Funcn project to ensure all generated code passes pre-commit hooks without requiring manual cleanup.

## Python Code Style

### Formatting (Ruff)
- **Line length**: Maximum 130 characters
- **Indentation**: 4 spaces (never tabs)
- **Line endings**: Use `\n` (LF) for all files
- **Quote style**: Preserve existing quote style in the file
- **Target Python version**: 3.11+

### Import Organization (isort via Ruff)
- Combine as imports: `from module import a, b, c`
- Order imports by type (standard library, third-party, local)
- No sections - all imports in one block
- Sort imports alphabetically within each type group

### Code Quality Rules
Apply these Ruff rules:
- **E**: pycodestyle errors (except E203, E251, E266, E401, E402, E501)
- **F**: Pyflakes (except F401, F403, F841)
- **UP**: pyupgrade - use modern Python syntax
- **B**: flake8-bugbear - avoid common bugs
- **SIM**: flake8-simplify - simplify code
- **I**: isort - proper import sorting

### Type Checking (mypy)
- Type hints are encouraged but not required
- Missing imports can be ignored
- Use `from typing import TYPE_CHECKING` for import cycle avoidance
- No need for complete type coverage

## Code Standards

### Functions and Methods
```python
def function_name(param1: str, param2: int = 10) -> list[str]:
    """Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    # Implementation
    return result
```

### Async Functions
```python
async def async_function(data: dict) -> str:
    """Always use async/await for I/O operations."""
    result = await some_async_operation(data)
    return result
```

### Classes
```python
class ComponentName:
    """Class description."""
    
    def __init__(self, config: dict) -> None:
        """Initialize the component."""
        self.config = config
```

### Imports
```python
# Standard library imports first
import os
import sys
from pathlib import Path

# Third-party imports
import httpx
from pydantic import BaseModel
from typer import Typer

# Local imports
from funcn_cli.core import utils
from funcn_cli.models import Component
```

### Mirascope Patterns
```python
from mirascope import llm, prompt_template
from mirascope.core import BaseModel

class OutputModel(BaseModel):
    """Always use Pydantic models for structured outputs."""
    result: str
    confidence: float

@llm.call(
    provider="{{provider}}",  # Template variable
    model="{{model}}",        # Template variable
    response_model=OutputModel
)
@prompt_template("""
Your prompt here: {input_var}
""")
async def agent_function(input_var: str) -> OutputModel:
    """Agent implementation."""
    ...
```

### Error Handling
```python
try:
    result = await risky_operation()
except SpecificError as e:
    # Handle specific error
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    # Handle unexpected errors
    logger.exception("Unexpected error")
    raise
```

## Pre-commit Checks to Pass

### File Standards
- **No debug statements**: Remove all `print()`, `breakpoint()`, `import pdb`
- **Docstring first**: Docstrings must be the first statement in modules/functions/classes
- **End with newline**: All Python files must end with a single newline
- **No trailing whitespace**: Remove all trailing spaces
- **No large files**: Files must be under 1MB
- **No private keys**: Never include private keys or secrets

### JSON Files
- Indent with 2 spaces
- Do not sort keys
- Must be valid JSON

### YAML Files
- Must be valid YAML syntax
- Can use unsafe features

## Common Patterns to Follow

### Component Structure
```python
# components/my_component/agent.py
"""Component module docstring."""

from mirascope import llm, prompt_template
from pydantic import BaseModel

# Define response models
class MyOutput(BaseModel):
    """Output model description."""
    field: str

# Define the main function
@llm.call(provider="{{provider}}", model="{{model}}")
@prompt_template("Template here")
async def my_agent(input: str) -> MyOutput:
    """Agent description."""
    ...

# Export public API
__all__ = ["my_agent", "MyOutput"]
```

### Tool Implementation
```python
# tools/my_tool/tool.py
"""Tool module docstring."""


def tool_function(query: str, limit: int = 10) -> list[str]:
    """Tool function with clear parameters and return type."""
    results = []
    # Implementation
    return results[:limit]


__all__ = ["tool_function"]
```

## Avoid These Common Issues

1. **Unused imports**: Remove all unused imports (F401)
2. **Unused variables**: Remove or prefix with underscore (F841)
3. **Star imports**: Never use `from module import *` (F403)
4. **Line too long**: Keep lines under 130 characters (E501)
5. **Multiple imports on one line**: Use separate lines (E401)
6. **Module level import not at top**: Keep all imports at the top (E402)
7. **Undefined names**: Ensure all names are defined before use
8. **Complexity**: Keep function complexity under 10

## Testing Standards

```python
import pytest
from funcn_cli.components import my_component

@pytest.mark.asyncio
async def test_async_function():
    """Test async functions with pytest-asyncio."""
    result = await my_component.process("input")
    assert result.success is True

@pytest.mark.unit
def test_sync_function():
    """Mark test types appropriately."""
    assert my_component.validate("data") is True
```

## Markdown Standards

Follow these rules to avoid markdownlint warnings:

### MD022: Headings must be surrounded by blank lines
```markdown
<!-- Bad -->
Some text
## Heading
More text

<!-- Good -->
Some text

## Heading

More text
```

### MD025: Only one top-level heading (H1) per document
```markdown
<!-- Bad -->
# Title
# Another Title

<!-- Good -->
# Main Title
## Section Title
```

### MD032: Lists must be surrounded by blank lines
```markdown
<!-- Bad -->
Some text
- List item
- Another item
More text

<!-- Good -->
Some text

- List item
- Another item

More text
```

### MD037: No spaces inside emphasis markers
```markdown
<!-- Bad -->
Component names must have type suffix (_ agent, _tool, etc.)

<!-- Good -->
Component names must have type suffix (_agent, _tool, etc.)
```

## Python Type Hints

### Use Modern Type Annotations (Python 3.9+)
```python
# BAD: Deprecated typing imports
from typing import List, Dict, Tuple, Optional, Union

def process(items: List[str]) -> Dict[str, int]:
    data: Tuple[int, str] = (1, "value")
    optional_value: Optional[str] = None
    union_value: Union[str, int] = "text"

# GOOD: Use built-in types and modern syntax
def process(items: list[str]) -> dict[str, int]:
    data: tuple[int, str] = (1, "value")
    optional_value: str | None = None
    union_value: str | int = "text"
```

### When to Import from typing
Only import these from typing module:
- `TYPE_CHECKING` - for avoiding circular imports
- `Any` - when type is truly dynamic
- `Callable` - for function types
- `TypeVar`, `Generic` - for generic types
- `Protocol` - for structural subtyping
- `Literal` - for literal types
- `TypedDict` - for typed dictionaries
- `cast` - for type casting

```python
# Good imports from typing
from typing import TYPE_CHECKING, Any, Callable, TypeVar, Protocol

if TYPE_CHECKING:
    from some_module import SomeType

T = TypeVar('T')

class Processor(Protocol):
    def process(self, data: Any) -> None: ...
```

## Quick Checklist Before Code Generation

- [ ] Docstring is first in file/function/class
- [ ] All imports at top of file
- [ ] No unused imports or variables
- [ ] Lines under 130 characters
- [ ] Proper async/await usage
- [ ] Use modern type hints (list, dict, not List, Dict)
- [ ] No debug print statements
- [ ] File ends with single newline
- [ ] No trailing whitespace
- [ ] Imports properly sorted
- [ ] Markdown headings have blank lines above/below
- [ ] Lists have blank lines above/below
- [ ] Only one H1 heading per Markdown file
- [ ] No spaces inside emphasis markers