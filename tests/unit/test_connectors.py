"""Tests for external system connectors."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from contextframe import FrameDataset, FrameRecord
from contextframe.connectors import (
    SourceConnector,
    ConnectorConfig,
    SyncResult,
    AuthType,
    GitHubConnector,
    LinearConnector,
)
from contextframe.schema import RecordType


class TestConnectorBase:
    """Test base connector functionality."""
    
    def test_connector_config(self):
        """Test ConnectorConfig initialization."""
        config = ConnectorConfig(
            name="Test Connector",
            auth_type=AuthType.API_KEY,
            auth_config={"api_key": "test-key"},
            sync_config={"setting": "value"},
            rate_limit=60,
            timeout=30,
            retry_count=3,
        )
        
        assert config.name == "Test Connector"
        assert config.auth_type == AuthType.API_KEY
        assert config.auth_config["api_key"] == "test-key"
        assert config.sync_config["setting"] == "value"
        assert config.rate_limit == 60
        
    def test_sync_result(self):
        """Test SyncResult functionality."""
        result = SyncResult(success=True)
        
        # Add some data
        result.frames_created = 10
        result.frames_updated = 5
        result.frames_failed = 2
        result.add_error("Test error")
        result.add_warning("Test warning")
        result.complete()
        
        assert result.success is True
        assert result.frames_created == 10
        assert result.frames_updated == 5
        assert result.frames_failed == 2
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert result.end_time is not None
        assert result.duration is not None
        
    def test_sync_state_management(self, tmp_path):
        """Test sync state save/load functionality."""
        # Create test dataset
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(str(dataset_path))
        
        # Create mock connector
        config = ConnectorConfig(name="Test Connector")
        
        class TestConnector(SourceConnector):
            def validate_connection(self): return True
            def discover_content(self): return {}
            def sync(self, incremental=True): return SyncResult(success=True)
            def map_to_frame(self, data): return None
            
        connector = TestConnector(config, dataset)
        
        # Test saving sync state
        test_state = {
            "last_sync": datetime.now().isoformat(),
            "cursor": "page-2",
            "processed": 100,
        }
        connector.save_sync_state(test_state)
        
        # Test loading sync state
        loaded_state = connector.get_last_sync_state()
        assert loaded_state is not None
        assert loaded_state["cursor"] == "page-2"
        assert loaded_state["processed"] == 100


class TestGitHubConnector:
    """Test GitHub connector functionality."""
    
    @pytest.fixture
    def mock_github(self):
        """Mock PyGithub objects."""
        with patch("contextframe.connectors.github.Github") as mock_github_class:
            # Create mocks
            mock_client = Mock()
            mock_repo = Mock()
            
            # Configure repo mock
            mock_repo.full_name = "owner/repo"
            mock_repo.description = "Test repository"
            mock_repo.default_branch = "main"
            mock_repo.size = 1000
            mock_repo.language = "Python"
            mock_repo.get_topics.return_value = ["test", "example"]
            
            # Configure client mock
            mock_client.get_repo.return_value = mock_repo
            mock_github_class.return_value = mock_client
            
            yield mock_client, mock_repo
            
    def test_github_connector_init(self, mock_github, tmp_path):
        """Test GitHub connector initialization."""
        mock_client, mock_repo = mock_github
        
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(str(dataset_path))
        
        config = ConnectorConfig(
            name="GitHub Test",
            auth_type=AuthType.TOKEN,
            auth_config={"token": "test-token"},
            sync_config={
                "owner": "owner",
                "repo": "repo",
                "branch": "main",
                "paths": ["/src"],
                "file_patterns": ["*.py"],
            }
        )
        
        connector = GitHubConnector(config, dataset)
        
        assert connector.owner == "owner"
        assert connector.repo == "repo"
        assert connector.branch == "main"
        assert connector.paths == ["/src"]
        assert connector.file_patterns == ["*.py"]
        
    def test_github_validate_connection(self, mock_github, tmp_path):
        """Test GitHub connection validation."""
        mock_client, mock_repo = mock_github
        
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(str(dataset_path))
        
        config = ConnectorConfig(
            name="GitHub Test",
            auth_type=AuthType.TOKEN,
            auth_config={"token": "test-token"},
            sync_config={"owner": "owner", "repo": "repo"}
        )
        
        connector = GitHubConnector(config, dataset)
        
        # Test successful validation
        assert connector.validate_connection() is True
        
        # Test failed validation
        mock_repo.full_name = Mock(side_effect=Exception("Access denied"))
        assert connector.validate_connection() is False
        
    def test_github_discover_content(self, mock_github, tmp_path):
        """Test GitHub content discovery."""
        mock_client, mock_repo = mock_github
        
        # Mock file structure
        mock_file1 = Mock()
        mock_file1.type = "file"
        mock_file1.path = "src/main.py"
        mock_file1.name = "main.py"
        mock_file1.size = 1000
        
        mock_file2 = Mock()
        mock_file2.type = "file"
        mock_file2.path = "src/test.py"
        mock_file2.name = "test.py"
        mock_file2.size = 500
        
        mock_dir = Mock()
        mock_dir.type = "dir"
        mock_dir.path = "src/utils"
        
        mock_repo.get_contents.return_value = [mock_file1, mock_file2, mock_dir]
        
        # Mock branches
        mock_branch = Mock()
        mock_branch.name = "main"
        mock_repo.get_branches.return_value = [mock_branch]
        
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(str(dataset_path))
        
        config = ConnectorConfig(
            name="GitHub Test",
            auth_type=AuthType.TOKEN,
            auth_config={"token": "test-token"},
            sync_config={
                "owner": "owner",
                "repo": "repo",
                "paths": ["/src"],
                "file_patterns": ["*.py"],
            }
        )
        
        connector = GitHubConnector(config, dataset)
        discovery = connector.discover_content()
        
        assert discovery["repository"]["owner"] == "owner"
        assert discovery["repository"]["name"] == "repo"
        assert "main" in discovery["branches"]
        assert discovery["stats"]["total_files"] == 2
        assert discovery["stats"]["file_types"][".py"] == 2
        
    def test_github_map_to_frame(self, mock_github, tmp_path):
        """Test mapping GitHub file to FrameRecord."""
        mock_client, mock_repo = mock_github
        
        # Mock file
        mock_file = Mock()
        mock_file.name = "README.md"
        mock_file.path = "README.md"
        mock_file.sha = "abc123"
        mock_file.size = 1234
        mock_file.type = "file"
        mock_file.html_url = "https://github.com/owner/repo/blob/main/README.md"
        mock_file.decoded_content = b"# Test Repository\n\nThis is a test."
        
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(str(dataset_path))
        
        config = ConnectorConfig(
            name="GitHub Test",
            auth_type=AuthType.TOKEN,
            auth_config={"token": "test-token"},
            sync_config={"owner": "owner", "repo": "repo"}
        )
        
        connector = GitHubConnector(config, dataset)
        frame = connector.map_to_frame(mock_file)
        
        assert frame is not None
        assert frame.metadata["title"] == "README.md"
        assert frame.metadata["source_type"] == "github"
        assert frame.metadata["source_file"] == "README.md"
        assert frame.metadata["source_url"] == mock_file.html_url
        assert frame.text_content == "# Test Repository\n\nThis is a test."
        assert frame.metadata["context"] == frame.text_content[:1000]


class TestLinearConnector:
    """Test Linear connector functionality."""
    
    @pytest.fixture
    def mock_linear(self):
        """Mock Linear API client."""
        with patch("contextframe.connectors.linear.LinearClient") as mock_linear_class:
            # Create mocks
            mock_client = Mock()
            
            # Mock viewer
            mock_viewer = Mock()
            mock_viewer.id = "viewer-id"
            mock_viewer.name = "Test User"
            mock_viewer.email = "test@example.com"
            mock_client.viewer = mock_viewer
            
            # Mock organization
            mock_org = Mock()
            mock_org.id = "org-id"
            mock_org.name = "Test Organization"
            mock_org.url_key = "testorg"
            mock_client.organization = mock_org
            
            # Configure client
            mock_linear_class.return_value = mock_client
            
            yield mock_client
            
    def test_linear_connector_init(self, mock_linear, tmp_path):
        """Test Linear connector initialization."""
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(str(dataset_path))
        
        config = ConnectorConfig(
            name="Linear Test",
            auth_type=AuthType.API_KEY,
            auth_config={"api_key": "test-key"},
            sync_config={
                "sync_teams": True,
                "sync_projects": True,
                "sync_issues": True,
                "include_archived": False,
                "include_comments": True,
            }
        )
        
        connector = LinearConnector(config, dataset)
        
        assert connector.sync_teams is True
        assert connector.sync_projects is True
        assert connector.sync_issues is True
        assert connector.include_archived is False
        assert connector.include_comments is True
        
    def test_linear_validate_connection(self, mock_linear, tmp_path):
        """Test Linear connection validation."""
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(str(dataset_path))
        
        config = ConnectorConfig(
            name="Linear Test",
            auth_type=AuthType.API_KEY,
            auth_config={"api_key": "test-key"},
        )
        
        connector = LinearConnector(config, dataset)
        
        # Test successful validation
        assert connector.validate_connection() is True
        
        # Test failed validation
        mock_linear.viewer = Mock(side_effect=Exception("Invalid API key"))
        assert connector.validate_connection() is False
        
    def test_linear_map_issue_to_frame(self, mock_linear, tmp_path):
        """Test mapping Linear issue to FrameRecord."""
        # Mock issue
        mock_issue = Mock()
        mock_issue.id = "issue-id"
        mock_issue.identifier = "PROJ-123"
        mock_issue.title = "Test Issue"
        mock_issue.description = "This is a test issue"
        mock_issue.priority = 2
        mock_issue.created_at = datetime.now()
        mock_issue.updated_at = datetime.now()
        mock_issue.parent = None
        mock_issue.related_issues = []
        mock_issue.labels = []
        mock_issue.comments = []
        
        # Mock state
        mock_state = Mock()
        mock_state.name = "In Progress"
        mock_issue.state = mock_state
        
        # Mock assignee
        mock_assignee = Mock()
        mock_assignee.id = "user-id"
        mock_assignee.name = "John Doe"
        mock_issue.assignee = mock_assignee
        
        # Mock team
        mock_team = Mock()
        mock_team.id = "team-id"
        mock_team.name = "Engineering"
        mock_issue.team = mock_team
        
        # Mock project
        mock_project = Mock()
        mock_project.id = "project-id"
        mock_project.name = "Q4 Goals"
        mock_issue.project = mock_project
        
        dataset_path = tmp_path / "test.lance"
        dataset = FrameDataset.create(str(dataset_path))
        
        config = ConnectorConfig(
            name="Linear Test",
            auth_type=AuthType.API_KEY,
            auth_config={"api_key": "test-key"},
        )
        
        connector = LinearConnector(config, dataset)
        frame = connector._map_issue_to_frame(mock_issue, "collection-id")
        
        assert frame is not None
        assert frame.metadata["title"] == "PROJ-123: Test Issue"
        assert frame.metadata["source_type"] == "linear_issue"
        assert frame.metadata["status"] == "In Progress"
        assert frame.metadata["author"] == "John Doe"
        assert "Engineering" in frame.text_content
        assert "Q4 Goals" in frame.text_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])