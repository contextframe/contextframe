# Meeting Notes Organization

Build a comprehensive meeting notes management system that captures, organizes, and makes searchable all meeting content including transcripts, action items, decisions, and follow-ups.

## Problem Statement

Organizations lose valuable insights and decisions made during meetings due to poor note-taking, scattered documentation, and lack of follow-up tracking. A centralized system can capture meeting intelligence and ensure accountability.

## Solution Overview

We'll build a meeting notes system that:
1. Processes meeting transcripts and notes from multiple sources
2. Extracts action items, decisions, and key points automatically
3. Links related meetings and tracks follow-ups
4. Provides intelligent search across all meetings
5. Generates meeting summaries and reports

## Complete Code

```python
import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import spacy
from dataclasses import dataclass
import whisper
import pandas as pd

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

@dataclass
class ActionItem:
    """Represents an action item from a meeting."""
    task: str
    assignee: Optional[str]
    due_date: Optional[datetime]
    status: str = "pending"
    
@dataclass
class Decision:
    """Represents a decision made in a meeting."""
    decision: str
    context: str
    participants: List[str]
    timestamp: Optional[str]

class MeetingNotesOrganizer:
    """Comprehensive meeting notes management system."""
    
    def __init__(self, dataset_path: str = "meeting_notes.lance"):
        """Initialize meeting notes system."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Load NLP model for entity extraction
        self.nlp = spacy.load("en_core_web_sm")
        
        # Whisper model for audio transcription
        self.whisper_model = None  # Lazy load
        
        # Meeting patterns
        self.action_patterns = [
            r"(?:action|todo|task):\s*(.+)",
            r"(?:we will|I will|they will)\s+(.+)",
            r"(?:need to|needs to|must)\s+(.+)",
            r"(?:follow up|follow-up)\s+(?:on|with)\s+(.+)",
            r"(?:assigned to|owner:)\s*(\w+)\s*[:,-]?\s*(.+)"
        ]
        
        self.decision_patterns = [
            r"(?:decided|agreed|resolved)(?:\s+that)?\s+(.+)",
            r"(?:decision|conclusion):\s*(.+)",
            r"(?:we are going to|we will)\s+(.+)",
            r"(?:approved|rejected)\s+(.+)"
        ]
    
    def process_meeting(self, 
                       title: str,
                       participants: List[str],
                       meeting_date: datetime,
                       content: str,
                       meeting_type: str = "general",
                       recording_path: Optional[str] = None,
                       attachments: Optional[List[str]] = None) -> FrameRecord:
        """Process a complete meeting."""
        print(f"Processing meeting: {title}")
        
        # If we have a recording, transcribe it
        if recording_path:
            transcript = self._transcribe_audio(recording_path)
            content = f"{content}\n\nTranscript:\n{transcript}"
        
        # Extract meeting intelligence
        intelligence = self._extract_meeting_intelligence(content, participants)
        
        # Create metadata
        metadata = create_metadata(
            title=title,
            source="meeting_notes",
            meeting_date=meeting_date.isoformat(),
            meeting_type=meeting_type,
            participants=participants,
            participant_count=len(participants),
            duration_minutes=intelligence.get('estimated_duration'),
            has_recording=bool(recording_path),
            has_attachments=bool(attachments),
            action_count=len(intelligence['action_items']),
            decision_count=len(intelligence['decisions']),
            topics=intelligence['topics'],
            sentiment=intelligence['sentiment'],
            **{k: v for k, v in intelligence.items() 
               if k not in ['action_items', 'decisions', 'topics', 'sentiment']}
        )
        
        # Add relationships to previous meetings
        related_meetings = self._find_related_meetings(title, participants, intelligence['topics'])
        for related in related_meetings:
            metadata = add_relationship_to_metadata(
                metadata,
                relationship_type="follows",
                target_id=related['unique_id'],
                metadata={"similarity_score": related['score']}
            )
        
        # Create record
        record = FrameRecord(
            text_content=f"Meeting: {title}\nDate: {meeting_date.strftime('%Y-%m-%d')}\nParticipants: {', '.join(participants)}\n\n{content}",
            metadata=metadata,
            unique_id=f"meeting_{generate_uuid(namespace='meeting', name=f'{title}_{meeting_date}')}",
            record_type="document",
            context={
                "intelligence": intelligence,
                "attachments": attachments or [],
                "recording_path": recording_path
            }
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        # Create separate records for action items
        self._create_action_item_records(intelligence['action_items'], record.unique_id)
        
        return record
    
    def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio recording using Whisper."""
        if not self.whisper_model:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
        
        print(f"Transcribing {audio_path}...")
        result = self.whisper_model.transcribe(audio_path)
        
        return result["text"]
    
    def _extract_meeting_intelligence(self, content: str, participants: List[str]) -> Dict[str, Any]:
        """Extract actionable intelligence from meeting content."""
        intelligence = {
            'action_items': [],
            'decisions': [],
            'topics': [],
            'key_points': [],
            'questions': [],
            'risks': [],
            'sentiment': 'neutral',
            'urgency': 'normal'
        }
        
        # Extract action items
        for pattern in self.action_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                action_text = match.group(1).strip()
                
                # Try to extract assignee
                assignee = self._extract_assignee(action_text, participants)
                
                # Try to extract due date
                due_date = self._extract_due_date(action_text)
                
                intelligence['action_items'].append(ActionItem(
                    task=action_text,
                    assignee=assignee,
                    due_date=due_date
                ))
        
        # Extract decisions
        for pattern in self.decision_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                decision_text = match.group(1).strip()
                intelligence['decisions'].append(Decision(
                    decision=decision_text,
                    context=self._extract_context(content, match.start(), 100),
                    participants=participants,
                    timestamp=None
                ))
        
        # Extract topics using NLP
        doc = self.nlp(content)
        
        # Topics from noun phrases
        topics = []
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3 and chunk.root.pos_ in ['NOUN', 'PROPN']:
                topics.append(chunk.text.lower())
        
        intelligence['topics'] = list(set(topics))[:20]  # Top 20 unique topics
        
        # Extract key points (sentences with high importance)
        sentences = [sent.text.strip() for sent in doc.sents]
        key_sentences = []
        
        for sent in sentences:
            # Simple importance scoring
            if any(keyword in sent.lower() for keyword in ['important', 'critical', 'key', 'must', 'priority']):
                key_sentences.append(sent)
            elif len(re.findall(r'\b(?:will|must|should|need)\b', sent, re.I)) >= 2:
                key_sentences.append(sent)
        
        intelligence['key_points'] = key_sentences[:10]
        
        # Extract questions
        questions = [sent.text for sent in doc.sents if sent.text.strip().endswith('?')]
        intelligence['questions'] = questions
        
        # Extract risks and concerns
        risk_patterns = [
            r"(?:risk|concern|worried|threat):\s*(.+)",
            r"(?:concerned about|worried about|risk of)\s+(.+)"
        ]
        
        risks = []
        for pattern in risk_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                risks.append(match.group(1).strip())
        
        intelligence['risks'] = risks
        
        # Analyze sentiment
        sentiment_score = self._analyze_sentiment(content)
        if sentiment_score > 0.2:
            intelligence['sentiment'] = 'positive'
        elif sentiment_score < -0.2:
            intelligence['sentiment'] = 'negative'
        else:
            intelligence['sentiment'] = 'neutral'
        
        # Detect urgency
        urgency_keywords = {
            'critical': ['urgent', 'critical', 'emergency', 'immediately', 'asap'],
            'high': ['important', 'priority', 'soon', 'quickly'],
            'normal': []
        }
        
        content_lower = content.lower()
        for urgency, keywords in urgency_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                intelligence['urgency'] = urgency
                break
        
        # Estimate duration
        intelligence['estimated_duration'] = self._estimate_duration(content)
        
        return intelligence
    
    def _extract_assignee(self, text: str, participants: List[str]) -> Optional[str]:
        """Extract assignee from action item text."""
        text_lower = text.lower()
        
        # Check for participant names
        for participant in participants:
            if participant.lower() in text_lower:
                return participant
        
        # Check for pronouns and common patterns
        if re.search(r'\b(I|i\'ll|i will)\b', text):
            # Would need context to determine who "I" is
            return "Self"
        
        # Pattern: "assigned to X" or "owner: X"
        assignee_match = re.search(r'(?:assigned to|owner:)\s*(\w+)', text, re.I)
        if assignee_match:
            return assignee_match.group(1)
        
        return None
    
    def _extract_due_date(self, text: str) -> Optional[datetime]:
        """Extract due date from action item text."""
        # Common date patterns
        date_patterns = [
            r'(?:by|before|due)\s+(\d{1,2}/\d{1,2}(?:/\d{2,4})?)',
            r'(?:by|before|due)\s+(next\s+\w+)',
            r'(?:by|before|due)\s+(\w+\s+\d{1,2})',
            r'(?:within|in)\s+(\d+)\s+(days?|weeks?|months?)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                date_str = match.group(1)
                # Parse date (simplified - would need robust date parsing)
                try:
                    if 'next' in date_str:
                        # Handle "next Monday", etc.
                        return datetime.now() + timedelta(days=7)
                    elif re.match(r'\d+', date_str):
                        # Handle "in X days/weeks"
                        amount = int(match.group(1))
                        unit = match.group(2)
                        if 'day' in unit:
                            return datetime.now() + timedelta(days=amount)
                        elif 'week' in unit:
                            return datetime.now() + timedelta(weeks=amount)
                except:
                    pass
        
        return None
    
    def _extract_context(self, content: str, position: int, context_size: int) -> str:
        """Extract context around a position in text."""
        start = max(0, position - context_size)
        end = min(len(content), position + context_size)
        return content[start:end].strip()
    
    def _analyze_sentiment(self, content: str) -> float:
        """Simple sentiment analysis."""
        positive_words = ['good', 'great', 'excellent', 'happy', 'success', 'achieved', 'completed']
        negative_words = ['bad', 'issue', 'problem', 'failed', 'delayed', 'concern', 'difficult']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _estimate_duration(self, content: str) -> int:
        """Estimate meeting duration from content."""
        # Simple estimation based on content length and complexity
        word_count = len(content.split())
        
        # Assume average speaking rate of 150 words per minute
        # and that transcript captures about 70% of meeting
        estimated_minutes = (word_count / 150) / 0.7
        
        # Round to nearest 5 minutes
        return int(round(estimated_minutes / 5) * 5)
    
    def _find_related_meetings(self, title: str, participants: List[str], 
                             topics: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Find related previous meetings."""
        # Search by similar title and topics
        search_query = f"{title} {' '.join(topics[:5])}"
        
        results = self.dataset.search(
            search_query,
            filter="metadata.source = 'meeting_notes'",
            limit=limit + 1  # +1 to exclude self if already exists
        )
        
        related = []
        for result in results:
            # Skip if same meeting
            if result.metadata.get('title') == title:
                continue
            
            # Calculate relevance score
            score = result.score
            
            # Boost score for participant overlap
            result_participants = set(result.metadata.get('participants', []))
            participant_overlap = len(set(participants) & result_participants) / len(participants)
            score *= (1 + participant_overlap * 0.5)
            
            related.append({
                'unique_id': result.unique_id,
                'title': result.metadata.get('title'),
                'date': result.metadata.get('meeting_date'),
                'score': score
            })
        
        return related[:limit]
    
    def _create_action_item_records(self, action_items: List[ActionItem], 
                                  meeting_id: str):
        """Create separate records for action items."""
        for i, action in enumerate(action_items):
            metadata = create_metadata(
                title=f"Action: {action.task[:50]}...",
                source="action_item",
                task=action.task,
                assignee=action.assignee,
                due_date=action.due_date.isoformat() if action.due_date else None,
                status=action.status,
                created_from_meeting=meeting_id
            )
            
            # Link to meeting
            metadata = add_relationship_to_metadata(
                metadata,
                relationship_type="created_from",
                target_id=meeting_id
            )
            
            record = FrameRecord(
                text_content=f"Action Item: {action.task}\nAssignee: {action.assignee or 'Unassigned'}\nDue: {action.due_date or 'No due date'}\nStatus: {action.status}",
                metadata=metadata,
                unique_id=f"action_{meeting_id}_{i}",
                record_type="document"
            )
            
            self.dataset.add(record)
    
    def search_meetings(self, query: str, 
                       filters: Optional[Dict[str, Any]] = None,
                       limit: int = 20) -> List[Dict[str, Any]]:
        """Search meetings with optional filters."""
        # Build filter conditions
        filter_conditions = ["metadata.source = 'meeting_notes'"]
        
        if filters:
            if 'participant' in filters:
                filter_conditions.append(f"array_contains(metadata.participants, '{filters['participant']}')")
            if 'date_from' in filters:
                filter_conditions.append(f"metadata.meeting_date >= '{filters['date_from']}'")
            if 'date_to' in filters:
                filter_conditions.append(f"metadata.meeting_date <= '{filters['date_to']}'")
            if 'meeting_type' in filters:
                filter_conditions.append(f"metadata.meeting_type = '{filters['meeting_type']}'")
        
        filter_str = " AND ".join(filter_conditions)
        
        # Search
        results = self.dataset.search(query, filter=filter_str, limit=limit)
        
        # Format results
        formatted = []
        for result in results:
            formatted.append({
                'title': result.metadata.get('title'),
                'date': result.metadata.get('meeting_date'),
                'participants': result.metadata.get('participants', []),
                'type': result.metadata.get('meeting_type'),
                'action_count': result.metadata.get('action_count', 0),
                'decision_count': result.metadata.get('decision_count', 0),
                'score': result.score,
                'unique_id': result.unique_id
            })
        
        return formatted
    
    def get_action_items(self, 
                        assignee: Optional[str] = None,
                        status: Optional[str] = None,
                        include_overdue: bool = True) -> List[Dict[str, Any]]:
        """Get action items with filters."""
        # Build filter
        filter_conditions = ["metadata.source = 'action_item'"]
        
        if assignee:
            filter_conditions.append(f"metadata.assignee = '{assignee}'")
        if status:
            filter_conditions.append(f"metadata.status = '{status}'")
        
        filter_str = " AND ".join(filter_conditions)
        
        # Get action items
        action_records = self.dataset.sql_filter(filter_str)
        
        actions = []
        for record in action_records:
            action_dict = {
                'task': record.metadata.get('task'),
                'assignee': record.metadata.get('assignee'),
                'due_date': record.metadata.get('due_date'),
                'status': record.metadata.get('status'),
                'meeting_id': record.metadata.get('created_from_meeting'),
                'unique_id': record.unique_id
            }
            
            # Check if overdue
            if include_overdue and action_dict['due_date'] and action_dict['status'] != 'completed':
                due = datetime.fromisoformat(action_dict['due_date'])
                if due < datetime.now():
                    action_dict['overdue'] = True
                    action_dict['days_overdue'] = (datetime.now() - due).days
            
            actions.append(action_dict)
        
        return actions
    
    def update_action_status(self, action_id: str, new_status: str):
        """Update action item status."""
        record = self.dataset.get(action_id)
        if record and record.metadata.get('source') == 'action_item':
            record.metadata['status'] = new_status
            if new_status == 'completed':
                record.metadata['completed_date'] = datetime.now().isoformat()
            
            self.dataset.update(action_id, metadata=record.metadata)
    
    def generate_meeting_summary(self, meeting_id: str) -> str:
        """Generate a summary of a meeting."""
        meeting = self.dataset.get(meeting_id)
        if not meeting:
            return "Meeting not found"
        
        intelligence = meeting.context.get('intelligence', {})
        
        summary = f"""# Meeting Summary: {meeting.metadata.get('title')}

**Date:** {meeting.metadata.get('meeting_date')}
**Participants:** {', '.join(meeting.metadata.get('participants', []))}
**Duration:** {meeting.metadata.get('duration_minutes', 'Unknown')} minutes

## Key Topics
{chr(10).join(f"- {topic}" for topic in intelligence.get('topics', [])[:10])}

## Decisions Made ({len(intelligence.get('decisions', []))})
"""
        
        for i, decision in enumerate(intelligence.get('decisions', [])[:10], 1):
            summary += f"{i}. {decision.decision}\n"
        
        summary += f"\n## Action Items ({len(intelligence.get('action_items', []))})\n"
        
        for i, action in enumerate(intelligence.get('action_items', [])[:10], 1):
            assignee = action.assignee or "Unassigned"
            due = action.due_date.strftime('%Y-%m-%d') if action.due_date else "No due date"
            summary += f"{i}. {action.task}\n   - Assignee: {assignee}\n   - Due: {due}\n"
        
        if intelligence.get('risks'):
            summary += "\n## Risks & Concerns\n"
            for risk in intelligence['risks'][:5]:
                summary += f"- {risk}\n"
        
        if intelligence.get('questions'):
            summary += "\n## Open Questions\n"
            for question in intelligence['questions'][:5]:
                summary += f"- {question}\n"
        
        return summary
    
    def generate_action_report(self, 
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> str:
        """Generate report on action items."""
        # Get all action items
        actions = self.get_action_items()
        
        # Filter by date if specified
        if start_date or end_date:
            filtered_actions = []
            for action in actions:
                if action.get('due_date'):
                    due = datetime.fromisoformat(action['due_date'])
                    if start_date and due < start_date:
                        continue
                    if end_date and due > end_date:
                        continue
                    filtered_actions.append(action)
            actions = filtered_actions
        
        # Group by assignee
        by_assignee = defaultdict(list)
        for action in actions:
            assignee = action.get('assignee', 'Unassigned')
            by_assignee[assignee].append(action)
        
        # Generate report
        report = "# Action Items Report\n\n"
        
        # Summary
        total = len(actions)
        completed = len([a for a in actions if a.get('status') == 'completed'])
        overdue = len([a for a in actions if a.get('overdue')])
        
        report += f"""## Summary
- Total Action Items: {total}
- Completed: {completed} ({completed/total*100:.1f}%)
- Pending: {total - completed}
- Overdue: {overdue}

## By Assignee
"""
        
        for assignee, items in sorted(by_assignee.items()):
            report += f"\n### {assignee} ({len(items)} items)\n"
            
            # Sort by due date
            items.sort(key=lambda x: x.get('due_date', '9999'))
            
            for item in items:
                status_emoji = {
                    'completed': '✅',
                    'in_progress': '🔄',
                    'pending': '⏳'
                }.get(item.get('status', 'pending'), '❓')
                
                overdue_text = " ⚠️ OVERDUE" if item.get('overdue') else ""
                due_text = f" (Due: {item.get('due_date', 'No date')})"
                
                report += f"- {status_emoji} {item['task']}{due_text}{overdue_text}\n"
        
        return report
    
    def create_meeting_series(self, base_title: str, meetings: List[str]) -> str:
        """Link meetings in a series."""
        series_id = f"series_{generate_uuid()}"
        
        # Get meeting records
        meeting_records = []
        for meeting_title in meetings:
            results = self.dataset.sql_filter(
                f"metadata.source = 'meeting_notes' AND metadata.title = '{meeting_title}'",
                limit=1
            )
            if results:
                meeting_records.append(results[0])
        
        # Update each meeting with series info
        for i, record in enumerate(meeting_records):
            record.metadata['series_id'] = series_id
            record.metadata['series_position'] = i + 1
            record.metadata['series_total'] = len(meeting_records)
            
            # Add relationships to previous/next
            if i > 0:
                record.metadata = add_relationship_to_metadata(
                    record.metadata,
                    relationship_type="previous_in_series",
                    target_id=meeting_records[i-1].unique_id
                )
            
            if i < len(meeting_records) - 1:
                record.metadata = add_relationship_to_metadata(
                    record.metadata,
                    relationship_type="next_in_series",
                    target_id=meeting_records[i+1].unique_id
                )
            
            self.dataset.update(record.unique_id, metadata=record.metadata)
        
        return series_id
    
    def analyze_meeting_patterns(self, 
                               participant: Optional[str] = None,
                               time_period_days: int = 90) -> Dict[str, Any]:
        """Analyze meeting patterns and trends."""
        # Get meetings in time period
        start_date = datetime.now() - timedelta(days=time_period_days)
        
        filter_conditions = [
            "metadata.source = 'meeting_notes'",
            f"metadata.meeting_date >= '{start_date.isoformat()}'"
        ]
        
        if participant:
            filter_conditions.append(f"array_contains(metadata.participants, '{participant}')")
        
        meetings = self.dataset.sql_filter(" AND ".join(filter_conditions))
        
        analysis = {
            'total_meetings': len(meetings),
            'total_hours': 0,
            'by_type': defaultdict(int),
            'by_day_of_week': defaultdict(int),
            'by_hour_of_day': defaultdict(int),
            'participant_frequency': defaultdict(int),
            'common_topics': defaultdict(int),
            'action_items_per_meeting': [],
            'decisions_per_meeting': [],
            'meeting_efficiency': []
        }
        
        for meeting in meetings:
            # Meeting type
            meeting_type = meeting.metadata.get('meeting_type', 'unknown')
            analysis['by_type'][meeting_type] += 1
            
            # Duration
            duration = meeting.metadata.get('duration_minutes', 0)
            analysis['total_hours'] += duration / 60
            
            # Day and time analysis
            if meeting.metadata.get('meeting_date'):
                date = datetime.fromisoformat(meeting.metadata['meeting_date'])
                analysis['by_day_of_week'][date.strftime('%A')] += 1
                analysis['by_hour_of_day'][date.hour] += 1
            
            # Participants
            for p in meeting.metadata.get('participants', []):
                analysis['participant_frequency'][p] += 1
            
            # Topics
            for topic in meeting.metadata.get('topics', []):
                analysis['common_topics'][topic] += 1
            
            # Productivity metrics
            action_count = meeting.metadata.get('action_count', 0)
            decision_count = meeting.metadata.get('decision_count', 0)
            
            analysis['action_items_per_meeting'].append(action_count)
            analysis['decisions_per_meeting'].append(decision_count)
            
            # Efficiency score (actions + decisions per hour)
            if duration > 0:
                efficiency = (action_count + decision_count) / (duration / 60)
                analysis['meeting_efficiency'].append(efficiency)
        
        # Calculate averages
        import numpy as np
        
        analysis['avg_duration_minutes'] = (analysis['total_hours'] * 60) / len(meetings) if meetings else 0
        analysis['avg_action_items'] = np.mean(analysis['action_items_per_meeting']) if analysis['action_items_per_meeting'] else 0
        analysis['avg_decisions'] = np.mean(analysis['decisions_per_meeting']) if analysis['decisions_per_meeting'] else 0
        analysis['avg_efficiency'] = np.mean(analysis['meeting_efficiency']) if analysis['meeting_efficiency'] else 0
        
        # Convert defaultdicts
        for key in ['by_type', 'by_day_of_week', 'by_hour_of_day']:
            analysis[key] = dict(analysis[key])
        
        # Top participants and topics
        analysis['top_participants'] = dict(
            sorted(analysis['participant_frequency'].items(), 
                   key=lambda x: x[1], reverse=True)[:10]
        )
        analysis['top_topics'] = dict(
            sorted(analysis['common_topics'].items(), 
                   key=lambda x: x[1], reverse=True)[:20]
        )
        
        return analysis

# Example usage
if __name__ == "__main__":
    # Initialize system
    organizer = MeetingNotesOrganizer()
    
    # Process a meeting with notes
    meeting_record = organizer.process_meeting(
        title="Q4 Planning Meeting",
        participants=["John Smith", "Jane Doe", "Bob Johnson", "Alice Williams"],
        meeting_date=datetime(2024, 1, 15, 14, 0),
        meeting_type="planning",
        content="""
        Meeting started with review of Q3 results.
        
        John presented the revenue figures - we exceeded targets by 15%.
        
        Decision: We will increase Q4 targets by 20% based on current momentum.
        
        Action: Jane will prepare revised budget projections by Friday.
        Action: Bob needs to hire 2 additional engineers by end of month.
        
        Discussed new product launch timeline.
        Concern: Supply chain delays might impact launch date.
        
        Action: Alice to follow up with suppliers and report back next week.
        
        Question: Should we consider alternative suppliers?
        
        Agreed that we need to explore backup options.
        
        Meeting concluded with agreement to reconvene in 2 weeks.
        """
    )
    
    # Process meeting with audio
    # organizer.process_meeting(
    #     title="Daily Standup",
    #     participants=["Dev Team"],
    #     meeting_date=datetime.now(),
    #     meeting_type="standup",
    #     content="Daily standup meeting",
    #     recording_path="meetings/standup_2024_01_15.mp3"
    # )
    
    # Search meetings
    results = organizer.search_meetings(
        "product launch",
        filters={'participant': 'John Smith'}
    )
    
    print("Search Results:")
    for result in results[:5]:
        print(f"- {result['title']} ({result['date']}) - Score: {result['score']:.2f}")
    
    # Get action items
    actions = organizer.get_action_items(assignee="Jane Doe")
    
    print("\nJane's Action Items:")
    for action in actions:
        status = "✅" if action['status'] == 'completed' else "⏳"
        print(f"{status} {action['task']} (Due: {action.get('due_date', 'No date')})")
    
    # Generate meeting summary
    summary = organizer.generate_meeting_summary(meeting_record.unique_id)
    print("\nMeeting Summary:")
    print(summary)
    
    # Analyze patterns
    patterns = organizer.analyze_meeting_patterns(time_period_days=30)
    print(f"\nMeeting Analytics (Last 30 days):")
    print(f"- Total meetings: {patterns['total_meetings']}")
    print(f"- Total hours: {patterns['total_hours']:.1f}")
    print(f"- Average duration: {patterns['avg_duration_minutes']:.0f} minutes")
    print(f"- Average action items: {patterns['avg_action_items']:.1f}")
    print(f"- Average efficiency: {patterns['avg_efficiency']:.2f} items/hour")
```

