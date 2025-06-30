# GitHub Knowledge Base

Build a comprehensive knowledge base from GitHub repositories that indexes code, documentation, issues, pull requests, and discussions to create a searchable development knowledge repository.

## Problem Statement

Development teams need to quickly find information across their GitHub repositories - from code examples and documentation to resolved issues and design decisions in pull requests. A unified knowledge base makes this institutional knowledge discoverable.

## Solution Overview

We'll build a GitHub knowledge base that:
1. Indexes multiple repositories comprehensively
2. Extracts and preserves code context
3. Links related issues, PRs, and code
4. Provides code-aware search
5. Tracks knowledge evolution over time

## Complete Code

```python
import os
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import re
import ast
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata
)
from contextframe.connectors import GitHubConnector

class GitHubKnowledgeBase:
    """Comprehensive GitHub repository knowledge base."""
    
    def __init__(self, dataset_path: str = "github_kb.lance"):
        """Initialize knowledge base."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        self.connector = None
        self.indexed_repos = set()
        
    def setup(self, github_token: str):
        """Setup GitHub connector."""
        self.connector = GitHubConnector(token=github_token)
        
    def index_repository(self, owner: str, repo: str, 
                        include_code: bool = True,
                        include_issues: bool = True,
                        include_prs: bool = True,
                        include_discussions: bool = True,
                        include_wiki: bool = True):
        """Index entire repository."""
        repo_key = f"{owner}/{repo}"
        print(f"Indexing repository: {repo_key}")
        
        # Create repository header
        repo_info = self.connector.get_repository(owner, repo)
        repo_header = self._create_repo_header(repo_info)
        self.dataset.add(repo_header)
        
        # Index components
        if include_code:
            self._index_code(owner, repo, repo_header.unique_id)
            
        if include_issues:
            self._index_issues(owner, repo, repo_header.unique_id)
            
        if include_prs:
            self._index_pull_requests(owner, repo, repo_header.unique_id)
            
        if include_discussions:
            self._index_discussions(owner, repo, repo_header.unique_id)
            
        if include_wiki:
            self._index_wiki(owner, repo, repo_header.unique_id)
        
        # Mark as indexed
        self.indexed_repos.add(repo_key)
        
        # Link related content
        self._create_cross_references(owner, repo)
        
        print(f"Completed indexing {repo_key}")
        
    def _create_repo_header(self, repo_info: Dict[str, Any]) -> FrameRecord:
        """Create repository header record."""
        return FrameRecord(
            text_content=f"{repo_info['full_name']}\n\n{repo_info.get('description', '')}",
            metadata=create_metadata(
                title=repo_info['full_name'],
                source="github",
                repository=repo_info['full_name'],
                type="repository",
                description=repo_info.get('description'),
                topics=repo_info.get('topics', []),
                language=repo_info.get('language'),
                stars=repo_info.get('stargazers_count', 0),
                forks=repo_info.get('forks_count', 0),
                created_at=repo_info.get('created_at'),
                updated_at=repo_info.get('updated_at'),
                default_branch=repo_info.get('default_branch', 'main'),
                url=repo_info.get('html_url')
            ),
            record_type="collection_header",
            unique_id=f"repo_{repo_info['full_name'].replace('/', '_')}"
        )
    
    def _index_code(self, owner: str, repo: str, repo_header_id: str):
        """Index repository code files."""
        print(f"  Indexing code files...")
        
        # Get file tree
        files = self.connector.sync_files(
            owner=owner,
            repo=repo,
            path_patterns=["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs", "*.md", "*.yml", "*.yaml"]
        )
        
        for file_data in files:
            if file_data.get('type') != 'file':
                continue
                
            # Create file record
            record = self._create_code_record(file_data, owner, repo, repo_header_id)
            if record:
                self.dataset.add(record, generate_embedding=True)
        
        print(f"    Indexed {len(files)} code files")
    
    def _create_code_record(self, file_data: Dict[str, Any], 
                          owner: str, repo: str, repo_header_id: str) -> Optional[FrameRecord]:
        """Create record for code file."""
        content = file_data.get('content', '')
        if not content:
            return None
        
        file_path = file_data['path']
        file_ext = Path(file_path).suffix
        
        # Extract code intelligence
        code_info = self._analyze_code(content, file_ext)
        
        # Create metadata
        metadata = create_metadata(
            title=file_path,
            source="github",
            repository=f"{owner}/{repo}",
            type="code_file",
            file_path=file_path,
            file_extension=file_ext,
            file_size=len(content),
            sha=file_data.get('sha'),
            url=file_data.get('html_url'),
            **code_info
        )
        
        # Add relationship to repository
        metadata = add_relationship_to_metadata(
            metadata,
            relationship_type="member_of",
            target_id=repo_header_id
        )
        
        # Format content with syntax highlighting
        formatted_content = self._format_code(content, file_ext, file_path)
        
        return FrameRecord(
            text_content=formatted_content,
            metadata=metadata,
            unique_id=f"code_{owner}_{repo}_{file_path.replace('/', '_')}",
            context={
                "code_analysis": code_info,
                "raw_content": content
            }
        )
    
    def _analyze_code(self, content: str, file_ext: str) -> Dict[str, Any]:
        """Analyze code for structure and metadata."""
        info = {
            "line_count": len(content.splitlines()),
            "char_count": len(content)
        }
        
        # Language-specific analysis
        if file_ext == '.py':
            info.update(self._analyze_python(content))
        elif file_ext in ['.js', '.ts']:
            info.update(self._analyze_javascript(content))
        elif file_ext in ['.md', '.markdown']:
            info.update(self._analyze_markdown(content))
            
        # Extract TODOs and FIXMEs
        todos = re.findall(r'(?:TODO|FIXME|HACK|NOTE):\s*(.+)', content)
        if todos:
            info['todos'] = todos
            
        # Extract imports/dependencies
        if file_ext == '.py':
            imports = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+(.+)$', content, re.MULTILINE)
            info['imports'] = [imp for imp in imports if imp[0] or imp[1]]
            
        return info
    
    def _analyze_python(self, content: str) -> Dict[str, Any]:
        """Analyze Python code."""
        info = {}
        
        try:
            tree = ast.parse(content)
            
            # Extract classes and functions
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node)
                    })
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node),
                        'args': [arg.arg for arg in node.args.args]
                    })
            
            info['classes'] = classes
            info['functions'] = functions
            info['has_main'] = any(
                isinstance(node, ast.If) and 
                isinstance(node.test, ast.Compare) and
                isinstance(node.test.left, ast.Name) and
                node.test.left.id == '__name__'
                for node in ast.walk(tree)
            )
            
        except SyntaxError:
            info['parse_error'] = True
            
        return info
    
    def _analyze_javascript(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code."""
        info = {}
        
        # Extract functions
        functions = re.findall(r'(?:function|const|let|var)\s+(\w+)\s*[=\(]', content)
        info['functions'] = list(set(functions))
        
        # Extract classes
        classes = re.findall(r'class\s+(\w+)', content)
        info['classes'] = classes
        
        # Check for React components
        if re.search(r'import\s+.*React|from\s+[\'"]react[\'"]', content):
            info['is_react'] = True
            components = re.findall(r'(?:function|const)\s+([A-Z]\w+)\s*[=\(]', content)
            info['components'] = components
            
        return info
    
    def _analyze_markdown(self, content: str) -> Dict[str, Any]:
        """Analyze Markdown content."""
        info = {}
        
        # Extract headers
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        info['headers'] = [{'level': len(h[0]), 'text': h[1]} for h in headers]
        
        # Extract links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        info['links'] = [{'text': l[0], 'url': l[1]} for l in links]
        
        # Check for code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        info['code_blocks'] = [{'lang': cb[0] or 'text', 'lines': len(cb[1].splitlines())} for cb in code_blocks]
        
        return info
    
    def _format_code(self, content: str, file_ext: str, file_path: str) -> str:
        """Format code with context."""
        header = f"File: {file_path}\n{'=' * 50}\n\n"
        
        # For markdown, render to text
        if file_ext in ['.md', '.markdown']:
            # Simple markdown to text
            formatted = re.sub(r'#{1,6}\s+', '', content)  # Remove headers
            formatted = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', formatted)  # Simplify links
            return header + formatted
        else:
            return header + content
    
    def _index_issues(self, owner: str, repo: str, repo_header_id: str):
        """Index repository issues."""
        print(f"  Indexing issues...")
        
        issues = self.connector.sync_issues(
            owner=owner,
            repo=repo,
            state="all",
            include_comments=True
        )
        
        issue_records = []
        for issue in issues:
            record = self._create_issue_record(issue, owner, repo, repo_header_id)
            issue_records.append(record)
            
        self.dataset.add_batch(issue_records, generate_embeddings=True)
        print(f"    Indexed {len(issues)} issues")
    
    def _create_issue_record(self, issue: Dict[str, Any], 
                           owner: str, repo: str, repo_header_id: str) -> FrameRecord:
        """Create record for issue."""
        # Combine issue body and comments
        content_parts = [
            f"Issue #{issue['number']}: {issue['title']}",
            "",
            issue.get('body', '') or "No description provided.",
            ""
        ]
        
        # Add comments
        if 'comments_data' in issue:
            content_parts.append("Comments:")
            for comment in issue['comments_data']:
                content_parts.extend([
                    f"\n--- {comment['user']['login']} at {comment['created_at']} ---",
                    comment['body'],
                    ""
                ])
        
        content = "\n".join(content_parts)
        
        # Create metadata
        metadata = create_metadata(
            title=f"Issue #{issue['number']}: {issue['title']}",
            source="github",
            repository=f"{owner}/{repo}",
            type="issue",
            issue_number=issue['number'],
            state=issue['state'],
            author=issue['user']['login'],
            created_at=issue['created_at'],
            updated_at=issue['updated_at'],
            closed_at=issue.get('closed_at'),
            labels=[label['name'] for label in issue.get('labels', [])],
            assignees=[user['login'] for user in issue.get('assignees', [])],
            comments_count=issue.get('comments', 0),
            url=issue['html_url']
        )
        
        # Add relationships
        metadata = add_relationship_to_metadata(
            metadata,
            relationship_type="member_of",
            target_id=repo_header_id
        )
        
        # Link to pull request if exists
        if issue.get('pull_request'):
            metadata = add_relationship_to_metadata(
                metadata,
                relationship_type="related",
                target_id=f"pr_{owner}_{repo}_{issue['number']}"
            )
        
        return FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=f"issue_{owner}_{repo}_{issue['number']}",
            context={
                "reactions": issue.get('reactions', {}),
                "timeline": issue.get('timeline_url')
            }
        )
    
    def _index_pull_requests(self, owner: str, repo: str, repo_header_id: str):
        """Index pull requests."""
        print(f"  Indexing pull requests...")
        
        prs = self.connector.sync_pull_requests(
            owner=owner,
            repo=repo,
            state="all",
            include_comments=True,
            include_reviews=True,
            include_commits=True
        )
        
        pr_records = []
        for pr in prs:
            record = self._create_pr_record(pr, owner, repo, repo_header_id)
            pr_records.append(record)
            
        self.dataset.add_batch(pr_records, generate_embeddings=True)
        print(f"    Indexed {len(prs)} pull requests")
    
    def _create_pr_record(self, pr: Dict[str, Any], 
                         owner: str, repo: str, repo_header_id: str) -> FrameRecord:
        """Create record for pull request."""
        # Build comprehensive content
        content_parts = [
            f"Pull Request #{pr['number']}: {pr['title']}",
            "",
            "Description:",
            pr.get('body', '') or "No description provided.",
            ""
        ]
        
        # Add commits
        if 'commits_data' in pr:
            content_parts.append(f"Commits ({len(pr['commits_data'])}):")
            for commit in pr['commits_data'][:10]:  # First 10 commits
                content_parts.append(f"  - {commit['commit']['message'].splitlines()[0]}")
            content_parts.append("")
        
        # Add reviews
        if 'reviews_data' in pr:
            content_parts.append("Reviews:")
            for review in pr['reviews_data']:
                content_parts.extend([
                    f"\n--- {review['user']['login']} - {review['state']} ---",
                    review.get('body', ''),
                    ""
                ])
        
        # Add diff statistics
        if pr.get('additions') or pr.get('deletions'):
            content_parts.extend([
                "Changes:",
                f"  +{pr.get('additions', 0)} additions",
                f"  -{pr.get('deletions', 0)} deletions",
                f"  {pr.get('changed_files', 0)} files changed",
                ""
            ])
        
        content = "\n".join(content_parts)
        
        # Create metadata
        metadata = create_metadata(
            title=f"PR #{pr['number']}: {pr['title']}",
            source="github",
            repository=f"{owner}/{repo}",
            type="pull_request",
            pr_number=pr['number'],
            state=pr['state'],
            author=pr['user']['login'],
            created_at=pr['created_at'],
            updated_at=pr['updated_at'],
            merged_at=pr.get('merged_at'),
            closed_at=pr.get('closed_at'),
            base_branch=pr['base']['ref'],
            head_branch=pr['head']['ref'],
            labels=[label['name'] for label in pr.get('labels', [])],
            reviewers=[r['login'] for r in pr.get('requested_reviewers', [])],
            additions=pr.get('additions', 0),
            deletions=pr.get('deletions', 0),
            changed_files=pr.get('changed_files', 0),
            url=pr['html_url']
        )
        
        # Add relationships
        metadata = add_relationship_to_metadata(
            metadata,
            relationship_type="member_of",
            target_id=repo_header_id
        )
        
        # Link to related issue
        if pr.get('issue_url'):
            issue_number = pr['issue_url'].split('/')[-1]
            metadata = add_relationship_to_metadata(
                metadata,
                relationship_type="related",
                target_id=f"issue_{owner}_{repo}_{issue_number}"
            )
        
        return FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=f"pr_{owner}_{repo}_{pr['number']}",
            context={
                "commits": len(pr.get('commits_data', [])),
                "reviews": len(pr.get('reviews_data', [])),
                "files_changed": pr.get('changed_files', 0)
            }
        )
    
    def _index_discussions(self, owner: str, repo: str, repo_header_id: str):
        """Index GitHub discussions."""
        print(f"  Indexing discussions...")
        
        try:
            discussions = self.connector.sync_discussions(owner=owner, repo=repo)
            
            discussion_records = []
            for discussion in discussions:
                record = self._create_discussion_record(discussion, owner, repo, repo_header_id)
                discussion_records.append(record)
                
            self.dataset.add_batch(discussion_records, generate_embeddings=True)
            print(f"    Indexed {len(discussions)} discussions")
        except Exception as e:
            print(f"    Skipping discussions: {e}")
    
    def _index_wiki(self, owner: str, repo: str, repo_header_id: str):
        """Index repository wiki."""
        print(f"  Indexing wiki...")
        
        try:
            wiki_pages = self.connector.sync_wiki(owner=owner, repo=repo)
            
            wiki_records = []
            for page in wiki_pages:
                record = self._create_wiki_record(page, owner, repo, repo_header_id)
                wiki_records.append(record)
                
            self.dataset.add_batch(wiki_records, generate_embeddings=True)
            print(f"    Indexed {len(wiki_pages)} wiki pages")
        except Exception as e:
            print(f"    Skipping wiki: {e}")
    
    def _create_cross_references(self, owner: str, repo: str):
        """Create cross-references between related content."""
        print(f"  Creating cross-references...")
        
        # Find issue references in code
        code_records = self.dataset.sql_filter(
            f"metadata.repository = '{owner}/{repo}' AND metadata.type = 'code_file'"
        )
        
        for code_record in code_records:
            # Search for issue references
            issue_refs = re.findall(r'#(\d+)', code_record.text_content)
            
            for issue_num in set(issue_refs):
                # Find corresponding issue
                issue_records = self.dataset.sql_filter(
                    f"metadata.repository = '{owner}/{repo}' AND "
                    f"metadata.type = 'issue' AND metadata.issue_number = {issue_num}",
                    limit=1
                )
                
                if issue_records:
                    # Add relationship
                    code_record.metadata = add_relationship_to_metadata(
                        code_record.metadata,
                        relationship_type="references",
                        target_id=issue_records[0].unique_id
                    )
                    self.dataset.update(code_record.unique_id, metadata=code_record.metadata)
    
    def search_code(self, query: str, language: Optional[str] = None, 
                   repo: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for code examples."""
        filters = ["metadata.type = 'code_file'"]
        
        if language:
            filters.append(f"metadata.language = '{language}'")
        
        if repo:
            filters.append(f"metadata.repository = '{repo}'")
        
        filter_str = " AND ".join(filters)
        
        results = self.dataset.search(
            query=query,
            filter=filter_str,
            limit=limit
        )
        
        # Format results with code highlighting
        formatted_results = []
        for result in results:
            formatted_results.append({
                'file_path': result.metadata['file_path'],
                'repository': result.metadata['repository'],
                'url': result.metadata.get('url'),
                'score': result.score,
                'snippet': self._extract_code_snippet(
                    result.context.get('raw_content', result.text_content),
                    query
                ),
                'language': result.metadata.get('language', 
                           result.metadata['file_extension'].lstrip('.'))
            })
        
        return formatted_results
    
    def _extract_code_snippet(self, content: str, query: str, 
                             context_lines: int = 5) -> str:
        """Extract relevant code snippet around query match."""
        lines = content.splitlines()
        query_lower = query.lower()
        
        # Find matching line
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                
                snippet_lines = []
                for j in range(start, end):
                    prefix = ">>> " if j == i else "    "
                    snippet_lines.append(f"{prefix}{lines[j]}")
                
                return "\n".join(snippet_lines)
        
        # No match found, return beginning
        return "\n".join(lines[:context_lines * 2])
    
    def find_similar_issues(self, issue_description: str, 
                          repo: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Find similar issues to avoid duplicates."""
        filters = ["metadata.type = 'issue'"]
        
        if repo:
            filters.append(f"metadata.repository = '{repo}'")
        
        filter_str = " AND ".join(filters)
        
        results = self.dataset.search(
            query=issue_description,
            filter=filter_str,
            limit=limit
        )
        
        return [{
            'number': r.metadata['issue_number'],
            'title': r.metadata['title'],
            'state': r.metadata['state'],
            'repository': r.metadata['repository'],
            'url': r.metadata['url'],
            'similarity': r.score,
            'labels': r.metadata.get('labels', [])
        } for r in results]
    
    def get_code_examples(self, function_name: str, 
                         language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get code examples for a function or pattern."""
        # Search in function definitions
        filter_parts = ["metadata.type = 'code_file'"]
        if language:
            filter_parts.append(f"metadata.language = '{language}'")
        
        results = self.dataset.search(
            query=function_name,
            filter=" AND ".join(filter_parts),
            limit=20
        )
        
        examples = []
        for result in results:
            # Check if function is defined in this file
            code_info = result.context.get('code_analysis', {})
            functions = code_info.get('functions', [])
            
            for func in functions:
                if function_name.lower() in func.get('name', '').lower():
                    examples.append({
                        'file': result.metadata['file_path'],
                        'repository': result.metadata['repository'],
                        'function': func['name'],
                        'line': func.get('line'),
                        'docstring': func.get('docstring'),
                        'url': result.metadata.get('url')
                    })
        
        return examples
    
    def analyze_repository(self, repo: str) -> Dict[str, Any]:
        """Get repository analytics."""
        # Get all records for repo
        records = self.dataset.sql_filter(
            f"metadata.repository = '{repo}'"
        )
        
        stats = {
            'total_records': len(records),
            'code_files': 0,
            'issues': {'open': 0, 'closed': 0},
            'pull_requests': {'open': 0, 'closed': 0, 'merged': 0},
            'languages': {},
            'contributors': set(),
            'labels': {},
            'file_types': {}
        }
        
        for record in records:
            if record.metadata['type'] == 'code_file':
                stats['code_files'] += 1
                ext = record.metadata.get('file_extension', 'unknown')
                stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                
            elif record.metadata['type'] == 'issue':
                state = record.metadata['state']
                stats['issues'][state] = stats['issues'].get(state, 0) + 1
                
                for label in record.metadata.get('labels', []):
                    stats['labels'][label] = stats['labels'].get(label, 0) + 1
                    
            elif record.metadata['type'] == 'pull_request':
                if record.metadata.get('merged_at'):
                    stats['pull_requests']['merged'] += 1
                elif record.metadata['state'] == 'open':
                    stats['pull_requests']['open'] += 1
                else:
                    stats['pull_requests']['closed'] += 1
            
            # Track contributors
            author = record.metadata.get('author')
            if author:
                stats['contributors'].add(author)
        
        stats['contributors'] = len(stats['contributors'])
        
        return stats

# Example usage
if __name__ == "__main__":
    # Initialize knowledge base
    kb = GitHubKnowledgeBase("github_knowledge.lance")
    kb.setup(github_token=os.getenv("GITHUB_TOKEN"))
    
    # Index repositories
    repositories = [
        ("facebook", "react"),
        ("microsoft", "vscode"),
        ("myorg", "internal-tools")
    ]
    
    for owner, repo in repositories:
        kb.index_repository(
            owner=owner,
            repo=repo,
            include_code=True,
            include_issues=True,
            include_prs=True
        )
    
    # Search for code examples
    react_hooks = kb.search_code(
        "useState useEffect",
        language="javascript",
        repo="facebook/react"
    )
    
    print("React Hook Examples:")
    for example in react_hooks[:5]:
        print(f"- {example['file_path']} (score: {example['score']:.2f})")
        print(f"  {example['snippet']}")
        print()
    
    # Find similar issues
    similar = kb.find_similar_issues(
        "Component not re-rendering when props change",
        repo="facebook/react"
    )
    
    print("\nSimilar Issues:")
    for issue in similar[:5]:
        print(f"- #{issue['number']}: {issue['title']} ({issue['state']})")
        print(f"  Similarity: {issue['similarity']:.2f}")
    
    # Get function examples
    examples = kb.get_code_examples("useEffect", language="javascript")
    
    print("\nuseEffect Examples:")
    for ex in examples[:5]:
        print(f"- {ex['repository']}: {ex['file']}")
        if ex.get('docstring'):
            print(f"  {ex['docstring']}")
    
    # Repository analytics
    stats = kb.analyze_repository("facebook/react")
    print(f"\nRepository Analytics for facebook/react:")
    print(f"- Total records: {stats['total_records']}")
    print(f"- Code files: {stats['code_files']}")
    print(f"- Open issues: {stats['issues']['open']}")
    print(f"- Contributors: {stats['contributors']}")
```

