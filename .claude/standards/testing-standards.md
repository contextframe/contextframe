# Testing Standards

This document defines testing standards for the Funcn project, ensuring good coverage while maintaining practical, maintainable tests.

## Testing Philosophy

**80/20 Rule**: Focus on testing the 80% of code paths that matter most, not every edge case.

Key principles:
1. **Test behavior, not implementation**
2. **Prioritize critical paths and happy paths**
3. **Make tests readable and maintainable**
4. **Use fixtures to reduce duplication**
5. **Balance coverage with test complexity**

## Test Structure

### Directory Organization

```
tests/
├── unit/                    # Fast, isolated unit tests
│   ├── test_component_manager.py
│   ├── test_registry_handler.py
│   └── test_utils.py
├── integration/             # Tests with external dependencies
│   ├── test_llm_calls.py
│   └── test_mcp_integration.py
├── e2e/                     # End-to-end workflow tests
│   └── test_full_workflow.py
├── fixtures/                # Test data and fixtures
│   ├── sample_components/
│   └── mock_responses.py
└── conftest.py             # Shared pytest fixtures
```

### Test File Naming

- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<feature>_integration.py`
- E2E tests: `test_<workflow>_e2e.py`

## Writing Tests

### Basic Test Structure

```python
"""Tests for component manager functionality."""

import pytest
from unittest.mock import Mock, patch

from funcn_cli.core.component_manager import ComponentManager
from funcn_cli.core.models import Component


class TestComponentManager:
    """Test suite for ComponentManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create a ComponentManager instance for testing."""
        return ComponentManager(config_path="test_config.json")
    
    @pytest.fixture
    def sample_component(self):
        """Create a sample component for testing."""
        return Component(
            name="test_agent",
            type="agent",
            version="1.0.0",
            files=["agent.py", "component.json"]
        )
    
    def test_add_component_success(self, manager, sample_component):
        """Test successfully adding a component."""
        # Arrange
        expected_path = "agents/test_agent"
        
        # Act
        result = manager.add_component(sample_component)
        
        # Assert
        assert result.success is True
        assert result.path == expected_path
        assert sample_component.name in manager.list_components()
    
    def test_add_duplicate_component_fails(self, manager, sample_component):
        """Test that adding duplicate component raises error."""
        # Arrange
        manager.add_component(sample_component)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Component already exists"):
            manager.add_component(sample_component)
```

### Async Test Structure

```python
@pytest.mark.asyncio
async def test_llm_call_with_retry():
    """Test LLM call with retry logic."""
    # Arrange
    mock_llm = Mock()
    mock_llm.call.side_effect = [
        Exception("API Error"),
        {"response": "Success"}
    ]
    
    # Act
    result = await call_llm_with_retry(mock_llm, "test prompt")
    
    # Assert
    assert result["response"] == "Success"
    assert mock_llm.call.call_count == 2
```

## Test Markers and Running Tests

### Using Markers

```python
@pytest.mark.unit
def test_parse_config():
    """Fast unit test for config parsing."""
    pass

@pytest.mark.integration
@pytest.mark.requires_api_key
async def test_openai_integration():
    """Integration test requiring OpenAI API key."""
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_full_component_workflow():
    """End-to-end test of complete workflow."""
    pass
```

### Running Specific Test Types

```bash
# Run only unit tests (fast)
pytest -m unit

# Run integration tests
pytest -m integration

# Run all tests except slow ones
pytest -m "not slow"

# Run tests with coverage
pytest --cov=funcn_cli --cov-report=html

# Run specific test file
pytest tests/unit/test_component_manager.py

# Run tests matching pattern
pytest -k "test_add_component"

# Run with verbose output
pytest -v

# Run parallel (requires pytest-xdist)
pytest -n auto
```

## Coverage Guidelines

### Target Coverage: 80%

Focus coverage on:
1. **Core business logic** (90%+ coverage)
2. **Public APIs** (85%+ coverage)
3. **Critical paths** (95%+ coverage)
4. **Error handling** (80%+ coverage)

Skip coverage for:
- Generated code
- Third-party integrations (mock instead)
- Temporary debugging code
- Simple getters/setters
- `__repr__` methods

### Coverage Pragmas

```python
def debug_only_function():  # pragma: no cover
    """This function is only for debugging."""
    import pdb; pdb.set_trace()

if TYPE_CHECKING:  # pragma: no cover
    from some_module import SomeType

