#!/usr/bin/env python3
"""Implementation of contextframe-list command."""

import argparse
import json
import sys
from contextframe.frame import FrameDataset
from datetime import datetime
from pathlib import Path


def format_as_table(records: list) -> str:
    """Format records as a table."""
    if not records:
        return "No records found."

    # Define columns and their widths
    columns = [
        ("ID", 36),  # UUID width
        ("Type", 15),
        ("Title", 40),
        ("Size", 10),
        ("Updated", 20),
    ]

    # Print header
    header = ""
    separator = ""
    for col_name, width in columns:
        header += f"{col_name:<{width}} "
        separator += "-" * width + " "

    lines = [header, separator]

    # Print rows
    for record in records:
        row = ""

        # ID
        identifier = record.metadata.get("identifier", "N/A")
        if len(identifier) > 36:
            identifier = identifier[:33] + "..."
        row += f"{identifier:<36} "

        # Type
        record_type = record.metadata.get("record_type", "document")
        row += f"{record_type:<15} "

        # Title
        title = record.metadata.get("title", "")
        if not title and "source" in record.metadata:
            # Use filename from source if no title
            source_path = record.metadata["source"].get("path", "")
            if source_path:
                title = Path(source_path).name
        if not title:
            # Use first line of content as fallback
            first_line = record.text_content.split('\n')[0]
            title = first_line[:37] + "..." if len(first_line) > 40 else first_line
        else:
            title = title[:37] + "..." if len(title) > 40 else title
        row += f"{title:<40} "

        # Size
        size = len(record.text_content)
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        row += f"{size_str:<10} "

        # Updated (if available in metadata)
        updated = record.metadata.get(
            "updated_at", record.metadata.get("created_at", "")
        )
        if updated:
            try:
                # Try to parse and format the date
                if isinstance(updated, str):
                    dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    updated = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    updated = str(updated)[:16]
            except:
                updated = str(updated)[:20]
        else:
            updated = "N/A"
        row += f"{updated:<20}"

        lines.append(row)

    # Add summary
    lines.append(separator)
    lines.append(f"Total: {len(records)} records")

    return "\n".join(lines)


def format_as_json(records: list) -> str:
    """Format records as JSON."""
    data = []
    for record in records:
        data.append(
            {
                "identifier": record.metadata.get("identifier"),
                "record_type": record.metadata.get("record_type", "document"),
                "title": record.metadata.get("title"),
                "content_preview": record.text_content[:200] + "..."
                if len(record.text_content) > 200
                else record.text_content,
                "metadata": record.metadata,
                "content_size": len(record.text_content),
                "has_vector": record.vector is not None and len(record.vector) > 0,
                "has_raw_data": record.raw_data is not None,
            }
        )

    return json.dumps({"records": data, "count": len(data)}, indent=2)


def format_as_ids(records: list) -> str:
    """Format records as a simple list of IDs."""
    ids = [record.metadata.get("identifier", "N/A") for record in records]
    return "\n".join(ids)


def main():
    """Main entry point for list command."""
    parser = argparse.ArgumentParser(
        description='List documents in a ContextFrame dataset'
    )
    parser.add_argument('dataset', help='Path to the dataset')
    parser.add_argument(
        '--limit', type=int, default=50, help='Number of records to return'
    )
    parser.add_argument(
        '--filter', dest='filter_expr', help='Lance SQL filter expression'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json', 'ids'],
        default='table',
        help='Output format',
    )

    args = parser.parse_args()

    # Open the dataset
    try:
        dataset = FrameDataset.open(args.dataset)
    except Exception as e:
        print(f"Error opening dataset: {e}", file=sys.stderr)
        sys.exit(1)

    # Get records
    try:
        records = dataset.search(filter=args.filter_expr, limit=args.limit)
    except Exception as e:
        print(f"Error listing records: {e}", file=sys.stderr)
        sys.exit(1)

    # Format and output
    if args.format == 'json':
        output = format_as_json(records)
    elif args.format == 'ids':
        output = format_as_ids(records)
    else:  # table
        output = format_as_table(records)

    print(output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
