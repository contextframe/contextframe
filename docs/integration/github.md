# GitHub Connector

The GitHub connector enables importing code files, documentation, issues, and other content from GitHub repositories into ContextFrame. This guide covers setup, usage, and advanced patterns.

## Overview

The GitHub connector can import:
- Source code files
- Markdown documentation
- Issues and pull requests
- Wiki pages
- Release notes
- Repository metadata

## Installation

The GitHub connector is included with ContextFrame:

```python
from contextframe.connectors import GitHubConnector
```

## Authentication

### Personal Access Token

The recommended authentication method:

```python
connector = GitHubConnector(
    token="ghp_xxxxxxxxxxxxxxxxxxxx",
    owner="octocat",
    repo="hello-world"
)
```

### Creating a Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` - Full repository access
   - `read:org` - Read organization data (if needed)
4. Copy the token immediately

### Environment Variables

Best practice for security:

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
export GITHUB_OWNER="myorg"
export GITHUB_REPO="myrepo"
```

```python
import os

connector = GitHubConnector(
    token=os.getenv("GITHUB_TOKEN"),
    owner=os.getenv("GITHUB_OWNER"),
    repo=os.getenv("GITHUB_REPO")
)
```

## Basic Usage

### Import Repository Files

```python
from contextframe import FrameDataset
from contextframe.connectors import GitHubConnector

# Create dataset
dataset = FrameDataset.create("github_docs.lance")

# Setup connector
connector = GitHubConnector(
    token="your-token",
    owner="facebook",
    repo="react"
)

# Authenticate
connector.authenticate()

# Sync documentation files
documents = connector.sync_documents(
    path="docs",
    file_pattern="**/*.md",
    branch="main"
)

# Import to dataset
records = []
for doc in documents:
    record = connector.map_to_frame_record(doc)
    records.append(record)

dataset.add_many(records)
print(f"Imported {len(records)} documents")
```

### Import Specific Files

```python
# Import only specific file types
documents = connector.sync_documents(
    file_pattern="**/*.py",  # Python files
    exclude_paths=[
        "**/test_*",
        "**/tests/**",
        "**/__pycache__/**"
    ]
)

# Import from specific directory
documents = connector.sync_documents(
    path="src/components",
    file_pattern="**/*.tsx",
    include_content=True
)
```

### Import Issues

```python
# Get repository issues
issues = connector.sync_issues(
    state="open",  # open, closed, all
    labels=["bug", "enhancement"],
    sort="updated",
    direction="desc",
    since="2024-01-01T00:00:00Z"
)

# Convert to FrameRecords
for issue in issues:
    record = FrameRecord.create(
        title=f"Issue #{issue.number}: {issue.title}",
        content=issue.body or "No description",
        author=issue.user.login,
        tags=["github-issue"] + [label.name for label in issue.labels],
        status="open" if issue.state == "open" else "closed",
        source_url=issue.html_url,
        custom_metadata={
            "github_issue_number": issue.number,
            "github_issue_state": issue.state,
            "github_assignees": [a.login for a in issue.assignees],
            "github_milestone": issue.milestone.title if issue.milestone else None,
            "github_created_at": issue.created_at.isoformat(),
            "github_updated_at": issue.updated_at.isoformat()
        }
    )
    dataset.add(record)
```

## Advanced Features

### Multi-Repository Import

```python
def import_multiple_repos(dataset, repos):
    """Import from multiple repositories."""
    
    for repo_config in repos:
        print(f"Importing from {repo_config['owner']}/{repo_config['repo']}...")
        
        connector = GitHubConnector(
            token=os.getenv("GITHUB_TOKEN"),
            owner=repo_config['owner'],
            repo=repo_config['repo']
        )
        
        try:
            connector.authenticate()
            
            # Sync documents
            documents = connector.sync_documents(
                path=repo_config.get('path', ''),
                file_pattern=repo_config.get('pattern', '**/*.md'),
                branch=repo_config.get('branch', 'main')
            )
            
            # Add repository context to each record
            records = []
            for doc in documents:
                record = connector.map_to_frame_record(doc)
                record.metadata['collection'] = f"{repo_config['owner']}-{repo_config['repo']}"
                record.metadata['tags'].append(f"repo:{repo_config['repo']}")
                records.append(record)
            
            dataset.add_many(records)
            print(f"  Imported {len(records)} files")
            
        except Exception as e:
            print(f"  Error: {e}")

# Example usage
repos = [
    {
        'owner': 'microsoft',
        'repo': 'TypeScript',
        'path': 'doc',
        'pattern': '**/*.md'
    },
    {
        'owner': 'nodejs',
        'repo': 'node',
        'path': 'doc/api',
        'pattern': '*.md'
    }
]