## Key Concepts

### 1. Meeting Intelligence Extraction
- Action item detection with assignee and due dates
- Decision identification and context
- Topic extraction using NLP
- Risk and concern detection
- Question tracking

### 2. Audio Transcription
- Whisper integration for meeting recordings
- Transcript processing and formatting
- Speaker diarization (with extensions)
- Time-stamped content

### 3. Relationship Management
- Meeting series tracking
- Follow-up meeting linking
- Related meeting discovery
- Participant network analysis

### 4. Action Item Tracking
- Separate records for accountability
- Status management
- Due date tracking
- Overdue notifications
- Assignment management

### 5. Analytics and Insights
- Meeting efficiency metrics
- Participant engagement analysis
- Time pattern analysis
- Topic trend tracking
- Productivity measurements

## Extensions

### 1. Calendar Integration
```python
from icalendar import Calendar, Event
import pytz

def sync_with_calendar(self, calendar_url: str):
    """Sync meetings with calendar system."""
    import requests
    
    # Fetch calendar
    response = requests.get(calendar_url)
    cal = Calendar.from_ical(response.text)
    
    for component in cal.walk():
        if component.name == "VEVENT":
            # Extract meeting info
            title = str(component.get('summary'))
            start = component.get('dtstart').dt
            attendees = []
            
            for attendee in component.get('attendee', []):
                email = str(attendee).replace('mailto:', '')
                attendees.append(email)
            
            # Check if meeting already exists
            existing = self.dataset.sql_filter(
                f"metadata.title = '{title}' AND metadata.meeting_date = '{start.isoformat()}'",
                limit=1
            )
            
            if not existing:
                # Create placeholder for future meeting
                self.process_meeting(
                    title=title,
                    participants=attendees,
                    meeting_date=start,
                    content="Meeting scheduled - notes to be added",
                    meeting_type="scheduled"
                )
```

