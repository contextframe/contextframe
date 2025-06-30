# Scientific Data Catalog

Build a comprehensive scientific data management system that catalogs research datasets, experimental results, and publications while maintaining provenance, reproducibility, and FAIR (Findable, Accessible, Interoperable, Reusable) principles.

## Problem Statement

Scientific research generates vast amounts of heterogeneous data across experiments, simulations, and observations. Researchers need to catalog, search, and track the lineage of datasets while ensuring reproducibility and compliance with data management plans.

## Solution Overview

We'll build a scientific data catalog that:
1. Catalogs diverse scientific datasets with rich metadata
2. Tracks data provenance and experimental conditions
3. Links datasets to publications and code
4. Enables discovery through semantic search
5. Ensures FAIR data principles compliance

## Complete Code

```python
import os
import re
import json
import hashlib
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import h5py
import netCDF4
import yaml
from dataclasses import dataclass
import pint
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
class DatasetMetadata:
    """Scientific dataset metadata following FAIR principles."""
    identifier: str  # DOI or persistent identifier
    title: str
    description: str
    creators: List[Dict[str, str]]  # name, orcid, affiliation
    subject: List[str]  # Scientific domains
    keywords: List[str]
    date_created: datetime
    date_modified: datetime
    version: str
    license: str
    access_rights: str
    format: str
    size_bytes: int
    checksum: str
    spatial_coverage: Optional[Dict[str, Any]] = None
    temporal_coverage: Optional[Dict[str, Any]] = None
    variables: Optional[List[Dict[str, Any]]] = None
    methodology: Optional[str] = None
    instruments: Optional[List[str]] = None
    funding: Optional[List[Dict[str, str]]] = None

class ScientificDataCatalog:
    """Comprehensive scientific data catalog system."""
    
    def __init__(self, dataset_path: str = "scientific_catalog.lance"):
        """Initialize scientific data catalog."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Unit registry for scientific units
        self.ureg = pint.UnitRegistry()
        
        # Supported data formats
        self.format_handlers = {
            '.csv': self._process_csv,
            '.h5': self._process_hdf5,
            '.hdf5': self._process_hdf5,
            '.nc': self._process_netcdf,
            '.json': self._process_json,
            '.yaml': self._process_yaml,
            '.npy': self._process_numpy,
            '.parquet': self._process_parquet
        }
        
        # Scientific domains taxonomy
        self.domains = {
            'physics': ['quantum', 'particle', 'condensed matter', 'astrophysics'],
            'chemistry': ['organic', 'inorganic', 'physical', 'analytical'],
            'biology': ['molecular', 'cellular', 'ecology', 'genomics'],
            'earth_science': ['geology', 'meteorology', 'oceanography', 'climate'],
            'astronomy': ['stellar', 'galactic', 'cosmology', 'planetary'],
            'materials': ['nanomaterials', 'polymers', 'ceramics', 'composites']
        }
        
    def catalog_dataset(self, 
                       file_path: str,
                       metadata: DatasetMetadata,
                       experiment_id: Optional[str] = None,
                       parent_dataset: Optional[str] = None) -> FrameRecord:
        """Catalog a scientific dataset with comprehensive metadata."""
        print(f"Cataloging dataset: {metadata.title}")
        
        # Calculate file checksum
        file_checksum = self._calculate_checksum(file_path)
        metadata.checksum = file_checksum
        
        # Get file size
        metadata.size_bytes = os.path.getsize(file_path)
        
        # Process data file to extract schema and sample
        file_ext = Path(file_path).suffix.lower()
        if file_ext in self.format_handlers:
            data_info = self.format_handlers[file_ext](file_path)
        else:
            data_info = {'format': 'unknown', 'preview': 'Binary data'}
        
        # Create comprehensive description
        description = self._create_description(metadata, data_info)
        
        # Create FAIR-compliant metadata
        fair_metadata = create_metadata(
            title=metadata.title,
            source="scientific_dataset",
            
            # Identification
            identifier=metadata.identifier,
            version=metadata.version,
            
            # Attribution
            creators=[self._format_creator(c) for c in metadata.creators],
            license=metadata.license,
            access_rights=metadata.access_rights,
            
            # Classification
            subject=metadata.subject,
            keywords=metadata.keywords,
            domains=self._classify_domains(metadata.subject, metadata.keywords),
            
            # Technical details
            format=metadata.format,
            size_bytes=metadata.size_bytes,
            checksum=metadata.checksum,
            variables=data_info.get('variables', metadata.variables),
            schema=data_info.get('schema'),
            
            # Temporal and spatial
            date_created=metadata.date_created.isoformat(),
            date_modified=metadata.date_modified.isoformat(),
            temporal_coverage=metadata.temporal_coverage,
            spatial_coverage=metadata.spatial_coverage,
            
            # Provenance
            experiment_id=experiment_id,
            methodology=metadata.methodology,
            instruments=metadata.instruments,
            parent_dataset=parent_dataset,
            derived_from=parent_dataset,
            
            # Administrative
            funding=metadata.funding,
            data_management_plan=True,
            fair_compliant=self._check_fair_compliance(metadata)
        )
        
        # Create record
        record = FrameRecord(
            text_content=description,
            metadata=fair_metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Add relationships
        if parent_dataset:
            record.metadata = add_relationship_to_metadata(
                record.metadata,
                create_relationship(
                    source_id=record.unique_id,
                    target_id=parent_dataset,
                    relationship_type="child",
                    properties={'derivation_type': 'processed'}
                )
            )
        
        self.dataset.add(record, generate_embedding=True)
        
        # Create data dictionary entries
        if data_info.get('variables'):
            self._create_data_dictionary(record.unique_id, data_info['variables'])
        
        return record
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Process CSV file to extract schema."""
        df = pd.read_csv(file_path, nrows=5)
        
        variables = []
        for col in df.columns:
            var_info = {
                'name': col,
                'type': str(df[col].dtype),
                'non_null_count': df[col].notna().sum(),
                'unique_values': df[col].nunique() if df[col].dtype in ['object', 'category'] else None,
                'min': df[col].min() if pd.api.types.is_numeric_dtype(df[col]) else None,
                'max': df[col].max() if pd.api.types.is_numeric_dtype(df[col]) else None
            }
            
            # Try to detect units from column name
            unit_match = re.search(r'\[([^\]]+)\]', col)
            if unit_match:
                var_info['unit'] = unit_match.group(1)
            
            variables.append(var_info)
        
        return {
            'format': 'CSV',
            'shape': df.shape,
            'variables': variables,
            'preview': df.head().to_string(),
            'schema': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    
    def _process_hdf5(self, file_path: str) -> Dict[str, Any]:
        """Process HDF5 file to extract structure."""
        with h5py.File(file_path, 'r') as f:
            structure = {}
            variables = []
            
            def visit_item(name, obj):
                if isinstance(obj, h5py.Dataset):
                    var_info = {
                        'name': name,
                        'shape': obj.shape,
                        'dtype': str(obj.dtype),
                        'size': obj.size,
                        'dimensions': len(obj.shape)
                    }
                    
                    # Extract attributes
                    attrs = dict(obj.attrs)
                    if 'units' in attrs:
                        var_info['unit'] = attrs['units']
                    if 'description' in attrs:
                        var_info['description'] = attrs['description']
                    
                    variables.append(var_info)
                    structure[name] = f"Dataset {obj.shape} {obj.dtype}"
                elif isinstance(obj, h5py.Group):
                    structure[name] = f"Group with {len(obj)} items"
            
            f.visititems(visit_item)
            
            return {
                'format': 'HDF5',
                'structure': structure,
                'variables': variables,
                'total_size': sum(v['size'] for v in variables if 'size' in v)
            }
    
    def _process_netcdf(self, file_path: str) -> Dict[str, Any]:
        """Process NetCDF file to extract metadata."""
        with netCDF4.Dataset(file_path, 'r') as nc:
            variables = []
            
            for var_name in nc.variables:
                var = nc.variables[var_name]
                var_info = {
                    'name': var_name,
                    'dimensions': var.dimensions,
                    'shape': var.shape,
                    'dtype': str(var.dtype),
                    'attributes': dict(var.__dict__)
                }
                
                # Standard NetCDF attributes
                if hasattr(var, 'units'):
                    var_info['unit'] = var.units
                if hasattr(var, 'long_name'):
                    var_info['description'] = var.long_name
                if hasattr(var, 'standard_name'):
                    var_info['standard_name'] = var.standard_name
                
                variables.append(var_info)
            
            # Global attributes
            global_attrs = dict(nc.__dict__)
            
            return {
                'format': 'NetCDF',
                'dimensions': dict(nc.dimensions),
                'variables': variables,
                'global_attributes': global_attrs,
                'conventions': global_attrs.get('Conventions', 'Unknown')
            }
    
    def _process_json(self, file_path: str) -> Dict[str, Any]:
        """Process JSON file to extract structure."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        def analyze_structure(obj, path=''):
            if isinstance(obj, dict):
                return {
                    'type': 'object',
                    'properties': {k: analyze_structure(v, f"{path}.{k}") for k, v in obj.items()}
                }
            elif isinstance(obj, list):
                if obj:
                    return {
                        'type': 'array',
                        'length': len(obj),
                        'items': analyze_structure(obj[0], f"{path}[]")
                    }
                return {'type': 'array', 'length': 0}
            else:
                return {'type': type(obj).__name__}
        
        return {
            'format': 'JSON',
            'structure': analyze_structure(data),
            'top_level_keys': list(data.keys()) if isinstance(data, dict) else None
        }
    
    def _process_yaml(self, file_path: str) -> Dict[str, Any]:
        """Process YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Reuse JSON structure analysis
        return self._process_json(file_path)
    
    def _process_numpy(self, file_path: str) -> Dict[str, Any]:
        """Process NumPy array file."""
        arr = np.load(file_path, allow_pickle=False)
        
        return {
            'format': 'NumPy',
            'shape': arr.shape,
            'dtype': str(arr.dtype),
            'size': arr.size,
            'ndim': arr.ndim,
            'statistics': {
                'mean': float(np.mean(arr)) if np.issubdtype(arr.dtype, np.number) else None,
                'std': float(np.std(arr)) if np.issubdtype(arr.dtype, np.number) else None,
                'min': float(np.min(arr)) if np.issubdtype(arr.dtype, np.number) else None,
                'max': float(np.max(arr)) if np.issubdtype(arr.dtype, np.number) else None
            }
        }
    
    def _process_parquet(self, file_path: str) -> Dict[str, Any]:
        """Process Parquet file."""
        df = pd.read_parquet(file_path)
        
        # Reuse CSV processing
        return self._process_csv(file_path)
    
    def _create_description(self, metadata: DatasetMetadata, 
                          data_info: Dict[str, Any]) -> str:
        """Create comprehensive dataset description."""
        desc_parts = [
            f"# {metadata.title}",
            f"\n{metadata.description}",
            f"\n## Dataset Information",
            f"- **Identifier**: {metadata.identifier}",
            f"- **Version**: {metadata.version}",
            f"- **Format**: {metadata.format}",
            f"- **Size**: {self._format_size(metadata.size_bytes)}",
            f"- **License**: {metadata.license}",
            f"- **Access Rights**: {metadata.access_rights}"
        ]
        
        # Creators
        desc_parts.append("\n## Creators")
        for creator in metadata.creators:
            creator_str = f"- {creator['name']}"
            if 'orcid' in creator:
                creator_str += f" (ORCID: {creator['orcid']})"
            if 'affiliation' in creator:
                creator_str += f" - {creator['affiliation']}"
            desc_parts.append(creator_str)
        
        # Coverage
        if metadata.temporal_coverage:
            desc_parts.append(f"\n## Temporal Coverage")
            desc_parts.append(f"- Start: {metadata.temporal_coverage.get('start')}")
            desc_parts.append(f"- End: {metadata.temporal_coverage.get('end')}")
        
        if metadata.spatial_coverage:
            desc_parts.append(f"\n## Spatial Coverage")
            for key, value in metadata.spatial_coverage.items():
                desc_parts.append(f"- {key}: {value}")
        
        # Variables
        if data_info.get('variables'):
            desc_parts.append("\n## Variables")
            for var in data_info['variables'][:10]:  # Limit to first 10
                var_desc = f"- **{var['name']}**"
                if 'unit' in var:
                    var_desc += f" [{var['unit']}]"
                if 'description' in var:
                    var_desc += f": {var['description']}"
                desc_parts.append(var_desc)
        
        # Methodology
        if metadata.methodology:
            desc_parts.append(f"\n## Methodology")
            desc_parts.append(metadata.methodology)
        
        # Keywords
        desc_parts.append(f"\n**Keywords**: {', '.join(metadata.keywords)}")
        
        return "\n".join(desc_parts)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def _format_creator(self, creator: Dict[str, str]) -> str:
        """Format creator information."""
        parts = [creator['name']]
        if 'orcid' in creator:
            parts.append(f"ORCID:{creator['orcid']}")
        if 'affiliation' in creator:
            parts.append(f"({creator['affiliation']})")
        return " ".join(parts)
    
    def _classify_domains(self, subjects: List[str], 
                        keywords: List[str]) -> List[str]:
        """Classify dataset into scientific domains."""
        classified_domains = set()
        
        # Check subjects and keywords
        all_terms = [s.lower() for s in subjects + keywords]
        
        for domain, subdomains in self.domains.items():
            if domain in all_terms:
                classified_domains.add(domain)
            
            for subdomain in subdomains:
                if any(subdomain in term for term in all_terms):
                    classified_domains.add(domain)
                    break
        
        return list(classified_domains)
    
    def _check_fair_compliance(self, metadata: DatasetMetadata) -> Dict[str, bool]:
        """Check FAIR principles compliance."""
        return {
            'findable': bool(metadata.identifier and metadata.keywords),
            'accessible': bool(metadata.license and metadata.access_rights),
            'interoperable': bool(metadata.format and metadata.variables),
            'reusable': bool(metadata.license and metadata.methodology and metadata.version)
        }
    
    def _create_data_dictionary(self, dataset_id: str, 
                              variables: List[Dict[str, Any]]):
        """Create detailed data dictionary entries."""
        for var in variables:
            metadata = create_metadata(
                title=f"Variable: {var['name']}",
                source="data_dictionary",
                dataset_id=dataset_id,
                variable_name=var['name'],
                data_type=var.get('type', 'unknown'),
                unit=var.get('unit'),
                description=var.get('description'),
                shape=var.get('shape'),
                statistics=var.get('statistics')
            )
            
            content = f"Variable: {var['name']}\n"
            if 'description' in var:
                content += f"\n{var['description']}\n"
            if 'unit' in var:
                content += f"\nUnit: {var['unit']}"
            
            record = FrameRecord(
                text_content=content,
                metadata=metadata,
                unique_id=generate_uuid(),
                record_type="document"
            )
            
            # Link to dataset
            record.metadata = add_relationship_to_metadata(
                record.metadata,
                create_relationship(
                    source_id=record.unique_id,
                    target_id=dataset_id,
                    relationship_type="child"
                )
            )
            
            self.dataset.add(record)
    
    def link_publication(self, dataset_id: str, 
                        publication: Dict[str, Any]) -> FrameRecord:
        """Link dataset to publication."""
        # Create publication record
        pub_metadata = create_metadata(
            title=publication['title'],
            source="publication",
            doi=publication.get('doi'),
            authors=publication.get('authors', []),
            journal=publication.get('journal'),
            year=publication.get('year'),
            abstract=publication.get('abstract'),
            dataset_references=[dataset_id]
        )
        
        pub_record = FrameRecord(
            text_content=f"{publication['title']}\n\n{publication.get('abstract', '')}",
            metadata=pub_metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Create bidirectional relationship
        pub_record.metadata = add_relationship_to_metadata(
            pub_record.metadata,
            create_relationship(
                source_id=pub_record.unique_id,
                target_id=dataset_id,
                relationship_type="reference",
                properties={'reference_type': 'uses_data'}
            )
        )
        
        self.dataset.add(pub_record, generate_embedding=True)
        
        return pub_record
    
    def link_code(self, dataset_id: str, 
                 code_repo: Dict[str, Any]) -> FrameRecord:
        """Link dataset to analysis code."""
        # Create code repository record
        code_metadata = create_metadata(
            title=f"Code: {code_repo['name']}",
            source="code_repository",
            repository_url=code_repo['url'],
            language=code_repo.get('language'),
            description=code_repo.get('description'),
            version=code_repo.get('version'),
            license=code_repo.get('license'),
            dataset_dependencies=[dataset_id]
        )
        
        code_record = FrameRecord(
            text_content=f"Analysis Code: {code_repo['name']}\n\n{code_repo.get('description', '')}\n\nRepository: {code_repo['url']}",
            metadata=code_metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        # Link to dataset
        code_record.metadata = add_relationship_to_metadata(
            code_record.metadata,
            create_relationship(
                source_id=code_record.unique_id,
                target_id=dataset_id,
                relationship_type="reference",
                properties={'reference_type': 'analyzes_data'}
            )
        )
        
        self.dataset.add(code_record, generate_embedding=True)
        
        return code_record
    
    def create_experiment_collection(self, experiment: Dict[str, Any]) -> str:
        """Create experiment collection linking multiple datasets."""
        # Create experiment header
        exp_metadata = create_metadata(
            title=f"Experiment: {experiment['title']}",
            source="experiment",
            experiment_id=experiment['id'],
            principal_investigator=experiment['pi'],
            start_date=experiment['start_date'],
            end_date=experiment.get('end_date'),
            hypothesis=experiment.get('hypothesis'),
            methods=experiment.get('methods', []),
            equipment=experiment.get('equipment', []),
            funding_sources=experiment.get('funding', [])
        )
        
        exp_record = FrameRecord(
            text_content=f"{experiment['title']}\n\n{experiment.get('description', '')}\n\nHypothesis: {experiment.get('hypothesis', 'N/A')}",
            metadata=exp_metadata,
            unique_id=generate_uuid(),
            record_type="collection_header"
        )
        
        self.dataset.add(exp_record, generate_embedding=True)
        
        return exp_record.unique_id
    
    def search_by_variable(self, variable_name: str, 
                         unit: Optional[str] = None) -> List[FrameRecord]:
        """Search datasets containing specific variable."""
        filter_dict = {
            'metadata.source': {'in': ['scientific_dataset', 'data_dictionary']}
        }
        
        # Search in variables
        results = self.dataset.search(
            query=variable_name,
            filter=filter_dict,
            limit=50
        )
        
        # Filter by unit if specified
        if unit:
            filtered_results = []
            for result in results:
                variables = result.metadata.custom_metadata.get('variables', [])
                for var in variables:
                    if var.get('name', '').lower() == variable_name.lower():
                        if var.get('unit', '').lower() == unit.lower():
                            filtered_results.append(result)
                            break
            results = filtered_results
        
        return results
    
    def find_related_datasets(self, dataset_id: str, 
                            similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find datasets related by content, methods, or domain."""
        # Get source dataset
        source = self.dataset.get(dataset_id)
        if not source:
            return []
        
        # Search similar datasets
        similar = self.dataset.search(
            query=source.text_content,
            filter={
                'metadata.source': 'scientific_dataset',
                'unique_id': {'ne': dataset_id}  # Exclude self
            },
            limit=20
        )
        
        # Analyze relationships
        related = []
        source_meta = source.metadata.custom_metadata
        
        for candidate in similar:
            if hasattr(candidate, 'score') and candidate.score < similarity_threshold:
                continue
            
            cand_meta = candidate.metadata.custom_metadata
            
            # Calculate relationship strength
            relationship_score = 0
            relationship_types = []
            
            # Same experiment
            if (source_meta.get('experiment_id') and 
                source_meta['experiment_id'] == cand_meta.get('experiment_id')):
                relationship_score += 0.5
                relationship_types.append('same_experiment')
            
            # Shared creators
            source_creators = set(c.split(' ORCID:')[0] for c in source_meta.get('creators', []))
            cand_creators = set(c.split(' ORCID:')[0] for c in cand_meta.get('creators', []))
            if source_creators & cand_creators:
                relationship_score += 0.3
                relationship_types.append('shared_creators')
            
            # Similar domains
            source_domains = set(source_meta.get('domains', []))
            cand_domains = set(cand_meta.get('domains', []))
            if source_domains & cand_domains:
                relationship_score += 0.2
                relationship_types.append('same_domain')
            
            # Similar instruments
            source_instruments = set(source_meta.get('instruments', []))
            cand_instruments = set(cand_meta.get('instruments', []))
            if source_instruments & cand_instruments:
                relationship_score += 0.2
                relationship_types.append('shared_instruments')
            
            if relationship_score > 0:
                related.append({
                    'dataset': candidate,
                    'similarity_score': getattr(candidate, 'score', 0),
                    'relationship_score': relationship_score,
                    'relationship_types': relationship_types,
                    'total_score': getattr(candidate, 'score', 0) * relationship_score
                })
        
        # Sort by total score
        return sorted(related, key=lambda x: x['total_score'], reverse=True)
    
    def generate_data_citation(self, dataset_id: str, 
                             style: str = 'datacite') -> str:
        """Generate proper data citation."""
        dataset = self.dataset.get(dataset_id)
        if not dataset:
            return ""
        
        meta = dataset.metadata.custom_metadata
        
        # Extract citation elements
        creators = meta.get('creators', ['Unknown'])
        year = datetime.fromisoformat(meta.get('date_created', '')).year
        title = dataset.metadata.title
        version = meta.get('version', '1.0')
        identifier = meta.get('identifier', dataset_id)
        
        if style == 'datacite':
            # DataCite format
            creator_str = "; ".join(c.split(' ORCID:')[0] for c in creators[:3])
            if len(creators) > 3:
                creator_str += " et al."
            
            citation = f"{creator_str} ({year}): {title}. Version {version}. "
            citation += f"[Data set]. {identifier}"
        
        elif style == 'bibtex':
            # BibTeX format
            creator_str = " and ".join(c.split(' ORCID:')[0] for c in creators)
            key = f"{creators[0].split()[0].lower()}{year}data"
            
            citation = f"@dataset{{{key},\n"
            citation += f"  author = {{{creator_str}}},\n"
            citation += f"  title = {{{title}}},\n"
            citation += f"  year = {{{year}}},\n"
            citation += f"  version = {{{version}}},\n"
            citation += f"  doi = {{{identifier}}},\n"
            citation += f"  url = {{{identifier}}}\n"
            citation += "}"
        
        return citation
    
    def export_metadata(self, dataset_id: str, 
                       format: str = 'datacite') -> str:
        """Export metadata in standard formats."""
        dataset = self.dataset.get(dataset_id)
        if not dataset:
            return ""
        
        meta = dataset.metadata.custom_metadata
        
        if format == 'datacite':
            # DataCite XML format
            xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
            xml_parts.append('<resource xmlns="http://datacite.org/schema/kernel-4">')
            
            # Required fields
            xml_parts.append(f'  <identifier identifierType="DOI">{meta.get("identifier", "")}</identifier>')
            
            xml_parts.append('  <creators>')
            for creator in meta.get('creators', []):
                xml_parts.append(f'    <creator><creatorName>{creator}</creatorName></creator>')
            xml_parts.append('  </creators>')
            
            xml_parts.append(f'  <titles><title>{dataset.metadata.title}</title></titles>')
            xml_parts.append(f'  <publisher>Scientific Data Catalog</publisher>')
            xml_parts.append(f'  <publicationYear>{datetime.fromisoformat(meta.get("date_created", "")).year}</publicationYear>')
            
            # Optional fields
            if meta.get('subjects'):
                xml_parts.append('  <subjects>')
                for subject in meta['subjects']:
                    xml_parts.append(f'    <subject>{subject}</subject>')
                xml_parts.append('  </subjects>')
            
            xml_parts.append('</resource>')
            
            return '\n'.join(xml_parts)
        
        elif format == 'json-ld':
            # Schema.org Dataset JSON-LD
            json_ld = {
                "@context": "https://schema.org/",
                "@type": "Dataset",
                "name": dataset.metadata.title,
                "description": meta.get('description', ''),
                "identifier": meta.get('identifier', ''),
                "url": meta.get('identifier', ''),
                "creator": [
                    {"@type": "Person", "name": c.split(' ORCID:')[0]}
                    for c in meta.get('creators', [])
                ],
                "datePublished": meta.get('date_created', ''),
                "dateModified": meta.get('date_modified', ''),
                "version": meta.get('version', ''),
                "keywords": meta.get('keywords', []),
                "license": meta.get('license', ''),
                "distribution": {
                    "@type": "DataDownload",
                    "encodingFormat": meta.get('format', ''),
                    "contentSize": meta.get('size_bytes', 0)
                }
            }
            
            return json.dumps(json_ld, indent=2)
        
        return ""

# Example usage
if __name__ == "__main__":
    # Initialize catalog
    catalog = ScientificDataCatalog()
    
    # Create experiment
    experiment_id = catalog.create_experiment_collection({
        'id': 'EXP-2024-001',
        'title': 'High-Temperature Superconductivity Study',
        'pi': 'Dr. Jane Smith',
        'start_date': '2024-01-15',
        'hypothesis': 'Novel copper oxide compounds will exhibit superconductivity above 150K',
        'methods': ['X-ray diffraction', 'SQUID magnetometry', 'Resistivity measurements'],
        'equipment': ['Bruker D8', 'Quantum Design MPMS3', 'PPMS DynaCool'],
        'funding': [{'agency': 'NSF', 'grant': 'DMR-2345678'}]
    })
    
    # Catalog experimental dataset
    dataset_metadata = DatasetMetadata(
        identifier='10.5555/example.001',
        title='Magnetization Data for CuO2 Compounds at Various Temperatures',
        description='SQUID magnetometry measurements of novel copper oxide compounds...',
        creators=[
            {'name': 'Jane Smith', 'orcid': '0000-0001-2345-6789', 'affiliation': 'University X'},
            {'name': 'John Doe', 'orcid': '0000-0002-3456-7890', 'affiliation': 'Lab Y'}
        ],
        subject=['condensed matter physics', 'superconductivity'],
        keywords=['high-Tc', 'cuprates', 'magnetization', 'SQUID'],
        date_created=datetime(2024, 3, 15),
        date_modified=datetime(2024, 3, 20),
        version='1.0',
        license='CC-BY-4.0',
        access_rights='Open Access',
        format='HDF5',
        spatial_coverage={'laboratory': 'Materials Science Lab, University X'},
        temporal_coverage={'start': '2024-01-20', 'end': '2024-03-15'},
        methodology='Samples prepared by solid-state reaction...',
        instruments=['Quantum Design MPMS3 SQUID']
    )
    
    dataset_record = catalog.catalog_dataset(
        file_path='/data/magnetization_data.h5',
        metadata=dataset_metadata,
        experiment_id=experiment_id
    )
    
    # Link publication
    publication = {
        'title': 'Observation of High-Temperature Superconductivity in Novel Cuprates',
        'doi': '10.1038/nature12345',
        'authors': ['Smith, J.', 'Doe, J.', 'Johnson, K.'],
        'journal': 'Nature',
        'year': 2024,
        'abstract': 'We report the discovery of superconductivity above 150K...'
    }
    
    catalog.link_publication(dataset_record.unique_id, publication)
    
    # Link analysis code
    code_repo = {
        'name': 'cuprate-analysis',
        'url': 'https://github.com/smithlab/cuprate-analysis',
        'language': 'Python',
        'description': 'Analysis scripts for magnetization data of cuprate superconductors',
        'version': 'v1.2.0',
        'license': 'MIT'
    }
    
    catalog.link_code(dataset_record.unique_id, code_repo)
    
    # Search for datasets with magnetization measurements
    results = catalog.search_by_variable('magnetization', unit='emu')
    
    print(f"Found {len(results)} datasets with magnetization data")
    
    # Find related datasets
    related = catalog.find_related_datasets(dataset_record.unique_id)
    
    print(f"\nRelated datasets:")
    for rel in related[:3]:
        print(f"- {rel['dataset'].metadata.title}")
        print(f"  Relationships: {', '.join(rel['relationship_types'])}")
    
    # Generate citation
    citation = catalog.generate_data_citation(dataset_record.unique_id)
    print(f"\nCitation:\n{citation}")
```

