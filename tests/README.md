# ContextFrame Tests

This directory contains all tests for the contextframe package, organized by test type.

## Directory Structure

```
tests/
├── unit/                  # Unit tests with mocking
│   ├── test_embed.py     # Embedding functionality tests
│   ├── test_enhance.py   # Enhancement functionality tests
│   ├── test_extract.py   # Extraction functionality tests
│   ├── test_io.py        # Import/export tests
│   ├── test_*.py         # Other unit tests
│   └── test_mcp/         # MCP-related unit tests
├── integration/          # Integration tests (no mocking)
│   ├── test_basic_functionality.py
│   ├── test_vector_search.py
│   ├── test_relationships.py
│   ├── test_collections.py
│   ├── test_edge_cases.py
│   └── README.md
└── fixtures/             # Test data and fixtures

```

## Running Tests

### All Tests
```bash
# Run all tests (unit + integration)
pytest tests/

# Run with coverage
pytest tests/ --cov=contextframe --cov-report=term-missing
```

### Unit Tests Only
```bash
# Run all unit tests
pytest tests/unit/

# Run specific unit test module
pytest tests/unit/test_embed.py -v
```

### Integration Tests Only
```bash
# Run all integration tests
pytest tests/integration/

# Or use the dedicated runner script
python run_integration_tests.py

# Run integration tests against PyPI version
python run_integration_tests.py --source pypi
```

## Test Types

### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Use mocking for external dependencies
- Fast execution
- Focus on logic and edge cases
- Should not require external resources

### Integration Tests (`tests/integration/`)
- Test the package as users would use it
- No mocking - real operations only
- Test interactions between components
- May be slower but more realistic
- Require the package to be installed

## Writing New Tests

### Unit Tests
- Place in `tests/unit/`
- Use mocking for dependencies
- Name files as `test_<module>.py`
- Focus on testing one component

### Integration Tests
- Place in `tests/integration/`
- Import from installed package: `from contextframe import ...`
- Test real workflows
- Clean up resources (temp files, etc.)
- See `tests/integration/README.md` for details

## Requirements

- Python 3.10-3.12
- pytest
- numpy (for integration tests)
- contextframe package (for integration tests)