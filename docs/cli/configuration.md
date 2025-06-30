# CLI Configuration

The ContextFrame CLI can be configured through multiple methods, allowing flexibility in different environments. Configuration follows a hierarchy where command-line options override environment variables, which override configuration files.

## Configuration Hierarchy

1. **Command-line options** (highest priority)
2. **Environment variables**
3. **User configuration file** (`~/.contextframe/config.yaml`)
4. **Project configuration file** (`.contextframe.yaml` in current directory)
5. **Default values** (lowest priority)

## Configuration File

The main configuration file is located at `~/.contextframe/config.yaml`. You can also place a `.contextframe.yaml` file in your project directory for project-specific settings.

### Example Configuration File

```yaml
# ~/.contextframe/config.yaml

# Embedding configuration
embedding:
  default_model: "openai/text-embedding-3-small"
  batch_size: 100
  cache_embeddings: true
  cache_dir: "~/.contextframe/cache/embeddings"

# API Keys (can also use environment variables)
api_keys:
  openai: "sk-..."
  anthropic: "sk-ant-..."
  cohere: "..."

# Search defaults
search:
  default_limit: 10
  similarity_threshold: 0.7
  enable_reranking: false

# Import/Export settings
import:
  default_chunk_size: 1000
  chunk_overlap: 200
  encoding: "utf-8"
  
export:
  include_embeddings: false
  compression: "gzip"

# CLI behavior
cli:
  verbose: false
  color_output: true
  progress_bars: true
  confirm_destructive: true
  
# Storage configuration
storage:
  default_location: "~/.contextframe/datasets"
  s3:
    region: "us-east-1"
    endpoint_url: null
  gcs:
    project_id: "my-project"
  azure:
    account_name: "myaccount"

# Logging
logging:
  level: "INFO"
  file: "~/.contextframe/logs/cli.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Environment Variables

All configuration options can be set via environment variables. The pattern is:
`CONTEXTFRAME_<SECTION>_<KEY>`

### Common Environment Variables

```bash
# API Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export COHERE_API_KEY="..."

# ContextFrame specific
export CONTEXTFRAME_EMBEDDING_DEFAULT_MODEL="openai/text-embedding-3-large"
export CONTEXTFRAME_EMBEDDING_BATCH_SIZE="50"
export CONTEXTFRAME_CLI_VERBOSE="true"
export CONTEXTFRAME_STORAGE_DEFAULT_LOCATION="/data/contextframe"

# Storage backends
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
export AZURE_STORAGE_ACCOUNT="..."
export AZURE_STORAGE_KEY="..."
```

## Command-Line Configuration

### Setting Configuration Values

```bash
# Set a single value
contextframe config set embedding.default_model "cohere/embed-english-v3.0"

# Set nested values
contextframe config set storage.s3.region "eu-west-1"

# Set from environment variable
contextframe config set api_keys.openai "$OPENAI_API_KEY"
```

### Getting Configuration Values

```bash
# Get a specific value
contextframe config get embedding.default_model

# Get all values in a section
contextframe config get embedding

# Show entire configuration
contextframe config show

# Show configuration with sources (file, env, default)
contextframe config show --with-sources
```

### Configuration Profiles

You can maintain multiple configuration profiles:

```bash
# Create a new profile
contextframe config profile create production

# Switch profiles
contextframe config profile use production

# List profiles
contextframe config profile list

# Delete a profile
contextframe config profile delete staging
```

## Project Configuration

Place a `.contextframe.yaml` file in your project root for project-specific settings:

```yaml
# .contextframe.yaml
embedding:
  default_model: "sentence-transformers/all-MiniLM-L6-v2"
  
storage:
  default_location: "./data/contextframe"
  
import:
  chunk_size: 500
  chunk_overlap: 50
```

## Configuration for Different Environments

### Development
```yaml
# ~/.contextframe/profiles/development.yaml
cli:
  verbose: true
  confirm_destructive: true
  
logging:
  level: "DEBUG"
  
embedding:
  cache_embeddings: true
```

### Production
```yaml
# ~/.contextframe/profiles/production.yaml
cli:
  verbose: false
  confirm_destructive: true
  
logging:
  level: "WARNING"
  
storage:
  s3:
    region: "us-east-1"
    server_side_encryption: "AES256"
```

### CI/CD
```bash
# In CI/CD scripts
export CONTEXTFRAME_CLI_CONFIRM_DESTRUCTIVE=false
export CONTEXTFRAME_CLI_COLOR_OUTPUT=false
export CONTEXTFRAME_CLI_PROGRESS_BARS=false
```

## Advanced Configuration

### Custom Embedding Providers

```yaml
embedding:
  providers:
    custom_ollama:
      type: "ollama"
      base_url: "http://localhost:11434"
      model: "nomic-embed-text"
      
    custom_openai:
      type: "openai"
      base_url: "https://api.custom.com/v1"
      api_key_env: "CUSTOM_API_KEY"
```

### Storage Options

```yaml
storage:
  backends:
    primary_s3:
      type: "s3"
      bucket: "my-contextframe-data"
      prefix: "datasets/"
      region: "us-east-1"
      storage_class: "STANDARD_IA"
      
    backup_gcs:
      type: "gcs"
      bucket: "contextframe-backup"
      project_id: "my-project"
```

### Performance Tuning

```yaml
performance:
  max_parallel_imports: 4
  embedding_queue_size: 1000
  search_cache_size: 100
  search_cache_ttl: 3600
  
  lance:
    read_batch_size: 1024
    write_batch_size: 1024
    num_threads: 8
```

## Debugging Configuration

### View Effective Configuration

```bash
# Show what configuration is actually being used
contextframe config debug

# Test configuration loading
contextframe config test

# Validate configuration file
contextframe config validate ~/.contextframe/config.yaml
```

### Configuration Precedence Example

Given:
1. Default: `embedding.default_model = "openai/text-embedding-ada-002"`
2. Config file: `embedding.default_model = "openai/text-embedding-3-small"`
3. Environment: `CONTEXTFRAME_EMBEDDING_DEFAULT_MODEL="cohere/embed-english-v3.0"`
4. Command line: `--embedding-model "custom/model"`

The effective value will be: `"custom/model"`

## Security Best Practices

1. **Never commit API keys** - Use environment variables or secure key management
2. **Use file permissions** - Protect config files: `chmod 600 ~/.contextframe/config.yaml`
3. **Separate environments** - Use different profiles for dev/staging/production
4. **Rotate keys regularly** - Update API keys and credentials periodically
5. **Use key references** - Reference environment variables instead of embedding keys:

```yaml
api_keys:
  openai: "${OPENAI_API_KEY}"
  anthropic: "${ANTHROPIC_API_KEY}"
```

## Troubleshooting

### Configuration Not Loading

```bash
# Check which config files are being loaded
contextframe config debug --show-files

# Verify environment variables
contextframe config debug --show-env

# Test specific configuration file
contextframe --config /path/to/config.yaml config show
```

### Common Issues

1. **YAML syntax errors** - Use `contextframe config validate` to check syntax
2. **Permission denied** - Check file permissions on config files
3. **Environment variables not working** - Ensure proper naming: `CONTEXTFRAME_SECTION_KEY`
4. **Relative paths** - Use absolute paths or paths relative to config file location