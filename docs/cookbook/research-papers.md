# Research Paper Collection

Build a comprehensive research paper management system that organizes academic papers, extracts citations, tracks references, and enables advanced literature review workflows.

## Problem Statement

Researchers need to manage large collections of academic papers, track citations, identify research trends, and maintain organized literature reviews. A dedicated system can automate paper organization, citation extraction, and provide intelligent search across research collections.

## Solution Overview

We'll build a research paper system that:
1. Imports papers from multiple sources (arXiv, PDFs, BibTeX)
2. Extracts metadata and citations automatically
3. Builds citation networks and identifies key papers
4. Enables semantic search across papers
5. Generates literature review summaries

## Complete Code

```python
import os
import re
import json
import bibtexparser
import arxiv
import requests
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
import networkx as nx
import numpy as np
from collections import defaultdict, Counter
import fitz  # PyMuPDF

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class ResearchPaperCollection:
    """Comprehensive research paper management system."""
    
    def __init__(self, dataset_path: str = "research_papers.lance"):
        """Initialize paper collection."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        self.citation_graph = nx.DiGraph()
        self.author_graph = nx.Graph()
        
    def import_arxiv_paper(self, arxiv_id: str) -> Optional[FrameRecord]:
        """Import paper from arXiv."""
        print(f"Importing arXiv paper: {arxiv_id}")
        
        try:
            # Search for paper
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(search.results())
            
            # Download PDF
            pdf_path = f"papers/{arxiv_id.replace('/', '_')}.pdf"
            os.makedirs("papers", exist_ok=True)
            paper.download_pdf(dirpath="papers", filename=f"{arxiv_id.replace('/', '_')}.pdf")
            
            # Extract text from PDF
            text_content = self._extract_pdf_text(pdf_path)
            
            # Extract citations from text
            citations = self._extract_citations(text_content)
            
            # Create record
            record = self._create_paper_record(
                title=paper.title,
                authors=[author.name for author in paper.authors],
                abstract=paper.summary,
                content=text_content,
                arxiv_id=arxiv_id,
                published=paper.published,
                categories=paper.categories,
                pdf_url=paper.pdf_url,
                citations=citations,
                pdf_path=pdf_path
            )
            
            self.dataset.add(record, generate_embedding=True)
            
            # Update graphs
            self._update_citation_graph(record)
            self._update_author_graph(record)
            
            return record
            
        except Exception as e:
            print(f"Error importing arXiv paper {arxiv_id}: {e}")
            return None
    
    def import_pdf(self, pdf_path: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[FrameRecord]:
        """Import paper from PDF file."""
        print(f"Importing PDF: {pdf_path}")
        
        try:
            # Extract text
            text_content = self._extract_pdf_text(pdf_path)
            
            # Extract metadata from PDF
            pdf_metadata = self._extract_pdf_metadata(pdf_path)
            
            # Try to extract paper details from text
            paper_info = self._extract_paper_info(text_content)
            
            # Merge metadata
            if metadata:
                paper_info.update(metadata)
            paper_info.update(pdf_metadata)
            
            # Extract citations
            citations = self._extract_citations(text_content)
            
            # Create record
            record = self._create_paper_record(
                title=paper_info.get('title', Path(pdf_path).stem),
                authors=paper_info.get('authors', []),
                abstract=paper_info.get('abstract', ''),
                content=text_content,
                published=paper_info.get('published'),
                citations=citations,
                pdf_path=pdf_path,
                **paper_info
            )
            
            self.dataset.add(record, generate_embedding=True)
            
            # Update graphs
            self._update_citation_graph(record)
            self._update_author_graph(record)
            
            return record
            
        except Exception as e:
            print(f"Error importing PDF {pdf_path}: {e}")
            return None
    
    def import_bibtex(self, bibtex_file: str) -> List[FrameRecord]:
        """Import papers from BibTeX file."""
        print(f"Importing BibTeX: {bibtex_file}")
        
        with open(bibtex_file, 'r') as f:
            bib_database = bibtexparser.load(f)
        
        records = []
        for entry in bib_database.entries:
            record = self._create_paper_record_from_bibtex(entry)
            if record:
                self.dataset.add(record, generate_embedding=True)
                records.append(record)
        
        print(f"Imported {len(records)} papers from BibTeX")
        return records
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text content from PDF."""
        doc = fitz.open(pdf_path)
        text_parts = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            text_parts.append(f"[Page {page_num + 1}]\n{text}")
        
        doc.close()
        return "\n\n".join(text_parts)
    
    def _extract_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        
        return {
            'pdf_title': metadata.get('title', ''),
            'pdf_author': metadata.get('author', ''),
            'pdf_subject': metadata.get('subject', ''),
            'pdf_keywords': metadata.get('keywords', ''),
            'pdf_creator': metadata.get('creator', ''),
            'pdf_producer': metadata.get('producer', ''),
            'pdf_creation_date': str(metadata.get('creationDate', ''))
        }
    
    def _extract_paper_info(self, text: str) -> Dict[str, Any]:
        """Extract paper information from text using patterns."""
        info = {}
        
        # Extract title (usually in first few lines)
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):
            if len(line) > 10 and len(line) < 200 and not line.isupper():
                if not any(skip in line.lower() for skip in ['abstract', 'introduction', 'keywords']):
                    info['title'] = line.strip()
                    break
        
        # Extract abstract
        abstract_match = re.search(
            r'(?:Abstract|ABSTRACT)[:\s]*\n?(.*?)(?:\n\n|\n(?:Introduction|INTRODUCTION|Keywords|1\.|I\.))',
            text,
            re.DOTALL | re.IGNORECASE
        )
        if abstract_match:
            info['abstract'] = abstract_match.group(1).strip()
        
        # Extract authors (common patterns)
        author_patterns = [
            r'^([A-Z][a-z]+(?: [A-Z][a-z]+)+(?:,? (?:and |, )?[A-Z][a-z]+(?: [A-Z][a-z]+)+)*)',
            r'(?:Authors?|by)[:\s]+(.+?)(?:\n|$)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text[:1000], re.MULTILINE)
            if match:
                authors_text = match.group(1)
                # Split by common delimiters
                authors = re.split(r',|\band\b', authors_text)
                info['authors'] = [a.strip() for a in authors if a.strip()]
                break
        
        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', text[:500])
        if year_match:
            info['year'] = int(year_match.group(0))
        
        return info
    
    def _extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """Extract citations from paper text."""
        citations = []
        
        # Pattern for [Author, Year] style citations
        pattern1 = re.findall(r'\[([A-Za-z\s]+(?:,\s*[A-Za-z\s]+)*),?\s*(\d{4})\]', text)
        for authors, year in pattern1:
            citations.append({
                'authors': authors,
                'year': year,
                'style': 'bracket'
            })
        
        # Pattern for (Author, Year) style citations  
        pattern2 = re.findall(r'\(([A-Z][a-z]+(?:\s+(?:and|&)\s+[A-Z][a-z]+)?),?\s*(\d{4})\)', text)
        for authors, year in pattern2:
            citations.append({
                'authors': authors,
                'year': year,
                'style': 'parenthesis'
            })
        
        # Pattern for numbered citations [1], [2,3], etc.
        pattern3 = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', text)
        for nums in pattern3:
            for num in nums.split(','):
                citations.append({
                    'number': int(num.strip()),
                    'style': 'numbered'
                })
        
        # Extract references section
        references = self._extract_references_section(text)
        
        return {
            'inline_citations': citations,
            'references': references,
            'citation_count': len(set(str(c) for c in citations))
        }
    
    def _extract_references_section(self, text: str) -> List[str]:
        """Extract references/bibliography section."""
        references = []
        
        # Find references section
        ref_match = re.search(
            r'(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY)[:\s]*\n(.*?)(?:\n\n[A-Z]|\Z)',
            text,
            re.DOTALL | re.IGNORECASE
        )
        
        if ref_match:
            ref_text = ref_match.group(1)
            
            # Split into individual references
            # Pattern for numbered references
            numbered_refs = re.split(r'\n\[\d+\]', ref_text)
            if len(numbered_refs) > 1:
                references = [ref.strip() for ref in numbered_refs if ref.strip()]
            else:
                # Pattern for new line references
                lines = ref_text.split('\n')
                current_ref = []
                
                for line in lines:
                    if line and not line[0].isspace() and current_ref:
                        # New reference
                        references.append(' '.join(current_ref))
                        current_ref = [line]
                    elif line:
                        current_ref.append(line.strip())
                
                if current_ref:
                    references.append(' '.join(current_ref))
        
        return references
    
    def _create_paper_record(self, title: str, authors: List[str], 
                           abstract: str, content: str,
                           citations: Dict[str, Any],
                           **kwargs) -> FrameRecord:
        """Create FrameRecord for research paper."""
        # Generate unique ID
        unique_id = generate_uuid(namespace="research_paper", name=title)
        
        # Build metadata
        metadata = create_metadata(
            title=title,
            source="research_paper",
            authors=authors,
            abstract=abstract,
            citation_count=citations.get('citation_count', 0),
            references_count=len(citations.get('references', [])),
            **{k: v for k, v in kwargs.items() 
               if k not in ['content', 'citations'] and v is not None}
        )
        
        # Add citation relationships
        for ref in citations.get('references', []):
            # Try to identify cited papers
            # This is simplified - in practice you'd use more sophisticated matching
            if ref:
                metadata = add_relationship_to_metadata(
                    metadata,
                    relationship_type="cites",
                    target_id=generate_uuid(namespace="citation", name=ref[:100]),
                    metadata={"reference_text": ref}
                )
        
        return FrameRecord(
            text_content=f"{title}\n\nAuthors: {', '.join(authors)}\n\nAbstract:\n{abstract}\n\n{content}",
            metadata=metadata,
            unique_id=unique_id,
            record_type="document",
            context={
                "citations": citations,
                "paper_type": "research_paper"
            }
        )
    
    def _create_paper_record_from_bibtex(self, entry: Dict[str, Any]) -> Optional[FrameRecord]:
        """Create paper record from BibTeX entry."""
        # Extract required fields
        title = entry.get('title', '').strip('{}')
        authors = entry.get('author', '').split(' and ')
        
        if not title:
            return None
        
        # Build abstract from BibTeX
        abstract = entry.get('abstract', '')
        if not abstract:
            # Build from available fields
            parts = []
            if entry.get('journal'):
                parts.append(f"Published in: {entry['journal']}")
            if entry.get('year'):
                parts.append(f"Year: {entry['year']}")
            if entry.get('keywords'):
                parts.append(f"Keywords: {entry['keywords']}")
            abstract = '. '.join(parts)
        
        return self._create_paper_record(
            title=title,
            authors=[a.strip() for a in authors],
            abstract=abstract,
            content=abstract,  # Limited content from BibTeX
            citations={'citation_count': 0, 'references': []},
            bibtex_key=entry.get('ID'),
            journal=entry.get('journal'),
            year=entry.get('year'),
            volume=entry.get('volume'),
            pages=entry.get('pages'),
            doi=entry.get('doi'),
            url=entry.get('url')
        )
    
    def _update_citation_graph(self, record: FrameRecord):
        """Update citation network graph."""
        # Add paper node
        self.citation_graph.add_node(
            record.unique_id,
            title=record.metadata['title'],
            authors=record.metadata.get('authors', []),
            year=record.metadata.get('year')
        )
        
        # Add citation edges
        for rel in record.metadata.get('relationships', []):
            if rel['relationship_type'] == 'cites':
                self.citation_graph.add_edge(
                    record.unique_id,
                    rel['target_id']
                )
    
    def _update_author_graph(self, record: FrameRecord):
        """Update author collaboration graph."""
        authors = record.metadata.get('authors', [])
        
        # Add author nodes
        for author in authors:
            if not self.author_graph.has_node(author):
                self.author_graph.add_node(author, papers=0)
            self.author_graph.nodes[author]['papers'] += 1
        
        # Add collaboration edges
        for i, author1 in enumerate(authors):
            for author2 in authors[i+1:]:
                if self.author_graph.has_edge(author1, author2):
                    self.author_graph[author1][author2]['weight'] += 1
                else:
                    self.author_graph.add_edge(author1, author2, weight=1)
    
    def search_papers(self, query: str, filters: Optional[Dict[str, Any]] = None,
                     limit: int = 20) -> List[Dict[str, Any]]:
        """Search papers with optional filters."""
        # Build filter string
        filter_conditions = []
        if filters:
            if 'author' in filters:
                filter_conditions.append(f"array_contains(metadata.authors, '{filters['author']}')")
            if 'year_from' in filters:
                filter_conditions.append(f"metadata.year >= {filters['year_from']}")
            if 'year_to' in filters:
                filter_conditions.append(f"metadata.year <= {filters['year_to']}")
            if 'min_citations' in filters:
                filter_conditions.append(f"metadata.citation_count >= {filters['min_citations']}")
        
        filter_str = " AND ".join(filter_conditions) if filter_conditions else None
        
        # Search
        results = self.dataset.search(query, filter=filter_str, limit=limit)
        
        # Format results
        formatted = []
        for result in results:
            formatted.append({
                'title': result.metadata['title'],
                'authors': result.metadata.get('authors', []),
                'year': result.metadata.get('year'),
                'abstract': result.metadata.get('abstract', '')[:200] + '...',
                'score': result.score,
                'unique_id': result.unique_id,
                'citations': result.metadata.get('citation_count', 0)
            })
        
        return formatted
    
    def find_similar_papers(self, paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find papers similar to a given paper."""
        # Get the paper
        paper = self.dataset.get(paper_id)
        if not paper:
            return []
        
        # Find similar using vector search
        similar = self.dataset.find_similar(paper_id, k=limit + 1)
        
        # Format results (exclude the query paper)
        formatted = []
        for result in similar[1:]:
            formatted.append({
                'title': result.metadata['title'],
                'authors': result.metadata.get('authors', []),
                'year': result.metadata.get('year'),
                'similarity': result.score,
                'abstract': result.metadata.get('abstract', '')[:200] + '...'
            })
        
        return formatted
    
    def get_citation_network(self, paper_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get citation network around a paper."""
        if paper_id not in self.citation_graph:
            return {'nodes': [], 'edges': []}
        
        # Get subgraph
        nodes = set([paper_id])
        
        # Forward citations (papers that cite this one)
        for _ in range(depth):
            new_nodes = set()
            for node in nodes:
                new_nodes.update(self.citation_graph.predecessors(node))
                new_nodes.update(self.citation_graph.successors(node))
            nodes.update(new_nodes)
        
        # Build subgraph
        subgraph = self.citation_graph.subgraph(nodes)
        
        # Format for visualization
        nodes_data = []
        for node in subgraph.nodes():
            paper = self.dataset.get(node)
            if paper:
                nodes_data.append({
                    'id': node,
                    'title': paper.metadata['title'],
                    'authors': paper.metadata.get('authors', []),
                    'year': paper.metadata.get('year'),
                    'citations': paper.metadata.get('citation_count', 0)
                })
        
        edges_data = []
        for source, target in subgraph.edges():
            edges_data.append({
                'source': source,
                'target': target
            })
        
        return {
            'nodes': nodes_data,
            'edges': edges_data,
            'center': paper_id
        }
    
    def identify_key_papers(self, min_citations: int = 10) -> List[Dict[str, Any]]:
        """Identify influential papers using citation metrics."""
        # Calculate PageRank
        if len(self.citation_graph) == 0:
            return []
        
        pagerank = nx.pagerank(self.citation_graph)
        
        # Get papers with high PageRank
        key_papers = []
        
        for paper_id, score in sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:20]:
            paper = self.dataset.get(paper_id)
            if paper and paper.metadata.get('citation_count', 0) >= min_citations:
                key_papers.append({
                    'title': paper.metadata['title'],
                    'authors': paper.metadata.get('authors', []),
                    'year': paper.metadata.get('year'),
                    'citations': paper.metadata.get('citation_count', 0),
                    'pagerank': score,
                    'unique_id': paper_id
                })
        
        return key_papers
    
    def analyze_research_trends(self, start_year: int = 2010, 
                              end_year: int = 2024) -> Dict[str, Any]:
        """Analyze research trends over time."""
        # Get papers in date range
        papers = self.dataset.sql_filter(
            f"metadata.year >= {start_year} AND metadata.year <= {end_year}"
        )
        
        # Analyze by year
        papers_by_year = defaultdict(list)
        for paper in papers:
            year = paper.metadata.get('year')
            if year:
                papers_by_year[year].append(paper)
        
        # Extract trends
        trends = {
            'papers_per_year': {},
            'top_authors_per_year': {},
            'popular_topics': {},
            'collaboration_growth': {}
        }
        
        for year, year_papers in sorted(papers_by_year.items()):
            trends['papers_per_year'][year] = len(year_papers)
            
            # Top authors
            author_counts = Counter()
            for paper in year_papers:
                for author in paper.metadata.get('authors', []):
                    author_counts[author] += 1
            
            trends['top_authors_per_year'][year] = author_counts.most_common(5)
            
            # Extract topics from titles and abstracts
            words = []
            for paper in year_papers:
                # Simple word extraction - could use NLP for better results
                text = f"{paper.metadata['title']} {paper.metadata.get('abstract', '')}"
                words.extend(re.findall(r'\b[a-z]{4,}\b', text.lower()))
            
            # Filter common words
            stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'their'}
            topic_counts = Counter(w for w in words if w not in stopwords)
            trends['popular_topics'][year] = topic_counts.most_common(10)
            
            # Average authors per paper (collaboration indicator)
            avg_authors = np.mean([len(p.metadata.get('authors', [])) for p in year_papers])
            trends['collaboration_growth'][year] = avg_authors
        
        return trends
    
    def generate_literature_review(self, topic: str, max_papers: int = 20) -> str:
        """Generate a literature review summary for a topic."""
        # Search for relevant papers
        papers = self.search_papers(topic, limit=max_papers)
        
        if not papers:
            return f"No papers found on topic: {topic}"
        
        # Group by year
        papers_by_year = defaultdict(list)
        for paper in papers:
            year = paper.get('year', 'Unknown')
            papers_by_year[year].append(paper)
        
        # Generate review
        review = f"# Literature Review: {topic}\n\n"
        review += f"This review covers {len(papers)} papers on the topic of {topic}.\n\n"
        
        # Chronological overview
        review += "## Chronological Overview\n\n"
        
        for year in sorted(papers_by_year.keys(), reverse=True):
            if year != 'Unknown':
                review += f"### {year}\n\n"
                for paper in papers_by_year[year]:
                    authors = paper['authors']
                    if len(authors) > 3:
                        author_str = f"{authors[0]} et al."
                    else:
                        author_str = ", ".join(authors)
                    
                    review += f"- **{paper['title']}** by {author_str}\n"
                    review += f"  - {paper['abstract']}\n"
                    review += f"  - Citations: {paper['citations']}\n\n"
        
        # Key findings
        review += "## Key Papers\n\n"
        
        # Sort by citations
        key_papers = sorted(papers, key=lambda x: x.get('citations', 0), reverse=True)[:5]
        
        for paper in key_papers:
            review += f"### {paper['title']}\n"
            review += f"Authors: {', '.join(paper['authors'])}\n"
            review += f"Year: {paper.get('year', 'Unknown')}\n"
            review += f"Citations: {paper['citations']}\n"
            review += f"Abstract: {paper['abstract']}\n\n"
        
        return review
    
    def export_to_bibtex(self, paper_ids: List[str], output_file: str):
        """Export papers to BibTeX format."""
        entries = []
        
        for paper_id in paper_ids:
            paper = self.dataset.get(paper_id)
            if not paper:
                continue
            
            # Create BibTeX entry
            entry = {
                'ENTRYTYPE': 'article',
                'ID': paper.metadata.get('bibtex_key', paper_id),
                'title': paper.metadata['title'],
                'author': ' and '.join(paper.metadata.get('authors', [])),
                'year': str(paper.metadata.get('year', '')),
                'journal': paper.metadata.get('journal', ''),
                'volume': paper.metadata.get('volume', ''),
                'pages': paper.metadata.get('pages', ''),
                'doi': paper.metadata.get('doi', ''),
                'url': paper.metadata.get('url', ''),
                'abstract': paper.metadata.get('abstract', '')
            }
            
            # Remove empty fields
            entry = {k: v for k, v in entry.items() if v}
            entries.append(entry)
        
        # Write BibTeX
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = entries
        
        with open(output_file, 'w') as f:
            bibtexparser.dump(db, f)

# Example usage
if __name__ == "__main__":
    # Initialize collection
    collection = ResearchPaperCollection()
    
    # Import papers from various sources
    # From arXiv
    collection.import_arxiv_paper("2017.03762")  # Attention Is All You Need
    collection.import_arxiv_paper("1810.04805")  # BERT
    
    # From PDF files
    pdf_dir = Path("research_papers")
    for pdf_file in pdf_dir.glob("*.pdf"):
        collection.import_pdf(str(pdf_file))
    
    # From BibTeX
    collection.import_bibtex("references.bib")
    
    # Search papers
    nlp_papers = collection.search_papers(
        "natural language processing transformer",
        filters={'year_from': 2017, 'min_citations': 50}
    )
    
    print("Found NLP papers:")
    for paper in nlp_papers[:5]:
        print(f"- {paper['title']} ({paper['year']}) - Citations: {paper['citations']}")
    
    # Find similar papers
    if nlp_papers:
        similar = collection.find_similar_papers(nlp_papers[0]['unique_id'])
        print(f"\nPapers similar to '{nlp_papers[0]['title']}':")
        for paper in similar[:3]:
            print(f"- {paper['title']} (similarity: {paper['similarity']:.2f})")
    
    # Identify key papers
    key_papers = collection.identify_key_papers(min_citations=100)
    print("\nMost influential papers:")
    for paper in key_papers[:5]:
        print(f"- {paper['title']} - PageRank: {paper['pagerank']:.4f}")
    
    # Analyze trends
    trends = collection.analyze_research_trends(2015, 2023)
    print("\nPapers per year:")
    for year, count in sorted(trends['papers_per_year'].items()):
        print(f"  {year}: {count} papers")
    
    # Generate literature review
    review = collection.generate_literature_review("transformer models", max_papers=15)
    with open("transformer_review.md", "w") as f:
        f.write(review)
    
    print("\nLiterature review saved to transformer_review.md")
```

