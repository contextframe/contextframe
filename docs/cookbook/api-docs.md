# API Documentation Management

Build a comprehensive API documentation system that automatically generates, updates, and maintains searchable documentation from OpenAPI specs, code comments, and usage examples.

## Problem Statement

API documentation often becomes outdated, lacks real-world examples, and is difficult to search. Developers need up-to-date, searchable documentation that includes working examples, change history, and usage patterns.

## Solution Overview

We'll build an API documentation system that:
1. Imports OpenAPI/Swagger specifications
2. Extracts inline code documentation
3. Captures real API usage examples
4. Tracks API changes over time
5. Provides intelligent search and discovery

## Complete Code

```python
import os
import re
import json
import yaml
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import requests
from pathlib import Path
import ast
import hashlib
from dataclasses import dataclass
from jsonschema import validate, ValidationError as JsonSchemaError

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    add_relationship_to_metadata,
    generate_uuid
)

@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    tags: List[str]
    security: List[Dict[str, Any]]
    
@dataclass
class APIExample:
    """Represents an API usage example."""
    endpoint: str
    method: str
    title: str
    description: str
    request: Dict[str, Any]
    response: Dict[str, Any]
    language: str
    status_code: int

class APIDocumentationManager:
    """Comprehensive API documentation management system."""
    
    def __init__(self, dataset_path: str = "api_docs.lance"):
        """Initialize documentation manager."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        self.api_versions = {}
        self.change_history = []
        
    def import_openapi_spec(self, 
                          spec_path: str,
                          api_name: str,
                          version: str,
                          base_url: Optional[str] = None) -> List[FrameRecord]:
        """Import OpenAPI/Swagger specification."""
        print(f"Importing OpenAPI spec for {api_name} v{version}")
        
        # Load spec
        with open(spec_path, 'r') as f:
            if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)
        
        # Extract base URL if not provided
        if not base_url and 'servers' in spec:
            base_url = spec['servers'][0]['url']
        
        # Create API overview record
        overview_record = self._create_api_overview(spec, api_name, version, base_url)
        self.dataset.add(overview_record, generate_embedding=True)
        
        # Process endpoints
        endpoint_records = []
        paths = spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    endpoint = self._parse_endpoint(path, method, operation, spec)
                    record = self._create_endpoint_record(
                        endpoint, api_name, version, base_url, overview_record.unique_id
                    )
                    endpoint_records.append(record)
                    self.dataset.add(record, generate_embedding=True)
        
        # Process schemas/components
        if 'components' in spec and 'schemas' in spec['components']:
            schema_records = self._process_schemas(
                spec['components']['schemas'], 
                api_name, 
                version,
                overview_record.unique_id
            )
            endpoint_records.extend(schema_records)
        
        print(f"Imported {len(endpoint_records)} endpoints and schemas")
        return [overview_record] + endpoint_records
    
    def _create_api_overview(self, spec: Dict[str, Any], 
                           api_name: str, version: str, 
                           base_url: Optional[str]) -> FrameRecord:
        """Create overview record for API."""
        info = spec.get('info', {})
        
        content = f"""# {api_name} API v{version}

{info.get('description', '')}

**Version:** {version}
**Base URL:** {base_url or 'Not specified'}

## Overview
{info.get('x-overview', info.get('description', ''))}

## Authentication
{self._extract_auth_info(spec)}

## Rate Limiting
{info.get('x-rate-limiting', 'See individual endpoints for rate limiting information.')}
"""
        
        metadata = create_metadata(
            title=f"{api_name} API v{version}",
            source="api_documentation",
            api_name=api_name,
            api_version=version,
            base_url=base_url,
            doc_type="overview",
            contact=info.get('contact', {}),
            license=info.get('license', {}),
            terms_of_service=info.get('termsOfService'),
            tags=self._extract_all_tags(spec)
        )
        
        return FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=f"api_{api_name}_{version}_overview",
            record_type="collection_header",
            context={
                "openapi_version": spec.get('openapi', '3.0.0'),
                "servers": spec.get('servers', []),
                "security_schemes": spec.get('components', {}).get('securitySchemes', {})
            }
        )
    
    def _parse_endpoint(self, path: str, method: str, 
                       operation: Dict[str, Any], 
                       spec: Dict[str, Any]) -> APIEndpoint:
        """Parse endpoint from OpenAPI operation."""
        # Resolve references
        operation = self._resolve_refs(operation, spec)
        
        return APIEndpoint(
            path=path,
            method=method.upper(),
            summary=operation.get('summary', ''),
            description=operation.get('description', ''),
            parameters=operation.get('parameters', []),
            request_body=operation.get('requestBody'),
            responses=operation.get('responses', {}),
            tags=operation.get('tags', []),
            security=operation.get('security', spec.get('security', []))
        )
    
    def _create_endpoint_record(self, endpoint: APIEndpoint,
                              api_name: str, version: str,
                              base_url: Optional[str],
                              overview_id: str) -> FrameRecord:
        """Create record for API endpoint."""
        # Generate content
        content = f"""# {endpoint.method} {endpoint.path}

{endpoint.summary}

{endpoint.description}

**Endpoint:** `{endpoint.method} {base_url or ''}{endpoint.path}`

## Parameters
{self._format_parameters(endpoint.parameters)}

## Request Body
{self._format_request_body(endpoint.request_body)}

## Responses
{self._format_responses(endpoint.responses)}

## Security
{self._format_security(endpoint.security)}

## Example Usage
{self._generate_example_code(endpoint, base_url)}
"""
        
        # Create metadata
        metadata = create_metadata(
            title=f"{endpoint.method} {endpoint.path}",
            source="api_documentation",
            api_name=api_name,
            api_version=version,
            doc_type="endpoint",
            endpoint_path=endpoint.path,
            http_method=endpoint.method,
            tags=endpoint.tags,
            has_parameters=bool(endpoint.parameters),
            has_request_body=bool(endpoint.request_body),
            response_codes=list(endpoint.responses.keys()),
            requires_auth=bool(endpoint.security)
        )
        
        # Add relationship to overview
        metadata = add_relationship_to_metadata(
            metadata,
            relationship_type="member_of",
            target_id=overview_id
        )
        
        return FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=f"api_{api_name}_{version}_{endpoint.method}_{endpoint.path.replace('/', '_')}",
            record_type="document",
            context={
                "endpoint": endpoint.__dict__,
                "generated_at": datetime.now().isoformat()
            }
        )
    
    def _format_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        """Format parameters for documentation."""
        if not parameters:
            return "No parameters required."
        
        formatted = []
        for param in parameters:
            required = "**Required**" if param.get('required') else "Optional"
            schema = param.get('schema', {})
            param_type = schema.get('type', 'string')
            
            formatted.append(
                f"- **{param['name']}** ({param.get('in')}) - {required}\n"
                f"  - Type: `{param_type}`\n"
                f"  - Description: {param.get('description', 'No description')}"
            )
            
            if 'enum' in schema:
                formatted.append(f"  - Allowed values: {', '.join(map(str, schema['enum']))}")
            
            if 'default' in schema:
                formatted.append(f"  - Default: `{schema['default']}`")
        
        return '\n'.join(formatted)
    
    def _format_request_body(self, request_body: Optional[Dict[str, Any]]) -> str:
        """Format request body for documentation."""
        if not request_body:
            return "No request body required."
        
        content = request_body.get('content', {})
        formatted = []
        
        for media_type, media_obj in content.items():
            formatted.append(f"### Content-Type: {media_type}\n")
            
            if 'schema' in media_obj:
                schema = media_obj['schema']
                formatted.append("```json")
                formatted.append(json.dumps(self._schema_to_example(schema), indent=2))
                formatted.append("```")
                
                if 'properties' in schema:
                    formatted.append("\n**Properties:**")
                    for prop_name, prop_schema in schema['properties'].items():
                        required = " (required)" if prop_name in schema.get('required', []) else ""
                        formatted.append(
                            f"- **{prop_name}**{required}: {prop_schema.get('type', 'any')} - "
                            f"{prop_schema.get('description', 'No description')}"
                        )
        
        return '\n'.join(formatted)
    
    def _format_responses(self, responses: Dict[str, Dict[str, Any]]) -> str:
        """Format responses for documentation."""
        formatted = []
        
        for status_code, response in responses.items():
            formatted.append(f"### {status_code} - {response.get('description', 'No description')}")
            
            content = response.get('content', {})
            for media_type, media_obj in content.items():
                formatted.append(f"\n**Content-Type:** {media_type}")
                
                if 'schema' in media_obj:
                    formatted.append("\n```json")
                    formatted.append(json.dumps(
                        self._schema_to_example(media_obj['schema']), 
                        indent=2
                    ))
                    formatted.append("```")
        
        return '\n\n'.join(formatted)
    
    def _schema_to_example(self, schema: Dict[str, Any]) -> Any:
        """Convert schema to example value."""
        if 'example' in schema:
            return schema['example']
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            example = {}
            for prop_name, prop_schema in schema.get('properties', {}).items():
                example[prop_name] = self._schema_to_example(prop_schema)
            return example
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self._schema_to_example(items_schema)]
        elif schema_type == 'string':
            if 'enum' in schema:
                return schema['enum'][0]
            elif 'format' in schema:
                formats = {
                    'date': '2024-01-15',
                    'date-time': '2024-01-15T10:30:00Z',
                    'email': 'user@example.com',
                    'uuid': '123e4567-e89b-12d3-a456-426614174000'
                }
                return formats.get(schema['format'], 'string')
            return 'string'
        elif schema_type == 'integer':
            return 0
        elif schema_type == 'number':
            return 0.0
        elif schema_type == 'boolean':
            return True
        else:
            return None
    
    def _generate_example_code(self, endpoint: APIEndpoint, 
                             base_url: Optional[str]) -> str:
        """Generate example code for endpoint."""
        examples = []
        
        # cURL example
        curl_example = self._generate_curl_example(endpoint, base_url)
        examples.append(f"### cURL\n```bash\n{curl_example}\n```")
        
        # Python example
        python_example = self._generate_python_example(endpoint, base_url)
        examples.append(f"### Python\n```python\n{python_example}\n```")
        
        # JavaScript example
        js_example = self._generate_javascript_example(endpoint, base_url)
        examples.append(f"### JavaScript\n```javascript\n{js_example}\n```")
        
        return '\n\n'.join(examples)
    
    def _generate_curl_example(self, endpoint: APIEndpoint, 
                             base_url: Optional[str]) -> str:
        """Generate cURL example."""
        url = f"{base_url or 'https://api.example.com'}{endpoint.path}"
        
        # Replace path parameters
        for param in endpoint.parameters:
            if param.get('in') == 'path':
                url = url.replace(f"{{{param['name']}}}", "value")
        
        curl_parts = [f"curl -X {endpoint.method} '{url}'"]
        
        # Add headers
        curl_parts.append("  -H 'Accept: application/json'")
        
        if endpoint.request_body:
            curl_parts.append("  -H 'Content-Type: application/json'")
            content = endpoint.request_body.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                example_data = self._schema_to_example(schema)
                curl_parts.append(f"  -d '{json.dumps(example_data)}'")
        
        # Add auth header if required
        if endpoint.security:
            curl_parts.append("  -H 'Authorization: Bearer YOUR_API_TOKEN'")
        
        return " \\\n".join(curl_parts)
    
    def _generate_python_example(self, endpoint: APIEndpoint, 
                               base_url: Optional[str]) -> str:
        """Generate Python example."""
        url = f"{base_url or 'https://api.example.com'}{endpoint.path}"
        
        example = f"""import requests

url = "{url}"
"""
        
        # Add headers
        example += "\nheaders = {\n    'Accept': 'application/json'"
        if endpoint.security:
            example += ",\n    'Authorization': 'Bearer YOUR_API_TOKEN'"
        example += "\n}\n"
        
        # Add request body
        if endpoint.request_body:
            content = endpoint.request_body.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                example_data = self._schema_to_example(schema)
                example += f"\ndata = {json.dumps(example_data, indent=4)}\n"
                example += f"\nresponse = requests.{endpoint.method.lower()}(url, headers=headers, json=data)"
        else:
            example += f"\nresponse = requests.{endpoint.method.lower()}(url, headers=headers)"
        
        example += "\nprint(response.json())"
        
        return example
    
    def _generate_javascript_example(self, endpoint: APIEndpoint, 
                                   base_url: Optional[str]) -> str:
        """Generate JavaScript example."""
        url = f"{base_url or 'https://api.example.com'}{endpoint.path}"
        
        options = {
            'method': endpoint.method,
            'headers': {
                'Accept': 'application/json'
            }
        }
        
        if endpoint.security:
            options['headers']['Authorization'] = 'Bearer YOUR_API_TOKEN'
        
        if endpoint.request_body:
            content = endpoint.request_body.get('content', {})
            if 'application/json' in content:
                options['headers']['Content-Type'] = 'application/json'
                schema = content['application/json'].get('schema', {})
                example_data = self._schema_to_example(schema)
                options['body'] = f"JSON.stringify({json.dumps(example_data, indent=2)})"
        
        example = f"""fetch('{url}', {json.dumps(options, indent=2)})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));"""
        
        return example
    
    def add_usage_example(self, example: APIExample) -> FrameRecord:
        """Add real-world usage example."""
        # Generate content
        content = f"""# Example: {example.title}

{example.description}

**Endpoint:** `{example.method} {example.endpoint}`
**Status Code:** {example.status_code}

## Request

```{example.language}
{json.dumps(example.request, indent=2)}
```

## Response

```json
{json.dumps(example.response, indent=2)}
```
"""
        
        # Create metadata
        metadata = create_metadata(
            title=f"Example: {example.title}",
            source="api_example",
            endpoint=example.endpoint,
            http_method=example.method,
            status_code=example.status_code,
            language=example.language,
            example_type="usage"
        )
        
        # Find related endpoint
        endpoint_results = self.dataset.sql_filter(
            f"metadata.endpoint_path = '{example.endpoint}' AND "
            f"metadata.http_method = '{example.method}'",
            limit=1
        )
        
        if endpoint_results:
            metadata = add_relationship_to_metadata(
                metadata,
                relationship_type="example_of",
                target_id=endpoint_results[0].unique_id
            )
        
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=f"example_{generate_uuid()}",
            record_type="document",
            context={
                "request": example.request,
                "response": example.response,
                "created_at": datetime.now().isoformat()
            }
        )
        
        self.dataset.add(record, generate_embedding=True)
        return record
    
    def extract_code_docs(self, code_path: str, language: str = "python") -> List[FrameRecord]:
        """Extract documentation from code files."""
        records = []
        
        if language == "python":
            records = self._extract_python_docs(code_path)
        elif language == "javascript":
            records = self._extract_javascript_docs(code_path)
        # Add more languages as needed
        
        return records
    
    def _extract_python_docs(self, file_path: str) -> List[FrameRecord]:
        """Extract documentation from Python code."""
        records = []
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return records
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if docstring and any(decorator.id == 'route' for decorator in node.decorator_list if isinstance(decorator, ast.Name)):
                    # This is likely an API endpoint
                    record = self._create_code_doc_record(
                        name=node.name,
                        docstring=docstring,
                        source_file=file_path,
                        line_number=node.lineno,
                        language="python"
                    )
                    records.append(record)
                    self.dataset.add(record, generate_embedding=True)
        
        return records
    
    def track_api_changes(self, 
                         old_spec_path: str,
                         new_spec_path: str,
                         api_name: str,
                         old_version: str,
                         new_version: str) -> Dict[str, Any]:
        """Track changes between API versions."""
        # Load specs
        with open(old_spec_path, 'r') as f:
            old_spec = yaml.safe_load(f) if old_spec_path.endswith('.yaml') else json.load(f)
        
        with open(new_spec_path, 'r') as f:
            new_spec = yaml.safe_load(f) if new_spec_path.endswith('.yaml') else json.load(f)
        
        changes = {
            'breaking': [],
            'additions': [],
            'modifications': [],
            'deprecations': []
        }
        
        # Compare endpoints
        old_paths = set(old_spec.get('paths', {}).keys())
        new_paths = set(new_spec.get('paths', {}).keys())
        
        # Removed endpoints (breaking)
        for path in old_paths - new_paths:
            changes['breaking'].append({
                'type': 'endpoint_removed',
                'path': path,
                'description': f"Endpoint {path} was removed"
            })
        
        # Added endpoints
        for path in new_paths - old_paths:
            changes['additions'].append({
                'type': 'endpoint_added',
                'path': path,
                'description': f"New endpoint {path} added"
            })
        
        # Modified endpoints
        for path in old_paths & new_paths:
            old_methods = set(old_spec['paths'][path].keys())
            new_methods = set(new_spec['paths'][path].keys())
            
            # Method changes
            for method in old_methods - new_methods:
                changes['breaking'].append({
                    'type': 'method_removed',
                    'path': path,
                    'method': method,
                    'description': f"Method {method} removed from {path}"
                })
            
            for method in new_methods - old_methods:
                changes['additions'].append({
                    'type': 'method_added',
                    'path': path,
                    'method': method,
                    'description': f"Method {method} added to {path}"
                })
        
        # Create change record
        self._create_change_record(changes, api_name, old_version, new_version)
        
        return changes
    
    def _create_change_record(self, changes: Dict[str, Any],
                            api_name: str,
                            old_version: str,
                            new_version: str) -> FrameRecord:
        """Create record for API changes."""
        # Generate content
        content = f"""# API Changes: {api_name} v{old_version} → v{new_version}

## Breaking Changes ({len(changes['breaking'])})
"""
        for change in changes['breaking']:
            content += f"- **{change['type']}**: {change['description']}\n"
        
        content += f"\n## Additions ({len(changes['additions'])})\n"
        for change in changes['additions']:
            content += f"- **{change['type']}**: {change['description']}\n"
        
        content += f"\n## Modifications ({len(changes['modifications'])})\n"
        for change in changes['modifications']:
            content += f"- **{change['type']}**: {change['description']}\n"
        
        content += f"\n## Deprecations ({len(changes['deprecations'])})\n"
        for change in changes['deprecations']:
            content += f"- **{change['type']}**: {change['description']}\n"
        
        # Create metadata
        metadata = create_metadata(
            title=f"Changes: {api_name} v{old_version} → v{new_version}",
            source="api_changelog",
            api_name=api_name,
            old_version=old_version,
            new_version=new_version,
            doc_type="changelog",
            breaking_change_count=len(changes['breaking']),
            addition_count=len(changes['additions']),
            has_breaking_changes=len(changes['breaking']) > 0
        )
        
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=f"changelog_{api_name}_{old_version}_{new_version}",
            record_type="document",
            context={
                "changes": changes,
                "generated_at": datetime.now().isoformat()
            }
        )
        
        self.dataset.add(record, generate_embedding=True)
        return record
    
    def search_endpoints(self, 
                        query: str,
                        filters: Optional[Dict[str, Any]] = None,
                        limit: int = 20) -> List[Dict[str, Any]]:
        """Search API endpoints."""
        # Build filter
        filter_conditions = ["metadata.doc_type = 'endpoint'"]
        
        if filters:
            if 'method' in filters:
                filter_conditions.append(f"metadata.http_method = '{filters['method']}'")
            if 'tag' in filters:
                filter_conditions.append(f"array_contains(metadata.tags, '{filters['tag']}')")
            if 'api_name' in filters:
                filter_conditions.append(f"metadata.api_name = '{filters['api_name']}'")
            if 'version' in filters:
                filter_conditions.append(f"metadata.api_version = '{filters['version']}'")
        
        filter_str = " AND ".join(filter_conditions)
        
        # Search
        results = self.dataset.search(query, filter=filter_str, limit=limit)
        
        # Format results
        formatted = []
        for result in results:
            formatted.append({
                'endpoint': f"{result.metadata['http_method']} {result.metadata['endpoint_path']}",
                'api': result.metadata['api_name'],
                'version': result.metadata['api_version'],
                'summary': result.metadata.get('title', ''),
                'tags': result.metadata.get('tags', []),
                'score': result.score,
                'unique_id': result.unique_id
            })
        
        return formatted
    
    def generate_client_sdk(self, 
                          api_name: str,
                          version: str,
                          language: str,
                          output_path: str):
        """Generate client SDK from API documentation."""
        # Get all endpoints for API
        endpoints = self.dataset.sql_filter(
            f"metadata.api_name = '{api_name}' AND "
            f"metadata.api_version = '{version}' AND "
            f"metadata.doc_type = 'endpoint'"
        )
        
        if language == "python":
            self._generate_python_sdk(endpoints, api_name, version, output_path)
        elif language == "javascript":
            self._generate_javascript_sdk(endpoints, api_name, version, output_path)
        # Add more languages as needed
    
    def _generate_python_sdk(self, endpoints: List[FrameRecord],
                           api_name: str, version: str,
                           output_path: str):
        """Generate Python SDK."""
        # Group endpoints by tag
        by_tag = {}
        for endpoint in endpoints:
            for tag in endpoint.metadata.get('tags', ['default']):
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(endpoint)
        
        # Generate SDK code
        sdk_code = f'''"""
{api_name} Python SDK v{version}
Auto-generated from OpenAPI specification
"""

import requests
from typing import Dict, Any, Optional, List


class {api_name.replace("-", "").title()}Client:
    """Client for {api_name} API v{version}."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
'''
        
        # Generate methods for each endpoint
        for tag, tag_endpoints in by_tag.items():
            sdk_code += f'\n    # {tag.title()} endpoints\n'
            
            for endpoint_record in tag_endpoints:
                endpoint = endpoint_record.context['endpoint']
                method_name = self._generate_method_name(
                    endpoint['path'], 
                    endpoint['method']
                )
                
                sdk_code += self._generate_python_method(
                    method_name, 
                    endpoint
                )
        
        # Write SDK
        with open(output_path, 'w') as f:
            f.write(sdk_code)
        
        print(f"Generated Python SDK at {output_path}")
    
    def _generate_method_name(self, path: str, method: str) -> str:
        """Generate method name from path and HTTP method."""
        # Convert path to method name
        parts = path.strip('/').split('/')
        
        # Remove parameter placeholders
        parts = [p for p in parts if not (p.startswith('{') and p.endswith('}'))]
        
        # Create method name
        if method == 'GET':
            prefix = 'get' if '/' in path else 'list'
        elif method == 'POST':
            prefix = 'create'
        elif method == 'PUT':
            prefix = 'update'
        elif method == 'DELETE':
            prefix = 'delete'
        else:
            prefix = method.lower()
        
        suffix = '_'.join(parts)
        return f"{prefix}_{suffix}" if suffix else prefix
    
    def _generate_python_method(self, method_name: str, 
                              endpoint: Dict[str, Any]) -> str:
        """Generate Python method for endpoint."""
        # Build parameter list
        params = []
        path_params = []
        query_params = []
        
        for param in endpoint.get('parameters', []):
            param_name = param['name']
            param_in = param.get('in')
            
            if param_in == 'path':
                path_params.append(param_name)
                params.append(f"{param_name}: str")
            elif param_in == 'query':
                query_params.append(param_name)
                default = " = None" if not param.get('required') else ""
                param_type = self._python_type_from_schema(param.get('schema', {}))
                params.append(f"{param_name}: Optional[{param_type}]{default}")
        
        # Add body parameter if needed
        if endpoint.get('request_body'):
            params.append("data: Dict[str, Any]")
        
        # Generate method
        method = f"""
    def {method_name}(self, {', '.join(params)}) -> Dict[str, Any]:
        \"\"\"{endpoint.get('summary', '')}
        
        {endpoint.get('description', '')}
        \"\"\"
        url = f"{{self.base_url}}{endpoint['path']}"
"""
        
        # Add query parameters
        if query_params:
            method += "        params = {}\n"
            for qp in query_params:
                method += f"        if {qp} is not None:\n"
                method += f"            params['{qp}'] = {qp}\n"
        
        # Make request
        if endpoint.get('request_body'):
            method += f"        response = self.session.{endpoint['method'].lower()}(url, json=data"
            if query_params:
                method += ", params=params"
            method += ")\n"
        else:
            method += f"        response = self.session.{endpoint['method'].lower()}(url"
            if query_params:
                method += ", params=params"
            method += ")\n"
        
        method += "        response.raise_for_status()\n"
        method += "        return response.json()\n"
        
        return method
    
    def _python_type_from_schema(self, schema: Dict[str, Any]) -> str:
        """Convert JSON schema type to Python type."""
        json_type = schema.get('type', 'any')
        
        type_map = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'List[Any]',
            'object': 'Dict[str, Any]'
        }
        
        return type_map.get(json_type, 'Any')
    
    def _extract_auth_info(self, spec: Dict[str, Any]) -> str:
        """Extract authentication information from spec."""
        security_schemes = spec.get('components', {}).get('securitySchemes', {})
        
        if not security_schemes:
            return "No authentication required."
        
        auth_info = []
        for scheme_name, scheme in security_schemes.items():
            if scheme['type'] == 'apiKey':
                auth_info.append(
                    f"**{scheme_name}**: API Key in {scheme['in']} "
                    f"(parameter name: {scheme['name']})"
                )
            elif scheme['type'] == 'http':
                auth_info.append(
                    f"**{scheme_name}**: HTTP {scheme.get('scheme', 'bearer').title()}"
                )
            elif scheme['type'] == 'oauth2':
                auth_info.append(f"**{scheme_name}**: OAuth 2.0")
        
        return '\n'.join(auth_info)
    
    def _extract_all_tags(self, spec: Dict[str, Any]) -> List[str]:
        """Extract all tags from spec."""
        tags = []
        
        # Get defined tags
        for tag in spec.get('tags', []):
            tags.append(tag['name'])
        
        # Get tags from endpoints
        for path in spec.get('paths', {}).values():
            for operation in path.values():
                if isinstance(operation, dict):
                    tags.extend(operation.get('tags', []))
        
        return list(set(tags))
    
    def _resolve_refs(self, obj: Any, spec: Dict[str, Any]) -> Any:
        """Resolve $ref references in OpenAPI spec."""
        if isinstance(obj, dict):
            if '$ref' in obj:
                ref_path = obj['$ref'].split('/')
                resolved = spec
                for part in ref_path[1:]:  # Skip '#'
                    resolved = resolved[part]
                return self._resolve_refs(resolved, spec)
            else:
                return {k: self._resolve_refs(v, spec) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_refs(item, spec) for item in obj]
        else:
            return obj
    
    def _process_schemas(self, schemas: Dict[str, Any],
                        api_name: str, version: str,
                        overview_id: str) -> List[FrameRecord]:
        """Process schema definitions."""
        records = []
        
        for schema_name, schema_def in schemas.items():
            content = f"""# Schema: {schema_name}

{schema_def.get('description', '')}

## Properties
"""
            if 'properties' in schema_def:
                for prop_name, prop_def in schema_def['properties'].items():
                    required = " **(required)**" if prop_name in schema_def.get('required', []) else ""
                    content += f"- **{prop_name}**{required}: `{prop_def.get('type', 'any')}` - {prop_def.get('description', '')}\n"
            
            content += f"\n## Example\n```json\n{json.dumps(self._schema_to_example(schema_def), indent=2)}\n```"
            
            metadata = create_metadata(
                title=f"Schema: {schema_name}",
                source="api_documentation",
                api_name=api_name,
                api_version=version,
                doc_type="schema",
                schema_name=schema_name
            )
            
            metadata = add_relationship_to_metadata(
                metadata,
                relationship_type="member_of",
                target_id=overview_id
            )
            
            record = FrameRecord(
                text_content=content,
                metadata=metadata,
                unique_id=f"schema_{api_name}_{version}_{schema_name}",
                record_type="document"
            )
            
            records.append(record)
            self.dataset.add(record, generate_embedding=True)
        
        return records