### 2. Real-time Collaboration
```python
import asyncio
import websockets

class RealtimeMeetingNotes:
    """Real-time collaborative note-taking."""
    
    def __init__(self, organizer: MeetingNotesOrganizer):
        self.organizer = organizer
        self.active_meetings = {}
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket connections."""
        meeting_id = path.strip('/')
        
        if meeting_id not in self.active_meetings:
            self.active_meetings[meeting_id] = {
                'participants': set(),
                'content': [],
                'actions': []
            }
        
        self.active_meetings[meeting_id]['participants'].add(websocket)
        
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'note':
                    # Broadcast to all participants
                    await self.broadcast_note(meeting_id, data)
                
                elif data['type'] == 'action':
                    # Add action item
                    self.active_meetings[meeting_id]['actions'].append(data)
                    await self.broadcast_action(meeting_id, data)
        
        finally:
            self.active_meetings[meeting_id]['participants'].remove(websocket)
```

### 3. Smart Scheduling
```python
def suggest_meeting_time(self, participants: List[str], 
                        duration_minutes: int,
                        preferred_times: Optional[Dict[str, Any]] = None) -> List[datetime]:
    """Suggest optimal meeting times based on patterns."""
    # Analyze when participants typically meet
    patterns = {}
    
    for participant in participants:
        p_analysis = self.analyze_meeting_patterns(
            participant=participant,
            time_period_days=30
        )
        patterns[participant] = p_analysis
    
    # Find common available times
    suggestions = []
    
    # Get typical meeting hours
    common_hours = set()
    for p_data in patterns.values():
        hours = p_data.get('by_hour_of_day', {})
        top_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:5]
        common_hours.update([h[0] for h in top_hours])
    
    # Generate suggestions for next 7 days
    for days_ahead in range(1, 8):
        date = datetime.now() + timedelta(days=days_ahead)
        
        for hour in sorted(common_hours):
            suggestion = date.replace(hour=hour, minute=0, second=0)
            
            # Check if time is reasonable
            if suggestion.weekday() < 5:  # Weekday
                if 9 <= hour <= 17:  # Business hours
                    suggestions.append(suggestion)
    
    return suggestions[:5]
```

