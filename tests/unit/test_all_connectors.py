"""Test imports and basic functionality for all connectors."""

import pytest
from contextframe.connectors import (
    SourceConnector,
    ConnectorConfig,
    SyncResult,
    AuthType,
    GitHubConnector,
    LinearConnector,
    GoogleDriveConnector,
    NotionConnector,
    SlackConnector,
    DiscordConnector,
    ObsidianConnector,
)


def test_connector_imports():
    """Test that all connectors can be imported."""
    # Base classes
    assert SourceConnector is not None
    assert ConnectorConfig is not None
    assert SyncResult is not None
    assert AuthType is not None
    
    # Connector implementations
    assert GitHubConnector is not None
    assert LinearConnector is not None
    assert GoogleDriveConnector is not None
    assert NotionConnector is not None
    assert SlackConnector is not None
    assert DiscordConnector is not None
    assert ObsidianConnector is not None


def test_auth_types():
    """Test AuthType enum values."""
    assert AuthType.API_KEY.value == "api_key"
    assert AuthType.OAUTH.value == "oauth"
    assert AuthType.BASIC.value == "basic"
    assert AuthType.TOKEN.value == "token"
    assert AuthType.NONE.value == "none"


def test_connector_config_creation():
    """Test ConnectorConfig creation."""
    config = ConnectorConfig(
        name="Test Connector",
        auth_type=AuthType.TOKEN,
        auth_config={"token": "test-token"},
        sync_config={"test": "value"}
    )
    
    assert config.name == "Test Connector"
    assert config.auth_type == AuthType.TOKEN
    assert config.auth_config["token"] == "test-token"
    assert config.sync_config["test"] == "value"
    assert config.timeout == 30  # default value


def test_sync_result_creation():
    """Test SyncResult creation and methods."""
    result = SyncResult(success=True)
    
    assert result.success is True
    assert result.frames_created == 0
    assert result.frames_updated == 0
    assert result.frames_failed == 0
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
    
    # Test adding errors and warnings
    result.add_error("Test error")
    result.add_warning("Test warning")
    
    assert len(result.errors) == 1
    assert len(result.warnings) == 1
    assert result.errors[0] == "Test error"
    assert result.warnings[0] == "Test warning"
    
    # Test completion
    result.complete()
    assert result.end_time is not None
    assert result.duration is not None
    assert result.duration >= 0


def test_connector_inheritance():
    """Test that all connectors inherit from SourceConnector."""
    assert issubclass(GitHubConnector, SourceConnector)
    assert issubclass(LinearConnector, SourceConnector)
    assert issubclass(GoogleDriveConnector, SourceConnector)
    assert issubclass(NotionConnector, SourceConnector)
    assert issubclass(SlackConnector, SourceConnector)
    assert issubclass(DiscordConnector, SourceConnector)
    assert issubclass(ObsidianConnector, SourceConnector)


def test_connector_required_methods():
    """Test that all connectors implement required abstract methods."""
    required_methods = [
        "validate_connection",
        "discover_content", 
        "sync",
        "map_to_frame"
    ]
    
    connectors = [
        GitHubConnector,
        LinearConnector,
        GoogleDriveConnector,
        NotionConnector,
        SlackConnector,
        DiscordConnector,
        ObsidianConnector,
    ]
    
    for connector_class in connectors:
        for method_name in required_methods:
            assert hasattr(connector_class, method_name), \
                f"{connector_class.__name__} missing method {method_name}"
            method = getattr(connector_class, method_name)
            assert callable(method), \
                f"{connector_class.__name__}.{method_name} is not callable"


@pytest.mark.parametrize("connector_class,expected_deps", [
    (GitHubConnector, ["github"]),
    (LinearConnector, ["linear"]),
    (GoogleDriveConnector, ["googleapiclient"]),
    (NotionConnector, ["notion_client"]),
    (SlackConnector, ["slack_sdk"]),
    (DiscordConnector, ["discord"]),
    (ObsidianConnector, []),  # No external dependencies
])
def test_connector_dependencies(connector_class, expected_deps):
    """Test that connectors handle missing dependencies gracefully."""
    config = ConnectorConfig(
        name="Test",
        auth_type=AuthType.NONE,
        sync_config={}
    )
    
    # For connectors with dependencies, they should raise ImportError
    # if the dependency is not available
    if expected_deps:
        # We can't easily test missing dependencies without actually
        # uninstalling packages, so we'll just verify the connectors
        # can be instantiated if dependencies are available
        try:
            # This might fail due to missing auth config, but not due to imports
            connector_class(config, None)
        except ImportError as e:
            # Expected if dependency is missing
            assert any(dep in str(e) for dep in expected_deps)
        except (ValueError, AttributeError):
            # Expected for invalid config or missing dataset
            pass
    else:
        # Obsidian should work without external dependencies
        # (though it might fail due to missing vault_path)
        try:
            connector_class(config, None)
        except (ValueError, AttributeError):
            # Expected for invalid config
            pass