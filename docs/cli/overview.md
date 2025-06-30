# CLI Reference Overview

The ContextFrame CLI provides command-line tools for managing and interacting with ContextFrame datasets. It offers a convenient interface for common operations without writing Python code.

## Installation

The CLI is included when you install ContextFrame:

```bash
pip install contextframe
```

After installation, the `contextframe` command will be available in your terminal.

## Core Commands

The ContextFrame CLI is organized into command groups:

- **`dataset`** - Create, inspect, and manage datasets
- **`record`** - Add, update, and query records
- **`search`** - Perform vector and text searches
- **`export`** - Export data in various formats
- **`import`** - Import data from different sources
- **`version`** - Manage dataset versions

## Quick Examples

### Create a new dataset
```bash
contextframe dataset create my_docs.lance
```

### Add a document
```bash
contextframe record add my_docs.lance --file document.txt --title "My Document"
```

### Search for similar documents
```bash
contextframe search vector my_docs.lance --query "machine learning concepts" --limit 5
```

### Export to JSON
```bash
contextframe export json my_docs.lance output.json
```

## Global Options

All commands support these global options:

- `--help` - Show help for any command
- `--version` - Display ContextFrame version
- `--verbose` - Enable detailed output
- `--quiet` - Suppress non-essential output
- `--config` - Specify configuration file

## Configuration

The CLI can be configured using:

1. **Configuration file** (`~/.contextframe/config.yaml`)
2. **Environment variables** (prefixed with `CONTEXTFRAME_`)
3. **Command-line options** (highest priority)

Example configuration file:
```yaml
# ~/.contextframe/config.yaml
default_embedding_model: "openai/text-embedding-3-small"
openai_api_key: "your-key-here"
default_chunk_size: 1000
verbose: false
```

## Next Steps

- See [Commands](commands.md) for detailed command reference
- Learn about [Configuration](configuration.md) options
- Check out usage examples in the [Cookbook](../cookbook/index.md)