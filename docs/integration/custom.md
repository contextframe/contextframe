# Custom Connectors

Build custom connectors to integrate any data source with ContextFrame. This guide covers the connector interface, implementation patterns, and best practices for creating production-ready connectors.

## Overview

Custom connectors enable you to:
- Integrate proprietary or internal systems
- Add support for new platforms
- Implement custom authentication flows
- Handle specialized data formats
- Create domain-specific mappings
- Build composite connectors
- Add custom enrichment logic

## Connector Interface

All connectors implement the `BaseConnector` interface:

```python
from contextframe.connectors.base import BaseConnector
from contextframe import FrameRecord
from typing import List, Dict, Any, Optional

class CustomConnector(BaseConnector):
    """Custom connector for YourPlatform."""
    
    def __init__(self, **kwargs):
        """Initialize connector with configuration."""
        super().__init__()
        # Your initialization code
    
    def authenticate(self) -> bool:
        """Authenticate with the service."""
        # Implementation required
        pass
    
    def sync_documents(self, **kwargs) -> List[Dict[str, Any]]:
        """Sync documents from the service."""
        # Implementation required
        pass
    
    def map_to_frame_record(self, item: Dict[str, Any]) -> FrameRecord:
        """Convert service data to FrameRecord."""
        # Implementation required
        pass
```

## Basic Implementation

### Simple File Connector

```python
from contextframe.connectors.base import BaseConnector
from contextframe import FrameRecord
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Any

class JSONFileConnector(BaseConnector):
    """Connector for JSON files in a directory."""
    
    def __init__(self, directory: str):
        super().__init__()
        self.directory = Path(directory)
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Verify directory access."""
        if not self.directory.exists():
            raise ValueError(f"Directory not found: {self.directory}")
        if not self.directory.is_dir():
            raise ValueError(f"Not a directory: {self.directory}")
        self.authenticated = True
        return True
    
    def sync_documents(self, pattern: str = "*.json") -> List[Dict[str, Any]]:
        """Load all JSON files matching pattern."""
        if not self.authenticated:
            raise RuntimeError("Not authenticated")
        
        documents = []
        for json_file in self.directory.glob(pattern):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Add file metadata
                data['_file_path'] = str(json_file)
                data['_file_name'] = json_file.name
                data['_modified_at'] = datetime.fromtimestamp(
                    json_file.stat().st_mtime
                ).isoformat()
                
                documents.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue
        
        return documents
    
    def map_to_frame_record(self, item: Dict[str, Any]) -> FrameRecord:
        """Convert JSON data to FrameRecord."""
        # Extract text content
        text_content = item.get('content', '')
        if not text_content:
            # Try common field names
            for field in ['text', 'body', 'description', 'message']:
                if field in item:
                    text_content = str(item[field])
                    break
        
        # Build metadata
        metadata = {
            'source': 'json_file',
            'file_path': item.get('_file_path'),
            'file_name': item.get('_file_name'),
            'modified_at': item.get('_modified_at'),
        }
        
        # Add custom fields
        for key, value in item.items():
            if not key.startswith('_') and key not in ['content', 'text']:
                metadata[key] = value
        
        # Create FrameRecord
        return FrameRecord(
            text_content=text_content,
            metadata=metadata,
            record_type='document',
            unique_id=f"json_file:{item['_file_path']}",
            timestamp=item.get('_modified_at', datetime.now().isoformat())
        )
```

### API-Based Connector

