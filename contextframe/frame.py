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
except ModuleNotFoundError as exc:
    raise ImportError(
        "lance is required for contextframe.frame. Please install contextframe with the 'lance' extra."
    ) from exc

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
            elif name == "custom_metadata" and "custom_metadata" in meta:
                # Convert dict → map
                arrays[name] = pa.array(
                    [list(meta["custom_metadata"].items())], type=field.type
                )
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
        metadata: dict[str, Any] = {
            k: v[0] if isinstance(v, list) else v
            for k, v in tbl.items()
            if k not in {"text_content", "vector"}
        }
        # Convert Map to dict
        if "custom_metadata" in metadata and metadata["custom_metadata"] is not None:
            metadata["custom_metadata"] = dict(metadata["custom_metadata"])

        # Extract raw data fields if present
        raw_data = tbl.get("raw_data", [None])[0]
        raw_data_type = tbl.get("raw_data_type", [None])[0]

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
        tbl = ds._native.scanner(filter=f"uuid = '{uuid}'").to_table()
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
            ds = lance.write_dataset(tbl, raw_uri, schema=schema)
        else:
            ds = lance.write_dataset(
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
        if storage_options is None:
            ds = lance.dataset(raw_uri, version=version)
        else:
            ds = lance.dataset(
                raw_uri, version=version, storage_options=storage_options
            )
        return cls(ds)

    # ------------------------------------------------------------------
    # Data modification helpers
    # ------------------------------------------------------------------

    def add(self, record: FrameRecord) -> None:
        """Append a single FrameRecord to the dataset."""
        ok, errs = validate_metadata_with_schema(record.metadata)
        if not ok:
            raise ValueError(f"Invalid metadata: {errs}")

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
                raise ValueError(f"Invalid metadata in record {rec.uuid}: {errs}")
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
        # Delegate to Lance which returns the count of deleted rows.
        count: int = self._dataset.delete(f"uuid = '{uuid}'")
        return count

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
            raise ValueError(f"Invalid metadata: {errs}")

        # Remove the existing record and sanity-check the outcome.
        delete_count: int = self._dataset.delete(f"uuid = '{record.uuid}'")
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
            raise ValueError(f"Invalid metadata: {errs}")

        # Attempt to remove any existing row(s).  We intentionally ignore the
        # returned count here because *upsert* semantics do not care whether
        # a previous record was present.
        self._dataset.delete(f"uuid = '{record.uuid}'")

        # Insert the (new or replacement) record.
        self.add(record)

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
        tbl = self.scanner(filter=f"uuid = '{uuid}'").to_table()
        if tbl.num_rows == 0:
            return None
        elif tbl.num_rows == 1:
            return FrameRecord.from_arrow(tbl, dataset_path=Path(self._dataset.uri))
        else:
            raise ValueError(
                f"Multiple records found with uuid={uuid!r} (data integrity error)"
            )

    # ------------------------------------------------------------------
    # Advanced scanner proxy (filter, columns, nearest, etc.)
    # ------------------------------------------------------------------

    def scanner(self, **scan_kwargs):
        """Return a LanceScanner for custom queries."""
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
        nearest_cfg = {"column": "vector", "q": query_vector, "k": k}
        if filter is None:
            return self._dataset.to_table(nearest=nearest_cfg, **extra_scan)
        # Use scanner so we can combine nearest + filter push-down when provided.
        return self.scanner(nearest=nearest_cfg, filter=filter, **extra_scan).to_table()

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
        self, query: str, *, columns: list[str] | None = None, k: int = 100
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
        """
        ftq = {"query": query, "columns": columns or ["text_content"]}
        tbl = self.scanner(full_text_query=ftq, limit=k).to_table()
        return [
            FrameRecord.from_arrow(
                tbl.slice(i, 1), dataset_path=Path(self._dataset.uri)
            )
            for i in range(tbl.num_rows)
        ]

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

    def create_scalar_index(self, column: str, *, replace: bool = True) -> None:
        """Create a bitmap index on *column* to accelerate predicate filtering.

        The helper validates that *column* exists and is a *scalar* type (not a
        list, struct, map, or the fixed-size list used for vectors).
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
        self._native.create_scalar_index(column, replace=replace)