def __repr__(self):  # pragma: no cover
    return f"<{self.__class__.__name__}>"
```

## Testing Best Practices

### 1. Use Fixtures Effectively

```python
@pytest.fixture(scope="session")
def app_config():
    """Shared app configuration for all tests."""
    return {"api_key": "test_key", "model": "test-model"}

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for API tests."""
    with patch("httpx.AsyncClient") as mock:
        yield mock
```

### 2. Test the Happy Path First

```python
def test_component_install_success():
    """Test successful component installation (happy path)."""
    # This is the most important test - what users expect to work

def test_component_install_missing_dependency():
    """Test handling of missing dependencies."""
    # Secondary test for common error case

def test_component_install_network_timeout():
    """Test handling of network timeouts."""
    # Edge case - lower priority
```

### 3. Use Descriptive Test Names

```python
# Good test names
def test_add_component_creates_directory_structure():
def test_registry_search_returns_matching_components():
def test_invalid_config_raises_validation_error():

# Bad test names
def test_add():
def test_search_works():
def test_error():
```

### 4. Arrange-Act-Assert Pattern

```python
def test_pattern_example():
    """Follow AAA pattern for clarity."""
    # Arrange - Set up test data and conditions
    manager = ComponentManager()
    component = create_test_component()
    
    # Act - Perform the action being tested
    result = manager.install(component)
    
    # Assert - Verify the outcome
    assert result.success is True
    assert Path(result.install_path).exists()
```

### 5. Mock External Dependencies

```python
@patch("funcn_cli.core.utils.fetch_from_registry")
def test_fetch_component(mock_fetch):
    """Test fetching component without hitting real API."""
    # Arrange
    mock_fetch.return_value = {"name": "test", "version": "1.0.0"}
    
    # Act
    result = fetch_component("test")
    
    # Assert
    assert result["name"] == "test"
    mock_fetch.assert_called_once_with("test")
```

## Practical Testing Scenarios

### Testing Mirascope Components

```python
@pytest.mark.asyncio
async def test_agent_with_mock_llm():
    """Test agent without making real LLM calls."""
    # Mock the LLM response
    with patch("mirascope.openai.call") as mock_call:
        mock_call.return_value = Mock(
            content="Mocked response",
            tool_calls=[]
        )
        
        # Test the agent
        from agents.research_agent import research_agent
        result = await research_agent("test query")
        
        assert "Mocked response" in result.content
```

### Testing File Operations

```python
def test_component_file_creation(tmp_path):
    """Test file creation using pytest's tmp_path fixture."""
    # Arrange
    component_dir = tmp_path / "test_component"
    
    # Act
    create_component_files(component_dir)
    
    # Assert
    assert (component_dir / "component.json").exists()
    assert (component_dir / "agent.py").exists()
    assert (component_dir / "funcn.md").exists()
```

### Testing CLI Commands

```python
from typer.testing import CliRunner
from funcn_cli.main import app

def test_cli_add_command():
    """Test CLI add command."""
    runner = CliRunner()
    
    result = runner.invoke(app, ["add", "test_component"])
    
    assert result.exit_code == 0
    assert "Successfully added" in result.stdout
```

## When NOT to Write Tests

Skip tests for:
1. **Trivial code**: Simple property accessors
2. **Framework code**: Don't test Typer, Pydantic, etc.
3. **Temporary code**: Debugging utilities
4. **Generated code**: Auto-generated files
5. **Pure configuration**: JSON/YAML files

## Test Maintenance

### Keeping Tests Fast

1. Use mocks for external services
2. Minimize file I/O (use tmp_path)
3. Avoid sleep/wait in tests
4. Run unit tests in parallel
5. Skip slow tests in CI for PRs

### Handling Flaky Tests

```python
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_occasionally_flaky_operation():
    """Test that might fail due to timing issues."""
    # Mark flaky tests explicitly
    # Fix the root cause when possible
```

## Quick Test Writing Checklist

- [ ] Test covers the happy path
- [ ] Test has descriptive name explaining what it verifies
- [ ] Test uses AAA pattern (Arrange, Act, Assert)
- [ ] External dependencies are mocked
- [ ] Test runs fast (< 1 second for unit tests)
- [ ] Test doesn't rely on test execution order
- [ ] Similar tests use shared fixtures
- [ ] Edge cases are tested only if critical
- [ ] Test failure message is helpful for debugging