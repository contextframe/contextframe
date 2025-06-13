"""Batch processing functionality for document extraction."""

import asyncio
from .base import ExtractionResult, TextExtractor, registry
from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Union


class BatchExtractor:
    """Batch processor for extracting multiple documents efficiently."""
    
    def __init__(
        self,
        max_workers: int | None = None,
        use_process_pool: bool = False,
        progress_callback: Callable[[int, int, str], None] | None = None
    ):
        """Initialize the batch extractor.
        
        Args:
            max_workers: Maximum number of workers for parallel processing.
                        If None, uses CPU count.
            use_process_pool: Whether to use process pool (True) or thread pool (False).
                            Process pool is better for CPU-intensive extraction.
            progress_callback: Optional callback function that receives:
                              (current_index, total_count, current_file_path)
        """
        self.max_workers = max_workers
        self.use_process_pool = use_process_pool
        self.progress_callback = progress_callback
        self._extractors = {}
    
    def extract_files(
        self,
        file_paths: Iterable[str | Path],
        encoding: str = "utf-8",
        skip_errors: bool = True,
        **extractor_kwargs
    ) -> list[ExtractionResult]:
        """Extract content from multiple files.
        
        Args:
            file_paths: Iterable of file paths to process
            encoding: Default text encoding
            skip_errors: Whether to skip files that fail extraction
            **extractor_kwargs: Additional arguments passed to extractors
            
        Returns:
            List of ExtractionResult objects
        """
        file_paths = list(file_paths)
        total_count = len(file_paths)
        
        if self.use_process_pool:
            executor_class = ProcessPoolExecutor
        else:
            executor_class = ThreadPoolExecutor
        
        results = []
        
        with executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = []
            for i, file_path in enumerate(file_paths):
                future = executor.submit(
                    self._extract_single,
                    file_path,
                    encoding,
                    extractor_kwargs
                )
                futures.append((i, file_path, future))
            
            # Collect results as they complete
            for i, file_path, future in futures:
                if self.progress_callback:
                    self.progress_callback(i + 1, total_count, str(file_path))
                
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    if not skip_errors:
                        raise
                    # Create error result
                    error_result = ExtractionResult(
                        content="",
                        source=file_path,
                        error=f"Extraction failed: {str(e)}"
                    )
                    results.append(error_result)
        
        return results
    
    def extract_directory(
        self,
        directory: str | Path,
        pattern: str = "*",
        recursive: bool = True,
        encoding: str = "utf-8",
        skip_errors: bool = True,
        **extractor_kwargs
    ) -> list[ExtractionResult]:
        """Extract content from all matching files in a directory.
        
        Args:
            directory: Directory path to scan
            pattern: Glob pattern for file matching (e.g., "*.md", "*.json")
            recursive: Whether to scan subdirectories
            encoding: Default text encoding
            skip_errors: Whether to skip files that fail extraction
            **extractor_kwargs: Additional arguments passed to extractors
            
        Returns:
            List of ExtractionResult objects
        """
        directory = Path(directory)
        
        if recursive:
            file_paths = directory.rglob(pattern)
        else:
            file_paths = directory.glob(pattern)
        
        # Filter to only files (not directories)
        file_paths = [p for p in file_paths if p.is_file()]
        
        return self.extract_files(
            file_paths,
            encoding=encoding,
            skip_errors=skip_errors,
            **extractor_kwargs
        )
    
    async def extract_files_async(
        self,
        file_paths: Iterable[str | Path],
        encoding: str = "utf-8",
        skip_errors: bool = True,
        **extractor_kwargs
    ) -> list[ExtractionResult]:
        """Asynchronously extract content from multiple files.
        
        Args:
            file_paths: Iterable of file paths to process
            encoding: Default text encoding
            skip_errors: Whether to skip files that fail extraction
            **extractor_kwargs: Additional arguments passed to extractors
            
        Returns:
            List of ExtractionResult objects
        """
        file_paths = list(file_paths)
        total_count = len(file_paths)
        
        # Create tasks
        tasks = []
        for i, file_path in enumerate(file_paths):
            task = self._extract_single_async(
                i,
                total_count,
                file_path,
                encoding,
                extractor_kwargs
            )
            tasks.append(task)
        
        # Run tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=skip_errors)
        
        # Process results
        final_results = []
        for file_path, result in zip(file_paths, results, strict=False):
            if isinstance(result, Exception):
                if not skip_errors:
                    raise result
                # Create error result
                error_result = ExtractionResult(
                    content="",
                    source=file_path,
                    error=f"Extraction failed: {str(result)}"
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        return final_results
    
    def _extract_single(
        self,
        file_path: str | Path,
        encoding: str,
        extractor_kwargs: dict
    ) -> ExtractionResult:
        """Extract a single file."""
        # Find appropriate extractor
        extractor = registry.find_extractor(file_path)
        
        if not extractor:
            return ExtractionResult(
                content="",
                source=file_path,
                error=f"No extractor found for file: {file_path}"
            )
        
        # Extract content
        return extractor.extract(file_path, encoding=encoding, **extractor_kwargs)
    
    async def _extract_single_async(
        self,
        index: int,
        total: int,
        file_path: str | Path,
        encoding: str,
        extractor_kwargs: dict
    ) -> ExtractionResult:
        """Extract a single file asynchronously."""
        if self.progress_callback:
            self.progress_callback(index + 1, total, str(file_path))
        
        # Run extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._extract_single,
            file_path,
            encoding,
            extractor_kwargs
        )
    
    def extract_with_custom_extractors(
        self,
        file_paths: Iterable[str | Path],
        extractors: dict[str, TextExtractor],
        encoding: str = "utf-8",
        skip_errors: bool = True,
        **extractor_kwargs
    ) -> list[ExtractionResult]:
        """Extract files using custom extractors for specific extensions.
        
        Args:
            file_paths: Iterable of file paths to process
            extractors: Dictionary mapping file extensions to extractor instances
                       e.g., {".txt": MyCustomTextExtractor()}
            encoding: Default text encoding
            skip_errors: Whether to skip files that fail extraction
            **extractor_kwargs: Additional arguments passed to extractors
            
        Returns:
            List of ExtractionResult objects
        """
        results = []
        file_paths = list(file_paths)
        total_count = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            if self.progress_callback:
                self.progress_callback(i + 1, total_count, str(file_path))
            
            path = Path(file_path)
            
            # Find extractor by extension
            extractor = extractors.get(path.suffix.lower())
            if not extractor:
                # Fall back to registry
                extractor = registry.find_extractor(file_path)
            
            if not extractor:
                if not skip_errors:
                    raise ValueError(f"No extractor found for file: {file_path}")
                error_result = ExtractionResult(
                    content="",
                    source=file_path,
                    error=f"No extractor found for file: {file_path}"
                )
                results.append(error_result)
                continue
            
            try:
                result = extractor.extract(file_path, encoding=encoding, **extractor_kwargs)
                results.append(result)
            except Exception as e:
                if not skip_errors:
                    raise
                error_result = ExtractionResult(
                    content="",
                    source=file_path,
                    error=f"Extraction failed: {str(e)}"
                )
                results.append(error_result)
        
        return results