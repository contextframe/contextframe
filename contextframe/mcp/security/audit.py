"""Audit logging for MCP server security events."""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import deque

from contextframe.frame import FrameDataset, FrameRecord


class AuditEventType(str, Enum):
    """Types of audit events."""
    
    # Authentication events
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILURE = "auth.failure"
    AUTH_TOKEN_CREATED = "auth.token_created"
    AUTH_TOKEN_REVOKED = "auth.token_revoked"
    
    # Authorization events
    AUTHZ_GRANTED = "authz.granted"
    AUTHZ_DENIED = "authz.denied"
    
    # Rate limiting events
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"
    RATE_LIMIT_RESET = "rate_limit.reset"
    
    # Resource access events
    RESOURCE_READ = "resource.read"
    RESOURCE_WRITE = "resource.write"
    RESOURCE_DELETE = "resource.delete"
    
    # Tool execution events
    TOOL_EXECUTED = "tool.executed"
    TOOL_FAILED = "tool.failed"
    
    # Security configuration events
    SECURITY_CONFIG_CHANGED = "security.config_changed"
    ROLE_CREATED = "security.role_created"
    ROLE_MODIFIED = "security.role_modified"
    ROLE_DELETED = "security.role_deleted"
    POLICY_CREATED = "security.policy_created"
    POLICY_MODIFIED = "security.policy_modified"
    POLICY_DELETED = "security.policy_deleted"
    
    # System events
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_ERROR = "system.error"


@dataclass
class AuditEvent:
    """Audit event record."""
    
    # Event metadata
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    
    # Principal information
    principal_id: Optional[str] = None
    principal_type: Optional[str] = None
    principal_name: Optional[str] = None
    auth_method: Optional[str] = None
    
    # Request context
    operation: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Network context
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Event details
    success: bool = True
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Computed fields
    severity: str = field(init=False)
    
    def __post_init__(self):
        # Compute severity based on event type and success
        if not self.success:
            if self.event_type in [
                AuditEventType.AUTH_FAILURE,
                AuditEventType.AUTHZ_DENIED,
                AuditEventType.RATE_LIMIT_EXCEEDED
            ]:
                self.severity = "warning"
            else:
                self.severity = "error"
        else:
            if self.event_type in [
                AuditEventType.SECURITY_CONFIG_CHANGED,
                AuditEventType.ROLE_CREATED,
                AuditEventType.ROLE_MODIFIED,
                AuditEventType.ROLE_DELETED,
                AuditEventType.POLICY_CREATED,
                AuditEventType.POLICY_MODIFIED,
                AuditEventType.POLICY_DELETED,
            ]:
                self.severity = "warning"
            else:
                self.severity = "info"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime to ISO format
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class AuditConfig:
    """Audit logging configuration."""
    
    # Storage settings
    storage_backend: str = "memory"  # "memory", "file", "dataset"
    file_path: Optional[str] = None
    dataset_path: Optional[str] = None
    
    # Retention settings
    max_events_memory: int = 10000
    retention_days: int = 90
    
    # Filtering
    enabled_event_types: Optional[List[AuditEventType]] = None
    disabled_event_types: Optional[List[AuditEventType]] = None
    
    # Performance
    buffer_size: int = 1000
    flush_interval: int = 60  # seconds
    
    # Security
    include_request_details: bool = True
    include_response_details: bool = False
    redact_sensitive_data: bool = True
    
    def should_log_event(self, event_type: AuditEventType) -> bool:
        """Check if event type should be logged."""
        if self.disabled_event_types and event_type in self.disabled_event_types:
            return False
        
        if self.enabled_event_types:
            return event_type in self.enabled_event_types
        
        return True


