"""Export format definitions and constants."""

from enum import Enum


class ExportFormat(Enum):
    """Supported export formats for FrameSets."""

    MARKDOWN = "markdown"  # .md - Human-readable with YAML frontmatter
    TEXT = "text"  # .txt - Plain text, simple format
    JSON = "json"  # .json - Structured data interchange
    PARQUET = "parquet"  # .parquet - Columnar format for data analysis
    CSV = "csv"  # .csv - Tabular data for spreadsheets/analysis

    @classmethod
    def choices(cls) -> list[str]:
        """Return list of format choices."""
        return [fmt.value for fmt in cls]
