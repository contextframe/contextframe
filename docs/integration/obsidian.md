# Obsidian Connector

The Obsidian connector enables importing markdown notes, attachments, and vault structure from Obsidian vaults into ContextFrame. This guide covers local vault access, plugin integration, and preserving Obsidian's rich linking system.

## Overview

The Obsidian connector can import:
- Markdown notes with frontmatter
- Internal links and backlinks
- Tags and nested tags
- Attachments and embedded files
- Canvas files and graph data
- Daily notes and templates
- Plugin data and metadata
- Vault folder structure

## Installation

The Obsidian connector works with local file systems:

```bash
pip install "contextframe[connectors]"
# Additional dependencies for Obsidian features
pip install python-frontmatter markdown-it-py
```

```python
from contextframe.connectors import ObsidianConnector
```

## Authentication

### Local Vault Access

The Obsidian connector accesses vaults directly from the file system:

```python
connector = ObsidianConnector(
    vault_path="/path/to/your/obsidian/vault"
)
```

### Remote Vault Access (via Obsidian Sync)

For vaults synced to cloud storage:

```python
# Access via synced folder
connector = ObsidianConnector(
    vault_path="/Users/username/Dropbox/ObsidianVault"
)

# Or from iCloud Drive (macOS)
connector = ObsidianConnector(
    vault_path="/Users/username/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault"
)
```

## Basic Usage

### Import Entire Vault

```python
from contextframe import FrameDataset
from contextframe.connectors import ObsidianConnector

# Create dataset
dataset = FrameDataset.create("obsidian_vault.lance")

# Setup connector
connector = ObsidianConnector(
    vault_path="/path/to/vault"
)

# Authenticate (validates vault access)
connector.authenticate()

# Sync all notes
notes = connector.sync_notes()

# Convert to FrameRecords
for note in notes:
    record = connector.map_to_frame_record(note)
    dataset.add(record)

print(f"Imported {len(notes)} notes")
```

### Import with Filters

```python
# Import specific folders
notes = connector.sync_notes(
    folders=["Projects", "Areas/Work"],
    exclude_folders=["Archive", "Templates"]
)

# Import by tags
notes = connector.sync_notes(
    tags=["#important", "#active"],
    exclude_tags=["#archive", "#draft"]
)

# Import modified recently
from datetime import datetime, timedelta

notes = connector.sync_notes(
    modified_after=datetime.now() - timedelta(days=7)
)
```

### Preserve Vault Structure

```python
def import_vault_with_structure(connector, dataset):
    """Import vault preserving folder hierarchy."""
    
    # Get vault metadata
    vault_info = connector.get_vault_info()
    
    # Create vault header
    vault_record = FrameRecord.create(
        title=f"Obsidian Vault: {vault_info['name']}",
        content=f"Vault containing {vault_info['note_count']} notes",
        record_type="collection_header",
        collection=f"obsidian-{vault_info['name'].lower().replace(' ', '-')}",
        source_type="obsidian",
        tags=["obsidian-vault"],
        custom_metadata={
            "obsidian_vault_path": vault_info['path'],
            "obsidian_note_count": vault_info['note_count'],
            "obsidian_attachment_count": vault_info['attachment_count'],
            "obsidian_plugins": vault_info.get('plugins', [])
        }
    )
    dataset.add(vault_record)
    
    # Process folders recursively
    def process_folder(folder_path, parent_record=None):
        folder_notes = connector.sync_notes(folder=folder_path)
        
        for note in folder_notes:
            record = connector.map_to_frame_record(note)
            
            # Add vault relationship
            record.add_relationship(
                vault_record.uuid,
                "member_of",
                title=f"Note in {vault_info['name']}"
            )
            
            # Add folder relationship if nested
            if parent_record:
                record.add_relationship(
                    parent_record.uuid,
                    "child",
                    title=f"In folder {folder_path}"
                )
            
            dataset.add(record)
    
    # Start processing from root
    process_folder("/")
```

## Advanced Features

### Link Graph Preservation

