# Enrichment

Document enrichment in ContextFrame involves augmenting your documents with additional metadata, extracted entities, computed features, and enhanced content. This guide covers various enrichment techniques to make your documents more searchable and valuable.

## Overview

Enrichment capabilities include:
- Metadata extraction and computation
- Entity recognition and linking
- Content summarization
- Classification and tagging
- Language detection and translation
- Feature extraction
- Quality scoring

## Metadata Enrichment

### Computed Metadata

```python
from contextframe import FrameRecord
import re
from datetime import datetime

def enrich_basic_metadata(doc):
    """Add computed metadata to document."""
    content = doc.text_content
    
    # Text statistics
    stats = {
        'word_count': len(content.split()),
        'char_count': len(content),
        'line_count': len(content.splitlines()),
        'paragraph_count': len(content.split('\n\n')),
        'sentence_count': len(re.split(r'[.!?]+', content)),
        'avg_word_length': sum(len(word) for word in content.split()) / len(content.split()) if content else 0
    }
    
    # Reading metrics
    words_per_minute = 200
    stats['reading_time_minutes'] = round(stats['word_count'] / words_per_minute, 1)
    stats['reading_difficulty'] = calculate_reading_difficulty(content)
    
    # Content features
    features = {
        'has_code': '```' in content or 'def ' in content or 'function ' in content,
        'has_urls': bool(re.search(r'https?://\S+', content)),
        'has_emails': bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)),
        'has_questions': '?' in content,
        'has_lists': bool(re.search(r'^\s*[-*]\s+', content, re.MULTILINE)) or bool(re.search(r'^\s*\d+\.\s+', content, re.MULTILINE)),
        'has_headings': bool(re.search(r'^#+\s+', content, re.MULTILINE))
    }
    
    # Update metadata
    if 'custom_metadata' not in doc.metadata:
        doc.metadata['custom_metadata'] = {}
    
    doc.metadata['custom_metadata'].update({
        'statistics': stats,
        'content_features': features,
        'enrichment_date': datetime.now().isoformat()
    })
    
    return doc

def calculate_reading_difficulty(text):
    """Calculate reading difficulty score (simplified Flesch-Kincaid)."""
    sentences = re.split(r'[.!?]+', text)
    words = text.split()
    syllables = sum(count_syllables(word) for word in words)
    
    if len(sentences) == 0 or len(words) == 0:
        return 0
    
    # Flesch Reading Ease Score
    score = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))
    
    # Convert to difficulty level
    if score >= 90:
        return "very_easy"
    elif score >= 80:
        return "easy"
    elif score >= 70:
        return "fairly_easy"
    elif score >= 60:
        return "standard"
    elif score >= 50:
        return "fairly_difficult"
    elif score >= 30:
        return "difficult"
    else:
        return "very_difficult"