```python
import requests
from typing import Optional
from urllib.parse import urljoin

class APIConnector(BaseConnector):
    """Connector for REST API endpoints."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Verify API access."""
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Test authentication endpoint
        response = self.session.get(
            urljoin(self.base_url, '/api/v1/me'),
            headers=headers
        )
        
        if response.status_code == 200:
            self.session.headers.update(headers)
            self.authenticated = True
            return True
        else:
            raise ValueError(f"Authentication failed: {response.status_code}")
    
    def sync_documents(self, 
                      endpoint: str = '/api/v1/documents',
                      params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch documents from API."""
        if not self.authenticated:
            raise RuntimeError("Not authenticated")
        
        documents = []
        url = urljoin(self.base_url, endpoint)
        
        # Handle pagination
        page = 1
        while True:
            paginated_params = {**(params or {}), 'page': page, 'limit': 100}
            response = self.session.get(url, params=paginated_params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', data.get('data', []))
            
            if not items:
                break
                
            documents.extend(items)
            
            # Check for more pages
            if not data.get('has_more', len(items) == 100):
                break
            
            page += 1
        
        return documents
    
    def map_to_frame_record(self, item: Dict[str, Any]) -> FrameRecord:
        """Convert API response to FrameRecord."""
        return FrameRecord(
            text_content=item.get('content', ''),
            metadata={
                'source': 'api',
                'api_id': item.get('id'),
                'api_url': item.get('url'),
                'created_at': item.get('created_at'),
                'updated_at': item.get('updated_at'),
                'author': item.get('author', {}).get('name'),
                **{k: v for k, v in item.items() 
                   if k not in ['content', 'id', 'url']}
            },
            record_type='document',
            unique_id=f"api:{item.get('id')}",
            timestamp=item.get('updated_at', datetime.now().isoformat())
        )
```

## Advanced Features

### Incremental Sync

```python
class IncrementalConnector(BaseConnector):
    """Connector with incremental sync support."""
    
    def __init__(self, state_file: Optional[str] = None):
        super().__init__()
        self.state_file = state_file
        self.last_sync = None
        self._load_state()
    
    def _load_state(self):
        """Load sync state from file."""
        if self.state_file and Path(self.state_file).exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.last_sync = state.get('last_sync')
    
    def _save_state(self):
        """Save sync state to file."""
        if self.state_file:
            state = {
                'last_sync': datetime.now().isoformat(),
                'stats': self.get_stats()
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
    
    def sync_documents(self, full_sync: bool = False) -> List[Dict[str, Any]]:
        """Sync with incremental support."""
        if full_sync or not self.last_sync:
            documents = self._full_sync()
        else:
            documents = self._incremental_sync(self.last_sync)
        
        self._save_state()
        return documents
    
    def _full_sync(self) -> List[Dict[str, Any]]:
        """Perform full synchronization."""
        # Implementation specific to your data source
        pass
    
    def _incremental_sync(self, since: str) -> List[Dict[str, Any]]:
        """Sync only changes since last sync."""
        # Implementation specific to your data source
        pass
```

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterator
import itertools

class BatchConnector(BaseConnector):
    """Connector with batch processing support."""
    
    def __init__(self, batch_size: int = 100, max_workers: int = 4):
        super().__init__()
        self.batch_size = batch_size
        self.max_workers = max_workers
    
    def sync_documents(self, total_items: int) -> List[Dict[str, Any]]:
        """Sync documents in batches."""
        documents = []
        
        # Create batch ranges
        batches = []
        for i in range(0, total_items, self.batch_size):
            batches.append((i, min(i + self.batch_size, total_items)))
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_batch, start, end): (start, end)
                for start, end in batches
            }
            
            for future in as_completed(futures):
                start, end = futures[future]
                try:
                    batch_docs = future.result()
                    documents.extend(batch_docs)
                    print(f"Processed batch {start}-{end}")
                except Exception as e:
                    print(f"Error in batch {start}-{end}: {e}")
        
        return documents
    
    def _fetch_batch(self, start: int, end: int) -> List[Dict[str, Any]]:
        """Fetch a single batch of documents."""
        # Implementation specific to your data source
        pass
```

### Streaming Support

```python
from typing import Iterator

