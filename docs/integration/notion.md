# Notion Connector

The Notion connector enables importing pages, databases, and blocks from Notion workspaces into ContextFrame. This guide covers authentication, usage patterns, and advanced integration techniques.

## Overview

The Notion connector can import:
- Pages with rich content and formatting
- Database entries with properties
- Nested page hierarchies
- Comments and discussions
- Files and media attachments
- Page history and versions
- User mentions and references

## Installation

The Notion connector requires the Notion SDK:

```bash
pip install "contextframe[connectors]"
# Or specifically
pip install notion-client
```

```python
from contextframe.connectors import NotionConnector
```

## Authentication

### API Key Setup

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name and select capabilities:
   - Read content
   - Read comments
   - Read user information (optional)
4. Copy the Internal Integration Token

### Workspace Connection

1. In your Notion workspace, go to the page/database you want to share
2. Click "..." menu → "Add connections"
3. Select your integration
4. The integration now has access to that page and its children

```python
connector = NotionConnector(
    api_key="secret_xxxxxxxxxxxx"
)
```

### Environment Variables

```bash
export NOTION_API_KEY="secret_xxxxxxxxxxxx"
```

```python
import os

connector = NotionConnector(
    api_key=os.getenv("NOTION_API_KEY")
)
```

## Basic Usage

### Import Pages

```python
from contextframe import FrameDataset
from contextframe.connectors import NotionConnector

# Create dataset
dataset = FrameDataset.create("notion_kb.lance")

# Setup connector
connector = NotionConnector(
    api_key="your-api-key"
)

# Authenticate
connector.authenticate()

# Get all accessible pages
pages = connector.sync_pages()

# Convert to FrameRecords
for page in pages:
    record = connector.map_to_frame_record(page)
    dataset.add(record)

print(f"Imported {len(pages)} pages")
```

### Import Specific Database

```python
# Get database ID from URL or share link
# URL format: https://www.notion.so/workspace/DATABASE_ID?v=VIEW_ID
database_id = "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"

# Get database metadata
database = connector.get_database(database_id)
print(f"Database: {database.title}")

# Query database entries
entries = connector.query_database(
    database_id=database_id,
    filter={
        "property": "Status",
        "select": {
            "equals": "Published"
        }
    },
    sorts=[{
        "property": "Created",
        "direction": "descending"
    }]
)

# Import entries
for entry in entries:
    record = connector.map_database_entry_to_record(entry)
    dataset.add(record)
```

### Import Page Hierarchy

```python
def import_page_tree(connector, dataset, root_page_id):
    """Import page and all its children recursively."""
    
    # Get root page
    page = connector.get_page(root_page_id)
    page_record = connector.map_to_frame_record(page)
    dataset.add(page_record)
    
    # Get child pages
    children = connector.get_child_pages(root_page_id)
    
    for child in children:
        # Create child record
        child_record = connector.map_to_frame_record(child)
        
        # Add parent relationship
        child_record.add_relationship(
            page_record.uuid,
            "child",
            title=f"Subpage of {page.title}"
        )
        
        dataset.add(child_record)
        
        # Recursively import children
        import_page_tree(connector, dataset, child.id)
```

## Advanced Features

### Rich Content Extraction

