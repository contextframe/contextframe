"""
Command-line interface for ContextFrame / Lance dataset utilities.

This module offers a rich CLI for inspecting, creating and manipulating
Lance datasets that store **Frame** rows (metadata, content and vector
embeddings).
"""

import argparse
import json
import os
import sys

# Use direct imports from local modules
from .frame import FrameRecord

# from .versioning import get_version_manager
from pathlib import Path
from typing import Optional

# Import command modules


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.

    Returns:
        An ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        description="ContextFrame command-line tools", prog="contextframe"
    )

    # Add version argument
    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Info command
    info_parser = subparsers.add_parser(
        "info", help="Display information about a Lance dataset (.lance dir)"
    )
    info_parser.add_argument("file", help="Dataset path (.lance directory)")
    info_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )

    # Create command
    create_parser = subparsers.add_parser(
        "create", help="Create a new Lance dataset (.lance dir)"
    )
    create_parser.add_argument("title", help="Document title")
    create_parser.add_argument("--output", "-o", required=True, help="Output file path")
    create_parser.add_argument("--author", help="Document author")
    create_parser.add_argument("--tags", help="Comma-separated list of tags")
    create_parser.add_argument("--content", help="Document content (use - for stdin)")
    create_parser.add_argument(
        "--content-file", help="File containing document content"
    )

    # Versioning commands
    # version_parser = subparsers.add_parser("version", help="Work with document versions")
    # version_subparsers = version_parser.add_subparsers(dest="version_command", help="Version command")
    #
    # # Create version
    # version_create_parser = version_subparsers.add_parser("create", help="Create a new version of a document")
    # version_create_parser.add_argument("file", help="Document file path")
    # version_create_parser.add_argument("--version", "-v", help="Version number (e.g., 1.0.0)")
    # version_create_parser.add_argument("--author", "-a", help="Author of this version")
    # version_create_parser.add_argument("--description", "-d", help="Description of changes")
    # version_create_parser.add_argument("--bump", choices=["major", "minor", "patch"],
    #                                 default="patch", help="Bump version (if --version not specified)")
    #
    # # List versions
    # version_list_parser = version_subparsers.add_parser("list", help="List all versions of a document")
    # version_list_parser.add_argument("file", help="Document file path")
    # version_list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    #
    # # Show version
    # version_show_parser = version_subparsers.add_parser("show", help="Show a specific version of a document")
    # version_show_parser.add_argument("file", help="Document file path")
    # version_show_parser.add_argument("version", help="Version number to show")
    # version_show_parser.add_argument("--metadata-only", action="store_true", help="Show only metadata")
    # version_show_parser.add_argument("--content-only", action="store_true", help="Show only content")
    #
    # # Compare versions
    # version_compare_parser = version_subparsers.add_parser("compare", help="Compare two versions of a document")
    # version_compare_parser.add_argument("file", help="Document file path")
    # version_compare_parser.add_argument("version1", help="First version to compare")
    # version_compare_parser.add_argument("version2", help="Second version to compare")
    # version_compare_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    #
    # # Rollback version
    # version_rollback_parser = version_subparsers.add_parser("rollback", help="Roll back to a previous version")
    # version_rollback_parser.add_argument("file", help="Document file path")
    # version_rollback_parser.add_argument("version", help="Version to roll back to")
    # version_rollback_parser.add_argument("--no-backup", action="store_true", help="Don't create a backup before rollback")
    #
    # # Branching
    # branch_parser = version_subparsers.add_parser("branch", help="Create a branch of a document")
    # branch_parser.add_argument("file", help="Document file path")
    # branch_parser.add_argument("name", help="Branch name")
    # branch_parser.add_argument("--base-version", help="Base version for the branch (defaults to latest)")
    #
    # # Merging
    # merge_parser = version_subparsers.add_parser("merge", help="Merge a branch into another document")
    # merge_parser.add_argument("branch", help="Branch document file path")
    # merge_parser.add_argument("target", help="Target document file path")
    # merge_parser.add_argument("--no-backup", action="store_true", help="Don't create a backup before merge")
    #
    # # Conflict resolution commands
    # conflict_parser = subparsers.add_parser("conflicts", help="Work with document conflicts")
    # conflict_subparsers = conflict_parser.add_subparsers(dest="conflict_command", help="Conflict command")
    #
    # # Check for conflicts
    # check_parser = conflict_subparsers.add_parser("check", help="Check for conflicts between two documents")
    # check_parser.add_argument("local", help="Path to local document")
    # check_parser.add_argument("remote", help="Path to remote document")
    # check_parser.add_argument("--base-version", help="Base version for comparison (optional)")
    # check_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    #
    # # Auto-merge
    # merge_parser = conflict_subparsers.add_parser("merge", help="Automatically merge changes from two documents")
    # merge_parser.add_argument("local", help="Path to local document")
    # merge_parser.add_argument("remote", help="Path to remote document")
    # merge_parser.add_argument("--output", "-o", help="Output path for merged document (default: overwrite local)")
    # merge_parser.add_argument("--base-version", help="Base version for comparison (optional)")
    #
    # # Create conflict resolution file
    # resolve_parser = conflict_subparsers.add_parser("create-resolution-file", help="Create a file for manual conflict resolution")
    # resolve_parser.add_argument("local", help="Path to local document")
    # resolve_parser.add_argument("remote", help="Path to remote document")
    # resolve_parser.add_argument("--output", "-o", required=True, help="Output path for resolution file")
    # resolve_parser.add_argument("--base-version", help="Base version for comparison (optional)")
    #
    # # Apply resolved conflicts
    # apply_parser = conflict_subparsers.add_parser("apply-resolution", help="Apply a manually resolved conflict file")
    # apply_parser.add_argument("resolution_file", help="Path to the resolved conflict file")
    # apply_parser.add_argument("--output", "-o", required=True, help="Output path for resolved document")
    #
    # # Check for concurrent modifications
    # concurrent_parser = conflict_subparsers.add_parser("check-concurrent", help="Check if a document has been modified concurrently")
    # concurrent_parser.add_argument("file", help="Path to the document")
    # concurrent_parser.add_argument("--expected-version", help="Expected version (optional)")

    return parser


