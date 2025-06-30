# Document Processing Pipeline

Build a comprehensive document processing pipeline that handles various file formats, extracts structured information, enriches content, and prepares documents for search and analysis.

## Problem Statement

Organizations deal with documents in many formats (PDFs, Word docs, emails, images) that need to be processed, standardized, and made searchable. A robust pipeline must handle format conversion, text extraction, metadata enrichment, and quality validation.

## Solution Overview

We'll build a pipeline that:
1. Accepts documents in multiple formats
2. Extracts text and metadata
3. Cleans and normalizes content
4. Enriches with NLP analysis
5. Validates quality and completeness
6. Stores in ContextFrame for search

## Complete Code

```python
import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import magic
import pymupdf  # PyMuPDF for PDF processing
from PIL import Image
import pytesseract
from docx import Document as DocxDocument
import email
from email import policy
from email.parser import BytesParser
import spacy
from transformers import pipeline
from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    generate_uuid,
    ValidationError
)

class DocumentProcessor:
    """Comprehensive document processing pipeline."""
    
    def __init__(self, dataset_path: str = "processed_docs.lance"):
        """Initialize processor with NLP models."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Load NLP models
        self.nlp = spacy.load("en_core_web_sm")
        self.classifier = pipeline("zero-shot-classification")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # File type detector
        self.mime = magic.Magic(mime=True)
        
        # Processing stats
        self.stats = {
            "processed": 0,
            "failed": 0,
            "by_type": {}
        }
    
    def process_directory(self, directory_path: str, recursive: bool = True):
        """Process all documents in a directory."""
        path = Path(directory_path)
        
        if recursive:
            files = path.rglob("*")
        else:
            files = path.glob("*")
        
        for file_path in files:
            if file_path.is_file():
                try:
                    self.process_file(str(file_path))
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")
                    self.stats["failed"] += 1
    
    def process_file(self, file_path: str) -> Optional[FrameRecord]:
        """Process a single file."""
        print(f"Processing: {file_path}")
        
        # Detect file type
        mime_type = self.mime.from_file(file_path)
        
        # Extract content based on type
        if mime_type == "application/pdf":
            content, metadata = self._process_pdf(file_path)
        elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            content, metadata = self._process_word(file_path)
        elif mime_type.startswith("image/"):
            content, metadata = self._process_image(file_path)
        elif mime_type == "message/rfc822":
            content, metadata = self._process_email(file_path)
        elif mime_type.startswith("text/"):
            content, metadata = self._process_text(file_path)
        else:
            print(f"Unsupported file type: {mime_type}")
            return None
        
        # Clean and normalize content
        cleaned_content = self._clean_text(content)
        
        # Enrich with NLP
        enriched_metadata = self._enrich_content(cleaned_content, metadata)
        
        # Create record
        record = self._create_record(
            cleaned_content,
            enriched_metadata,
            file_path,
            mime_type
        )
        
        # Validate quality
        if self._validate_record(record):
            self.dataset.add(record, generate_embedding=True)
            self.stats["processed"] += 1
            self.stats["by_type"][mime_type] = self.stats["by_type"].get(mime_type, 0) + 1
            return record
        else:
            print(f"Record failed validation: {file_path}")
            self.stats["failed"] += 1
            return None
    
    def _process_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text and metadata from PDF."""
        doc = pymupdf.open(file_path)
        
        # Extract text
        text_parts = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            text_parts.append(f"[Page {page_num + 1}]\n{text}")
        
        content = "\n\n".join(text_parts)
        
        # Extract metadata
        metadata = {
            "page_count": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": str(doc.metadata.get("creationDate", "")),
            "modification_date": str(doc.metadata.get("modDate", ""))
        }
        
        # Extract images if any
        image_count = 0
        for page in doc:
            image_list = page.get_images()
            image_count += len(image_list)
        
        metadata["image_count"] = image_count
        
        doc.close()
        return content, metadata
    
    def _process_word(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text and metadata from Word documents."""
        doc = DocxDocument(file_path)
        
        # Extract text
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        
        content = "\n\n".join(paragraphs)
        
        # Extract metadata
        core_props = doc.core_properties
        metadata = {
            "title": core_props.title or "",
            "author": core_props.author or "",
            "subject": core_props.subject or "",
            "keywords": core_props.keywords or "",
            "created": str(core_props.created) if core_props.created else "",
            "modified": str(core_props.modified) if core_props.modified else "",
            "paragraph_count": len(paragraphs),
            "table_count": len(doc.tables)
        }
        
        # Extract tables
        if doc.tables:
            table_data = []
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text for cell in row.cells]
                    table_data.append(row_data)
            metadata["tables"] = table_data
        
        return content, metadata
    
    def _process_image(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text from images using OCR."""
        image = Image.open(file_path)
        
        # Extract text using OCR
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"OCR failed for {file_path}: {e}")
            text = ""
        
        # Image metadata
        metadata = {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
            "has_text": bool(text.strip())
        }
        
        # EXIF data for photos
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            metadata["exif"] = {k: v for k, v in exif.items() if isinstance(v, (str, int, float))}
        
        return text, metadata
    
    def _process_email(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract content from email files."""
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        
        # Extract text content
        body_parts = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body_parts.append(part.get_content())
        
        content = "\n\n".join(body_parts)
        
        # Extract metadata
        metadata = {
            "subject": msg.get("Subject", ""),
            "from": msg.get("From", ""),
            "to": msg.get("To", ""),
            "cc": msg.get("Cc", ""),
            "date": msg.get("Date", ""),
            "message_id": msg.get("Message-ID", ""),
            "has_attachments": any(part.get_content_disposition() == "attachment" for part in msg.walk())
        }
        
        # Extract attachments info
        attachments = []
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                attachments.append({
                    "filename": part.get_filename(),
                    "content_type": part.get_content_type(),
                    "size": len(part.get_content())
                })
        
        if attachments:
            metadata["attachments"] = attachments
        
        return content, metadata
    
    def _process_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process plain text files."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Basic metadata
        file_stat = os.stat(file_path)
        metadata = {
            "file_size": file_stat.st_size,
            "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "encoding": "utf-8"
        }
        
        return content, metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove excess whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\xff]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _enrich_content(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich content with NLP analysis."""
        enriched = metadata.copy()
        
        # Skip if content is too short
        if len(content) < 50:
            return enriched
        
        # Named Entity Recognition
        doc = self.nlp(content[:5000])  # Limit for performance
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        enriched["entities"] = entities
        
        # Key phrases extraction
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        enriched["key_phrases"] = list(set(noun_phrases))[:20]
        
        # Document classification
        if len(content) > 100:
            try:
                labels = ["technical", "business", "legal", "financial", "medical", "general"]
                classification = self.classifier(
                    content[:500],
                    candidate_labels=labels,
                    multi_label=True
                )
                enriched["categories"] = [
                    {"label": label, "score": score}
                    for label, score in zip(classification["labels"], classification["scores"])
                    if score > 0.3
                ]
            except Exception as e:
                print(f"Classification failed: {e}")
        
        # Generate summary for long documents
        if len(content) > 1000:
            try:
                summary = self.summarizer(
                    content[:1024],
                    max_length=150,
                    min_length=50,
                    do_sample=False
                )
                enriched["summary"] = summary[0]["summary_text"]
            except Exception as e:
                print(f"Summarization failed: {e}")
        
        # Language detection
        enriched["language"] = "en"  # Can use langdetect for multi-language
        
        # Statistics
        enriched["word_count"] = len(content.split())
        enriched["char_count"] = len(content)
        enriched["sentence_count"] = len(list(doc.sents))
        
        return enriched
    
    def _create_record(self, content: str, metadata: Dict[str, Any], 
                      file_path: str, mime_type: str) -> FrameRecord:
        """Create FrameRecord from processed content."""
        # Generate stable ID based on file content
        file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Core metadata
        record_metadata = create_metadata(
            title=metadata.get("title") or Path(file_path).name,
            source="file_system",
            file_path=file_path,
            mime_type=mime_type,
            file_hash=file_hash,
            processed_at=datetime.now().isoformat(),
            **{k: v for k, v in metadata.items() 
               if k not in ["title"] and not isinstance(v, (list, dict)) or k in ["entities", "categories"]}
        )
        
        # Create record
        record = FrameRecord(
            text_content=content,
            metadata=record_metadata,
            unique_id=f"doc_{file_hash}",
            context={
                "processing_version": "1.0",
                "nlp_enrichment": {
                    k: v for k, v in metadata.items()
                    if k in ["entities", "key_phrases", "categories", "summary"]
                }
            }
        )
        
        # Add raw file data for certain types
        if mime_type.startswith("image/") or mime_type == "application/pdf":
            with open(file_path, 'rb') as f:
                record.raw_data = f.read()
        
        return record
    
    def _validate_record(self, record: FrameRecord) -> bool:
        """Validate record quality."""
        # Must have content
        if not record.text_content or len(record.text_content.strip()) < 10:
            return False
        
        # Must have basic metadata
        required_fields = ["title", "source", "file_path"]
        for field in required_fields:
            if field not in record.metadata:
                return False
        
        # Check for spam/junk content
        if self._is_spam(record.text_content):
            return False
        
        return True
    
    def _is_spam(self, content: str) -> bool:
        """Simple spam detection."""
        spam_indicators = [
            r'\b(viagra|cialis|casino|lottery)\b',
            r'[A-Z]{5,}',  # Excessive caps
            r'(.)\1{5,}',  # Repeated characters
        ]
        
        for pattern in spam_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "total_processed": self.stats["processed"],
            "total_failed": self.stats["failed"],
            "success_rate": self.stats["processed"] / (self.stats["processed"] + self.stats["failed"]) if (self.stats["processed"] + self.stats["failed"]) > 0 else 0,
            "by_file_type": self.stats["by_type"],
            "dataset_size": len(self.dataset)
        }
    
    def export_metadata_report(self, output_path: str):
        """Export metadata analysis report."""
        import pandas as pd
        
        # Get all records
        records = list(self.dataset.iter_records(batch_size=1000))
        
        # Extract metadata
        data = []
        for record in records:
            data.append({
                "file_path": record.metadata.get("file_path"),
                "mime_type": record.metadata.get("mime_type"),
                "word_count": record.metadata.get("word_count", 0),
                "has_entities": bool(record.context.get("nlp_enrichment", {}).get("entities")),
                "categories": len(record.context.get("nlp_enrichment", {}).get("categories", [])),
                "has_summary": "summary" in record.context.get("nlp_enrichment", {})
            })
        
        # Create report
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        
        # Summary statistics
        print(f"Total documents: {len(df)}")
        print(f"Average word count: {df['word_count'].mean():.0f}")
        print(f"Documents with entities: {df['has_entities'].sum()}")
        print(f"Documents with summaries: {df['has_summary'].sum()}")

# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = DocumentProcessor("document_lake.lance")
    
    # Process a directory
    processor.process_directory("/path/to/documents", recursive=True)
    
    # Process specific file types
    for pdf_file in Path("/path/to/pdfs").glob("*.pdf"):
        processor.process_file(str(pdf_file))
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"Processing complete: {stats['total_processed']} files processed")
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"File types: {stats['by_file_type']}")
    
    # Export report
    processor.export_metadata_report("processing_report.csv")
    
    # Search processed documents
    dataset = processor.dataset
    
    # Find technical documents
    tech_docs = dataset.sql_filter(
        "json_extract(context, '$.nlp_enrichment.categories[0].label') = 'technical'",
        limit=10
    )
    
    # Search by entities
    company_docs = dataset.search(
        "Microsoft",
        filter="json_extract(context, '$.nlp_enrichment.entities.ORG') LIKE '%Microsoft%'"
    )
```

