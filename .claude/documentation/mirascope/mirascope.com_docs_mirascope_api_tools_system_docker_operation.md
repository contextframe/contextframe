---
url: "https://mirascope.com/docs/mirascope/api/tools/system/docker_operation"
title: "mirascope.tools.system._docker_operation | Mirascope"
---

# mirascope.tools.system.\_docker\_operation [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#mirascope-tools-system-docker-operation)

## Module \_docker\_operation [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#docker-operation)

## Class DockerOperationToolKitConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#dockeroperationtoolkitconfig)

Configuration for `DockerOperationToolKit` toolkit

**Bases:**

\_ConfigurableToolConfig

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| docker\_image | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| max\_memory | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| allow\_network | [bool](https://docs.python.org/3/library/functions.html#bool) | - |

## Class DockerOperation [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#dockeroperation)

Base class for Docker operations.

**Bases:** ConfigurableTool\[[DockerOperationToolKitConfig](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation#dockeroperationtoolkitconfig)\], ABC

## Class DockerContainer [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#dockercontainer)

**Bases:**

[BaseModel](https://docs.pydantic.dev/latest/api/base_model/)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| config | [DockerOperationToolKitConfig](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation#dockeroperationtoolkitconfig) | - |
| container | Container | - |

## Class DockerOperationToolKit [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#dockeroperationtoolkit)

ToolKit for executing Python code and shell commands in a Docker container.

**Bases:**

ConfigurableToolKit\[[DockerOperationToolKitConfig](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation#dockeroperationtoolkitconfig)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| config | [DockerOperationToolKitConfig](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation#dockeroperationtoolkitconfig) | - |
| docker\_container | [DockerContainer](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation#dockercontainer) | - |

## Function create\_tools [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#create-tools)

The method to create the tools.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [list](https://docs.python.org/3/library/stdtypes.html#list)\[[type](https://docs.python.org/3/library/functions.html#type)\[[BaseTool](https://mirascope.com/docs/mirascope/api/core/base/tool#basetool)\]\] | - |

## Class ExecutePython [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#executepython)

Tool for executing Python code in a Docker container.

**Bases:**

[DockerOperation](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation#dockeroperation)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| code | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| requirements | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#call)

Executes Python code in a Docker container.

docker\_image: {self. **config**.docker\_image}
allow\_network: {self. **config**.allow\_network}

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Output of the code execution |

## Class ExecuteShell [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#executeshell)

Tool for executing shell commands in a Docker container.

**Bases:**

[DockerOperation](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation#dockeroperation)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| command | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/docker_operation\#call)

Executes shell commands in a Docker container.

docker\_image: {self. **config**.docker\_image}
allow\_network: {self. **config**.allow\_network}

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Output of the command execution |

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