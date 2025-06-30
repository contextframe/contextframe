# Podcast Episode Index

Build a comprehensive podcast discovery and search system that transcribes episodes, extracts key topics, identifies speakers, and enables deep searching across podcast content.

## Problem Statement

Podcast listeners and researchers struggle to find specific information within the millions of hours of podcast content. Traditional search only covers titles and descriptions, missing the rich discussions within episodes. A comprehensive index enables discovery of specific topics, quotes, and insights buried in audio content.

## Solution Overview

We'll build a podcast indexing system that:
1. Ingests podcasts from multiple sources (RSS, APIs)
2. Transcribes audio with speaker diarization
3. Extracts topics, entities, and key moments
4. Enables timestamp-specific search
5. Provides episode recommendations and insights

## Complete Code

```python
import os
import re
import json
import feedparser
import requests
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import whisper
import librosa
import soundfile as sf
from pydub import AudioSegment
from collections import defaultdict, Counter
import spacy
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class PodcastIndexSystem:
    """Comprehensive podcast indexing and search system."""
    
    def __init__(self, dataset_path: str = "podcast_index.lance"):
        """Initialize podcast index system."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Load models
        self.whisper_model = whisper.load_model("base")
        self.nlp = spacy.load("en_core_web_sm")
        
        # Podcast sources
        self.podcast_directories = {
            'apple': 'https://itunes.apple.com/lookup',
            'spotify': 'https://api.spotify.com/v1/shows',
            'rss': 'direct_feed'
        }
        
        # Episode processing settings
        self.segment_duration = 300  # 5 minutes
        self.min_segment_words = 50
        
        # Topic extraction patterns
        self.topic_indicators = [
            r"today we're (?:talking about|discussing|covering)\s+(.+)",
            r"our topic (?:today|for this episode) is\s+(.+)",
            r"we're going to (?:talk about|discuss|explore)\s+(.+)",
            r"let's (?:talk about|discuss|dive into)\s+(.+)"
        ]
        
        # Speaker patterns
        self.speaker_indicators = [
            r"(?:my name is|i'm|this is)\s+([A-Z][a-z]+ [A-Z][a-z]+)",
            r"(?:host|guest|joining us)(?:ed by)?\s+([A-Z][a-z]+ [A-Z][a-z]+)",
            r"(?:with|interview(?:ing)?)\s+([A-Z][a-z]+ [A-Z][a-z]+)"
        ]
        
    def index_podcast(self, feed_url: str,
                     podcast_name: Optional[str] = None,
                     max_episodes: int = 10) -> List[FrameRecord]:
        """Index podcast episodes from RSS feed."""
        print(f"Indexing podcast from: {feed_url}")
        
        # Parse RSS feed
        feed = feedparser.parse(feed_url)
        
        # Extract podcast metadata
        podcast_info = {
            'title': podcast_name or feed.feed.get('title', 'Unknown Podcast'),
            'description': feed.feed.get('description', ''),
            'author': feed.feed.get('author', ''),
            'language': feed.feed.get('language', 'en'),
            'categories': self._extract_categories(feed.feed),
            'image': feed.feed.get('image', {}).get('href', '')
        }
        
        # Create podcast record
        podcast_record = self._create_podcast_record(podcast_info, feed_url)
        
        # Process episodes
        episode_records = []
        episodes_to_process = feed.entries[:max_episodes]
        
        for entry in episodes_to_process:
            try:
                episode_record = self._process_episode(
                    entry, 
                    podcast_record.unique_id,
                    podcast_info
                )
                if episode_record:
                    episode_records.append(episode_record)
            except Exception as e:
                print(f"Error processing episode: {e}")
                continue
        
        print(f"Indexed {len(episode_records)} episodes")
        
        return [podcast_record] + episode_records
    
    def _extract_categories(self, feed_info: Dict[str, Any]) -> List[str]:
        """Extract podcast categories from feed."""
        categories = []
        
        # iTunes categories
        if 'itunes_category' in feed_info:
            cat = feed_info['itunes_category']
            if isinstance(cat, list):
                categories.extend([c.get('text', '') for c in cat])
            elif isinstance(cat, dict):
                categories.append(cat.get('text', ''))
        
        # Regular categories
        if 'tags' in feed_info:
            for tag in feed_info['tags']:
                if 'term' in tag:
                    categories.append(tag['term'])
        
        return list(set(categories))
    
    def _create_podcast_record(self, podcast_info: Dict[str, Any],
                             feed_url: str) -> FrameRecord:
        """Create podcast collection record."""
        metadata = create_metadata(
            title=podcast_info['title'],
            source="podcast",
            feed_url=feed_url,
            author=podcast_info['author'],
            description=podcast_info['description'],
            language=podcast_info['language'],
            categories=podcast_info['categories'],
            image_url=podcast_info['image'],
            created_date=datetime.now().isoformat(),
            episode_count=0,
            total_duration_hours=0
        )
        
        record = FrameRecord(
            text_content=f"{podcast_info['title']}\n\n{podcast_info['description']}",
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="collection_header"
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        return record
    
    def _process_episode(self, entry: Dict[str, Any],
                        podcast_id: str,
                        podcast_info: Dict[str, Any]) -> Optional[FrameRecord]:
        """Process individual podcast episode."""
        # Extract episode metadata
        title = entry.get('title', 'Untitled Episode')
        description = entry.get('summary', '')
        published = entry.get('published_parsed')
        duration = self._parse_duration(entry)
        
        # Get audio URL
        audio_url = self._extract_audio_url(entry)
        if not audio_url:
            print(f"No audio URL found for: {title}")
            return None
        
        # Check if already processed
        episode_hash = hashlib.md5(audio_url.encode()).hexdigest()
        existing = self.dataset.filter({'metadata.episode_hash': episode_hash})
        if existing:
            print(f"Episode already indexed: {title}")
            return None
        
        print(f"Processing episode: {title}")
        
        # Download and process audio
        try:
            audio_path = self._download_audio(audio_url, episode_hash)
            
            # Transcribe audio
            transcript_segments = self._transcribe_episode(audio_path)
            
            # Process transcript
            processed_segments = self._process_transcript(
                transcript_segments,
                title,
                description
            )
            
            # Extract episode insights
            insights = self._extract_episode_insights(
                processed_segments,
                title,
                description
            )
            
            # Create episode record
            episode_record = self._create_episode_record(
                title=title,
                description=description,
                audio_url=audio_url,
                episode_hash=episode_hash,
                published=published,
                duration=duration,
                podcast_id=podcast_id,
                podcast_info=podcast_info,
                insights=insights
            )
            
            # Create segment records
            self._create_segment_records(
                processed_segments,
                episode_record.unique_id,
                audio_url
            )
            
            # Clean up
            os.remove(audio_path)
            
            return episode_record
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            return None
    
    def _parse_duration(self, entry: Dict[str, Any]) -> int:
        """Parse episode duration in seconds."""
        # iTunes duration
        if 'itunes_duration' in entry:
            duration_str = entry['itunes_duration']
            if ':' in duration_str:
                parts = duration_str.split(':')
                if len(parts) == 3:  # HH:MM:SS
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                elif len(parts) == 2:  # MM:SS
                    return int(parts[0]) * 60 + int(parts[1])
            else:
                return int(duration_str)
        
        return 0
    
    def _extract_audio_url(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract audio URL from episode entry."""
        # Check enclosures
        if 'enclosures' in entry:
            for enclosure in entry['enclosures']:
                if enclosure.get('type', '').startswith('audio/'):
                    return enclosure.get('href')
        
        # Check links
        if 'links' in entry:
            for link in entry['links']:
                if link.get('type', '').startswith('audio/'):
                    return link.get('href')
                
        return None
    
    def _download_audio(self, audio_url: str, episode_hash: str) -> str:
        """Download audio file for processing."""
        audio_path = f"temp_audio_{episode_hash}.mp3"
        
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        
        with open(audio_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return audio_path
    
    def _transcribe_episode(self, audio_path: str) -> List[Dict[str, Any]]:
        """Transcribe podcast episode with timestamps."""
        print("Transcribing audio...")
        
        # Load audio
        audio = AudioSegment.from_file(audio_path)
        
        # Convert to format suitable for Whisper
        temp_wav = "temp_audio.wav"
        audio.export(temp_wav, format="wav", parameters=["-ar", "16000"])
        
        # Transcribe
        result = self.whisper_model.transcribe(
            temp_wav,
            language="en",
            verbose=False
        )
        
        # Clean up
        os.remove(temp_wav)
        
        return result['segments']
    
    def _process_transcript(self, segments: List[Dict[str, Any]],
                          title: str,
                          description: str) -> List[Dict[str, Any]]:
        """Process transcript segments with NLP analysis."""
        processed_segments = []
        current_chunk = {
            'start': 0,
            'end': 0,
            'text': [],
            'segments': []
        }
        
        for segment in segments:
            # Add to current chunk
            current_chunk['segments'].append(segment)
            current_chunk['text'].append(segment['text'])
            current_chunk['end'] = segment['end']
            
            # Check if chunk is complete
            if (segment['end'] - current_chunk['start']) >= self.segment_duration:
                # Process chunk
                processed = self._process_chunk(current_chunk, title)
                processed_segments.append(processed)
                
                # Start new chunk
                current_chunk = {
                    'start': segment['end'],
                    'end': segment['end'],
                    'text': [],
                    'segments': []
                }
        
        # Process final chunk
        if current_chunk['text']:
            processed = self._process_chunk(current_chunk, title)
            processed_segments.append(processed)
        
        return processed_segments
    
    def _process_chunk(self, chunk: Dict[str, Any], 
                      episode_title: str) -> Dict[str, Any]:
        """Process a transcript chunk with NLP."""
        text = ' '.join(chunk['text'])
        
        # NLP analysis
        doc = self.nlp(text)
        
        # Extract entities
        entities = defaultdict(set)
        for ent in doc.ents:
            entities[ent.label_].add(ent.text)
        
        # Extract potential speakers
        speakers = self._extract_speakers(text)
        
        # Extract topics
        topics = self._extract_topics_from_text(text)
        
        # Calculate importance score
        importance_score = self._calculate_segment_importance(
            text, episode_title, topics, entities
        )
        
        return {
            'start_time': chunk['start'],
            'end_time': chunk['end'],
            'duration': chunk['end'] - chunk['start'],
            'text': text,
            'word_count': len(text.split()),
            'entities': {k: list(v) for k, v in entities.items()},
            'speakers': speakers,
            'topics': topics,
            'importance_score': importance_score,
            'key_phrases': self._extract_key_phrases(doc)
        }
    
    def _extract_speakers(self, text: str) -> List[str]:
        """Extract speaker names from text."""
        speakers = set()
        
        for pattern in self.speaker_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            speakers.update(matches)
        
        # Also look for dialogue patterns
        dialogue_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):(?:\s|$)'
        for line in text.split('\n'):
            match = re.match(dialogue_pattern, line)
            if match:
                speakers.add(match.group(1))
        
        return list(speakers)
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text segment."""
        topics = []
        text_lower = text.lower()
        
        # Check topic indicators
        for pattern in self.topic_indicators:
            matches = re.findall(pattern, text_lower)
            topics.extend([m.strip().split('.')[0] for m in matches])
        
        # Extract noun phrases as potential topics
        doc = self.nlp(text)
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks
                       if len(chunk.text.split()) <= 4 and len(chunk.text) > 10]
        
        # Get most common meaningful phrases
        phrase_counts = Counter(noun_phrases)
        topics.extend([phrase for phrase, count in phrase_counts.most_common(5)
                      if count >= 2])
        
        return list(set(topics))[:10]
    
    def _calculate_segment_importance(self, text: str,
                                    episode_title: str,
                                    topics: List[str],
                                    entities: Dict[str, List[str]]) -> float:
        """Calculate importance score for segment."""
        score = 0.0
        
        # Length factor
        word_count = len(text.split())
        if word_count > 100:
            score += 0.2
        
        # Topic richness
        if len(topics) >= 3:
            score += 0.3
        
        # Entity richness
        total_entities = sum(len(v) for v in entities.values())
        if total_entities >= 5:
            score += 0.2
        
        # Key phrases
        importance_phrases = [
            'important', 'key point', 'main thing', 'remember',
            'takeaway', 'lesson', 'insight', 'discovery'
        ]
        
        text_lower = text.lower()
        for phrase in importance_phrases:
            if phrase in text_lower:
                score += 0.1
        
        # Title relevance
        title_words = set(episode_title.lower().split())
        text_words = set(text_lower.split())
        overlap = len(title_words & text_words) / len(title_words) if title_words else 0
        score += overlap * 0.2
        
        return min(score, 1.0)
    
    def _extract_key_phrases(self, doc) -> List[str]:
        """Extract key phrases from spaCy doc."""
        key_phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if 2 <= len(chunk.text.split()) <= 4:
                key_phrases.append(chunk.text.lower())
        
        # Extract verb phrases
        for token in doc:
            if token.pos_ == "VERB":
                phrase_tokens = [token]
                
                # Add dependent tokens
                for child in token.children:
                    if child.dep_ in ["dobj", "pobj", "attr"]:
                        phrase_tokens.append(child)
                
                if len(phrase_tokens) > 1:
                    phrase = ' '.join([t.text for t in sorted(phrase_tokens, key=lambda x: x.i)])
                    key_phrases.append(phrase.lower())
        
        # Return unique phrases
        return list(set(key_phrases))[:20]
    
    def _extract_episode_insights(self, segments: List[Dict[str, Any]],
                                title: str,
                                description: str) -> Dict[str, Any]:
        """Extract high-level insights from episode."""
        # Aggregate entities
        all_entities = defaultdict(Counter)
        for segment in segments:
            for ent_type, ent_list in segment['entities'].items():
                all_entities[ent_type].update(ent_list)
        
        # Get top entities
        top_entities = {}
        for ent_type, counter in all_entities.items():
            top_entities[ent_type] = [ent for ent, _ in counter.most_common(5)]
        
        # Aggregate topics
        all_topics = []
        for segment in segments:
            all_topics.extend(segment['topics'])
        
        topic_counts = Counter(all_topics)
        main_topics = [topic for topic, _ in topic_counts.most_common(10)]
        
        # Identify key moments
        key_moments = sorted(
            segments,
            key=lambda x: x['importance_score'],
            reverse=True
        )[:5]
        
        # Speaker analysis
        all_speakers = set()
        for segment in segments:
            all_speakers.update(segment['speakers'])
        
        return {
            'main_topics': main_topics,
            'key_entities': top_entities,
            'speakers': list(all_speakers),
            'key_moments': [
                {
                    'timestamp': self._format_timestamp(moment['start_time']),
                    'duration': moment['duration'],
                    'preview': moment['text'][:200] + "..."
                }
                for moment in key_moments
            ],
            'total_segments': len(segments),
            'avg_segment_importance': sum(s['importance_score'] for s in segments) / len(segments)
        }
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def _create_episode_record(self, **kwargs) -> FrameRecord:
        """Create episode record."""
        metadata = create_metadata(
            title=kwargs['title'],
            source="podcast_episode",
            episode_hash=kwargs['episode_hash'],
            audio_url=kwargs['audio_url'],
            podcast_id=kwargs['podcast_id'],
            podcast_title=kwargs['podcast_info']['title'],
            description=kwargs['description'],
            published_date=datetime(*kwargs['published'][:6]).isoformat() if kwargs['published'] else None,
            duration_seconds=kwargs['duration'],
            
            # Insights
            main_topics=kwargs['insights']['main_topics'],
            speakers=kwargs['insights']['speakers'],
            key_entities=kwargs['insights']['key_entities'],
            key_moments=kwargs['insights']['key_moments'],
            segment_count=kwargs['insights']['total_segments'],
            avg_importance=kwargs['insights']['avg_segment_importance'],
            
            # Podcast info
            podcast_author=kwargs['podcast_info']['author'],
            podcast_categories=kwargs['podcast_info']['categories'],
            
            indexed_date=datetime.now().isoformat()
        )
        
        # Create searchable content
        content = f"{kwargs['title']}\n\n{kwargs['description']}\n\n"
        content += f"Topics: {', '.join(kwargs['insights']['main_topics'][:5])}\n"
        content += f"Speakers: {', '.join(kwargs['insights']['speakers'])}"
        
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Add relationship to podcast
        record.metadata = add_relationship_to_metadata(
            record.metadata,
            create_relationship(
                source_id=record.unique_id,
                target_id=kwargs['podcast_id'],
                relationship_type="child"
            )
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        # Update podcast episode count
        podcast = self.dataset.get(kwargs['podcast_id'])
        if podcast:
            podcast.metadata.custom_metadata['episode_count'] += 1
            podcast.metadata.custom_metadata['total_duration_hours'] += kwargs['duration'] / 3600
            self.dataset.update(podcast)
        
        return record
    
    def _create_segment_records(self, segments: List[Dict[str, Any]],
                              episode_id: str,
                              audio_url: str):
        """Create records for transcript segments."""
        for i, segment in enumerate(segments):
            metadata = create_metadata(
                title=f"Segment {i+1} ({self._format_timestamp(segment['start_time'])})",
                source="podcast_segment",
                episode_id=episode_id,
                segment_index=i,
                start_time=segment['start_time'],
                end_time=segment['end_time'],
                duration=segment['duration'],
                word_count=segment['word_count'],
                entities=segment['entities'],
                speakers=segment['speakers'],
                topics=segment['topics'],
                importance_score=segment['importance_score'],
                key_phrases=segment['key_phrases'],
                audio_url=audio_url,
                deep_link=f"{audio_url}#t={int(segment['start_time'])}"
            )
            
            record = FrameRecord(
                text_content=segment['text'],
                metadata=metadata,
                unique_id=generate_uuid(),
                record_type="document"
            )
            
            # Add relationship to episode
            record.metadata = add_relationship_to_metadata(
                record.metadata,
                create_relationship(
                    source_id=record.unique_id,
                    target_id=episode_id,
                    relationship_type="child"
                )
            )
            
            self.dataset.add(record, generate_embedding=True)
    
    def search_episodes(self, query: str,
                       podcast_id: Optional[str] = None,
                       speaker: Optional[str] = None,
                       date_range: Optional[Tuple[datetime, datetime]] = None,
                       min_importance: float = 0.0) -> List[Dict[str, Any]]:
        """Search across podcast episodes and segments."""
        # Build filter
        filter_dict = {
            'metadata.source': {'in': ['podcast_episode', 'podcast_segment']}
        }
        
        if podcast_id:
            filter_dict['metadata.podcast_id'] = podcast_id
        
        if speaker:
            filter_dict['metadata.speakers'] = {'contains': speaker}
        
        if date_range:
            filter_dict['metadata.published_date'] = {
                'gte': date_range[0].isoformat(),
                'lte': date_range[1].isoformat()
            }
        
        if min_importance > 0:
            filter_dict['metadata.importance_score'] = {'gte': min_importance}
        
        # Search
        results = self.dataset.search(
            query=query,
            filter=filter_dict,
            limit=50
        )
        
        # Format results
        formatted_results = []
        for result in results:
            meta = result.metadata.custom_metadata
            
            if meta.get('source') == 'podcast_episode':
                formatted_results.append({
                    'type': 'episode',
                    'title': result.metadata.title,
                    'podcast': meta.get('podcast_title'),
                    'date': meta.get('published_date'),
                    'topics': meta.get('main_topics', []),
                    'url': meta.get('audio_url'),
                    'score': getattr(result, 'score', 0)
                })
            else:  # segment
                formatted_results.append({
                    'type': 'segment',
                    'episode_id': meta.get('episode_id'),
                    'timestamp': self._format_timestamp(meta.get('start_time', 0)),
                    'duration': meta.get('duration', 0),
                    'text_preview': result.text_content[:200] + "...",
                    'importance': meta.get('importance_score', 0),
                    'deep_link': meta.get('deep_link'),
                    'score': getattr(result, 'score', 0)
                })
        
        return formatted_results
    
    def find_similar_episodes(self, episode_id: str,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Find episodes similar to given episode."""
        # Get source episode
        source_episode = self.dataset.get(episode_id)
        if not source_episode:
            return []
        
        source_meta = source_episode.metadata.custom_metadata
        source_topics = source_meta.get('main_topics', [])
        
        # Search based on topics and content
        results = self.dataset.search(
            query=' '.join(source_topics[:5]),
            filter={
                'metadata.source': 'podcast_episode',
                'unique_id': {'ne': episode_id}
            },
            limit=limit * 2
        )
        
        # Calculate similarity
        similar_episodes = []
        
        for result in results:
            meta = result.metadata.custom_metadata
            
            # Topic overlap
            result_topics = set(meta.get('main_topics', []))
            source_topics_set = set(source_topics)
            
            topic_overlap = len(result_topics & source_topics_set) / len(result_topics | source_topics_set) if result_topics else 0
            
            # Entity overlap
            source_entities = source_meta.get('key_entities', {})
            result_entities = meta.get('key_entities', {})
            
            entity_overlap = self._calculate_entity_overlap(source_entities, result_entities)
            
            # Combined similarity
            similarity_score = (
                getattr(result, 'score', 0) * 0.5 +
                topic_overlap * 0.3 +
                entity_overlap * 0.2
            )
            
            similar_episodes.append({
                'episode': result,
                'similarity_score': similarity_score,
                'title': result.metadata.title,
                'podcast': meta.get('podcast_title'),
                'common_topics': list(result_topics & source_topics_set),
                'date': meta.get('published_date')
            })
        
        # Sort by similarity
        return sorted(
            similar_episodes,
            key=lambda x: x['similarity_score'],
            reverse=True
        )[:limit]
    
    def _calculate_entity_overlap(self, entities1: Dict[str, List[str]],
                                entities2: Dict[str, List[str]]) -> float:
        """Calculate overlap between entity sets."""
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
    
    def generate_episode_summary(self, episode_id: str) -> Dict[str, Any]:
        """Generate comprehensive episode summary."""
        # Get episode
        episode = self.dataset.get(episode_id)
        if not episode:
            return {}
        
        meta = episode.metadata.custom_metadata
        
        # Get all segments
        segments = self.dataset.filter({
            'metadata.source': 'podcast_segment',
            'metadata.episode_id': episode_id
        })
        
        # Sort by timestamp
        segments.sort(key=lambda x: x.metadata.custom_metadata.get('start_time', 0))
        
        # Build timeline
        timeline = []
        for segment in segments:
            seg_meta = segment.metadata.custom_metadata
            if seg_meta.get('importance_score', 0) >= 0.5:
                timeline.append({
                    'timestamp': self._format_timestamp(seg_meta['start_time']),
                    'topics': seg_meta.get('topics', [])[:2],
                    'preview': segment.text_content[:100] + "..."
                })
        
        # Generate summary
        summary = {
            'episode_id': episode_id,
            'title': episode.metadata.title,
            'podcast': meta.get('podcast_title'),
            'date': meta.get('published_date'),
            'duration': f"{meta.get('duration_seconds', 0) // 60} minutes",
            'speakers': meta.get('speakers', []),
            'main_topics': meta.get('main_topics', []),
            'key_people': meta.get('key_entities', {}).get('PERSON', []),
            'key_organizations': meta.get('key_entities', {}).get('ORG', []),
            'key_moments': meta.get('key_moments', []),
            'timeline': timeline[:10],  # Top 10 moments
            'audio_url': meta.get('audio_url')
        }
        
        return summary
    
    def discover_trending_topics(self, days: int = 7) -> List[Dict[str, Any]]:
        """Discover trending topics across recent episodes."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get recent episodes
        recent_episodes = self.dataset.filter({
            'metadata.source': 'podcast_episode',
            'metadata.indexed_date': {'gte': cutoff_date.isoformat()}
        })
        
        # Aggregate topics
        topic_counts = Counter()
        topic_episodes = defaultdict(list)
        
        for episode in recent_episodes:
            meta = episode.metadata.custom_metadata
            topics = meta.get('main_topics', [])
            
            for topic in topics:
                topic_counts[topic] += 1
                topic_episodes[topic].append({
                    'title': episode.metadata.title,
                    'podcast': meta.get('podcast_title'),
                    'date': meta.get('published_date')
                })
        
        # Build trending list
        trending = []
        for topic, count in topic_counts.most_common(20):
            trending.append({
                'topic': topic,
                'episode_count': count,
                'recent_episodes': topic_episodes[topic][:3],
                'trend_score': count / len(recent_episodes) if recent_episodes else 0
            })
        
        return trending

# Example usage
if __name__ == "__main__":
    # Initialize system
    podcast_system = PodcastIndexSystem()
    
    # Index a podcast
    feed_url = "https://example.com/podcast/feed.xml"
    episodes = podcast_system.index_podcast(
        feed_url=feed_url,
        podcast_name="Tech Talks Daily",
        max_episodes=5
    )
    
    print(f"Indexed {len(episodes)} items (1 podcast + episodes)")
    
    # Search for content
    results = podcast_system.search_episodes(
        query="artificial intelligence machine learning",
        min_importance=0.5
    )
    
    print(f"\nFound {len(results)} results")
    for result in results[:5]:
        if result['type'] == 'episode':
            print(f"\nEpisode: {result['title']}")
            print(f"Podcast: {result['podcast']}")
            print(f"Topics: {', '.join(result['topics'][:3])}")
        else:  # segment
            print(f"\nSegment at {result['timestamp']}")
            print(f"Importance: {result['importance']:.2f}")
            print(f"Preview: {result['text_preview']}")
    
    # Find similar episodes
    if episodes and len(episodes) > 1:
        similar = podcast_system.find_similar_episodes(
            episodes[1].unique_id,  # First episode after podcast record
            limit=5
        )
        
        print(f"\nSimilar episodes:")
        for ep in similar:
            print(f"- {ep['title']} (similarity: {ep['similarity_score']:.2f})")
            print(f"  Common topics: {', '.join(ep['common_topics'])}")
    
    # Discover trending topics
    trending = podcast_system.discover_trending_topics(days=30)
    
    print(f"\nTrending topics:")
    for topic in trending[:5]:
        print(f"- {topic['topic']}: {topic['episode_count']} episodes")
```