```python
class NotionContentExtractor:
    """Extract and convert Notion blocks to markdown."""
    
    def __init__(self, connector):
        self.connector = connector
    
    def extract_page_content(self, page_id):
        """Extract full content from a Notion page."""
        # Get page blocks
        blocks = self.connector.get_blocks(page_id)
        
        # Convert to markdown
        markdown = self.blocks_to_markdown(blocks)
        
        # Get page properties
        page = self.connector.get_page(page_id)
        properties = self.extract_properties(page)
        
        # Combine content
        full_content = f"# {page.title}\n\n"
        
        # Add properties as metadata
        if properties:
            full_content += "## Metadata\n\n"
            for key, value in properties.items():
                full_content += f"- **{key}**: {value}\n"
            full_content += "\n"
        
        full_content += markdown
        
        return full_content
    
    def blocks_to_markdown(self, blocks, indent_level=0):
        """Convert Notion blocks to markdown."""
        markdown = ""
        indent = "  " * indent_level
        
        for block in blocks:
            block_type = block['type']
            
            if block_type == 'paragraph':
                text = self.extract_text(block['paragraph']['rich_text'])
                markdown += f"{indent}{text}\n\n"
            
            elif block_type == 'heading_1':
                text = self.extract_text(block['heading_1']['rich_text'])
                markdown += f"{indent}# {text}\n\n"
            
            elif block_type == 'heading_2':
                text = self.extract_text(block['heading_2']['rich_text'])
                markdown += f"{indent}## {text}\n\n"
            
            elif block_type == 'heading_3':
                text = self.extract_text(block['heading_3']['rich_text'])
                markdown += f"{indent}### {text}\n\n"
            
            elif block_type == 'bulleted_list_item':
                text = self.extract_text(block['bulleted_list_item']['rich_text'])
                markdown += f"{indent}- {text}\n"
            
            elif block_type == 'numbered_list_item':
                text = self.extract_text(block['numbered_list_item']['rich_text'])
                # Note: Real implementation would track numbering
                markdown += f"{indent}1. {text}\n"
            
            elif block_type == 'code':
                code = self.extract_text(block['code']['rich_text'])
                language = block['code'].get('language', '')
                markdown += f"{indent}```{language}\n{code}\n{indent}```\n\n"
            
            elif block_type == 'quote':
                text = self.extract_text(block['quote']['rich_text'])
                markdown += f"{indent}> {text}\n\n"
            
            elif block_type == 'callout':
                text = self.extract_text(block['callout']['rich_text'])
                icon = block['callout'].get('icon', {}).get('emoji', '💡')
                markdown += f"{indent}> {icon} {text}\n\n"
            
            elif block_type == 'toggle':
                text = self.extract_text(block['toggle']['rich_text'])
                markdown += f"{indent}<details>\n{indent}<summary>{text}</summary>\n\n"
                
                # Get child blocks
                if block.get('has_children'):
                    children = self.connector.get_blocks(block['id'])
                    markdown += self.blocks_to_markdown(children, indent_level + 1)
                
                markdown += f"{indent}</details>\n\n"
            
            elif block_type == 'table':
                markdown += self.table_to_markdown(block, indent)
            
            elif block_type == 'image':
                url = block['image'].get('external', {}).get('url', '')
                if not url:
                    url = block['image'].get('file', {}).get('url', '')
                caption = self.extract_text(block['image'].get('caption', []))
                markdown += f"{indent}![{caption}]({url})\n\n"
            
            # Handle child blocks
            if block.get('has_children') and block_type not in ['toggle']:
                children = self.connector.get_blocks(block['id'])
                markdown += self.blocks_to_markdown(children, indent_level + 1)
        
        return markdown
    
    def extract_text(self, rich_text_array):
        """Extract plain text from Notion rich text."""
        text = ""
        
        for text_obj in rich_text_array:
            plain_text = text_obj.get('plain_text', '')
            annotations = text_obj.get('annotations', {})
            
            # Apply formatting
            if annotations.get('bold'):
                plain_text = f"**{plain_text}**"
            if annotations.get('italic'):
                plain_text = f"*{plain_text}*"
            if annotations.get('code'):
                plain_text = f"`{plain_text}`"
            if annotations.get('strikethrough'):
                plain_text = f"~~{plain_text}~~"
            
            # Handle links
            if text_obj.get('href'):
                plain_text = f"[{plain_text}]({text_obj['href']})"
            
            text += plain_text
        
        return text
    
    def table_to_markdown(self, table_block, indent=""):
        """Convert Notion table to markdown."""
        # Get table rows
        table_id = table_block['id']
        rows = self.connector.get_table_rows(table_id)
        
        if not rows:
            return ""
        
        markdown = ""
        
        # Process header row
        header_cells = rows[0].get('table_row', {}).get('cells', [])
        headers = [self.extract_text(cell) for cell in header_cells]
        markdown += f"{indent}| " + " | ".join(headers) + " |\n"
        markdown += f"{indent}|" + "|".join(["---"] * len(headers)) + "|\n"
        
        # Process data rows
        for row in rows[1:]:
            cells = row.get('table_row', {}).get('cells', [])
            values = [self.extract_text(cell) for cell in cells]
            markdown += f"{indent}| " + " | ".join(values) + " |\n"
        
        markdown += "\n"
        return markdown
```

