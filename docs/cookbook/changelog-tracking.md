# Product Changelog Tracking

Build a comprehensive changelog management system that tracks product updates, analyzes feature evolution, monitors competitor changes, and provides insights into product development trends.

## Problem Statement

Product teams, developers, and users need to track changes across multiple products, understand feature evolution, monitor competitor updates, and analyze development patterns. Traditional changelogs are scattered, inconsistently formatted, and difficult to analyze systematically.

## Solution Overview

We'll build a changelog tracking system that:
1. Ingests changelogs from multiple sources and formats
2. Normalizes and categorizes changes
3. Tracks feature evolution and dependencies
4. Analyzes release patterns and velocity
5. Provides competitive intelligence

## Complete Code

```python
import os
import re
import json
import requests
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum
import semver
import feedparser
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class ChangeType(Enum):
    """Types of changes in changelog."""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    IMPROVEMENT = "improvement"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BREAKING = "breaking"
    DEPRECATED = "deprecated"
    REMOVED = "removed"

class ChangeCategory(Enum):
    """Product areas affected by changes."""
    API = "api"
    UI = "ui"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    INFRASTRUCTURE = "infrastructure"

@dataclass
class VersionInfo:
    """Structured version information."""
    version: str
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    @classmethod
    def parse(cls, version_string: str) -> 'VersionInfo':
        """Parse version string into structured format."""
        try:
            parsed = semver.VersionInfo.parse(version_string)
            return cls(
                version=version_string,
                major=parsed.major,
                minor=parsed.minor,
                patch=parsed.patch,
                prerelease=parsed.prerelease,
                build=parsed.build
            )
        except:
            # Fallback for non-semver versions
            parts = re.findall(r'\d+', version_string)
            return cls(
                version=version_string,
                major=int(parts[0]) if parts else 0,
                minor=int(parts[1]) if len(parts) > 1 else 0,
                patch=int(parts[2]) if len(parts) > 2 else 0
            )

class ChangelogTracker:
    """Comprehensive changelog tracking and analysis system."""
    
    def __init__(self, dataset_path: str = "changelog_tracker.lance"):
        """Initialize changelog tracker."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Change detection patterns
        self.change_patterns = {
            ChangeType.FEATURE: [
                r'(?:new|added?|introduce[ds]?|implement(?:ed)?)\s+(.+)',
                r'(?:feature|functionality):\s*(.+)',
                r'\[(?:new|feature)\]\s*(.+)'
            ],
            ChangeType.BUGFIX: [
                r'(?:fix(?:ed)?|resolve[ds]?|repair(?:ed)?)\s+(.+)',
                r'(?:bug|issue|problem)(?:\s+fix)?:\s*(.+)',
                r'\[(?:fix|bugfix)\]\s*(.+)'
            ],
            ChangeType.IMPROVEMENT: [
                r'(?:improve[ds]?|enhance[ds]?|optimize[ds]?)\s+(.+)',
                r'(?:enhancement|improvement):\s*(.+)',
                r'\[(?:enhancement|improvement)\]\s*(.+)'
            ],
            ChangeType.SECURITY: [
                r'(?:security|vulnerability|CVE)[\s:-]+(.+)',
                r'\[security\]\s*(.+)'
            ],
            ChangeType.BREAKING: [
                r'(?:breaking[\s-]change|BREAKING):\s*(.+)',
                r'\[breaking\]\s*(.+)'
            ],
            ChangeType.DEPRECATED: [
                r'(?:deprecate[ds]?|deprecated):\s*(.+)',
                r'\[deprecated?\]\s*(.+)'
            ]
        }
        
        # Category detection keywords
        self.category_keywords = {
            ChangeCategory.API: ['api', 'endpoint', 'rest', 'graphql', 'webhook'],
            ChangeCategory.UI: ['ui', 'interface', 'design', 'layout', 'component', 'style'],
            ChangeCategory.DATABASE: ['database', 'db', 'migration', 'schema', 'query'],
            ChangeCategory.AUTHENTICATION: ['auth', 'login', 'oauth', 'jwt', 'session'],
            ChangeCategory.PERFORMANCE: ['performance', 'speed', 'optimization', 'cache'],
            ChangeCategory.SECURITY: ['security', 'encryption', 'vulnerability', 'permission'],
            ChangeCategory.DOCUMENTATION: ['docs', 'documentation', 'readme', 'guide'],
            ChangeCategory.INFRASTRUCTURE: ['infrastructure', 'deployment', 'docker', 'kubernetes', 'ci/cd']
        }
        
        # Product tracking
        self.tracked_products = {}
        self.release_patterns = defaultdict(list)
        
    def add_product(self, product_name: str,
                   changelog_url: str,
                   product_type: str = "software",
                   company: Optional[str] = None,
                   repository_url: Optional[str] = None,
                   tags: List[str] = None) -> FrameRecord:
        """Add product to tracking system."""
        print(f"Adding product: {product_name}")
        
        # Create product metadata
        metadata = create_metadata(
            title=product_name,
            source="product",
            product_name=product_name,
            product_type=product_type,
            company=company,
            changelog_url=changelog_url,
            repository_url=repository_url,
            tags=tags or [],
            added_date=datetime.now().isoformat(),
            last_checked=datetime.now().isoformat(),
            total_releases=0,
            latest_version=None,
            first_tracked_version=None
        )
        
        # Create product record
        record = FrameRecord(
            text_content=f"{product_name}\n\nType: {product_type}\nCompany: {company or 'Unknown'}\nChangelog: {changelog_url}",
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="collection_header"
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        # Track product
        self.tracked_products[product_name] = {
            'id': record.unique_id,
            'url': changelog_url,
            'type': product_type
        }
        
        return record
    
    def ingest_changelog(self, product_name: str,
                        changelog_content: Optional[str] = None,
                        changelog_format: str = "markdown") -> List[FrameRecord]:
        """Ingest and parse changelog for a product."""
        if product_name not in self.tracked_products:
            raise ValueError(f"Product {product_name} not tracked")
        
        product_info = self.tracked_products[product_name]
        
        # Fetch changelog if not provided
        if not changelog_content:
            changelog_content = self._fetch_changelog(product_info['url'])
        
        # Parse changelog based on format
        if changelog_format == "markdown":
            releases = self._parse_markdown_changelog(changelog_content)
        elif changelog_format == "json":
            releases = self._parse_json_changelog(changelog_content)
        elif changelog_format == "rss":
            releases = self._parse_rss_changelog(product_info['url'])
        else:
            releases = self._parse_generic_changelog(changelog_content)
        
        print(f"Parsed {len(releases)} releases")
        
        # Process each release
        release_records = []
        for release in releases:
            record = self._create_release_record(
                release, 
                product_info['id'],
                product_name
            )
            if record:
                release_records.append(record)
        
        # Update product metadata
        if release_records:
            self._update_product_metadata(product_info['id'], release_records)
        
        # Analyze release patterns
        self._analyze_release_patterns(product_name, release_records)
        
        return release_records
    
    def _fetch_changelog(self, url: str) -> str:
        """Fetch changelog content from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching changelog: {e}")
            return ""
    
    def _parse_markdown_changelog(self, content: str) -> List[Dict[str, Any]]:
        """Parse markdown-formatted changelog."""
        releases = []
        
        # Common patterns for version headers
        version_patterns = [
            r'^#{1,3}\s*(?:v|version)?\s*(\d+\.\d+(?:\.\d+)?(?:[-\.]\w+)?)',
            r'^#{1,3}\s*\[(\d+\.\d+(?:\.\d+)?(?:[-\.]\w+)?)\]',
            r'^\*\*(?:v|version)?\s*(\d+\.\d+(?:\.\d+)?(?:[-\.]\w+)?)\*\*'
        ]
        
        lines = content.split('\n')
        current_release = None
        
        for i, line in enumerate(lines):
            # Check for version header
            version_match = None
            for pattern in version_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    version_match = match
                    break
            
            if version_match:
                # Save previous release
                if current_release:
                    releases.append(current_release)
                
                # Start new release
                version = version_match.group(1)
                
                # Extract date if present
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                release_date = date_match.group(1) if date_match else None
                
                current_release = {
                    'version': version,
                    'date': release_date,
                    'changes': [],
                    'raw_content': line
                }
            
            elif current_release and line.strip():
                # Parse change entry
                change = self._parse_change_entry(line)
                if change:
                    current_release['changes'].append(change)
                    current_release['raw_content'] += '\n' + line
        
        # Don't forget last release
        if current_release:
            releases.append(current_release)
        
        return releases
    
    def _parse_json_changelog(self, content: str) -> List[Dict[str, Any]]:
        """Parse JSON-formatted changelog."""
        try:
            data = json.loads(content)
            releases = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                # Array of releases
                for item in data:
                    release = {
                        'version': item.get('version', ''),
                        'date': item.get('date', item.get('released', '')),
                        'changes': self._parse_json_changes(item.get('changes', [])),
                        'raw_content': json.dumps(item, indent=2)
                    }
                    releases.append(release)
            
            elif isinstance(data, dict) and 'releases' in data:
                # Releases under a key
                for item in data['releases']:
                    release = {
                        'version': item.get('version', ''),
                        'date': item.get('date', ''),
                        'changes': self._parse_json_changes(item.get('changes', [])),
                        'raw_content': json.dumps(item, indent=2)
                    }
                    releases.append(release)
            
            return releases
            
        except json.JSONDecodeError:
            print("Failed to parse JSON changelog")
            return []
    
    def _parse_json_changes(self, changes: List[Any]) -> List[Dict[str, Any]]:
        """Parse changes from JSON format."""
        parsed_changes = []
        
        for change in changes:
            if isinstance(change, str):
                parsed = self._parse_change_entry(change)
                if parsed:
                    parsed_changes.append(parsed)
            elif isinstance(change, dict):
                parsed_changes.append({
                    'type': self._detect_change_type(change.get('description', '')),
                    'category': self._detect_change_category(change.get('description', '')),
                    'description': change.get('description', ''),
                    'scope': change.get('scope'),
                    'breaking': change.get('breaking', False)
                })
        
        return parsed_changes
    
    def _parse_rss_changelog(self, feed_url: str) -> List[Dict[str, Any]]:
        """Parse RSS/Atom feed changelog."""
        releases = []
        
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # Extract version from title
                version_match = re.search(r'(\d+\.\d+(?:\.\d+)?(?:[-\.]\w+)?)', entry.title)
                if version_match:
                    version = version_match.group(1)
                    
                    # Parse content for changes
                    content = entry.get('summary', entry.get('description', ''))
                    changes = self._extract_changes_from_html(content)
                    
                    release = {
                        'version': version,
                        'date': entry.get('published', entry.get('updated')),
                        'changes': changes,
                        'raw_content': content,
                        'link': entry.get('link')
                    }
                    
                    releases.append(release)
        
        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
        
        return releases
    
    def _parse_generic_changelog(self, content: str) -> List[Dict[str, Any]]:
        """Parse changelog with unknown format."""
        releases = []
        
        # Try to identify version sections
        lines = content.split('\n')
        current_release = None
        
        for line in lines:
            # Look for version-like strings
            version_match = re.search(r'(\d+\.\d+(?:\.\d+)?(?:[-\.]\w+)?)', line)
            
            if version_match and not current_release:
                # Likely a new version section
                current_release = {
                    'version': version_match.group(1),
                    'date': self._extract_date(line),
                    'changes': [],
                    'raw_content': line
                }
            
            elif current_release and line.strip() and not version_match:
                # Likely a change entry
                change = self._parse_change_entry(line)
                if change:
                    current_release['changes'].append(change)
                    current_release['raw_content'] += '\n' + line
            
            elif version_match and current_release:
                # New version found, save current
                releases.append(current_release)
                current_release = {
                    'version': version_match.group(1),
                    'date': self._extract_date(line),
                    'changes': [],
                    'raw_content': line
                }
        
        # Don't forget last release
        if current_release:
            releases.append(current_release)
        
        return releases
    
    def _parse_change_entry(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse individual change entry."""
        # Skip empty or header-like lines
        if not line.strip() or line.strip().startswith('#'):
            return None
        
        # Remove common prefixes
        clean_line = re.sub(r'^[-*+•]\s*', '', line.strip())
        
        # Detect change type
        change_type = self._detect_change_type(clean_line)
        
        # Detect category
        category = self._detect_change_category(clean_line)
        
        # Check if breaking change
        breaking = bool(re.search(r'\bBREAKING\b|⚠️|🚨', line))
        
        # Extract scope if present (e.g., "feat(api): ...")
        scope_match = re.match(r'^(\w+)\(([^)]+)\):\s*(.+)', clean_line)
        scope = scope_match.group(2) if scope_match else None
        description = scope_match.group(3) if scope_match else clean_line
        
        return {
            'type': change_type,
            'category': category,
            'description': description,
            'scope': scope,
            'breaking': breaking,
            'raw': line
        }
    
    def _detect_change_type(self, text: str) -> ChangeType:
        """Detect type of change from text."""
        text_lower = text.lower()
        
        for change_type, patterns in self.change_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return change_type
        
        # Default to improvement
        return ChangeType.IMPROVEMENT
    
    def _detect_change_category(self, text: str) -> Optional[ChangeCategory]:
        """Detect category of change from text."""
        text_lower = text.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text."""
        # Common date patterns
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
            r'(\d{2}\.\d{2}\.\d{4})',  # DD.MM.YYYY
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})'  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_changes_from_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract changes from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        changes = []
        
        # Look for list items
        for li in soup.find_all('li'):
            text = li.get_text().strip()
            change = self._parse_change_entry(text)
            if change:
                changes.append(change)
        
        # If no list items, try paragraphs
        if not changes:
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if text:
                    change = self._parse_change_entry(text)
                    if change:
                        changes.append(change)
        
        return changes
    
    def _create_release_record(self, release: Dict[str, Any],
                             product_id: str,
                             product_name: str) -> Optional[FrameRecord]:
        """Create release record from parsed data."""
        if not release.get('version'):
            return None
        
        # Parse version
        version_info = VersionInfo.parse(release['version'])
        
        # Analyze changes
        change_analysis = self._analyze_changes(release['changes'])
        
        # Create metadata
        metadata = create_metadata(
            title=f"{product_name} v{release['version']}",
            source="product_release",
            product_id=product_id,
            product_name=product_name,
            version=release['version'],
            version_major=version_info.major,
            version_minor=version_info.minor,
            version_patch=version_info.patch,
            release_date=release.get('date'),
            indexed_date=datetime.now().isoformat(),
            
            # Change analysis
            total_changes=len(release['changes']),
            change_types=change_analysis['types'],
            change_categories=change_analysis['categories'],
            breaking_changes=change_analysis['breaking_count'],
            
            # Detailed changes
            features=change_analysis['features'],
            bugfixes=change_analysis['bugfixes'],
            improvements=change_analysis['improvements'],
            security_fixes=change_analysis['security'],
            
            # Additional info
            release_link=release.get('link'),
            is_prerelease=bool(version_info.prerelease),
            is_major_release=version_info.minor == 0 and version_info.patch == 0
        )
        
        # Create searchable content
        content = f"# {product_name} v{release['version']}\n\n"
        if release.get('date'):
            content += f"Released: {release['date']}\n\n"
        
        content += "## Changes\n\n"
        for change in release['changes']:
            content += f"- {change['description']}\n"
        
        # Create record
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Add relationship to product
        record.metadata = add_relationship_to_metadata(
            record.metadata,
            create_relationship(
                source_id=record.unique_id,
                target_id=product_id,
                relationship_type="child"
            )
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        return record
    
    def _analyze_changes(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze changes in a release."""
        analysis = {
            'types': defaultdict(int),
            'categories': defaultdict(int),
            'breaking_count': 0,
            'features': [],
            'bugfixes': [],
            'improvements': [],
            'security': []
        }
        
        for change in changes:
            # Count types
            change_type = change.get('type', ChangeType.IMPROVEMENT)
            analysis['types'][change_type.value] += 1
            
            # Count categories
            category = change.get('category')
            if category:
                analysis['categories'][category.value] += 1
            
            # Count breaking changes
            if change.get('breaking'):
                analysis['breaking_count'] += 1
            
            # Categorize changes
            desc = change['description']
            if change_type == ChangeType.FEATURE:
                analysis['features'].append(desc)
            elif change_type == ChangeType.BUGFIX:
                analysis['bugfixes'].append(desc)
            elif change_type == ChangeType.IMPROVEMENT:
                analysis['improvements'].append(desc)
            elif change_type == ChangeType.SECURITY:
                analysis['security'].append(desc)
        
        # Convert defaultdicts to regular dicts
        analysis['types'] = dict(analysis['types'])
        analysis['categories'] = dict(analysis['categories'])
        
        return analysis
    
    def _update_product_metadata(self, product_id: str,
                               release_records: List[FrameRecord]):
        """Update product metadata with latest release info."""
        product = self.dataset.get(product_id)
        if not product:
            return
        
        # Sort releases by version
        sorted_releases = sorted(
            release_records,
            key=lambda x: semver.VersionInfo.parse(
                x.metadata.custom_metadata['version'].replace('-', '+')
            ),
            reverse=True
        )
        
        if sorted_releases:
            latest = sorted_releases[0].metadata.custom_metadata
            product.metadata.custom_metadata['latest_version'] = latest['version']
            product.metadata.custom_metadata['latest_release_date'] = latest.get('release_date')
            product.metadata.custom_metadata['total_releases'] = len(release_records)
            
            if not product.metadata.custom_metadata.get('first_tracked_version'):
                oldest = sorted_releases[-1].metadata.custom_metadata
                product.metadata.custom_metadata['first_tracked_version'] = oldest['version']
        
        product.metadata.custom_metadata['last_checked'] = datetime.now().isoformat()
        
        self.dataset.update(product)
    
    def _analyze_release_patterns(self, product_name: str,
                                releases: List[FrameRecord]):
        """Analyze release patterns for a product."""
        if len(releases) < 2:
            return
        
        # Sort by date
        dated_releases = [
            r for r in releases
            if r.metadata.custom_metadata.get('release_date')
        ]
        
        dated_releases.sort(
            key=lambda x: x.metadata.custom_metadata['release_date']
        )
        
        # Calculate release intervals
        intervals = []
        for i in range(1, len(dated_releases)):
            prev_date = datetime.fromisoformat(
                dated_releases[i-1].metadata.custom_metadata['release_date']
            )
            curr_date = datetime.fromisoformat(
                dated_releases[i].metadata.custom_metadata['release_date']
            )
            
            interval = (curr_date - prev_date).days
            intervals.append(interval)
        
        # Store patterns
        if intervals:
            self.release_patterns[product_name] = {
                'intervals': intervals,
                'avg_interval': sum(intervals) / len(intervals),
                'min_interval': min(intervals),
                'max_interval': max(intervals),
                'release_count': len(dated_releases)
            }
    
    def search_changes(self, query: str,
                      product_name: Optional[str] = None,
                      change_type: Optional[ChangeType] = None,
                      category: Optional[ChangeCategory] = None,
                      date_range: Optional[Tuple[datetime, datetime]] = None) -> List[Dict[str, Any]]:
        """Search across changelog entries."""
        # Build filter
        filter_dict = {'metadata.source': 'product_release'}
        
        if product_name:
            filter_dict['metadata.product_name'] = product_name
        
        if change_type:
            filter_dict[f'metadata.change_types.{change_type.value}'] = {'gt': 0}
        
        if category:
            filter_dict[f'metadata.change_categories.{category.value}'] = {'gt': 0}
        
        if date_range:
            filter_dict['metadata.release_date'] = {
                'gte': date_range[0].isoformat(),
                'lte': date_range[1].isoformat()
            }
        
        # Search
        results = self.dataset.search(
            query=query,
            filter=filter_dict,
            limit=100
        )
        
        # Format results
        formatted_results = []
        for result in results:
            meta = result.metadata.custom_metadata
            
            formatted_results.append({
                'product': meta['product_name'],
                'version': meta['version'],
                'date': meta.get('release_date'),
                'matching_changes': self._extract_matching_changes(
                    result.text_content, query
                ),
                'total_changes': meta['total_changes'],
                'breaking_changes': meta.get('breaking_changes', 0),
                'score': getattr(result, 'score', 0)
            })
        
        return formatted_results
    
    def _extract_matching_changes(self, content: str, query: str) -> List[str]:
        """Extract changes matching search query."""
        matching = []
        query_lower = query.lower()
        
        # Extract change lines
        lines = content.split('\n')
        for line in lines:
            if line.startswith('- ') and query_lower in line.lower():
                matching.append(line[2:].strip())
        
        return matching[:5]  # Limit to 5 matches
    
    def compare_products(self, products: List[str],
                        days_back: int = 365) -> Dict[str, Any]:
        """Compare release patterns across products."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        comparison = {
            'products': products,
            'period': f"Last {days_back} days",
            'metrics': {}
        }
        
        for product in products:
            # Get releases
            releases = self.dataset.filter({
                'metadata.source': 'product_release',
                'metadata.product_name': product,
                'metadata.release_date': {'gte': cutoff_date.isoformat()}
            })
            
            if releases:
                # Calculate metrics
                total_releases = len(releases)
                
                # Count change types
                total_features = sum(
                    r.metadata.custom_metadata.get('change_types', {}).get('feature', 0)
                    for r in releases
                )
                total_bugfixes = sum(
                    r.metadata.custom_metadata.get('change_types', {}).get('bugfix', 0)
                    for r in releases
                )
                
                # Major releases
                major_releases = sum(
                    1 for r in releases
                    if r.metadata.custom_metadata.get('is_major_release')
                )
                
                # Release velocity
                patterns = self.release_patterns.get(product, {})
                
                comparison['metrics'][product] = {
                    'total_releases': total_releases,
                    'major_releases': major_releases,
                    'total_features': total_features,
                    'total_bugfixes': total_bugfixes,
                    'avg_days_between_releases': patterns.get('avg_interval', 0),
                    'features_per_release': total_features / total_releases if total_releases else 0,
                    'latest_version': releases[0].metadata.custom_metadata.get('version')
                }
        
        return comparison
    
    def track_feature_evolution(self, feature_keywords: List[str],
                              product_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Track evolution of features across releases."""
        # Search for features
        filter_dict = {
            'metadata.source': 'product_release',
            'metadata.change_types.feature': {'gt': 0}
        }
        
        if product_name:
            filter_dict['metadata.product_name'] = product_name
        
        # Search for each keyword
        evolution = []
        
        for keyword in feature_keywords:
            results = self.dataset.search(
                query=keyword,
                filter=filter_dict,
                limit=50
            )
            
            # Track mentions over time
            timeline = []
            for result in results:
                meta = result.metadata.custom_metadata
                
                # Check if keyword appears in features
                features = meta.get('features', [])
                matching_features = [
                    f for f in features
                    if keyword.lower() in f.lower()
                ]
                
                if matching_features:
                    timeline.append({
                        'product': meta['product_name'],
                        'version': meta['version'],
                        'date': meta.get('release_date'),
                        'features': matching_features
                    })
            
            if timeline:
                evolution.append({
                    'keyword': keyword,
                    'timeline': sorted(timeline, key=lambda x: x['date'] or ''),
                    'total_mentions': len(timeline)
                })
        
        return evolution
    
    def generate_release_summary(self, product_name: str,
                               version: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive release summary."""
        # Get release
        filter_dict = {
            'metadata.source': 'product_release',
            'metadata.product_name': product_name
        }
        
        if version:
            filter_dict['metadata.version'] = version
        else:
            # Get latest
            releases = self.dataset.filter(filter_dict)
            if not releases:
                return {'error': 'No releases found'}
            
            # Sort by version
            releases.sort(
                key=lambda x: semver.VersionInfo.parse(
                    x.metadata.custom_metadata['version'].replace('-', '+')
                ),
                reverse=True
            )
            
            release = releases[0]
        else:
            releases = self.dataset.filter(filter_dict)
            if not releases:
                return {'error': 'Release not found'}
            release = releases[0]
        
        meta = release.metadata.custom_metadata
        
        # Generate summary
        summary = {
            'product': product_name,
            'version': meta['version'],
            'release_date': meta.get('release_date'),
            'type': 'Major' if meta.get('is_major_release') else 'Minor',
            'total_changes': meta['total_changes'],
            'breakdown': {
                'features': len(meta.get('features', [])),
                'bugfixes': len(meta.get('bugfixes', [])),
                'improvements': len(meta.get('improvements', [])),
                'security': len(meta.get('security', []))
            },
            'breaking_changes': meta.get('breaking_changes', 0),
            'highlights': {
                'top_features': meta.get('features', [])[:3],
                'critical_fixes': [
                    fix for fix in meta.get('bugfixes', [])
                    if any(word in fix.lower() for word in ['critical', 'security', 'vulnerability'])
                ]
            },
            'categories_affected': list(meta.get('change_categories', {}).keys())
        }
        
        return summary
    
    def predict_next_release(self, product_name: str) -> Dict[str, Any]:
        """Predict next release date based on patterns."""
        patterns = self.release_patterns.get(product_name)
        if not patterns or not patterns.get('intervals'):
            return {'error': 'Insufficient data for prediction'}
        
        # Get latest release
        releases = self.dataset.filter({
            'metadata.source': 'product_release',
            'metadata.product_name': product_name
        })
        
        if not releases:
            return {'error': 'No releases found'}
        
        # Sort by date
        dated_releases = [
            r for r in releases
            if r.metadata.custom_metadata.get('release_date')
        ]
        
        if not dated_releases:
            return {'error': 'No dated releases found'}
        
        dated_releases.sort(
            key=lambda x: x.metadata.custom_metadata['release_date'],
            reverse=True
        )
        
        latest_release = dated_releases[0]
        latest_date = datetime.fromisoformat(
            latest_release.metadata.custom_metadata['release_date']
        )
        
        # Predict based on average interval
        avg_interval = patterns['avg_interval']
        predicted_date = latest_date + timedelta(days=avg_interval)
        
        # Calculate confidence based on consistency
        intervals = patterns['intervals']
        std_dev = np.std(intervals) if len(intervals) > 1 else 0
        consistency = 1 - (std_dev / avg_interval) if avg_interval > 0 else 0
        
        return {
            'product': product_name,
            'latest_version': latest_release.metadata.custom_metadata['version'],
            'latest_release_date': latest_date.isoformat(),
            'predicted_next_release': predicted_date.isoformat(),
            'days_until_release': (predicted_date - datetime.now()).days,
            'average_release_cycle': f"{avg_interval:.1f} days",
            'confidence': f"{consistency * 100:.1f}%",
            'based_on_releases': patterns['release_count']
        }

# Example usage
if __name__ == "__main__":
    # Initialize tracker
    tracker = ChangelogTracker()
    
    # Add products to track
    products = [
        {
            'name': 'React',
            'url': 'https://github.com/facebook/react/blob/main/CHANGELOG.md',
            'company': 'Meta',
            'type': 'library',
            'tags': ['frontend', 'javascript', 'ui']
        },
        {
            'name': 'Node.js',
            'url': 'https://github.com/nodejs/node/blob/main/CHANGELOG.md',
            'company': 'OpenJS Foundation',
            'type': 'runtime',
            'tags': ['backend', 'javascript', 'server']
        }
    ]
    
    for product in products:
        tracker.add_product(
            product_name=product['name'],
            changelog_url=product['url'],
            product_type=product['type'],
            company=product['company'],
            tags=product['tags']
        )
    
    # Ingest changelogs
    for product in products:
        releases = tracker.ingest_changelog(
            product_name=product['name'],
            changelog_format='markdown'
        )
        print(f"Ingested {len(releases)} releases for {product['name']}")
    
    # Search for specific changes
    results = tracker.search_changes(
        query="performance optimization",
        change_type=ChangeType.IMPROVEMENT
    )
    
    print(f"\nFound {len(results)} releases with performance optimizations:")
    for result in results[:5]:
        print(f"- {result['product']} v{result['version']}: {result['matching_changes'][0] if result['matching_changes'] else 'N/A'}")
    
    # Compare products
    comparison = tracker.compare_products(['React', 'Node.js'])
    
    print("\nProduct Comparison:")
    for product, metrics in comparison['metrics'].items():
        print(f"\n{product}:")
        print(f"  Total releases: {metrics['total_releases']}")
        print(f"  Features per release: {metrics['features_per_release']:.1f}")
        print(f"  Avg release cycle: {metrics['avg_days_between_releases']:.1f} days")
    
    # Track feature evolution
    evolution = tracker.track_feature_evolution(
        feature_keywords=['hooks', 'async', 'performance'],
        product_name='React'
    )
    
    print("\nFeature Evolution:")
    for feature in evolution:
        print(f"\n{feature['keyword']}: {feature['total_mentions']} mentions")
        for item in feature['timeline'][-3:]:
            print(f"  v{item['version']}: {item['features'][0][:50]}...")
    
    # Predict next release
    prediction = tracker.predict_next_release('React')
    if 'error' not in prediction:
        print(f"\nNext Release Prediction for {prediction['product']}:")
        print(f"  Expected: {prediction['predicted_next_release']}")
        print(f"  Days until release: {prediction['days_until_release']}")
        print(f"  Confidence: {prediction['confidence']}")
```