# Example usage
if __name__ == "__main__":
    # Initialize manager
    doc_manager = APIDocumentationManager()
    
    # Import OpenAPI spec
    doc_manager.import_openapi_spec(
        spec_path="api/openapi.yaml",
        api_name="MyAPI",
        version="2.0.0",
        base_url="https://api.mycompany.com"
    )
    
    # Add usage examples
    example = APIExample(
        endpoint="/users/{id}",
        method="GET",
        title="Get User by ID",
        description="Retrieve a specific user's details",
        request={
            "path_params": {"id": "12345"}
        },
        response={
            "id": "12345",
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": "2024-01-15T10:30:00Z"
        },
        language="curl",
        status_code=200
    )
    
    doc_manager.add_usage_example(example)
    
    # Track API changes
    changes = doc_manager.track_api_changes(
        old_spec_path="api/openapi-v1.yaml",
        new_spec_path="api/openapi-v2.yaml",
        api_name="MyAPI",
        old_version="1.0.0",
        new_version="2.0.0"
    )
    
    print(f"Breaking changes: {len(changes['breaking'])}")
    print(f"New endpoints: {len(changes['additions'])}")
    
    # Search endpoints
    results = doc_manager.search_endpoints(
        "user authentication",
        filters={'method': 'POST'}
    )
    
    print("\nSearch Results:")
    for result in results[:5]:
        print(f"- {result['endpoint']} ({result['api']} v{result['version']})")
    
    # Generate SDK
    doc_manager.generate_client_sdk(
        api_name="MyAPI",
        version="2.0.0",
        language="python",
        output_path="sdk/myapi_client.py"
    )