def count_syllables(word):
    """Simple syllable counter."""
    word = word.lower()
    count = 0
    vowels = 'aeiouy'
    
    if word[0] in vowels:
        count += 1
    
    for index in range(1, len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            count += 1
    
    if word.endswith('e'):
        count -= 1
    
    if word.endswith('le'):
        count += 1
    
    if count == 0:
        count += 1
    
    return count
```

### Domain-Specific Metadata

```python
def enrich_code_document(doc):
    """Enrich documents containing code."""
    content = doc.text_content
    metadata = {}
    
    # Detect programming languages
    languages = set()
    if 'def ' in content or 'import ' in content:
        languages.add('python')
    if 'function ' in content or 'const ' in content:
        languages.add('javascript')
    if '#include' in content or 'int main' in content:
        languages.add('c/c++')
    
    metadata['programming_languages'] = list(languages)
    
    # Count code blocks
    code_blocks = re.findall(r'```[\s\S]*?```', content)
    metadata['code_block_count'] = len(code_blocks)
    
    # Extract imports/dependencies
    python_imports = re.findall(r'^import\s+(\S+)', content, re.MULTILINE)
    python_imports.extend(re.findall(r'^from\s+(\S+)\s+import', content, re.MULTILINE))
    metadata['python_imports'] = list(set(python_imports))
    
    # Find function/class definitions
    functions = re.findall(r'def\s+(\w+)\s*\(', content)
    classes = re.findall(r'class\s+(\w+)\s*[:\(]', content)
    metadata['defined_functions'] = functions
    metadata['defined_classes'] = classes
    
    # Update document
    doc.metadata['custom_metadata'].update({
        'code_metadata': metadata
    })
    
    return doc

def enrich_scientific_document(doc):
    """Enrich scientific/research documents."""
    content = doc.text_content
    metadata = {}
    
    # Extract citations
    citations = re.findall(r'\([A-Za-z\s]+,\s*\d{4}\)', content)
    metadata['citation_count'] = len(citations)
    metadata['citations'] = list(set(citations))
    
    # Find DOIs
    dois = re.findall(r'10\.\d{4,}/[-._;()/:\w]+', content)
    metadata['dois'] = list(set(dois))
    
    # Extract figures and tables
    figures = re.findall(r'Figure\s+\d+', content, re.IGNORECASE)
    tables = re.findall(r'Table\s+\d+', content, re.IGNORECASE)
    metadata['figure_count'] = len(figures)
    metadata['table_count'] = len(tables)
    
    # Find equations (LaTeX)
    equations = re.findall(r'\$[^\$]+\$|\\\[[^\]]+\\\]', content)
    metadata['equation_count'] = len(equations)
    
    doc.metadata['custom_metadata'].update({
        'scientific_metadata': metadata
    })
    
    return doc
```

## Entity Extraction

### Named Entity Recognition

```python
import spacy

class EntityExtractor:
    """Extract named entities from documents."""
    
    def __init__(self, model="en_core_web_sm"):
        self.nlp = spacy.load(model)
    
    def extract_entities(self, doc):
        """Extract named entities from document."""
        text = doc.text_content
        
        # Process with spaCy
        spacy_doc = self.nlp(text)
        
        # Extract entities by type
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'money': [],
            'products': []
        }
        
        for ent in spacy_doc.ents:
            if ent.label_ == "PERSON":
                entities['persons'].append(ent.text)
            elif ent.label_ in ["ORG", "COMPANY"]:
                entities['organizations'].append(ent.text)
            elif ent.label_ in ["LOC", "GPE"]:
                entities['locations'].append(ent.text)
            elif ent.label_ == "DATE":
                entities['dates'].append(ent.text)
            elif ent.label_ == "MONEY":
                entities['money'].append(ent.text)
            elif ent.label_ == "PRODUCT":
                entities['products'].append(ent.text)
        
        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        # Update document
        doc.metadata['custom_metadata']['entities'] = entities
        
        # Add as tags
        all_entities = []
        for entity_type, entity_list in entities.items():
            for entity in entity_list[:5]:  # Limit tags
                all_entities.append(f"{entity_type}:{entity.lower().replace(' ', '_')}")
        
        if 'tags' not in doc.metadata:
            doc.metadata['tags'] = []
        doc.metadata['tags'].extend(all_entities)
        doc.metadata['tags'] = list(set(doc.metadata['tags']))
        
        return doc
```

### Custom Entity Extraction

```python
def extract_custom_entities(doc, patterns):
    """Extract custom entities using patterns."""
    content = doc.text_content
    entities = {}
    
    # Example patterns
    default_patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'url': r'https?://[^\s]+',
        'ipv4': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'hashtag': r'#\w+',
        'mention': r'@\w+',
        'ticket': r'[A-Z]+-\d+',  # JIRA style
        'version': r'v?\d+\.\d+(?:\.\d+)?'
    }
    
    patterns = {**default_patterns, **patterns}
    
    for entity_type, pattern in patterns.items():
        matches = re.findall(pattern, content)
        if matches:
            entities[entity_type] = list(set(matches))
    
    # Update document
    if 'custom_entities' not in doc.metadata.get('custom_metadata', {}):
        doc.metadata['custom_metadata']['custom_entities'] = {}
    
    doc.metadata['custom_metadata']['custom_entities'].update(entities)
    
    return doc
```

## Content Enhancement

### Summarization

```python
def add_summary(doc, max_length=200):
    """Add AI-generated summary to document."""
    from transformers import pipeline
    
    # Initialize summarizer
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Prepare text
    text = doc.text_content
    
    # Handle long documents
    if len(text.split()) > 1024:
        # Take first and last parts
        words = text.split()
        text = ' '.join(words[:512] + ['...'] + words[-512:])
    
    # Generate summary
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    
    # Add to metadata
    doc.metadata['summary'] = summary[0]['summary_text']
    
    # Also add to custom metadata with more details
    doc.metadata['custom_metadata']['summarization'] = {
        'summary': summary[0]['summary_text'],
        'method': 'bart-large-cnn',
        'max_length': max_length,
        'generated_at': datetime.now().isoformat()
    }
    
    return doc