## Key Concepts

### 1. Multi-Format Support
- PDF text and metadata extraction
- Word document processing with tables
- OCR for images
- Email parsing with attachments
- Plain text handling

### 2. Content Cleaning
- Whitespace normalization
- Special character removal
- Quote standardization
- Spam detection

### 3. NLP Enrichment
- Named Entity Recognition (NER)
- Key phrase extraction
- Document classification
- Automatic summarization
- Language detection

### 4. Quality Validation
- Content length checks
- Required metadata validation
- Spam/junk detection
- Deduplication via hashing

### 5. Metadata Preservation
- Original file metadata
- Processing metadata
- Enrichment results
- File system information

## Extensions

### 1. Advanced OCR
```python
def _advanced_ocr(self, image_path: str) -> Dict[str, Any]:
    """Advanced OCR with layout analysis."""
    import layoutparser as lp
    
    # Load layout model
    model = lp.Detectron2LayoutModel(
        "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config"
    )
    
    # Detect layout
    image = cv2.imread(image_path)
    layout = model.detect(image)
    
    # Extract text by region
    regions = {}
    for block in layout:
        if block.type in ["Text", "Title", "Table"]:
            roi = image[block.y1:block.y2, block.x1:block.x2]
            text = pytesseract.image_to_string(roi)
            regions[block.type] = regions.get(block.type, [])
            regions[block.type].append(text)
    
    return regions
```