### Database Properties Handling

```python
def extract_database_properties(page):
    """Extract and format database properties."""
    properties = {}
    
    for prop_name, prop_data in page.properties.items():
        prop_type = prop_data['type']
        
        if prop_type == 'title':
            properties[prop_name] = prop_data['title'][0]['plain_text'] if prop_data['title'] else ''
        
        elif prop_type == 'rich_text':
            texts = [t['plain_text'] for t in prop_data['rich_text']]
            properties[prop_name] = ' '.join(texts)
        
        elif prop_type == 'number':
            properties[prop_name] = prop_data['number']
        
        elif prop_type == 'select':
            properties[prop_name] = prop_data['select']['name'] if prop_data['select'] else None
        
        elif prop_type == 'multi_select':
            properties[prop_name] = [opt['name'] for opt in prop_data['multi_select']]
        
        elif prop_type == 'date':
            date_obj = prop_data['date']
            if date_obj:
                properties[prop_name] = {
                    'start': date_obj['start'],
                    'end': date_obj.get('end'),
                    'time_zone': date_obj.get('time_zone')
                }
        
        elif prop_type == 'people':
            people = []
            for person in prop_data['people']:
                people.append({
                    'name': person.get('name', 'Unknown'),
                    'email': person.get('person', {}).get('email')
                })
            properties[prop_name] = people
        
        elif prop_type == 'files':
            files = []
            for file in prop_data['files']:
                if file['type'] == 'external':
                    files.append(file['external']['url'])
                else:
                    files.append(file['file']['url'])
            properties[prop_name] = files
        
        elif prop_type == 'checkbox':
            properties[prop_name] = prop_data['checkbox']
        
        elif prop_type == 'url':
            properties[prop_name] = prop_data['url']
        
        elif prop_type == 'email':
            properties[prop_name] = prop_data['email']
        
        elif prop_type == 'phone_number':
            properties[prop_name] = prop_data['phone_number']
        
        elif prop_type == 'formula':
            formula_result = prop_data['formula']
            if formula_result['type'] == 'string':
                properties[prop_name] = formula_result['string']
            elif formula_result['type'] == 'number':
                properties[prop_name] = formula_result['number']
            elif formula_result['type'] == 'boolean':
                properties[prop_name] = formula_result['boolean']
        
        elif prop_type == 'relation':
            properties[prop_name] = [rel['id'] for rel in prop_data['relation']]
        
        elif prop_type == 'rollup':
            rollup = prop_data['rollup']
            if rollup['type'] == 'number':
                properties[prop_name] = rollup['number']
            elif rollup['type'] == 'array':
                properties[prop_name] = rollup['array']
    
    return properties
```

### Sync with Filters

```python
def sync_filtered_content(connector, dataset, filters):
    """Sync content with complex filters."""
    
    # Example filters structure
    filters = {
        'databases': {
            'database_id_1': {
                'filter': {
                    'and': [
                        {
                            'property': 'Status',
                            'select': {'equals': 'Published'}
                        },
                        {
                            'property': 'Tags',
                            'multi_select': {'contains': 'Important'}
                        }
                    ]
                },
                'sorts': [
                    {'property': 'Updated', 'direction': 'descending'}
                ]
            }
        },
        'pages': {
            'parent_ids': ['page_id_1', 'page_id_2'],
            'recursive': True
        }
    }
    
    imported_count = 0
    
    # Sync databases
    for db_id, db_filter in filters.get('databases', {}).items():
        entries = connector.query_database(
            database_id=db_id,
            filter=db_filter.get('filter'),
            sorts=db_filter.get('sorts')
        )
        
        for entry in entries:
            record = connector.map_database_entry_to_record(entry)
            dataset.add(record)
            imported_count += 1
    
    # Sync pages
    page_config = filters.get('pages', {})
    for parent_id in page_config.get('parent_ids', []):
        pages = connector.get_child_pages(parent_id, 
                                         recursive=page_config.get('recursive', False))
        
        for page in pages:
            record = connector.map_to_frame_record(page)
            dataset.add(record)
            imported_count += 1
    
    return imported_count
```

