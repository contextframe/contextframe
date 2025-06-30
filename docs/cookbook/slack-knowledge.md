# Slack Community Knowledge

Build a searchable knowledge base from Slack workspace conversations, capturing community wisdom, answered questions, and shared resources.

## Problem Statement

Valuable knowledge shared in Slack conversations gets lost in the message history. Community members repeatedly ask the same questions, and finding previous discussions or shared resources becomes increasingly difficult as the workspace grows.

## Solution Overview

We'll build a Slack knowledge system that:
1. Archives important conversations and threads
2. Extracts Q&A pairs and solutions
3. Identifies key resources and links
4. Creates searchable documentation from discussions
5. Tracks topic evolution over time

## Complete Code

```python
import os
import re
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pandas as pd

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class SlackKnowledgeExtractor:
    """Extract and organize knowledge from Slack workspaces."""
    
    def __init__(self, slack_token: str, dataset_path: str = "slack_knowledge.lance"):
        """Initialize Slack knowledge extractor."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        self.client = WebClient(token=slack_token)
        
        # Patterns for identifying valuable content
        self.qa_patterns = [
            r"(?:how|what|why|when|where|can|could|should|would)\s+.*\?",
            r"(?:anyone know|does anyone|has anyone|is there)",
            r"(?:problem|issue|error|bug).*(?:solved|fixed|resolved)",
            r"(?:solution|answer|fix|workaround):\s*(.+)"
        ]
        
        self.resource_patterns = [
            r"https?://[^\s<>\"{}|\\^`\[\]]+",
            r"(?:doc|documentation|guide|tutorial|article).*?(?:here|at|:)\s*(.+)",
            r"(?:repo|repository|github|gitlab).*?(?:here|at|:)\s*(.+)"
        ]
        
        # Track processed messages
        self.processed_messages = set()
        
    def index_channel(self, channel_id: str, 
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     min_reactions: int = 2) -> List[FrameRecord]:
        """Index messages from a Slack channel."""
        print(f"Indexing Slack channel: {channel_id}")
        
        try:
            # Get channel info
            channel_info = self.client.conversations_info(channel=channel_id)
            channel_name = channel_info['channel']['name']
            
            # Create channel header
            channel_header = self._create_channel_header(channel_info['channel'])
            self.dataset.add(channel_header)
            
            # Fetch messages
            messages = self._fetch_channel_messages(channel_id, start_date, end_date)
            
            # Process messages
            records = []
            threads_processed = set()
            
            for message in messages:
                # Skip if already processed
                msg_id = f"{channel_id}-{message['ts']}"
                if msg_id in self.processed_messages:
                    continue
                
                # Check if message is valuable
                if self._is_valuable_message(message, min_reactions):
                    # Process thread if it exists
                    if 'thread_ts' in message and message['thread_ts'] not in threads_processed:
                        thread_records = self._process_thread(
                            channel_id, 
                            message['thread_ts'],
                            channel_header.unique_id
                        )
                        records.extend(thread_records)
                        threads_processed.add(message['thread_ts'])
                    elif 'thread_ts' not in message:
                        # Process standalone message
                        record = self._process_message(
                            message, 
                            channel_id,
                            channel_name,
                            channel_header.unique_id
                        )
                        if record:
                            records.append(record)
                            self.dataset.add(record, generate_embedding=True)
                
                self.processed_messages.add(msg_id)
            
            print(f"Indexed {len(records)} valuable messages from {channel_name}")
            return records
            
        except SlackApiError as e:
            print(f"Error indexing channel {channel_id}: {e}")
            return []
    
    def _create_channel_header(self, channel: Dict[str, Any]) -> FrameRecord:
        """Create channel header record."""
        return FrameRecord(
            text_content=f"Slack Channel: {channel['name']}\\n\\n{channel.get('purpose', {}).get('value', '')}",
            metadata=create_metadata(
                title=f"#{channel['name']}",
                source="slack",
                channel_id=channel['id'],
                channel_name=channel['name'],
                purpose=channel.get('purpose', {}).get('value', ''),
                topic=channel.get('topic', {}).get('value', ''),
                created=datetime.fromtimestamp(channel['created']).isoformat(),
                is_archived=channel.get('is_archived', False),
                num_members=channel.get('num_members', 0)
            ),
            unique_id=generate_uuid(),
            record_type="collection_header"
        )
    
    def _fetch_channel_messages(self, channel_id: str,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch messages from channel."""
        messages = []
        
        # Convert dates to timestamps
        oldest = start_date.timestamp() if start_date else None
        latest = end_date.timestamp() if end_date else None
        
        try:
            # Paginate through messages
            cursor = None
            while True:
                response = self.client.conversations_history(
                    channel=channel_id,
                    oldest=oldest,
                    latest=latest,
                    cursor=cursor,
                    limit=200
                )
                
                messages.extend(response['messages'])
                
                if not response.get('has_more', False):
                    break
                    
                cursor = response.get('response_metadata', {}).get('next_cursor')
                
        except SlackApiError as e:
            print(f"Error fetching messages: {e}")
            
        return messages
    
    def _is_valuable_message(self, message: Dict[str, Any], min_reactions: int) -> bool:
        """Determine if message contains valuable knowledge."""
        # Check reactions
        reactions = message.get('reactions', [])
        total_reactions = sum(r['count'] for r in reactions)
        if total_reactions >= min_reactions:
            return True
            
        # Check for Q&A patterns
        text = message.get('text', '').lower()
        for pattern in self.qa_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check for resources
        for pattern in self.resource_patterns:
            if re.search(pattern, text):
                return True
                
        # Check if pinned
        if message.get('pinned'):
            return True
            
        return False
    
    def _process_thread(self, channel_id: str, thread_ts: str, 
                       channel_header_id: str) -> List[FrameRecord]:
        """Process an entire thread as a Q&A or discussion."""
        try:
            # Fetch thread messages
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )
            
            messages = response['messages']
            if len(messages) < 2:  # No real thread
                return []
            
            # Extract thread content
            thread_data = self._extract_thread_content(messages)
            
            # Create thread record
            thread_record = FrameRecord(
                text_content=thread_data['content'],
                metadata=create_metadata(
                    title=thread_data['title'],
                    source="slack_thread",
                    channel_id=channel_id,
                    thread_ts=thread_ts,
                    thread_type=thread_data['type'],
                    participants=thread_data['participants'],
                    message_count=len(messages),
                    has_solution=thread_data['has_solution'],
                    resources=thread_data['resources'],
                    tags=thread_data['tags'],
                    created_at=datetime.fromtimestamp(float(thread_ts)).isoformat()
                ),
                unique_id=generate_uuid(),
                record_type="document"
            )
            
            # Add relationship to channel
            thread_record.metadata = add_relationship_to_metadata(
                thread_record.metadata,
                create_relationship(
                    source_id=thread_record.unique_id,
                    target_id=channel_header_id,
                    relationship_type="member_of"
                )
            )
            
            self.dataset.add(thread_record, generate_embedding=True)
            
            # Process individual valuable messages
            records = [thread_record]
            for msg in messages[1:]:  # Skip first message (included in thread)
                if self._contains_solution(msg):
                    solution_record = self._create_solution_record(
                        msg, thread_record.unique_id, channel_id
                    )
                    records.append(solution_record)
                    self.dataset.add(solution_record, generate_embedding=True)
            
            return records
            
        except SlackApiError as e:
            print(f"Error processing thread: {e}")
            return []
    
    def _extract_thread_content(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract structured content from thread."""
        first_msg = messages[0]
        
        # Determine thread type
        thread_type = "discussion"
        if re.search(r"\?", first_msg.get('text', '')):
            thread_type = "question"
        elif any(word in first_msg.get('text', '').lower() 
                for word in ['issue', 'problem', 'error', 'bug']):
            thread_type = "troubleshooting"
        
        # Build content
        content_parts = [f"**Original Message:**\\n{first_msg.get('text', '')}\\n"]
        
        # Add replies
        content_parts.append("\\n**Discussion:**")
        for msg in messages[1:]:
            user_id = msg.get('user', 'Unknown')
            text = msg.get('text', '')
            content_parts.append(f"\\n- {user_id}: {text}")
        
        # Extract participants
        participants = list(set(msg.get('user', '') for msg in messages if msg.get('user')))
        
        # Check for solution
        has_solution = any(self._contains_solution(msg) for msg in messages)
        
        # Extract resources
        resources = []
        for msg in messages:
            resources.extend(self._extract_resources(msg.get('text', '')))
        
        # Generate title
        title = self._generate_thread_title(first_msg.get('text', ''), thread_type)
        
        # Extract tags
        tags = self._extract_tags(messages)
        
        return {
            'content': "\\n".join(content_parts),
            'title': title,
            'type': thread_type,
            'participants': participants,
            'has_solution': has_solution,
            'resources': list(set(resources)),
            'tags': tags
        }
    
    def _contains_solution(self, message: Dict[str, Any]) -> bool:
        """Check if message contains a solution."""
        indicators = [
            'solved', 'fixed', 'solution', 'answer', 'resolved',
            'works now', 'that worked', 'thanks', 'perfect'
        ]
        
        text = message.get('text', '').lower()
        
        # Check text
        if any(indicator in text for indicator in indicators):
            return True
            
        # Check reactions
        solution_reactions = ['white_check_mark', 'heavy_check_mark', 'thumbsup', 'tada']
        reactions = message.get('reactions', [])
        
        return any(r['name'] in solution_reactions for r in reactions)
    
    def _extract_resources(self, text: str) -> List[str]:
        """Extract URLs and resources from text."""
        resources = []
        
        # Extract URLs
        url_pattern = r'<(https?://[^|>]+)(?:\|[^>]+)?>'
        urls = re.findall(url_pattern, text)
        resources.extend(urls)
        
        # Also get plain URLs
        plain_url_pattern = r'(?<!<)https?://[^\s<>\"{}|\\^`\[\]]+'
        plain_urls = re.findall(plain_url_pattern, text)
        resources.extend(plain_urls)
        
        return resources
    
    def _generate_thread_title(self, first_message: str, thread_type: str) -> str:
        """Generate descriptive title for thread."""
        # Clean message
        clean_text = re.sub(r'<[^>]+>', '', first_message)  # Remove Slack formatting
        clean_text = clean_text.strip()
        
        # Truncate if needed
        if len(clean_text) > 100:
            clean_text = clean_text[:97] + "..."
            
        # Add type prefix
        prefix = {
            'question': "Q: ",
            'troubleshooting': "Issue: ",
            'discussion': "Discussion: "
        }.get(thread_type, "")
        
        return f"{prefix}{clean_text}"
    
    def _extract_tags(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract tags from messages."""
        tags = set()
        
        # Common technical terms to look for
        tech_terms = [
            'python', 'javascript', 'typescript', 'react', 'node', 'api',
            'database', 'sql', 'mongodb', 'redis', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'ci/cd', 'testing', 'deployment'
        ]
        
        for msg in messages:
            text = msg.get('text', '').lower()
            
            # Check for tech terms
            for term in tech_terms:
                if term in text:
                    tags.add(term)
            
            # Extract hashtags
            hashtags = re.findall(r'#(\w+)', text)
            tags.update(hashtags)
        
        return list(tags)
    
    def _create_solution_record(self, message: Dict[str, Any], 
                               thread_id: str, channel_id: str) -> FrameRecord:
        """Create a record for a solution message."""
        return FrameRecord(
            text_content=f"Solution:\\n\\n{message.get('text', '')}",
            metadata=create_metadata(
                title="Solution",
                source="slack_solution",
                channel_id=channel_id,
                message_ts=message['ts'],
                user=message.get('user'),
                reactions=[r['name'] for r in message.get('reactions', [])]
            ),
            unique_id=generate_uuid(),
            record_type="document"
        )
    
    def _process_message(self, message: Dict[str, Any], 
                        channel_id: str, channel_name: str,
                        channel_header_id: str) -> Optional[FrameRecord]:
        """Process standalone valuable message."""
        text = message.get('text', '')
        if not text:
            return None
        
        # Extract content
        resources = self._extract_resources(text)
        
        # Create record
        record = FrameRecord(
            text_content=text,
            metadata=create_metadata(
                title=self._generate_message_title(text),
                source="slack_message",
                channel_id=channel_id,
                channel_name=channel_name,
                message_ts=message['ts'],
                user=message.get('user'),
                resources=resources,
                reactions=[r['name'] for r in message.get('reactions', [])],
                is_pinned=message.get('pinned', False),
                created_at=datetime.fromtimestamp(float(message['ts'])).isoformat()
            ),
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Add relationship to channel
        record.metadata = add_relationship_to_metadata(
            record.metadata,
            create_relationship(
                source_id=record.unique_id,
                target_id=channel_header_id,
                relationship_type="member_of"
            )
        )
        
        return record
    
    def _generate_message_title(self, text: str) -> str:
        """Generate title for standalone message."""
        # Clean text
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = clean_text.strip()
        
        # Get first sentence or line
        sentences = re.split(r'[.!?\\n]', clean_text)
        if sentences:
            title = sentences[0].strip()
            if len(title) > 100:
                title = title[:97] + "..."
            return title
            
        return clean_text[:100]
    
    def search_solutions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for solutions to problems."""
        # Search with solution-focused filter
        results = self.dataset.search(
            query=query,
            filter={
                'or': [
                    {'metadata.has_solution': True},
                    {'metadata.source': 'slack_solution'},
                    {'metadata.thread_type': 'troubleshooting'}
                ]
            },
            limit=limit
        )
        
        return [self._format_solution_result(r) for r in results]
    
    def _format_solution_result(self, result: FrameRecord) -> Dict[str, Any]:
        """Format solution for display."""
        metadata = result.metadata.custom_metadata
        
        return {
            'title': result.metadata.title,
            'content': result.text_content,
            'channel': metadata.get('channel_name', 'Unknown'),
            'date': metadata.get('created_at', ''),
            'participants': metadata.get('participants', []),
            'resources': metadata.get('resources', []),
            'tags': metadata.get('tags', []),
            'url': self._generate_slack_url(
                metadata.get('channel_id'),
                metadata.get('thread_ts') or metadata.get('message_ts')
            )
        }
    
    def _generate_slack_url(self, channel_id: str, timestamp: str) -> str:
        """Generate Slack archive URL."""
        if not channel_id or not timestamp:
            return ""
            
        # Convert timestamp to message ID format
        msg_id = timestamp.replace('.', '')
        
        # This is a template - actual workspace URL needed
        return f"https://workspace.slack.com/archives/{channel_id}/p{msg_id}"
    
    def generate_faq(self, channel_id: Optional[str] = None, 
                    min_occurrences: int = 3) -> List[Dict[str, str]]:
        """Generate FAQ from frequently asked questions."""
        # Get questions
        filter_dict = {'metadata.thread_type': 'question'}
        if channel_id:
            filter_dict['metadata.channel_id'] = channel_id
            
        questions = self.dataset.filter(filter_dict)
        
        # Group similar questions
        question_groups = defaultdict(list)
        
        for q in questions:
            # Simple similarity - in production use embeddings
            key = self._normalize_question(q.text_content)
            question_groups[key].append(q)
        
        # Build FAQ
        faq = []
        for key, questions in question_groups.items():
            if len(questions) >= min_occurrences:
                # Find best answer
                best_q = max(questions, 
                           key=lambda x: x.metadata.custom_metadata.get('has_solution', False))
                
                faq.append({
                    'question': best_q.metadata.title,
                    'answer': self._extract_answer(best_q),
                    'frequency': len(questions),
                    'last_asked': max(q.metadata.custom_metadata.get('created_at', '') 
                                    for q in questions)
                })
        
        # Sort by frequency
        return sorted(faq, key=lambda x: x['frequency'], reverse=True)
    
    def _normalize_question(self, text: str) -> str:
        """Normalize question for grouping."""
        # Remove common words and punctuation
        stop_words = {'how', 'to', 'do', 'i', 'can', 'what', 'is', 'the', 'a', 'an'}
        
        words = re.findall(r'\w+', text.lower())
        key_words = [w for w in words if w not in stop_words]
        
        return ' '.join(sorted(key_words[:5]))  # Use first 5 key words
    
    def _extract_answer(self, question_record: FrameRecord) -> str:
        """Extract answer from question thread."""
        # In a real implementation, would fetch the thread
        # and extract the accepted answer
        return "See thread for complete solution and discussion."

# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = SlackKnowledgeExtractor(
        slack_token=os.getenv("SLACK_BOT_TOKEN"),
        dataset_path="slack_knowledge.lance"
    )
    
    # Index channels
    channels = ["C1234567890", "C0987654321"]  # Your channel IDs
    
    for channel_id in channels:
        # Index last 30 days of valuable messages
        extractor.index_channel(
            channel_id=channel_id,
            start_date=datetime.now() - timedelta(days=30),
            min_reactions=2
        )
    
    # Search for solutions
    results = extractor.search_solutions("docker deployment error")
    
    for result in results:
        print(f"\\nFound: {result['title']}")
        print(f"Channel: {result['channel']}")
        print(f"Tags: {', '.join(result['tags'])}")
        print(f"URL: {result['url']}")
    
    # Generate FAQ
    faq = extractor.generate_faq(min_occurrences=2)
    
    print("\\n## Frequently Asked Questions\\n")
    for item in faq[:10]:
        print(f"**Q: {item['question']}** (asked {item['frequency']} times)")
        print(f"A: {item['answer']}\\n")
```

## Key Concepts

### Message Value Detection

The system identifies valuable messages through:
- **Reaction count**: Messages with multiple reactions likely contain useful information
- **Q&A patterns**: Questions and their answers are preserved
- **Resource sharing**: Links and documentation references
- **Pinned messages**: Explicitly marked important content

### Thread Processing

Complete threads are captured as single units to preserve context:
- Original question or problem statement
- Full discussion with all participants
- Identified solutions or resolutions
- Related resources and links

### Knowledge Extraction

The system extracts structured information:
- **Technical tags**: Programming languages, tools, and technologies mentioned
- **Solution indicators**: Messages marked as solving the problem
- **Resource links**: Documentation, repositories, and external references
- **Participant expertise**: Who provided helpful answers

## Extensions

### Advanced Features

1. **Expert Identification**
   - Track who provides the most helpful answers
   - Build expertise profiles
   - Route new questions to experts

2. **Sentiment Analysis**
   - Detect frustration in problem reports
   - Identify particularly helpful responses
   - Track community health metrics

3. **Auto-Documentation**
   - Generate documentation from resolved issues
   - Create runbooks from troubleshooting threads
   - Build glossaries from explained terms

4. **Integration with Other Systems**
   - Link Slack discussions to GitHub issues
   - Connect to internal wikis
   - Export to documentation platforms

### Performance Optimization

1. **Incremental Updates**
   - Track last indexed timestamp per channel
   - Only process new messages
   - Handle message edits and deletions

2. **Parallel Processing**
   - Index multiple channels concurrently
   - Batch message processing
   - Async thread fetching

3. **Smart Filtering**
   - Skip bot messages (unless valuable)
   - Ignore simple reactions/acknowledgments
   - Focus on substantive discussions

## Best Practices

1. **Privacy and Compliance**
   - Respect channel privacy settings
   - Implement retention policies
   - Anonymize sensitive information
   - Get consent for public channels

2. **Content Quality**
   - Verify solutions actually work
   - Update outdated information
   - Mark deprecated solutions
   - Track solution effectiveness

3. **Search Optimization**
   - Use channel-specific vocabularies
   - Build synonym mappings
   - Index code snippets specially
   - Boost recent solutions

4. **Community Engagement**
   - Share knowledge extraction insights
   - Highlight valuable contributors
   - Encourage solution marking
   - Provide search interface to Slack

This Slack knowledge system transforms ephemeral conversations into a permanent, searchable knowledge base that grows with your community.