class AuditLogger:
    """Audit logger for security events."""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self._buffer: deque = deque(maxlen=config.buffer_size)
        self._memory_store: deque = deque(maxlen=config.max_events_memory)
        self._logger = logging.getLogger(__name__)
        
        # Storage backend
        self._file_handle = None
        self._dataset: Optional[FrameDataset] = None
        
        # Background tasks
        self._flush_task = None
        self._cleanup_task = None
        
        # Event counter
        self._event_counter = 0
    
    async def start(self):
        """Start the audit logger."""
        # Initialize storage backend
        if self.config.storage_backend == "file" and self.config.file_path:
            Path(self.config.file_path).parent.mkdir(parents=True, exist_ok=True)
            self._file_handle = open(self.config.file_path, "a")
        elif self.config.storage_backend == "dataset" and self.config.dataset_path:
            try:
                self._dataset = FrameDataset.open(self.config.dataset_path)
            except Exception:
                # Create new dataset for audit logs
                self._dataset = FrameDataset.create(self.config.dataset_path)
        
        # Start background tasks
        self._flush_task = asyncio.create_task(self._flush_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop the audit logger."""
        # Stop background tasks
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining events
        await self._flush_buffer()
        
        # Close storage
        if self._file_handle:
            self._file_handle.close()
    
    async def _flush_loop(self):
        """Periodically flush buffered events."""
        while True:
            try:
                await asyncio.sleep(self.config.flush_interval)
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
    
    async def _cleanup_loop(self):
        """Periodically clean up old events."""
        while True:
            try:
                await asyncio.sleep(86400)  # Daily cleanup
                await self._cleanup_old_events()
            except asyncio.CancelledError:
                break
    
    async def _flush_buffer(self):
        """Flush buffered events to storage."""
        if not self._buffer:
            return
        
        events = []
        while self._buffer:
            events.append(self._buffer.popleft())
        
        # Store based on backend
        if self.config.storage_backend == "memory":
            self._memory_store.extend(events)
        
        elif self.config.storage_backend == "file" and self._file_handle:
            for event in events:
                self._file_handle.write(event.to_json() + "\n")
            self._file_handle.flush()
        
        elif self.config.storage_backend == "dataset" and self._dataset:
            # Convert events to FrameRecords
            records = []
            for event in events:
                record = FrameRecord(
                    uuid=event.event_id,
                    type="audit_event",
                    title=f"{event.event_type}: {event.operation or 'Unknown'}",
                    content=event.to_json(),
                    metadata={
                        "event_type": event.event_type,
                        "principal_id": event.principal_id,
                        "success": event.success,
                        "severity": event.severity,
                        "timestamp": event.timestamp.isoformat(),
                    },
                    created_at=event.timestamp,
                    updated_at=event.timestamp,
                )
                records.append(record)
            
            # Batch insert
            self._dataset.add_records(records)
    
    async def _cleanup_old_events(self):
        """Clean up events older than retention period."""
        if self.config.retention_days <= 0:
            return
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.config.retention_days)
        
        if self.config.storage_backend == "memory":
            # Filter memory store
            self._memory_store = deque(
                (e for e in self._memory_store if e.timestamp > cutoff),
                maxlen=self.config.max_events_memory
            )
        
        elif self.config.storage_backend == "dataset" and self._dataset:
            # Delete old records from dataset
            self._dataset.delete_where(f"created_at < '{cutoff.isoformat()}'")
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _redact_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive data from event details."""
        if not self.config.redact_sensitive_data:
            return data
        
        sensitive_keys = {
            "password", "secret", "token", "api_key", "private_key",
            "client_secret", "access_token", "refresh_token"
        }
        
        redacted = {}
        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_keys):
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact_sensitive_data(value)
            else:
                redacted[key] = value
        
        return redacted
    
    async def log_event(
        self,
        event_type: AuditEventType,
        success: bool = True,
        principal_id: Optional[str] = None,
        principal_type: Optional[str] = None,
        principal_name: Optional[str] = None,
        auth_method: Optional[str] = None,
        operation: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an audit event.
        
        Args:
            event_type: Type of event
            success: Whether operation succeeded
            principal_id: ID of principal performing action
            principal_type: Type of principal (user, agent, service)
            principal_name: Human-readable name
            auth_method: Authentication method used
            operation: Operation being performed
            resource_type: Type of resource accessed
            resource_id: ID of resource accessed
            request_id: Request correlation ID
            session_id: Session ID
            client_ip: Client IP address
            user_agent: User agent string
            error_code: Error code if failed
            error_message: Error message if failed
            details: Additional event details
        """
        # Check if event should be logged
        if not self.config.should_log_event(event_type):
            return
        
        # Create event
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            success=success,
            principal_id=principal_id,
            principal_type=principal_type,
            principal_name=principal_name,
            auth_method=auth_method,
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=request_id,
            session_id=session_id,
            client_ip=client_ip,
            user_agent=user_agent,
            error_code=error_code,
            error_message=error_message,
            details=self._redact_sensitive_data(details or {}),
        )
        
        # Add to buffer
        self._buffer.append(event)
        
        # Log to standard logger as well
        log_msg = (
            f"Audit: {event.event_type} - "
            f"Principal: {principal_id or 'anonymous'} - "
            f"Operation: {operation or 'unknown'} - "
            f"Success: {success}"
        )
        
        if event.severity == "error":
            self._logger.error(log_msg)
        elif event.severity == "warning":
            self._logger.warning(log_msg)
        else:
            self._logger.info(log_msg)
        
        # Increment counter
        self._event_counter += 1
        
        # Flush if buffer is full
        if len(self._buffer) >= self.config.buffer_size:
            asyncio.create_task(self._flush_buffer())
    
    async def search_events(
        self,
        event_types: Optional[List[AuditEventType]] = None,
        principal_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        success: Optional[bool] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Search audit events.
        
        Args:
            event_types: Filter by event types
            principal_id: Filter by principal
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            start_time: Start time filter
            end_time: End time filter
            success: Filter by success/failure
            limit: Maximum events to return
            
        Returns:
            List of matching audit events
        """
        # For memory backend, search in-memory store
        if self.config.storage_backend == "memory":
            results = []
            
            for event in reversed(self._memory_store):
                # Apply filters
                if event_types and event.event_type not in event_types:
                    continue
                if principal_id and event.principal_id != principal_id:
                    continue
                if resource_type and event.resource_type != resource_type:
                    continue
                if resource_id and event.resource_id != resource_id:
                    continue
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue
                if success is not None and event.success != success:
                    continue
                
                results.append(event)
                if len(results) >= limit:
                    break
            
            return results
        
        # For other backends, would implement appropriate search
        return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit logging statistics."""
        stats = {
            "total_events": self._event_counter,
            "buffer_size": len(self._buffer),
            "storage_backend": self.config.storage_backend,
        }
        
        if self.config.storage_backend == "memory":
            stats["memory_events"] = len(self._memory_store)
        
        return stats