### 4. Meeting Templates
```python
class MeetingTemplate:
    """Predefined meeting templates."""
    
    TEMPLATES = {
        'standup': {
            'sections': ['Yesterday', 'Today', 'Blockers'],
            'duration': 15,
            'prompts': [
                "What did you complete yesterday?",
                "What will you work on today?",
                "Are there any blockers?"
            ]
        },
        'retrospective': {
            'sections': ['What went well', 'What could improve', 'Action items'],
            'duration': 60,
            'prompts': [
                "What went well this sprint?",
                "What challenges did we face?",
                "What should we do differently?"
            ]
        },
        'one_on_one': {
            'sections': ['Updates', 'Feedback', 'Goals', 'Support needed'],
            'duration': 30,
            'prompts': [
                "How are things going?",
                "Any feedback or concerns?",
                "Progress on goals?",
                "How can I support you?"
            ]
        }
    }
    
    @classmethod
    def generate_agenda(cls, template_name: str, 
                       participants: List[str]) -> str:
        """Generate meeting agenda from template."""
        template = cls.TEMPLATES.get(template_name, {})
        
        agenda = f"# {template_name.title()} Meeting Agenda\n\n"
        agenda += f"**Duration:** {template.get('duration', 60)} minutes\n"
        agenda += f"**Participants:** {', '.join(participants)}\n\n"
        
        for i, section in enumerate(template.get('sections', []), 1):
            agenda += f"## {i}. {section}\n"
            if i <= len(template.get('prompts', [])):
                agenda += f"_{template['prompts'][i-1]}_\n"
            agenda += "\n\n"
        
        agenda += "## Action Items\n\n"
        agenda += "## Next Steps\n"
        
        return agenda
```