def extract_key_sentences(doc, num_sentences=5):
    """Extract key sentences using TextRank."""
    from summa import summarize
    
    # Extract key sentences
    key_sentences = summarize(
        doc.text_content,
        ratio=0.1,  # Extract 10% of sentences
        split=True  # Return as list
    )[:num_sentences]
    
    doc.metadata['custom_metadata']['key_sentences'] = key_sentences
    
    return doc
```

### Keyword Extraction

```python
def extract_keywords(doc, num_keywords=10):
    """Extract keywords using multiple methods."""
    from rake_nltk import Rake
    from summa import keywords
    
    text = doc.text_content
    
    # Method 1: RAKE
    rake = Rake()
    rake.extract_keywords_from_text(text)
    rake_keywords = rake.get_ranked_phrases()[:num_keywords]
    
    # Method 2: TextRank
    textrank_keywords = keywords(text, words=num_keywords, split=True)
    
    # Method 3: TF-IDF (simple version)
    words = text.lower().split()
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Skip short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    tfidf_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    tfidf_keywords = [word for word, freq in tfidf_keywords[:num_keywords]]
    
    # Combine and deduplicate
    all_keywords = list(set(rake_keywords + textrank_keywords + tfidf_keywords))
    
    # Update document
    doc.metadata['custom_metadata']['keywords'] = {
        'rake': rake_keywords,
        'textrank': textrank_keywords,
        'tfidf': tfidf_keywords,
        'combined': all_keywords[:num_keywords]
    }
    
    # Add top keywords as tags
    if 'tags' not in doc.metadata:
        doc.metadata['tags'] = []
    
    for keyword in all_keywords[:5]:
        doc.metadata['tags'].append(f"keyword:{keyword.lower().replace(' ', '_')}")
    
    doc.metadata['tags'] = list(set(doc.metadata['tags']))
    
    return doc