```python
class ObsidianLinkGraph:
    """Build and preserve Obsidian's link graph."""
    
    def __init__(self, connector):
        self.connector = connector
        self.graph = {}
    
    def build_graph(self):
        """Build complete link graph from vault."""
        notes = self.connector.sync_notes()
        
        # First pass: collect all notes
        note_map = {note['path']: note for note in notes}
        
        # Second pass: extract links
        for note in notes:
            note_path = note['path']
            self.graph[note_path] = {
                'title': note['title'],
                'outgoing_links': [],
                'incoming_links': [],
                'tags': note.get('tags', [])
            }
            
            # Parse links from content
            links = self.extract_links(note['content'])
            
            for link in links:
                # Resolve link to actual file
                resolved_path = self.resolve_link(link, note_path)
                
                if resolved_path and resolved_path in note_map:
                    self.graph[note_path]['outgoing_links'].append({
                        'path': resolved_path,
                        'title': note_map[resolved_path]['title'],
                        'type': 'wiki_link'
                    })
                    
                    # Add backlink
                    if resolved_path not in self.graph:
                        self.graph[resolved_path] = {
                            'title': note_map[resolved_path]['title'],
                            'outgoing_links': [],
                            'incoming_links': [],
                            'tags': []
                        }
                    
                    self.graph[resolved_path]['incoming_links'].append({
                        'path': note_path,
                        'title': note['title'],
                        'type': 'backlink'
                    })
        
        return self.graph
    
    def extract_links(self, content):
        """Extract wiki links from markdown content."""
        import re
        
        # Match [[Link]] and [[Link|Alias]] patterns
        wiki_link_pattern = r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
        matches = re.findall(wiki_link_pattern, content)
        
        links = []
        for match in matches:
            link = match[0]
            alias = match[1] if match[1] else match[0]
            links.append({'link': link, 'alias': alias})
        
        # Also match markdown links
        md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        md_matches = re.findall(md_link_pattern, content)
        
        for text, url in md_matches:
            if not url.startswith(('http://', 'https://', 'mailto:')):
                links.append({'link': url, 'alias': text})
        
        return links
    
    def resolve_link(self, link_info, source_path):
        """Resolve a link to actual file path."""
        link = link_info['link']
        
        # Handle absolute paths
        if link.startswith('/'):
            return link + '.md' if not link.endswith('.md') else link
        
        # Handle relative paths
        source_dir = os.path.dirname(source_path)
        
        # Try with .md extension
        candidates = [
            os.path.join(source_dir, link + '.md'),
            os.path.join(source_dir, link),
            link + '.md',
            link
        ]
        
        for candidate in candidates:
            if self.connector.file_exists(candidate):
                return candidate
        
        return None
    
    def import_with_links(self, dataset):
        """Import notes with full link preservation."""
        graph = self.build_graph()
        note_uuid_map = {}
        
        # First pass: create all note records
        for path, node in graph.items():
            note = self.connector.get_note(path)
            record = self.connector.map_to_frame_record(note)
            
            # Add link metadata
            record.metadata['custom_metadata']['obsidian_links'] = {
                'outgoing': len(node['outgoing_links']),
                'incoming': len(node['incoming_links'])
            }
            
            dataset.add(record)
            note_uuid_map[path] = record.uuid
        
        # Second pass: create link relationships
        for path, node in graph.items():
            source_uuid = note_uuid_map[path]
            
            # Add outgoing links
            for link in node['outgoing_links']:
                target_path = link['path']
                if target_path in note_uuid_map:
                    source_record = dataset.get(source_uuid)
                    source_record.add_relationship(
                        note_uuid_map[target_path],
                        'reference',
                        title=f"Links to {link['title']}"
                    )
                    dataset.update_record(source_uuid, source_record)
```

### Tag Hierarchy

```python
class ObsidianTagProcessor:
    """Process Obsidian's nested tag system."""
    
    def extract_tag_hierarchy(self, notes):
        """Build tag hierarchy from notes."""
        tag_tree = {}
        
        for note in notes:
            # Get tags from frontmatter
            frontmatter_tags = note.get('frontmatter', {}).get('tags', [])
            
            # Get inline tags from content
            inline_tags = self.extract_inline_tags(note['content'])
            
            all_tags = frontmatter_tags + inline_tags
            
            for tag in all_tags:
                self.add_to_tag_tree(tag_tree, tag)
        
        return tag_tree
    
    def extract_inline_tags(self, content):
        """Extract #tags from content."""
        import re
        
        # Match #tag and #nested/tag patterns
        tag_pattern = r'#([a-zA-Z0-9_/\-]+)'
        matches = re.findall(tag_pattern, content)
        
        return [f"#{match}" for match in matches]
    
    def add_to_tag_tree(self, tree, tag):
        """Add tag to hierarchical tree."""
        # Remove # prefix
        tag = tag.lstrip('#')
        
        # Split nested tags
        parts = tag.split('/')
        
        current = tree
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {
                    'count': 0,
                    'full_tag': '#' + '/'.join(parts[:i+1]),
                    'children': {}
                }
            
            current[part]['count'] += 1
            current = current[part]['children']
    
    def create_tag_records(self, dataset, tag_tree, parent_record=None, prefix=''):
        """Create records for tag hierarchy."""
        for tag_name, tag_data in tag_tree.items():
            full_tag = tag_data['full_tag']
            
            # Create tag record
            tag_record = FrameRecord.create(
                title=f"Tag: {full_tag}",
                content=f"Tag used in {tag_data['count']} notes",
                record_type="tag",
                source_type="obsidian",
                tags=["obsidian-tag"],
                custom_metadata={
                    "obsidian_tag": full_tag,
                    "obsidian_tag_count": tag_data['count'],
                    "obsidian_tag_level": full_tag.count('/') + 1
                }
            )
            
            if parent_record:
                tag_record.add_relationship(
                    parent_record.uuid,
                    "child",
                    title=f"Subtag of {prefix}"
                )
            
            dataset.add(tag_record)
            
            # Process children
            if tag_data['children']:
                self.create_tag_records(
                    dataset,
                    tag_data['children'],
                    tag_record,
                    full_tag
                )
```