def main(args: list[str] | None = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command-line arguments (if None, uses sys.argv)

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Handle version flag before checking for command
    if hasattr(parsed_args, 'version') and parsed_args.version:
        from . import __version__

        print(f"ContextFrame version {__version__}")
        return 0

    if not parsed_args.command:
        parser.print_help()
        return 1

    try:
        if parsed_args.command == "info":
            return _handle_info(parsed_args)
        elif parsed_args.command == "create":
            return _handle_create(parsed_args)
        # elif parsed_args.command == "version":
        #     return _handle_version(parsed_args)
        # elif parsed_args.command == "conflicts":
        #     return _handle_conflicts(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_info(args):
    """Handle the info command."""
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    try:
        # Load the document
        doc = FrameRecord.from_file(file_path)

        if args.json:
            # Output as JSON
            info = {
                "title": doc.title,
                "author": doc.author,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at,
                "path": str(doc.path),
                "tags": doc.tags,
                "metadata": doc.metadata,
            }
            print(json.dumps(info, indent=2))
        else:
            # Output as text
            print(f"Title: {doc.title}")
            if doc.author:
                print(f"Author: {doc.author}")
            if doc.created_at:
                print(f"Created: {doc.created_at}")
            if doc.updated_at:
                print(f"Updated: {doc.updated_at}")
            if doc.tags:
                print(f"Tags: {', '.join(doc.tags)}")

            # Display metadata count
            meta_count = len(doc.metadata)
            print(f"Metadata: {meta_count} fields")

            # Display content stats
            content_lines = doc.content.count("\n") + 1
            content_words = len(doc.content.split())
            print(f"Content: {content_lines} lines, {content_words} words")

        return 0
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        return 1


def _handle_create(args):
    """Handle the create command."""
    # Parse tags
    tag_list = None
    if args.tags:
        tag_list = [tag.strip() for tag in args.tags.split(",")]

    # Get content
    content = ""
    if args.content == "-":
        # Read from stdin
        content = sys.stdin.read()
    elif args.content:
        content = args.content
    elif args.content_file:
        with open(args.content_file, encoding="utf-8") as f:
            content = f.read()

    try:
        # Create document
        doc = FrameRecord.create(
            title=args.title, content=content, author=args.author, tags=tag_list
        )

        # Save document
        doc.save(args.output)
        print(f"Document created: {args.output}")
        return 0
    except Exception as e:
        print(f"Error creating document: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
