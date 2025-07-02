#!/usr/bin/env python3
"""
Test improved error messages with field context.
"""

import os
import shutil
import tempfile
import pytest

from contextframe import FrameRecord, FrameDataset
from contextframe.exceptions import ValidationError


class TestImprovedErrorMessages:
    """Test that error messages provide helpful field context."""
    
    def setup_method(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.dataset_path = os.path.join(self.temp_dir, "error_test.lance")
        self.embed_dim = 1536
        
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_custom_metadata_type_error(self):
        """Test error message for non-string custom metadata values."""
        # Try to create record with invalid custom metadata
        with pytest.raises(ValidationError) as exc_info:
            record = FrameRecord.create(
                title="Test Document",
                content="Test content",
                custom_metadata={
                    "priority": 1,  # Should be string
                    "active": True  # Should be string
                }
            )
            dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
            dataset.add(record)
            
        error_msg = str(exc_info.value)
        assert "custom_metadata.priority" in error_msg
        assert "All custom_metadata values must be strings" in error_msg
        assert "Convert" in error_msg
        assert "wait for v0.2.0" in error_msg
        
    def test_invalid_relationship_type_error(self):
        """Test error message for invalid relationship type."""
        from contextframe.helpers.metadata_utils import create_relationship
        
        with pytest.raises(ValidationError) as exc_info:
            create_relationship("some-uuid", rel_type="invalid_type")
            
        error_msg = str(exc_info.value)
        assert "Invalid relationship type: 'invalid_type'" in error_msg
        assert "Valid types are:" in error_msg
        assert "parent, child, related, reference" in error_msg
        assert "member_of" in error_msg
        
    def test_missing_relationship_fields_error(self):
        """Test error message for relationships missing required fields."""
        record = FrameRecord.create(
            title="Test Document",
            content="Test content"
        )
        
        # Add invalid relationship directly to metadata
        record.metadata["relationships"] = [
            {
                "relationship_type": "parent"
                # Missing target identifier
            }
        ]
        
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        with pytest.raises(ValidationError) as exc_info:
            dataset.add(record)
            
        error_msg = str(exc_info.value)
        assert "relationships" in error_msg
        assert "must include 'relationship_type' and at least one identifier" in error_msg
        
    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are shown clearly."""
        record = FrameRecord.create(
            title="Test Document",
            content="Test content"
        )
        
        # Add multiple invalid fields
        record.metadata["uuid"] = "invalid-uuid-format"
        record.metadata["created_at"] = "2024/01/01"  # Wrong date format
        record.metadata["custom_metadata"] = {"score": 0.95}  # Wrong type
        
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        with pytest.raises(ValidationError) as exc_info:
            dataset.add(record)
            
        error_msg = str(exc_info.value)
        # Should show multiple errors
        assert "uuid" in error_msg
        assert "UUID must be in format" in error_msg
        assert "created_at" in error_msg
        assert "ISO 8601 format" in error_msg
        assert "custom_metadata.score" in error_msg
        
    def test_error_with_record_context(self):
        """Test that errors include record title and UUID for context."""
        records = [
            FrameRecord.create(title="Valid Record", content="Valid"),
            FrameRecord.create(
                title="Invalid Record",
                content="Invalid",
                custom_metadata={"priority": 1}  # Invalid type
            )
        ]
        
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        
        with pytest.raises(ValidationError) as exc_info:
            dataset.add_many(records)
            
        error_msg = str(exc_info.value)
        assert "Invalid Record" in error_msg
        assert "UUID:" in error_msg
        assert "custom_metadata.priority" in error_msg
        
    def test_update_error_context(self):
        """Test error messages during update operations."""
        # Create and add a valid record first
        record = FrameRecord.create(
            title="Original Record",
            content="Original content"
        )
        
        dataset = FrameDataset.create(self.dataset_path, embed_dim=self.embed_dim)
        dataset.add(record)
        
        # Try to update with invalid metadata
        record.metadata["custom_metadata"] = {"invalid": True}
        
        with pytest.raises(ValidationError) as exc_info:
            dataset.update(record)
            
        error_msg = str(exc_info.value)
        assert "Cannot update record" in error_msg
        assert "Original Record" in error_msg
        assert record.uuid in error_msg
        assert "custom_metadata.invalid" in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])