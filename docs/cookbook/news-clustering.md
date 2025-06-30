# News Article Clustering

Build an intelligent news aggregation system that clusters related articles, tracks story evolution, identifies trending topics, and provides multi-perspective analysis of news events.

## Problem Statement

News organizations and readers face information overload with thousands of articles published daily across multiple sources. Identifying related stories, tracking narrative evolution, and understanding different perspectives on the same event requires sophisticated clustering and analysis.

## Solution Overview

We'll build a news clustering system that:
1. Ingests articles from multiple news sources
2. Clusters related stories automatically
3. Tracks story evolution over time
4. Identifies bias and different perspectives
5. Generates comprehensive news briefs

## Complete Code

```python
import os
import re
import json
import feedparser
import requests
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from textblob import TextBlob
import hashlib

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class NewsClusteringSystem:
    """Intelligent news article clustering and analysis system."""
    
    def __init__(self, dataset_path: str = "news_clusters.lance"):
        """Initialize news clustering system."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Load NLP model
        self.nlp = spacy.load("en_core_web_sm")
        
        # News sources configuration
        self.news_sources = {
            'bbc': {
                'name': 'BBC News',
                'rss': 'http://feeds.bbci.co.uk/news/rss.xml',
                'bias': 'center',
                'region': 'uk'
            },
            'cnn': {
                'name': 'CNN',
                'rss': 'http://rss.cnn.com/rss/cnn_topstories.rss',
                'bias': 'left-center',
                'region': 'us'
            },
            'foxnews': {
                'name': 'Fox News',
                'rss': 'http://feeds.foxnews.com/foxnews/latest',
                'bias': 'right',
                'region': 'us'
            },
            'reuters': {
                'name': 'Reuters',
                'rss': 'http://feeds.reuters.com/reuters/topNews',
                'bias': 'center',
                'region': 'global'
            },
            'guardian': {
                'name': 'The Guardian',
                'rss': 'https://www.theguardian.com/world/rss',
                'bias': 'left-center',
                'region': 'uk'
            }
        }
        
        # Clustering parameters
        self.min_cluster_size = 3
        self.similarity_threshold = 0.3
        
        # Story tracking
        self.active_stories = {}
        self.story_evolution = defaultdict(list)
        
    def ingest_articles(self, hours_back: int = 24) -> List[FrameRecord]:
        """Ingest articles from all configured news sources."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        ingested_articles = []
        
        for source_id, source_config in self.news_sources.items():
            print(f"Fetching articles from {source_config['name']}")
            
            try:
                # Parse RSS feed
                feed = feedparser.parse(source_config['rss'])
                
                for entry in feed.entries:
                    # Check if article is recent
                    published = datetime(*entry.published_parsed[:6])
                    if published < cutoff_time:
                        continue
                    
                    # Create article record
                    article = self._create_article_record(
                        entry, source_id, source_config
                    )
                    
                    if article:
                        ingested_articles.append(article)
                        self.dataset.add(article, generate_embedding=True)
                        
            except Exception as e:
                print(f"Error fetching from {source_config['name']}: {e}")
        
        print(f"Ingested {len(ingested_articles)} articles")
        
        # Cluster new articles
        if ingested_articles:
            self._cluster_articles(ingested_articles)
        
        return ingested_articles
    
    def _create_article_record(self, entry: Any, 
                             source_id: str,
                             source_config: Dict[str, str]) -> Optional[FrameRecord]:
        """Create article record from RSS entry."""
        # Extract article content
        title = entry.get('title', '')
        summary = entry.get('summary', '')
        link = entry.get('link', '')
        published = datetime(*entry.published_parsed[:6])
        
        # Skip if essential fields missing
        if not title or not link:
            return None
        
        # Generate article ID
        article_id = hashlib.md5(link.encode()).hexdigest()
        
        # Check if already exists
        existing = self.dataset.filter({'metadata.article_id': article_id})
        if existing:
            return None
        
        # Extract full content if available
        content = f"{title}\n\n{summary}"
        
        # Extract entities
        entities = self._extract_entities(content)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(content)
        
        # Extract keywords
        keywords = self._extract_keywords(content)
        
        # Create metadata
        metadata = create_metadata(
            title=title,
            source="news_article",
            article_id=article_id,
            url=link,
            source_name=source_config['name'],
            source_id=source_id,
            source_bias=source_config['bias'],
            source_region=source_config['region'],
            published_date=published.isoformat(),
            ingested_date=datetime.now().isoformat(),
            
            # Content analysis
            entities=entities,
            keywords=keywords,
            sentiment=sentiment,
            
            # Clustering info (to be updated)
            cluster_id=None,
            story_id=None,
            is_duplicate=False,
            is_update=False
        )
        
        # Create record
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        return record
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        doc = self.nlp(text)
        
        entities = defaultdict(set)
        for ent in doc.ents:
            entities[ent.label_].add(ent.text)
        
        return {k: list(v) for k, v in entities.items()}
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text."""
        blob = TextBlob(text)
        
        return {
            'polarity': blob.sentiment.polarity,  # -1 to 1
            'subjectivity': blob.sentiment.subjectivity,  # 0 to 1
            'sentiment_label': self._get_sentiment_label(blob.sentiment.polarity)
        }
    
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert polarity score to label."""
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract keywords using TF-IDF."""
        # Simple keyword extraction - in production use more sophisticated methods
        doc = self.nlp(text.lower())
        
        # Extract noun phrases and important words
        keywords = []
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                keywords.append(token.lemma_)
        
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:
                keywords.append(chunk.text.lower())
        
        # Count frequency and return top keywords
        keyword_counts = Counter(keywords)
        return [kw for kw, _ in keyword_counts.most_common(num_keywords)]
    
    def _cluster_articles(self, new_articles: List[FrameRecord]):
        """Cluster articles into related stories."""
        # Get recent articles for clustering
        cutoff = datetime.now() - timedelta(hours=48)
        recent_articles = self.dataset.filter({
            'metadata.source': 'news_article',
            'metadata.published_date': {'gte': cutoff.isoformat()}
        })
        
        if len(recent_articles) < self.min_cluster_size:
            return
        
        # Prepare texts for clustering
        texts = [article.text_content for article in recent_articles]
        article_ids = [article.unique_id for article in recent_articles]
        
        # Vectorize texts
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(X)
        
        # Cluster using DBSCAN
        clustering = DBSCAN(
            eps=1 - self.similarity_threshold,
            min_samples=self.min_cluster_size,
            metric='precomputed'
        ).fit(1 - similarity_matrix)
        
        # Update article clusters
        cluster_updates = defaultdict(list)
        
        for idx, (article_id, cluster_label) in enumerate(zip(article_ids, clustering.labels_)):
            if cluster_label != -1:  # Not noise
                cluster_updates[cluster_label].append((idx, article_id))
        
        # Process each cluster
        for cluster_label, article_indices in cluster_updates.items():
            cluster_id = f"cluster_{datetime.now().strftime('%Y%m%d')}_{cluster_label}"
            
            # Check if this is an existing story
            story_id = self._find_or_create_story(
                [recent_articles[idx] for idx, _ in article_indices],
                cluster_id
            )
            
            # Update articles with cluster info
            for idx, article_id in article_indices:
                article = recent_articles[idx]
                article.metadata.custom_metadata['cluster_id'] = cluster_id
                article.metadata.custom_metadata['story_id'] = story_id
                
                # Check for duplicates within cluster
                is_duplicate = self._check_duplicate(
                    idx, article_indices, similarity_matrix
                )
                article.metadata.custom_metadata['is_duplicate'] = is_duplicate
                
                self.dataset.update(article)
    
    def _find_or_create_story(self, cluster_articles: List[FrameRecord],
                            cluster_id: str) -> str:
        """Find existing story or create new one."""
        # Extract common entities across articles
        all_entities = defaultdict(Counter)
        for article in cluster_articles:
            entities = article.metadata.custom_metadata.get('entities', {})
            for ent_type, ent_list in entities.items():
                for entity in ent_list:
                    all_entities[ent_type][entity] += 1
        
        # Get most common entities
        key_entities = {
            ent_type: [ent for ent, count in counter.most_common(3)]
            for ent_type, counter in all_entities.items()
        }
        
        # Try to match with existing stories
        for story_id, story_info in self.active_stories.items():
            similarity = self._calculate_story_similarity(
                key_entities, story_info['entities']
            )
            
            if similarity > 0.5:
                # Update existing story
                self._update_story(story_id, cluster_articles)
                return story_id
        
        # Create new story
        story_id = self._create_story(cluster_articles, key_entities)
        return story_id
    
    def _calculate_story_similarity(self, entities1: Dict[str, List[str]],
                                  entities2: Dict[str, List[str]]) -> float:
        """Calculate similarity between two entity sets."""
        all_entities1 = set()
        all_entities2 = set()
        
        for ent_list in entities1.values():
            all_entities1.update(ent_list)
        
        for ent_list in entities2.values():
            all_entities2.update(ent_list)
        
        if not all_entities1 or not all_entities2:
            return 0.0
        
        intersection = len(all_entities1 & all_entities2)
        union = len(all_entities1 | all_entities2)
        
        return intersection / union if union > 0 else 0.0
    
    def _create_story(self, articles: List[FrameRecord],
                     key_entities: Dict[str, List[str]]) -> str:
        """Create new story from article cluster."""
        story_id = generate_uuid()
        
        # Generate story title
        title = self._generate_story_title(articles, key_entities)
        
        # Create story record
        metadata = create_metadata(
            title=title,
            source="news_story",
            story_id=story_id,
            created_date=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            key_entities=key_entities,
            article_count=len(articles),
            sources=list(set(a.metadata.custom_metadata['source_name'] for a in articles)),
            bias_distribution=self._calculate_bias_distribution(articles),
            sentiment_trend=self._calculate_sentiment_trend(articles),
            evolution_stage="emerging"
        )
        
        # Create story summary
        summary = self._generate_story_summary(articles)
        
        story_record = FrameRecord(
            text_content=summary,
            metadata=metadata,
            unique_id=story_id,
            record_type="collection_header"
        )
        
        self.dataset.add(story_record, generate_embedding=True)
        
        # Track active story
        self.active_stories[story_id] = {
            'entities': key_entities,
            'created': datetime.now(),
            'article_count': len(articles)
        }
        
        # Create relationships to articles
        for article in articles:
            story_record.metadata = add_relationship_to_metadata(
                story_record.metadata,
                create_relationship(
                    source_id=article.unique_id,
                    target_id=story_id,
                    relationship_type="member_of"
                )
            )
        
        return story_id
    
    def _update_story(self, story_id: str, new_articles: List[FrameRecord]):
        """Update existing story with new articles."""
        story = self.dataset.get(story_id)
        if not story:
            return
        
        # Update article count
        story.metadata.custom_metadata['article_count'] += len(new_articles)
        story.metadata.custom_metadata['last_updated'] = datetime.now().isoformat()
        
        # Update sources
        current_sources = set(story.metadata.custom_metadata.get('sources', []))
        new_sources = set(a.metadata.custom_metadata['source_name'] for a in new_articles)
        story.metadata.custom_metadata['sources'] = list(current_sources | new_sources)
        
        # Update bias distribution
        all_articles = self._get_story_articles(story_id)
        story.metadata.custom_metadata['bias_distribution'] = self._calculate_bias_distribution(all_articles)
        
        # Update evolution stage
        story.metadata.custom_metadata['evolution_stage'] = self._determine_evolution_stage(all_articles)
        
        # Regenerate summary
        story.text_content = self._generate_story_summary(all_articles)
        
        self.dataset.update(story)
        
        # Track evolution
        self.story_evolution[story_id].append({
            'timestamp': datetime.now().isoformat(),
            'new_articles': len(new_articles),
            'total_articles': len(all_articles),
            'stage': story.metadata.custom_metadata['evolution_stage']
        })
    
    def _generate_story_title(self, articles: List[FrameRecord],
                            key_entities: Dict[str, List[str]]) -> str:
        """Generate descriptive title for story."""
        # Get most common keywords across articles
        all_keywords = []
        for article in articles:
            keywords = article.metadata.custom_metadata.get('keywords', [])
            all_keywords.extend(keywords)
        
        keyword_counts = Counter(all_keywords)
        top_keywords = [kw for kw, _ in keyword_counts.most_common(3)]
        
        # Include key entities
        key_people = key_entities.get('PERSON', [])[:1]
        key_orgs = key_entities.get('ORG', [])[:1]
        key_locations = key_entities.get('GPE', [])[:1]
        
        # Build title
        title_parts = []
        if key_people:
            title_parts.extend(key_people)
        if key_orgs:
            title_parts.extend(key_orgs)
        if key_locations:
            title_parts.extend(key_locations)
        
        if title_parts:
            title = f"{' and '.join(title_parts)}: {' '.join(top_keywords[:2])}"
        else:
            title = ' '.join(top_keywords[:4])
        
        return title.title()
    
    def _generate_story_summary(self, articles: List[FrameRecord]) -> str:
        """Generate comprehensive story summary."""
        # Sort articles by date
        articles.sort(key=lambda x: x.metadata.custom_metadata.get('published_date', ''))
        
        summary_parts = ["# Story Summary\n"]
        
        # Add key facts
        summary_parts.append("## Key Facts")
        
        # Extract common entities
        entity_counts = defaultdict(Counter)
        for article in articles:
            entities = article.metadata.custom_metadata.get('entities', {})
            for ent_type, ent_list in entities.items():
                for entity in ent_list:
                    entity_counts[ent_type][entity] += 1
        
        # Add most mentioned entities
        for ent_type in ['PERSON', 'ORG', 'GPE']:
            if ent_type in entity_counts:
                top_entities = [ent for ent, _ in entity_counts[ent_type].most_common(3)]
                if top_entities:
                    summary_parts.append(f"- **{ent_type}**: {', '.join(top_entities)}")
        
        # Add timeline
        summary_parts.append("\n## Timeline")
        for article in articles[-5:]:  # Last 5 articles
            date = article.metadata.custom_metadata.get('published_date', '')
            if date:
                date_str = datetime.fromisoformat(date).strftime('%Y-%m-%d %H:%M')
                source = article.metadata.custom_metadata.get('source_name', 'Unknown')
                summary_parts.append(f"- **{date_str}** ({source}): {article.metadata.title}")
        
        # Add perspective analysis
        bias_dist = self._calculate_bias_distribution(articles)
        if bias_dist:
            summary_parts.append("\n## Coverage Analysis")
            for bias, percentage in bias_dist.items():
                summary_parts.append(f"- {bias}: {percentage:.1f}%")
        
        return "\n".join(summary_parts)
    
    def _calculate_bias_distribution(self, articles: List[FrameRecord]) -> Dict[str, float]:
        """Calculate distribution of source bias."""
        bias_counts = Counter()
        
        for article in articles:
            bias = article.metadata.custom_metadata.get('source_bias', 'unknown')
            bias_counts[bias] += 1
        
        total = sum(bias_counts.values())
        
        return {
            bias: (count / total) * 100
            for bias, count in bias_counts.items()
        } if total > 0 else {}
    
    def _calculate_sentiment_trend(self, articles: List[FrameRecord]) -> List[Dict[str, Any]]:
        """Calculate sentiment trend over time."""
        # Sort by date
        articles.sort(key=lambda x: x.metadata.custom_metadata.get('published_date', ''))
        
        trend = []
        for article in articles:
            sentiment = article.metadata.custom_metadata.get('sentiment', {})
            trend.append({
                'date': article.metadata.custom_metadata.get('published_date'),
                'polarity': sentiment.get('polarity', 0),
                'source': article.metadata.custom_metadata.get('source_name')
            })
        
        return trend
    
    def _determine_evolution_stage(self, articles: List[FrameRecord]) -> str:
        """Determine story evolution stage."""
        article_count = len(articles)
        
        # Calculate time span
        dates = [
            datetime.fromisoformat(a.metadata.custom_metadata.get('published_date'))
            for a in articles
            if a.metadata.custom_metadata.get('published_date')
        ]
        
        if not dates:
            return "emerging"
        
        time_span = max(dates) - min(dates)
        
        # Determine stage
        if article_count < 5:
            return "emerging"
        elif article_count < 20 and time_span.days < 3:
            return "developing"
        elif article_count >= 20 or time_span.days >= 3:
            return "mature"
        else:
            return "developing"
    
    def _check_duplicate(self, article_idx: int,
                        cluster_indices: List[Tuple[int, str]],
                        similarity_matrix: np.ndarray) -> bool:
        """Check if article is duplicate within cluster."""
        for other_idx, _ in cluster_indices:
            if other_idx != article_idx:
                if similarity_matrix[article_idx, other_idx] > 0.9:
                    return True
        return False
    
    def _get_story_articles(self, story_id: str) -> List[FrameRecord]:
        """Get all articles belonging to a story."""
        return self.dataset.filter({
            'metadata.story_id': story_id
        })
    
    def get_trending_stories(self, hours: int = 6) -> List[Dict[str, Any]]:
        """Get currently trending stories."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Get recent stories
        recent_stories = self.dataset.filter({
            'metadata.source': 'news_story',
            'metadata.last_updated': {'gte': cutoff.isoformat()}
        })
        
        trending = []
        
        for story in recent_stories:
            meta = story.metadata.custom_metadata
            
            # Calculate trending score
            article_count = meta.get('article_count', 0)
            source_diversity = len(meta.get('sources', []))
            
            # Check evolution
            evolution = self.story_evolution.get(story.unique_id, [])
            recent_growth = sum(
                e['new_articles'] for e in evolution
                if datetime.fromisoformat(e['timestamp']) > cutoff
            )
            
            trending_score = (article_count * 0.5 + 
                            source_diversity * 2 + 
                            recent_growth * 3)
            
            trending.append({
                'story_id': story.unique_id,
                'title': story.metadata.title,
                'article_count': article_count,
                'sources': meta.get('sources', []),
                'stage': meta.get('evolution_stage'),
                'trending_score': trending_score,
                'key_entities': meta.get('key_entities', {})
            })
        
        # Sort by trending score
        return sorted(trending, key=lambda x: x['trending_score'], reverse=True)
    
    def analyze_story_perspectives(self, story_id: str) -> Dict[str, Any]:
        """Analyze different perspectives on a story."""
        articles = self._get_story_articles(story_id)
        
        if not articles:
            return {}
        
        # Group by source bias
        perspectives = defaultdict(list)
        for article in articles:
            bias = article.metadata.custom_metadata.get('source_bias', 'unknown')
            perspectives[bias].append(article)
        
        # Analyze each perspective
        analysis = {
            'story_id': story_id,
            'total_articles': len(articles),
            'perspectives': {}
        }
        
        for bias, bias_articles in perspectives.items():
            # Calculate average sentiment
            sentiments = [
                a.metadata.custom_metadata.get('sentiment', {}).get('polarity', 0)
                for a in bias_articles
            ]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            # Extract common keywords
            all_keywords = []
            for article in bias_articles:
                keywords = article.metadata.custom_metadata.get('keywords', [])
                all_keywords.extend(keywords)
            
            keyword_counts = Counter(all_keywords)
            top_keywords = [kw for kw, _ in keyword_counts.most_common(5)]
            
            analysis['perspectives'][bias] = {
                'article_count': len(bias_articles),
                'average_sentiment': avg_sentiment,
                'sentiment_label': self._get_sentiment_label(avg_sentiment),
                'top_keywords': top_keywords,
                'sources': list(set(
                    a.metadata.custom_metadata.get('source_name')
                    for a in bias_articles
                ))
            }
        
        # Calculate perspective diversity score
        if len(perspectives) > 1:
            # Higher score for more diverse perspectives
            analysis['diversity_score'] = len(perspectives) / 5.0  # Normalize by max expected
        else:
            analysis['diversity_score'] = 0.0
        
        return analysis
    
    def generate_news_brief(self, hours: int = 24) -> str:
        """Generate comprehensive news brief."""
        # Get trending stories
        trending = self.get_trending_stories(hours)[:10]
        
        brief_parts = [
            f"# News Brief - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"\nCovering the last {hours} hours\n"
        ]
        
        # Add trending stories
        brief_parts.append("## Top Stories\n")
        
        for i, story in enumerate(trending, 1):
            brief_parts.append(f"### {i}. {story['title']}")
            brief_parts.append(f"- **Coverage**: {story['article_count']} articles from {len(story['sources'])} sources")
            brief_parts.append(f"- **Status**: {story['stage'].title()}")
            
            # Add key entities
            entities = story['key_entities']
            if entities:
                entity_str = []
                for ent_type, ent_list in entities.items():
                    if ent_list:
                        entity_str.append(f"{ent_type}: {', '.join(ent_list[:2])}")
                if entity_str:
                    brief_parts.append(f"- **Key Players**: {'; '.join(entity_str)}")
            
            # Add perspective analysis
            perspectives = self.analyze_story_perspectives(story['story_id'])
            if perspectives.get('diversity_score', 0) > 0.4:
                brief_parts.append("- **Note**: Multiple perspectives available")
            
            brief_parts.append("")
        
        return "\n".join(brief_parts)

# Example usage
if __name__ == "__main__":
    # Initialize system
    news_system = NewsClusteringSystem()
    
    # Ingest articles from last 24 hours
    articles = news_system.ingest_articles(hours_back=24)
    print(f"Processed {len(articles)} new articles")
    
    # Get trending stories
    trending = news_system.get_trending_stories(hours=6)
    
    print("\nTrending Stories:")
    for story in trending[:5]:
        print(f"\n{story['title']}")
        print(f"  Articles: {story['article_count']}")
        print(f"  Sources: {', '.join(story['sources'])}")
        print(f"  Stage: {story['stage']}")
    
    # Analyze perspectives on top story
    if trending:
        top_story = trending[0]
        perspectives = news_system.analyze_story_perspectives(top_story['story_id'])
        
        print(f"\nPerspective Analysis: {top_story['title']}")
        print(f"Diversity Score: {perspectives['diversity_score']:.2f}")
        
        for bias, analysis in perspectives['perspectives'].items():
            print(f"\n{bias.upper()} perspective:")
            print(f"  Articles: {analysis['article_count']}")
            print(f"  Sentiment: {analysis['sentiment_label']}")
            print(f"  Keywords: {', '.join(analysis['top_keywords'][:3])}")
    
    # Generate news brief
    brief = news_system.generate_news_brief(hours=24)
    print(f"\n{brief}")
```