## Key Concepts

### 1. Comprehensive Indexing
- Code files with syntax analysis
- Issues with comments and timeline
- Pull requests with reviews and commits
- Discussions and wiki pages
- Cross-references between content

### 2. Code Intelligence
- Language-specific parsing (Python AST, regex for others)
- Function and class extraction
- Import/dependency analysis
- TODO/FIXME tracking
- Code structure metadata

### 3. Relationship Mapping
- Repository hierarchy
- Issue-PR relationships
- Code-issue references
- File dependencies
- Contributor networks

### 4. Specialized Search
- Code-aware search with snippets
- Similar issue detection
- Function example finding
- Repository analytics
- Language-specific filtering

### 5. Knowledge Preservation
- Historical issue resolutions
- Design decisions in PRs
- Code evolution tracking
- Documentation versioning

## Extensions

### 1. Code Navigation
```python
class CodeNavigator:
    """Navigate code relationships."""
    
    def find_callers(self, function_name: str, repo: str) -> List[Dict[str, Any]]:
        """Find all files that call a function."""
        # Search for function calls
        pattern = f"{function_name}\\("
        
        results = self.dataset.search(
            query=pattern,
            filter=f"metadata.repository = '{repo}' AND metadata.type = 'code_file'"
        )
        
        callers = []
        for result in results:
            # Verify it's a function call
            if re.search(rf'\b{function_name}\s*\(', result.text_content):
                callers.append({
                    'file': result.metadata['file_path'],
                    'repository': repo,
                    'url': result.metadata.get('url')
                })
        
        return callers
    
    def get_import_graph(self, repo: str) -> Dict[str, List[str]]:
        """Build import dependency graph."""
        graph = {}
        
        code_files = self.dataset.sql_filter(
            f"metadata.repository = '{repo}' AND metadata.type = 'code_file'"
        )
        
        for file in code_files:
            imports = file.context.get('code_analysis', {}).get('imports', [])
            graph[file.metadata['file_path']] = imports
        
        return graph
```