### Comments and Mentions

```python
def import_with_comments(connector, dataset, page_id):
    """Import page with comments and discussions."""
    
    # Get page
    page = connector.get_page(page_id)
    page_record = connector.map_to_frame_record(page)
    dataset.add(page_record)
    
    # Get comments
    comments = connector.get_comments(page_id)
    
    for comment in comments:
        # Create comment record
        comment_record = FrameRecord.create(
            title=f"Comment on {page.title[:50]}",
            content=comment.rich_text[0].plain_text if comment.rich_text else "",
            author=comment.created_by.name if comment.created_by else "Unknown",
            created_at=comment.created_time,
            source_type="notion",
            tags=["comment", "discussion"],
            custom_metadata={
                "notion_comment_id": comment.id,
                "notion_page_id": page_id,
                "notion_discussion_id": comment.discussion_id,
                "notion_parent_id": comment.parent_id
            }
        )
        
        # Link to page
        comment_record.add_relationship(
            page_record.uuid,
            "child",
            title="Comment on page"
        )
        
        # Link to parent comment if reply
        if comment.parent_id:
            parent_comments = dataset.scanner(
                filter=f"custom_metadata.notion_comment_id = '{comment.parent_id}'"
            ).to_table().to_pylist()
            
            if parent_comments:
                comment_record.add_relationship(
                    parent_comments[0]['uuid'],
                    "child",
                    title="Reply to comment"
                )
        
        dataset.add(comment_record)
```

## Data Mapping

### Page to FrameRecord

```python
def map_to_frame_record(self, notion_page):
    """Map Notion page to FrameRecord."""
    
    # Extract content
    content_extractor = NotionContentExtractor(self)
    content = content_extractor.extract_page_content(notion_page.id)
    
    # Extract properties
    properties = extract_database_properties(notion_page)
    
    # Get title
    title = properties.get('title', properties.get('Name', 'Untitled'))
    
    # Build metadata
    metadata = {
        "notion_page_id": notion_page.id,
        "notion_url": notion_page.url,
        "notion_created_time": notion_page.created_time,
        "notion_last_edited_time": notion_page.last_edited_time,
        "notion_created_by": notion_page.created_by.id if notion_page.created_by else None,
        "notion_last_edited_by": notion_page.last_edited_by.id if notion_page.last_edited_by else None,
        "notion_parent_type": notion_page.parent.type,
        "notion_parent_id": self.get_parent_id(notion_page.parent),
        "notion_archived": notion_page.archived,
        "notion_properties": properties
    }
    
    # Handle cover and icon
    if notion_page.cover:
        metadata['notion_cover_url'] = self.get_file_url(notion_page.cover)
    
    if notion_page.icon:
        if notion_page.icon.type == 'emoji':
            metadata['notion_icon_emoji'] = notion_page.icon.emoji
        else:
            metadata['notion_icon_url'] = self.get_file_url(notion_page.icon)
    
    # Generate tags
    tags = ["notion"]
    
    # Add property-based tags
    if 'Tags' in properties:
        tags.extend(properties['Tags'] if isinstance(properties['Tags'], list) else [properties['Tags']])
    
    if 'Status' in properties:
        tags.append(f"status:{properties['Status'].lower()}")
    
    if notion_page.parent.type == 'database_id':
        tags.append("database-entry")
    else:
        tags.append("page")
    
    return FrameRecord.create(
        title=title,
        content=content,
        author=self.get_user_name(notion_page.created_by),
        created_at=notion_page.created_time,
        updated_at=notion_page.last_edited_time,
        source_url=notion_page.url,
        source_type="notion",
        tags=tags,
        custom_metadata=metadata
    )
```

### Database Schema Mapping

