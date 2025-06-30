# Multi-Language Documentation

Build a comprehensive multi-language documentation system that manages translations, maintains consistency across languages, and provides intelligent cross-language search capabilities.

## Problem Statement

Global organizations need documentation in multiple languages while maintaining consistency, tracking translation status, and ensuring updates propagate across all language versions. Manual translation management leads to outdated content and inconsistencies.

## Solution Overview

We'll build a multi-language documentation system that:
1. Manages source and translated documents
2. Tracks translation status and versions
3. Identifies outdated translations
4. Provides cross-language search
5. Maintains terminology consistency

## Complete Code

```python
import os
import re
import json
import hashlib
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
import langdetect
from deep_translator import GoogleTranslator
import difflib
from collections import defaultdict

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

@dataclass
class TranslationUnit:
    """Represents a translatable unit of content."""
    source_id: str
    source_lang: str
    source_text: str
    source_hash: str
    translations: Dict[str, Dict[str, Any]]  # lang -> {text, translator, date}

class MultiLanguageDocumentation:
    """Multi-language documentation management system."""
    
    def __init__(self, dataset_path: str = "multilang_docs.lance"):
        """Initialize multi-language system."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Supported languages
        self.supported_languages = [
            'en', 'es', 'fr', 'de', 'ja', 'zh', 'pt', 'ru', 'ar', 'hi'
        ]
        
        # Translation memory
        self.translation_memory = {}
        self._load_translation_memory()
        
        # Terminology glossary
        self.glossary = self._load_glossary()
        
    def create_source_document(self, 
                             title: str,
                             content: str,
                             doc_type: str = "guide",
                             language: str = "en",
                             tags: List[str] = None) -> FrameRecord:
        """Create a source document in the primary language."""
        print(f"Creating source document: {title} ({language})")
        
        # Detect language if not specified
        if not language:
            language = langdetect.detect(content)
        
        # Generate content hash for change detection
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Create document sections for granular translation
        sections = self._extract_sections(content)
        
        # Create metadata
        metadata = create_metadata(
            title=title,
            source="documentation",
            doc_type=doc_type,
            language=language,
            is_source=True,
            content_hash=content_hash,
            section_count=len(sections),
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            translation_status={lang: "pending" for lang in self.supported_languages if lang != language}
        )
        
        # Create record
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        # Create section records for translation tracking
        for i, section in enumerate(sections):
            self._create_section_record(record.unique_id, section, i, language)
        
        return record
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract translatable sections from content."""
        sections = []
        
        # Split by headers
        header_pattern = r'^(#{1,6})\s+(.+)$'
        lines = content.split('\\n')
        
        current_section = {
            'header': '',
            'content': [],
            'level': 0
        }
        
        for line in lines:
            header_match = re.match(header_pattern, line)
            
            if header_match:
                # Save previous section
                if current_section['content']:
                    current_section['content'] = '\\n'.join(current_section['content'])
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'header': header_match.group(2),
                    'content': [],
                    'level': len(header_match.group(1))
                }
            else:
                current_section['content'].append(line)
        
        # Add final section
        if current_section['content']:
            current_section['content'] = '\\n'.join(current_section['content'])
            sections.append(current_section)
        
        return sections
    
    def _create_section_record(self, parent_id: str, section: Dict[str, str], 
                             index: int, language: str) -> FrameRecord:
        """Create a section record for granular translation."""
        content = f"{section['header']}\\n\\n{section['content']}"
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        metadata = create_metadata(
            title=f"Section: {section['header']}",
            source="documentation_section",
            parent_document=parent_id,
            section_index=index,
            section_level=section['level'],
            language=language,
            content_hash=content_hash,
            is_translated=False
        )
        
        record = FrameRecord(
            text_content=content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Add relationship to parent
        record.metadata = add_relationship_to_metadata(
            record.metadata,
            create_relationship(
                source_id=record.unique_id,
                target_id=parent_id,
                relationship_type="child"
            )
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        return record
    
    def translate_document(self, document_id: str, 
                         target_language: str,
                         translator: str = "auto",
                         use_memory: bool = True) -> FrameRecord:
        """Translate a document to target language."""
        # Get source document
        source_doc = self.dataset.get(document_id)
        if not source_doc:
            raise ValueError(f"Document {document_id} not found")
        
        source_lang = source_doc.metadata.custom_metadata.get('language')
        print(f"Translating from {source_lang} to {target_language}")
        
        # Get sections
        sections = self.dataset.filter({
            'metadata.parent_document': document_id
        })
        
        # Translate content
        if sections:
            # Translate section by section
            translated_content = self._translate_sections(
                sections, source_lang, target_language, translator, use_memory
            )
        else:
            # Translate as whole
            translated_content = self._translate_text(
                source_doc.text_content, source_lang, target_language, 
                translator, use_memory
            )
        
        # Translate title
        translated_title = self._translate_text(
            source_doc.metadata.title, source_lang, target_language,
            translator, use_memory
        )
        
        # Create translated document
        metadata = create_metadata(
            title=translated_title,
            source="documentation",
            doc_type=source_doc.metadata.custom_metadata.get('doc_type'),
            language=target_language,
            is_source=False,
            source_document_id=document_id,
            source_language=source_lang,
            translator=translator,
            translation_date=datetime.now().isoformat(),
            source_content_hash=source_doc.metadata.custom_metadata.get('content_hash'),
            tags=source_doc.metadata.custom_metadata.get('tags', [])
        )
        
        translated_record = FrameRecord(
            text_content=translated_content,
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Add relationship to source
        translated_record.metadata = add_relationship_to_metadata(
            translated_record.metadata,
            create_relationship(
                source_id=translated_record.unique_id,
                target_id=document_id,
                relationship_type="reference",
                properties={'reference_type': 'translation'}
            )
        )
        
        self.dataset.add(translated_record, generate_embedding=True)
        
        # Update source document translation status
        self._update_translation_status(document_id, target_language, "completed")
        
        return translated_record
    
    def _translate_sections(self, sections: List[FrameRecord], 
                          source_lang: str, target_lang: str,
                          translator: str, use_memory: bool) -> str:
        """Translate document sections."""
        translated_sections = []
        
        # Sort sections by index
        sections.sort(key=lambda x: x.metadata.custom_metadata.get('section_index', 0))
        
        for section in sections:
            # Check translation memory
            content_hash = section.metadata.custom_metadata.get('content_hash')
            
            if use_memory and content_hash in self.translation_memory:
                if target_lang in self.translation_memory[content_hash]:
                    translated_text = self.translation_memory[content_hash][target_lang]
                else:
                    translated_text = self._translate_text(
                        section.text_content, source_lang, target_lang, translator
                    )
                    self._update_translation_memory(
                        content_hash, source_lang, section.text_content,
                        target_lang, translated_text
                    )
            else:
                translated_text = self._translate_text(
                    section.text_content, source_lang, target_lang, translator
                )
                if use_memory:
                    self._update_translation_memory(
                        content_hash, source_lang, section.text_content,
                        target_lang, translated_text
                    )
            
            translated_sections.append(translated_text)
        
        return "\\n\\n".join(translated_sections)
    
    def _translate_text(self, text: str, source_lang: str, 
                       target_lang: str, translator: str = "auto") -> str:
        """Translate text using specified translator."""
        if not text.strip():
            return text
        
        # Apply glossary terms
        text_with_placeholders, replacements = self._apply_glossary_placeholders(
            text, source_lang
        )
        
        # Translate
        if translator == "auto" or translator == "google":
            translator_obj = GoogleTranslator(
                source=source_lang,
                target=target_lang
            )
            translated = translator_obj.translate(text_with_placeholders)
        else:
            # Add other translators as needed
            translated = text_with_placeholders
        
        # Replace placeholders with glossary translations
        translated = self._replace_glossary_terms(
            translated, replacements, target_lang
        )
        
        return translated
    
    def _apply_glossary_placeholders(self, text: str, 
                                    source_lang: str) -> Tuple[str, Dict[str, str]]:
        """Replace glossary terms with placeholders."""
        replacements = {}
        modified_text = text
        
        for term_id, term_data in self.glossary.items():
            if source_lang in term_data:
                source_term = term_data[source_lang]
                placeholder = f"[[TERM_{term_id}]]"
                
                # Case-insensitive replacement
                pattern = re.compile(re.escape(source_term), re.IGNORECASE)
                if pattern.search(modified_text):
                    modified_text = pattern.sub(placeholder, modified_text)
                    replacements[placeholder] = term_id
        
        return modified_text, replacements
    
    def _replace_glossary_terms(self, text: str, replacements: Dict[str, str], 
                              target_lang: str) -> str:
        """Replace placeholders with translated glossary terms."""
        for placeholder, term_id in replacements.items():
            if term_id in self.glossary and target_lang in self.glossary[term_id]:
                target_term = self.glossary[term_id][target_lang]
                text = text.replace(placeholder, target_term)
        
        return text
    
    def check_translation_status(self, document_id: str) -> Dict[str, Any]:
        """Check translation status for a document."""
        source_doc = self.dataset.get(document_id)
        if not source_doc:
            return {}
        
        status = {
            'source_language': source_doc.metadata.custom_metadata.get('language'),
            'last_modified': source_doc.metadata.custom_metadata.get('last_modified'),
            'translations': {}
        }
        
        # Find all translations
        translations = self.dataset.filter({
            'metadata.source_document_id': document_id
        })
        
        for trans in translations:
            lang = trans.metadata.custom_metadata.get('language')
            status['translations'][lang] = {
                'status': 'completed',
                'translation_date': trans.metadata.custom_metadata.get('translation_date'),
                'is_outdated': self._is_translation_outdated(source_doc, trans)
            }
        
        # Add missing languages
        for lang in self.supported_languages:
            if lang != status['source_language'] and lang not in status['translations']:
                status['translations'][lang] = {
                    'status': 'pending',
                    'translation_date': None,
                    'is_outdated': False
                }
        
        return status
    
    def _is_translation_outdated(self, source_doc: FrameRecord, 
                               translation: FrameRecord) -> bool:
        """Check if translation is outdated."""
        source_hash = source_doc.metadata.custom_metadata.get('content_hash')
        trans_source_hash = translation.metadata.custom_metadata.get('source_content_hash')
        
        return source_hash != trans_source_hash
    
    def update_source_document(self, document_id: str, 
                             new_content: str) -> Dict[str, Any]:
        """Update source document and track changes."""
        source_doc = self.dataset.get(document_id)
        if not source_doc:
            raise ValueError(f"Document {document_id} not found")
        
        # Calculate diff
        old_content = source_doc.text_content
        diff = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            lineterm=''
        ))
        
        # Update content hash
        new_hash = hashlib.md5(new_content.encode()).hexdigest()
        
        # Create updated record
        source_doc.text_content = new_content
        source_doc.metadata.custom_metadata['content_hash'] = new_hash
        source_doc.metadata.custom_metadata['last_modified'] = datetime.now().isoformat()
        
        # Mark all translations as outdated
        translations = self.dataset.filter({
            'metadata.source_document_id': document_id
        })
        
        outdated_languages = []
        for trans in translations:
            lang = trans.metadata.custom_metadata.get('language')
            outdated_languages.append(lang)
        
        # Update the document
        self.dataset.update(source_doc)
        
        return {
            'document_id': document_id,
            'old_hash': source_doc.metadata.custom_metadata.get('content_hash'),
            'new_hash': new_hash,
            'changes': len(diff),
            'outdated_translations': outdated_languages
        }
    
    def cross_language_search(self, query: str, 
                            languages: List[str] = None,
                            source_language: str = None) -> List[Dict[str, Any]]:
        """Search across multiple languages."""
        if not languages:
            languages = self.supported_languages
        
        # Detect query language if not specified
        if not source_language:
            try:
                source_language = langdetect.detect(query)
            except:
                source_language = 'en'
        
        all_results = []
        
        # Search in source language
        if source_language in languages:
            results = self.dataset.search(
                query=query,
                filter={'metadata.language': source_language},
                limit=20
            )
            all_results.extend([(r, 1.0) for r in results])  # Original query score
        
        # Translate query and search in other languages
        for lang in languages:
            if lang != source_language:
                try:
                    translated_query = self._translate_text(
                        query, source_language, lang, "auto", False
                    )
                    
                    results = self.dataset.search(
                        query=translated_query,
                        filter={'metadata.language': lang},
                        limit=20
                    )
                    
                    # Slightly lower score for translated searches
                    all_results.extend([(r, 0.9) for r in results])
                    
                except Exception as e:
                    print(f"Error searching in {lang}: {e}")
        
        # Deduplicate and sort by score
        seen_ids = set()
        unique_results = []
        
        for result, score in sorted(all_results, key=lambda x: x[1], reverse=True):
            if result.unique_id not in seen_ids:
                seen_ids.add(result.unique_id)
                unique_results.append({
                    'document': result,
                    'score': score,
                    'language': result.metadata.custom_metadata.get('language')
                })
        
        return unique_results
    
    def _load_translation_memory(self):
        """Load translation memory from dataset."""
        tm_records = self.dataset.filter({
            'metadata.source': 'translation_memory'
        })
        
        for record in tm_records:
            content_hash = record.metadata.custom_metadata.get('content_hash')
            translations = record.metadata.custom_metadata.get('translations', {})
            self.translation_memory[content_hash] = translations
    
    def _update_translation_memory(self, content_hash: str, 
                                 source_lang: str, source_text: str,
                                 target_lang: str, target_text: str):
        """Update translation memory."""
        if content_hash not in self.translation_memory:
            self.translation_memory[content_hash] = {
                'source_language': source_lang,
                'source_text': source_text,
                'translations': {}
            }
        
        self.translation_memory[content_hash]['translations'][target_lang] = {
            'text': target_text,
            'date': datetime.now().isoformat()
        }
        
        # Persist to dataset
        self._save_translation_memory_entry(content_hash)
    
    def _save_translation_memory_entry(self, content_hash: str):
        """Save translation memory entry to dataset."""
        entry = self.translation_memory[content_hash]
        
        metadata = create_metadata(
            title=f"TM Entry: {content_hash[:8]}",
            source="translation_memory",
            content_hash=content_hash,
            source_language=entry['source_language'],
            translations=entry['translations']
        )
        
        record = FrameRecord(
            text_content=entry['source_text'],
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        self.dataset.add(record)
    
    def _load_glossary(self) -> Dict[str, Dict[str, str]]:
        """Load terminology glossary."""
        # In production, load from database or file
        return {
            "contextframe": {
                "en": "ContextFrame",
                "es": "ContextFrame",
                "fr": "ContextFrame",
                "de": "ContextFrame",
                "ja": "コンテキストフレーム"
            },
            "embedding": {
                "en": "embedding",
                "es": "incrustación",
                "fr": "incorporation",
                "de": "Einbettung",
                "ja": "埋め込み"
            },
            "dataset": {
                "en": "dataset",
                "es": "conjunto de datos",
                "fr": "jeu de données",
                "de": "Datensatz",
                "ja": "データセット"
            }
        }
    
    def _update_translation_status(self, document_id: str, 
                                 language: str, status: str):
        """Update translation status for a document."""
        doc = self.dataset.get(document_id)
        if doc and 'translation_status' in doc.metadata.custom_metadata:
            doc.metadata.custom_metadata['translation_status'][language] = status
            self.dataset.update(doc)
    
    def generate_translation_report(self) -> Dict[str, Any]:
        """Generate report on translation coverage."""
        report = {
            'total_documents': 0,
            'languages': {},
            'coverage_by_type': {},
            'outdated_translations': [],
            'missing_translations': []
        }
        
        # Get all source documents
        source_docs = self.dataset.filter({
            'metadata.is_source': True
        })
        
        report['total_documents'] = len(source_docs)
        
        # Initialize language stats
        for lang in self.supported_languages:
            report['languages'][lang] = {
                'total': 0,
                'completed': 0,
                'outdated': 0,
                'missing': 0
            }
        
        # Analyze each document
        for doc in source_docs:
            source_lang = doc.metadata.custom_metadata.get('language')
            doc_type = doc.metadata.custom_metadata.get('doc_type')
            
            if doc_type not in report['coverage_by_type']:
                report['coverage_by_type'][doc_type] = {
                    lang: {'total': 0, 'translated': 0} 
                    for lang in self.supported_languages
                }
            
            # Check translation status
            status = self.check_translation_status(doc.unique_id)
            
            for lang, trans_info in status['translations'].items():
                if trans_info['status'] == 'completed':
                    report['languages'][lang]['completed'] += 1
                    report['coverage_by_type'][doc_type][lang]['translated'] += 1
                    
                    if trans_info['is_outdated']:
                        report['languages'][lang]['outdated'] += 1
                        report['outdated_translations'].append({
                            'document_id': doc.unique_id,
                            'title': doc.metadata.title,
                            'language': lang
                        })
                else:
                    report['languages'][lang]['missing'] += 1
                    report['missing_translations'].append({
                        'document_id': doc.unique_id,
                        'title': doc.metadata.title,
                        'source_language': source_lang,
                        'target_language': lang
                    })
                
                report['coverage_by_type'][doc_type][lang]['total'] += 1
        
        # Calculate percentages
        for lang in report['languages']:
            if report['total_documents'] > 0:
                report['languages'][lang]['coverage_percent'] = (
                    report['languages'][lang]['completed'] / report['total_documents'] * 100
                )
        
        return report

# Example usage
if __name__ == "__main__":
    # Initialize system
    ml_docs = MultiLanguageDocumentation()
    
    # Create source document
    source_doc = ml_docs.create_source_document(
        title="Getting Started with ContextFrame",
        content="""# Getting Started with ContextFrame

ContextFrame is a powerful framework for managing document embeddings.

## Installation

Install ContextFrame using pip:

```bash
pip install contextframe
```

## Basic Usage

Here's how to create your first dataset:

```python
from contextframe import FrameDataset
dataset = FrameDataset.create("my_docs.lance")
```""",
        doc_type="guide",
        language="en",
        tags=["getting-started", "installation"]
    )
    
    # Translate to Spanish
    spanish_doc = ml_docs.translate_document(
        source_doc.unique_id,
        target_language="es"
    )
    
    # Check translation status
    status = ml_docs.check_translation_status(source_doc.unique_id)
    print(f"Translation status: {json.dumps(status, indent=2)}")
    
    # Cross-language search
    results = ml_docs.cross_language_search(
        "install ContextFrame",
        languages=["en", "es", "fr"]
    )
    
    print(f"\\nFound {len(results)} results across languages")
    for result in results[:3]:
        print(f"- {result['document'].metadata.title} ({result['language']})")
    
    # Generate translation report
    report = ml_docs.generate_translation_report()
    print(f"\\nTranslation Coverage Report:")
    print(f"Total documents: {report['total_documents']}")
    for lang, stats in report['languages'].items():
        if stats['total'] > 0:
            print(f"{lang}: {stats['coverage_percent']:.1f}% coverage")
```