### 2. PR Impact Analysis
```python
def analyze_pr_impact(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
    """Analyze the impact of a pull request."""
    # Get PR record
    pr_records = self.dataset.sql_filter(
        f"metadata.repository = '{owner}/{repo}' AND "
        f"metadata.type = 'pull_request' AND metadata.pr_number = {pr_number}",
        limit=1
    )
    
    if not pr_records:
        return {}
    
    pr = pr_records[0]
    
    # Get changed files from PR
    changed_files = pr.context.get('files_changed', 0)
    
    # Find related issues
    related_issues = []
    for rel in pr.metadata.get('relationships', []):
        if rel['relationship_type'] == 'related' and 'issue' in rel['target_id']:
            issue = self.dataset.get(rel['target_id'])
            if issue:
                related_issues.append(issue)
    
    # Calculate impact metrics
    return {
        'pr_number': pr_number,
        'files_changed': changed_files,
        'lines_added': pr.metadata.get('additions', 0),
        'lines_removed': pr.metadata.get('deletions', 0),
        'related_issues': len(related_issues),
        'issue_titles': [i.metadata['title'] for i in related_issues],
        'review_count': len(pr.context.get('reviews', [])),
        'commit_count': pr.context.get('commits', 0)
    }
```

### 3. Knowledge Graph
```python
import networkx as nx

def build_knowledge_graph(self, repo: str) -> nx.DiGraph:
    """Build knowledge graph for repository."""
    G = nx.DiGraph()
    
    # Get all records
    records = self.dataset.sql_filter(
        f"metadata.repository = '{repo}'"
    )
    
    # Add nodes
    for record in records:
        G.add_node(
            record.unique_id,
            type=record.metadata['type'],
            title=record.metadata.get('title', ''),
            url=record.metadata.get('url')
        )
    
    # Add edges from relationships
    for record in records:
        for rel in record.metadata.get('relationships', []):
            G.add_edge(
                record.unique_id,
                rel['target_id'],
                relationship=rel['relationship_type']
            )
    
    return G

def find_related_content(self, node_id: str, max_depth: int = 2) -> List[str]:
    """Find related content using graph traversal."""
    G = self.build_knowledge_graph()
    
    related = set()
    
    # BFS to find related nodes
    from collections import deque
    queue = deque([(node_id, 0)])
    visited = set()
    
    while queue:
        current, depth = queue.popleft()
        if current in visited or depth > max_depth:
            continue
            
        visited.add(current)
        related.add(current)
        
        # Add neighbors
        for neighbor in G.neighbors(current):
            queue.append((neighbor, depth + 1))
    
    return list(related)
```

