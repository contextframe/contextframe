# Email Archive Search

Build a comprehensive email archive system that indexes, searches, and analyzes email communications for knowledge management, compliance, and discovery purposes.

## Problem Statement

Organizations accumulate vast email archives containing critical business knowledge, decisions, and communications. Finding specific information, tracking conversation threads, and ensuring compliance requires sophisticated search and analysis capabilities.

## Solution Overview

We'll build an email archive system that:
1. Imports emails from multiple sources (PST, MBOX, IMAP)
2. Preserves complete conversation threads
3. Extracts entities and attachments
4. Provides advanced search with filters
5. Enables compliance and e-discovery workflows

## Complete Code

```python
import os
import re
import email
import mailbox
import imaplib
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from collections import defaultdict
import mimetypes
from email.utils import parseaddr, parsedate_to_datetime
import chardet

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class EmailArchiveSystem:
    """Comprehensive email archive and search system."""
    
    def __init__(self, dataset_path: str = "email_archive.lance"):
        """Initialize email archive system."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Track processed emails by message ID
        self.processed_messages = set()
        
        # Entity patterns
        self.entity_patterns = {
            'phone': r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'case_number': r'\b(?:case|matter|file)\s*#?\s*(\d{4,})\b',
            'contract': r'\b(?:contract|agreement)\s*#?\s*(\w{2,}-\d{3,})\b'
        }
        
    def import_mbox(self, mbox_path: str, 
                   email_account: str = None) -> List[FrameRecord]:
        """Import emails from MBOX file."""
        print(f"Importing emails from {mbox_path}")
        
        records = []
        mbox = mailbox.mbox(mbox_path)
        
        for message in mbox:
            record = self._process_email(message, email_account)
            if record:
                records.append(record)
                self.dataset.add(record, generate_embedding=True)
        
        # Build conversation threads
        self._build_conversation_threads(records)
        
        print(f"Imported {len(records)} emails")
        return records
    
    def import_pst(self, pst_path: str, 
                  email_account: str = None) -> List[FrameRecord]:
        """Import emails from PST file."""
        # Note: Requires pypff or similar library
        # This is a simplified example
        print(f"Importing emails from {pst_path}")
        
        # In production, use pypff or libpst
        # This is placeholder logic
        records = []
        
        # Example PST processing would go here
        # pst = pypff.file()
        # pst.open(pst_path)
        # for folder in pst.root_folder.sub_folders:
        #     for message in folder.sub_messages:
        #         record = self._process_pst_message(message)
        #         ...
        
        return records
    
    def import_imap(self, server: str, username: str, 
                   password: str, folders: List[str] = None) -> List[FrameRecord]:
        """Import emails from IMAP server."""
        print(f"Connecting to {server}")
        
        records = []
        
        # Connect to IMAP
        imap = imaplib.IMAP4_SSL(server)
        imap.login(username, password)
        
        # Get folders to process
        if not folders:
            folders = ['INBOX', 'Sent']
        
        for folder in folders:
            print(f"Processing folder: {folder}")
            
            try:
                imap.select(folder)
                
                # Search for all emails
                _, message_ids = imap.search(None, 'ALL')
                
                for msg_id in message_ids[0].split():
                    # Fetch email
                    _, msg_data = imap.fetch(msg_id, '(RFC822)')
                    
                    # Parse email
                    email_body = msg_data[0][1]
                    message = email.message_from_bytes(email_body)
                    
                    # Process email
                    record = self._process_email(message, username, folder)
                    if record:
                        records.append(record)
                        self.dataset.add(record, generate_embedding=True)
                        
            except Exception as e:
                print(f"Error processing folder {folder}: {e}")
        
        imap.close()
        imap.logout()
        
        # Build conversation threads
        self._build_conversation_threads(records)
        
        return records
    
    def _process_email(self, message: email.message.Message, 
                      email_account: str = None,
                      folder: str = None) -> Optional[FrameRecord]:
        """Process individual email message."""
        # Get message ID
        message_id = message.get('Message-ID', '')
        if not message_id:
            # Generate one based on content
            content_hash = hashlib.md5(str(message).encode()).hexdigest()
            message_id = f"<generated-{content_hash}@archive>"
        
        # Skip if already processed
        if message_id in self.processed_messages:
            return None
        
        # Extract headers
        subject = message.get('Subject', 'No Subject')
        from_addr = parseaddr(message.get('From', ''))[1]
        to_addrs = self._extract_addresses(message.get('To', ''))
        cc_addrs = self._extract_addresses(message.get('CC', ''))
        date_str = message.get('Date', '')
        
        # Parse date
        try:
            email_date = parsedate_to_datetime(date_str)
        except:
            email_date = datetime.now()
        
        # Extract body
        body_text, body_html = self._extract_body(message)
        
        # Extract attachments
        attachments = self._extract_attachments(message)
        
        # Detect entities
        entities = self._detect_entities(body_text)
        
        # Extract thread info
        in_reply_to = message.get('In-Reply-To', '')
        references = message.get('References', '').split()
        
        # Create metadata
        metadata = create_metadata(
            title=subject,
            source="email",
            email_account=email_account,
            folder=folder,
            message_id=message_id,
            from_address=from_addr,
            to_addresses=to_addrs,
            cc_addresses=cc_addrs,
            date=email_date.isoformat(),
            in_reply_to=in_reply_to,
            references=references,
            thread_id=self._get_thread_id(message_id, references),
            has_attachments=len(attachments) > 0,
            attachment_names=[att['filename'] for att in attachments],
            attachment_types=[att['content_type'] for att in attachments],
            entities=entities,
            importance=message.get('Importance', 'normal'),
            size_bytes=len(str(message))
        )
        
        # Create record
        record = FrameRecord(
            text_content=f"Subject: {subject}\\n\\nFrom: {from_addr}\\nTo: {', '.join(to_addrs)}\\nDate: {email_date}\\n\\n{body_text}",
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        self.processed_messages.add(message_id)
        
        return record
    
    def _extract_addresses(self, addr_string: str) -> List[str]:
        """Extract email addresses from address string."""
        if not addr_string:
            return []
        
        addresses = []
        for addr in addr_string.split(','):
            parsed = parseaddr(addr.strip())
            if parsed[1]:
                addresses.append(parsed[1].lower())
        
        return addresses
    
    def _extract_body(self, message: email.message.Message) -> Tuple[str, str]:
        """Extract text and HTML body from email."""
        text_body = ""
        html_body = ""
        
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        # Detect encoding
                        encoding = chardet.detect(payload)['encoding'] or 'utf-8'
                        text_body += payload.decode(encoding, errors='ignore')
                        
                elif content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    if payload:
                        encoding = chardet.detect(payload)['encoding'] or 'utf-8'
                        html_body += payload.decode(encoding, errors='ignore')
        else:
            payload = message.get_payload(decode=True)
            if payload:
                encoding = chardet.detect(payload)['encoding'] or 'utf-8'
                text_body = payload.decode(encoding, errors='ignore')
        
        return text_body, html_body
    
    def _extract_attachments(self, message: email.message.Message) -> List[Dict[str, Any]]:
        """Extract attachment information."""
        attachments = []
        
        if message.is_multipart():
            for part in message.walk():
                disposition = part.get('Content-Disposition', '')
                
                if 'attachment' in disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type(),
                            'size': len(part.get_payload(decode=True) or b'')
                        })
        
        return attachments
    
    def _detect_entities(self, text: str) -> Dict[str, List[str]]:
        """Detect sensitive entities in email text."""
        entities = defaultdict(list)
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type].extend(matches)
        
        return dict(entities)
    
    def _get_thread_id(self, message_id: str, references: List[str]) -> str:
        """Determine thread ID for email."""
        # Use first reference as thread ID, or message ID if no references
        if references:
            return references[0]
        return message_id
    
    def _build_conversation_threads(self, records: List[FrameRecord]):
        """Build conversation thread relationships."""
        # Group by thread ID
        threads = defaultdict(list)
        
        for record in records:
            thread_id = record.metadata.custom_metadata.get('thread_id')
            if thread_id:
                threads[thread_id].append(record)
        
        # Create relationships within threads
        for thread_id, thread_records in threads.items():
            if len(thread_records) > 1:
                # Sort by date
                thread_records.sort(
                    key=lambda x: x.metadata.custom_metadata.get('date', '')
                )
                
                # Link each email to previous in thread
                for i in range(1, len(thread_records)):
                    current = thread_records[i]
                    previous = thread_records[i-1]
                    
                    current.metadata = add_relationship_to_metadata(
                        current.metadata,
                        create_relationship(
                            source_id=current.unique_id,
                            target_id=previous.unique_id,
                            relationship_type="reference",
                            properties={'reference_type': 'in_reply_to'}
                        )
                    )
    
    def search_emails(self, query: str, 
                     from_address: Optional[str] = None,
                     to_address: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     has_attachments: Optional[bool] = None,
                     folder: Optional[str] = None) -> List[FrameRecord]:
        """Search emails with advanced filters."""
        # Build filter
        filter_dict = {}
        
        if from_address:
            filter_dict['metadata.from_address'] = from_address.lower()
        
        if to_address:
            filter_dict['metadata.to_addresses'] = {'contains': to_address.lower()}
        
        if start_date:
            filter_dict['metadata.date'] = {'gte': start_date.isoformat()}
        
        if end_date:
            if 'metadata.date' not in filter_dict:
                filter_dict['metadata.date'] = {}
            filter_dict['metadata.date']['lte'] = end_date.isoformat()
        
        if has_attachments is not None:
            filter_dict['metadata.has_attachments'] = has_attachments
        
        if folder:
            filter_dict['metadata.folder'] = folder
        
        # Search
        return self.dataset.search(query=query, filter=filter_dict, limit=100)
    
    def get_conversation_thread(self, email_id: str) -> List[FrameRecord]:
        """Get complete conversation thread for an email."""
        # Get the email
        email_record = self.dataset.get(email_id)
        if not email_record:
            return []
        
        # Get thread ID
        thread_id = email_record.metadata.custom_metadata.get('thread_id')
        if not thread_id:
            return [email_record]
        
        # Get all emails in thread
        thread_emails = self.dataset.filter({
            'metadata.thread_id': thread_id
        })
        
        # Sort by date
        thread_emails.sort(
            key=lambda x: x.metadata.custom_metadata.get('date', '')
        )
        
        return thread_emails
    
    def analyze_communication_patterns(self, 
                                     email_account: str,
                                     start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze email communication patterns."""
        # Get emails for account
        filter_dict = {'metadata.email_account': email_account}
        if start_date:
            filter_dict['metadata.date'] = {'gte': start_date.isoformat()}
        
        emails = self.dataset.filter(filter_dict)
        
        # Analyze patterns
        analysis = {
            'total_emails': len(emails),
            'sent_emails': 0,
            'received_emails': 0,
            'top_correspondents': defaultdict(int),
            'busiest_hours': defaultdict(int),
            'busiest_days': defaultdict(int),
            'attachment_stats': {
                'with_attachments': 0,
                'total_attachments': 0,
                'common_types': defaultdict(int)
            }
        }
        
        for email_record in emails:
            metadata = email_record.metadata.custom_metadata
            
            # Sent vs received
            if metadata.get('from_address', '').lower() == email_account.lower():
                analysis['sent_emails'] += 1
                # Track recipients
                for addr in metadata.get('to_addresses', []):
                    analysis['top_correspondents'][addr] += 1
            else:
                analysis['received_emails'] += 1
                # Track sender
                analysis['top_correspondents'][metadata.get('from_address', '')] += 1
            
            # Time patterns
            try:
                date = datetime.fromisoformat(metadata.get('date', ''))
                analysis['busiest_hours'][date.hour] += 1
                analysis['busiest_days'][date.strftime('%A')] += 1
            except:
                pass
            
            # Attachment stats
            if metadata.get('has_attachments'):
                analysis['attachment_stats']['with_attachments'] += 1
                
                for att_type in metadata.get('attachment_types', []):
                    analysis['attachment_stats']['common_types'][att_type] += 1
                    analysis['attachment_stats']['total_attachments'] += 1
        
        # Get top correspondents
        analysis['top_correspondents'] = dict(
            sorted(analysis['top_correspondents'].items(), 
                  key=lambda x: x[1], reverse=True)[:10]
        )
        
        return analysis
    
    def compliance_search(self, 
                         keywords: List[str],
                         entity_types: List[str] = None,
                         date_range: Tuple[datetime, datetime] = None) -> List[Dict[str, Any]]:
        """Search for compliance-related content."""
        results = []
        
        # Build search query
        query = ' OR '.join(keywords)
        
        # Build filter
        filter_dict = {}
        if date_range:
            filter_dict['metadata.date'] = {
                'gte': date_range[0].isoformat(),
                'lte': date_range[1].isoformat()
            }
        
        # Search
        matches = self.dataset.search(query=query, filter=filter_dict, limit=1000)
        
        for match in matches:
            metadata = match.metadata.custom_metadata
            
            # Check for entities if specified
            if entity_types:
                found_entities = {}
                for entity_type in entity_types:
                    if entity_type in metadata.get('entities', {}):
                        found_entities[entity_type] = metadata['entities'][entity_type]
                
                if not found_entities:
                    continue
            else:
                found_entities = metadata.get('entities', {})
            
            results.append({
                'email_id': match.unique_id,
                'subject': match.metadata.title,
                'from': metadata.get('from_address'),
                'to': metadata.get('to_addresses'),
                'date': metadata.get('date'),
                'matched_keywords': [kw for kw in keywords if kw.lower() in match.text_content.lower()],
                'entities_found': found_entities,
                'has_attachments': metadata.get('has_attachments'),
                'thread_id': metadata.get('thread_id')
            })
        
        return results
    
    def export_thread_for_legal(self, thread_id: str, 
                               output_path: str,
                               include_attachments: bool = True) -> str:
        """Export email thread for legal discovery."""
        # Get all emails in thread
        thread_emails = self.dataset.filter({
            'metadata.thread_id': thread_id
        })
        
        # Sort by date
        thread_emails.sort(
            key=lambda x: x.metadata.custom_metadata.get('date', '')
        )
        
        # Create export document
        export_content = [
            "# Email Thread Export",
            f"Export Date: {datetime.now().isoformat()}",
            f"Thread ID: {thread_id}",
            f"Total Emails: {len(thread_emails)}",
            "\\n---\\n"
        ]
        
        for i, email_record in enumerate(thread_emails, 1):
            metadata = email_record.metadata.custom_metadata
            
            export_content.extend([
                f"## Email {i} of {len(thread_emails)}",
                f"**Message ID:** {metadata.get('message_id')}",
                f"**From:** {metadata.get('from_address')}",
                f"**To:** {', '.join(metadata.get('to_addresses', []))}",
                f"**CC:** {', '.join(metadata.get('cc_addresses', []))}",
                f"**Date:** {metadata.get('date')}",
                f"**Subject:** {email_record.metadata.title}",
                ""
            ])
            
            if metadata.get('has_attachments'):
                export_content.extend([
                    "**Attachments:**",
                    *[f"- {name}" for name in metadata.get('attachment_names', [])],
                    ""
                ])
            
            export_content.extend([
                "**Content:**",
                "```",
                email_record.text_content,
                "```",
                "\\n---\\n"
            ])
        
        # Write export file
        with open(output_path, 'w') as f:
            f.write("\\n".join(export_content))
        
        return output_path