class StreamingConnector(BaseConnector):
    """Connector with streaming support for large datasets."""
    
    def sync_documents_stream(self, **kwargs) -> Iterator[Dict[str, Any]]:
        """Stream documents instead of loading all into memory."""
        # Example: streaming from a large file
        with open('large_dataset.jsonl', 'r') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
    
    def sync_to_dataset(self, dataset, **kwargs):
        """Stream directly to dataset without memory overhead."""
        count = 0
        for item in self.sync_documents_stream(**kwargs):
            record = self.map_to_frame_record(item)
            dataset.add(record)
            count += 1
            
            if count % 1000 == 0:
                print(f"Processed {count} documents...")
        
        return count
```

## Authentication Patterns

### OAuth 2.0 Implementation

```python
from datetime import datetime, timedelta
import webbrowser

class OAuthConnector(BaseConnector):
    """Connector with OAuth 2.0 authentication."""
    
    def __init__(self, client_id: str, client_secret: str,
                 redirect_uri: str = 'http://localhost:8080/callback'):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
    
    def authenticate(self) -> bool:
        """OAuth 2.0 authentication flow."""
        # Generate authorization URL
        auth_url = self._build_auth_url()
        
        # Open browser for user authorization
        print(f"Opening browser for authorization: {auth_url}")
        webbrowser.open(auth_url)
        
        # Start local server to receive callback
        code = self._wait_for_callback()
        
        # Exchange code for tokens
        tokens = self._exchange_code(code)
        self.access_token = tokens['access_token']
        self.refresh_token = tokens.get('refresh_token')
        self.token_expires = datetime.now() + timedelta(
            seconds=tokens.get('expires_in', 3600)
        )
        
        return True
    
    def _ensure_authenticated(self):
        """Refresh token if needed."""
        if not self.access_token:
            raise RuntimeError("Not authenticated")
        
        if self.token_expires and datetime.now() >= self.token_expires:
            self._refresh_access_token()
    
    def _refresh_access_token(self):
        """Refresh expired access token."""
        if not self.refresh_token:
            raise RuntimeError("No refresh token available")
        
        # Implementation specific to OAuth provider
        pass
```

### Multi-Factor Authentication

```python
class MFAConnector(BaseConnector):
    """Connector with MFA support."""
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with MFA support."""
        # Initial authentication
        auth_response = self._initial_auth(username, password)
        
        if auth_response.get('requires_mfa'):
            # Prompt for MFA code
            mfa_code = input("Enter MFA code: ")
            
            # Complete authentication
            final_response = self._complete_mfa(
                auth_response['session_id'],
                mfa_code
            )
            
            self.session_token = final_response['token']
        else:
            self.session_token = auth_response['token']
        
        return True
```

## Data Mapping Strategies

### Complex Field Mapping

```python
class AdvancedMapper:
    """Advanced mapping strategies for complex data."""
    
    @staticmethod
    def extract_text_content(item: Dict[str, Any]) -> str:
        """Extract text from nested structures."""
        text_parts = []
        
        # Handle different content structures
        if 'blocks' in item:
            # Block-based content (like Notion)
            for block in item['blocks']:
                if block['type'] == 'text':
                    text_parts.append(block['content'])
                elif block['type'] == 'code':
                    text_parts.append(f"```\n{block['content']}\n```")
        
        elif 'sections' in item:
            # Section-based content
            for section in item['sections']:
                if section.get('title'):
                    text_parts.append(f"# {section['title']}")
                if section.get('content'):
                    text_parts.append(section['content'])
        
        else:
            # Fallback to simple extraction
            for field in ['content', 'text', 'body', 'description']:
                if field in item and item[field]:
                    text_parts.append(str(item[field]))
        
        return '\n\n'.join(text_parts)
    
    @staticmethod
    def build_relationships(item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relationships from data."""
        relationships = []
        
        # Parent relationship
        if item.get('parent_id'):
            relationships.append({
                'relationship_type': 'parent',
                'target_id': item['parent_id'],
                'metadata': {'source': 'hierarchy'}
            })
        
        # References
        for ref_id in item.get('references', []):
            relationships.append({
                'relationship_type': 'reference',
                'target_id': ref_id,
                'metadata': {'source': 'explicit_reference'}
            })
        
        # Tags as relationships
        for tag in item.get('tags', []):
            relationships.append({
                'relationship_type': 'tagged_with',
                'target_id': f"tag:{tag}",
                'metadata': {'tag_name': tag}
            })
        
        return relationships
