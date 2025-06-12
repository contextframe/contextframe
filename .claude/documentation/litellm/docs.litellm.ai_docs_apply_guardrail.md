---
url: "https://docs.litellm.ai/docs/apply_guardrail"
title: "/guardrails/apply_guardrail | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/apply_guardrail#__docusaurus_skipToContent_fallback)

On this page

# /guardrails/apply\_guardrail

Use this endpoint to directly call a guardrail configured on your LiteLLM instance. This is useful when you have services that need to directly call a guardrail.

## Usage [​](https://docs.litellm.ai/docs/apply_guardrail\#usage "Direct link to Usage")

* * *

In this example `mask_pii` is the guardrail name configured on LiteLLM.

Example calling the endpoint

```codeBlockLines_e6Vv codeBlockLinesWithNumbering_o6Pm
curl -X POST 'http://localhost:4000/guardrails/apply_guardrail' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer your-api-key' \
-d '{
    "guardrail_name": "mask_pii",
    "text": "My name is John Doe and my email is john@example.com",
    "language": "en",
    "entities": ["NAME", "EMAIL"]
}'

```

## Request Format [​](https://docs.litellm.ai/docs/apply_guardrail\#request-format "Direct link to Request Format")

* * *

The request body should follow the ApplyGuardrailRequest format.

#### Example Request Body [​](https://docs.litellm.ai/docs/apply_guardrail\#example-request-body "Direct link to Example Request Body")

```codeBlockLines_e6Vv
{
    "guardrail_name": "mask_pii",
    "text": "My name is John Doe and my email is john@example.com",
    "language": "en",
    "entities": ["NAME", "EMAIL"]
}

```

#### Required Fields [​](https://docs.litellm.ai/docs/apply_guardrail\#required-fields "Direct link to Required Fields")

- **guardrail\_name** (string):

The identifier for the guardrail to apply (e.g., "mask\_pii").
- **text** (string):

The input text to process through the guardrail.

#### Optional Fields [​](https://docs.litellm.ai/docs/apply_guardrail\#optional-fields "Direct link to Optional Fields")

- **language** (string):

The language of the input text (e.g., "en" for English).
- **entities** (array of strings):

Specific entities to process or filter (e.g., \["NAME", "EMAIL"\]).

## Response Format [​](https://docs.litellm.ai/docs/apply_guardrail\#response-format "Direct link to Response Format")

* * *

The response will contain the processed text after applying the guardrail.

#### Example Response [​](https://docs.litellm.ai/docs/apply_guardrail\#example-response "Direct link to Example Response")

```codeBlockLines_e6Vv
{
    "response_text": "My name is [REDACTED] and my email is [REDACTED]"
}

```

#### Response Fields [​](https://docs.litellm.ai/docs/apply_guardrail\#response-fields "Direct link to Response Fields")

- **response\_text** (string):

The text after applying the guardrail.

- [Usage](https://docs.litellm.ai/docs/apply_guardrail#usage)
- [Request Format](https://docs.litellm.ai/docs/apply_guardrail#request-format)
- [Response Format](https://docs.litellm.ai/docs/apply_guardrail#response-format)