```python
class NotionDatabaseMapper:
    """Map Notion database to structured data."""
    
    def __init__(self, connector):
        self.connector = connector
    
    def map_database_schema(self, database_id):
        """Extract database schema information."""
        database = self.connector.get_database(database_id)
        
        schema = {
            'id': database.id,
            'title': database.title[0].plain_text if database.title else 'Untitled',
            'properties': {},
            'description': database.description[0].plain_text if database.description else ''
        }
        
        # Map property schemas
        for prop_name, prop_config in database.properties.items():
            prop_type = prop_config['type']
            
            schema['properties'][prop_name] = {
                'type': prop_type,
                'id': prop_config['id']
            }
            
            # Add type-specific configuration
            if prop_type == 'select':
                schema['properties'][prop_name]['options'] = [
                    {
                        'name': opt['name'],
                        'color': opt['color']
                    }
                    for opt in prop_config['select']['options']
                ]
            
            elif prop_type == 'multi_select':
                schema['properties'][prop_name]['options'] = [
                    {
                        'name': opt['name'],
                        'color': opt['color']
                    }
                    for opt in prop_config['multi_select']['options']
                ]
            
            elif prop_type == 'relation':
                schema['properties'][prop_name]['database_id'] = prop_config['relation']['database_id']
                schema['properties'][prop_name]['type'] = prop_config['relation'].get('type', 'single_property')
        
        return schema
    
    def create_collection_from_database(self, dataset, database_id):
        """Create a collection from Notion database."""
        schema = self.map_database_schema(database_id)
        
        # Create collection header
        collection_record = FrameRecord.create(
            title=schema['title'],
            content=schema['description'],
            record_type="collection_header",
            collection=f"notion-db-{database_id[:8]}",
            source_type="notion",
            tags=["notion-database", "collection"],
            custom_metadata={
                "notion_database_id": database_id,
                "notion_database_schema": schema['properties']
            }
        )
        
        dataset.add(collection_record)
        
        return collection_record, schema
```

## Sync Strategies

### Incremental Updates

```python
def incremental_sync_notion(connector, dataset, last_sync_time=None):
    """Sync only changed content since last sync."""
    
    from datetime import datetime, timezone
    
    if not last_sync_time:
        # Default to last 24 hours
        last_sync_time = datetime.now(timezone.utc).isoformat()
    
    # Search for recently edited pages
    results = connector.search(
        filter={
            "property": "object",
            "value": "page"
        },
        sort={
            "direction": "descending",
            "timestamp": "last_edited_time"
        }
    )
    
    updated_count = 0
    new_count = 0
    
    for page in results:
        if page.last_edited_time <= last_sync_time:
            break  # Pages are sorted by edit time
        
        # Check if exists
        existing = dataset.scanner(
            filter=f"custom_metadata.notion_page_id = '{page.id}'"
        ).to_table().to_pylist()
        
        record = connector.map_to_frame_record(page)
        
        if existing:
            dataset.update_record(existing[0]['uuid'], record)
            updated_count += 1
        else:
            dataset.add(record)
            new_count += 1
    
    return new_count, updated_count
```

### Workspace Monitoring