## Key Concepts

### Intelligent Clustering

The system uses advanced clustering techniques:
- **TF-IDF Vectorization**: Convert articles to numerical representations
- **DBSCAN Clustering**: Density-based clustering for flexible groups
- **Entity Matching**: Group by common people, organizations, locations
- **Temporal Proximity**: Consider publication time in clustering

### Story Evolution Tracking

Stories are tracked through their lifecycle:
- **Emerging**: New stories with few articles
- **Developing**: Growing coverage across sources
- **Mature**: Established stories with comprehensive coverage
- **Historical Context**: Link to related past events

### Perspective Analysis

Multi-perspective understanding:
- **Source Bias Tracking**: Left, center, right perspectives
- **Sentiment Analysis**: How different sources frame the story
- **Keyword Differences**: Language variations across perspectives
- **Geographic Variations**: Regional coverage differences

## Extensions

### Advanced Features

1. **Real-time Processing**
   - Stream processing for breaking news
   - Push notifications for story updates
   - Live clustering adjustments
   - Trend prediction

2. **Deep Analysis**
   - Fact checking integration
   - Quote extraction and attribution
   - Image analysis for visual stories
   - Video transcript inclusion

3. **Personalization**
   - User interest profiling
   - Customized news briefs
   - Perspective preferences
   - Topic subscriptions

4. **Verification**
   - Source credibility scoring
   - Claim verification
   - Image reverse search
   - Cross-reference checking

### Integration Options

1. **News Sources**
   - RSS/Atom feeds
   - News APIs (NewsAPI, GDELT)
   - Social media monitoring
   - Press release wires

2. **Analysis Tools**
   - Named entity recognition
   - Sentiment analysis
   - Topic modeling
   - Fake news detection

3. **Distribution**
   - Email newsletters
   - Mobile push notifications
   - Slack/Teams integration
   - API for third-party apps

## Best Practices

1. **Content Quality**
   - Verify source reliability
   - Handle paywall content ethically
   - Respect robots.txt
   - Attribute sources properly

2. **Clustering Accuracy**
   - Regular parameter tuning
   - Manual verification sampling
   - Feedback incorporation
   - Performance monitoring

3. **Bias Mitigation**
   - Diverse source selection
   - Transparent bias labeling
   - Balanced perspective presentation
   - Regular bias audits

4. **Performance**
   - Incremental clustering
   - Caching strategies
   - Distributed processing
   - Database optimization

This news clustering system provides intelligent aggregation and analysis of news content, helping readers understand complex stories from multiple perspectives.