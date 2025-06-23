"""Integration of monitoring with MCP server components."""

import time
import uuid
from typing import Any, Dict, Optional

from contextframe.mcp.handlers import MessageHandler as BaseMessageHandler
from contextframe.mcp.tools import ToolRegistry as BaseToolRegistry

from .collector import MetricsCollector, MetricsConfig
from .cost import CostCalculator, PricingConfig
from .performance import PerformanceMonitor
from .tools import init_monitoring_tools
from .usage import UsageTracker


class MonitoringSystem:
    """Central monitoring system for MCP server."""
    
    def __init__(
        self,
        dataset: Any,
        metrics_config: MetricsConfig | None = None,
        pricing_config: PricingConfig | None = None
    ):
        # Initialize components
        self.collector = MetricsCollector(dataset, metrics_config)
        self.usage_tracker = UsageTracker(self.collector)
        self.performance_monitor = PerformanceMonitor(self.collector)
        self.cost_calculator = CostCalculator(self.collector, pricing_config)
        
        # Initialize monitoring tools
        init_monitoring_tools(
            self.collector,
            self.usage_tracker,
            self.performance_monitor,
            self.cost_calculator
        )
    
    async def start(self) -> None:
        """Start monitoring system."""
        await self.collector.start()
        await self.performance_monitor.start()
    
    async def stop(self) -> None:
        """Stop monitoring system."""
        await self.performance_monitor.stop()
        await self.collector.stop()


class MonitoredMessageHandler(BaseMessageHandler):
    """Message handler with integrated monitoring."""
    
    def __init__(self, server: Any, monitoring: MonitoringSystem | None = None):
        super().__init__(server)
        self.monitoring = monitoring
    
    def _get_agent_id(self, message: dict[str, Any]) -> str | None:
        """Extract agent ID from message metadata."""
        # Check for agent ID in various places
        if "agent_id" in message:
            return message["agent_id"]
        
        # Check in params
        params = message.get("params", {})
        if isinstance(params, dict):
            if "agent_id" in params:
                return params["agent_id"]
            # Check metadata
            metadata = params.get("metadata", {})
            if isinstance(metadata, dict) and "agent_id" in metadata:
                return metadata["agent_id"]
        
        return None
    
    async def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Handle message with monitoring."""
        if not self.monitoring:
            # No monitoring, use base implementation
            return await super().handle(message)
        
        # Generate operation ID
        operation_id = str(uuid.uuid4())
        method = message.get("method", "unknown")
        agent_id = self._get_agent_id(message)
        
        # Start performance tracking
        context = await self.monitoring.performance_monitor.start_operation(
            operation_id=operation_id,
            operation_type=method,
            agent_id=agent_id,
            metadata={
                "request_id": message.get("id"),
                "params": message.get("params", {})
            }
        )
        
        try:
            # Execute base handler
            result = await super().handle(message)
            
            # Track success
            result_size = len(str(result)) if result else 0
            await self.monitoring.performance_monitor.end_operation(
                operation_id=operation_id,
                status="success",
                result_size=result_size
            )
            
            # Track specific operations
            if method == "tools/call" and result and "result" in result:
                await self._track_tool_call(message, result, agent_id)
            elif method == "resources/read" and result and "result" in result:
                await self._track_resource_read(message, result, agent_id)
            
            return result
            
        except Exception as e:
            # Track error
            await self.monitoring.performance_monitor.end_operation(
                operation_id=operation_id,
                status="error",
                error=str(e)
            )
            raise
    
    async def _track_tool_call(
        self,
        request: dict[str, Any],
        response: dict[str, Any],
        agent_id: str | None
    ) -> None:
        """Track tool call metrics."""
        params = request.get("params", {})
        tool_name = params.get("name", "unknown")
        
        # Track tool usage
        await self.monitoring.usage_tracker.track_query(
            query=tool_name,
            query_type="tool_call",
            result_count=1,
            execution_time_ms=0,  # Already tracked in performance
            agent_id=agent_id,
            success=True,
            metadata={"tool": tool_name}
        )
        
        # Track document access for document-related tools
        if tool_name in ["get_document", "search_documents", "update_document"]:
            result = response.get("result", {})
            
            if tool_name == "get_document" and "document" in result:
                doc_id = result["document"].get("uuid")
                if doc_id:
                    await self.monitoring.usage_tracker.track_document_access(
                        document_id=doc_id,
                        operation="read",
                        agent_id=agent_id
                    )
            
            elif tool_name == "search_documents" and "documents" in result:
                for doc in result["documents"]:
                    doc_id = doc.get("uuid")
                    if doc_id:
                        await self.monitoring.usage_tracker.track_document_access(
                            document_id=doc_id,
                            operation="search_hit",
                            agent_id=agent_id
                        )
    
    async def _track_resource_read(
        self,
        request: dict[str, Any],
        response: dict[str, Any],
        agent_id: str | None
    ) -> None:
        """Track resource read metrics."""
        params = request.get("params", {})
        uri = params.get("uri", "unknown")
        
        # Track resource access
        await self.monitoring.usage_tracker.track_query(
            query=uri,
            query_type="resource_read",
            result_count=1,
            execution_time_ms=0,
            agent_id=agent_id,
            success=True,
            metadata={"uri": uri}
        )


class MonitoredToolRegistry(BaseToolRegistry):
    """Tool registry with cost tracking."""
    
    def __init__(self, dataset: Any, transport: Any, monitoring: MonitoringSystem | None = None):
        super().__init__(dataset, transport)
        self.monitoring = monitoring
    
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call tool with cost tracking for LLM operations."""
        # Check if this is an enhancement tool that uses LLMs
        llm_tools = [
            "enhance_context",
            "extract_metadata", 
            "generate_tags",
            "improve_title",
            "enhance_for_purpose",
            "batch_enhance"
        ]
        
        if name in llm_tools and self.monitoring:
            # Track LLM usage (simplified - in reality would need actual token counts)
            operation_id = arguments.get("operation_id", str(uuid.uuid4()))
            
            # Estimate tokens based on content size
            content_size = 0
            if "content" in arguments:
                content_size = len(arguments["content"])
            elif "document_id" in arguments:
                # Would need to fetch document to get size
                content_size = 1000  # Estimate
            
            # Rough token estimation (1 token ≈ 4 characters)
            estimated_tokens = content_size // 4
            
            # Track cost (assuming GPT-3.5 by default)
            await self.monitoring.cost_calculator.track_llm_usage(
                provider="openai",
                model="gpt-3.5-turbo",
                input_tokens=estimated_tokens,
                output_tokens=estimated_tokens // 2,  # Rough estimate
                operation_id=operation_id,
                purpose=name
            )
        
        # Call base implementation
        return await super().call_tool(name, arguments)