```python
class NotionWorkspaceMonitor:
    """Monitor Notion workspace for changes."""
    
    def __init__(self, connector, dataset):
        self.connector = connector
        self.dataset = dataset
        self.known_pages = set()
        self._load_known_pages()
    
    def _load_known_pages(self):
        """Load known page IDs from dataset."""
        for batch in self.dataset.to_batches(columns=['custom_metadata']):
            for row in batch.to_pylist():
                page_id = row['custom_metadata'].get('notion_page_id')
                if page_id:
                    self.known_pages.add(page_id)
    
    def check_for_changes(self):
        """Check for new, updated, and deleted pages."""
        current_pages = {}
        
        # Get all current pages
        results = self.connector.search()
        
        for page in results:
            current_pages[page.id] = page
        
        # Find changes
        current_ids = set(current_pages.keys())
        
        new_pages = current_ids - self.known_pages
        deleted_pages = self.known_pages - current_ids
        potentially_updated = current_ids & self.known_pages
        
        # Check for actual updates
        updated_pages = []
        for page_id in potentially_updated:
            page = current_pages[page_id]
            
            # Get existing record
            existing = self.dataset.scanner(
                filter=f"custom_metadata.notion_page_id = '{page_id}'"
            ).to_table().to_pylist()
            
            if existing:
                last_edited = existing[0]['custom_metadata'].get('notion_last_edited_time')
                if last_edited and page.last_edited_time > last_edited:
                    updated_pages.append(page)
        
        return {
            'new': [current_pages[id] for id in new_pages],
            'updated': updated_pages,
            'deleted': list(deleted_pages)
        }
    
    def sync_changes(self):
        """Sync all detected changes."""
        changes = self.check_for_changes()
        
        # Add new pages
        for page in changes['new']:
            record = self.connector.map_to_frame_record(page)
            self.dataset.add(record)
            self.known_pages.add(page.id)
            print(f"Added: {page.title}")
        
        # Update existing pages
        for page in changes['updated']:
            existing = self.dataset.scanner(
                filter=f"custom_metadata.notion_page_id = '{page.id}'"
            ).to_table().to_pylist()
            
            if existing:
                record = self.connector.map_to_frame_record(page)
                self.dataset.update_record(existing[0]['uuid'], record)
                print(f"Updated: {page.title}")
        
        # Handle deletions
        for page_id in changes['deleted']:
            existing = self.dataset.scanner(
                filter=f"custom_metadata.notion_page_id = '{page_id}'"
            ).to_table().to_pylist()
            
            if existing:
                self.dataset.delete_record(existing[0]['uuid'])
                self.known_pages.remove(page_id)
                print(f"Deleted: {existing[0]['title']}")
        
        return len(changes['new']), len(changes['updated']), len(changes['deleted'])
```

## Search and Analytics

### Cross-Database Search

```python
def search_across_databases(connector, query, database_ids):
    """Search across multiple Notion databases."""
    
    all_results = []
    
    for db_id in database_ids:
        # Search in database
        results = connector.query_database(
            database_id=db_id,
            filter={
                'or': [
                    {
                        'property': 'Name',
                        'title': {'contains': query}
                    },
                    {
                        'property': 'Description',
                        'rich_text': {'contains': query}
                    },
                    {
                        'property': 'Content',
                        'rich_text': {'contains': query}
                    }
                ]
            }
        )
        
        all_results.extend(results)
    
    return all_results
```

### Content Analytics

```python
def analyze_notion_content(dataset):
    """Analyze imported Notion content."""
    
    analytics = {
        'total_pages': 0,
        'by_type': {},
        'by_author': {},
        'by_status': {},
        'databases': {},
        'update_frequency': []
    }
    
    # Scan all Notion content
    scanner = dataset.scanner(
        filter="source_type = 'notion'"
    )
    
    for batch in scanner.to_batches():
        for row in batch.to_pylist():
            analytics['total_pages'] += 1
            metadata = row.get('custom_metadata', {})
            
            # Type distribution
            if metadata.get('notion_parent_type') == 'database_id':
                page_type = 'database_entry'
            else:
                page_type = 'page'
            
            analytics['by_type'][page_type] = analytics['by_type'].get(page_type, 0) + 1
            
            # Author distribution
            author = row.get('author', 'Unknown')
            analytics['by_author'][author] = analytics['by_author'].get(author, 0) + 1
            
            # Status distribution (from properties)
            properties = metadata.get('notion_properties', {})
            status = properties.get('Status', 'No Status')
            analytics['by_status'][status] = analytics['by_status'].get(status, 0) + 1
            
            # Database distribution
            if metadata.get('notion_parent_type') == 'database_id':
                db_id = metadata.get('notion_parent_id')
                analytics['databases'][db_id] = analytics['databases'].get(db_id, 0) + 1
            
            # Update frequency
            created = metadata.get('notion_created_time')
            edited = metadata.get('notion_last_edited_time')
            if created and edited:
                # Calculate days between creation and last edit
                from datetime import datetime
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                edited_dt = datetime.fromisoformat(edited.replace('Z', '+00:00'))
                days_active = (edited_dt - created_dt).days
                analytics['update_frequency'].append(days_active)
    
    # Calculate averages
    if analytics['update_frequency']:
        analytics['avg_days_active'] = sum(analytics['update_frequency']) / len(analytics['update_frequency'])
    
    return analytics
```