### 4. Automated Documentation
```python
def generate_api_docs(self, repo: str, output_path: str):
    """Generate API documentation from code."""
    # Get all Python files
    python_files = self.dataset.sql_filter(
        f"metadata.repository = '{repo}' AND "
        f"metadata.type = 'code_file' AND "
        f"metadata.file_extension = '.py'"
    )
    
    api_docs = []
    
    for file in python_files:
        code_info = file.context.get('code_analysis', {})
        
        # Document classes
        for cls in code_info.get('classes', []):
            api_docs.append({
                'type': 'class',
                'name': cls['name'],
                'file': file.metadata['file_path'],
                'line': cls['line'],
                'docstring': cls.get('docstring', ''),
                'url': f"{file.metadata.get('url')}#L{cls['line']}"
            })
        
        # Document functions
        for func in code_info.get('functions', []):
            api_docs.append({
                'type': 'function',
                'name': func['name'],
                'file': file.metadata['file_path'],
                'line': func['line'],
                'args': func.get('args', []),
                'docstring': func.get('docstring', ''),
                'url': f"{file.metadata.get('url')}#L{func['line']}"
            })
    
    # Generate markdown
    with open(output_path, 'w') as f:
        f.write(f"# API Documentation for {repo}\n\n")
        
        # Group by file
        from itertools import groupby
        api_docs.sort(key=lambda x: x['file'])
        
        for file, items in groupby(api_docs, key=lambda x: x['file']):
            f.write(f"\n## {file}\n\n")
            
            for item in items:
                if item['type'] == 'class':
                    f.write(f"### class {item['name']}\n")
                else:
                    args = ', '.join(item['args'])
                    f.write(f"### {item['name']}({args})\n")
                
                if item['docstring']:
                    f.write(f"\n{item['docstring']}\n")
                
                f.write(f"\n[View source]({item['url']})\n\n")
```