```

## Key Concepts

### 1. OpenAPI Import
- Complete spec parsing
- Reference resolution
- Schema extraction
- Example generation
- Multi-version support

### 2. Code Documentation
- AST parsing for docstrings
- Decorator detection
- Function signature extraction
- Inline comment parsing

### 3. Change Tracking
- Version comparison
- Breaking change detection
- Migration guide generation
- Deprecation tracking

### 4. Search & Discovery
- Endpoint search
- Parameter filtering
- Tag-based navigation
- Version-aware search

### 5. SDK Generation
- Language-specific code generation
- Type mapping
- Authentication handling
- Error handling patterns

## Extensions

### 1. GraphQL Support
```python
def import_graphql_schema(self, schema_path: str, 
                         api_name: str, version: str):
    """Import GraphQL schema."""
    with open(schema_path, 'r') as f:
        schema_sdl = f.read()
    
    # Parse schema
    from graphql import build_schema
    schema = build_schema(schema_sdl)
    
    # Process types
    for type_name, type_def in schema.type_map.items():
        if not type_name.startswith('__'):  # Skip introspection types
            record = self._create_graphql_type_record(
                type_name, type_def, api_name, version
            )
            self.dataset.add(record, generate_embedding=True)
```

### 2. API Testing Integration
```python
def generate_api_tests(self, api_name: str, version: str,
                      test_framework: str = "pytest"):
    """Generate API tests from documentation."""
    endpoints = self.dataset.sql_filter(
        f"metadata.api_name = '{api_name}' AND "
        f"metadata.api_version = '{version}' AND "
        f"metadata.doc_type = 'endpoint'"
    )
    
    if test_framework == "pytest":
        test_code = f"""import pytest
import requests
from myapi_client import MyAPIClient

@pytest.fixture
def client():
    return MyAPIClient(api_key="test_key")

"""
        
        for endpoint in endpoints:
            test_name = f"test_{endpoint.metadata['http_method'].lower()}_{endpoint.metadata['endpoint_path'].replace('/', '_')}"
            test_code += f"""
def {test_name}(client):
    \"\"\"Test {endpoint.metadata['http_method']} {endpoint.metadata['endpoint_path']}.\"\"\"
    # Add test implementation
    pass
"""
        
        return test_code