# Example usage
if __name__ == "__main__":
    # Initialize archive
    archive = EmailArchiveSystem()
    
    # Import emails
    archive.import_mbox("archive.mbox", "john.doe@company.com")
    
    # Search emails
    results = archive.search_emails(
        query="project deadline",
        from_address="manager@company.com",
        start_date=datetime.now() - timedelta(days=30)
    )
    
    print(f"Found {len(results)} matching emails")
    
    # Analyze patterns
    patterns = archive.analyze_communication_patterns(
        "john.doe@company.com",
        start_date=datetime.now() - timedelta(days=90)
    )
    
    print(f"\\nCommunication Analysis:")
    print(f"Total emails: {patterns['total_emails']}")
    print(f"Sent: {patterns['sent_emails']}, Received: {patterns['received_emails']}")
    print(f"\\nTop correspondents:")
    for addr, count in list(patterns['top_correspondents'].items())[:5]:
        print(f"  {addr}: {count} emails")
    
    # Compliance search
    compliance_results = archive.compliance_search(
        keywords=["confidential", "proprietary", "trade secret"],
        entity_types=["ssn", "credit_card"],
        date_range=(datetime(2024, 1, 1), datetime.now())
    )
    
    if compliance_results:
        print(f"\\nCompliance Alert: Found {len(compliance_results)} emails with sensitive content")
