#!/usr/bin/env python3
"""Helper script to create a new ContextFrame dataset."""

import sys
from pathlib import Path
from contextframe.frame import FrameDataset


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m contextframe.scripts.create_dataset <dataset_path>")
        sys.exit(1)
    
    dataset_path = Path(sys.argv[1])
    
    try:
        # Create the dataset
        dataset = FrameDataset.create(dataset_path)
        print(f"Created dataset at: {dataset_path}")
    except Exception as e:
        print(f"Error creating dataset: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()