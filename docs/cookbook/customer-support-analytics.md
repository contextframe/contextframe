# Customer Support Analytics

Build a comprehensive customer support analytics system that processes tickets, chat logs, and feedback to identify trends, measure sentiment, and improve support quality.

## Problem Statement

Customer support teams need to analyze thousands of support interactions to identify common issues, track resolution times, measure customer satisfaction, and discover opportunities for improvement. Manual analysis is time-consuming and misses patterns.

## Solution Overview

We'll build a support analytics system that:
1. Ingests support tickets from multiple channels
2. Analyzes sentiment and urgency
3. Categorizes issues automatically
4. Tracks resolution patterns
5. Generates actionable insights

## Complete Code

```python
import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from textblob import TextBlob
import plotly.graph_objects as go
import plotly.express as px

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    add_relationship_to_metadata,
    generate_uuid
)

class SupportAnalytics:
    """Customer support analytics system."""
    
    def __init__(self, dataset_path: str = "support_analytics.lance"):
        """Initialize analytics system."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Categories and patterns
        self.issue_categories = {
            'billing': ['payment', 'charge', 'invoice', 'refund', 'subscription', 'price'],
            'technical': ['bug', 'error', 'crash', 'slow', 'broken', 'fix', 'issue'],
            'account': ['login', 'password', 'reset', 'access', 'permission', 'locked'],
            'feature': ['request', 'feature', 'add', 'new', 'implement', 'suggestion'],
            'integration': ['api', 'integration', 'connect', 'sync', 'import', 'export'],
            'documentation': ['how to', 'guide', 'tutorial', 'help', 'documentation', 'manual']
        }
        
        # Urgency indicators
        self.urgency_patterns = {
            'critical': ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'down', 'broken completely'],
            'high': ['important', 'soon', 'quickly', 'high priority', 'affecting business'],
            'medium': ['when possible', 'would like', 'hoping', 'planning'],
            'low': ['whenever', 'no rush', 'curious', 'question', 'wondering']
        }
    
    def ingest_support_ticket(self, ticket: Dict[str, Any]) -> FrameRecord:
        """Ingest a support ticket with analysis."""
        # Combine all text content
        content = f"{ticket.get('subject', '')}\n\n{ticket.get('description', '')}"
        
        # Add conversation history if available
        if 'messages' in ticket:
            content += "\n\nConversation:\n"
            for msg in ticket['messages']:
                content += f"\n[{msg['sender']} at {msg['timestamp']}]:\n{msg['content']}\n"
        
        # Analyze ticket
        analysis = self._analyze_ticket(content, ticket)
        
        # Create metadata
        metadata = create_metadata(
            title=ticket.get('subject', 'Support Ticket'),
            source="support_system",
            ticket_id=ticket.get('id'),
            customer_id=ticket.get('customer_id'),
            customer_email=ticket.get('customer_email'),
            status=ticket.get('status', 'open'),
            priority=analysis['urgency'],
            category=analysis['category'],
            subcategory=analysis.get('subcategory'),
            sentiment=analysis['sentiment']['label'],
            sentiment_score=analysis['sentiment']['score'],
            created_at=ticket.get('created_at'),
            updated_at=ticket.get('updated_at'),
            resolved_at=ticket.get('resolved_at'),
            first_response_time=ticket.get('first_response_time'),
            resolution_time=ticket.get('resolution_time'),
            agent_id=ticket.get('agent_id'),
            agent_name=ticket.get('agent_name'),
            tags=ticket.get('tags', []),
            channel=ticket.get('channel', 'email'),
            satisfaction_score=ticket.get('satisfaction_score')
        )
        
        # Add relationships
        if ticket.get('related_tickets'):
            for related_id in ticket['related_tickets']:
                metadata = add_relationship_to_metadata(
                    metadata,
                    relationship_type="related",
                    target_id=f"ticket_{related_id}"
                )
        
        # Create record
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=f"ticket_{ticket.get('id', generate_uuid())}",
            record_type="document",
            context={
                "analysis": analysis,
                "message_count": len(ticket.get('messages', [])),
                "has_attachments": bool(ticket.get('attachments')),
                "escalated": ticket.get('escalated', False)
            }
        )
        
        self.dataset.add(record, generate_embedding=True)
        return record
    
    def _analyze_ticket(self, content: str, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ticket content for insights."""
        analysis = {}
        
        # Sentiment analysis
        blob = TextBlob(content)
        sentiment = blob.sentiment
        
        analysis['sentiment'] = {
            'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity,
            'label': self._get_sentiment_label(sentiment.polarity),
            'score': sentiment.polarity
        }
        
        # Category detection
        category, subcategory = self._detect_category(content)
        analysis['category'] = category
        analysis['subcategory'] = subcategory
        
        # Urgency detection
        analysis['urgency'] = self._detect_urgency(content, ticket)
        
        # Extract key phrases
        analysis['key_phrases'] = self._extract_key_phrases(content)
        
        # Detect customer emotion
        analysis['emotion'] = self._detect_emotion(content)
        
        # Technical indicators
        analysis['contains_error'] = bool(re.search(r'error|exception|traceback', content, re.I))
        analysis['contains_code'] = bool(re.search(r'```|`[^`]+`|\bcode\b', content))
        analysis['contains_screenshot'] = bool(ticket.get('attachments')) and any(
            'image' in str(att.get('type', '')) for att in ticket.get('attachments', [])
        )
        
        # Question analysis
        questions = re.findall(r'[^.!?]*\?', content)
        analysis['question_count'] = len(questions)
        analysis['is_question'] = len(questions) > 0
        
        return analysis
    
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert polarity score to label."""
        if polarity >= 0.3:
            return 'positive'
        elif polarity <= -0.3:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_category(self, content: str) -> Tuple[str, Optional[str]]:
        """Detect ticket category and subcategory."""
        content_lower = content.lower()
        
        # Score each category
        category_scores = {}
        
        for category, keywords in self.issue_categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return 'general', None
        
        # Get primary category
        primary_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Detect subcategory based on specific patterns
        subcategory = None
        if primary_category == 'billing':
            if 'refund' in content_lower:
                subcategory = 'refund_request'
            elif 'upgrade' in content_lower or 'downgrade' in content_lower:
                subcategory = 'plan_change'
            elif 'cancel' in content_lower:
                subcategory = 'cancellation'
                
        elif primary_category == 'technical':
            if 'api' in content_lower:
                subcategory = 'api_issue'
            elif 'performance' in content_lower or 'slow' in content_lower:
                subcategory = 'performance'
            elif 'data' in content_lower and 'loss' in content_lower:
                subcategory = 'data_issue'
        
        return primary_category, subcategory
    
    def _detect_urgency(self, content: str, ticket: Dict[str, Any]) -> str:
        """Detect ticket urgency."""
        content_lower = content.lower()
        
        # Check explicit priority
        if ticket.get('priority'):
            return ticket['priority']
        
        # Check urgency patterns
        for urgency, patterns in self.urgency_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    return urgency
        
        # Check business impact mentions
        if any(phrase in content_lower for phrase in ['business impact', 'losing customers', 'revenue loss']):
            return 'high'
        
        # Default based on sentiment
        sentiment = TextBlob(content).sentiment.polarity
        if sentiment < -0.5:
            return 'high'
        
        return 'medium'
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content."""
        # Simple noun phrase extraction
        blob = TextBlob(content)
        noun_phrases = [str(np).lower() for np in blob.noun_phrases]
        
        # Filter and clean
        key_phrases = []
        for phrase in noun_phrases:
            if len(phrase.split()) <= 4 and len(phrase) > 3:
                key_phrases.append(phrase)
        
        # Get unique phrases
        return list(set(key_phrases))[:10]
    
    def _detect_emotion(self, content: str) -> str:
        """Detect primary emotion in content."""
        content_lower = content.lower()
        
        emotions = {
            'frustrated': ['frustrated', 'annoying', 'irritated', 'fed up'],
            'angry': ['angry', 'furious', 'unacceptable', 'terrible'],
            'confused': ['confused', 'don\'t understand', 'unclear', 'lost'],
            'happy': ['happy', 'pleased', 'great', 'excellent', 'love'],
            'grateful': ['thank', 'appreciate', 'grateful', 'helpful']
        }
        
        emotion_scores = {}
        for emotion, keywords in emotions.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        return 'neutral'
    
    def analyze_support_trends(self, 
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze support trends over time."""
        # Build date filter
        filters = []
        if start_date:
            filters.append(f"metadata.created_at >= '{start_date.isoformat()}'")
        if end_date:
            filters.append(f"metadata.created_at <= '{end_date.isoformat()}'")
        
        filter_str = " AND ".join(filters) if filters else None
        
        # Get tickets
        tickets = self.dataset.sql_filter(filter_str) if filter_str else list(self.dataset.iter_records())
        
        # Analyze trends
        trends = {
            'total_tickets': len(tickets),
            'by_category': defaultdict(int),
            'by_priority': defaultdict(int),
            'by_sentiment': defaultdict(int),
            'by_channel': defaultdict(int),
            'resolution_times': [],
            'satisfaction_scores': [],
            'daily_volume': defaultdict(int),
            'top_issues': Counter(),
            'agent_performance': defaultdict(lambda: {'tickets': 0, 'avg_resolution': 0, 'satisfaction': []})
        }
        
        for ticket in tickets:
            meta = ticket.metadata
            
            # Category distribution
            trends['by_category'][meta.get('category', 'unknown')] += 1
            
            # Priority distribution
            trends['by_priority'][meta.get('priority', 'medium')] += 1
            
            # Sentiment distribution
            trends['by_sentiment'][meta.get('sentiment', 'neutral')] += 1
            
            # Channel distribution
            trends['by_channel'][meta.get('channel', 'unknown')] += 1
            
            # Resolution time
            if meta.get('resolution_time'):
                trends['resolution_times'].append(meta['resolution_time'])
            
            # Satisfaction
            if meta.get('satisfaction_score'):
                trends['satisfaction_scores'].append(meta['satisfaction_score'])
            
            # Daily volume
            if meta.get('created_at'):
                date = meta['created_at'][:10]  # YYYY-MM-DD
                trends['daily_volume'][date] += 1
            
            # Top issues
            for phrase in ticket.context.get('analysis', {}).get('key_phrases', []):
                trends['top_issues'][phrase] += 1
            
            # Agent performance
            agent = meta.get('agent_id')
            if agent:
                trends['agent_performance'][agent]['tickets'] += 1
                if meta.get('resolution_time'):
                    # Simple average (should use proper averaging)
                    trends['agent_performance'][agent]['avg_resolution'] = meta['resolution_time']
                if meta.get('satisfaction_score'):
                    trends['agent_performance'][agent]['satisfaction'].append(meta['satisfaction_score'])
        
        # Calculate aggregates
        trends['avg_resolution_time'] = np.mean(trends['resolution_times']) if trends['resolution_times'] else 0
        trends['avg_satisfaction'] = np.mean(trends['satisfaction_scores']) if trends['satisfaction_scores'] else 0
        trends['top_issues'] = dict(trends['top_issues'].most_common(20))
        
        # Convert defaultdicts to regular dicts
        for key in ['by_category', 'by_priority', 'by_sentiment', 'by_channel', 'daily_volume']:
            trends[key] = dict(trends[key])
        
        # Process agent performance
        agent_metrics = {}
        for agent, data in trends['agent_performance'].items():
            agent_metrics[agent] = {
                'tickets': data['tickets'],
                'avg_resolution': data['avg_resolution'],
                'avg_satisfaction': np.mean(data['satisfaction']) if data['satisfaction'] else 0
            }
        trends['agent_performance'] = agent_metrics
        
        return trends
    
    def identify_problem_areas(self, threshold_negative: float = 0.3) -> Dict[str, Any]:
        """Identify problematic areas needing attention."""
        problems = {
            'high_negative_sentiment': [],
            'long_resolution_times': [],
            'escalated_tickets': [],
            'repeat_issues': defaultdict(list),
            'unresolved_critical': []
        }
        
        # Get all tickets
        tickets = list(self.dataset.iter_records())
        
        # Track customer issues
        customer_issues = defaultdict(list)
        
        for ticket in tickets:
            meta = ticket.metadata
            analysis = ticket.context.get('analysis', {})
            
            # High negative sentiment
            if meta.get('sentiment') == 'negative' and analysis.get('sentiment', {}).get('score', 0) < -threshold_negative:
                problems['high_negative_sentiment'].append({
                    'ticket_id': meta.get('ticket_id'),
                    'subject': meta.get('title'),
                    'sentiment_score': analysis['sentiment']['score'],
                    'category': meta.get('category'),
                    'customer': meta.get('customer_email')
                })
            
            # Long resolution times (> 48 hours)
            if meta.get('resolution_time') and meta['resolution_time'] > 48:
                problems['long_resolution_times'].append({
                    'ticket_id': meta.get('ticket_id'),
                    'resolution_hours': meta['resolution_time'],
                    'category': meta.get('category'),
                    'priority': meta.get('priority')
                })
            
            # Escalated tickets
            if ticket.context.get('escalated'):
                problems['escalated_tickets'].append({
                    'ticket_id': meta.get('ticket_id'),
                    'reason': 'Escalated to higher support tier',
                    'category': meta.get('category')
                })
            
            # Track by customer
            if meta.get('customer_id'):
                customer_issues[meta['customer_id']].append({
                    'ticket_id': meta.get('ticket_id'),
                    'date': meta.get('created_at'),
                    'category': meta.get('category')
                })
            
            # Unresolved critical
            if meta.get('priority') == 'critical' and meta.get('status') != 'resolved':
                problems['unresolved_critical'].append({
                    'ticket_id': meta.get('ticket_id'),
                    'age_hours': self._calculate_age(meta.get('created_at')),
                    'subject': meta.get('title')
                })
        
        # Identify repeat customers
        for customer, issues in customer_issues.items():
            if len(issues) >= 3:  # 3+ tickets
                problems['repeat_issues'][customer] = {
                    'ticket_count': len(issues),
                    'categories': Counter(i['category'] for i in issues),
                    'tickets': [i['ticket_id'] for i in issues]
                }
        
        return dict(problems)
    
    def _calculate_age(self, created_at: Optional[str]) -> float:
        """Calculate age of ticket in hours."""
        if not created_at:
            return 0
        
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.now() - created
            return age.total_seconds() / 3600
        except:
            return 0
    
    def generate_insights_report(self, period_days: int = 30) -> str:
        """Generate comprehensive insights report."""
        start_date = datetime.now() - timedelta(days=period_days)
        
        # Get trends
        trends = self.analyze_support_trends(start_date=start_date)
        problems = self.identify_problem_areas()
        
        # Generate report
        report = f"""# Customer Support Insights Report
        
## Executive Summary
- **Total Tickets**: {trends['total_tickets']} in last {period_days} days
- **Average Resolution Time**: {trends['avg_resolution_time']:.1f} hours
- **Customer Satisfaction**: {trends['avg_satisfaction']:.1f}/5.0

## Ticket Distribution

### By Category
"""
        for category, count in sorted(trends['by_category'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / trends['total_tickets']) * 100
            report += f"- **{category.title()}**: {count} tickets ({percentage:.1f}%)\n"
        
        report += "\n### By Priority\n"
        priority_order = ['critical', 'high', 'medium', 'low']
        for priority in priority_order:
            if priority in trends['by_priority']:
                count = trends['by_priority'][priority]
                percentage = (count / trends['total_tickets']) * 100
                report += f"- **{priority.title()}**: {count} tickets ({percentage:.1f}%)\n"
        
        report += "\n### By Sentiment\n"
        for sentiment, count in trends['by_sentiment'].items():
            percentage = (count / trends['total_tickets']) * 100
            emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😞'}.get(sentiment, '')
            report += f"- **{sentiment.title()}** {emoji}: {count} tickets ({percentage:.1f}%)\n"
        
        report += "\n## Problem Areas Requiring Attention\n\n"
        
        # High negative sentiment
        if problems['high_negative_sentiment']:
            report += f"### High Negative Sentiment ({len(problems['high_negative_sentiment'])} tickets)\n"
            for ticket in problems['high_negative_sentiment'][:5]:
                report += f"- Ticket #{ticket['ticket_id']}: {ticket['subject']} (Score: {ticket['sentiment_score']:.2f})\n"
            report += "\n"
        
        # Long resolution times
        if problems['long_resolution_times']:
            report += f"### Extended Resolution Times ({len(problems['long_resolution_times'])} tickets)\n"
            for ticket in sorted(problems['long_resolution_times'], key=lambda x: x['resolution_hours'], reverse=True)[:5]:
                report += f"- Ticket #{ticket['ticket_id']}: {ticket['resolution_hours']:.1f} hours ({ticket['category']})\n"
            report += "\n"
        
        # Repeat customers
        if problems['repeat_issues']:
            report += f"### Customers with Multiple Issues ({len(problems['repeat_issues'])} customers)\n"
            for customer, data in list(problems['repeat_issues'].items())[:5]:
                categories = ', '.join(f"{cat} ({count})" for cat, count in data['categories'].most_common(3))
                report += f"- Customer {customer}: {data['ticket_count']} tickets - {categories}\n"
            report += "\n"
        
        # Top issues
        report += "## Most Common Issues\n"
        for issue, count in list(trends['top_issues'].items())[:10]:
            report += f"- **{issue}**: {count} occurrences\n"
        
        # Agent performance
        report += "\n## Agent Performance\n"
        agent_list = sorted(
            trends['agent_performance'].items(),
            key=lambda x: x[1]['tickets'],
            reverse=True
        )
        for agent, metrics in agent_list[:10]:
            report += f"- **Agent {agent}**: {metrics['tickets']} tickets, "
            report += f"Avg Resolution: {metrics['avg_resolution']:.1f}h, "
            report += f"Satisfaction: {metrics['avg_satisfaction']:.1f}/5.0\n"
        
        # Recommendations
        report += "\n## Recommendations\n\n"
        
        # Based on data
        if trends['by_category'].get('technical', 0) > trends['total_tickets'] * 0.3:
            report += "1. **Technical Issues Prevalent**: Consider additional technical training or documentation\n"
        
        if trends['avg_resolution_time'] > 24:
            report += "2. **High Resolution Times**: Review support processes and consider automation\n"
        
        if trends['by_sentiment'].get('negative', 0) > trends['total_tickets'] * 0.2:
            report += "3. **Negative Sentiment High**: Implement proactive customer communication\n"
        
        if len(problems['repeat_issues']) > trends['total_tickets'] * 0.1:
            report += "4. **Many Repeat Customers**: Consider customer success outreach program\n"
        
        return report
    
    def create_visualizations(self, output_dir: str = "support_analytics"):
        """Create visualization charts."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Get data
        trends = self.analyze_support_trends()
        
        # 1. Ticket volume over time
        dates = sorted(trends['daily_volume'].keys())
        volumes = [trends['daily_volume'][date] for date in dates]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=volumes,
            mode='lines+markers',
            name='Daily Tickets',
            line=dict(color='blue', width=2)
        ))
        fig.update_layout(
            title='Support Ticket Volume Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Tickets'
        )
        fig.write_html(f"{output_dir}/ticket_volume.html")
        
        # 2. Category distribution
        categories = list(trends['by_category'].keys())
        values = list(trends['by_category'].values())
        
        fig = px.pie(
            values=values,
            names=categories,
            title='Ticket Distribution by Category'
        )
        fig.write_html(f"{output_dir}/category_distribution.html")
        
        # 3. Sentiment analysis
        sentiments = list(trends['by_sentiment'].keys())
        sent_values = list(trends['by_sentiment'].values())
        colors = {'positive': 'green', 'neutral': 'gray', 'negative': 'red'}
        
        fig = go.Figure(data=[
            go.Bar(
                x=sentiments,
                y=sent_values,
                marker_color=[colors.get(s, 'blue') for s in sentiments]
            )
        ])
        fig.update_layout(
            title='Customer Sentiment Distribution',
            xaxis_title='Sentiment',
            yaxis_title='Number of Tickets'
        )
        fig.write_html(f"{output_dir}/sentiment_distribution.html")
        
        # 4. Resolution time distribution
        if trends['resolution_times']:
            fig = go.Figure(data=[
                go.Histogram(
                    x=trends['resolution_times'],
                    nbinsx=20,
                    marker_color='purple'
                )
            ])
            fig.update_layout(
                title='Resolution Time Distribution',
                xaxis_title='Hours to Resolution',
                yaxis_title='Number of Tickets'
            )
            fig.write_html(f"{output_dir}/resolution_times.html")
        
        print(f"Visualizations saved to {output_dir}/")
    
    def predict_ticket_category(self, ticket_content: str) -> Dict[str, float]:
        """Predict ticket category using historical data."""
        # Simple approach - in practice, use ML model
        content_lower = ticket_content.lower()
        
        category_scores = {}
        total_score = 0
        
        for category, keywords in self.issue_categories.items():
            score = sum(2 if keyword in content_lower else 0 for keyword in keywords)
            category_scores[category] = score
            total_score += score
        
        # Normalize to probabilities
        if total_score > 0:
            for category in category_scores:
                category_scores[category] = category_scores[category] / total_score
        else:
            # Default distribution
            for category in self.issue_categories:
                category_scores[category] = 1.0 / len(self.issue_categories)
        
        return category_scores
    
    def suggest_response_template(self, ticket: Dict[str, Any]) -> str:
        """Suggest response template based on ticket analysis."""
        analysis = self._analyze_ticket(
            f"{ticket.get('subject', '')}\n{ticket.get('description', '')}",
            ticket
        )
        
        category = analysis['category']
        sentiment = analysis['sentiment']['label']
        urgency = analysis['urgency']
        
        # Base greeting based on sentiment
        if sentiment == 'negative':
            greeting = "I sincerely apologize for the frustration you're experiencing."
        elif urgency == 'critical':
            greeting = "Thank you for bringing this urgent matter to our attention."
        else:
            greeting = "Thank you for reaching out to us."
        
        # Category-specific content
        templates = {
            'billing': """
{greeting}

I've reviewed your billing inquiry and I'm here to help resolve this for you.

[Specific response to billing issue]

To assist you better, could you please provide:
- Your account number or email
- The specific charge or invoice in question
- Any relevant dates

I'll investigate this immediately and ensure we resolve it to your satisfaction.
""",
            'technical': """
{greeting}

I understand you're experiencing a technical issue, and I'm here to help get this resolved quickly.

[Acknowledge specific issue mentioned]

To troubleshoot this effectively, I'll need:
- Your system/browser information
- Steps to reproduce the issue
- Any error messages you're seeing
- Screenshots if possible

In the meantime, you might try:
- Clearing your browser cache
- Checking our status page for any known issues
- Trying a different browser

I'll work with you to resolve this as quickly as possible.
""",
            'feature': """
{greeting}

Thank you for your feature suggestion! We truly value feedback from users like you as it helps us improve our product.

[Acknowledge specific feature request]

I've documented your request and will share it with our product team. While I can't guarantee implementation or provide a timeline, I want you to know that we take all suggestions seriously.

In the meantime, [suggest any workarounds or similar existing features].

Is there anything else I can help you with today?
"""
        }
        
        template = templates.get(category, """
{greeting}

I've received your message and I'm here to help.

[Address specific concern]

Please let me know if you need any clarification or have additional questions.
""")
        
        return template.format(greeting=greeting)

# Example usage
if __name__ == "__main__":
    # Initialize analytics system
    analytics = SupportAnalytics()
    
    # Sample ticket data
    sample_tickets = [
        {
            'id': '12345',
            'subject': 'Unable to login to my account',
            'description': 'I\'ve been trying to login for the past hour but keep getting an error. This is urgent as I need to access my data for a presentation.',
            'customer_id': 'cust_001',
            'customer_email': 'john@example.com',
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'channel': 'email',
            'messages': [
                {
                    'sender': 'customer',
                    'timestamp': datetime.now().isoformat(),
                    'content': 'I\'ve tried resetting my password but that didn\'t work either.'
                }
            ]
        },
        {
            'id': '12346',
            'subject': 'Refund request for duplicate charge',
            'description': 'I was charged twice for my subscription this month. Please refund the duplicate charge immediately.',
            'customer_id': 'cust_002',
            'customer_email': 'jane@example.com',
            'status': 'resolved',
            'created_at': (datetime.now() - timedelta(days=2)).isoformat(),
            'resolved_at': (datetime.now() - timedelta(hours=4)).isoformat(),
            'resolution_time': 44,  # hours
            'channel': 'chat',
            'satisfaction_score': 4
        }
    ]
    
    # Ingest tickets
    for ticket in sample_tickets:
        analytics.ingest_support_ticket(ticket)
    
    # Analyze trends
    trends = analytics.analyze_support_trends()
    print(f"Total tickets: {trends['total_tickets']}")
    print(f"Categories: {trends['by_category']}")
    print(f"Average satisfaction: {trends['avg_satisfaction']:.2f}")
    
    # Identify problems
    problems = analytics.identify_problem_areas()
    if problems['high_negative_sentiment']:
        print(f"\nHigh negative sentiment tickets: {len(problems['high_negative_sentiment'])}")
    
    # Generate report
    report = analytics.generate_insights_report(period_days=30)
    with open("support_insights.md", "w") as f:
        f.write(report)
    print("\nInsights report saved to support_insights.md")
    
    # Create visualizations
    analytics.create_visualizations()
    
    # Test category prediction
    new_ticket = "I can't connect my Slack integration. Getting API error 401."
    prediction = analytics.predict_ticket_category(new_ticket)
    print(f"\nCategory prediction for new ticket:")
    for cat, prob in sorted(prediction.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {prob:.2%}")
    
    # Suggest response
    template = analytics.suggest_response_template({
        'subject': 'Integration not working',
        'description': new_ticket
    })
    print(f"\nSuggested response template:\n{template}")
```

