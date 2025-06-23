"""Cost tracking and attribution for MCP operations."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .collector import MetricsCollector


@dataclass
class LLMPricing:
    """Pricing for a specific LLM model."""
    
    provider: str
    model: str
    input_cost_per_1k: float  # Cost per 1k input tokens
    output_cost_per_1k: float  # Cost per 1k output tokens
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given token counts."""
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost


@dataclass
class StoragePricing:
    """Pricing for storage operations."""
    
    read_cost_per_gb: float = 0.01  # Cost per GB read
    write_cost_per_gb: float = 0.02  # Cost per GB written
    storage_cost_per_gb_month: float = 0.023  # Monthly storage cost
    
    def calculate_operation_cost(self, operation: str, size_bytes: int) -> float:
        """Calculate cost for a storage operation."""
        size_gb = size_bytes / (1024 ** 3)
        
        if operation in ["read", "search"]:
            return size_gb * self.read_cost_per_gb
        elif operation in ["write", "update"]:
            return size_gb * self.write_cost_per_gb
        elif operation == "delete":
            return 0.0  # No cost for deletion
        else:
            return 0.0


@dataclass
class PricingConfig:
    """Complete pricing configuration."""
    
    # Default LLM pricing (as of 2024)
    llm_pricing: dict[str, LLMPricing] = field(default_factory=lambda: {
        "openai:gpt-4": LLMPricing("openai", "gpt-4", 0.03, 0.06),
        "openai:gpt-3.5-turbo": LLMPricing("openai", "gpt-3.5-turbo", 0.0005, 0.0015),
        "anthropic:claude-3-opus": LLMPricing("anthropic", "claude-3-opus", 0.015, 0.075),
        "anthropic:claude-3-sonnet": LLMPricing("anthropic", "claude-3-sonnet", 0.003, 0.015),
        "cohere:command": LLMPricing("cohere", "command", 0.0015, 0.002),
    })
    
    storage_pricing: StoragePricing = field(default_factory=StoragePricing)
    
    # Bandwidth pricing
    bandwidth_cost_per_gb: float = 0.09  # Egress bandwidth cost
    
    @classmethod
    def from_file(cls, path: str) -> "PricingConfig":
        """Load pricing config from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        config = cls()
        
        # Load LLM pricing
        if "llm_pricing" in data:
            config.llm_pricing = {}
            for key, pricing in data["llm_pricing"].items():
                config.llm_pricing[key] = LLMPricing(**pricing)
        
        # Load storage pricing
        if "storage_pricing" in data:
            config.storage_pricing = StoragePricing(**data["storage_pricing"])
        
        # Load bandwidth pricing
        if "bandwidth_cost_per_gb" in data:
            config.bandwidth_cost_per_gb = data["bandwidth_cost_per_gb"]
        
        return config


@dataclass
class CostSummary:
    """Summary of costs for a period."""
    
    period_start: datetime
    period_end: datetime
    total_cost: float = 0.0
    llm_cost: float = 0.0
    storage_cost: float = 0.0
    bandwidth_cost: float = 0.0
    costs_by_provider: dict[str, float] = field(default_factory=dict)
    costs_by_operation: dict[str, float] = field(default_factory=dict)
    costs_by_agent: dict[str, float] = field(default_factory=dict)
    top_expensive_operations: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class CostReport:
    """Detailed cost report."""
    
    summary: CostSummary
    daily_breakdown: list[CostSummary] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    projected_monthly_cost: float = 0.0


class CostCalculator:
    """Calculate and track costs for operations."""
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        pricing_config: PricingConfig | None = None
    ):
        self.metrics = metrics_collector
        self.pricing = pricing_config or PricingConfig()
        
        # Cost tracking by operation
        self._operation_costs: dict[str, float] = {}
        
        # Aggregated costs
        self._daily_costs: dict[str, CostSummary] = {}
        
        # Token usage tracking for projections
        self._token_usage: dict[str, dict[str, int]] = {}
    
    async def track_llm_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation_id: str,
        agent_id: str | None = None,
        purpose: str | None = None
    ) -> float:
        """Track LLM API usage and calculate cost.
        
        Args:
            provider: LLM provider (openai, anthropic, etc.)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            operation_id: Associated operation ID
            agent_id: Optional agent identifier
            purpose: Purpose of the LLM call (enhancement, extraction, etc.)
            
        Returns:
            Calculated cost in USD
        """
        # Look up pricing
        pricing_key = f"{provider}:{model}"
        llm_pricing = self.pricing.llm_pricing.get(pricing_key)
        
        if not llm_pricing:
            # Use a default pricing if model not found
            llm_pricing = LLMPricing(provider, model, 0.01, 0.02)
        
        # Calculate cost
        cost = llm_pricing.calculate_cost(input_tokens, output_tokens)
        
        # Track operation cost
        self._operation_costs[operation_id] = self._operation_costs.get(operation_id, 0.0) + cost
        
        # Track token usage
        if provider not in self._token_usage:
            self._token_usage[provider] = {}
        if model not in self._token_usage[provider]:
            self._token_usage[provider][model] = {"input": 0, "output": 0}
        
        self._token_usage[provider][model]["input"] += input_tokens
        self._token_usage[provider][model]["output"] += output_tokens
        
        # Record metric
        await self.metrics.record_cost(
            operation_id=operation_id,
            cost_type="llm",
            provider=provider,
            amount_usd=cost,
            units=input_tokens + output_tokens,
            agent_id=agent_id,
            metadata={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "purpose": purpose
            }
        )
        
        return cost
    
    async def track_storage_usage(
        self,
        operation: str,
        size_bytes: int,
        agent_id: str | None = None,
        operation_id: str | None = None
    ) -> float:
        """Track storage operations and costs.
        
        Args:
            operation: Type of operation (read, write, delete)
            size_bytes: Size of data in bytes
            agent_id: Optional agent identifier
            operation_id: Optional operation ID
            
        Returns:
            Calculated cost in USD
        """
        # Calculate cost
        cost = self.pricing.storage_pricing.calculate_operation_cost(operation, size_bytes)
        
        # Track operation cost
        if operation_id:
            self._operation_costs[operation_id] = self._operation_costs.get(operation_id, 0.0) + cost
        
        # Record metric
        await self.metrics.record_cost(
            operation_id=operation_id or "storage",
            cost_type="storage",
            provider="lance",
            amount_usd=cost,
            units=size_bytes,
            agent_id=agent_id,
            metadata={
                "operation": operation,
                "size_bytes": size_bytes
            }
        )
        
        return cost
    
    async def track_bandwidth_usage(
        self,
        size_bytes: int,
        direction: str = "egress",
        agent_id: str | None = None,
        operation_id: str | None = None
    ) -> float:
        """Track bandwidth usage and costs.
        
        Args:
            size_bytes: Size of data transferred
            direction: Transfer direction (egress, ingress)
            agent_id: Optional agent identifier
            operation_id: Optional operation ID
            
        Returns:
            Calculated cost in USD
        """
        # Only charge for egress
        if direction != "egress":
            return 0.0
        
        # Calculate cost
        size_gb = size_bytes / (1024 ** 3)
        cost = size_gb * self.pricing.bandwidth_cost_per_gb
        
        # Track operation cost
        if operation_id:
            self._operation_costs[operation_id] = self._operation_costs.get(operation_id, 0.0) + cost
        
        # Record metric
        await self.metrics.record_cost(
            operation_id=operation_id or "bandwidth",
            cost_type="bandwidth",
            provider="network",
            amount_usd=cost,
            units=size_bytes,
            agent_id=agent_id,
            metadata={
                "direction": direction
            }
        )
        
        return cost
    
    async def get_cost_report(
        self,
        start_time: datetime,
        end_time: datetime,
        group_by: str = "agent"
    ) -> CostReport:
        """Generate cost attribution report.
        
        Args:
            start_time: Start of reporting period
            end_time: End of reporting period
            group_by: How to group costs (agent, operation, provider)
            
        Returns:
            Detailed cost report
        """
        # Create summary
        summary = CostSummary(
            period_start=start_time,
            period_end=end_time
        )
        
        # Get aggregated metrics from collector
        cost_metrics = await self.metrics.get_aggregated_metrics(
            "cost",
            interval="1h",
            lookback_hours=int((end_time - start_time).total_seconds() / 3600)
        )
        
        # Calculate totals from operation costs
        for op_id, cost in self._operation_costs.items():
            summary.total_cost += cost
        
        # Generate daily breakdown
        daily_breakdown = []
        current_date = start_time.date()
        end_date = end_time.date()
        
        while current_date <= end_date:
            day_start = datetime.combine(current_date, datetime.min.time(), timezone.utc)
            day_end = day_start + timedelta(days=1)
            
            day_summary = CostSummary(
                period_start=day_start,
                period_end=day_end
            )
            
            # Add to daily breakdown
            daily_breakdown.append(day_summary)
            current_date += timedelta(days=1)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(summary)
        
        # Calculate projected monthly cost
        days_in_period = (end_time - start_time).days or 1
        daily_average = summary.total_cost / days_in_period
        projected_monthly = daily_average * 30
        
        return CostReport(
            summary=summary,
            daily_breakdown=daily_breakdown,
            recommendations=recommendations,
            projected_monthly_cost=projected_monthly
        )
    
    def _generate_recommendations(self, summary: CostSummary) -> list[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Check if LLM costs are high
        if summary.llm_cost > summary.total_cost * 0.7:
            recommendations.append(
                "LLM costs represent over 70% of total costs. "
                "Consider using cheaper models for non-critical operations."
            )
        
        # Check for expensive providers
        if summary.costs_by_provider:
            most_expensive = max(summary.costs_by_provider.items(), key=lambda x: x[1])
            if most_expensive[1] > summary.total_cost * 0.5:
                recommendations.append(
                    f"{most_expensive[0]} accounts for over 50% of costs. "
                    f"Consider diversifying providers or negotiating rates."
                )
        
        # Check token usage patterns
        total_tokens = sum(
            usage["input"] + usage["output"]
            for provider_models in self._token_usage.values()
            for usage in provider_models.values()
        )
        
        if total_tokens > 1_000_000:
            recommendations.append(
                "High token usage detected. Consider implementing caching "
                "for frequently requested enhancements."
            )
        
        return recommendations
    
    def get_operation_cost(self, operation_id: str) -> float:
        """Get total cost for a specific operation."""
        return self._operation_costs.get(operation_id, 0.0)