#!/usr/bin/env python3
"""Implementation of contextframe-get command."""

import argparse
import json
import sys
from contextframe.frame import FrameDataset, FrameRecord
from pathlib import Path


def format_as_json(record: FrameRecord) -> str:
    """Format record as JSON."""
    data = {
        "identifier": record.metadata.get("identifier"),
        "record_type": record.metadata.get("record_type", "document"),
        "title": record.metadata.get("title"),
        "text_content": record.text_content,
        "metadata": record.metadata,
        "has_raw_data": record.raw_data is not None,
        "raw_data_type": record.raw_data_type,
        "vector_dimension": len(record.vector) if record.vector is not None else 0,
    }
    return json.dumps(data, indent=2)


def format_as_text(record: FrameRecord) -> str:
    """Format record as plain text."""
    lines = []

    # Basic info
    lines.append(f"Identifier: {record.metadata.get('identifier')}")
    lines.append(f"Type: {record.metadata.get('record_type', 'document')}")

    if 'title' in record.metadata:
        lines.append(f"Title: {record.metadata['title']}")

    # Source info
    if 'source' in record.metadata:
        source = record.metadata['source']
        lines.append(
            f"Source: {source.get('type', 'unknown')} - {source.get('path', 'N/A')}"
        )

    # Relationships
    relationships = record.metadata.get('relationships', [])
    if relationships:
        lines.append("\nRelationships:")
        for rel in relationships:
            lines.append(
                f"  - {rel.get('relationship_type')} -> {rel.get('target_type')}: {rel.get('target_identifier')}"
            )

    # Custom metadata
    if 'custom_metadata' in record.metadata and record.metadata['custom_metadata']:
        lines.append("\nCustom Metadata:")
        for key, value in record.metadata['custom_metadata'].items():
            lines.append(f"  {key}: {value}")

    # Content
    lines.append("\nContent:")
    lines.append("-" * 60)
    lines.append(record.text_content)

    # Additional info
    if record.raw_data:
        lines.append(
            f"\nRaw Data: {len(record.raw_data)} bytes ({record.raw_data_type or 'unknown type'})"
        )

    if record.vector is not None and len(record.vector) > 0:
        lines.append(f"\nVector: {len(record.vector)} dimensions")

    return "\n".join(lines)


def format_as_markdown(record: FrameRecord) -> str:
    """Format record as Markdown."""
    lines = []

    # Title
    title = record.metadata.get('title', record.metadata.get('identifier', 'Document'))
    lines.append(f"# {title}")
    lines.append("")

    # Metadata section
    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- **Identifier**: `{record.metadata.get('identifier')}`")
    lines.append(f"- **Type**: {record.metadata.get('record_type', 'document')}")

    if 'source' in record.metadata:
        source = record.metadata['source']
        lines.append(
            f"- **Source**: {source.get('type', 'unknown')} - `{source.get('path', 'N/A')}`"
        )

    # Relationships
    relationships = record.metadata.get('relationships', [])
    if relationships:
        lines.append("")
        lines.append("### Relationships")
        lines.append("")
        for rel in relationships:
            rel_type = rel.get('relationship_type', 'unknown')
            target_type = rel.get('target_type', 'unknown')
            target_id = rel.get('target_identifier', 'unknown')
            lines.append(f"- **{rel_type}** → {target_type}: `{target_id}`")

    # Custom metadata
    if 'custom_metadata' in record.metadata and record.metadata['custom_metadata']:
        lines.append("")
        lines.append("### Custom Metadata")
        lines.append("")
        for key, value in record.metadata['custom_metadata'].items():
            lines.append(f"- **{key}**: {value}")

    # Content section
    lines.append("")
    lines.append("## Content")
    lines.append("")

    # If it looks like markdown, include it directly
    if record.text_content.strip().startswith('#') or '\n#' in record.text_content:
        lines.append(record.text_content)
    else:
        # Otherwise, format as code block
        lines.append("```")
        lines.append(record.text_content)
        lines.append("```")

    # Additional info
    if record.raw_data or record.vector is not None:
        lines.append("")
        lines.append("## Additional Information")
        lines.append("")

        if record.raw_data:
            lines.append(
                f"- **Raw Data**: {len(record.raw_data)} bytes ({record.raw_data_type or 'unknown type'})"
            )

        if record.vector is not None and len(record.vector) > 0:
            lines.append(f"- **Vector**: {len(record.vector)} dimensions")

    return "\n".join(lines)


def main():
    """Main entry point for get command."""
    parser = argparse.ArgumentParser(
        description='Get a specific document from a ContextFrame dataset'
    )
    parser.add_argument('dataset', help='Path to the dataset')
    parser.add_argument('identifier', help='Document identifier')
    parser.add_argument(
        '--format',
        choices=['json', 'text', 'markdown'],
        default='text',
        help='Output format',
    )

    args = parser.parse_args()

    # Open the dataset
    try:
        dataset = FrameDataset.open(args.dataset)
    except Exception as e:
        print(f"Error opening dataset: {e}", file=sys.stderr)
        sys.exit(1)

    # Find the document
    try:
        # Use filter to find by identifier
        filter_expr = f"identifier = '{args.identifier}'"
        results = dataset.search(filter=filter_expr, limit=1)

        if not results:
            print(f"Error: Document not found: {args.identifier}", file=sys.stderr)
            sys.exit(1)

        record = results[0]
    except Exception as e:
        print(f"Error retrieving document: {e}", file=sys.stderr)
        sys.exit(1)

    # Format and output
    if args.format == 'json':
        output = format_as_json(record)
    elif args.format == 'markdown':
        output = format_as_markdown(record)
    else:  # text
        output = format_as_text(record)

    print(output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