## Key Concepts

### 1. Multi-Source Import
- arXiv API integration
- PDF text extraction with PyMuPDF
- BibTeX parsing
- Metadata extraction from multiple formats

### 2. Citation Analysis
- Citation extraction from text
- Reference parsing
- Citation network building
- PageRank for influence metrics

### 3. Knowledge Graphs
- Citation graph (directed)
- Author collaboration graph
- Network analysis metrics
- Subgraph extraction

### 4. Advanced Search
- Semantic search on content
- Metadata filtering
- Similar paper discovery
- Multi-criteria ranking

### 5. Research Analytics
- Trend analysis over time
- Author productivity metrics
- Topic evolution tracking
- Collaboration patterns

## Extensions

### 1. Enhanced Citation Matching
```python
def match_citations_to_papers(self):
    """Match citation references to actual papers in collection."""
    all_papers = list(self.dataset.iter_records())
    
    # Build search index
    paper_index = {}
    for paper in all_papers:
        # Index by title, authors, year
        key = f"{paper.metadata['title'].lower()} {paper.metadata.get('year', '')}"
        paper_index[key] = paper.unique_id
        
        # Also index by first author + year
        if paper.metadata.get('authors'):
            first_author = paper.metadata['authors'][0].split()[-1]  # Last name
            author_key = f"{first_author.lower()} {paper.metadata.get('year', '')}"
            paper_index[author_key] = paper.unique_id
    
    # Match citations
    for paper in all_papers:
        updated = False
        new_relationships = []
        
        for rel in paper.metadata.get('relationships', []):
            if rel['relationship_type'] == 'cites':
                ref_text = rel['metadata'].get('reference_text', '')
                
                # Try to match reference
                matched_id = self._match_reference(ref_text, paper_index)
                if matched_id and matched_id != rel['target_id']:
                    # Update relationship
                    new_relationships.append({
                        'relationship_type': 'cites',
                        'target_id': matched_id,
                        'metadata': {'reference_text': ref_text, 'matched': True}
                    })
                    updated = True
                else:
                    new_relationships.append(rel)
        
        if updated:
            paper.metadata['relationships'] = new_relationships
            self.dataset.update(paper.unique_id, metadata=paper.metadata)
```