```

## Classification

### Topic Classification

```python
def classify_topic(doc, categories):
    """Classify document into predefined categories."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Define category keywords
    category_keywords = {
        'technology': ['software', 'computer', 'programming', 'algorithm', 'data', 'system'],
        'business': ['company', 'market', 'revenue', 'customer', 'strategy', 'profit'],
        'science': ['research', 'study', 'experiment', 'hypothesis', 'analysis', 'theory'],
        'health': ['medical', 'patient', 'treatment', 'disease', 'health', 'doctor'],
        'education': ['student', 'learning', 'teaching', 'school', 'course', 'education']
    }
    
    # Vectorize document and categories
    vectorizer = TfidfVectorizer()
    
    # Combine document with category descriptions
    texts = [doc.text_content]
    for cat, keywords in category_keywords.items():
        texts.append(' '.join(keywords))
    
    # Calculate similarities
    tfidf_matrix = vectorizer.fit_transform(texts)
    doc_vector = tfidf_matrix[0]
    
    similarities = {}
    for i, category in enumerate(category_keywords.keys(), 1):
        similarity = cosine_similarity(doc_vector, tfidf_matrix[i])[0][0]
        similarities[category] = float(similarity)
    
    # Get top categories
    sorted_categories = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    primary_category = sorted_categories[0][0]
    
    # Update document
    doc.metadata['custom_metadata']['classification'] = {
        'primary_category': primary_category,
        'category_scores': similarities,
        'confidence': sorted_categories[0][1]
    }
    
    # Add as tag
    if 'tags' not in doc.metadata:
        doc.metadata['tags'] = []
    doc.metadata['tags'].append(f"category:{primary_category}")
    doc.metadata['tags'] = list(set(doc.metadata['tags']))
    
    return doc

def classify_sentiment(doc):
    """Classify document sentiment."""
    from transformers import pipeline
    
    # Initialize sentiment analyzer
    sentiment_analyzer = pipeline("sentiment-analysis")
    
    # Analyze sentiment (handle long texts)
    text = doc.text_content[:512]  # Truncate for model
    result = sentiment_analyzer(text)[0]
    
    # Update document
    doc.metadata['custom_metadata']['sentiment'] = {
        'label': result['label'].lower(),
        'score': float(result['score']),
        'analyzed_at': datetime.now().isoformat()
    }
    
    return doc
```

## Language Processing

### Language Detection

```python
from langdetect import detect, detect_langs

def detect_language(doc):
    """Detect document language."""
    try:
        # Simple detection
        language = detect(doc.text_content)
        
        # Detailed detection with probabilities
        lang_probs = detect_langs(doc.text_content)
        
        # Update document
        doc.metadata['language'] = language
        doc.metadata['custom_metadata']['language_detection'] = {
            'primary_language': language,
            'language_probabilities': [
                {'language': lang.lang, 'probability': float(lang.prob)}
                for lang in lang_probs
            ]
        }
        
        # Add as tag
        if 'tags' not in doc.metadata:
            doc.metadata['tags'] = []
        doc.metadata['tags'].append(f"lang:{language}")
        doc.metadata['tags'] = list(set(doc.metadata['tags']))
        
    except Exception as e:
        doc.metadata['custom_metadata']['language_detection'] = {
            'error': str(e)
        }
    
    return doc
```

### Translation

```python
def add_translation(doc, target_language='en'):
    """Add translation to document."""
    from googletrans import Translator
    
    translator = Translator()
    
    # Detect source language if not specified
    if 'language' not in doc.metadata:
        doc = detect_language(doc)
    
    source_lang = doc.metadata.get('language', 'auto')
    
    # Skip if already in target language
    if source_lang == target_language:
        return doc
    
    try:
        # Translate (handle long texts by chunking)
        text = doc.text_content
        if len(text) > 5000:
            # Translate in chunks
            chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
            translations = []
            for chunk in chunks:
                result = translator.translate(chunk, src=source_lang, dest=target_language)
                translations.append(result.text)
            translated_text = ' '.join(translations)
        else:
            result = translator.translate(text, src=source_lang, dest=target_language)
            translated_text = result.text
        
        # Store translation
        doc.metadata['custom_metadata']['translations'] = {
            target_language: {
                'text': translated_text,
                'source_language': source_lang,
                'translated_at': datetime.now().isoformat()
            }
        }
        
        # Optionally create a new document for the translation
        translated_doc = FrameRecord.create(
            title=f"{doc.metadata['title']} ({target_language})",
            content=translated_text,
            language=target_language,
            custom_metadata={
                'is_translation': True,
                'source_document': doc.uuid,
                'source_language': source_lang
            }
        )
        
        # Link documents
        translated_doc.add_relationship(
            doc.uuid,
            "reference",
            title="Original document",
            description=f"Translated from {source_lang}"
        )
        
        return doc, translated_doc
        
    except Exception as e:
        doc.metadata['custom_metadata']['translation_error'] = str(e)
        return doc, None
```

## Quality Scoring

### Content Quality

```python
def calculate_quality_score(doc):
    """Calculate document quality score."""
    score = 100  # Start with perfect score
    details = {}
    
    # Length checks
    word_count = len(doc.text_content.split())
    if word_count < 100:
        score -= 20
        details['too_short'] = True
    elif word_count > 10000:
        score -= 10
        details['very_long'] = True
    
    # Metadata completeness
    metadata_fields = ['title', 'author', 'tags', 'summary']
    missing_fields = []
    for field in metadata_fields:
        if not doc.metadata.get(field):
            score -= 5
            missing_fields.append(field)
    if missing_fields:
        details['missing_metadata'] = missing_fields
    
    # Content checks
    content = doc.text_content
    
    # Check for lorem ipsum
    if 'lorem ipsum' in content.lower():
        score -= 30
        details['placeholder_content'] = True
    
    # Check for repeated content
    lines = content.splitlines()
    unique_lines = set(lines)
    if len(lines) > 10 and len(unique_lines) < len(lines) * 0.8:
        score -= 15
        details['repetitive_content'] = True
    
    # Check structure
    if not re.search(r'^#+\s+', content, re.MULTILINE):
        score -= 5
        details['no_headings'] = True
    
    # Check for code blocks without language
    untagged_code = re.findall(r'```\n[^`]+```', content)
    if untagged_code:
        score -= 5
        details['untagged_code_blocks'] = len(untagged_code)
    
    # Ensure score doesn't go below 0
    score = max(0, score)
    
    # Update document
    doc.metadata['custom_metadata']['quality_score'] = {
        'score': score,
        'details': details,
        'assessed_at': datetime.now().isoformat()
    }
    
    # Add quality tag
    if score >= 80:
        quality = 'high_quality'
    elif score >= 60:
        quality = 'medium_quality'
    else:
        quality = 'low_quality'
    
    if 'tags' not in doc.metadata:
        doc.metadata['tags'] = []
    doc.metadata['tags'].append(f"quality:{quality}")
    doc.metadata['tags'] = list(set(doc.metadata['tags']))
    
    return doc
```

## Batch Enrichment

### Pipeline Processing

```python
class EnrichmentPipeline:
    """Pipeline for document enrichment."""
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, func, name=None, **kwargs):
        """Add enrichment step to pipeline."""
        self.steps.append({
            'function': func,
            'name': name or func.__name__,
            'kwargs': kwargs
        })
        return self
    
    def process(self, doc):
        """Process document through pipeline."""
        for step in self.steps:
            try:
                if step['kwargs']:
                    doc = step['function'](doc, **step['kwargs'])
                else:
                    doc = step['function'](doc)
            except Exception as e:
                print(f"Error in {step['name']}: {e}")
                # Continue with next step
        
        # Mark as enriched
        doc.metadata['custom_metadata']['enrichment_pipeline'] = {
            'steps': [s['name'] for s in self.steps],
            'completed_at': datetime.now().isoformat()
        }
        
        return doc
    
    def process_batch(self, docs, parallel=False):
        """Process multiple documents."""
        if parallel:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as executor:
                return list(executor.map(self.process, docs))
        else:
            return [self.process(doc) for doc in docs]

# Example pipeline
def create_standard_pipeline():
    """Create standard enrichment pipeline."""
    pipeline = EnrichmentPipeline()
    
    pipeline.add_step(enrich_basic_metadata)
    pipeline.add_step(detect_language)
    pipeline.add_step(extract_keywords, num_keywords=15)
    pipeline.add_step(classify_topic, categories=['technology', 'business', 'science'])
    pipeline.add_step(calculate_quality_score)
    
    return pipeline
```

### Dataset Enrichment

```python
def enrich_dataset(dataset, pipeline, batch_size=100):
    """Enrich all documents in dataset."""
    from tqdm import tqdm
    
    total = len(dataset)
    enriched = 0
    
    for batch in tqdm(dataset.to_batches(batch_size=batch_size)):
        # Convert to FrameRecords
        docs = [FrameRecord.from_arrow(row) for row in batch.to_pylist()]
        
        # Process through pipeline
        enriched_docs = pipeline.process_batch(docs, parallel=True)
        
        # Update in dataset
        for doc in enriched_docs:
            dataset.update_record(doc.uuid, doc)
        
        enriched += len(docs)
    
    print(f"Enriched {enriched} documents")
```

## Best Practices

### 1. Incremental Enrichment

```python
def should_enrich(doc, force=False):
    """Check if document needs enrichment."""
    if force:
        return True
    
    # Check if already enriched
    enrichment_date = doc.metadata.get('custom_metadata', {}).get('enrichment_date')
    if not enrichment_date:
        return True
    
    # Check if content changed since enrichment
    updated_at = doc.metadata.get('updated_at')
    if updated_at > enrichment_date:
        return True
    
    # Check age of enrichment
    from datetime import datetime, timedelta
    enriched = datetime.fromisoformat(enrichment_date)
    if datetime.now() - enriched > timedelta(days=30):
        return True
    
    return False

def selective_enrichment(dataset, pipeline):
    """Only enrich documents that need it."""
    to_enrich = []
    
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            doc = FrameRecord.from_arrow(row)
            if should_enrich(doc):
                to_enrich.append(doc)
    
    print(f"Found {len(to_enrich)} documents needing enrichment")
    
    if to_enrich:
        enriched = pipeline.process_batch(to_enrich, parallel=True)
        for doc in enriched:
            dataset.update_record(doc.uuid, doc)
```

### 2. Error Handling

```python
def safe_enrichment(func):
    """Decorator for safe enrichment functions."""
    def wrapper(doc, *args, **kwargs):
        try:
            return func(doc, *args, **kwargs)
        except Exception as e:
            # Log error in metadata
            if 'enrichment_errors' not in doc.metadata.get('custom_metadata', {}):
                doc.metadata['custom_metadata']['enrichment_errors'] = []
            
            doc.metadata['custom_metadata']['enrichment_errors'].append({
                'function': func.__name__,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            return doc
    return wrapper

@safe_enrichment
def risky_enrichment(doc):
    """Example of protected enrichment function."""
    # Potentially failing operation
    result = external_api_call(doc.text_content)
    doc.metadata['custom_metadata']['api_result'] = result
    return doc
```

### 3. Performance Optimization

```python
import functools
import pickle
from pathlib import Path

class EnrichmentCache:
    """Cache enrichment results."""
    
    def __init__(self, cache_dir="./enrichment_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def cache_key(self, doc, func_name):
        """Generate cache key."""
        import hashlib
        content = f"{func_name}:{doc.text_content}:{doc.metadata}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, doc, func_name):
        """Get cached result."""
        key = self.cache_key(doc, func_name)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, doc, func_name, result):
        """Cache result."""
        key = self.cache_key(doc, func_name)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

def cached_enrichment(cache):
    """Decorator for cached enrichment."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(doc, *args, **kwargs):
            # Check cache
            cached = cache.get(doc, func.__name__)
            if cached is not None:
                return cached
            
            # Compute and cache
            result = func(doc, *args, **kwargs)
            cache.set(doc, func.__name__, result)
            
            return result
        return wrapper
    return decorator