```

### 3. Interactive Documentation
```python
def generate_interactive_docs(self, output_dir: str):
    """Generate interactive API documentation."""
    import shutil
    
    # Copy Swagger UI files
    shutil.copytree("swagger-ui-dist", f"{output_dir}/swagger-ui")
    
    # Generate index.html
    html = """<!DOCTYPE html>
<html>
<head>
    <title>API Documentation</title>
    <link rel="stylesheet" href="swagger-ui/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="swagger-ui/swagger-ui-bundle.js"></script>
    <script>
        const ui = SwaggerUIBundle({
            url: "/openapi.json",
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ]
        });
    </script>
</body>
</html>"""
    
    with open(f"{output_dir}/index.html", 'w') as f:
        f.write(html)
```

### 4. API Mocking
```python
from flask import Flask, jsonify, request

def create_mock_server(self, api_name: str, version: str):
    """Create mock server from API documentation."""
    app = Flask(__name__)
    
    # Get all endpoints
    endpoints = self.dataset.sql_filter(
        f"metadata.api_name = '{api_name}' AND "
        f"metadata.api_version = '{version}' AND "
        f"metadata.doc_type = 'endpoint'"
    )
    
    for endpoint_record in endpoints:
        endpoint = endpoint_record.context['endpoint']
        
        # Create route
        def create_handler(ep):
            def handler(**kwargs):
                # Return example response
                responses = ep.get('responses', {})
                if '200' in responses:
                    content = responses['200'].get('content', {})
                    if 'application/json' in content:
                        schema = content['application/json'].get('schema', {})
                        return jsonify(self._schema_to_example(schema))
                return jsonify({"message": "Mock response"})
            return handler
        
        # Register route
        app.add_url_rule(
            endpoint['path'],
            endpoint_name=f"{endpoint['method']}_{endpoint['path']}",
            view_func=create_handler(endpoint),
            methods=[endpoint['method']]
        )
    
    return app