import_multiple_repos(dataset, repos)
```

### Branch Comparison

```python
def compare_branches(connector, base_branch, compare_branch):
    """Compare documentation between branches."""
    
    # Get files from base branch
    base_docs = connector.sync_documents(
        branch=base_branch,
        file_pattern="**/*.md"
    )
    base_paths = {doc.path for doc in base_docs}
    
    # Get files from compare branch
    compare_docs = connector.sync_documents(
        branch=compare_branch,
        file_pattern="**/*.md"
    )
    compare_paths = {doc.path for doc in compare_docs}
    
    # Find differences
    added = compare_paths - base_paths
    removed = base_paths - compare_paths
    common = base_paths & compare_paths
    
    # Check for modifications
    modified = []
    for path in common:
        base_doc = next(d for d in base_docs if d.path == path)
        compare_doc = next(d for d in compare_docs if d.path == path)
        
        if base_doc.sha != compare_doc.sha:
            modified.append(path)
    
    return {
        'added': list(added),
        'removed': list(removed),
        'modified': modified
    }
```

### Pull Request Analysis

```python
def analyze_pull_requests(connector, dataset):
    """Import and analyze pull requests."""
    
    # Get recent PRs
    pulls = connector.sync_pull_requests(
        state="all",
        sort="updated",
        direction="desc",
        per_page=100
    )
    
    for pr in pulls:
        # Get PR files
        files = connector.get_pull_request_files(pr.number)
        
        # Create PR summary record
        pr_record = FrameRecord.create(
            title=f"PR #{pr.number}: {pr.title}",
            content=f"""
# Pull Request #{pr.number}

**Title**: {pr.title}
**Author**: {pr.user.login}
**State**: {pr.state}
**Created**: {pr.created_at}
**Updated**: {pr.updated_at}

## Description
{pr.body or 'No description provided'}

## Changes
- Files changed: {len(files)}
- Additions: {sum(f.additions for f in files)}
- Deletions: {sum(f.deletions for f in files)}

## Files Modified
{chr(10).join(f"- {f.filename} (+{f.additions}/-{f.deletions})" for f in files)}
""",
            author=pr.user.login,
            tags=["github-pr", f"pr-{pr.state}"],
            source_url=pr.html_url,
            custom_metadata={
                "github_pr_number": pr.number,
                "github_pr_state": pr.state,
                "github_pr_merged": pr.merged,
                "github_pr_base": pr.base.ref,
                "github_pr_head": pr.head.ref,
                "github_pr_files": [f.filename for f in files]
            }
        )
        
        dataset.add(pr_record)