### Daily Notes Processing

```python
def process_daily_notes(connector, dataset):
    """Process Obsidian daily notes with special handling."""
    
    # Get daily notes settings
    daily_settings = connector.get_plugin_settings('daily-notes')
    date_format = daily_settings.get('format', 'YYYY-MM-DD')
    folder = daily_settings.get('folder', '/')
    
    # Get all daily notes
    daily_notes = connector.sync_notes(
        folder=folder,
        pattern=f"*{date_format}*"
    )
    
    # Sort by date
    daily_notes.sort(key=lambda n: extract_date_from_title(n['title'], date_format))
    
    # Create timeline
    for i, note in enumerate(daily_notes):
        record = connector.map_to_frame_record(note)
        
        # Add daily note metadata
        note_date = extract_date_from_title(note['title'], date_format)
        record.metadata['custom_metadata']['daily_note_date'] = note_date.isoformat()
        record.metadata['tags'].append('daily-note')
        
        # Link to previous/next
        if i > 0:
            prev_note = daily_notes[i-1]
            prev_record = find_record_by_path(dataset, prev_note['path'])
            if prev_record:
                record.add_relationship(
                    prev_record['uuid'],
                    'related',
                    title="Previous day"
                )
        
        if i < len(daily_notes) - 1:
            next_note = daily_notes[i+1]
            # Note: Would need to handle this after all imports
        
        dataset.add(record)

def extract_date_from_title(title, date_format):
    """Extract date from daily note title."""
    from datetime import datetime
    
    # Convert moment.js format to Python format
    py_format = date_format.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
    
    try:
        return datetime.strptime(title, py_format)
    except:
        # Try to extract date from anywhere in title
        import re
        date_pattern = r'(\d{4})-(\d{2})-(\d{2})'
        match = re.search(date_pattern, title)
        if match:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return datetime.now()
```

### Canvas Files

```python
def import_canvas_files(connector, dataset):
    """Import Obsidian canvas files."""
    
    canvas_files = connector.get_canvas_files()
    
    for canvas_path in canvas_files:
        canvas_data = connector.load_canvas(canvas_path)
        
        # Create canvas record
        canvas_record = FrameRecord.create(
            title=f"Canvas: {canvas_data['name']}",
            content=generate_canvas_description(canvas_data),
            record_type="canvas",
            source_type="obsidian",
            tags=["obsidian-canvas"],
            custom_metadata={
                "obsidian_canvas_nodes": len(canvas_data['nodes']),
                "obsidian_canvas_edges": len(canvas_data['edges']),
                "obsidian_canvas_data": canvas_data
            }
        )
        dataset.add(canvas_record)
        
        # Process canvas nodes
        for node in canvas_data['nodes']:
            if node['type'] == 'file':
                # Link to note
                note_path = node['file']
                note_record = find_record_by_path(dataset, note_path)
                
                if note_record:
                    canvas_record.add_relationship(
                        note_record['uuid'],
                        'reference',
                        title=f"Contains {note_path}"
                    )
            
            elif node['type'] == 'text':
                # Create text node record
                text_record = FrameRecord.create(
                    title=f"Canvas Text: {node.get('text', '')[:50]}...",
                    content=node.get('text', ''),
                    source_type="obsidian",
                    tags=["canvas-text"],
                    custom_metadata={
                        "obsidian_canvas_id": canvas_path,
                        "obsidian_node_id": node['id'],
                        "obsidian_node_position": {
                            'x': node.get('x', 0),
                            'y': node.get('y', 0)
                        }
                    }
                )
                
                text_record.add_relationship(
                    canvas_record.uuid,
                    'child',
                    title="Text in canvas"
                )
                
                dataset.add(text_record)

def generate_canvas_description(canvas_data):
    """Generate description of canvas contents."""
    nodes = canvas_data['nodes']
    edges = canvas_data['edges']
    
    file_nodes = [n for n in nodes if n['type'] == 'file']
    text_nodes = [n for n in nodes if n['type'] == 'text']
    
    description = f"""# {canvas_data['name']}

Canvas containing:
- {len(file_nodes)} file nodes
- {len(text_nodes)} text nodes  
- {len(edges)} connections

## Files Referenced
"""
    
    for node in file_nodes[:10]:  # Limit to first 10
        description += f"- {node['file']}\n"
    
    if len(file_nodes) > 10:
        description += f"- ... and {len(file_nodes) - 10} more files\n"
    
    return description
```

## Data Mapping

### Note to FrameRecord