```

### Custom Enrichment

```python
class EnrichmentConnector(BaseConnector):
    """Connector with built-in enrichment."""
    
    def __init__(self, enrichers: Optional[List] = None):
        super().__init__()
        self.enrichers = enrichers or []
    
    def map_to_frame_record(self, item: Dict[str, Any]) -> FrameRecord:
        """Map with enrichment pipeline."""
        # Basic mapping
        record = FrameRecord(
            text_content=self._extract_text(item),
            metadata=self._extract_metadata(item),
            record_type='document'
        )
        
        # Apply enrichers
        for enricher in self.enrichers:
            record = enricher.enrich(record, item)
        
        return record

# Example enricher
class KeywordEnricher:
    """Extract keywords from content."""
    
    def enrich(self, record: FrameRecord, source_item: Dict[str, Any]) -> FrameRecord:
        # Extract keywords using simple frequency analysis
        import re
        from collections import Counter
        
        # Tokenize and count
        words = re.findall(r'\b\w+\b', record.text_content.lower())
        word_counts = Counter(words)
        
        # Get top keywords
        keywords = [word for word, _ in word_counts.most_common(10)]
        
        # Add to context
        if not record.context:
            record.context = {}
        record.context['keywords'] = keywords
        
        return record
```

## Testing Your Connector

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch

class TestCustomConnector(unittest.TestCase):
    """Test suite for custom connector."""
    
    def setUp(self):
        self.connector = CustomConnector(api_key='test-key')
    
    def test_authentication(self):
        """Test authentication flow."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'user': 'test'}
            
            result = self.connector.authenticate()
            self.assertTrue(result)
            self.assertTrue(self.connector.authenticated)
    
    def test_sync_documents(self):
        """Test document synchronization."""
        self.connector.authenticated = True
        
        with patch.object(self.connector, '_fetch_data') as mock_fetch:
            mock_fetch.return_value = [
                {'id': 1, 'content': 'Test 1'},
                {'id': 2, 'content': 'Test 2'}
            ]
            
            documents = self.connector.sync_documents()
            self.assertEqual(len(documents), 2)
    
    def test_mapping(self):
        """Test FrameRecord mapping."""
        item = {
            'id': '123',
            'content': 'Test content',
            'created_at': '2024-01-01T00:00:00Z',
            'author': 'Test User'
        }
        
        record = self.connector.map_to_frame_record(item)
        
        self.assertEqual(record.text_content, 'Test content')
        self.assertEqual(record.unique_id, 'custom:123')
        self.assertEqual(record.metadata['author'], 'Test User')
```

### Integration Tests

```python
class TestConnectorIntegration(unittest.TestCase):
    """Integration tests with ContextFrame."""
    
    def test_full_workflow(self):
        """Test complete import workflow."""
        # Create temporary dataset
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / 'test.lance'
            dataset = FrameDataset.create(str(dataset_path))
            
            # Setup connector
            connector = CustomConnector(test_mode=True)
            connector.authenticate()
            
            # Sync documents
            documents = connector.sync_documents()
            self.assertGreater(len(documents), 0)
            
            # Import to dataset
            for doc in documents:
                record = connector.map_to_frame_record(doc)
                dataset.add(record)
            
            # Verify import
            self.assertEqual(len(dataset), len(documents))
            
            # Test search
            results = dataset.search("test", limit=5)
            self.assertGreater(len(results), 0)
```

## Performance Optimization

### Connection Pooling

```python
class PooledConnector(BaseConnector):
    """Connector with connection pooling."""
    
    def __init__(self, pool_size: int = 10):
        super().__init__()
        self.pool = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
            max_retries=3
        )
        self.pool.mount('http://', adapter)
        self.pool.mount('https://', adapter)
```

