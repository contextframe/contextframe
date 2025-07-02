"""Frame abstraction backed by Lance datasets.

A *Frame* corresponds to a single row stored inside a Lance dataset that
captures all metadata and text for a logical document plus its vector
embedding.  `FrameRecord` represents that in memory, while `FrameDataset`
wraps the `lance.dataset.Dataset` object providing higher-level helpers that
mimic the public surface for documents (create, add, search,
version access, etc.).
"""

from __future__ import annotations

import datetime as _dt
import numpy as np
import pyarrow as pa
import uuid as _uuid
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Optional, Union

try:
    import lance
    from lance.dataset import write_dataset
except ModuleNotFoundError as exc:
    raise ImportError(
        "lance is required for contextframe.frame. Please install contextframe with the 'lance' extra."
    ) from exc

from .exceptions import ValidationError
from .helpers.metadata_utils import add_relationship_to_metadata, create_relationship
from .schema import get_schema
from .schema.contextframe_schema import DEFAULT_EMBED_DIM
from .schema.validation import validate_metadata_with_schema

# ---------------------------------------------------------------------------
# FrameRecord
# ---------------------------------------------------------------------------


class FrameRecord:
    """In-memory representation of one Frame row.

    Attributes
    ----------
    text_content : str
        The primary textual content of the frame.
    metadata : dict[str, Any]
        A dictionary containing metadata for the frame.
    vector : np.ndarray
        The vector embedding for the frame.
    embed_dim : int
        The dimension of the embedding vector.
    raw_data : bytes | None
        Raw binary data associated with the frame (e.g., image bytes).
    raw_data_type : str | None
        The MIME type for `raw_data`.
    path : Path | None
        The file system path to the Lance dataset (.lance directory) this record
        is associated with. It is typically set when a record is loaded from
        or saved to a dataset. It can be used as the default location for
        a subsequent `save()` operation if no explicit path is provided.

    """

    def __init__(
        self,
        text_content: str,
        metadata: dict[str, Any],
        *,
        vector: np.ndarray | None = None,
        embed_dim: int = DEFAULT_EMBED_DIM,
        raw_data: bytes | None = None,
        raw_data_type: str | None = None,
        dataset_path: Path | None = None,
    ) -> None:
        """
        Initialize a FrameRecord.

        Parameters
        ----------
        text_content : str
            The primary textual content of the frame.
        metadata : dict[str, Any]
            A dictionary containing metadata for the frame.
            A copy of this dictionary will be stored.
        vector : np.ndarray | None, optional
            The vector embedding for the frame. If None, a zero vector of
            `embed_dim` will be created. Defaults to None.
        embed_dim : int, optional
            The dimension of the embedding vector.
            Defaults to `DEFAULT_EMBED_DIM`.
        raw_data : bytes | None, optional
            Raw binary data associated with the frame (e.g., image bytes).
            If provided, `raw_data_type` must also be provided. Defaults to None.
        raw_data_type : str | None, optional
            The MIME type for `raw_data`. Required if `raw_data` is provided.
            Defaults to None.
        dataset_path : Path | None, optional
            The path to the Lance dataset this record is associated with.
            This is often set when loading a record or after saving it.
            Defaults to None.

        Raises
        ------
        ValueError
            If `raw_data` is provided without `raw_data_type` or vice-versa.
            If `vector` is provided and its length does not match `embed_dim`.
        """
        self.text_content = text_content
        # Ensure we have a copy so callers cannot mutate unexpectedly
        self.metadata: dict[str, Any] = dict(metadata)
        self.embed_dim = embed_dim
        self.path = dataset_path  # May be None, kept for backward compat

        # Handle raw data fields + validation
        if (raw_data is not None and raw_data_type is None) or (
            raw_data is None and raw_data_type is not None
        ):
            raise ValueError(
                "Both 'raw_data' and 'raw_data_type' must be provided together, or both must be None."
            )
        self.raw_data = raw_data
        self.raw_data_type = raw_data_type

        if vector is None:
            # Allow creation without embedding; caller must fill later
            self.vector = np.zeros(embed_dim, dtype=np.float32)
        else:
            if len(vector) != embed_dim:
                raise ValueError(
                    f"Vector length {len(vector)} != embedding dimension {embed_dim}"
                )
            self.vector = vector.astype(np.float32)

        # Default/auto fields
        self.metadata.setdefault("uuid", str(_uuid.uuid4()))
        # Convert dates; store as ISO strings (FrameDataset will convert to
        # timestamps as needed)
        now_iso = _dt.date.today().isoformat()
        self.metadata.setdefault("created_at", now_iso)
        self.metadata.setdefault("updated_at", now_iso)

    # ---------------------------------------------------------------------
    # Arrow conversion helpers
    # ---------------------------------------------------------------------

    def _arrowify_scalar(self, field_name: str, value: Any, pa_type: pa.DataType):
        """Return a PyArrow array of length 1 for given scalar value."""
        return pa.array([value], type=pa_type)

    def to_table(self) -> pa.Table:
        """Return a 1-row Arrow Table matching the canonical schema."""
        schema = get_schema(embed_dim=self.embed_dim)
        arrays: dict[str, pa.Array] = {}

        # Mapping between schema fields and metadata / attributes
        meta = self.metadata
        for field in schema:
            name = field.name
            if name == "text_content":
                arrays[name] = self._arrowify_scalar(
                    name, self.text_content, pa.string()
                )
            elif name == "vector":
                arrays[name] = pa.FixedSizeListArray.from_arrays(
                    pa.array(self.vector),  # type: ignore[arg-type]
                    field.type.list_size,
                )
            elif name == "raw_data":
                arrays[name] = self._arrowify_scalar(
                    name, self.raw_data, pa.large_binary()
                )
            elif name == "raw_data_type":
                arrays[name] = self._arrowify_scalar(
                    name, self.raw_data_type, pa.string()
                )
            elif name == "contributors" and "contributors" in meta:
                arrays[name] = pa.array([meta["contributors"]], type=field.type)
            elif name == "tags" and "tags" in meta:
                arrays[name] = pa.array([meta["tags"]], type=field.type)
            elif name == "relationships" and "relationships" in meta:
                arrays[name] = pa.array([meta["relationships"]], type=field.type)
            elif name == "custom_metadata":
                # Convert dict to list of key-value structs for Lance compatibility
                custom_meta = meta.get("custom_metadata", {})
                if custom_meta:
                    kv_list = [{"key": k, "value": v} for k, v in custom_meta.items()]
                else:
                    kv_list = []
                arrays[name] = pa.array([kv_list], type=field.type)
            else:
                # Scalar fields directly from metadata or None
                arrays[name] = self._arrowify_scalar(name, meta.get(name), field.type)

        # Build table with schema
        return pa.Table.from_arrays(arrays.values(), schema=schema)

    # Convenience alias
    def to_arrow(self) -> pa.Table:
        """Return a 1-row Arrow Table matching the canonical schema."""
        return self.to_table()

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_arrow(
        cls, record_batch: pa.RecordBatch | pa.Table, dataset_path: Path | None = None
    ) -> FrameRecord:
        """Create a FrameRecord from a 1-row RecordBatch/Table."""
        if len(record_batch) != 1:
            raise ValueError("from_arrow expects exactly 1 row")
        tbl = record_batch.to_pydict()
        # Extract vector list<fixed_size_list<float32>> value
        vector_list = tbl["vector"][0]
        vector = np.array(vector_list, dtype=np.float32)
        text_content = tbl["text_content"][0]
        # Extract metadata, handling missing fields gracefully
        metadata: dict[str, Any] = {}
        for k, v in tbl.items():
            if k in {"text_content", "vector", "raw_data", "raw_data_type"}:
                continue
            # Handle list values (from pydict conversion)
            value = v[0] if isinstance(v, list) and len(v) > 0 else v
            # Don't include None values in metadata
            if value is not None:
                metadata[k] = value
        # Convert list of key-value structs back to dict
        if "custom_metadata" in metadata and metadata["custom_metadata"] is not None:
            kv_list = metadata["custom_metadata"]
            if kv_list:
                metadata["custom_metadata"] = {
                    item["key"]: item["value"] for item in kv_list
                }
            else:
                metadata["custom_metadata"] = {}
        else:
            metadata["custom_metadata"] = {}

        # Clean up relationships - remove None values from struct fields
        if "relationships" in metadata and metadata["relationships"]:
            cleaned_relationships = []
            for rel in metadata["relationships"]:
                # Only include non-None fields in the relationship
                cleaned_rel = {k: v for k, v in rel.items() if v is not None}
                cleaned_relationships.append(cleaned_rel)
            metadata["relationships"] = cleaned_relationships

        # Extract raw data fields if present
        # Handle case where raw_data might not be in the table (e.g., excluded from scan)
        if "raw_data" in tbl:
            raw_data = tbl.get("raw_data", [None])[0]
        else:
            raw_data = None

        if "raw_data_type" in tbl:
            raw_data_type = tbl.get("raw_data_type", [None])[0]
        else:
            raw_data_type = None
            
        # Ensure both are None if either is None (to satisfy FrameRecord validation)
        if raw_data is None or raw_data_type is None:
            raw_data = None
            raw_data_type = None

        # Determine embed_dim from the loaded vector
        current_embed_dim = (
            len(vector) if vector is not None and vector.ndim > 0 else DEFAULT_EMBED_DIM
        )

        return cls(
            text_content=text_content,
            metadata=metadata,
            vector=vector,
            embed_dim=current_embed_dim,  # Pass the determined embed_dim
            raw_data=raw_data,
            raw_data_type=raw_data_type,
            dataset_path=dataset_path,
        )

    # ------------------------------------------------------------------
    # Convenience factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        title: str,
        *,
        content: str = "",
        embed_dim: int = DEFAULT_EMBED_DIM,
        vector: np.ndarray | None = None,
        raw_data: bytes | None = None,
        raw_data_type: str | None = None,
        uuid: str | None = None,
        **metadata: Any,
    ) -> FrameRecord:
        """Create a new FrameRecord with common metadata fields.

        This is a user-friendly factory method for creating FrameRecord instances.
        It ensures the 'title' is set and provides clear parameters for common fields.

        Parameters
        ----------
        title:
            The document title. Stored in ``metadata['title']``.
        content:
            Raw content body for the document (plain text, markdown or any
            textual representation). No front-matter processing is done – all
            structured information must be supplied via *metadata*.
        embed_dim:
            Dimension of the embedding vector (default: ``DEFAULT_EMBED_DIM``).
        vector:
            Pre-computed embedding. If *None*, a zero-vector is stored and can
            be filled later.
        raw_data:
            Optional raw binary content (e.g., image bytes).
        raw_data_type:
            Optional MIME type for raw_data (required if raw_data is provided).
        uuid:
            Optional UUID for the record. If not provided, a new UUID will be
            generated automatically. Useful for testing or migration scenarios.
        **metadata:
            Additional key/value pairs to store in the document metadata.
            The 'title', 'raw_data', and 'raw_data_type' if passed through here
            will be overridden by the explicit parameters.
        """
        if "title" in metadata:
            # Allow if it's the same as the title argument, or warn, or just let it be overwritten
            # For now, let explicit param win.
            pass

        # Explicit parameters take precedence and are added to the metadata dict
        # which will be passed to the constructor.
        current_metadata = metadata.copy()  # Work with a copy
        current_metadata["title"] = title
        
        # Add UUID if provided
        if uuid is not None:
            current_metadata["uuid"] = uuid

        # The raw_data and raw_data_type are passed directly to the constructor,
        # not through the metadata dict for the constructor.
        # The earlier check for raw_data/raw_data_type in metadata.pop was removed
        # because they are now explicit params.

        return cls(
            text_content=content,
            metadata=current_metadata,  # Pass the processed metadata
            vector=vector,
            embed_dim=embed_dim,
            raw_data=raw_data,  # Pass explicit raw_data
            raw_data_type=raw_data_type,  # Pass explicit raw_data_type
            # dataset_path is not set at creation time by this factory.
        )

    # ------------------------------------------------------------------
    # Single-record dataset persistence
    # ------------------------------------------------------------------

    def save(
        self,
        path: Path | str | None = None,
        *,
        overwrite_dataset: bool = False,
        storage_options: dict | None = None,
    ) -> Path:
        """Persist this FrameRecord into a Lance dataset.

        The *path* must point to a directory ending with ``.lance``
        with the same stem). If the dataset does not yet exist it will be
        created automatically.  When *overwrite_dataset* is *True* and the
        directory exists, it will be **fully replaced** with a fresh, empty
        dataset before inserting this record.

        Parameters
        ----------
        path:
            Local or remote URI where the dataset should live.  If *None* and
            the record has been loaded from an existing dataset, that path is
            reused.
        overwrite_dataset:
            When *True* and *path* already contains a dataset it is deleted
            first (local file-system only).
        storage_options:
            Optional mapping forwarded to :pyclass:`FrameDataset.create` /
            :pyclass:`FrameDataset.open` for remote object-store
            configuration.
        """
        # Preserve remote URIs as *strings* because pathlib will mangle the
        # double slash (e.g. "s3://" → "s3:/").  We therefore keep both a
        # raw string variant and a local-Path variant for checks that only
        # make sense on the local file system.

        def _is_remote(uri: str) -> bool:
            return "://" in uri  # crude but sufficient (s3://, gs://, az://, ...)

        if path is not None:
            raw_uri = str(path)
        elif self.path is not None:
            raw_uri = str(self.path)
        else:
            raise ValueError(
                "No dataset path provided and FrameRecord has no existing path reference."
            )

        is_remote = _is_remote(raw_uri)

        # Only wrap in Path for local paths where OS checks make sense.
        dataset_path_obj: Path | None = None if is_remote else Path(raw_uri)

        dataset_path = dataset_path_obj if not is_remote else raw_uri

        # Suffix checks only apply to local Path objects.
        if (
            not is_remote and dataset_path_obj and dataset_path_obj.suffix != ".lance"
        ) or (is_remote and not raw_uri.endswith(".lance")):
            raise ValueError(
                f"Dataset path must point to a '.lance' directory. Received: {dataset_path}"
            )

        # Create or open dataset
        if (
            not is_remote
            and dataset_path_obj
            and dataset_path_obj.exists()
            and overwrite_dataset
        ):
            # Dangerously wipe the dataset directory before re-creating.
            import shutil

            shutil.rmtree(dataset_path_obj)

        if (
            not is_remote and dataset_path_obj and not dataset_path_obj.exists()
        ) or is_remote:
            ds = FrameDataset.create(
                raw_uri, embed_dim=self.embed_dim, storage_options=storage_options
            )
        else:
            ds = FrameDataset.open(raw_uri, storage_options=storage_options)

        ds.add(self)
        # Store the *original* URI/path for subsequent calls.
        self.path = Path(raw_uri) if not is_remote else raw_uri  # type: ignore[arg-type]

        return dataset_path

    @classmethod
    def from_file(cls, path: Path | str) -> FrameRecord:
        """Load a FrameRecord from a Lance dataset directory containing exactly one row."""
        dataset_path = Path(path)

        # Expect a .lance directory path only

        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        if not dataset_path.is_dir() or not dataset_path.name.endswith(".lance"):
            raise ValueError(
                "from_file expects a directory ending with '.lance' that represents a Lance dataset"
            )

        ds = FrameDataset.open(dataset_path)
        row_count = ds._native.count_rows()
        if row_count != 1:
            raise ValueError(
                "from_file only supports datasets with exactly one row. Found "
                f"{row_count} rows in {dataset_path}. Use from_dataset_row instead."
            )
        tbl = ds._native.to_table()
        batch = tbl.to_batches()[0]
        return cls.from_arrow(batch.slice(0, 1), dataset_path=dataset_path)

    # ------------------------------------------------------------------
    # New granular helpers
    # ------------------------------------------------------------------

    def write_to_dataset(
        self, dataset_path: str | Path, *, overwrite_dataset: bool = False
    ) -> None:
        """Alias for :py:meth:`save` to maintain naming symmetry with spec."""
        self.save(dataset_path, overwrite_dataset=overwrite_dataset)

    @classmethod
    def from_dataset_row(
        cls,
        dataset_path: str | Path,
        uuid: str,
    ) -> FrameRecord:
        """Load a specific row identified by *uuid* from a Lance dataset."""
        ds = FrameDataset.open(dataset_path)
        tbl = ds.scanner(filter=f"uuid = '{uuid}'").to_table()
        if tbl.num_rows != 1:
            raise ValueError(
                f"Expected exactly one row with uuid={uuid!r} in dataset {dataset_path}, "
                f"found {tbl.num_rows}."
            )
        return cls.from_arrow(tbl, dataset_path=Path(dataset_path))

    # ------------------------------------------------------------------
    # Property accessors for common metadata
    # ------------------------------------------------------------------

    # Textual content alias
    @property
    def content(self) -> str:
        """Get or set the textual content of the frame."""
        return self.text_content

    @content.setter
    def content(self, value: str) -> None:
        """Set the textual content of the frame."""
        self.text_content = value

    @property
    def title(self) -> str:
        """Get or set the title from metadata."""
        return self.metadata.get("title", "")

    @title.setter
    def title(self, value: str) -> None:
        """Set the title in metadata."""
        self.metadata["title"] = value

    @property
    def author(self) -> str | None:
        """Get or set the author from metadata."""
        return self.metadata.get("author")

    @author.setter
    def author(self, value: str | None) -> None:
        """Set the author in metadata."""
        if value is None:
            self.metadata.pop("author", None)
        else:
            self.metadata["author"] = value

    @property
    def created_at(self) -> str | None:
        """Get the creation timestamp from metadata."""
        return self.metadata.get("created_at")

    @property
    def updated_at(self) -> str | None:
        """Get the update timestamp from metadata."""
        return self.metadata.get("updated_at")

    @property
    def tags(self) -> list[str] | None:
        """Get or set the tags from metadata."""
        return self.metadata.get("tags")

    @tags.setter
    def tags(self, value: list[str] | None) -> None:
        """Set the tags in metadata."""
        if value is None:
            self.metadata.pop("tags", None)
        else:
            self.metadata["tags"] = value

    # ------------------------------------------------------------------
    # Relationship helpers
    # ------------------------------------------------------------------

    def add_relationship(
        self,
        reference: str | FrameRecord,
        *,
        relationship_type: str = "related",
        title: str | None = None,
        description: str | None = None,
    ) -> None:
        """Add a relationship entry to this record's metadata.

        This convenience method uses `contextframe.create_relationship` and
        `contextframe.add_relationship_to_metadata` to build and append a
        relationship structure to the 'relationships' list in this record's
        metadata.
        """
        if isinstance(reference, FrameRecord):
            # Use UUID reference when passing a full document object.
            rel = create_relationship(
                reference.uuid,
                rel_type=relationship_type,
                title=title or reference.title,
                description=description,
            )
        else:
            # Treat *reference* as a path or identifier string
            rel = create_relationship(
                reference,
                rel_type=relationship_type,
                title=title,
                description=description,
            )
        add_relationship_to_metadata(self.metadata, rel)

    # ------------------------------------------------------------------
    # Convenience getters
    # ------------------------------------------------------------------

    @property
    def uuid(self) -> str:
        """Get the UUID from metadata."""
        return self.metadata["uuid"]


