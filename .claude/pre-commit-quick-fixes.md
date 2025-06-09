# Pre-commit Quick Fixes for Claude

Apply these fixes automatically when generating or modifying Python code in the Funcn project:

## Import Fixes

### Before:
```python
import os, sys  # E401: Multiple imports on one line
from module import *  # F403: Star import
import unused_module  # F401: Unused import
```

### After:
```python
import os
import sys
from module import specific_function, SpecificClass
# Remove unused imports entirely
```

## Line Length Fixes

### Before:
```python
result = very_long_function_call_with_many_parameters(param1="value1", param2="value2", param3="value3", param4="value4")  # Line > 130 chars
```

### After:
```python
result = very_long_function_call_with_many_parameters(
    param1="value1",
    param2="value2", 
    param3="value3",
    param4="value4"
)
```

## Docstring Placement

### Before:
```python
import os
"""This module does something."""  # D203: Docstring not first

def function():
    x = 1
    """This function does something."""  # Docstring not first
    return x
```

### After:
```python
"""This module does something."""
import os

def function():
    """This function does something."""
    x = 1
    return x
```

## Common Simplifications (SIM rules)

### Before:
```python
# SIM108: Use ternary operator
if condition:
    x = 1
else:
    x = 2

# SIM110: Use any()
for item in items:
    if condition(item):
        found = True
        break
else:
    found = False
```

### After:
```python
# Ternary operator
x = 1 if condition else 2

# Use any()
found = any(condition(item) for item in items)
```

## Unused Variables

### Before:
```python
def function():
    unused_var = compute_something()  # F841: Unused variable
    result = compute_other()
    return result
```

### After:
```python
def function():
    _ = compute_something()  # Prefix with underscore if side effects needed
    # Or remove entirely if not needed
    result = compute_other()
    return result
```

## Debug Statements

### Before:
```python
def function():
    print("Debug:", value)  # Remove debug prints
    breakpoint()  # Remove breakpoints
    import pdb; pdb.set_trace()  # Remove pdb
    return value
```

### After:
```python
def function():
    # Use proper logging instead
    # logger.debug(f"Debug: {value}")
    return value
```

## File Endings

Always ensure:
- Files end with exactly one newline character
- No trailing whitespace at end of lines
- Unix line endings (\n) not Windows (\r\n)

## Import Sorting

Sort imports in this order:
1. Standard library
2. Third-party packages  
3. Local imports

Within each group, sort alphabetically:

```python
# Standard library
import json
import os
from pathlib import Path

# Third-party
import httpx
from pydantic import BaseModel
from typer import Typer

# Local
from funcn_cli.core import utils
from funcn_cli.models import Component
```

## Type Hints Best Practices

```python
# Good: Clear type hints
def process_items(items: list[str], max_count: int = 10) -> dict[str, int]:
    return {"count": min(len(items), max_count)}

# Avoid: Missing return type hints
def process_items(items, max_count=10):  # Add type hints
    return {"count": min(len(items), max_count)}
```

## Async Best Practices

```python
# Good: Proper async/await
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Avoid: Sync operations in async functions
async def fetch_data(url: str) -> dict:
    response = requests.get(url)  # Use async httpx instead
    return response.json()
```

Remember: When in doubt, run `task lint` or `ruff check --fix` to see what needs fixing!