```

### Code Analysis

```python
def analyze_code_files(connector, dataset, language="python"):
    """Import and analyze code files."""
    
    # Language to extension mapping
    extensions = {
        "python": "**/*.py",
        "javascript": "**/*.js",
        "typescript": "**/*.ts",
        "java": "**/*.java",
        "go": "**/*.go"
    }
    
    # Sync code files
    files = connector.sync_documents(
        file_pattern=extensions.get(language, "**/*"),
        include_content=True
    )
    
    for file in files:
        # Skip large files
        if file.size > 100000:  # 100KB
            continue
        
        # Create record with code analysis
        record = connector.map_to_frame_record(file)
        
        # Add code-specific metadata
        content = file.decoded_content
        lines = content.split('\n')
        
        record.metadata['custom_metadata'].update({
            'code_language': language,
            'code_lines': len(lines),
            'code_size': file.size,
            'has_tests': 'test' in file.path.lower(),
            'is_config': any(file.name.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.toml']),
            'imports': extract_imports(content, language)
        })
        
        # Add code-specific tags
        if 'test' in file.path.lower():
            record.metadata['tags'].append('test-code')
        if file.path.startswith('src/'):
            record.metadata['tags'].append('source-code')
        if file.path.startswith('examples/'):
            record.metadata['tags'].append('example-code')
        
        dataset.add(record)

def extract_imports(content, language):
    """Extract import statements from code."""
    imports = []
    
    if language == "python":
        import re
        # Match import statements
        import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(.+)$'
        for line in content.split('\n'):
            match = re.match(import_pattern, line.strip())
            if match:
                if match.group(1):  # from X import Y
                    imports.append(match.group(1))
                else:  # import X
                    imports.extend(m.strip() for m in match.group(2).split(','))
    
    return list(set(imports))
```

## Data Mapping

### Default Mapping

The GitHub connector maps files to FrameRecords as follows:

```python
def map_to_frame_record(self, github_file):
    """Map GitHub file to FrameRecord."""
    
    # Determine title
    title = github_file.name
    if github_file.path != github_file.name:
        title = f"{github_file.path}"
    
    # Get content
    content = ""
    if hasattr(github_file, 'decoded_content'):
        content = github_file.decoded_content
    
    # Create record
    return FrameRecord.create(
        title=title,
        content=content,
        source_url=github_file.html_url,
        source_type="github",
        source_file=github_file.path,
        author=self.get_file_author(github_file),
        tags=self.generate_tags(github_file),
        custom_metadata={
            "github_owner": self.owner,
            "github_repo": self.repo,
            "github_path": github_file.path,
            "github_sha": github_file.sha,
            "github_size": github_file.size,
            "github_type": github_file.type,
            "github_encoding": github_file.encoding,
            "github_branch": self.branch or "main"
        }
    )
```

### Custom Mapping

```python
class CustomGitHubConnector(GitHubConnector):
    """GitHub connector with custom mapping."""
    
    def map_to_frame_record(self, github_file):
        """Custom mapping for specific needs."""
        
        # Get base mapping
        record = super().map_to_frame_record(github_file)
        
        # Extract front matter from markdown
        if github_file.name.endswith('.md'):
            content = github_file.decoded_content
            if content.startswith('---'):
                import yaml
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        record.metadata.update(frontmatter)
                        record.text_content = parts[2].strip()
                    except:
                        pass
        
        # Add custom categorization
        if github_file.path.startswith('docs/api/'):
            record.metadata['category'] = 'api-reference'
        elif github_file.path.startswith('docs/guides/'):
            record.metadata['category'] = 'guide'
        elif github_file.path.startswith('examples/'):
            record.metadata['category'] = 'example'
        
        # Extract language from code files
        extension = github_file.name.split('.')[-1]
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'go': 'go',
            'rs': 'rust'
        }
        
        if extension in language_map:
            record.metadata['programming_language'] = language_map[extension]
        
        return record
```

## Sync Strategies

### Incremental Sync

```python
def incremental_sync(connector, dataset, last_sync_time):
    """Sync only changed files since last sync."""
    
    # Get commits since last sync
    commits = connector.get_commits(since=last_sync_time)
    
    changed_files = set()
    for commit in commits:
        # Get files changed in commit
        files = connector.get_commit_files(commit.sha)
        for file in files:
            changed_files.add(file.filename)
    
    # Sync only changed files
    records = []
    for filepath in changed_files:
        try:
            file = connector.get_file(filepath)
            record = connector.map_to_frame_record(file)
            
            # Check if exists and update
            existing = dataset.scanner(
                filter=f"custom_metadata.github_path = '{filepath}'"
            ).to_table().to_pylist()
            
            if existing:
                dataset.update_record(existing[0]['uuid'], record)
            else:
                records.append(record)
        
        except Exception as e:
            print(f"Error syncing {filepath}: {e}")
    
    # Add new records
    if records:
        dataset.add_many(records)
    
    return len(changed_files)
```

### Watch Mode

```python
import time
from datetime import datetime, timezone

def watch_repository(connector, dataset, interval=300):
    """Watch repository for changes."""
    
    last_check = datetime.now(timezone.utc)
    
    while True:
        print(f"Checking for changes... ({datetime.now()})")
        
        try:
            # Get recent commits
            commits = connector.get_commits(
                since=last_check.isoformat()
            )
            
            if commits:
                print(f"Found {len(commits)} new commits")
                
                # Process each commit
                for commit in commits:
                    files = connector.get_commit_files(commit.sha)
                    
                    for file in files:
                        # Skip if not matching pattern
                        if not file.filename.endswith(('.md', '.mdx')):
                            continue
                        
                        print(f"  Updating: {file.filename}")
                        
                        # Get file content
                        file_content = connector.get_file(file.filename)
                        record = connector.map_to_frame_record(file_content)
                        
                        # Add commit info
                        record.metadata['custom_metadata']['last_commit'] = {
                            'sha': commit.sha,
                            'message': commit.message,
                            'author': commit.author.login if commit.author else 'unknown',
                            'date': commit.created_at.isoformat()
                        }
                        
                        # Update or add
                        existing = dataset.scanner(
                            filter=f"custom_metadata.github_path = '{file.filename}'"
                        ).to_table().to_pylist()
                        
                        if existing:
                            dataset.update_record(existing[0]['uuid'], record)
                        else:
                            dataset.add(record)
            
            last_check = datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"Error checking repository: {e}")
        
        # Wait before next check
        time.sleep(interval)
