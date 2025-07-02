# ContextFrame Integration Tests

This directory contains integration tests for the contextframe package. These tests treat the package as a black box and test real functionality without mocking. Integration tests are located in `tests/integration/` to distinguish them from unit tests in `tests/unit/`.

## Test Structure

- `test_basic_functionality.py` - Tests basic FrameRecord and FrameDataset operations
- `test_vector_search.py` - Tests vector search and similarity functionality
- `test_relationships.py` - Tests document relationship management
- `test_collections.py` - Tests collection and collection header functionality
- `test_edge_cases.py` - Tests error handling, edge cases, and real-world scenarios

## Running Tests

### Quick Start

From the repository root:

```bash
# Run all integration tests (assumes contextframe is installed)
python run_integration_tests.py

# Install from local source and run tests
python run_integration_tests.py --source local

# Install from PyPI and run tests
python run_integration_tests.py --source pypi

# Run only quick validation
python run_integration_tests.py --quick

# Run with verbose output
python run_integration_tests.py -v
```

### Manual Testing

If you prefer to run tests manually:

```bash
# Install the package (choose one)
pip install -e .  # Local development
pip install contextframe  # From PyPI

# Install test dependencies
pip install pytest numpy

# Run all integration tests
pytest tests/integration/

# Run specific test file
pytest tests/integration/test_basic_functionality.py -v

# Run specific test
pytest tests/integration/test_basic_functionality.py::TestBasicFrameRecord::test_create_simple_record -v
```

## Test Coverage

The integration tests cover:

1. **Basic Operations**
   - Creating FrameRecord objects with various metadata
   - Creating and opening FrameDataset
   - Adding, updating, deleting records
   - Upsert functionality

2. **Vector Search**
   - K-nearest neighbor search
   - Search with SQL filters
   - Full-text search
   - Search within collections
   - Handling documents without vectors

3. **Relationships**
   - Adding relationships between documents
   - Multiple relationships per document
   - Bidirectional relationships
   - Different relationship types
   - Finding related documents

4. **Collections**
   - Collection headers
   - Collection members with positions
   - Multiple collections
   - Nested collections
   - Collection-specific searches

5. **Edge Cases**
   - Empty datasets
   - Large content
   - Unicode and special characters
   - Null/empty fields
   - Concurrent-like modifications
   - Various vector dimensions
   - Batch operations
   - Real-world scenarios

## Adding New Tests

When adding new integration tests:

1. Create test classes that inherit from `object` (or nothing)
2. Use `setup_method` and `teardown_method` for test isolation
3. Always clean up temporary files/directories
4. Test real operations without mocking
5. Include both positive and negative test cases
6. Document what each test is validating

## Requirements

- Python 3.10-3.12
- contextframe package installed
- pytest
- numpy

## Notes

- Tests create temporary directories for Lance datasets
- All temporary data is cleaned up after tests
- Tests use small embedding dimensions (384) for efficiency
- No external services or APIs are required
- Tests run completely offline