## Key Concepts

### 1. Multi-Channel Support
- Email tickets
- Chat conversations
- Phone call logs
- Social media mentions
- In-app feedback

### 2. Intelligent Analysis
- Sentiment analysis with TextBlob
- Category auto-detection
- Urgency classification
- Emotion detection
- Key phrase extraction

### 3. Performance Metrics
- Resolution time tracking
- First response time
- Customer satisfaction scores
- Agent performance metrics
- SLA compliance

### 4. Pattern Recognition
- Common issue identification
- Repeat customer detection
- Escalation patterns
- Seasonal trends
- Category evolution

### 5. Actionable Insights
- Problem area identification
- Agent coaching opportunities
- Process improvement suggestions
- Customer experience gaps

## Extensions

### 1. Machine Learning Classification
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

class MLTicketClassifier:
    """ML-based ticket classification."""
    
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000)),
            ('classifier', MultinomialNB())
        ])
        self.is_trained = False
    
    def train(self, tickets: List[FrameRecord]):
        """Train classifier on historical tickets."""
        # Prepare training data
        texts = []
        labels = []
        
        for ticket in tickets:
            if ticket.metadata.get('category'):
                texts.append(ticket.text_content)
                labels.append(ticket.metadata['category'])
        
        if texts:
            self.pipeline.fit(texts, labels)
            self.is_trained = True
    
    def predict(self, text: str) -> Tuple[str, float]:
        """Predict category with confidence."""
        if not self.is_trained:
            raise ValueError("Classifier not trained")
        
        # Predict
        prediction = self.pipeline.predict([text])[0]
        probabilities = self.pipeline.predict_proba([text])[0]
        confidence = max(probabilities)
        
        return prediction, confidence