```

### 5. Documentation Quality Metrics
```python
def analyze_documentation_quality(self, api_name: str, 
                                version: str) -> Dict[str, Any]:
    """Analyze API documentation quality."""
    endpoints = self.dataset.sql_filter(
        f"metadata.api_name = '{api_name}' AND "
        f"metadata.api_version = '{version}' AND "
        f"metadata.doc_type = 'endpoint'"
    )
    
    metrics = {
        'total_endpoints': len(endpoints),
        'documented_endpoints': 0,
        'endpoints_with_examples': 0,
        'endpoints_with_descriptions': 0,
        'average_description_length': 0,
        'missing_descriptions': [],
        'missing_examples': []
    }
    
    desc_lengths = []
    
    for endpoint in endpoints:
        endpoint_data = endpoint.context['endpoint']
        
        # Check description
        if endpoint_data.get('description'):
            metrics['endpoints_with_descriptions'] += 1
            desc_lengths.append(len(endpoint_data['description']))
        else:
            metrics['missing_descriptions'].append(
                f"{endpoint_data['method']} {endpoint_data['path']}"
            )
        
        # Check for examples
        example_results = self.dataset.sql_filter(
            f"metadata.source = 'api_example' AND "
            f"metadata.endpoint = '{endpoint_data['path']}' AND "
            f"metadata.http_method = '{endpoint_data['method']}'",
            limit=1
        )
        
        if example_results:
            metrics['endpoints_with_examples'] += 1
        else:
            metrics['missing_examples'].append(
                f"{endpoint_data['method']} {endpoint_data['path']}"
            )
    
    if desc_lengths:
        metrics['average_description_length'] = sum(desc_lengths) / len(desc_lengths)
    
    # Calculate completeness score
    metrics['completeness_score'] = (
        (metrics['endpoints_with_descriptions'] / metrics['total_endpoints']) * 0.5 +
        (metrics['endpoints_with_examples'] / metrics['total_endpoints']) * 0.5
    ) * 100
    
    return metrics
```

## Best Practices

1. **Version Everything**: Track all API versions comprehensively
2. **Real Examples**: Include actual request/response examples
3. **Change Logs**: Maintain detailed change history
4. **Search Optimization**: Index all relevant fields
5. **Consistency**: Use consistent terminology and formatting
6. **Automation**: Auto-generate docs from code when possible
7. **Testing**: Generate tests from documentation

## See Also

- [GitHub Knowledge Base](github-knowledge-base.md) - Code documentation
- [Document Processing Pipeline](document-pipeline.md) - Processing API specs
- [Multi-Source Search](multi-source-search.md) - Searching documentation
- [API Reference](../api/overview.md) - FrameDataset documentation