### 2. Table Extraction
```python
def _extract_tables(self, pdf_path: str) -> List[pd.DataFrame]:
    """Extract tables from PDFs."""
    import camelot
    
    tables = camelot.read_pdf(pdf_path, pages='all')
    
    dataframes = []
    for table in tables:
        df = table.df
        # Clean and process dataframe
        df = df.dropna(how='all')
        dataframes.append(df)
    
    return dataframes
```

### 3. Custom Extractors
```python
class InvoiceExtractor:
    """Extract structured data from invoices."""
    
    def extract(self, content: str) -> Dict[str, Any]:
        patterns = {
            "invoice_number": r"Invoice #?\s*(\w+)",
            "date": r"Date:\s*(\d{1,2}/\d{1,2}/\d{4})",
            "total": r"Total:\s*\$?([\d,]+\.?\d*)",
            "vendor": r"From:\s*(.+?)(?:\n|$)"
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1)
        
        return extracted
```

### 4. Parallel Processing
```python
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

def process_parallel(self, file_paths: List[str], max_workers: int = 4):
    """Process files in parallel."""
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(self.process_file, path): path 
            for path in file_paths
        }
        
        for future in tqdm(as_completed(futures), total=len(futures)):
            path = futures[future]
            try:
                result = future.result()
                if result:
                    print(f"✓ Processed: {path}")
            except Exception as e:
                print(f"✗ Failed: {path} - {e}")
```

