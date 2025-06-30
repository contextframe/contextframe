# Course Material Management

Build a comprehensive learning management system that organizes course content, tracks student progress, enables collaborative learning, and provides intelligent content recommendations.

## Problem Statement

Educational institutions and online learning platforms need to manage diverse learning materials including lectures, assignments, readings, and multimedia content while tracking student engagement, providing personalized learning paths, and ensuring content accessibility.

## Solution Overview

We'll build a course material system that:
1. Organizes multi-format educational content hierarchically
2. Tracks student progress and engagement
3. Enables collaborative annotations and discussions
4. Provides adaptive learning recommendations
5. Generates analytics for instructors

## Complete Code

```python
import os
import re
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import hashlib

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class ContentType(Enum):
    """Types of course content."""
    LECTURE = "lecture"
    READING = "reading"
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    VIDEO = "video"
    LAB = "lab"
    DISCUSSION = "discussion"
    PROJECT = "project"
    RESOURCE = "resource"

class DifficultyLevel(Enum):
    """Content difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class LearningObjective:
    """Represents a learning objective."""
    id: str
    description: str
    bloom_level: str  # remember, understand, apply, analyze, evaluate, create
    measurable: bool
    assessment_methods: List[str]

class CourseManagementSystem:
    """Comprehensive course material management system."""
    
    def __init__(self, dataset_path: str = "course_materials.lance"):
        """Initialize course management system."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Learning analytics tracking
        self.student_progress = defaultdict(dict)
        self.engagement_metrics = defaultdict(list)
        
        # Bloom's taxonomy levels
        self.bloom_levels = [
            "remember", "understand", "apply", 
            "analyze", "evaluate", "create"
        ]
        
        # Content quality indicators
        self.quality_metrics = {
            'completeness': 0.0,
            'clarity': 0.0,
            'engagement': 0.0,
            'effectiveness': 0.0
        }
        
    def create_course(self, 
                     course_code: str,
                     title: str,
                     description: str,
                     instructor: Dict[str, str],
                     credits: int,
                     prerequisites: List[str] = None,
                     learning_objectives: List[LearningObjective] = None,
                     schedule: Dict[str, Any] = None) -> FrameRecord:
        """Create a new course."""
        print(f"Creating course: {course_code} - {title}")
        
        # Create course metadata
        metadata = create_metadata(
            title=f"{course_code}: {title}",
            source="course",
            course_code=course_code,
            course_title=title,
            description=description,
            instructor=instructor,
            credits=credits,
            prerequisites=prerequisites or [],
            learning_objectives=[
                {
                    'id': obj.id,
                    'description': obj.description,
                    'bloom_level': obj.bloom_level,
                    'measurable': obj.measurable,
                    'assessment_methods': obj.assessment_methods
                } for obj in (learning_objectives or [])
            ],
            schedule=schedule or {},
            created_date=datetime.now().isoformat(),
            enrollment_count=0,
            modules=[],
            total_content_items=0,
            estimated_hours=0
        )
        
        # Create comprehensive course description
        content = self._generate_course_description(
            course_code, title, description, instructor, 
            prerequisites, learning_objectives
        )
        
        # Create course record
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="collection_header"
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        return record
    
    def add_module(self, course_id: str,
                  module_number: int,
                  title: str,
                  description: str,
                  learning_objectives: List[str],
                  estimated_hours: float) -> FrameRecord:
        """Add module to course."""
        print(f"Adding module: {title}")
        
        # Get course
        course = self.dataset.get(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")
        
        # Create module metadata
        metadata = create_metadata(
            title=f"Module {module_number}: {title}",
            source="course_module",
            course_id=course_id,
            module_number=module_number,
            description=description,
            learning_objectives=learning_objectives,
            estimated_hours=estimated_hours,
            content_items=[],
            completion_requirements=[],
            created_date=datetime.now().isoformat()
        )
        
        # Create module content
        content = f"# Module {module_number}: {title}\n\n"
        content += f"{description}\n\n"
        content += "## Learning Objectives\n"
        for obj in learning_objectives:
            content += f"- {obj}\n"
        content += f"\n**Estimated Time:** {estimated_hours} hours"
        
        # Create module record
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="collection_header"
        )
        
        # Add relationship to course
        record.metadata = add_relationship_to_metadata(
            record.metadata,
            create_relationship(
                source_id=record.unique_id,
                target_id=course_id,
                relationship_type="child"
            )
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        # Update course modules list
        course.metadata.custom_metadata['modules'].append({
            'id': record.unique_id,
            'number': module_number,
            'title': title
        })
        course.metadata.custom_metadata['estimated_hours'] += estimated_hours
        self.dataset.update(course)
        
        return record
    
    def add_content(self, module_id: str,
                   content_type: ContentType,
                   title: str,
                   content_path: str,
                   description: str = "",
                   difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
                   estimated_time: int = 30,
                   prerequisites: List[str] = None,
                   learning_objectives: List[str] = None,
                   metadata_extra: Dict[str, Any] = None) -> FrameRecord:
        """Add content item to module."""
        print(f"Adding {content_type.value}: {title}")
        
        # Extract content based on type
        if content_type == ContentType.VIDEO:
            content_text = self._process_video_content(content_path, title, description)
        elif content_type == ContentType.ASSIGNMENT:
            content_text = self._process_assignment(content_path, metadata_extra)
        elif content_type in [ContentType.LECTURE, ContentType.READING]:
            content_text = self._extract_text_content(content_path)
        else:
            content_text = description
        
        # Calculate content hash for version tracking
        content_hash = hashlib.md5(content_text.encode()).hexdigest()
        
        # Create content metadata
        metadata = create_metadata(
            title=title,
            source="course_content",
            content_type=content_type.value,
            module_id=module_id,
            file_path=content_path,
            description=description,
            difficulty=difficulty.value,
            estimated_time_minutes=estimated_time,
            prerequisites=prerequisites or [],
            learning_objectives=learning_objectives or [],
            content_hash=content_hash,
            created_date=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            version=1,
            view_count=0,
            average_rating=0.0,
            completion_rate=0.0
        )
        
        # Add type-specific metadata
        if metadata_extra:
            metadata.custom_metadata.update(metadata_extra)
        
        # Create content record
        record = FrameRecord(
            text_content=content_text[:10000],  # Limit content size
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Add relationship to module
        record.metadata = add_relationship_to_metadata(
            record.metadata,
            create_relationship(
                source_id=record.unique_id,
                target_id=module_id,
                relationship_type="child"
            )
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        # Update module content list
        module = self.dataset.get(module_id)
        if module:
            module.metadata.custom_metadata['content_items'].append({
                'id': record.unique_id,
                'type': content_type.value,
                'title': title,
                'estimated_time': estimated_time
            })
            self.dataset.update(module)
        
        # Create prerequisite relationships
        if prerequisites:
            for prereq_id in prerequisites:
                record.metadata = add_relationship_to_metadata(
                    record.metadata,
                    create_relationship(
                        source_id=record.unique_id,
                        target_id=prereq_id,
                        relationship_type="reference",
                        properties={'reference_type': 'prerequisite'}
                    )
                )
        
        return record
    
    def _generate_course_description(self, course_code: str, title: str,
                                   description: str, instructor: Dict[str, str],
                                   prerequisites: List[str],
                                   objectives: List[LearningObjective]) -> str:
        """Generate comprehensive course description."""
        content = f"# {course_code}: {title}\n\n"
        content += f"**Instructor:** {instructor.get('name', 'TBA')}"
        if instructor.get('email'):
            content += f" ({instructor['email']})"
        content += f"\n\n## Course Description\n{description}\n"
        
        if prerequisites:
            content += "\n## Prerequisites\n"
            for prereq in prerequisites:
                content += f"- {prereq}\n"
        
        if objectives:
            content += "\n## Learning Objectives\n"
            content += "Upon completion of this course, students will be able to:\n"
            for obj in objectives:
                content += f"- {obj.description} (Bloom's: {obj.bloom_level})\n"
        
        return content
    
    def _extract_text_content(self, file_path: str) -> str:
        """Extract text content from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return f"Content file: {file_path}"
    
    def _process_video_content(self, video_path: str, 
                             title: str, description: str) -> str:
        """Process video content metadata."""
        content = f"# Video: {title}\n\n"
        content += f"{description}\n\n"
        content += f"**Video Location:** {video_path}\n"
        
        # In production, extract video metadata, generate transcript, etc.
        return content
    
    def _process_assignment(self, assignment_path: str,
                          metadata: Dict[str, Any]) -> str:
        """Process assignment content."""
        content = self._extract_text_content(assignment_path)
        
        # Add assignment-specific information
        if metadata:
            if metadata.get('due_date'):
                content = f"**Due Date:** {metadata['due_date']}\n\n" + content
            if metadata.get('points'):
                content = f"**Points:** {metadata['points']}\n" + content
            if metadata.get('submission_type'):
                content = f"**Submission Type:** {metadata['submission_type']}\n" + content
        
        return content
    
    def track_student_progress(self, student_id: str,
                             content_id: str,
                             action: str,
                             data: Dict[str, Any] = None):
        """Track student progress and engagement."""
        timestamp = datetime.now()
        
        # Record engagement event
        event = {
            'timestamp': timestamp.isoformat(),
            'content_id': content_id,
            'action': action,
            'data': data or {}
        }
        
        self.engagement_metrics[student_id].append(event)
        
        # Update progress tracking
        if action == 'completed':
            if content_id not in self.student_progress[student_id]:
                self.student_progress[student_id][content_id] = {}
            
            self.student_progress[student_id][content_id].update({
                'completed': True,
                'completion_date': timestamp.isoformat(),
                'time_spent': data.get('time_spent', 0),
                'score': data.get('score')
            })
            
            # Update content completion rate
            content = self.dataset.get(content_id)
            if content:
                completions = content.metadata.custom_metadata.get('completion_count', 0)
                content.metadata.custom_metadata['completion_count'] = completions + 1
                self.dataset.update(content)
    
    def get_learning_path(self, student_id: str,
                         course_id: str) -> List[Dict[str, Any]]:
        """Generate personalized learning path for student."""
        # Get course structure
        course = self.dataset.get(course_id)
        if not course:
            return []
        
        # Get all course content
        all_content = self._get_course_content(course_id)
        
        # Get student progress
        student_progress = self.student_progress.get(student_id, {})
        
        # Build learning path
        learning_path = []
        
        for content in all_content:
            content_id = content.unique_id
            meta = content.metadata.custom_metadata
            
            # Check completion status
            is_completed = student_progress.get(content_id, {}).get('completed', False)
            
            # Check prerequisites
            prerequisites_met = self._check_prerequisites_met(
                content_id, student_progress
            )
            
            # Calculate priority based on various factors
            priority = self._calculate_content_priority(
                content, student_progress, is_completed
            )
            
            learning_path.append({
                'content_id': content_id,
                'title': content.metadata.title,
                'type': meta.get('content_type'),
                'module': meta.get('module_id'),
                'estimated_time': meta.get('estimated_time_minutes'),
                'difficulty': meta.get('difficulty'),
                'is_completed': is_completed,
                'prerequisites_met': prerequisites_met,
                'priority': priority,
                'locked': not prerequisites_met
            })
        
        # Sort by priority and prerequisites
        learning_path.sort(key=lambda x: (
            not x['prerequisites_met'],  # Unlocked content first
            x['is_completed'],          # Uncompleted content next
            -x['priority']              # High priority first
        ))
        
        return learning_path
    
    def _get_course_content(self, course_id: str) -> List[FrameRecord]:
        """Get all content for a course."""
        # Get all modules
        modules = self.dataset.filter({
            'metadata.source': 'course_module',
            'metadata.course_id': course_id
        })
        
        all_content = []
        
        for module in modules:
            # Get module content
            content = self.dataset.filter({
                'metadata.source': 'course_content',
                'metadata.module_id': module.unique_id
            })
            all_content.extend(content)
        
        return all_content
    
    def _check_prerequisites_met(self, content_id: str,
                               student_progress: Dict[str, Any]) -> bool:
        """Check if prerequisites are met for content."""
        content = self.dataset.get(content_id)
        if not content:
            return True
        
        prerequisites = content.metadata.custom_metadata.get('prerequisites', [])
        
        for prereq_id in prerequisites:
            if not student_progress.get(prereq_id, {}).get('completed', False):
                return False
        
        return True
    
    def _calculate_content_priority(self, content: FrameRecord,
                                  student_progress: Dict[str, Any],
                                  is_completed: bool) -> float:
        """Calculate priority score for content."""
        if is_completed:
            return 0.0
        
        priority = 1.0
        meta = content.metadata.custom_metadata
        
        # Boost priority for content types based on learning style
        content_type = meta.get('content_type')
        if content_type == ContentType.ASSIGNMENT.value:
            priority *= 1.5  # Assignments are high priority
        elif content_type == ContentType.QUIZ.value:
            priority *= 1.3  # Quizzes are important for assessment
        
        # Adjust for difficulty progression
        difficulty = meta.get('difficulty')
        completed_difficulties = [
            self.dataset.get(cid).metadata.custom_metadata.get('difficulty')
            for cid, progress in student_progress.items()
            if progress.get('completed')
        ]
        
        if difficulty == DifficultyLevel.BEGINNER.value:
            priority *= 1.2
        elif difficulty == DifficultyLevel.ADVANCED.value and \
             DifficultyLevel.INTERMEDIATE.value not in completed_difficulties:
            priority *= 0.7  # Reduce priority if not ready
        
        return priority
    
    def search_content(self, query: str,
                      course_id: Optional[str] = None,
                      content_type: Optional[ContentType] = None,
                      difficulty: Optional[DifficultyLevel] = None) -> List[FrameRecord]:
        """Search course content."""
        # Build filter
        filter_dict = {'metadata.source': 'course_content'}
        
        if course_id:
            # Get course modules first
            modules = self.dataset.filter({
                'metadata.source': 'course_module',
                'metadata.course_id': course_id
            })
            module_ids = [m.unique_id for m in modules]
            filter_dict['metadata.module_id'] = {'in': module_ids}
        
        if content_type:
            filter_dict['metadata.content_type'] = content_type.value
        
        if difficulty:
            filter_dict['metadata.difficulty'] = difficulty.value
        
        # Search
        return self.dataset.search(query=query, filter=filter_dict, limit=50)
    
    def recommend_content(self, student_id: str,
                        course_id: str,
                        num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Recommend content based on student progress and preferences."""
        # Get student progress
        student_progress = self.student_progress.get(student_id, {})
        
        # Get learning path
        learning_path = self.get_learning_path(student_id, course_id)
        
        # Filter to unlocked, uncompleted content
        available_content = [
            item for item in learning_path
            if not item['is_completed'] and item['prerequisites_met']
        ]
        
        # If not enough available content, include related content
        if len(available_content) < num_recommendations:
            # Get completed content
            completed_ids = [
                cid for cid, progress in student_progress.items()
                if progress.get('completed')
            ]
            
            if completed_ids:
                # Find similar content
                for completed_id in completed_ids[-3:]:  # Last 3 completed
                    completed_content = self.dataset.get(completed_id)
                    if completed_content:
                        similar = self.dataset.search(
                            query=completed_content.text_content[:500],
                            filter={'metadata.source': 'course_content'},
                            limit=10
                        )
                        
                        for sim_content in similar:
                            if sim_content.unique_id not in [c['content_id'] for c in available_content]:
                                available_content.append({
                                    'content_id': sim_content.unique_id,
                                    'title': sim_content.metadata.title,
                                    'type': sim_content.metadata.custom_metadata.get('content_type'),
                                    'reason': 'similar_to_completed'
                                })
        
        # Sort by priority and return top N
        recommendations = sorted(
            available_content,
            key=lambda x: x.get('priority', 0),
            reverse=True
        )[:num_recommendations]
        
        return recommendations
    
    def generate_progress_report(self, student_id: str,
                               course_id: str) -> Dict[str, Any]:
        """Generate detailed progress report for student."""
        # Get course info
        course = self.dataset.get(course_id)
        if not course:
            return {}
        
        # Get all course content
        all_content = self._get_course_content(course_id)
        total_content = len(all_content)
        
        # Get student progress
        student_progress = self.student_progress.get(student_id, {})
        
        # Calculate metrics
        completed_content = [
            cid for cid, progress in student_progress.items()
            if progress.get('completed')
        ]
        
        completion_rate = len(completed_content) / total_content if total_content > 0 else 0
        
        # Calculate time spent
        total_time_spent = sum(
            progress.get('time_spent', 0)
            for progress in student_progress.values()
        )
        
        # Calculate average score
        scores = [
            progress.get('score', 0)
            for progress in student_progress.values()
            if progress.get('score') is not None
        ]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Analyze by content type
        progress_by_type = defaultdict(lambda: {'total': 0, 'completed': 0})
        
        for content in all_content:
            content_type = content.metadata.custom_metadata.get('content_type')
            progress_by_type[content_type]['total'] += 1
            
            if content.unique_id in completed_content:
                progress_by_type[content_type]['completed'] += 1
        
        # Generate report
        report = {
            'student_id': student_id,
            'course_id': course_id,
            'course_title': course.metadata.title,
            'overall_progress': {
                'completion_rate': completion_rate,
                'completed_items': len(completed_content),
                'total_items': total_content,
                'time_spent_hours': total_time_spent / 60,
                'average_score': average_score
            },
            'progress_by_type': dict(progress_by_type),
            'recent_activity': self._get_recent_activity(student_id, course_id),
            'strengths': self._identify_strengths(student_id, student_progress),
            'areas_for_improvement': self._identify_improvements(student_id, student_progress),
            'next_recommended': self.recommend_content(student_id, course_id, 3)
        }
        
        return report
    
    def _get_recent_activity(self, student_id: str,
                           course_id: str,
                           days: int = 7) -> List[Dict[str, Any]]:
        """Get recent student activity."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_events = [
            event for event in self.engagement_metrics.get(student_id, [])
            if datetime.fromisoformat(event['timestamp']) > cutoff_date
        ]
        
        # Get content details
        activity = []
        for event in recent_events[-10:]:  # Last 10 events
            content = self.dataset.get(event['content_id'])
            if content:
                activity.append({
                    'timestamp': event['timestamp'],
                    'action': event['action'],
                    'content_title': content.metadata.title,
                    'content_type': content.metadata.custom_metadata.get('content_type')
                })
        
        return activity
    
    def _identify_strengths(self, student_id: str,
                          progress: Dict[str, Any]) -> List[str]:
        """Identify student strengths based on performance."""
        strengths = []
        
        # High scores
        high_score_content = [
            self.dataset.get(cid)
            for cid, prog in progress.items()
            if prog.get('score', 0) >= 90
        ]
        
        if len(high_score_content) >= 3:
            strengths.append("Consistently high performance on assessments")
        
        # Quick completion
        quick_completions = [
            prog for prog in progress.values()
            if prog.get('time_spent', float('inf')) < 20
        ]
        
        if len(quick_completions) >= 5:
            strengths.append("Efficient learning and quick comprehension")
        
        return strengths
    
    def _identify_improvements(self, student_id: str,
                             progress: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement."""
        improvements = []
        
        # Low scores
        low_score_content = [
            self.dataset.get(cid)
            for cid, prog in progress.items()
            if prog.get('score', 100) < 70
        ]
        
        if low_score_content:
            topics = set()
            for content in low_score_content:
                if content:
                    objectives = content.metadata.custom_metadata.get('learning_objectives', [])
                    topics.update(objectives[:1])  # Get primary objective
            
            if topics:
                improvements.append(f"Focus on: {', '.join(list(topics)[:3])}")
        
        return improvements

# Example usage
if __name__ == "__main__":
    # Initialize system
    cms = CourseManagementSystem()
    
    # Create course
    course = cms.create_course(
        course_code="CS101",
        title="Introduction to Computer Science",
        description="Foundational course covering programming fundamentals...",
        instructor={
            "name": "Dr. Jane Smith",
            "email": "jsmith@university.edu",
            "office": "Science Building 203"
        },
        credits=3,
        prerequisites=["MATH101"],
        learning_objectives=[
            LearningObjective(
                id="LO1",
                description="Write and debug Python programs",
                bloom_level="apply",
                measurable=True,
                assessment_methods=["programming assignments", "lab exercises"]
            ),
            LearningObjective(
                id="LO2",
                description="Analyze algorithm complexity",
                bloom_level="analyze",
                measurable=True,
                assessment_methods=["quizzes", "exams"]
            )
        ]
    )
    
    # Add module
    module1 = cms.add_module(
        course_id=course.unique_id,
        module_number=1,
        title="Python Basics",
        description="Introduction to Python programming language",
        learning_objectives=[
            "Understand Python syntax and data types",
            "Write simple Python programs",
            "Use Python's built-in functions"
        ],
        estimated_hours=8.0
    )
    
    # Add lecture
    lecture = cms.add_content(
        module_id=module1.unique_id,
        content_type=ContentType.LECTURE,
        title="Variables and Data Types",
        content_path="/materials/cs101/lecture1.pdf",
        description="Introduction to Python variables and basic data types",
        difficulty=DifficultyLevel.BEGINNER,
        estimated_time=45,
        learning_objectives=["Understand Python data types"]
    )
    
    # Add assignment
    assignment = cms.add_content(
        module_id=module1.unique_id,
        content_type=ContentType.ASSIGNMENT,
        title="Programming Assignment 1",
        content_path="/materials/cs101/assignment1.md",
        description="Practice with variables and basic operations",
        difficulty=DifficultyLevel.BEGINNER,
        estimated_time=120,
        prerequisites=[lecture.unique_id],
        metadata_extra={
            "due_date": "2024-09-15",
            "points": 100,
            "submission_type": "file upload"
        }
    )
    
    # Track student progress
    student_id = "student123"
    
    cms.track_student_progress(
        student_id=student_id,
        content_id=lecture.unique_id,
        action="completed",
        data={"time_spent": 42, "score": 100}
    )
    
    cms.track_student_progress(
        student_id=student_id,
        content_id=assignment.unique_id,
        action="submitted",
        data={"time_spent": 95, "score": 88}
    )
    
    # Get learning path
    learning_path = cms.get_learning_path(student_id, course.unique_id)
    
    print("Learning Path:")
    for item in learning_path[:5]:
        status = "✓" if item['is_completed'] else ("🔒" if item['locked'] else "○")
        print(f"{status} {item['title']} ({item['type']}) - {item['estimated_time']}min")
    
    # Generate progress report
    report = cms.generate_progress_report(student_id, course.unique_id)
    
    print(f"\nProgress Report:")
    print(f"Completion: {report['overall_progress']['completion_rate']:.1%}")
    print(f"Average Score: {report['overall_progress']['average_score']:.1f}")
    print(f"Time Spent: {report['overall_progress']['time_spent_hours']:.1f} hours")
```