## Key Concepts

### Multi-Format Support

The system handles various changelog formats:
- **Markdown**: Headers, lists, sections
- **JSON**: Structured release data
- **RSS/Atom**: Blog-style releases
- **HTML**: Scraped web pages

### Change Analysis

Comprehensive change categorization:
- **Type Detection**: Features, bugs, improvements
- **Category Mapping**: API, UI, Security, etc.
- **Breaking Change**: Impact assessment
- **Scope Extraction**: Component affected

### Release Intelligence

Advanced analytics capabilities:
- **Pattern Analysis**: Release cycles and velocity
- **Feature Evolution**: Track feature development
- **Competitive Analysis**: Compare products
- **Predictive Modeling**: Next release forecasting

## Extensions

### Advanced Features

1. **Automated Monitoring**
   - Scheduled changelog checks
   - Change notifications
   - RSS feed generation
   - Webhook integration

2. **Deep Analysis**
   - Sentiment analysis
   - Technical debt tracking
   - Dependency impact
   - Migration guides

3. **Visualization**
   - Release timelines
   - Feature roadmaps
   - Change heatmaps
   - Velocity charts

4. **Integration**
   - Issue tracker sync
   - CI/CD pipelines
   - Documentation updates
   - Release notes generation

### Data Sources

1. **Repository Integration**
   - GitHub releases
   - GitLab tags
   - Bitbucket
   - Custom Git hooks

2. **Package Registries**
   - npm
   - PyPI
   - Maven Central
   - RubyGems

3. **Documentation Sites**
   - Read the Docs
   - GitBook
   - Docusaurus
   - MkDocs

## Best Practices

1. **Data Quality**
   - Validate versions
   - Normalize formats
   - Handle duplicates
   - Clean descriptions

2. **Performance**
   - Incremental updates
   - Caching strategies
   - Batch processing
   - Index optimization

3. **Analysis Accuracy**
   - Pattern validation
   - Outlier detection
   - Confidence scoring
   - Manual verification

4. **User Experience**
   - Clear visualizations
   - Actionable insights
   - Export options
   - API access

This changelog tracking system provides comprehensive monitoring and analysis of product evolution, helping teams stay informed about changes across their technology stack.