## Integration Patterns

### Notion + Linear Integration

```python
def sync_notion_to_linear(notion_connector, linear_connector, database_id, team_id):
    """Sync Notion database to Linear issues."""
    
    # Get Notion entries
    entries = notion_connector.query_database(
        database_id=database_id,
        filter={
            'property': 'Sync to Linear',
            'checkbox': {'equals': True}
        }
    )
    
    for entry in entries:
        properties = extract_database_properties(entry)
        
        # Check if already synced
        linear_id = properties.get('Linear ID')
        
        if linear_id:
            # Update existing issue
            linear_connector.update_issue(
                issue_id=linear_id,
                title=properties.get('Name'),
                description=properties.get('Description'),
                state_id=map_status_to_linear(properties.get('Status'))
            )
        else:
            # Create new issue
            issue = linear_connector.create_issue(
                team_id=team_id,
                title=properties.get('Name'),
                description=properties.get('Description'),
                priority=map_priority_to_linear(properties.get('Priority'))
            )
            
            # Update Notion with Linear ID
            notion_connector.update_page(
                page_id=entry.id,
                properties={
                    'Linear ID': {
                        'rich_text': [{
                            'text': {'content': issue.id}
                        }]
                    },
                    'Linear URL': {
                        'url': issue.url
                    }
                }
            )
```

### Knowledge Base Export

```python
def export_notion_kb_to_markdown(connector, dataset, root_page_id, output_dir):
    """Export Notion knowledge base to markdown files."""
    
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    def export_page(page_id, parent_path=""):
        """Export a single page and its children."""
        page = connector.get_page(page_id)
        properties = extract_database_properties(page)
        title = properties.get('title', 'Untitled')
        
        # Clean title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        safe_title = safe_title[:50]
        
        # Extract content
        extractor = NotionContentExtractor(connector)
        content = extractor.extract_page_content(page_id)
        
        # Write to file
        file_path = output_path / parent_path / f"{safe_title}.md"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Exported: {file_path}")
        
        # Export child pages
        children = connector.get_child_pages(page_id)
        if children:
            child_dir = parent_path / safe_title
            for child in children:
                export_page(child.id, child_dir)
    
    # Start export
    export_page(root_page_id)
```

## Performance Optimization

### Batch Operations

```python
def batch_import_database(connector, dataset, database_id, batch_size=100):
    """Import large database with batching."""
    
    has_more = True
    start_cursor = None
    total_imported = 0
    
    while has_more:
        # Query batch
        response = connector.query_database(
            database_id=database_id,
            page_size=batch_size,
            start_cursor=start_cursor
        )
        
        entries = response['results']
        has_more = response['has_more']
        start_cursor = response.get('next_cursor')
        
        # Process batch
        records = []
        for entry in entries:
            record = connector.map_database_entry_to_record(entry)
            records.append(record)
        
        # Batch insert
        dataset.add_many(records)
        total_imported += len(records)
        
        print(f"Imported batch: {len(records)} entries (total: {total_imported})")
    
    return total_imported
```

### Caching

```python
class CachedNotionConnector(NotionConnector):
    """Notion connector with caching."""
    
    def __init__(self, cache_ttl=300, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    def _cache_key(self, method, *args):
        """Generate cache key."""
        import hashlib
        key_str = f"{method}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_page(self, page_id, use_cache=True):
        """Get page with caching."""
        if not use_cache:
            return super().get_page(page_id)
        
        cache_key = self._cache_key('get_page', page_id)
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        
        # Fetch and cache
        page = super().get_page(page_id)
        self.cache[cache_key] = (page, time.time())
        
        return page
```

## Error Handling

### Rate Limiting