## Key Concepts

### Hierarchical Organization

Course content is organized hierarchically:
- **Courses**: Top-level containers with metadata
- **Modules**: Logical units within courses
- **Content Items**: Individual learning materials
- **Prerequisites**: Dependencies between content

### Learning Analytics

Comprehensive tracking and analysis:
- **Progress Tracking**: Completion status and scores
- **Engagement Metrics**: Time spent, interactions
- **Learning Paths**: Personalized content sequences
- **Performance Analysis**: Strengths and weaknesses

### Adaptive Learning

The system adapts to student needs:
- **Prerequisite Checking**: Ensures readiness
- **Difficulty Progression**: Gradual complexity increase
- **Personalized Recommendations**: Based on performance
- **Learning Style Adaptation**: Content type preferences

## Extensions

### Advanced Features

1. **Collaborative Learning**
   - Discussion forums
   - Peer review
   - Group projects
   - Study groups

2. **Assessment Engine**
   - Auto-graded quizzes
   - Rubric-based grading
   - Plagiarism detection
   - Competency mapping

3. **Content Authoring**
   - WYSIWYG editors
   - Interactive elements
   - Multimedia support
   - Version control

4. **Analytics Dashboard**
   - Real-time metrics
   - Predictive analytics
   - Early warning system
   - Engagement heatmaps

### Integration Options

1. **LMS Platforms**
   - Canvas API
   - Moodle plugins
   - Blackboard integration
   - Google Classroom

2. **Content Sources**
   - YouTube videos
   - Khan Academy
   - Coursera content
   - Open textbooks

3. **Communication Tools**
   - Email notifications
   - SMS alerts
   - Push notifications
   - Calendar integration

## Best Practices

1. **Content Design**
   - Clear learning objectives
   - Consistent structure
   - Accessible formats
   - Mobile-friendly

2. **Student Engagement**
   - Regular feedback
   - Progress visualization
   - Achievement badges
   - Social learning

3. **Data Privacy**
   - FERPA compliance
   - Secure authentication
   - Data encryption
   - Access controls

4. **Quality Assurance**
   - Content review process
   - Student feedback loops
   - Performance metrics
   - Continuous improvement

This course management system provides a comprehensive foundation for modern educational content delivery and learning analytics.