# ---------------------------------------------------------------------------
# FrameDataset wrapper
# ---------------------------------------------------------------------------


class FrameDataset:
    """High-level wrapper around a Lance dataset storing Frames."""

    def __init__(self, dataset: lance.LanceDataset) -> None:
        """Initialize a FrameDataset with a Lance dataset."""
        self._dataset = dataset
        self._non_blob_columns = self._get_non_blob_columns()

    def _get_non_blob_columns(self) -> list[str] | None:
        """Get list of columns that are not blob-encoded.

        Lance doesn't support scanning blob columns directly, so we need
        to exclude them from projections when using filters.
        """
        schema = self._dataset.schema
        non_blob_cols = []
        has_blob = False

        for field in schema:
            if field.metadata and field.metadata.get(b"lance-encoding:blob") == b"true":
                has_blob = True
            else:
                non_blob_cols.append(field.name)

        # Return None if there are no blob columns (so scanner uses default projection)
        return non_blob_cols if has_blob else None

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        path: str | Path,
        *,
        embed_dim: int = DEFAULT_EMBED_DIM,
        overwrite: bool = False,
        storage_options: dict | None = None,
    ) -> FrameDataset:
        """Create a new, empty Lance dataset at *path*.

        Parameters
        ----------
        path:
            Local or remote URI to the dataset directory. When the URI
            starts with ``s3://``, ``gs://`` or ``az://`` Lance will use the
            corresponding object-store backend.
        embed_dim:
            Dimensionality of the embedding vector column.
        overwrite:
            If *True* and the destination already exists it is **replaced**.
        storage_options:
            Optional mapping with object-store configuration forwarded to
            Lance.  See the `Lance object-store docs <https://lancedb.github.io/lance/object_store.html>`_
            for the complete list of keys.  Ignored for local file-system
            paths.
        """
        # Avoid pathlib for remote URIs because it mangles double slashes.
        raw_uri = str(path)
        is_remote = "://" in raw_uri

        schema = get_schema(embed_dim=embed_dim)

        if not is_remote and Path(raw_uri).exists() and not overwrite:
            raise FileExistsError(
                f"Dataset already exists at {path}. Pass overwrite=True to recreate."
            )
        # Create empty arrays matching the schema
        empty_arrays = [pa.array([], type=field.type) for field in schema]
        tbl = pa.Table.from_arrays(empty_arrays, schema=schema)
        # `write_dataset` will create or overwrite based on directory state.
        # We wiped any existing dir in caller, so simply write.
        if storage_options is None:
            ds = write_dataset(tbl, raw_uri, schema=schema)
        else:
            ds = write_dataset(
                tbl, raw_uri, schema=schema, storage_options=storage_options
            )
        return cls(ds)

    @classmethod
    def open(
        cls,
        path: str | Path,
        *,
        version: int | None = None,
        storage_options: dict | None = None,
    ) -> FrameDataset:
        """Open an existing Lance dataset.

        Parameters
        ----------
        path:
            Local or remote URI to the dataset directory. For remote object
            stores, use the appropriate URI scheme (e.g. ``s3://``).
        version:
            Optional dataset version to open.
        storage_options:
            A mapping of object store configuration parameters forwarded to
            Lance. See the `Lance object-store docs <https://lancedb.github.io/lance/object_store.html>`_
            for the full list of supported keys.
        """
        raw_uri = str(path)
        from lance.dataset import LanceDataset

        if storage_options is None:
            ds = LanceDataset(raw_uri, version=version)
        else:
            ds = LanceDataset(raw_uri, version=version, storage_options=storage_options)
        return cls(ds)

    # ------------------------------------------------------------------
    # Data modification helpers
    # ------------------------------------------------------------------

    def add(self, record: FrameRecord) -> None:
        """Append a single FrameRecord to the dataset."""
        ok, errs = validate_metadata_with_schema(record.metadata)
        if not ok:
            raise ValidationError("Invalid metadata", errors=errs)

        # Ensure record_type defaults to 'document' if not provided
        record.metadata.setdefault("record_type", "document")

        tbl = record.to_table()
        self._dataset.insert(tbl, mode="append")

    def add_many(self, records: Iterable[FrameRecord]) -> None:
        """Append multiple FrameRecords to the dataset efficiently.

        This method validates each record's metadata before attempting to add
        any of them. If any record is invalid, a ValueError is raised.
        All records are combined into a single PyArrow Table before insertion
        for better performance compared to adding one by one.

        Parameters
        ----------
        records : Iterable[FrameRecord]
            An iterable of FrameRecord instances to add to the dataset.

        Raises
        ------
        ValueError
            If metadata for any of the records is invalid according to the schema.
        """
        tbls = []
        for rec in records:
            ok, errs = validate_metadata_with_schema(rec.metadata)
            if not ok:
                # Add context about which record failed
                error_msg = f"Invalid metadata in record '{rec.title}' (UUID: {rec.uuid})"
                raise ValidationError(error_msg, errors=errs)
            tbls.append(rec.to_table())
        if not tbls:
            return
        combined = pa.concat_tables(tbls)
        self._dataset.insert(combined, mode="append")

    def merge(self, table: pa.Table, *, on: str = "uuid") -> None:
        """Merge additional columns using Lance merge."""
        self._dataset.merge(table, on)

    def delete_record(self, uuid: str) -> int:
        """Delete a single record identified by *uuid*.

        Parameters
        ----------
        uuid:
            The universally‐unique identifier of the record to delete.

        Returns
        -------
        int
            The number of rows deleted (``0`` if no matching record was found,
            ``1`` in the expected successful case).
        """
        # Delegate to Lance. Note: Lance delete returns None, not a count
        # We need to count before and after to determine how many were deleted
        count_before = self._dataset.count_rows()
        self._dataset.delete(f"uuid = '{uuid}'")
        count_after = self._dataset.count_rows()
        return count_before - count_after

    def update_record(self, record: FrameRecord) -> None:
        """Update an existing record in-place.

        The update is performed as a *delete → add* cycle which guarantees a
        clean replacement of the existing row while re-using the high-level
        :py:meth:`add` helper for validation and insertion.

        Parameters
        ----------
        record:
            A fully-populated :class:`FrameRecord` instance whose ``uuid`` must
            already exist in the dataset.

        Raises
        ------
        ValueError
            If the metadata on *record* is not valid, if the record does not
            exist, or if multiple records share the same UUID (data integrity
            violation).
        """
        # First validate the incoming metadata so we fail fast before touching
        # the dataset.
        ok, errs = validate_metadata_with_schema(record.metadata)
        if not ok:
            error_msg = f"Cannot update record '{record.title}' (UUID: {record.uuid})"
            raise ValidationError(error_msg, errors=errs)

        # Remove the existing record and sanity-check the outcome.
        delete_count = self.delete_record(record.uuid)
        if delete_count == 0:
            raise ValueError(
                f"No record found with uuid={record.uuid!r} – cannot update."
            )
        if delete_count > 1:
            raise ValueError(
                f"Integrity error: multiple ({delete_count}) records deleted for uuid={record.uuid!r}."
            )

        # Re-insert the (updated) record.  This will run validation once more
        # inside :py:meth:`add` but that is acceptable and keeps all insert
        # logic centralised in one place.
        self.add(record)

    def upsert_record(self, record: FrameRecord) -> None:
        """Insert *record* or replace an existing one with the same UUID.

        The helper combines *update* and *create* semantics in a single call.
        If a row with the same ``uuid`` already exists it is deleted first and
        then replaced by the provided record.  If no matching row exists the
        record is simply inserted.

        Parameters
        ----------
        record:
            The :class:`FrameRecord` instance to persist.

        Raises
        ------
        ValueError
            If the metadata on *record* fails schema validation.
        """
        ok, errs = validate_metadata_with_schema(record.metadata)
        if not ok:
            error_msg = f"Cannot upsert record '{record.title}' (UUID: {record.uuid})"
            raise ValidationError(error_msg, errors=errs)

        # Attempt to remove any existing row(s).  We intentionally ignore the
        # returned count here because *upsert* semantics do not care whether
        # a previous record was present.
        self.delete_record(record.uuid)

        # Insert the (new or replacement) record.
        self.add(record)

    def enrich(
        self,
        enrichments: dict[str, str | dict[str, Any]],
        filter: str | None = None,
        skip_existing: bool = True,
        batch_size: int = 10,
        show_progress: bool = True,
        model: str = "gpt-4o-mini",
        **enricher_kwargs,
    ) -> list[Any]:
        """Enrich documents in the dataset using LLM-powered analysis.

        This convenience method provides easy access to the enrichment
        functionality, allowing AI agents and users to populate schema
        fields with meaningful metadata.

        Parameters
        ----------
        enrichments:
            Map of field_name -> prompt or config dict. Example:
            {
                "context": "Summarize in 2 sentences",
                "tags": "Extract 5 topic tags",
                "custom_metadata": {
                    "prompt": "Extract technical details as JSON",
                    "format": "json"
                }
            }
        filter:
            Optional Lance SQL filter to select documents
        skip_existing:
            Whether to skip fields that already have values
        batch_size:
            Number of documents to process at once
        show_progress:
            Whether to show progress bar
        model:
            LLM model to use for enrichment
        **enricher_kwargs:
            Additional arguments for ContextEnricher

        Returns
        -------
        list[EnrichmentResult]
            Results of the enrichment operations

        Examples
        --------
        >>> # Basic enrichment
        >>> dataset.enrich({
        ...     "context": "Explain what this document teaches",
        ...     "tags": "Extract technology and concept tags"
        ... })

        >>> # Custom metadata extraction
        >>> dataset.enrich({
        ...     "custom_metadata": {
        ...         "prompt": "Rate complexity 1-5 and list main topics",
        ...         "format": "json"
        ...     }
        ... }, filter="context IS NULL")

        >>> # Using different model
        >>> dataset.enrich(
        ...     {"context": "Summarize for AI developers"},
        ...     model="anthropic/claude-3-haiku"
        ... )
        """
        from contextframe.enrich import ContextEnricher

        enricher = ContextEnricher(model=model, **enricher_kwargs)
        return enricher.enrich_dataset(
            self,
            enrichments=enrichments,
            filter=filter,
            skip_existing=skip_existing,
            batch_size=batch_size,
            show_progress=show_progress,
        )

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def to_pandas(self, **kwargs):
        """Convert the dataset to a Pandas DataFrame."""
        return self._dataset.to_table(**kwargs).to_pandas()

    def nearest(self, query_vector: np.ndarray, *, k: int = 10, **kwargs):
        """Find k-nearest neighbors to a query vector."""
        return self._dataset.to_table(
            nearest={"column": "vector", "q": query_vector, "k": k}, **kwargs
        )

    def get_by_uuid(self, uuid: str) -> FrameRecord | None:
        """Retrieve a specific record by its UUID.

        Parameters
        ----------
        uuid:
            The UUID of the record to retrieve

        Returns
        -------
        Optional[FrameRecord]
            The record if found, None otherwise
        """
        # Use non-blob columns to avoid Lance scanning limitation
        tbl = self.scanner(
            filter=f"uuid = '{uuid}'", columns=self._non_blob_columns
        ).to_table()

        if tbl.num_rows == 0:
            return None
        elif tbl.num_rows == 1:
            # Note: raw_data will be None since we can't scan blob columns
            # In the future, we could use take_blobs if needed
            return FrameRecord.from_arrow(tbl, dataset_path=Path(self._dataset.uri))
        else:
            raise ValueError(
                f"Multiple records found with uuid={uuid!r} (data integrity error)"
            )

    # ------------------------------------------------------------------
    # Advanced scanner proxy (filter, columns, nearest, etc.)
    # ------------------------------------------------------------------

    def scanner(self, **scan_kwargs):
        """Return a LanceScanner for custom queries.

        Note: If a filter is provided and the dataset has blob columns,
        those columns will be automatically excluded from the projection
        to avoid Lance's limitation on scanning blob columns.
        """
        # If there's a filter and we have blob columns, exclude them
        if 'filter' in scan_kwargs and self._non_blob_columns is not None:
            # Only override columns if not explicitly set by user
            if 'columns' not in scan_kwargs:
                scan_kwargs['columns'] = self._non_blob_columns

        return self._dataset.scanner(**scan_kwargs)

    # ------------------------------------------------------------------
    # Versioning wrappers
    # ------------------------------------------------------------------

    def versions(self) -> list[int]:
        """List available versions of the dataset."""
        return list(range(self._dataset.version + 1))

    def checkout(self, version: int) -> FrameDataset:
        """Checkout a specific version of the dataset."""
        return FrameDataset.open(self._dataset.uri, version=version)

    # ------------------------------------------------------------------
    # Low-level proxy
    # ------------------------------------------------------------------

    @property
    def _native(self):
        """Access the underlying native Lance dataset object."""
        return self._dataset

    def __repr__(self):
        return f"<FrameDataset at {self._dataset.uri}>"

    # ------------------------------------------------------------------
    # Collection management helpers
    # ------------------------------------------------------------------

    def get_collection_header(self, collection_name: str) -> FrameRecord | None:
        """Return the *Collection Header* record for *collection_name*.

        The helper follows the *Collection Header* convention where the
        header record is identified by the presence of::

            metadata['custom_metadata']['record_type'] == 'collection_header'

        Parameters
        ----------
        collection_name:
            The ``collection`` metadata value designating the logical
            collection.  Matching is performed using a simple equality
            filter on the *collection* column.

        Returns
        -------
        Optional[FrameRecord]
            The header record if exactly one is found.  If none exist the
            function returns *None*.  If multiple header records are found an
            exception is raised as this indicates a data‐integrity problem.
        """
        # We first narrow down to rows that belong to the collection to avoid
        # scanning the entire dataset.
        tbl = self.scanner(filter=f"collection = '{collection_name}'").to_table()
        header: FrameRecord | None = None
        for i in range(tbl.num_rows):
            fr = FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            meta = fr.metadata
            record_type = meta.get("record_type") or (
                meta.get("custom_metadata", {}).get("record_type")
                if meta.get("custom_metadata")
                else None
            )
            if record_type == "collection_header":
                if header is not None:
                    raise ValueError(
                        f"Multiple collection header records found for collection '{collection_name}'."
                    )
                header = fr
        return header

    def get_collection_members(
        self, collection_name: str, *, include_header: bool = False
    ) -> list[FrameRecord]:
        """Return all *member* records for *collection_name*.

        Parameters
        ----------
        collection_name:
            The name stored in the ``collection`` metadata field.
        include_header:
            When *True*, the collection header record is included in the
            returned list.  Defaults to *False*.
        """
        tbl = self.scanner(filter=f"collection = '{collection_name}'").to_table()
        out: list[FrameRecord] = []
        for i in range(tbl.num_rows):
            fr = FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            meta = fr.metadata
            is_header = (meta.get("record_type") == "collection_header") or (
                meta.get("custom_metadata", {}).get("record_type")
                == "collection_header"
                if meta.get("custom_metadata")
                else False
            )
            if is_header and not include_header:
                continue
            out.append(fr)
        return out

    def get_members_linked_to_header(self, header_uuid: str) -> list[FrameRecord]:
        """Return all *member* records that include a relationship linking to *header_uuid*.

        The function inspects the ``relationships`` metadata array of each
        record and returns those that contain a struct with::

            {
                "type": "member_of",  # recommended convention
                "id": header_uuid      # or path/uri/cid depending on identifier
            }

        Notes
        -----
        The implementation currently performs the relationship filtering in
        Python after loading candidate rows.  Depending on dataset size this
        could be optimised further once Lance gains richer predicate support
        for nested structs.
        """
        # Fetch all rows that have non-null relationships to minimise the
        # amount of data pulled into memory.
        # Unfortunately filtering on nested list<struct> is not fully
        # supported yet, so we load the *relationships* column for all rows
        # and apply filtering in Python.
        tbl = self._dataset.to_table(
            columns=None
        )  # include all columns so we can build FrameRecord later
        members: list[FrameRecord] = []
        for i in range(tbl.num_rows):
            fr = FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for rel in fr.metadata.get("relationships", []) or []:
                # A relationship can reference the header using one of the
                # identifier fields.  Match against any of them so the caller
                # can pass the UUID irrespective of the exact field used.
                identifier_match = False
                if (
                    rel.get("id") == header_uuid
                    or rel.get("path") == header_uuid
                    or rel.get("uri") == header_uuid
                    or rel.get("cid") == header_uuid
                ):
                    identifier_match = True

                if identifier_match and rel.get("type") == "member_of":
                    members.append(fr)
                    break  # no need to inspect other relationships for this record

    # ------------------------------------------------------------------
    # FrameSet management helpers
    # ------------------------------------------------------------------

    def create_frameset(
        self,
        title: str,
        content: str,
        query: str | None = None,
        source_records: list[tuple[str, str]] | None = None,
        vector: np.ndarray | None = None,
        **kwargs,
    ) -> FrameRecord:
        """Create a FrameSet record from LLM analysis results.

        A FrameSet is a derived document that contains LLM-generated analysis,
        relevant excerpts from source documents, and contextual explanations.
        It's created as a result of querying a ContextFrame and synthesizing
        information from multiple sources.

        Parameters
        ----------
        title:
            Title of the frameset (e.g., "Q4 COGS Analysis for Tesla")
        content:
            The main content including LLM analysis and excerpts
        query:
            The original query that generated this frameset
        source_records:
            List of (uuid, excerpt) tuples linking to source documents
        vector:
            Optional embedding for the frameset content
        **kwargs:
            Additional metadata fields for the FrameRecord

        Returns
        -------
        FrameRecord
            The created frameset record
        """
        # Build custom metadata
        custom_metadata = kwargs.pop("custom_metadata", {})
        if query:
            custom_metadata["original_query"] = query
        if source_records:
            # Store source references as JSON
            custom_metadata["source_excerpts"] = str(source_records)

        # Build relationships to source documents
        relationships = kwargs.pop("relationships", [])
        if source_records:
            for uuid, _ in source_records:
                relationships.append(
                    {
                        "type": "reference",
                        "id": uuid,
                        "description": "Source document for frameset",
                    }
                )

        # Create the frameset record
        frameset = FrameRecord.create(
            title=title,
            content=content,
            record_type="frameset",
            custom_metadata=custom_metadata,
            relationships=relationships,
            vector=vector,
            **kwargs,
        )

        # Add to dataset
        self.add(frameset)
        return frameset

    def get_frameset(self, frameset_id: str) -> FrameRecord | None:
        """Retrieve a FrameSet record by UUID.

        Parameters
        ----------
        frameset_id:
            UUID of the frameset

        Returns
        -------
        Optional[FrameRecord]
            The frameset record if found and is of type 'frameset'
        """
        record = self.get_by_uuid(frameset_id)
        if record and record.metadata.get("record_type") == "frameset":
            return record
        return None

    def get_frameset_sources(self, frameset_id: str) -> list[tuple[FrameRecord, str]]:
        """Get source documents and excerpts referenced by a frameset.

        Parameters
        ----------
        frameset_id:
            UUID of the frameset

        Returns
        -------
        List[Tuple[FrameRecord, str]]
            List of (source_record, excerpt) tuples
        """
        frameset = self.get_frameset(frameset_id)
        if not frameset:
            return []

        # Get source excerpts from metadata
        import ast

        excerpts_str = frameset.metadata.get("custom_metadata", {}).get(
            "source_excerpts", ""
        )
        if not excerpts_str:
            # Just return referenced documents without excerpts
            refs = self.find_related_to(frameset_id, relationship_type="reference")
            return [(ref, "") for ref in refs]

        try:
            source_records = ast.literal_eval(excerpts_str)
            results = []
            for uuid, excerpt in source_records:
                record = self.get_by_uuid(uuid)
                if record:
                    results.append((record, excerpt))
            return results
        except (ValueError, SyntaxError):
            # Fallback to relationships
            refs = self.find_related_to(frameset_id, relationship_type="reference")
            return [(ref, "") for ref in refs]

    def update_frameset_content(
        self,
        frameset_id: str,
        new_content: str | None = None,
        append_content: str | None = None,
        new_sources: list[tuple[str, str]] | None = None,
    ) -> FrameRecord:
        """Update a frameset's content or add new source references.

        Parameters
        ----------
        frameset_id:
            UUID of the frameset to update
        new_content:
            Replace the entire content
        append_content:
            Append to existing content
        new_sources:
            Additional (uuid, excerpt) tuples to add

        Returns
        -------
        FrameRecord
            The updated frameset record
        """
        frameset = self.get_frameset(frameset_id)
        if not frameset:
            raise ValueError(f"FrameSet {frameset_id} not found")

        # Update content
        if new_content is not None:
            frameset.content = new_content
        elif append_content is not None:
            frameset.content = frameset.content + "\n\n" + append_content

        # Add new sources
        if new_sources:
            import ast

            # Get existing sources
            excerpts_str = frameset.metadata.get("custom_metadata", {}).get(
                "source_excerpts", ""
            )
            try:
                existing = ast.literal_eval(excerpts_str) if excerpts_str else []
            except (ValueError, SyntaxError):
                existing = []

            # Add new sources
            existing.extend(new_sources)
            frameset.metadata.setdefault("custom_metadata", {})["source_excerpts"] = (
                str(existing)
            )

            # Add relationships
            for uuid, _ in new_sources:
                frameset.add_relationship(
                    uuid,
                    relationship_type="reference",
                    description="Source document for frameset",
                )

        # Update the record
        self.update_record(frameset)
        return frameset

    def find_framesets_by_query(self, query_substring: str) -> list[FrameRecord]:
        """Find framesets that were created from queries containing a substring.

        Parameters
        ----------
        query_substring:
            Substring to search for in original queries

        Returns
        -------
        List[FrameRecord]
            Framesets whose original_query contains the substring
        """
        all_framesets = self.find_by_record_type("frameset")
        results = []
        for fs in all_framesets:
            original_query = fs.metadata.get("custom_metadata", {}).get(
                "original_query", ""
            )
            if query_substring.lower() in original_query.lower():
                results.append(fs)
        return results

    def find_framesets_referencing(self, document_uuid: str) -> list[FrameRecord]:
        """Find all framesets that reference a specific document.

        Parameters
        ----------
        document_uuid:
            UUID of the document to search for

        Returns
        -------
        List[FrameRecord]
            Framesets that reference this document
        """
        # Use the existing relationship finder
        return [
            record
            for record in self.find_related_to(
                document_uuid, relationship_type="reference"
            )
            if record.metadata.get("record_type") == "frameset"
        ]

    def list_framesets(self) -> list[FrameRecord]:
        """List all framesets in the dataset.

        Returns
        -------
        List[FrameRecord]
            All records with record_type='frameset'
        """
        return self.find_by_record_type("frameset")

    def get_frameset_headers(self) -> list[FrameRecord]:
        """Get all frameset header records in the dataset.

        This is an alias for list_framesets() to match the naming convention
        in the Linear issue.

        Returns
        -------
        List[FrameRecord]
            All records with record_type='frameset'
        """
        return self.list_framesets()

    def get_frameset_frames(self, frameset_uuid: str) -> list[FrameRecord]:
        """Get all frames referenced by a frameset.

        This method retrieves the actual frame records that are included in
        the frameset, based on the relationships stored in the frameset's metadata.

        Parameters
        ----------
        frameset_uuid:
            UUID of the frameset

        Returns
        -------
        List[FrameRecord]
            List of frame records included in the frameset

        Raises
        ------
        ValueError
            If the frameset is not found or is not a valid frameset
        """
        # Get the frameset record
        frameset = self.get_frameset(frameset_uuid)
        if not frameset:
            raise ValueError(f"FrameSet {frameset_uuid} not found")

        # Extract frame UUIDs from relationships
        # Framesets use the "contains" relationship type to reference their member frames
        # This allows us to track which documents are part of the frameset while
        # keeping frameset-specific metadata (like source_query) in custom_metadata
        frames = []
        for rel in frameset.metadata.get("relationships", []):
            if rel.get("type") == "contains" and rel.get("id"):
                frame = self.get_by_uuid(rel["id"])
                if frame:
                    frames.append(frame)

        return frames

    def get_frameset_frame_count(self, frameset_uuid: str) -> int:
        """Get the number of frames in a frameset.

        This method counts the number of "contains" relationships in the frameset,
        which is more reliable than storing a static count that could become
        out of sync.

        Parameters
        ----------
        frameset_uuid:
            UUID of the frameset

        Returns
        -------
        int
            Number of frames contained in the frameset

        Raises
        ------
        ValueError
            If the frameset is not found
        """
        frameset = self.get_frameset(frameset_uuid)
        if not frameset:
            raise ValueError(f"FrameSet {frameset_uuid} not found")

        # Count relationships with type="contains"
        count = 0
        for rel in frameset.metadata.get("relationships", []):
            if rel.get("type") == "contains":
                count += 1

        return count

    def find_by_status(self, status: str) -> list[FrameRecord]:
        """Return all records whose ``status`` metadata exactly matches *status*.

        The helper utilises Lance's SQL‐style predicate push-down to filter
        rows server-side whenever possible which is efficient even for large
        datasets::

            published_docs = ds.find_by_status("published")

        Parameters
        ----------
        status:
            The exact status string to match (case-sensitive).

        Returns
        -------
        List[FrameRecord]
            A list of :class:`FrameRecord` instances with ``metadata['status']``
            equal to *status*.  If no rows match the filter an empty list is
            returned.
        """
        # Build a simple equality filter which Lance can execute efficiently.
        filter_str = f"status = '{status}'"
        tbl = self.scanner(filter=filter_str).to_table()
        records: list[FrameRecord] = []
        for i in range(tbl.num_rows):
            records.append(
                FrameRecord.from_arrow(
                    tbl.slice(i, 1),
                    dataset_path=Path(self._dataset.uri),
                )
            )
        return records

    def find_by_tag(self, tag: str) -> list[FrameRecord]:
        """Return all records that contain *tag* in their ``tags`` list.

        Notes
        -----
        Direct predicate push-down on *list* columns is currently not
        universally supported by Lance.  Therefore the current
        implementation loads the candidate rows into memory and performs the
        tag containment check in Python which is acceptable for small to
        medium-sized datasets but may become a bottleneck for very large
        collections.  Future versions may leverage enhanced predicate
        support once available upstream.
        """
        # Load *all* rows so we can reconstruct full FrameRecord objects for
        # the matches.  We could read only the *tags* column first but we
        # would then need an additional random-access take() call to fetch
        # the remaining columns for each matching row.  Given that tags are
        # usually small in size the simpler approach of reading everything
        # at once is acceptable for now.
        tbl = self.scanner().to_table()
        records: list[FrameRecord] = []
        tags_col = tbl.column("tags")
        for i in range(tbl.num_rows):
            raw_tags = tags_col[i].as_py()  # returns list | None
            if raw_tags is not None and tag in raw_tags:
                records.append(
                    FrameRecord.from_arrow(
                        tbl.slice(i, 1),
                        dataset_path=Path(self._dataset.uri),
                    )
                )
        return records

    def find_related_to(
        self,
        identifier: str,
        *,
        relationship_type: str | None = None,
    ) -> list[FrameRecord]:
        """Return records that have a relationship pointing at *identifier*.

        The function inspects each row's ``relationships`` column (a
        ``list<struct>``) and returns those where at least one relationship
        element satisfies *both* of the following criteria:

        1. One of the identifier fields (``id``, ``uri``, ``path`` or ``cid``)
           equals *identifier*.
        2. If *relationship_type* is provided, the ``type`` field must also
           match it exactly.

        Examples
        --------
        >>> refs = ds.find_related_to(header_uuid, relationship_type="member_of")

        Notes
        -----
        Due to the current limitations in Lance's predicate support for
        nested list/struct columns the filtering occurs client-side in
        Python after loading the candidate rows.  Performance therefore
        scales with the total number of rows that have a non-null
        ``relationships`` column.
        """
        # Attempt to minimise IO by asking for rows where relationships is not
        # null.  If the predicate fails (e.g. due to dialect support) we fall
        # back to scanning all rows.
        try:
            tbl = self.scanner(filter="relationships IS NOT NULL").to_table()
        except Exception:  # pragma: no cover – fallback path for older Lance
            tbl = self.scanner().to_table()

        records: list[FrameRecord] = []
        rels_col = tbl.column("relationships")
        for i in range(tbl.num_rows):
            rels = rels_col[i].as_py()
            if not rels:
                continue
            for rel in rels:
                id_match = (
                    rel.get("id") == identifier
                    or rel.get("uri") == identifier
                    or rel.get("path") == identifier
                    or rel.get("cid") == identifier
                )
                type_match = (
                    relationship_type is None or rel.get("type") == relationship_type
                )
                if id_match and type_match:
                    records.append(
                        FrameRecord.from_arrow(
                            tbl.slice(i, 1),
                            dataset_path=Path(self._dataset.uri),
                        )
                    )
                    break  # no need to inspect further relationships

        return records

    # ------------------------------------------------------------------
    # Additional scalar metadata helpers
    # ------------------------------------------------------------------

    def find_by_author(self, author: str) -> list[FrameRecord]:
        """Return all records whose ``author`` column equals *author*."""
        tbl = self.scanner(filter=f"author = '{author}'").to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

    def find_by_collection(
        self, collection: str, *, include_header: bool = False
    ) -> list[FrameRecord]:
        """Fetch all rows that belong to *collection*.

        Parameters
        ----------
        collection:
            Value of the ``collection`` metadata field.
        include_header:
            If *False* (default) rows whose ``record_type`` is
            ``collection_header`` are excluded.
        """
        filter_str = f"collection = '{collection}'"
        if not include_header:
            filter_str += (
                " AND (record_type IS NULL OR record_type <> 'collection_header')"
            )
        tbl = self.scanner(filter=filter_str).to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

    def find_by_record_type(self, record_type: str) -> list[FrameRecord]:
        """Return rows whose ``record_type`` equals *record_type*."""
        tbl = self.scanner(filter=f"record_type = '{record_type}'").to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

    def find_by_source_type(self, source_type: str) -> list[FrameRecord]:
        """Return rows with a matching ``source_type`` value."""
        tbl = self.scanner(filter=f"source_type = '{source_type}'").to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

    def find_since(self, date_iso: str) -> list[FrameRecord]:
        """Return rows whose ``updated_at`` column >= *date_iso* (YYYY-MM-DD)."""
        tbl = self.scanner(filter=f"updated_at >= '{date_iso}'").to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

    def find_between(self, start_iso: str, end_iso: str) -> list[FrameRecord]:
        """Return rows whose ``updated_at`` date lies in *[start_iso, end_iso]*."""
        filter_str = f"updated_at >= '{start_iso}' AND updated_at <= '{end_iso}'"
        tbl = self.scanner(filter=filter_str).to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

    def find_by_uuid_list(self, uuids: list[str]) -> list[FrameRecord]:
        """Return rows whose UUID is in *uuids* list."""
        if not uuids:
            return []
        # Build comma-separated quoted list for SQL IN.
        quoted = ", ".join(f"'{u}'" for u in uuids)
        tbl = self.scanner(filter=f"uuid IN [{quoted}]").to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

    # ------------------------------------------------------------------
    # Nested/list helpers (Python post-filtering)
    # ------------------------------------------------------------------

    def _iter_records_table(self, tbl):
        """Internal helper to yield FrameRecord from a full arrow Table."""
        for i in range(tbl.num_rows):
            yield FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )

    def find_by_any_tag(self, tags: list[str]) -> list[FrameRecord]:
        """Return rows that contain *at least one* tag from *tags*."""
        if not tags:
            return []
        tbl = self.scanner().to_table()
        results: list[FrameRecord] = []
        tags_col = tbl.column("tags")
        tag_set = set(tags)
        for i in range(tbl.num_rows):
            row_tags = tags_col[i].as_py()
            if row_tags and tag_set.intersection(row_tags):
                results.append(
                    FrameRecord.from_arrow(
                        tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
                    )
                )
        return results

    def find_by_all_tags(self, tags: list[str]) -> list[FrameRecord]:
        """Return rows that contain *all* tags in *tags*."""
        if not tags:
            return []
        required = set(tags)
        tbl = self.scanner().to_table()
        results: list[FrameRecord] = []
        tags_col = tbl.column("tags")
        for i in range(tbl.num_rows):
            row_tags = tags_col[i].as_py()
            if row_tags and required.issubset(row_tags):
                results.append(
                    FrameRecord.from_arrow(
                        tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
                    )
                )
        return results

    def find_custom_metadata(
        self, key: str, *, value: str | None = None
    ) -> list[FrameRecord]:
        """Return rows whose ``custom_metadata`` map contains *key* (and optionally *value*)."""
        tbl = self.scanner().to_table()
        results: list[FrameRecord] = []
        meta_col = tbl.column("custom_metadata")
        for i in range(tbl.num_rows):
            mapping = meta_col[i].as_py()
            if mapping is None:
                continue
            if key in mapping and (value is None or mapping[key] == value):
                results.append(
                    FrameRecord.from_arrow(
                        tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
                    )
                )
        return results

    def find_by_contributor(self, contributor: str) -> list[FrameRecord]:
        """Return rows whose ``contributors`` list contains *contributor*."""
        tbl = self.scanner().to_table()
        contrib_col = tbl.column("contributors")
        results: list[FrameRecord] = []
        for i in range(tbl.num_rows):
            contribs = contrib_col[i].as_py()
            if contribs and contributor in contribs:
                results.append(
                    FrameRecord.from_arrow(
                        tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
                    )
                )
        return results

    # ------------------------------------------------------------------
    # Vector / full-text search convenience wrappers
    # ------------------------------------------------------------------

    def _knn_table(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        *,
        filter: str | None = None,
        **extra_scan,
    ) -> pa.Table:
        """Internal helper returning a pyarrow Table with *k* nearest neighbours."""
        # Workaround for Lance v0.30.0 bug: "Task was aborted" error
        # See: https://github.com/lancedb/lance/issues/2464
        # This occurs due to a Rust panic in Lance's vector search on small datasets
        try:
            nearest_cfg = {"column": "vector", "q": query_vector, "k": k}
            if filter is None:
                return self._dataset.to_table(nearest=nearest_cfg, **extra_scan)
            # Use scanner so we can combine nearest + filter push-down when provided.
            return self.scanner(nearest=nearest_cfg, filter=filter, **extra_scan).to_table()
            
        except Exception as e:
            # Catch the Lance "Task was aborted" error specifically
            error_str = str(e)
            if "Task was aborted" in error_str or "range end index" in error_str:
                import warnings
                warnings.warn(
                    f"Lance v0.30.0 vector search bug encountered: {error_str}. "
                    "This is a known issue with small datasets. Returning empty results.",
                    RuntimeWarning,
                    stacklevel=3
                )
                return self._dataset.to_table(limit=0)
            else:
                # Re-raise other unexpected errors
                raise

    def knn_search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        *,
        filter: str | None = None,
        **extra_scan,
    ) -> list[FrameRecord]:
        """Return the *k* nearest neighbours to *query_vector* as FrameRecords.

        Parameters
        ----------
        query_vector:
            The query embedding (numpy array of float32).
        k:
            Number of neighbours to retrieve.
        filter:
            Optional SQL filter applied after the vector search (prefilter=False
            semantics).  Useful to, e.g., restrict results to a collection.
        extra_scan:
            Additional keyword arguments forwarded to Lance *scanner* (e.g.
            `columns=[...]`).
        """
        tbl = self._knn_table(query_vector, k=k, filter=filter, **extra_scan)
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

    def full_text_search(
        self, query: str, *, columns: list[str] | None = None, k: int = 100, auto_index: bool = False
    ) -> list[FrameRecord]:
        """Run a BM25 full-text search.

        Parameters
        ----------
        query:
            Search query string.
        columns:
            List of columns to search.  Defaults to ["text_content"].
        k:
            Maximum number of rows to return.
        auto_index:
            If True, automatically create an inverted index if one doesn't exist.
            This may take time on large datasets. Default is False.
            
        Notes
        -----
        This method requires an inverted index on the search column(s).
        Use `create_fts_index()` to create the index before searching,
        or set auto_index=True to create it automatically.
        """
        # Auto-create index if requested
        if auto_index:
            try:
                # Try the search first to see if index exists
                ftq = {"query": query, "columns": columns or ["text_content"]}
                tbl = self.scanner(full_text_query=ftq, limit=1).to_table()
            except Exception as e:
                # If error mentions missing index, create it
                error_msg = str(e).lower()
                if "no inverted index" in error_msg or "inverted index" in error_msg:
                    # Create index on the first column
                    column = (columns or ["text_content"])[0]
                    self.create_fts_index(column)
        
        ftq = {"query": query, "columns": columns or ["text_content"]}
        tbl = self.scanner(full_text_query=ftq, limit=k).to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]
        
    def create_fts_index(self, column: str = "text_content", *, replace: bool = True, **kwargs) -> None:
        """Create a full-text search index on the specified column.
        
        This is a convenience method that creates an inverted index
        optimized for full-text search using BM25 ranking.
        
        Parameters
        ----------
        column:
            The column to index. Defaults to "text_content".
        replace:
            Whether to replace an existing index on the column.
        **kwargs:
            Additional options such as tokenizer configuration.
            
        Example
        -------
        >>> dataset.create_fts_index()
        >>> results = dataset.full_text_search("machine learning")
        """
        self.create_scalar_index(column, index_type="INVERTED", replace=replace, **kwargs)

    # ------------------------------------------------------------------
    # Generic scanner / streaming utilities
    # ------------------------------------------------------------------

    def scanner_for(self, **preds) -> lance.LanceScanner:
        """Return a *LanceScanner* built from keyword-style equality predicates.

        Example::

            ds.scanner_for(status="published", author="Bob").to_table()
        """
        if not preds:
            return self.scanner()
        clauses = [f"{k} = '{v}'" for k, v in preds.items()]
        filter_str = " AND ".join(clauses)
        return self.scanner(filter=filter_str)

    def stream_by_filter(self, filter: str, *, batch_size: int = 1024):
        """Yield :class:`FrameRecord` objects matching *filter* lazily in batches."""
        scanner = self.scanner(filter=filter, batch_size=batch_size)
        for batch in scanner.to_batches():
            table = pa.Table.from_batches([batch])
            yield from self._iter_records_table(table)

    def count_by_filter(self, filter: str) -> int:
        """Return the number of rows that satisfy *filter*."""
        return self.scanner(filter=filter).count_rows()

    # ------------------------------------------------------------------
    # Index management helpers
    # ------------------------------------------------------------------

    def create_vector_index(
        self,
        *,
        index_type: str = "IVF_PQ",
        num_partitions: int | None = None,
        num_sub_vectors: int | None = None,
        replace: bool = True,
        **kwargs,
    ) -> None:
        """Create or replace a vector index on the canonical ``vector`` column.

        Parameters
        ----------
        index_type:
            The index algorithm to use (e.g. ``"IVF_PQ"``, ``"IVF_FLAT"``).
            Refer to Lance documentation for the complete list.  The default
            ``IVF_PQ`` is usually a good trade-off between speed and memory.
        num_partitions:
            Number of partitions (cells) for IVF family indices.  If *None*
            Lance will auto-tune based on data volume.
        num_sub_vectors:
            Number of sub-vectors used by PQ-codec.  If *None* Lance chooses a
            default.
        replace:
            When *True* (default) an existing index on the column will be
            replaced; when *False* Lance will raise an error if one exists.
        **kwargs:
            Additional keyword arguments are forwarded to
            :py:meth:`lance.dataset.LanceDataset.create_index` to expose
            engine-specific tuning knobs (e.g. ``metric_type=\"cosine\"``).
        """
        params = {
            "index_type": index_type,
            "replace": replace,
        }
        if num_partitions is not None:
            params["num_partitions"] = num_partitions
        if num_sub_vectors is not None:
            params["num_sub_vectors"] = num_sub_vectors
        params.update(kwargs)
        # Delegate to Lance
        self._native.create_index("vector", **params)

    def create_scalar_index(self, column: str, *, index_type: str = "BITMAP", replace: bool = True, **kwargs) -> None:
        """Create a scalar index on *column* to accelerate predicate filtering.

        The helper validates that *column* exists and is a *scalar* type (not a
        list, struct, map, or the fixed-size list used for vectors).
        
        Parameters
        ----------
        column:
            The column to index.
        index_type:
            The type of index to create. Options include:
            - "BITMAP": Default bitmap index for filtering
            - "BTREE": B-tree index for range queries
            - "INVERTED": Inverted index for full-text search
            - "FTS": Full-text search index (alias for INVERTED)
        replace:
            Whether to replace an existing index on the column.
        **kwargs:
            Additional options passed to Lance (e.g., tokenizer settings).
        """
        # Validate column existence
        field = self._dataset.schema.get_field_index(column)
        if field == -1:
            raise ValueError(f"Column {column!r} does not exist in dataset schema.")
        pa_field = self._dataset.schema.field(column)
        arrow_type = pa_field.type
        import pyarrow as pa  # local import to avoid global dependency issues

        if (
            pa.types.is_struct(arrow_type)
            or pa.types.is_list(arrow_type)
            or pa.types.is_map(arrow_type)
            or pa.types.is_fixed_size_list(arrow_type)
        ):
            raise ValueError(
                f"Column {column!r} has non-scalar type {arrow_type} – cannot build scalar index."
            )
        # Delegate to Lance
        self._dataset.create_scalar_index(column, index_type=index_type, replace=replace, **kwargs)

    def enhance(
        self,
        enhancements: dict[str, str | dict[str, Any]],
        filter: str | None = None,
        batch_size: int = 10,
        skip_existing: bool = True,
        show_progress: bool = True,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
        **kwargs,
    ) -> list[Any]:
        """Enhance documents in the dataset with LLM-generated metadata.

        This is a convenience method that wraps ContextEnhancer functionality.

        Args:
            enhancements: Map of field_name -> prompt or config dict
            filter: Optional Lance SQL filter
            batch_size: Number of documents to process at once
            skip_existing: Whether to skip already-enhanced fields
            show_progress: Whether to show progress bar
            provider: LLM provider (openai, anthropic, etc.)
            model: Model name
            **kwargs: Additional provider-specific arguments

        Returns:
            List of enhancement results

        Example:
            >>> dataset.enhance({
            ...     "context": "Summarize what this document teaches",
            ...     "tags": "Extract key technical concepts",
            ...     "custom_metadata": {
            ...         "prompt": "Extract author and date if mentioned",
            ...         "format": "json"
            ...     }
            ... })
        """
        from contextframe.enhance import ContextEnhancer

        enhancer = ContextEnhancer(provider=provider, model=model, **kwargs)
        return enhancer.enhance_dataset(
            self,
            enhancements=enhancements,
            filter=filter,
            batch_size=batch_size,
            skip_existing=skip_existing,
            show_progress=show_progress,
        )

    # ------------------------------------------------------------------
    # Analytics and Performance Methods
    # ------------------------------------------------------------------

    def get_dataset_stats(self) -> dict[str, Any]:
        """Get comprehensive dataset statistics using Lance's native stats.

        Returns:
            Dictionary containing:
            - dataset_stats: Fragment counts, deleted rows, small files
            - data_stats: Field-level statistics
            - storage_size: Total size in bytes
            - version_info: Current and latest versions
            - index_info: List of indices
        """
        stats = {}

        # Basic dataset stats
        if hasattr(self._dataset, 'stats'):
            dataset_stats = self._dataset.stats.dataset_stats()
            stats['dataset_stats'] = {
                'num_fragments': dataset_stats.num_fragments,
                'num_deleted_rows': dataset_stats.num_deleted_rows,
                'num_small_files': dataset_stats.num_small_files,
            }

            # Data statistics
            data_stats = self._dataset.stats.data_stats()
            if data_stats:
                stats['data_stats'] = data_stats

        # Version info
        stats['version_info'] = {
            'current_version': self._dataset.version,
            'latest_version': self._dataset.latest_version,
            'data_storage_version': self._dataset.data_storage_version,
        }

        # Storage info
        stats['storage'] = {
            'uri': self._dataset.uri,
            'num_rows': len(self),
        }

        # Index info
        if hasattr(self._dataset, 'list_indices'):
            indices = self._dataset.list_indices()
            stats['indices'] = [
                {
                    'name': idx.name,
                    'type': idx.type,
                    'fields': idx.fields,
                    'version': idx.version,
                }
                for idx in indices
            ]

        return stats

    def get_fragment_stats(self) -> list[dict[str, Any]]:
        """Get statistics for all fragments in the dataset.

        Returns:
            List of fragment statistics including:
            - fragment_id: Fragment identifier
            - num_rows: Number of rows after deletions
            - num_deletions: Number of deleted rows
            - physical_rows: Original row count
            - files: List of data files
        """
        fragments = []

        for fragment in self._dataset.get_fragments():
            metadata = fragment.metadata
            fragments.append(
                {
                    'fragment_id': fragment.fragment_id
                    if hasattr(fragment, 'fragment_id')
                    else len(fragments),
                    'num_rows': metadata.num_rows,
                    'num_deletions': metadata.num_deletions
                    if hasattr(metadata, 'num_deletions')
                    else 0,
                    'physical_rows': metadata.physical_rows
                    if hasattr(metadata, 'physical_rows')
                    else metadata.num_rows,
                    'files': [f.path() for f in metadata.files]
                    if hasattr(metadata, 'files')
                    else [],
                }
            )

        return fragments

    def compact_files(
        self, target_rows_per_fragment: int = 1024 * 1024, **kwargs
    ) -> dict[str, Any]:
        """Compact dataset files to optimize storage.

        Args:
            target_rows_per_fragment: Target number of rows per fragment
            **kwargs: Additional arguments passed to Lance optimizer

        Returns:
            Dictionary with compaction metrics
        """
        if not hasattr(self._dataset, 'optimize'):
            raise NotImplementedError(
                "Dataset optimization requires newer Lance version"
            )

        # Perform compaction
        metrics = self._dataset.optimize.compact_files(
            target_rows_per_fragment=target_rows_per_fragment, **kwargs
        )

        return {
            'fragments_compacted': getattr(metrics, 'fragments_compacted', 0),
            'files_removed': getattr(metrics, 'files_removed', 0),
            'files_added': getattr(metrics, 'files_added', 0),
        }

    def optimize_indices(self, **kwargs) -> dict[str, Any]:
        """Optimize dataset indices for better query performance.

        Returns:
            Dictionary with optimization results
        """
        if not hasattr(self._dataset, 'optimize'):
            raise NotImplementedError("Index optimization requires newer Lance version")

        # Optimize indices
        self._dataset.optimize.optimize_indices(**kwargs)

        return {
            'status': 'completed',
            'indices_optimized': len(self._dataset.list_indices())
            if hasattr(self._dataset, 'list_indices')
            else 0,
        }

    def cleanup_old_versions(
        self, older_than: _dt.timedelta | None = None
    ) -> dict[str, Any]:
        """Clean up old dataset versions to reclaim space.

        Args:
            older_than: Only clean versions older than this duration

        Returns:
            Dictionary with cleanup statistics
        """
        cleanup_stats = self._dataset.cleanup_old_versions(older_than=older_than)

        return {
            'bytes_removed': getattr(cleanup_stats, 'bytes_removed', 0),
            'old_versions_removed': getattr(cleanup_stats, 'old_versions', 0),
        }

    def list_indices(self) -> list[dict[str, Any]]:
        """List all indices in the dataset.

        Returns:
            List of index information dictionaries
        """
        if not hasattr(self._dataset, 'list_indices'):
            return []

        indices = []
        for idx in self._dataset.list_indices():
            indices.append(
                {
                    'name': idx.name,
                    'type': idx.type,
                    'uuid': str(idx.uuid) if hasattr(idx, 'uuid') else None,
                    'fields': idx.fields,
                    'version': idx.version,
                    'fragment_ids': list(idx.fragment_ids)
                    if hasattr(idx, 'fragment_ids')
                    else [],
                }
            )

        return indices

    def get_version_history(self) -> list[dict[str, Any]]:
        """Get version history with metadata.

        Returns:
            List of version information dictionaries
        """
        versions = []

        for version in range(self._dataset.latest_version + 1):
            try:
                # Checkout version to get metadata
                versioned_ds = self._dataset.checkout_version(version)
                versions.append(
                    {
                        'version': version,
                        'num_rows': len(versioned_ds),
                        'schema_fields': len(versioned_ds.schema),
                    }
                )
            except Exception:
                # Version might be cleaned up
                continue

        return versions