### Caching

```python
from functools import lru_cache
import hashlib

class CachedConnector(BaseConnector):
    """Connector with intelligent caching."""
    
    def __init__(self, cache_ttl: int = 3600):
        super().__init__()
        self.cache_ttl = cache_ttl
        self._cache = {}
    
    @lru_cache(maxsize=1000)
    def _fetch_with_cache(self, cache_key: str) -> Dict[str, Any]:
        """Fetch with LRU cache."""
        # Implementation
        pass
    
    def _get_cache_key(self, **params) -> str:
        """Generate cache key from parameters."""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.sha256(param_str.encode()).hexdigest()
```

## Best Practices

### Error Handling

```python
class RobustConnector(BaseConnector):
    """Connector with comprehensive error handling."""
    
    def sync_documents(self, **kwargs) -> List[Dict[str, Any]]:
        """Sync with retry logic and error handling."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return self._sync_documents_internal(**kwargs)
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise
            except requests.exceptions.RequestException as e:
                # Log error and continue with partial results
                print(f"Error during sync: {e}")
                return self._get_cached_results()
```

### Logging

```python
import logging

class LoggedConnector(BaseConnector):
    """Connector with structured logging."""
    
    def __init__(self, log_level=logging.INFO):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
    
    def sync_documents(self, **kwargs) -> List[Dict[str, Any]]:
        """Sync with detailed logging."""
        self.logger.info(f"Starting sync with params: {kwargs}")
        start_time = time.time()
        
        try:
            documents = self._sync_internal(**kwargs)
            elapsed = time.time() - start_time
            self.logger.info(
                f"Sync completed: {len(documents)} documents in {elapsed:.2f}s"
            )
            return documents
        except Exception as e:
            self.logger.error(f"Sync failed: {e}", exc_info=True)
            raise
```

## Publishing Your Connector

### Package Structure

```
my-connector/
├── setup.py
├── README.md
├── LICENSE
├── requirements.txt
├── src/
│   └── my_connector/
│       ├── __init__.py
│       ├── connector.py
│       ├── auth.py
│       └── utils.py
└── tests/
    ├── __init__.py
    ├── test_connector.py
    └── test_integration.py
```

### Setup.py

```python
from setuptools import setup, find_packages

setup(
    name='contextframe-myplatform',
    version='0.1.0',
    description='MyPlatform connector for ContextFrame',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/contextframe-myplatform',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'contextframe>=0.1.0',
        'requests>=2.28.0',
        # Your dependencies
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.10',
    entry_points={
        'contextframe.connectors': [
            'myplatform = my_connector.connector:MyPlatformConnector',
        ],
    },
)
```

### Documentation

Create comprehensive documentation:

```markdown
# ContextFrame MyPlatform Connector

Connect MyPlatform to ContextFrame for intelligent document management.

## Installation

```bash
pip install contextframe-myplatform
```

## Quick Start

```python
from contextframe import FrameDataset
from my_connector import MyPlatformConnector

# Setup
connector = MyPlatformConnector(api_key="your-api-key")
dataset = FrameDataset.create("myplatform.lance")

# Import data
connector.authenticate()
documents = connector.sync_documents()

for doc in documents:
    record = connector.map_to_frame_record(doc)
    dataset.add(record)
```

## Configuration

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| api_key | API key for authentication | Yes | None |
| base_url | API base URL | No | https://api.myplatform.com |
| timeout | Request timeout in seconds | No | 30 |

## Features

- ✅ Full API coverage
- ✅ Incremental sync
- ✅ Batch processing
- ✅ Rate limiting
- ✅ Error recovery

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
```

## Next Steps

- Review the [API Reference](../api/connectors.md) for detailed interface documentation
- See the [Cookbook](../cookbook/custom-connector.md) for complete examples
- Join the community to share your connectors
- Consider contributing to the official connector repository