### 5. Meeting Coach
```python
class MeetingCoach:
    """Provide real-time meeting effectiveness feedback."""
    
    def __init__(self, organizer: MeetingNotesOrganizer):
        self.organizer = organizer
    
    def analyze_meeting_effectiveness(self, meeting_id: str) -> Dict[str, Any]:
        """Analyze meeting effectiveness."""
        meeting = self.organizer.dataset.get(meeting_id)
        if not meeting:
            return {}
        
        intelligence = meeting.context.get('intelligence', {})
        
        # Calculate effectiveness scores
        scores = {
            'clarity': self._score_clarity(meeting),
            'productivity': self._score_productivity(meeting),
            'engagement': self._score_engagement(meeting),
            'follow_through': self._score_follow_through(meeting)
        }
        
        # Generate recommendations
        recommendations = []
        
        if scores['clarity'] < 0.7:
            recommendations.append(
                "Consider creating a clearer agenda before the meeting"
            )
        
        if scores['productivity'] < 0.7:
            recommendations.append(
                "Try to generate more concrete action items and decisions"
            )
        
        if scores['engagement'] < 0.7:
            recommendations.append(
                "Encourage more participation from all attendees"
            )
        
        return {
            'scores': scores,
            'overall': sum(scores.values()) / len(scores),
            'recommendations': recommendations
        }
    
    def _score_clarity(self, meeting: FrameRecord) -> float:
        """Score meeting clarity."""
        intelligence = meeting.context.get('intelligence', {})
        
        # Check for clear topics and agenda
        has_topics = len(intelligence.get('topics', [])) > 3
        has_decisions = len(intelligence.get('decisions', [])) > 0
        has_structure = bool(re.search(r'\b(agenda|topic|item) \d+', 
                                      meeting.text_content, re.I))
        
        score = sum([has_topics, has_decisions, has_structure]) / 3
        return score
```

## Best Practices

1. **Consistent Format**: Use templates for consistent note-taking
2. **Action Accountability**: Always assign owners and due dates
3. **Regular Reviews**: Periodically review and update action items
4. **Audio Backup**: Record important meetings for reference
5. **Participant Validation**: Verify participant lists are complete
6. **Follow-up Tracking**: Link related meetings explicitly
7. **Privacy Considerations**: Handle sensitive meeting content appropriately

## See Also

- [Email Archive Search](email-archive.md) - Email meeting invites
- [Slack Community Knowledge](slack-knowledge.md) - Chat-based meetings
- [Document Processing Pipeline](document-pipeline.md) - Processing attachments
- [API Reference](../api/overview.md) - FrameDataset documentation