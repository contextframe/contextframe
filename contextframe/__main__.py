"""
Command-line entry point for the contextframe package.

This module allows the package to be run directly as a command-line script:
python -m contextframe
"""

import sys
from .cli import main


def main_entry():
    """Main entry point for the CLI."""
    # Extract arguments (excluding the script name)
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    try:
        # Call the main CLI function
        return_code = main(args)

        # Exit with the appropriate return code
        sys.exit(return_code)
    except Exception as e:
        # In case of unexpected errors, print and exit with error code
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main_entry()