### 2. Topic Modeling
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def extract_topics(self, n_topics: int = 10) -> Dict[str, Any]:
    """Extract topics from paper collection using LDA."""
    # Get all papers
    papers = list(self.dataset.iter_records())
    
    # Prepare documents
    documents = []
    for paper in papers:
        doc = f"{paper.metadata['title']} {paper.metadata.get('abstract', '')}"
        documents.append(doc)
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    doc_term_matrix = vectorizer.fit_transform(documents)
    
    # LDA topic modeling
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42
    )
    lda.fit(doc_term_matrix)
    
    # Extract topics
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    
    for topic_idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[-10:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append({
            'topic_id': topic_idx,
            'words': top_words,
            'weight': topic[top_words_idx].tolist()
        })
    
    # Assign topics to papers
    doc_topics = lda.transform(doc_term_matrix)
    
    for i, paper in enumerate(papers):
        topic_dist = doc_topics[i]
        main_topic = topic_dist.argmax()
        
        paper.metadata['topics'] = {
            'main_topic': int(main_topic),
            'topic_distribution': topic_dist.tolist()
        }
        self.dataset.update(paper.unique_id, metadata=paper.metadata)
    
    return {
        'topics': topics,
        'n_documents': len(papers)
    }
```

### 3. Reading List Generator
```python
def generate_reading_list(self, topic: str, level: str = "beginner",
                         max_papers: int = 10) -> List[Dict[str, Any]]:
    """Generate curated reading list for a topic."""
    # Search for papers
    papers = self.search_papers(topic, limit=50)
    
    # Score papers based on level
    scored_papers = []
    
    for paper in papers:
        score = 0
        
        if level == "beginner":
            # Prefer survey papers, tutorials
            if any(word in paper['title'].lower() 
                   for word in ['survey', 'tutorial', 'introduction', 'overview']):
                score += 5
            # Prefer well-cited papers
            score += min(paper.get('citations', 0) / 100, 3)
            
        elif level == "intermediate":
            # Balance of citations and recency
            score += min(paper.get('citations', 0) / 50, 4)
            year = paper.get('year', 0)
            if year > 2020:
                score += 2
                
        elif level == "advanced":
            # Recent papers with moderate citations
            year = paper.get('year', 0)
            if year > 2022:
                score += 3
            score += min(paper.get('citations', 0) / 20, 2)
        
        scored_papers.append((paper, score))
    
    # Sort by score
    scored_papers.sort(key=lambda x: x[1], reverse=True)
    
    # Create reading list
    reading_list = []
    for paper, score in scored_papers[:max_papers]:
        reading_list.append({
            **paper,
            'relevance_score': score,
            'reading_time': self._estimate_reading_time(paper['unique_id'])
        })
    
    return reading_list

def _estimate_reading_time(self, paper_id: str) -> int:
    """Estimate reading time in minutes."""
    paper = self.dataset.get(paper_id)
    if not paper:
        return 30
    
    # Estimate based on content length
    word_count = len(paper.text_content.split())
    
    # Average reading speed: 200-250 words per minute
    # Academic papers need slower reading
    reading_time = word_count / 150  
    
    return int(reading_time)
```

### 4. Collaboration Network Analysis
```python
def analyze_collaboration_network(self) -> Dict[str, Any]:
    """Analyze author collaboration patterns."""
    # Compute network metrics
    metrics = {
        'total_authors': self.author_graph.number_of_nodes(),
        'collaborations': self.author_graph.number_of_edges(),
        'avg_collaborators': np.mean([d for n, d in self.author_graph.degree()]),
        'network_density': nx.density(self.author_graph)
    }
    
    # Find most collaborative authors
    centrality = nx.degree_centrality(self.author_graph)
    top_collaborators = sorted(
        centrality.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    metrics['top_collaborators'] = [
        {
            'author': author,
            'collaborators': self.author_graph.degree(author),
            'centrality': cent
        }
        for author, cent in top_collaborators
    ]
    
    # Find research groups (communities)
    communities = nx.community.louvain_communities(self.author_graph)
    
    metrics['research_groups'] = []
    for i, community in enumerate(communities):
        if len(community) >= 3:  # Significant groups only
            metrics['research_groups'].append({
                'group_id': i,
                'size': len(community),
                'members': list(community)[:10]  # Top members
            })
    
    return metrics
```

### 5. Paper Recommendation System
```python
def recommend_papers(self, user_history: List[str], 
                    method: str = "collaborative") -> List[Dict[str, Any]]:
    """Recommend papers based on user reading history."""
    if method == "collaborative":
        # Based on what similar users read
        return self._collaborative_filtering(user_history)
    elif method == "content":
        # Based on paper similarity
        return self._content_based_filtering(user_history)
    elif method == "hybrid":
        # Combine both approaches
        collab = self._collaborative_filtering(user_history, limit=15)
        content = self._content_based_filtering(user_history, limit=15)
        
        # Merge and re-rank
        all_recs = {}
        for rec in collab + content:
            if rec['unique_id'] not in all_recs:
                all_recs[rec['unique_id']] = rec
            else:
                # Average scores
                all_recs[rec['unique_id']]['score'] = (
                    all_recs[rec['unique_id']]['score'] + rec['score']
                ) / 2
        
        # Sort by combined score
        return sorted(all_recs.values(), 
                     key=lambda x: x['score'], 
                     reverse=True)[:10]

def _content_based_filtering(self, user_history: List[str], 
                           limit: int = 10) -> List[Dict[str, Any]]:
    """Recommend based on content similarity."""
    if not user_history:
        return []
    
    # Get embeddings of read papers
    read_embeddings = []
    for paper_id in user_history:
        paper = self.dataset.get(paper_id)
        if paper and paper.vector:
            read_embeddings.append(paper.vector)
    
    if not read_embeddings:
        return []
    
    # Average embedding
    avg_embedding = np.mean(read_embeddings, axis=0)
    
    # Find similar papers
    similar = self.dataset.knn_search(
        avg_embedding,
        k=limit + len(user_history)
    )
    
    # Filter out already read
    recommendations = []
    for result in similar:
        if result.unique_id not in user_history:
            recommendations.append({
                'unique_id': result.unique_id,
                'title': result.metadata['title'],
                'authors': result.metadata.get('authors', []),
                'score': result.score,
                'reason': 'Similar to your reading history'
            })
    
    return recommendations[:limit]
```

## Best Practices

1. **Citation Accuracy**: Validate extracted citations
2. **Duplicate Detection**: Check for duplicate papers
3. **Metadata Quality**: Ensure consistent metadata
4. **PDF Processing**: Handle various PDF formats
5. **Network Analysis**: Regular graph updates
6. **Storage Efficiency**: Store PDFs separately
7. **Privacy**: Respect copyright and access rights

## See Also

- [Document Processing Pipeline](document-pipeline.md) - PDF processing techniques
- [Multi-Source Search](multi-source-search.md) - Searching across papers
- [Scientific Data Catalog](scientific-catalog.md) - Managing research data
- [API Reference](../api/overview.md) - FrameDataset documentation