```python
import time
from typing import Callable
import random

def handle_rate_limit(func: Callable, max_retries=3):
    """Handle Notion API rate limits."""
    
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "rate_limited" in str(e):
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    raise
        
        raise Exception(f"Failed after {max_retries} retries")
    
    return wrapper

# Usage
@handle_rate_limit
def get_page_with_retry(connector, page_id):
    return connector.get_page(page_id)
```

### Invalid Block Handling

```python
def safe_block_extraction(connector, block_id):
    """Safely extract block content."""
    
    try:
        block = connector.get_block(block_id)
        
        # Handle unsupported block types
        unsupported_types = ['embed', 'bookmark', 'link_preview']
        if block['type'] in unsupported_types:
            return f"[{block['type'].upper()} - Content not extracted]"
        
        # Extract content based on type
        return extract_block_content(block)
        
    except Exception as e:
        error_msg = str(e)
        
        if "block_not_found" in error_msg:
            return "[Block deleted or inaccessible]"
        elif "validation_error" in error_msg:
            return "[Invalid block format]"
        else:
            return f"[Error extracting block: {error_msg}]"
```

## Best Practices

### 1. API Key Security

```python
# Use environment variables
api_key = os.getenv("NOTION_API_KEY")
if not api_key:
    raise ValueError("NOTION_API_KEY not set")

# For production, use secret management
from your_secret_manager import get_secret
api_key = get_secret("notion/api_key")
```

### 2. Efficient Queries

```python
# Good - filter at API level
results = connector.query_database(
    database_id=db_id,
    filter={
        'property': 'Status',
        'select': {'equals': 'Published'}
    },
    page_size=100  # Get more per request
)

# Bad - filter after fetching
all_entries = connector.query_database(database_id=db_id)
published = [e for e in all_entries if e.properties['Status']['select']['name'] == 'Published']
```

### 3. Content Preservation

```python
def preserve_notion_formatting(rich_text):
    """Preserve Notion's rich text formatting."""
    
    formatted_parts = []
    
    for text_obj in rich_text:
        text = text_obj['plain_text']
        annotations = text_obj.get('annotations', {})
        
        # Build format string
        if annotations.get('bold') and annotations.get('italic'):
            text = f"***{text}***"
        elif annotations.get('bold'):
            text = f"**{text}**"
        elif annotations.get('italic'):
            text = f"*{text}*"
        
        if annotations.get('code'):
            text = f"`{text}`"
        
        if annotations.get('underline'):
            text = f"<u>{text}</u>"
        
        if annotations.get('strikethrough'):
            text = f"~~{text}~~"
        
        # Handle colors
        if annotations.get('color') != 'default':
            color = annotations['color']
            text = f'<span style="color: {color}">{text}</span>'
        
        formatted_parts.append(text)
    
    return ''.join(formatted_parts)
```

## Troubleshooting

### Authentication Issues

```python
# Test authentication
try:
    connector.authenticate()
    # Try a simple API call
    users = connector.notion.users.list()
    print(f"Authenticated successfully. Found {len(users['results'])} users.")
except Exception as e:
    print(f"Authentication failed: {e}")
    print("Check:")
    print("1. API key is valid")
    print("2. Integration has access to workspace")
    print("3. Pages are shared with integration")
```

### Permission Errors

```python
def diagnose_permission_error(error):
    """Diagnose Notion permission errors."""
    
    error_str = str(error)
    
    if "unauthorized" in error_str:
        return "Integration doesn't have access. Share the page/database with your integration."
    
    elif "restricted_resource" in error_str:
        return "This resource is restricted. Check workspace settings."
    
    elif "object_not_found" in error_str:
        return "Page/database not found or not shared with integration."
    
    elif "validation_error" in error_str:
        return "Invalid request format. Check API parameters."
    
    return f"Unknown error: {error_str}"
```

## Next Steps

- Explore other connectors:
  - [Slack Connector](slack.md) for conversations
  - [Google Drive Connector](google-drive.md) for documents
  - [Discord Connector](discord.md) for community content
- Learn about [Custom Connectors](custom.md)
- See [Cookbook Examples](../cookbook/notion-sync.md)
- Check the [API Reference](../api/connectors.md#notion)