## Key Concepts

### FAIR Principles

The catalog ensures FAIR compliance:
- **Findable**: Persistent identifiers, rich metadata, indexed
- **Accessible**: Clear access rights, standard protocols
- **Interoperable**: Standard formats, controlled vocabularies
- **Reusable**: Clear licenses, provenance, methodology

### Data Provenance

Complete lineage tracking:
- Parent/child dataset relationships
- Processing history
- Experimental conditions
- Instrument configurations
- Version control

### Scientific Metadata

Comprehensive metadata capture:
- Standard schemas (DataCite, Dublin Core)
- Domain-specific vocabularies
- Units and measurements
- Spatial/temporal coverage
- Quality indicators

## Extensions

### Advanced Features

1. **Automated Extraction**
   - Metadata from file headers
   - Units from data
   - Statistics calculation
   - Quality metrics

2. **Workflow Integration**
   - Pipeline tracking
   - Automated cataloging
   - Validation checks
   - DOI minting

3. **Discovery Services**
   - Faceted search
   - Recommendation engine
   - Citation networks
   - Impact tracking

4. **Preservation**
   - Checksum verification
   - Format migration
   - Replication policies
   - Long-term archival

### Integration Options

1. **Repository Systems**
   - Dataverse integration
   - Zenodo deposits
   - Figshare sync
   - Institutional repositories

2. **Compute Platforms**
   - HPC job tracking
   - Cloud storage
   - Jupyter integration
   - Workflow managers

3. **Standards Compliance**
   - OAI-PMH provider
   - SWORD protocol
   - BagIt packaging
   - RO-Crate

## Best Practices

1. **Metadata Quality**
   - Use controlled vocabularies
   - Include rich descriptions
   - Specify units clearly
   - Document uncertainties

2. **Data Organization**
   - Consistent file naming
   - Logical folder structure
   - README files
   - Data dictionaries

3. **Preservation**
   - Use open formats
   - Include raw data
   - Document processing
   - Version datasets

4. **Sharing**
   - Clear licenses
   - Embargo periods
   - Access controls
   - Citation guidelines

This scientific data catalog provides a robust foundation for FAIR data management in research environments.