### 5. Incremental Processing
```python
def process_incremental(self, directory: str):
    """Only process new or modified files."""
    # Load processing history
    history_file = "processing_history.json"
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = {}
    
    # Check each file
    for file_path in Path(directory).rglob("*"):
        if file_path.is_file():
            # Check if already processed
            file_stat = file_path.stat()
            file_key = str(file_path)
            
            if file_key in history:
                if history[file_key]["mtime"] == file_stat.st_mtime:
                    continue  # Skip unchanged files
            
            # Process file
            try:
                self.process_file(str(file_path))
                history[file_key] = {
                    "mtime": file_stat.st_mtime,
                    "processed": datetime.now().isoformat()
                }
            except Exception as e:
                print(f"Error: {e}")
    
    # Save history
    with open(history_file, 'w') as f:
        json.dump(history, f)
```

## Best Practices

1. **Error Handling**: Always handle format-specific errors gracefully
2. **Memory Management**: Process large files in chunks
3. **Metadata Standards**: Use consistent metadata schemas
4. **Validation Rules**: Define clear quality criteria
5. **Performance**: Use parallel processing for large batches
6. **Monitoring**: Track processing statistics and failures
7. **Versioning**: Version your processing pipeline

## See Also

- [RAG System](rag-system.md) - Using processed documents for RAG
- [Multi-Source Search](multi-source-search.md) - Searching processed content
- [Extraction Module](../modules/extraction.md) - Built-in extractors
- [API Reference](../api/overview.md) - Detailed API documentation