---
url: "https://mirascope.com/docs/mirascope/api/tools/system/file_system"
title: "mirascope.tools.system._file_system | Mirascope"
---

# mirascope.tools.system.\_file\_system [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#mirascope-tools-system-file-system)

## Module \_file\_system [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#file-system)

## Class FileSystemToolKitConfig [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#filesystemtoolkitconfig)

Configuration for file\_system toolkit

**Bases:**

\_ConfigurableToolConfig

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| max\_file\_size | [int](https://docs.python.org/3/library/functions.html#int) | - |
| allowed\_extensions | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[str](https://docs.python.org/3/library/stdtypes.html#str)\] | - |

## Class FileOperation [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#fileoperation)

Base class for file system operations.

**Bases:** ConfigurableTool\[[FileSystemToolKitConfig](https://mirascope.com/docs/mirascope/api/tools/system/file_system#filesystemtoolkitconfig)\], ABC

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| base\_directory | Path | - |

## Class FileSystemToolKit [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#filesystemtoolkit)

ToolKit for file system operations.
Read, write, list, create, and delete files and directories.

**Bases:**

ConfigurableToolKit\[[FileSystemToolKitConfig](https://mirascope.com/docs/mirascope/api/tools/system/file_system#filesystemtoolkitconfig)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| config | [FileSystemToolKitConfig](https://mirascope.com/docs/mirascope/api/tools/system/file_system#filesystemtoolkitconfig) | - |
| base\_directory | Path | - |

## Class ReadFile [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#readfile)

Tool for reading file contents.

**Bases:**

[FileOperation](https://mirascope.com/docs/mirascope/api/tools/system/file_system#fileoperation)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| path | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#call)

Read and return file contents.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | File contents or error message if operation fails |

## Class WriteFile [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#writefile)

Tool for writing content to a file.

**Bases:**

[FileOperation](https://mirascope.com/docs/mirascope/api/tools/system/file_system#fileoperation)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| path | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#call)

Write content to file and return status.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Success message or error message if operation fails |

## Class ListDirectory [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#listdirectory)

Tool for listing directory contents.

**Bases:**

[FileOperation](https://mirascope.com/docs/mirascope/api/tools/system/file_system#fileoperation)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| path | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#call)

List directory contents and return formatted string.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Formatted directory listing or error message if operation fails |

## Class CreateDirectory [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#createdirectory)

Tool for creating directories.

**Bases:**

[FileOperation](https://mirascope.com/docs/mirascope/api/tools/system/file_system#fileoperation)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| path | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#call)

Create directory and return status.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Success message or error message if operation fails |

## Class DeleteFile [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#deletefile)

Tool for deleting files.

**Bases:**

[FileOperation](https://mirascope.com/docs/mirascope/api/tools/system/file_system#fileoperation)

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| path | [str](https://docs.python.org/3/library/stdtypes.html#str) | - |

## Function call [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#call)

Delete file and return status.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| self | Any | - |

### Returns

| Type | Description |
| --- | --- |
| [str](https://docs.python.org/3/library/stdtypes.html#str) | Success message or error message if operation fails |

## Function validate\_base\_directory [Link to this heading](https://mirascope.com/docs/mirascope/api/tools/system/file_system\#validate-base-directory)

Validates that the base directory exists and is a directory.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| cls | Any | - |
| v | Path | The path to validate |

### Returns

| Type | Description |
| --- | --- |
| Path | The validated path |

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