```

## Rate Limiting

GitHub API has rate limits. The connector handles this automatically:

```python
class RateLimitedGitHubConnector(GitHubConnector):
    """GitHub connector with rate limit handling."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
    
    def check_rate_limit(self):
        """Check and handle rate limits."""
        if hasattr(self.github, 'get_rate_limit'):
            rate_limit = self.github.get_rate_limit()
            core = rate_limit.core
            
            self.rate_limit_remaining = core.remaining
            self.rate_limit_reset = core.reset
            
            print(f"Rate limit: {core.remaining}/{core.limit} (resets at {core.reset})")
            
            # If close to limit, wait
            if core.remaining < 10:
                wait_time = (core.reset - datetime.now(timezone.utc)).total_seconds()
                if wait_time > 0:
                    print(f"Rate limit nearly exhausted. Waiting {wait_time}s...")
                    time.sleep(wait_time + 1)
    
    def sync_documents(self, **kwargs):
        """Sync with rate limit checking."""
        self.check_rate_limit()
        return super().sync_documents(**kwargs)
```

## Error Handling

### Common Errors

```python
def handle_github_errors(func):
    """Decorator for GitHub error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            
            if "404" in str(e):
                print(f"Repository or file not found: {e}")
            elif "401" in str(e):
                print("Authentication failed. Check your token.")
            elif "403" in str(e):
                if "rate limit" in str(e).lower():
                    print("Rate limit exceeded. Try again later.")
                else:
                    print("Permission denied. Check token scopes.")
            elif "422" in str(e):
                print(f"Invalid request: {e}")
            else:
                print(f"GitHub API error ({error_type}): {e}")
            
            return None
    
    return wrapper

# Use decorator
@handle_github_errors
def safe_sync(connector, **options):
    return connector.sync_documents(**options)
```

## Performance Optimization

### Parallel Downloads

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_sync(connector, file_paths, max_workers=5):
    """Download files in parallel."""
    
    def download_file(path):
        try:
            file = connector.get_file(path)
            record = connector.map_to_frame_record(file)
            return record
        except Exception as e:
            print(f"Error downloading {path}: {e}")
            return None
    
    records = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(download_file, path): path 
            for path in file_paths
        }
        
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                record = future.result()
                if record:
                    records.append(record)
                    print(f"Downloaded: {path}")
            except Exception as e:
                print(f"Failed: {path} - {e}")
    
    return records
```

### Caching

```python
import pickle
from pathlib import Path

class CachedGitHubConnector(GitHubConnector):
    """GitHub connector with local caching."""
    
    def __init__(self, cache_dir=".github_cache", **kwargs):
        super().__init__(**kwargs)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _cache_key(self, path, branch=None):
        """Generate cache key for file."""
        branch = branch or self.branch or "main"
        return f"{self.owner}_{self.repo}_{branch}_{path.replace('/', '_')}"
    
    def get_file(self, path, use_cache=True):
        """Get file with caching."""
        cache_key = self._cache_key(path)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Check cache
        if use_cache and cache_file.exists():
            # Check if cache is fresh (less than 1 hour old)
            if time.time() - cache_file.stat().st_mtime < 3600:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        
        # Fetch from GitHub
        file = super().get_file(path)
        
        # Cache result
        with open(cache_file, 'wb') as f:
            pickle.dump(file, f)
        
        return file
```

## Examples

### Documentation Site Import

```python
def import_documentation_site(dataset):
    """Import complete documentation site."""
    
    connector = GitHubConnector(
        token=os.getenv("GITHUB_TOKEN"),
        owner="vercel",
        repo="next.js"
    )
    
    # Define documentation structure
    doc_sections = [
        {
            'path': 'docs/01-getting-started',
            'collection': 'nextjs-getting-started',
            'tags': ['tutorial', 'beginner']
        },
        {
            'path': 'docs/02-app',
            'collection': 'nextjs-app-router',
            'tags': ['app-router', 'routing']
        },
        {
            'path': 'docs/03-pages',
            'collection': 'nextjs-pages-router',
            'tags': ['pages-router', 'routing']
        }
    ]
    
    for section in doc_sections:
        print(f"Importing {section['path']}...")
        
        documents = connector.sync_documents(
            path=section['path'],
            file_pattern="**/*.mdx",
            include_content=True
        )
        
        records = []
        for doc in documents:
            record = connector.map_to_frame_record(doc)
            
            # Add section metadata
            record.metadata['collection'] = section['collection']
            record.metadata['tags'].extend(section['tags'])
            
            # Extract page metadata from path
            path_parts = doc.path.split('/')
            if len(path_parts) > 2:
                record.metadata['custom_metadata']['section'] = path_parts[1]
                record.metadata['custom_metadata']['subsection'] = path_parts[2] if len(path_parts) > 3 else None
            
            records.append(record)
        
        dataset.add_many(records)
        print(f"  Imported {len(records)} documents")
```

