---
url: "https://mirascope.com/docs/mirascope/api/core/costs/calculate_cost"
title: "mirascope.core.costs.calculate_cost | Mirascope"
---

# mirascope.core.costs.calculate\_cost [Link to this heading](https://mirascope.com/docs/mirascope/api/core/costs/calculate_cost\#mirascope-core-costs-calculate-cost)

Cost calculation utilities for LLM API calls.

## Function calculate\_cost [Link to this heading](https://mirascope.com/docs/mirascope/api/core/costs/calculate_cost\#calculate-cost)

Calculate the cost for an LLM API call.

This function routes to the appropriate provider-specific cost calculation function,
preserving existing behavior while providing a unified interface.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| provider | [Provider](https://mirascope.com/docs/mirascope/api/core/base/types#provider) | The LLM provider (e.g., "openai", "anthropic") |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | The model name (e.g., "gpt-4", "claude-3-opus") |
| metadata= None | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) \| [None](https://docs.python.org/3/library/constants.html#None) | Additional metadata required for cost calculation |

### Returns

| Type | Description |
| --- | --- |
| [float](https://docs.python.org/3/library/functions.html#float) \| [None](https://docs.python.org/3/library/constants.html#None) | The calculated cost in USD or None if unable to calculate |

Copy as Markdown

#### Provider

OpenAI

#### On this page

Copy as Markdown

#### Provider

OpenAI

#### On this page

## Cookie Consent

We use cookies to track usage and improve the site.

RejectAccept