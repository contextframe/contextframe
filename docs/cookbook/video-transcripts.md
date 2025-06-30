# Video Transcript Database

Build a comprehensive video content management system that transcribes, indexes, and makes searchable video content from multiple sources including YouTube, internal training videos, and webinars.

## Problem Statement

Organizations have valuable knowledge locked in video content that's difficult to search and reference. Finding specific information requires watching entire videos. A searchable transcript database makes video content as accessible as text documents.

## Solution Overview

We'll build a video transcript system that:
1. Processes videos from multiple sources
2. Generates accurate transcriptions with timestamps
3. Extracts key topics and speakers
4. Enables timestamp-based search
5. Links to original video segments

## Complete Code

```python
import os
import re
import json
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import whisper
import yt_dlp
import cv2
import numpy as np
from collections import defaultdict
import requests

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class VideoTranscriptDatabase:
    """Comprehensive video transcript management system."""
    
    def __init__(self, dataset_path: str = "video_transcripts.lance"):
        """Initialize video transcript database."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Load Whisper model for transcription
        self.whisper_model = whisper.load_model("base")
        
        # Video processing settings
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.chunk_duration = 300  # 5 minutes chunks for processing
        
        # Speaker diarization patterns
        self.speaker_patterns = [
            r'(?:^|\n)([A-Z][a-z]+ [A-Z][a-z]+):\s*',  # "John Smith: "
            r'(?:^|\n)\[([^\]]+)\]\s*',  # "[Speaker Name]"
            r'(?:^|\n)Speaker (\d+):\s*'  # "Speaker 1: "
        ]
        
    def process_youtube_video(self, url: str, 
                            video_title: Optional[str] = None,
                            tags: List[str] = None) -> FrameRecord:
        """Process a YouTube video."""
        print(f"Processing YouTube video: {url}")
        
        # Download video info and audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            video_id = info['id']
            title = video_title or info.get('title', 'Untitled Video')
            description = info.get('description', '')
            duration = info.get('duration', 0)
            channel = info.get('channel', 'Unknown')
            upload_date = info.get('upload_date', '')
            
            # Audio file path
            audio_path = f"downloads/{video_id}.mp3"
        
        # Create video header record
        video_record = self._create_video_record(
            title=title,
            url=url,
            video_id=video_id,
            duration=duration,
            channel=channel,
            description=description,
            upload_date=upload_date,
            tags=tags
        )
        
        # Transcribe audio
        segments = self._transcribe_audio(audio_path, video_id)
        
        # Process transcript segments
        self._process_transcript_segments(segments, video_record.unique_id, url)
        
        # Extract key moments
        key_moments = self._extract_key_moments(segments)
        video_record.metadata.custom_metadata['key_moments'] = key_moments
        
        # Update video record
        self.dataset.update(video_record)
        
        # Cleanup
        os.remove(audio_path)
        
        return video_record
    
    def process_local_video(self, video_path: str,
                          title: str,
                          tags: List[str] = None,
                          speakers: List[str] = None) -> FrameRecord:
        """Process a local video file."""
        print(f"Processing local video: {video_path}")
        
        # Extract video info
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        
        # Extract audio for transcription
        audio_path = video_path.rsplit('.', 1)[0] + '_audio.wav'
        self._extract_audio_from_video(video_path, audio_path)
        
        # Create video record
        video_record = self._create_video_record(
            title=title,
            url=f"file://{os.path.abspath(video_path)}",
            video_id=Path(video_path).stem,
            duration=duration,
            tags=tags,
            speakers=speakers
        )
        
        # Transcribe
        segments = self._transcribe_audio(audio_path, video_record.unique_id)
        
        # Process segments
        self._process_transcript_segments(
            segments, 
            video_record.unique_id,
            f"file://{os.path.abspath(video_path)}"
        )
        
        # Extract visual keyframes
        keyframes = self._extract_keyframes(video_path)
        video_record.metadata.custom_metadata['keyframes'] = keyframes
        
        # Update record
        self.dataset.update(video_record)
        
        # Cleanup
        os.remove(audio_path)
        
        return video_record
    
    def _create_video_record(self, **kwargs) -> FrameRecord:
        """Create video header record."""
        metadata = create_metadata(
            title=kwargs.get('title', 'Untitled Video'),
            source="video",
            url=kwargs.get('url'),
            video_id=kwargs.get('video_id'),
            duration_seconds=kwargs.get('duration', 0),
            channel=kwargs.get('channel'),
            speakers=kwargs.get('speakers', []),
            upload_date=kwargs.get('upload_date'),
            tags=kwargs.get('tags', []),
            processed_date=datetime.now().isoformat()
        )
        
        content = f"{kwargs.get('title', '')}\\n\\n{kwargs.get('description', '')}"
        
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="collection_header"
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        return record
    
    def _extract_audio_from_video(self, video_path: str, audio_path: str):
        """Extract audio track from video."""
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1',
            audio_path, '-y'
        ]
        subprocess.run(cmd, capture_output=True, check=True)
    
    def _transcribe_audio(self, audio_path: str, 
                         video_id: str) -> List[Dict[str, Any]]:
        """Transcribe audio using Whisper."""
        print("Transcribing audio...")
        
        # Transcribe with timestamps
        result = self.whisper_model.transcribe(
            audio_path,
            verbose=False,
            language="en",  # Auto-detect or specify
            task="transcribe"
        )
        
        # Extract segments with timestamps
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'confidence': segment.get('avg_logprob', 0)
            })
        
        return segments
    
    def _process_transcript_segments(self, segments: List[Dict[str, Any]], 
                                   video_id: str, video_url: str):
        """Process and store transcript segments."""
        # Group segments into chunks for better context
        chunks = self._group_segments_into_chunks(segments)
        
        for i, chunk in enumerate(chunks):
            # Combine text from segments
            text_parts = []
            start_time = chunk[0]['start']
            end_time = chunk[-1]['end']
            
            for segment in chunk:
                timestamp = self._format_timestamp(segment['start'])
                text_parts.append(f"[{timestamp}] {segment['text']}")
            
            full_text = "\\n".join(text_parts)
            
            # Detect speakers if present
            speakers = self._detect_speakers(full_text)
            
            # Extract topics
            topics = self._extract_topics(full_text)
            
            # Create segment record
            metadata = create_metadata(
                title=f"Segment {i+1} ({self._format_timestamp(start_time)} - {self._format_timestamp(end_time)})",
                source="video_transcript",
                video_id=video_id,
                segment_index=i,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                speakers=speakers,
                topics=topics,
                video_url=video_url,
                deep_link=self._create_deep_link(video_url, start_time)
            )
            
            record = FrameRecord(
                text_content=full_text,
                metadata=metadata,
                unique_id=generate_uuid(),
                record_type="document"
            )
            
            # Add relationship to video
            record.metadata = add_relationship_to_metadata(
                record.metadata,
                create_relationship(
                    source_id=record.unique_id,
                    target_id=video_id,
                    relationship_type="child"
                )
            )
            
            self.dataset.add(record, generate_embedding=True)
    
    def _group_segments_into_chunks(self, segments: List[Dict[str, Any]], 
                                  max_duration: float = 300) -> List[List[Dict[str, Any]]]:
        """Group segments into chunks of reasonable duration."""
        chunks = []
        current_chunk = []
        chunk_start = 0
        
        for segment in segments:
            if current_chunk and (segment['end'] - chunk_start) > max_duration:
                # Start new chunk
                chunks.append(current_chunk)
                current_chunk = [segment]
                chunk_start = segment['start']
            else:
                current_chunk.append(segment)
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def _create_deep_link(self, video_url: str, timestamp: float) -> str:
        """Create deep link to specific timestamp."""
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            # YouTube timestamp format
            return f"{video_url}&t={int(timestamp)}s"
        elif video_url.startswith('file://'):
            # Local file with timestamp
            return f"{video_url}#t={int(timestamp)}"
        else:
            return video_url
    
    def _detect_speakers(self, text: str) -> List[str]:
        """Detect speaker names in transcript."""
        speakers = set()
        
        for pattern in self.speaker_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            speakers.update(matches)
        
        return list(speakers)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text segment."""
        # Simple keyword extraction - in production use NLP
        topics = []
        
        # Common topic indicators
        topic_patterns = [
            r'(?:talking about|discussing|topic is|subject of)\s+(\w+(?:\s+\w+){0,2})',
            r'(?:question about|regarding|concerning)\s+(\w+(?:\s+\w+){0,2})',
            r'(?:let\'s talk about|today\'s topic|focus on)\s+(\w+(?:\s+\w+){0,2})'
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            topics.extend(matches)
        
        # Remove duplicates and clean
        topics = list(set(t.strip().lower() for t in topics))
        
        return topics[:5]  # Limit to top 5 topics
    
    def _extract_key_moments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract key moments from transcript."""
        key_moments = []
        
        # Patterns indicating important moments
        importance_patterns = [
            r'(?:important|key|crucial|critical|essential)',
            r'(?:remember|note|pay attention|focus on)',
            r'(?:in conclusion|to summarize|key takeaway)',
            r'(?:the main point|most importantly)'
        ]
        
        for segment in segments:
            text_lower = segment['text'].lower()
            
            # Check for importance indicators
            for pattern in importance_patterns:
                if re.search(pattern, text_lower):
                    key_moments.append({
                        'timestamp': segment['start'],
                        'text': segment['text'],
                        'reason': 'importance_indicator'
                    })
                    break
        
        return key_moments
    
    def _extract_keyframes(self, video_path: str, 
                          num_frames: int = 10) -> List[Dict[str, Any]]:
        """Extract keyframes from video."""
        keyframes = []
        
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames > 0:
            # Extract frames at regular intervals
            interval = total_frames // num_frames
            
            for i in range(num_frames):
                frame_pos = i * interval
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                
                ret, frame = cap.read()
                if ret:
                    # Calculate timestamp
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    timestamp = frame_pos / fps if fps > 0 else 0
                    
                    # In production, save frame and store path
                    keyframes.append({
                        'frame_number': frame_pos,
                        'timestamp': timestamp
                    })
        
        cap.release()
        
        return keyframes
    
    def search_transcripts(self, query: str,
                         speaker: Optional[str] = None,
                         channel: Optional[str] = None,
                         min_duration: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search video transcripts."""
        # Build filter
        filter_dict = {'metadata.source': {'in': ['video_transcript', 'video']}}
        
        if speaker:
            filter_dict['metadata.speakers'] = {'contains': speaker}
        
        if channel:
            filter_dict['metadata.channel'] = channel
        
        if min_duration:
            filter_dict['metadata.duration_seconds'] = {'gte': min_duration}
        
        # Search
        results = self.dataset.search(query=query, filter=filter_dict, limit=50)
        
        # Format results
        formatted_results = []
        for result in results:
            metadata = result.metadata.custom_metadata
            
            formatted_results.append({
                'title': result.metadata.title,
                'video_id': metadata.get('video_id'),
                'timestamp': metadata.get('start_time', 0),
                'duration': metadata.get('duration', 0),
                'speakers': metadata.get('speakers', []),
                'excerpt': result.text_content[:200] + "...",
                'deep_link': metadata.get('deep_link'),
                'score': getattr(result, 'score', 1.0)
            })
        
        return formatted_results
    
    def get_video_summary(self, video_id: str) -> Dict[str, Any]:
        """Generate summary for a video."""
        # Get video record
        video_records = self.dataset.filter({
            'metadata.video_id': video_id,
            'metadata.source': 'video'
        })
        
        if not video_records:
            return {}
        
        video_record = video_records[0]
        
        # Get all transcript segments
        segments = self.dataset.filter({
            'metadata.video_id': video_id,
            'metadata.source': 'video_transcript'
        })
        
        # Sort by segment index
        segments.sort(key=lambda x: x.metadata.custom_metadata.get('segment_index', 0))
        
        # Extract summary info
        all_speakers = set()
        all_topics = set()
        total_words = 0
        
        for segment in segments:
            metadata = segment.metadata.custom_metadata
            all_speakers.update(metadata.get('speakers', []))
            all_topics.update(metadata.get('topics', []))
            total_words += len(segment.text_content.split())
        
        summary = {
            'video_id': video_id,
            'title': video_record.metadata.title,
            'duration': video_record.metadata.custom_metadata.get('duration_seconds', 0),
            'channel': video_record.metadata.custom_metadata.get('channel'),
            'speakers': list(all_speakers),
            'topics': list(all_topics),
            'total_words': total_words,
            'segment_count': len(segments),
            'key_moments': video_record.metadata.custom_metadata.get('key_moments', []),
            'url': video_record.metadata.custom_metadata.get('url')
        }
        
        return summary
    
    def create_video_clips(self, video_id: str, 
                         search_query: str,
                         context_seconds: int = 30) -> List[Dict[str, Any]]:
        """Create video clips based on search results."""
        # Search within video
        results = self.dataset.search(
            query=search_query,
            filter={
                'metadata.video_id': video_id,
                'metadata.source': 'video_transcript'
            },
            limit=10
        )
        
        clips = []
        for result in results:
            metadata = result.metadata.custom_metadata
            
            # Calculate clip boundaries with context
            start_time = max(0, metadata.get('start_time', 0) - context_seconds)
            end_time = metadata.get('end_time', 0) + context_seconds
            
            clips.append({
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'highlight_start': metadata.get('start_time', 0),
                'highlight_end': metadata.get('end_time', 0),
                'text': result.text_content,
                'deep_link': metadata.get('deep_link')
            })
        
        return clips
    
    def generate_subtitles(self, video_id: str, 
                          output_format: str = 'srt') -> str:
        """Generate subtitle file from transcripts."""
        # Get all segments for video
        segments = self.dataset.filter({
            'metadata.video_id': video_id,
            'metadata.source': 'video_transcript'
        })
        
        # Sort by start time
        segments.sort(key=lambda x: x.metadata.custom_metadata.get('start_time', 0))
        
        if output_format == 'srt':
            return self._generate_srt(segments)
        elif output_format == 'vtt':
            return self._generate_vtt(segments)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _generate_srt(self, segments: List[FrameRecord]) -> str:
        """Generate SRT format subtitles."""
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            metadata = segment.metadata.custom_metadata
            start = self._seconds_to_srt_time(metadata.get('start_time', 0))
            end = self._seconds_to_srt_time(metadata.get('end_time', 0))
            
            # Extract clean text without timestamps
            text = re.sub(r'\[\d{2}:\d{2}(?::\d{2})?\]\s*', '', segment.text_content)
            
            srt_lines.extend([
                str(i),
                f"{start} --> {end}",
                text.strip(),
                ""
            ])
        
        return "\\n".join(srt_lines)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

# Example usage
if __name__ == "__main__":
    # Initialize database
    video_db = VideoTranscriptDatabase()
    
    # Process YouTube video
    video_record = video_db.process_youtube_video(
        url="https://youtube.com/watch?v=example",
        tags=["tutorial", "programming", "python"]
    )
    
    # Process local video
    local_video = video_db.process_local_video(
        video_path="/path/to/training_video.mp4",
        title="Internal Training: API Development",
        tags=["training", "api", "development"],
        speakers=["John Smith", "Jane Doe"]
    )
    
    # Search across all videos
    results = video_db.search_transcripts(
        query="authentication best practices",
        min_duration=600  # At least 10 minutes
    )
    
    print(f"Found {len(results)} relevant segments:")
    for result in results[:5]:
        print(f"\\n- {result['title']}")
        print(f"  Timestamp: {result['timestamp']:.0f}s")
        print(f"  Speakers: {', '.join(result['speakers'])}")
        print(f"  Link: {result['deep_link']}")
    
    # Get video summary
    summary = video_db.get_video_summary(video_record.unique_id)
    print(f"\\nVideo Summary:")
    print(f"Title: {summary['title']}")
    print(f"Duration: {summary['duration']/60:.1f} minutes")
    print(f"Topics: {', '.join(summary['topics'])}")
    print(f"Key moments: {len(summary['key_moments'])}")
    
    # Generate subtitles
    subtitles = video_db.generate_subtitles(
        video_record.unique_id,
        output_format='srt'
    )
    
    with open(f"{video_record.unique_id}.srt", 'w') as f:
        f.write(subtitles)
```