### Code Knowledge Base

```python
def build_code_knowledge_base(dataset, language="python"):
    """Build knowledge base from code repositories."""
    
    # Popular repositories by language
    repos_by_language = {
        'python': [
            ('python', 'cpython', 'Lib'),
            ('django', 'django', 'django'),
            ('pandas-dev', 'pandas', 'pandas'),
            ('numpy', 'numpy', 'numpy')
        ],
        'javascript': [
            ('facebook', 'react', 'packages'),
            ('vuejs', 'vue', 'src'),
            ('nodejs', 'node', 'lib'),
            ('expressjs', 'express', 'lib')
        ]
    }
    
    repos = repos_by_language.get(language, [])
    
    for owner, repo, path in repos:
        print(f"Importing {owner}/{repo}...")
        
        connector = GitHubConnector(
            token=os.getenv("GITHUB_TOKEN"),
            owner=owner,
            repo=repo
        )
        
        try:
            # Import source code
            files = connector.sync_documents(
                path=path,
                file_pattern=f"**/*.{language[:2]}",  # .py, .js, etc
                include_content=True
            )
            
            records = []
            for file in files:
                # Skip test files and examples
                if any(skip in file.path.lower() for skip in ['test', 'example', 'demo']):
                    continue
                
                record = connector.map_to_frame_record(file)
                
                # Add knowledge base metadata
                record.metadata['collection'] = f"{language}-stdlib"
                record.metadata['tags'] = [
                    f"lang:{language}",
                    f"lib:{repo}",
                    "source-code",
                    "reference"
                ]
                
                # Extract module name
                module = file.path.replace('/', '.').replace(f'.{language[:2]}', '')
                record.metadata['custom_metadata']['module'] = module
                
                records.append(record)
            
            dataset.add_many(records)
            print(f"  Imported {len(records)} source files")
            
        except Exception as e:
            print(f"  Error: {e}")
```

## Best Practices

### 1. Token Security

```python
# Use environment variables
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise ValueError("GITHUB_TOKEN environment variable not set")

# For GitHub Apps, use installation tokens
from github import GithubIntegration

integration = GithubIntegration(
    app_id,
    private_key
)
installation = integration.get_installation(owner, repo)
token = installation.get_access_token().token
```

### 2. Efficient Filtering

```python
# Filter at API level, not in post-processing
# Good - filtered by API
documents = connector.sync_documents(
    path="docs",
    file_pattern="**/*.md"
)

# Bad - downloads everything then filters
all_files = connector.sync_documents()
md_files = [f for f in all_files if f.name.endswith('.md')]
```

### 3. Metadata Preservation

```python
def preserve_github_context(record, file, repo_info):
    """Preserve complete GitHub context."""
    
    record.metadata['custom_metadata'].update({
        # Repository context
        'github_repo_full_name': repo_info.full_name,
        'github_repo_description': repo_info.description,
        'github_repo_topics': repo_info.get_topics(),
        'github_repo_language': repo_info.language,
        'github_repo_default_branch': repo_info.default_branch,
        
        # File context
        'github_file_url': file.html_url,
        'github_file_download_url': file.download_url,
        'github_file_api_url': file.url,
        
        # Useful for updates
        'github_last_modified': file.last_modified,
        'github_etag': file.etag
    })
    
    return record
```

## Troubleshooting

### Authentication Issues

```python
# Test authentication
try:
    connector.authenticate()
    user = connector.github.get_user()
    print(f"Authenticated as: {user.login}")
except Exception as e:
    print(f"Authentication failed: {e}")
    print("Check:")
    print("1. Token is valid and not expired")
    print("2. Token has required scopes")
    print("3. Network connectivity")
```

### File Encoding Issues

```python
def safe_decode_content(file):
    """Safely decode file content."""
    if file.encoding == 'base64':
        import base64
        content_bytes = base64.b64decode(file.content)
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                return content_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # Fallback - ignore errors
        return content_bytes.decode('utf-8', errors='ignore')
    
    return file.content
```

## Next Steps

- Explore other connectors:
  - [Linear Connector](linear.md) for issue tracking
  - [Notion Connector](notion.md) for knowledge bases
  - [Slack Connector](slack.md) for conversations
- Learn about [Custom Connectors](custom.md)
- See [Cookbook Examples](../cookbook/github-documentation.md)
- Check the [API Reference](../api/connectors.md#github)