## Key Concepts

### Audio Processing Pipeline

The system handles complete audio processing:
- **Audio Download**: Stream processing for large files
- **Transcription**: Whisper model for accurate speech-to-text
- **Speaker Diarization**: Identify different speakers
- **Segmentation**: Break into digestible chunks

### Content Analysis

Deep analysis of podcast content:
- **Topic Extraction**: Identify main themes and discussions
- **Entity Recognition**: People, organizations, locations
- **Importance Scoring**: Highlight key moments
- **Key Phrase Extraction**: Memorable quotes and insights

### Discovery Features

Help listeners find relevant content:
- **Semantic Search**: Search within episode content
- **Timestamp Navigation**: Jump to specific moments
- **Similar Episodes**: Find related discussions
- **Trending Topics**: Discover popular themes

## Extensions

### Advanced Features

1. **Speaker Identification**
   - Voice fingerprinting
   - Automatic speaker labeling
   - Guest detection
   - Speaker statistics

2. **Content Enhancement**
   - Chapter generation
   - Show notes creation
   - Quote extraction
   - Fact checking

3. **Personalization**
   - Listening history
   - Preference learning
   - Custom playlists
   - Speed recommendations

4. **Analytics**
   - Podcast metrics
   - Topic trends
   - Guest analysis
   - Engagement tracking

### Integration Options

1. **Podcast Platforms**
   - Apple Podcasts API
   - Spotify API
   - Podcast Index API
   - RSS aggregators

2. **Audio Processing**
   - Advanced diarization
   - Music detection
   - Ad detection
   - Silence removal

3. **Distribution**
   - Newsletter generation
   - Social media clips
   - Transcript export
   - API access

## Best Practices

1. **Audio Quality**
   - Handle various formats
   - Noise reduction
   - Volume normalization
   - Error handling

2. **Transcription Accuracy**
   - Domain-specific models
   - Manual corrections
   - Confidence scoring
   - Multiple passes

3. **Storage Efficiency**
   - Compress transcripts
   - Cache audio temporarily
   - Incremental indexing
   - Cleanup policies

4. **User Experience**
   - Fast search results
   - Accurate timestamps
   - Mobile-friendly
   - Offline support

This podcast indexing system transforms audio content into a searchable knowledge base, making podcast discovery and research significantly more efficient.