## Key Concepts

### Transcript Segmentation

The system intelligently segments transcripts:
- **Time-based chunks**: Groups content into digestible segments
- **Speaker detection**: Identifies different speakers
- **Topic boundaries**: Detects topic changes
- **Key moment extraction**: Highlights important segments

### Deep Linking

Every transcript segment includes deep links:
- **YouTube videos**: Links with timestamp parameters
- **Local files**: File URLs with time markers
- **Web players**: Compatible with various video platforms
- **Clip generation**: Create shareable video segments

### Multi-Format Support

Handles various video sources:
- **YouTube/Online**: Downloads and processes via URLs
- **Local files**: Processes MP4, AVI, MOV, etc.
- **Live streams**: Can process recorded streams
- **Webinar platforms**: Zoom, Teams recordings

## Extensions

### Advanced Features

1. **Speaker Diarization**
   - Automatic speaker identification
   - Voice fingerprinting
   - Speaker change detection
   - Multi-speaker overlap handling

2. **Visual Analysis**
   - Scene detection
   - OCR for on-screen text
   - Slide extraction
   - Object recognition

3. **Content Enhancement**
   - Auto-generated chapters
   - Topic summaries
   - Action item extraction
   - Q&A detection

4. **Translation**
   - Multi-language transcription
   - Subtitle translation
   - Cross-language search
   - Dubbing alignment

### Integration Options

1. **Video Platforms**
   - YouTube Data API
   - Vimeo API
   - Zoom recordings
   - Microsoft Stream

2. **Learning Management**
   - LMS integration
   - Course video indexing
   - Student engagement tracking
   - Quiz generation

3. **Collaboration Tools**
   - Slack notifications
   - Team highlights
   - Meeting summaries
   - Action item tracking

## Best Practices

1. **Accuracy Optimization**
   - Use appropriate Whisper models
   - Domain-specific vocabulary
   - Speaker training data
   - Manual correction workflow

2. **Performance**
   - Process videos asynchronously
   - Cache transcription results
   - Optimize chunk sizes
   - Use GPU acceleration

3. **Storage Efficiency**
   - Store only transcripts, not videos
   - Compress keyframe images
   - Archive old transcripts
   - Deduplicate content

4. **Privacy Compliance**
   - Respect video permissions
   - Implement access controls
   - Anonymize sensitive content
   - Audit trail for access

This video transcript database transforms video content into a searchable knowledge repository, making video as accessible as text documentation.