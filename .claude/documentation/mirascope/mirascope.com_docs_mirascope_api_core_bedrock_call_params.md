---
url: "https://mirascope.com/docs/mirascope/api/core/bedrock/call_params"
title: "mirascope.core.bedrock.call_params | Mirascope"
---

# mirascope.core.bedrock.call\_params [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/call_params\#mirascope-core-bedrock-call-params)

Usage

[Calls](https://mirascope.com/docs/mirascope/learn/calls#provider-specific-parameters)

## Class BedrockCallParams [Link to this heading](https://mirascope.com/docs/mirascope/api/core/bedrock/call_params\#bedrockcallparams)

The parameters to use when calling the Bedrock API.

[Bedrock converse API Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html)

**Bases:**

[BaseCallParams](https://mirascope.com/docs/mirascope/api/core/base/call_params#basecallparams)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| system | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[list](https://docs.python.org/3/library/stdtypes.html#list)\[SystemContentBlockTypeDef\]\] | - |
| inferenceConfig | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[InferenceConfigurationTypeDef\] | - |
| toolConfig | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[ToolConfigurationTypeDef\] | - |
| guardrailConfig | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[GuardrailConfigurationTypeDef\] | - |
| additionalModelRequestFields | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[Mapping\[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)\]\] | - |
| additionalModelResponseFieldPaths | [NotRequired](https://docs.python.org/3/library/typing.html#typing.NotRequired)\[[list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\]\] | - |

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