```python
def map_to_frame_record(self, obsidian_note):
    """Map Obsidian note to FrameRecord."""
    
    # Parse frontmatter
    frontmatter = obsidian_note.get('frontmatter', {})
    
    # Extract content without frontmatter
    content = obsidian_note['content']
    if obsidian_note.get('has_frontmatter'):
        # Remove frontmatter from content
        content = content.split('---', 2)[2] if content.count('---') >= 2 else content
    
    # Build metadata
    metadata = {
        "obsidian_path": obsidian_note['path'],
        "obsidian_vault": obsidian_note['vault_name'],
        "obsidian_created": obsidian_note['created_at'],
        "obsidian_modified": obsidian_note['modified_at'],
        "obsidian_size": obsidian_note['size'],
        "obsidian_frontmatter": frontmatter,
        "obsidian_links_count": len(obsidian_note.get('links', [])),
        "obsidian_backlinks_count": len(obsidian_note.get('backlinks', [])),
        "obsidian_tags": obsidian_note.get('tags', [])
    }
    
    # Handle aliases
    if 'aliases' in frontmatter:
        aliases = frontmatter['aliases']
        if isinstance(aliases, str):
            aliases = [aliases]
        metadata['obsidian_aliases'] = aliases
    
    # Generate tags
    tags = ["obsidian-note"]
    
    # Add frontmatter tags
    if 'tags' in frontmatter:
        fm_tags = frontmatter['tags']
        if isinstance(fm_tags, str):
            fm_tags = [fm_tags]
        tags.extend(fm_tags)
    
    # Add inline tags
    inline_tags = self.extract_inline_tags(content)
    tags.extend(inline_tags)
    
    # Add folder as tag
    folder = os.path.dirname(obsidian_note['path'])
    if folder and folder != '.':
        tags.append(f"folder:{folder.replace('/', '-')}")
    
    # Determine title
    title = frontmatter.get('title', obsidian_note['title'])
    if not title:
        # Extract from first heading
        import re
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = heading_match.group(1) if heading_match else os.path.basename(obsidian_note['path'])
    
    return FrameRecord.create(
        title=title,
        content=content,
        author=frontmatter.get('author', 'Unknown'),
        created_at=obsidian_note['created_at'],
        updated_at=obsidian_note['modified_at'],
        source_type="obsidian",
        source_file=obsidian_note['path'],
        tags=list(set(tags)),  # Deduplicate
        status=frontmatter.get('status', 'published'),
        custom_metadata=metadata
    )
```

### Attachment Handling

```python
class ObsidianAttachmentProcessor:
    """Process Obsidian attachments and embeds."""
    
    def __init__(self, connector):
        self.connector = connector
    
    def process_attachments(self, dataset):
        """Import all vault attachments."""
        attachments = self.connector.get_attachments()
        
        for attachment in attachments:
            # Create attachment record
            att_record = FrameRecord.create(
                title=f"Attachment: {attachment['name']}",
                content=self.generate_attachment_description(attachment),
                source_type="obsidian",
                source_file=attachment['path'],
                tags=["obsidian-attachment", attachment['type']],
                custom_metadata={
                    "obsidian_attachment_path": attachment['path'],
                    "obsidian_attachment_type": attachment['type'],
                    "obsidian_attachment_size": attachment['size'],
                    "obsidian_attachment_referenced_by": attachment.get('referenced_by', [])
                }
            )
            
            # Handle images - extract text if possible
            if attachment['type'] in ['image/jpeg', 'image/png']:
                text = self.extract_image_text(attachment['full_path'])
                if text:
                    att_record.text_content += f"\n\nExtracted Text:\n{text}"
            
            dataset.add(att_record)
            
            # Link to referencing notes
            for ref_path in attachment.get('referenced_by', []):
                ref_record = find_record_by_path(dataset, ref_path)
                if ref_record:
                    ref_record.add_relationship(
                        att_record.uuid,
                        'reference',
                        title=f"Embeds {attachment['name']}"
                    )
    
    def generate_attachment_description(self, attachment):
        """Generate description for attachment."""
        desc = f"# {attachment['name']}\n\n"
        desc += f"Type: {attachment['type']}\n"
        desc += f"Size: {attachment['size']} bytes\n"
        desc += f"Path: {attachment['path']}\n"
        
        if attachment.get('referenced_by'):
            desc += f"\n## Referenced By\n"
            for ref in attachment['referenced_by'][:10]:
                desc += f"- {ref}\n"
            
            if len(attachment['referenced_by']) > 10:
                desc += f"- ... and {len(attachment['referenced_by']) - 10} more notes\n"
        
        return desc
    
    def extract_image_text(self, image_path):
        """Extract text from images using OCR."""
        try:
            from PIL import Image
            import pytesseract
            
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text.strip()
        except:
            return None
```

## Sync Strategies

### Incremental Sync