## Key Concepts

### Translation Memory

The system maintains a translation memory to:
- Reuse previous translations for consistency
- Reduce translation costs
- Speed up translation process
- Maintain terminology consistency

### Glossary Management

Technical terms are managed through a glossary:
- Ensures consistent terminology across languages
- Preserves brand names and technical terms
- Customizable per organization
- Supports context-specific translations

### Change Tracking

Document changes are tracked to:
- Identify outdated translations
- Show what changed between versions
- Prioritize retranslation efforts
- Maintain translation history

## Extensions

### Advanced Features

1. **Machine Translation Integration**
   - Multiple translation engines
   - Quality scoring
   - Post-editing workflows
   - Translation review process

2. **Collaborative Translation**
   - Translator assignments
   - Review workflows
   - Comment system
   - Translation suggestions

3. **Localization Features**
   - Date/time formatting
   - Number formatting
   - Currency conversion
   - Cultural adaptations

4. **Quality Assurance**
   - Consistency checking
   - Terminology validation
   - Completeness verification
   - Style guide enforcement

### Integration Options

1. **CAT Tools**
   - TMX export/import
   - XLIFF support
   - TBX terminology exchange
   - API for CAT tools

2. **CMS Integration**
   - WordPress plugins
   - Drupal modules
   - Custom CMS adapters
   - Webhook notifications

3. **Version Control**
   - Git integration
   - Merge conflict resolution
   - Branch-based workflows
   - CI/CD pipelines

## Best Practices

1. **Content Structure**
   - Use consistent formatting
   - Minimize inline formatting
   - Use semantic markup
   - Avoid hardcoded values

2. **Translation Workflow**
   - Translate stable content first
   - Review critical content
   - Test in context
   - Gather user feedback

3. **Performance**
   - Cache translations
   - Batch translation jobs
   - Use translation memory
   - Optimize search indexes

4. **Quality Control**
   - Regular review cycles
   - Native speaker validation
   - Consistency checks
   - User feedback loops

This multi-language documentation system provides comprehensive translation management for global documentation needs.