```

### 2. Automated Response System
```python
class AutoResponder:
    """Automated response system for common issues."""
    
    def __init__(self, analytics: SupportAnalytics):
        self.analytics = analytics
        self.response_templates = self._load_templates()
    
    def should_auto_respond(self, ticket: Dict[str, Any]) -> bool:
        """Determine if ticket qualifies for auto-response."""
        analysis = self.analytics._analyze_ticket(
            f"{ticket.get('subject', '')}\n{ticket.get('description', '')}",
            ticket
        )
        
        # Auto-respond criteria
        if analysis['category'] in ['documentation', 'feature']:
            if analysis['urgency'] in ['low', 'medium']:
                if analysis['sentiment']['label'] != 'negative':
                    return True
        
        return False
    
    def generate_auto_response(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automated response."""
        analysis = self.analytics._analyze_ticket(
            f"{ticket.get('subject', '')}\n{ticket.get('description', '')}",
            ticket
        )
        
        category = analysis['category']
        
        # Get relevant help articles
        help_articles = self._find_help_articles(
            ticket.get('description', ''),
            category
        )
        
        response = {
            'type': 'auto_response',
            'subject': f"Re: {ticket.get('subject', 'Your inquiry')}",
            'body': self._build_response_body(
                category,
                help_articles,
                analysis
            ),
            'attachments': [],
            'follow_up_required': analysis['urgency'] == 'medium'
        }
        
        return response
```

### 3. Predictive Analytics
```python
def predict_resolution_time(self, ticket: Dict[str, Any]) -> float:
    """Predict resolution time for new ticket."""
    # Get similar historical tickets
    similar_tickets = self.find_similar_tickets(
        ticket.get('description', ''),
        limit=20
    )
    
    # Extract resolution times
    resolution_times = []
    for similar in similar_tickets:
        if similar.metadata.get('resolution_time'):
            resolution_times.append(similar.metadata['resolution_time'])
    
    if not resolution_times:
        # Use category average
        category = self._detect_category(ticket.get('description', ''))[0]
        category_tickets = self.dataset.sql_filter(
            f"metadata.category = '{category}' AND metadata.resolution_time IS NOT NULL"
        )
        resolution_times = [t.metadata['resolution_time'] for t in category_tickets]
    
    if resolution_times:
        # Weighted average based on similarity
        return np.average(resolution_times)
    
    return 24.0  # Default 24 hours

def predict_escalation_risk(self, ticket: Dict[str, Any]) -> float:
    """Predict risk of escalation."""
    risk_score = 0.0
    
    analysis = self._analyze_ticket(
        f"{ticket.get('subject', '')}\n{ticket.get('description', '')}",
        ticket
    )
    
    # Risk factors
    if analysis['sentiment']['score'] < -0.5:
        risk_score += 0.3
    
    if analysis['urgency'] in ['critical', 'high']:
        risk_score += 0.3
    
    if analysis['emotion'] in ['angry', 'frustrated']:
        risk_score += 0.2
    
    # Check customer history
    customer_id = ticket.get('customer_id')
    if customer_id:
        history = self.dataset.sql_filter(
            f"metadata.customer_id = '{customer_id}'"
        )
        if len(history) > 5:  # Frequent complainer
            risk_score += 0.2
    
    return min(risk_score, 1.0)
```

### 4. Quality Assurance
```python
class QualityAssurance:
    """Monitor and improve support quality."""
    
    def __init__(self, analytics: SupportAnalytics):
        self.analytics = analytics
        self.quality_criteria = {
            'response_time': {'target': 2, 'weight': 0.2},  # hours
            'resolution_time': {'target': 24, 'weight': 0.2},  # hours
            'satisfaction': {'target': 4.5, 'weight': 0.3},  # out of 5
            'first_contact_resolution': {'target': 0.7, 'weight': 0.3}  # percentage
        }
    
    def score_agent_performance(self, agent_id: str, 
                               period_days: int = 30) -> Dict[str, Any]:
        """Score agent performance."""
        # Get agent's tickets
        agent_tickets = self.analytics.dataset.sql_filter(
            f"metadata.agent_id = '{agent_id}' AND "
            f"metadata.created_at >= '{(datetime.now() - timedelta(days=period_days)).isoformat()}'"
        )
        
        if not agent_tickets:
            return {'score': 0, 'tickets': 0}
        
        # Calculate metrics
        metrics = {
            'response_times': [],
            'resolution_times': [],
            'satisfaction_scores': [],
            'first_contact_resolutions': 0
        }
        
        for ticket in agent_tickets:
            if ticket.metadata.get('first_response_time'):
                metrics['response_times'].append(ticket.metadata['first_response_time'])
            
            if ticket.metadata.get('resolution_time'):
                metrics['resolution_times'].append(ticket.metadata['resolution_time'])
            
            if ticket.metadata.get('satisfaction_score'):
                metrics['satisfaction_scores'].append(ticket.metadata['satisfaction_score'])
            
            if ticket.context.get('message_count', 0) <= 2:
                metrics['first_contact_resolutions'] += 1
        
        # Calculate scores
        total_score = 0
        
        # Response time score
        if metrics['response_times']:
            avg_response = np.mean(metrics['response_times'])
            response_score = min(self.quality_criteria['response_time']['target'] / avg_response, 1.0)
            total_score += response_score * self.quality_criteria['response_time']['weight']
        
        # Resolution time score  
        if metrics['resolution_times']:
            avg_resolution = np.mean(metrics['resolution_times'])
            resolution_score = min(self.quality_criteria['resolution_time']['target'] / avg_resolution, 1.0)
            total_score += resolution_score * self.quality_criteria['resolution_time']['weight']
        
        # Satisfaction score
        if metrics['satisfaction_scores']:
            avg_satisfaction = np.mean(metrics['satisfaction_scores'])
            satisfaction_score = avg_satisfaction / 5.0
            total_score += satisfaction_score * self.quality_criteria['satisfaction']['weight']
        
        # FCR score
        fcr_rate = metrics['first_contact_resolutions'] / len(agent_tickets)
        fcr_score = fcr_rate / self.quality_criteria['first_contact_resolution']['target']
        total_score += fcr_score * self.quality_criteria['first_contact_resolution']['weight']
        
        return {
            'agent_id': agent_id,
            'overall_score': total_score,
            'ticket_count': len(agent_tickets),
            'avg_response_time': np.mean(metrics['response_times']) if metrics['response_times'] else None,
            'avg_resolution_time': np.mean(metrics['resolution_times']) if metrics['resolution_times'] else None,
            'avg_satisfaction': np.mean(metrics['satisfaction_scores']) if metrics['satisfaction_scores'] else None,
            'fcr_rate': fcr_rate
        }
```

### 5. Real-time Dashboard
```python
from flask import Flask, jsonify, render_template
import threading
import time

class SupportDashboard:
    """Real-time support dashboard."""
    
    def __init__(self, analytics: SupportAnalytics):
        self.analytics = analytics
        self.app = Flask(__name__)
        self.setup_routes()
        self.cache = {}
        self.start_background_refresh()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            return jsonify(self.cache.get('stats', {}))
        
        @self.app.route('/api/live_tickets')
        def get_live_tickets():
            # Get tickets from last hour
            recent = self.analytics.dataset.sql_filter(
                f"metadata.created_at >= '{(datetime.now() - timedelta(hours=1)).isoformat()}'"
            )
            
            tickets = []
            for ticket in recent[:10]:
                tickets.append({
                    'id': ticket.metadata.get('ticket_id'),
                    'subject': ticket.metadata.get('title'),
                    'category': ticket.metadata.get('category'),
                    'priority': ticket.metadata.get('priority'),
                    'sentiment': ticket.metadata.get('sentiment'),
                    'age_minutes': self._calculate_age_minutes(ticket.metadata.get('created_at'))
                })
            
            return jsonify(tickets)
    
    def refresh_cache(self):
        """Refresh cached statistics."""
        while True:
            try:
                # Get current stats
                trends = self.analytics.analyze_support_trends()
                problems = self.analytics.identify_problem_areas()
                
                self.cache['stats'] = {
                    'total_open': len([t for t in self.analytics.dataset.iter_records() 
                                      if t.metadata.get('status') == 'open']),
                    'avg_resolution_time': trends['avg_resolution_time'],
                    'satisfaction_score': trends['avg_satisfaction'],
                    'critical_tickets': len(problems['unresolved_critical']),
                    'by_category': trends['by_category'],
                    'by_sentiment': trends['by_sentiment']
                }
            except Exception as e:
                print(f"Cache refresh error: {e}")
            
            time.sleep(60)  # Refresh every minute
    
    def start_background_refresh(self):
        """Start background cache refresh."""
        thread = threading.Thread(target=self.refresh_cache, daemon=True)
        thread.start()
    
    def run(self, host='0.0.0.0', port=5000):
        """Run dashboard server."""
        self.app.run(host=host, port=port)
```

## Best Practices

1. **Data Privacy**: Anonymize customer data appropriately
2. **Regular Analysis**: Run analytics daily/weekly
3. **Action Items**: Convert insights into actionable tasks
4. **Feedback Loop**: Use insights to improve processes
5. **Agent Training**: Use data for targeted training
6. **Automation**: Automate repetitive responses carefully
7. **Customer Focus**: Always prioritize customer experience

## See Also

- [Multi-Source Search](multi-source-search.md) - Searching support data
- [Slack Community Knowledge](slack-knowledge.md) - Analyzing chat support
- [Email Archive Search](email-archive.md) - Email ticket processing
- [API Reference](../api/overview.md) - FrameDataset documentation