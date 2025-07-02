# NumPy Compatibility Issues

## Problem

You may encounter this error when running tests or importing ContextFrame:

```
ImportError: numpy.core.multiarray failed to import

A module that was compiled using NumPy 1.x cannot be run in
NumPy 2.x as it may crash. To support both 1.x and 2.x
versions of NumPy, modules must be compiled with NumPy 2.0.
```

## Cause

This occurs when:
- NumPy 2.x is installed
- PyArrow (or another dependency) was compiled against NumPy 1.x
- There's a binary incompatibility between the versions

## Solutions

### Option 1: Downgrade NumPy (Recommended for now)

```bash
# Using pip
pip install "numpy<2"

# Using uv
uv pip install "numpy<2"

# Or specifically install NumPy 1.26.4
uv pip install numpy==1.26.4
```

### Option 2: Upgrade PyArrow

Wait for PyArrow to release a version compiled against NumPy 2.x:

```bash
# Check for updates
pip install --upgrade pyarrow

# Or wait for pyarrow>=15.0.0 which should support NumPy 2.x
```

### Option 3: Use Compatible Versions

Add to your `requirements.txt` or `pyproject.toml`:

```toml
# pyproject.toml
[project]
dependencies = [
    "numpy>=1.24,<2",  # Pin to NumPy 1.x
    "pyarrow>=14.0.2",
    # ... other dependencies
]
```

## Checking Versions

```bash
# Check installed versions
pip list | grep -E "numpy|pyarrow"

# Or with uv
uv pip list | grep -E "numpy|pyarrow"
```

## Long-term Solution

The ecosystem is transitioning to NumPy 2.x compatibility. Most packages should be updated by early 2025. Until then, pinning to NumPy 1.x is the most stable approach.

## ContextFrame Compatibility

ContextFrame itself is compatible with both NumPy 1.x and 2.x. The issue is with compiled dependencies like PyArrow. We're tracking this issue and will update our dependencies when compatible versions are available.