### 5. Code Quality Metrics
```python
def calculate_code_metrics(self, repo: str) -> Dict[str, Any]:
    """Calculate code quality metrics."""
    metrics = {
        'total_lines': 0,
        'comment_lines': 0,
        'todo_count': 0,
        'function_count': 0,
        'class_count': 0,
        'avg_function_length': 0,
        'files_with_todos': []
    }
    
    code_files = self.dataset.sql_filter(
        f"metadata.repository = '{repo}' AND metadata.type = 'code_file'"
    )
    
    function_lengths = []
    
    for file in code_files:
        metrics['total_lines'] += file.metadata.get('line_count', 0)
        
        code_info = file.context.get('code_analysis', {})
        
        # Count TODOs
        todos = code_info.get('todos', [])
        if todos:
            metrics['todo_count'] += len(todos)
            metrics['files_with_todos'].append({
                'file': file.metadata['file_path'],
                'count': len(todos),
                'todos': todos
            })
        
        # Count functions and classes
        functions = code_info.get('functions', [])
        metrics['function_count'] += len(functions)
        
        classes = code_info.get('classes', [])
        metrics['class_count'] += len(classes)
    
    return metrics
```

## Best Practices

1. **Incremental Updates**: Index only changed content
2. **Rate Limiting**: Respect GitHub API limits
3. **Batch Processing**: Use batch operations for efficiency
4. **Cross-References**: Build rich relationship networks
5. **Code Analysis**: Extract meaningful code metadata
6. **Search Optimization**: Create appropriate indexes
7. **Privacy**: Respect repository access controls

## See Also

- [Multi-Source Search](multi-source-search.md) - Searching across sources
- [RAG System](rag-system.md) - Q&A on repository knowledge
- [API Documentation Management](api-docs.md) - Auto-generating docs
- [GitHub Connector](../integration/github.md) - Connector details