# Usage
cache = EnrichmentCache()

@cached_enrichment(cache)
def expensive_enrichment(doc):
    """Expensive enrichment operation."""
    # Complex processing...
    return doc
```

## Monitoring and Validation

### Enrichment Status

```python
def get_enrichment_status(dataset):
    """Get enrichment status for dataset."""
    status = {
        'total_documents': 0,
        'enriched_documents': 0,
        'enrichment_steps': {},
        'errors': 0,
        'quality_distribution': {
            'high': 0,
            'medium': 0,
            'low': 0
        }
    }
    
    for batch in dataset.to_batches():
        for row in batch.to_pylist():
            status['total_documents'] += 1
            
            custom = row.get('custom_metadata', {})
            
            # Check if enriched
            if 'enrichment_date' in custom:
                status['enriched_documents'] += 1
            
            # Check enrichment steps
            if 'enrichment_pipeline' in custom:
                for step in custom['enrichment_pipeline'].get('steps', []):
                    status['enrichment_steps'][step] = status['enrichment_steps'].get(step, 0) + 1
            
            # Check errors
            if 'enrichment_errors' in custom:
                status['errors'] += len(custom['enrichment_errors'])
            
            # Check quality
            if 'quality_score' in custom:
                score = custom['quality_score']['score']
                if score >= 80:
                    status['quality_distribution']['high'] += 1
                elif score >= 60:
                    status['quality_distribution']['medium'] += 1
                else:
                    status['quality_distribution']['low'] += 1
    
    status['enrichment_percentage'] = (
        status['enriched_documents'] / status['total_documents'] * 100
        if status['total_documents'] > 0 else 0
    )
    
    return status
```

### Validation

```python
def validate_enrichment(doc):
    """Validate enrichment results."""
    issues = []
    
    custom = doc.metadata.get('custom_metadata', {})
    
    # Check for required enrichments
    required = ['statistics', 'keywords', 'language_detection']
    for field in required:
        if field not in custom:
            issues.append(f"Missing required enrichment: {field}")
    
    # Validate statistics
    if 'statistics' in custom:
        stats = custom['statistics']
        if stats.get('word_count', 0) == 0 and doc.text_content:
            issues.append("Invalid word count")
    
    # Validate keywords
    if 'keywords' in custom:
        keywords = custom['keywords'].get('combined', [])
        if len(keywords) == 0 and len(doc.text_content) > 100:
            issues.append("No keywords extracted from substantial content")
    
    # Check for enrichment errors
    if 'enrichment_errors' in custom:
        issues.append(f"Enrichment errors: {len(custom['enrichment_errors'])}")
    
    return len(issues) == 0, issues
```

## Next Steps

- Learn about [Search & Query](search-query.md) using enriched metadata
- Explore [Import/Export](import-export.md) with enrichment
- See [Cookbook Examples](../cookbook/document-enrichment.md)
- Check the [API Reference](../api/enrichment.md)