```

## Key Concepts

### Email Processing

The system handles various email formats and encodings:
- **Message parsing**: Extracts headers, body, and attachments
- **Encoding detection**: Handles different character encodings
- **Thread reconstruction**: Links related emails
- **Entity extraction**: Identifies sensitive information

### Search Capabilities

Advanced search features include:
- **Full-text search**: Search across subject and body
- **Metadata filters**: Date ranges, senders, recipients
- **Attachment search**: Find emails with specific attachments
- **Thread search**: Get complete conversation context

### Compliance Features

Built-in compliance and e-discovery support:
- **Entity detection**: SSN, credit cards, case numbers
- **Keyword monitoring**: Flag sensitive terms
- **Legal hold**: Preserve and export threads
- **Audit trails**: Track access and searches

## Extensions

### Advanced Features

1. **Machine Learning**
   - Email categorization
   - Spam/phishing detection
   - Important email prediction
   - Auto-tagging

2. **Analytics**
   - Communication network analysis
   - Response time metrics
   - Email volume trends
   - Relationship mapping

3. **Integration**
   - Exchange/Office 365 sync
   - Gmail API integration
   - Slack/Teams connectors
   - CRM synchronization

4. **Security**
   - Encryption at rest
   - Access control lists
   - DLP integration
   - Retention policies

### Performance Optimization

1. **Parallel Processing**
   - Multi-threaded import
   - Batch processing
   - Async IMAP operations
   - Distributed indexing

2. **Storage Efficiency**
   - Deduplication
   - Compression
   - Tiered storage
   - Archive policies

3. **Search Performance**
   - Pre-computed threads
   - Cached frequent searches
   - Optimized filters
   - Result pagination

## Best Practices

1. **Privacy Compliance**
   - GDPR compliance
   - Data minimization
   - Consent management
   - Right to deletion

2. **Data Quality**
   - Validate email formats
   - Handle corrupted messages
   - Preserve original format
   - Maintain chain of custody

3. **Security**
   - Secure credentials
   - Audit all access
   - Encrypt sensitive data
   - Regular backups

4. **User Experience**
   - Fast search results
   - Relevant ranking
   - Thread visualization
   - Export options

This email archive system provides comprehensive email management capabilities for both knowledge preservation and compliance requirements.