```python
def incremental_sync_vault(connector, dataset, last_sync_file=".obsidian_sync_state.json"):
    """Incrementally sync Obsidian vault."""
    
    import json
    
    # Load last sync state
    sync_state = {}
    if os.path.exists(last_sync_file):
        with open(last_sync_file, 'r') as f:
            sync_state = json.load(f)
    
    last_sync_time = sync_state.get('last_sync')
    known_files = set(sync_state.get('known_files', []))
    
    # Get current vault state
    current_notes = connector.sync_notes()
    current_files = {note['path']: note for note in current_notes}
    
    # Detect changes
    current_paths = set(current_files.keys())
    
    new_files = current_paths - known_files
    deleted_files = known_files - current_paths
    potentially_modified = current_paths & known_files
    
    # Check for actual modifications
    modified_files = []
    if last_sync_time:
        last_sync_dt = datetime.fromisoformat(last_sync_time)
        for path in potentially_modified:
            note = current_files[path]
            if datetime.fromisoformat(note['modified_at']) > last_sync_dt:
                modified_files.append(path)
    
    # Process changes
    stats = {
        'new': len(new_files),
        'modified': len(modified_files),
        'deleted': len(deleted_files)
    }
    
    # Add new files
    for path in new_files:
        note = current_files[path]
        record = connector.map_to_frame_record(note)
        dataset.add(record)
    
    # Update modified files
    for path in modified_files:
        note = current_files[path]
        existing = dataset.scanner(
            filter=f"custom_metadata.obsidian_path = '{path}'"
        ).to_table().to_pylist()
        
        if existing:
            record = connector.map_to_frame_record(note)
            dataset.update_record(existing[0]['uuid'], record)
    
    # Handle deleted files
    for path in deleted_files:
        existing = dataset.scanner(
            filter=f"custom_metadata.obsidian_path = '{path}'"
        ).to_table().to_pylist()
        
        if existing:
            dataset.delete_record(existing[0]['uuid'])
    
    # Save sync state
    new_sync_state = {
        'last_sync': datetime.now().isoformat(),
        'known_files': list(current_paths),
        'stats': stats
    }
    
    with open(last_sync_file, 'w') as f:
        json.dump(new_sync_state, f)
    
    return stats
```

