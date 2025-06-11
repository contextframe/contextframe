import pyarrow as pa
from typing import Optional

# Embedding dimension can be configured externally
DEFAULT_EMBED_DIM = 1536  # Change if you use a different encoder

# ---------------------------------------------------------------------------
# Helper enum values (kept in Python for convenience)
# ---------------------------------------------------------------------------


class RecordType:
    """Enumerated record_type values used in the canonical schema."""

    DOCUMENT = "document"
    COLLECTION_HEADER = "collection_header"
    DATASET_HEADER = "dataset_header"
    FRAMESET = "frameset"

    @classmethod
    def choices(cls):  # noqa: D401
        return [cls.DOCUMENT, cls.COLLECTION_HEADER, cls.DATASET_HEADER, cls.FRAMESET]


# ---------------------------------------------------------------------------
# Common MIME Types (Optional Raw Data)
# ---------------------------------------------------------------------------


class MimeTypes:
    """Standardized MIME types for the optional raw_data field."""

    # Images
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_GIF = "image/gif"
    IMAGE_WEBP = "image/webp"
    IMAGE_SVG = "image/svg+xml"
    IMAGE_TIFF = "image/tiff"
    # Audio
    AUDIO_WAV = "audio/wav"
    AUDIO_MPEG = "audio/mpeg"  # MP3
    AUDIO_OGG = "audio/ogg"
    AUDIO_WEBM = "audio/webm"
    AUDIO_FLAC = "audio/flac"
    AUDIO_AAC = "audio/aac"
    # Video
    VIDEO_MP4 = "video/mp4"
    VIDEO_WEBM = "video/webm"
    # Documents
    APP_PDF = "application/pdf"
    TEXT_PLAIN = "text/plain"
    TEXT_MARKDOWN = "text/markdown"
    TEXT_HTML = "text/html"
    APP_JSON = "application/json"
    TEXT_CSV = "text/csv"
    TEXT_XML = "text/xml"
    APP_ZIP = "application/zip"
    # Generic Binary
    APP_OCTET_STREAM = "application/octet-stream"

    @classmethod
    def common_image_types(cls):
        return [
            cls.IMAGE_JPEG,
            cls.IMAGE_PNG,
            cls.IMAGE_GIF,
            cls.IMAGE_WEBP,
            cls.IMAGE_SVG,
            cls.IMAGE_TIFF,
        ]

    @classmethod
    def common_audio_types(cls):
        return [
            cls.AUDIO_WAV,
            cls.AUDIO_MPEG,
            cls.AUDIO_OGG,
            cls.AUDIO_WEBM,
            cls.AUDIO_FLAC,
            cls.AUDIO_AAC,
        ]


# ---------------------------------------------------------------------------
# Schema Builder
# ---------------------------------------------------------------------------


def build_schema(embed_dim: int = DEFAULT_EMBED_DIM) -> pa.Schema:  # noqa: D401
    """Return the canonical Arrow schema for a Frame record.

    A *Frame* represents one logical document row stored inside a Lance
    dataset.  Each column name / type corresponds to the metadata fields that
    previously lived in an .mdp front-matter.  See the MDP specification for
    semantics.

    Parameters
    ----------
    embed_dim:
        Size of the floating-point embedding vector.
    """
    # Relationship struct mirrors the JSON schema definition where exactly one
    # of the identifier fields (id | uri | path | cid) must be present.
    relationship_struct = pa.struct(
        [
            pa.field("type", pa.string(), nullable=False),
            pa.field("id", pa.string()),
            pa.field("uri", pa.string()),
            pa.field("path", pa.string()),
            pa.field("cid", pa.string()),
            pa.field("title", pa.string()),
            pa.field("description", pa.string()),
        ]
    )

    fields = [
        pa.field("uuid", pa.string(), nullable=False),
        pa.field("text_content", pa.string()),
        pa.field(
            "vector",
            pa.list_(pa.float32(), list_size=embed_dim),
        ),
        pa.field("title", pa.string(), nullable=False),
        pa.field("version", pa.string()),
        pa.field("context", pa.string()),
        pa.field("uri", pa.string()),
        pa.field("local_path", pa.string()),
        pa.field("cid", pa.string()),
        pa.field("collection", pa.string()),
        pa.field("collection_id", pa.string()),
        pa.field("collection_id_type", pa.string()),  # uuid|uri|cid|string
        pa.field("position", pa.int32()),
        pa.field("author", pa.string()),
        pa.field("contributors", pa.list_(pa.string())),
        # Store dates as ISO strings to stay compatible with the JSON schema
        # validation pattern (YYYY-MM-DD).  Using string instead of timestamp
        # avoids implicit conversion issues between Arrow and JSON.
        pa.field("created_at", pa.string()),
        pa.field("updated_at", pa.string()),
        pa.field("tags", pa.list_(pa.string())),
        pa.field("status", pa.string()),
        pa.field("source_file", pa.string()),
        pa.field("source_type", pa.string()),
        pa.field("source_url", pa.string()),
        pa.field("relationships", pa.list_(relationship_struct)),
        pa.field(
            "custom_metadata",
            pa.list_(
                pa.struct(
                    [pa.field("key", pa.string()), pa.field("value", pa.string())]
                )
            ),
        ),
        pa.field("record_type", pa.string()),
        # Optional fields for raw multimodal data
        pa.field("raw_data_type", pa.string()),  # MIME type (e.g., "image/jpeg")
        # Large binary column flagged as blob for efficient lazy loading
        pa.field(
            "raw_data",
            pa.large_binary(),
            metadata={"lance-encoding:blob": "true"},
        ),  # Raw byte content stored as Lance Blob
    ]

    return pa.schema(fields)


def get_schema(*, embed_dim: int | None = None) -> pa.Schema:  # noqa: D401
    """Public helper returning the canonical schema.

    Lazily creates and caches the schema object.
    """
    global _CACHED_SCHEMA  # pylint: disable=global-statement
    dim = embed_dim or DEFAULT_EMBED_DIM
    try:
        cached = _CACHED_SCHEMA[dim]
    except (NameError, KeyError):
        if "_CACHED_SCHEMA" not in globals():
            globals()["_CACHED_SCHEMA"] = {}
        _CACHED_SCHEMA[dim] = build_schema(dim)
        cached = _CACHED_SCHEMA[dim]
    return cached