### Watch Mode

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ObsidianWatcher(FileSystemEventHandler):
    """Watch Obsidian vault for changes."""
    
    def __init__(self, connector, dataset):
        self.connector = connector
        self.dataset = dataset
        self.pending_changes = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.md'):
            # Debounce - Obsidian saves frequently
            self.pending_changes[event.src_path] = {
                'type': 'modified',
                'time': time.time()
            }
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.md'):
            self.pending_changes[event.src_path] = {
                'type': 'created',
                'time': time.time()
            }
    
    def on_deleted(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.md'):
            self.process_deletion(event.src_path)
    
    def process_deletion(self, path):
        """Process file deletion."""
        vault_path = os.path.relpath(path, self.connector.vault_path)
        
        existing = self.dataset.scanner(
            filter=f"custom_metadata.obsidian_path = '{vault_path}'"
        ).to_table().to_pylist()
        
        if existing:
            self.dataset.delete_record(existing[0]['uuid'])
            print(f"Deleted: {vault_path}")
    
    def process_pending_changes(self):
        """Process debounced changes."""
        current_time = time.time()
        processed = []
        
        for path, change in self.pending_changes.items():
            # Wait 2 seconds after last modification
            if current_time - change['time'] > 2:
                vault_path = os.path.relpath(path, self.connector.vault_path)
                
                try:
                    note = self.connector.get_note(vault_path)
                    record = self.connector.map_to_frame_record(note)
                    
                    if change['type'] == 'created':
                        self.dataset.add(record)
                        print(f"Added: {vault_path}")
                    else:
                        # Update existing
                        existing = self.dataset.scanner(
                            filter=f"custom_metadata.obsidian_path = '{vault_path}'"
                        ).to_table().to_pylist()
                        
                        if existing:
                            self.dataset.update_record(existing[0]['uuid'], record)
                            print(f"Updated: {vault_path}")
                        else:
                            self.dataset.add(record)
                            print(f"Added: {vault_path}")
                    
                    processed.append(path)
                    
                except Exception as e:
                    print(f"Error processing {vault_path}: {e}")
        
        # Remove processed changes
        for path in processed:
            del self.pending_changes[path]

def watch_vault(connector, dataset, vault_path):
    """Watch Obsidian vault for real-time updates."""
    event_handler = ObsidianWatcher(connector, dataset)
    observer = Observer()
    observer.schedule(event_handler, vault_path, recursive=True)
    observer.start()
    
    print(f"Watching vault: {vault_path}")
    
    try:
        while True:
            time.sleep(1)
            event_handler.process_pending_changes()
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
```

## Search and Analytics

### Link Analysis

```python
def analyze_vault_connections(dataset):
    """Analyze connection patterns in vault."""
    
    # Get all Obsidian notes
    notes = dataset.scanner(
        filter="source_type = 'obsidian' AND record_type != 'tag'"
    ).to_table().to_pylist()
    
    # Build connection statistics
    stats = {
        'total_notes': len(notes),
        'orphan_notes': [],
        'hub_notes': [],  # Many connections
        'most_linked': [],
        'tag_distribution': {},
        'folder_distribution': {}
    }
    
    link_counts = {}
    
    for note in notes:
        path = note['custom_metadata']['obsidian_path']
        links = note['custom_metadata'].get('obsidian_links_count', 0)
        backlinks = note['custom_metadata'].get('obsidian_backlinks_count', 0)
        
        total_connections = links + backlinks
        link_counts[path] = {
            'title': note['title'],
            'total': total_connections,
            'outgoing': links,
            'incoming': backlinks
        }
        
        # Identify orphans
        if total_connections == 0:
            stats['orphan_notes'].append({
                'title': note['title'],
                'path': path
            })
        
        # Identify hubs (top 10%)
        if total_connections > 10:  # Threshold
            stats['hub_notes'].append({
                'title': note['title'],
                'path': path,
                'connections': total_connections
            })
        
        # Tag distribution
        for tag in note.get('tags', []):
            if tag.startswith('#') or tag.startswith('obsidian'):
                continue
            stats['tag_distribution'][tag] = stats['tag_distribution'].get(tag, 0) + 1
        
        # Folder distribution
        folder = os.path.dirname(path)
        if folder:
            stats['folder_distribution'][folder] = stats['folder_distribution'].get(folder, 0) + 1
    
    # Find most linked notes
    stats['most_linked'] = sorted(
        link_counts.items(),
        key=lambda x: x[1]['incoming'],
        reverse=True
    )[:20]
    
    # Calculate averages
    if notes:
        total_links = sum(lc['total'] for lc in link_counts.values())
        stats['avg_connections_per_note'] = total_links / len(notes)
        stats['orphan_percentage'] = len(stats['orphan_notes']) / len(notes) * 100
    
    return stats
```

### Content Search

```python
def search_vault_content(dataset, query, search_type='all'):
    """Search Obsidian vault content."""
    
    base_filter = "source_type = 'obsidian'"
    
    if search_type == 'notes':
        base_filter += " AND custom_metadata.obsidian_path LIKE '%.md'"
    elif search_type == 'daily':
        base_filter += " AND tags.contains('daily-note')"
    elif search_type == 'tagged':
        base_filter += " AND array_length(tags) > 1"  # Has tags beyond default
    
    # Full text search
    results = dataset.full_text_search(
        query,
        filter=base_filter,
        limit=50
    )
    
    # Enhance results with backlink context
    enhanced_results = []
    
    for result in results.to_pylist():
        enhanced = result.copy()
        
        # Get backlinks to this note
        path = result['custom_metadata']['obsidian_path']
        backlinks = dataset.scanner(
            filter=f"source_type = 'obsidian' AND text_content LIKE '%{path}%'"
        ).to_table().to_pylist()
        
        enhanced['backlink_context'] = [
            {
                'title': bl['title'],
                'path': bl['custom_metadata']['obsidian_path']
            }
            for bl in backlinks[:5]  # Limit to 5
        ]
        
        enhanced_results.append(enhanced)
    
    return enhanced_results
```

## Integration Patterns

### Obsidian + GitHub Pages

```python
def export_vault_to_github_pages(connector, dataset, output_dir):
    """Export Obsidian vault for GitHub Pages."""
    
    from pathlib import Path
    import yaml
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create Jekyll-compatible structure
    (output_path / '_posts').mkdir(exist_ok=True)
    (output_path / 'assets').mkdir(exist_ok=True)
    (output_path / 'tags').mkdir(exist_ok=True)
    
    # Export notes
    notes = connector.sync_notes()
    
    for note in notes:
        # Skip private notes
        if note.get('frontmatter', {}).get('private', False):
            continue
        
        # Convert to Jekyll format
        jekyll_content = convert_to_jekyll(note)
        
        # Determine output path
        if is_blog_post(note):
            # Blog posts go in _posts with date prefix
            date = extract_post_date(note)
            filename = f"{date}-{slugify(note['title'])}.md"
            output_file = output_path / '_posts' / filename
        else:
            # Regular pages
            output_file = output_path / f"{slugify(note['title'])}.md"
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(jekyll_content)
    
    # Create tag pages
    all_tags = collect_all_tags(notes)
    for tag in all_tags:
        create_tag_page(output_path / 'tags', tag)
    
    # Create index
    create_index_page(output_path, notes)

def convert_to_jekyll(note):
    """Convert Obsidian note to Jekyll format."""
    # Update frontmatter
    frontmatter = note.get('frontmatter', {}).copy()
    frontmatter['layout'] = frontmatter.get('layout', 'post')
    frontmatter['title'] = note['title']
    
    # Convert tags format
    if 'tags' in frontmatter:
        tags = frontmatter['tags']
        if isinstance(tags, str):
            tags = [tags]
        frontmatter['tags'] = [tag.lstrip('#') for tag in tags]
    
    # Convert Obsidian links to Jekyll links
    content = note['content']
    content = convert_wiki_links_to_jekyll(content)
    
    # Build Jekyll post
    jekyll_post = "---\n"
    jekyll_post += yaml.dump(frontmatter, default_flow_style=False)
    jekyll_post += "---\n\n"
    jekyll_post += content
    
    return jekyll_post
```

### Knowledge Graph Visualization

```python
def export_knowledge_graph(dataset, output_file):
    """Export Obsidian knowledge graph for visualization."""
    
    import json
    
    # Get all notes and relationships
    notes = dataset.scanner(
        filter="source_type = 'obsidian'"
    ).to_table().to_pylist()
    
    # Build graph data
    nodes = []
    edges = []
    node_map = {}
    
    # Create nodes
    for i, note in enumerate(notes):
        node = {
            'id': i,
            'label': note['title'],
            'path': note['custom_metadata']['obsidian_path'],
            'tags': note.get('tags', []),
            'size': note['custom_metadata'].get('obsidian_links_count', 1) + 1
        }
        nodes.append(node)
        node_map[note['uuid']] = i
    
    # Create edges from relationships
    for note in notes:
        source_id = node_map[note['uuid']]
        
        for rel in note.get('relationships', []):
            if rel['target_uuid'] in node_map:
                target_id = node_map[rel['target_uuid']]
                
                edge = {
                    'source': source_id,
                    'target': target_id,
                    'type': rel['relationship_type'],
                    'label': rel.get('title', '')
                }
                edges.append(edge)
    
    # Export graph data
    graph_data = {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'total_notes': len(nodes),
            'total_connections': len(edges),
            'vault_name': notes[0]['custom_metadata']['obsidian_vault'] if notes else 'Unknown'
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(graph_data, f, indent=2)
    
    # Also create D3.js visualization
    create_d3_visualization(graph_data, output_file.replace('.json', '.html'))
```

## Performance Optimization

### Parallel Note Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_import_vault(connector, dataset, max_workers=4):
    """Import vault with parallel processing."""
    
    # Get all note paths
    note_paths = connector.list_note_paths()
    total = len(note_paths)
    
    processed = 0
    errors = []
    
    def process_note(path):
        try:
            note = connector.get_note(path)
            record = connector.map_to_frame_record(note)
            return record
        except Exception as e:
            return {'error': str(e), 'path': path}
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_path = {
            executor.submit(process_note, path): path
            for path in note_paths
        }
        
        # Collect results in batches
        batch = []
        batch_size = 100
        
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            result = future.result()
            
            if isinstance(result, dict) and 'error' in result:
                errors.append(result)
            else:
                batch.append(result)
            
            # Insert batch
            if len(batch) >= batch_size:
                dataset.add_many(batch)
                processed += len(batch)
                print(f"Processed {processed}/{total} notes")
                batch = []
        
        # Insert remaining
        if batch:
            dataset.add_many(batch)
            processed += len(batch)
    
    print(f"Import complete: {processed} succeeded, {len(errors)} failed")
    return processed, errors
```

### Metadata Caching

```python
class CachedObsidianConnector(ObsidianConnector):
    """Obsidian connector with metadata caching."""
    
    def __init__(self, vault_path, cache_file=".obsidian_cache.json"):
        super().__init__(vault_path)
        self.cache_file = os.path.join(vault_path, cache_file)
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Load metadata cache."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_cache(self):
        """Save metadata cache."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def get_note_metadata(self, path):
        """Get note metadata with caching."""
        # Check if file changed
        stat = os.stat(os.path.join(self.vault_path, path))
        mtime = stat.st_mtime
        
        cached = self.cache.get(path)
        if cached and cached['mtime'] == mtime:
            return cached['metadata']
        
        # Parse metadata
        metadata = super().get_note_metadata(path)
        
        # Update cache
        self.cache[path] = {
            'mtime': mtime,
            'metadata': metadata
        }
        
        return metadata
```

## Error Handling

### Permission Issues

```python
def check_vault_access(vault_path):
    """Check vault access permissions."""
    
    issues = []
    
    # Check if path exists
    if not os.path.exists(vault_path):
        issues.append(f"Vault path does not exist: {vault_path}")
        return issues
    
    # Check if it's a directory
    if not os.path.isdir(vault_path):
        issues.append(f"Vault path is not a directory: {vault_path}")
        return issues
    
    # Check read permission
    if not os.access(vault_path, os.R_OK):
        issues.append(f"No read permission for vault: {vault_path}")
    
    # Check for .obsidian folder
    obsidian_dir = os.path.join(vault_path, '.obsidian')
    if not os.path.exists(obsidian_dir):
        issues.append("No .obsidian folder found - might not be an Obsidian vault")
    
    # Try to list files
    try:
        files = os.listdir(vault_path)
        md_files = [f for f in files if f.endswith('.md')]
        if not md_files:
            issues.append("No markdown files found in vault")
    except Exception as e:
        issues.append(f"Cannot list vault contents: {e}")
    
    return issues
```

### Corrupted Note Handling

```python
def safe_parse_note(connector, path):
    """Safely parse potentially corrupted notes."""
    
    try:
        # Try normal parsing
        return connector.get_note(path)
    except Exception as e:
        # Fallback parsing
        full_path = os.path.join(connector.vault_path, path)
        
        try:
            # Read raw content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            # Try different encoding
            with open(full_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Create minimal note structure
        stat = os.stat(full_path)
        
        return {
            'path': path,
            'title': os.path.basename(path).replace('.md', ''),
            'content': content,
            'frontmatter': {},
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'size': stat.st_size,
            'vault_name': os.path.basename(connector.vault_path),
            'error': str(e)
        }
```

## Best Practices

### 1. Vault Path Security

```python
# Use absolute paths
vault_path = os.path.abspath(os.path.expanduser("~/Documents/ObsidianVault"))

# Validate path
if not os.path.exists(vault_path):
    raise ValueError(f"Vault not found: {vault_path}")

connector = ObsidianConnector(vault_path=vault_path)
```

### 2. Respect .obsidianignore

```python
def load_ignore_patterns(vault_path):
    """Load patterns from .obsidianignore."""
    ignore_file = os.path.join(vault_path, '.obsidianignore')
    patterns = []
    
    if os.path.exists(ignore_file):
        with open(ignore_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    
    return patterns

# Use in connector
connector.ignore_patterns = load_ignore_patterns(vault_path)
```

### 3. Preserve Obsidian Features

```python
def preserve_obsidian_features(note_content):
    """Preserve Obsidian-specific syntax."""
    
    # Preserve block references ^block-id
    # Preserve embeds ![[Note]]
    # Preserve queries ```query
    # Don't convert these to standard markdown
    
    preserved = note_content
    
    # Mark special syntax for preservation
    obsidian_patterns = [
        (r'\^\w+', 'OBSIDIAN_BLOCK_REF'),
        (r'!\[\[([^\]]+)\]\]', 'OBSIDIAN_EMBED'),
        (r'```query\n(.*?)\n```', 'OBSIDIAN_QUERY', re.DOTALL)
    ]
    
    return preserved
```

## Troubleshooting

### Vault Detection Issues

```python
# Diagnose vault issues
def diagnose_vault(path):
    """Diagnose Obsidian vault issues."""
    
    print(f"Checking vault: {path}")
    
    # Check path
    if not os.path.exists(path):
        print("❌ Path does not exist")
        return
    
    print("✓ Path exists")
    
    # Check .obsidian folder
    obsidian_dir = os.path.join(path, '.obsidian')
    if os.path.exists(obsidian_dir):
        print("✓ .obsidian folder found")
        
        # Check config
        config_file = os.path.join(obsidian_dir, 'config')
        if os.path.exists(config_file):
            print("✓ Config file found")
    else:
        print("❌ No .obsidian folder - might not be a vault")
    
    # Count notes
    md_files = list(Path(path).rglob("*.md"))
    print(f"✓ Found {len(md_files)} markdown files")
    
    # Check permissions
    if os.access(path, os.R_OK):
        print("✓ Read permission OK")
    else:
        print("❌ No read permission")
```

### Link Resolution Issues

```python
def debug_link_resolution(connector, source_note, link):
    """Debug why a link isn't resolving."""
    
    print(f"Resolving '{link}' from '{source_note}'")
    
    # Try different resolution strategies
    strategies = [
        ('exact', link),
        ('with_extension', f"{link}.md"),
        ('absolute', f"/{link}"),
        ('relative', os.path.join(os.path.dirname(source_note), link))
    ]
    
    for strategy_name, candidate in strategies:
        exists = connector.file_exists(candidate)
        print(f"  {strategy_name}: {candidate} -> {'✓' if exists else '✗'}")
    
    # Search for partial matches
    all_notes = connector.list_note_paths()
    matches = [n for n in all_notes if link.lower() in n.lower()]
    
    if matches:
        print(f"\nPossible matches:")
        for match in matches[:5]:
            print(f"  - {match}")
```

## Next Steps

- Explore other connectors:
  - [Notion Connector](notion.md) for cloud-based notes
  - [Google Drive Connector](google-drive.md) for documents
  - [GitHub Connector](github.md) for code documentation
- Learn about [Custom Connectors](custom.md)
- See [Cookbook Examples](../cookbook/obsidian-migration.md)
- Check the [API Reference](../api/connectors.md#obsidian)