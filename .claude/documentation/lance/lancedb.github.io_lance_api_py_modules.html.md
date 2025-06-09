---
url: "https://lancedb.github.io/lance/api/py_modules.html"
title: "Exceptions - Lance  documentation"
---

_class_ lance.BlobColumn(_[blob\_column](https://lancedb.github.io/lance/api/python/BlobColumn.__init__.html "lance.BlobColumn.__init__.blob_column"):[Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \| [ChunkedArray](https://arrow.apache.org/docs/python/generated/pyarrow.ChunkedArray.html#pyarrow.ChunkedArray "(in Apache Arrow v20.0.0)")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobColumn "Link to this definition")

A utility to wrap a Pyarrow binary column and iterate over the rows as
file-like objects.

This can be useful for working with medium-to-small binary objects that need
to interface with APIs that expect file-like objects. For very large binary
objects (4-8MB or more per value) you might be better off creating a blob column
and using `lance.Dataset.take_blobs()` to access the blob data.

_class_ lance.BlobFile(_[inner](https://lancedb.github.io/lance/api/python/BlobFile.__init__.html "lance.BlobFile.__init__.inner"):LanceBlobFile_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile "Link to this definition")

Represents a blob in a Lance dataset as a file-like object.

close()→None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.close "Link to this definition")

Flush and close the IO object.

This method has no effect if the file is already closed.

_property_ closed:bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.closed "Link to this definition")readable()→bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.readable "Link to this definition")

Return whether object was opened for reading.

If False, read() will raise OSError.

readall()→bytes [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.readall "Link to this definition")

Read until EOF, using multiple read() call.

readinto(_[b](https://lancedb.github.io/lance/api/python/BlobFile.readinto.html "lance.BlobFile.readinto.b"):bytearray_)→int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.readinto "Link to this definition")seek(_[offset](https://lancedb.github.io/lance/api/python/BlobFile.seek.html "lance.BlobFile.seek.offset"):int_, _[whence](https://lancedb.github.io/lance/api/python/BlobFile.seek.html "lance.BlobFile.seek.whence"):int= `0`_)→int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.seek "Link to this definition")

Change the stream position to the given byte offset.

> offset
>
> The stream position, relative to ‘whence’.
>
> whence
>
> The relative position to seek from.

The offset is interpreted relative to the position indicated by whence.
Values for whence are:

- os.SEEK\_SET or 0 – start of stream (the default); offset should be zero or positive

- os.SEEK\_CUR or 1 – current stream position; offset may be negative

- os.SEEK\_END or 2 – end of stream; offset is usually negative


Return the new absolute position.

seekable()→bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.seekable "Link to this definition")

Return whether object supports random access.

If False, seek(), tell() and truncate() will raise OSError.
This method may need to do a test seek().

size()→int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.size "Link to this definition")

Returns the size of the blob in bytes.

tell()→int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile.tell "Link to this definition")

Return current stream position.

_class_ lance.DataStatistics(_[fields](https://lancedb.github.io/lance/api/python/DataStatistics.__init__.html "lance.DataStatistics.__init__.fields"):[FieldStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics "lance.dataset.FieldStatistics — Statistics about a field in the dataset")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.DataStatistics "Link to this definition")

Statistics about the data in the dataset

fields:[FieldStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics "lance.dataset.FieldStatistics — Statistics about a field in the dataset") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.DataStatistics.fields "Link to this definition")

Statistics about the fields in the dataset

_class_ lance.FFILanceTableProvider(_[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.FFILanceTableProvider "lance.FFILanceTableProvider.__init__.dataset")_, _\*_, _[with\_row\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.FFILanceTableProvider "lance.FFILanceTableProvider.__init__.with_row_id") = `False`_, _[with\_row\_addr](https://lancedb.github.io/lance/api/py_modules.html#lance.FFILanceTableProvider "lance.FFILanceTableProvider.__init__.with_row_addr") = `False`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FFILanceTableProvider "Link to this definition")_class_ lance.FieldStatistics(_[id](https://lancedb.github.io/lance/api/python/FieldStatistics.__init__.html "lance.FieldStatistics.__init__.id"):int_, _[bytes\_on\_disk](https://lancedb.github.io/lance/api/python/FieldStatistics.__init__.html "lance.FieldStatistics.__init__.bytes_on_disk"):int_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FieldStatistics "Link to this definition")

Statistics about a field in the dataset

bytes\_on\_disk:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FieldStatistics.bytes_on_disk "Link to this definition")

(possibly compressed) bytes on disk used to store the field

id:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FieldStatistics.id "Link to this definition")

id of the field

_class_ lance.FragmentMetadata(_[id](https://lancedb.github.io/lance/api/python/FragmentMetadata.__init__.html "lance.FragmentMetadata.__init__.id"):int_, _[files](https://lancedb.github.io/lance/api/python/FragmentMetadata.__init__.html "lance.FragmentMetadata.__init__.files"):list\[ [DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")\]_, _[physical\_rows](https://lancedb.github.io/lance/api/python/FragmentMetadata.__init__.html "lance.FragmentMetadata.__init__.physical_rows"):int_, _[deletion\_file](https://lancedb.github.io/lance/api/python/FragmentMetadata.__init__.html "lance.FragmentMetadata.__init__.deletion_file"):[DeletionFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile — asdict()      file_type      static from_json(json)      id      json()      num_deleted_rows      path(fragment_id, base_uri=None)      read_version") \|None= `None`_, _[row\_id\_meta](https://lancedb.github.io/lance/api/python/FragmentMetadata.__init__.html "lance.FragmentMetadata.__init__.row_id_meta"):[RowIdMeta](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta "lance.fragment.RowIdMeta — asdict()      static from_json(json)      json()") \|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata "Link to this definition")

Metadata for a fragment.

id [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.id "Link to this definition")

The ID of the fragment.

Type:

int

files [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.files "Link to this definition")

The data files of the fragment. Each data file must have the same number
of rows. Each file stores a different subset of the columns.

Type:

List\[ [DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")\]

physical\_rows [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.physical_rows "Link to this definition")

The number of rows originally in this fragment. This is the number of rows
in the data files before deletions.

Type:

int

deletion\_file [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.deletion_file "Link to this definition")

The deletion file, if any.

Type:

Optional\[ [DeletionFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile — asdict()      file_type      static from_json(json)      id      json()      num_deleted_rows      path(fragment_id, base_uri=None)      read_version")\]

row\_id\_meta [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.row_id_meta "Link to this definition")

The row id metadata, if any.

Type:

Optional\[ [RowIdMeta](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta "lance.fragment.RowIdMeta — asdict()      static from_json(json)      json()")\]

data\_files()→list\[ [DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.data_files "Link to this definition")deletion\_file:[DeletionFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile — asdict()      file_type      static from_json(json)      id      json()      num_deleted_rows      path(fragment_id, base_uri=None)      read_version") \|None=`None` [¶](https://lancedb.github.io/lance/api/py_modules.html#id0 "Link to this definition")files:List\[ [DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id1 "Link to this definition")_static_ from\_json(_[json\_data](https://lancedb.github.io/lance/api/python/FragmentMetadata.from_json.html "lance.FragmentMetadata.from_json.json_data"):str_)→[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.from_json "Link to this definition")id:int [¶](https://lancedb.github.io/lance/api/py_modules.html#id2 "Link to this definition")_property_ num\_deletions:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.num_deletions "Link to this definition")

The number of rows that have been deleted from this fragment.

_property_ num\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.num_rows "Link to this definition")

The number of rows in this fragment after deletions.

physical\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#id3 "Link to this definition")row\_id\_meta:[RowIdMeta](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta "lance.fragment.RowIdMeta — asdict()      static from_json(json)      json()") \|None=`None` [¶](https://lancedb.github.io/lance/api/py_modules.html#id4 "Link to this definition")to\_json()→dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.FragmentMetadata.to_json "Link to this definition")

Get this as a simple JSON-serializable dictionary.

_class_ lance.LanceDataset(_[uri](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.uri"):str\|Path_, _[version](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.version"):int\|str\|None= `None`_, _[block\_size](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.block_size"):int\|None= `None`_, _[index\_cache\_size](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.index_cache_size"):int\|None= `None`_, _[metadata\_cache\_size](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.metadata_cache_size"):int\|None= `None`_, _[commit\_lock](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.commit_lock"):CommitLock\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.storage_options"):dict\[str,str\]\|None= `None`_, _[serialized\_manifest](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.serialized_manifest"):bytes\|None= `None`_, _[default\_scan\_options](https://lancedb.github.io/lance/api/python/LanceDataset.__init__.html "lance.LanceDataset.__init__.default_scan_options"):dict\[str,Any\]\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset "Link to this definition")

A Lance Dataset in Lance format where the data is stored at the given uri.

add\_columns(_[transforms](https://lancedb.github.io/lance/api/python/LanceDataset.add_columns.html#p-transforms "lance.LanceDataset.add_columns.transforms — If this is a dictionary, then the keys are the names of the new columns and the values are SQL expression strings."):dict\[str,str\]\|BatchUDF\|ReaderLike\| [pyarrow.Field](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)") \|list\[ [pyarrow.Field](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)")\]\| [pyarrow.Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_, _[read\_columns](https://lancedb.github.io/lance/api/python/LanceDataset.add_columns.html#p-read_columns "lance.LanceDataset.add_columns.read_columns — The names of the columns that the UDF will read."):list\[str\]\|None= `None`_, _[reader\_schema](https://lancedb.github.io/lance/api/python/LanceDataset.add_columns.html#p-reader_schema "lance.LanceDataset.add_columns.reader_schema — Only valid if transforms is a ReaderLike object."):pa.Schema\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python/LanceDataset.add_columns.html#p-batch_size "lance.LanceDataset.add_columns.batch_size — The number of rows to read at a time from the source dataset when applying the transform."):int\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.add_columns "Link to this definition")

Add new columns with defined values.

There are several ways to specify the new columns. First, you can provide
SQL expressions for each new column. Second you can provide a UDF that
takes a batch of existing data and returns a new batch with the new
columns. These new columns will be appended to the dataset.

You can also provide a RecordBatchReader which will read the new column
values from some external source. This is often useful when the new column
values have already been staged to files (often by some distributed process)

See the `lance.add_columns_udf()` decorator for more information on
writing UDFs.

Parameters:transforms : dict or AddColumnsUDF or ReaderLike [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.add_columns.transforms "Permalink to this definition")

If this is a dictionary, then the keys are the names of the new
columns and the values are SQL expression strings. These strings can
reference existing columns in the dataset.
If this is a AddColumnsUDF, then it is a UDF that takes a batch of
existing data and returns a new batch with the new columns.
If this is [`pyarrow.Field`](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)") or [`pyarrow.Schema`](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)"), it adds
all NULL columns with the given schema, in a metadata-only operation.

read\_columns : list of str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.add_columns.read_columns "Permalink to this definition")

The names of the columns that the UDF will read. If None, then the
UDF will read all columns. This is only used when transforms is a
UDF. Otherwise, the read columns are inferred from the SQL expressions.

reader\_schema : pa.Schema, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.add_columns.reader_schema "Permalink to this definition")

Only valid if transforms is a ReaderLike object. This will be used to
determine the schema of the reader.

batch\_size : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.add_columns.batch_size "Permalink to this definition")

The number of rows to read at a time from the source dataset when applying
the transform. This is ignored if the dataset is a v1 dataset.

Examples

```
>>> import lance
>>> import pyarrow as pa
>>> table = pa.table({"a": [1, 2, 3]})
>>> dataset = lance.write_dataset(table, "my_dataset")
>>> @lance.batch_udf()
... def double_a(batch):
...     df = batch.to_pandas()
...     return pd.DataFrame({'double_a': 2 * df['a']})
>>> dataset.add_columns(double_a)
>>> dataset.to_table().to_pandas()
   a  double_a
0  1         2
1  2         4
2  3         6
>>> dataset.add_columns({"triple_a": "a * 3"})
>>> dataset.to_table().to_pandas()
   a  double_a  triple_a
0  1         2         3
1  2         4         6
2  3         6         9

```

See also

[`LanceDataset.merge`](https://lancedb.github.io/lance/api/python/LanceDataset.merge.html "lance.LanceDataset.merge — Merge another dataset into this one.")

Merge a pre-computed set of columns into the dataset.

alter\_columns(_\* [alterations](https://lancedb.github.io/lance/api/python/LanceDataset.alter_columns.html#p-alterations "lance.LanceDataset.alter_columns.alterations — A sequence of dictionaries, each with the following keys:"):Iterable\[ [AlterColumn](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AlterColumn "lance.dataset.AlterColumn — data_type : DataType | None      name : str | None      nullable : bool | None      path : str")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.alter_columns "Link to this definition")

Alter column name, data type, and nullability.

Columns that are renamed can keep any indices that are on them. If a
column has an IVF\_PQ index, it can be kept if the column is casted to
another type. However, other index types don’t support casting at this
time.

Column types can be upcasted (such as int32 to int64) or downcasted
(such as int64 to int32). However, downcasting will fail if there are
any values that cannot be represented in the new type. In general,
columns can be casted to same general type: integers to integers,
floats to floats, and strings to strings. However, strings, binary, and
list columns can be casted between their size variants. For example,
string to large string, binary to large binary, and list to large list.

Columns that are renamed can keep any indices that are on them. However, if
the column is casted to a different type, its indices will be dropped.

Parameters:alterations : Iterable\[Dict\[str, Any\]\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.alter_columns.alterations "Permalink to this definition")

A sequence of dictionaries, each with the following keys:

- ”path”: str

The column path to alter. For a top-level column, this is the name.
For a nested column, this is the dot-separated path, e.g. “a.b.c”.

- ”name”: str, optional

The new name of the column. If not specified, the column name is
not changed.

- ”nullable”: bool, optional

Whether the column should be nullable. If not specified, the column
nullability is not changed. Only non-nullable columns can be changed
to nullable. Currently, you cannot change a nullable column to
non-nullable.

- ”data\_type”: pyarrow.DataType, optional

The new data type to cast the column to. If not specified, the column
data type is not changed.


Examples

```
>>> import lance
>>> import pyarrow as pa
>>> schema = pa.schema([pa.field('a', pa.int64()),\
...                     pa.field('b', pa.string(), nullable=False)])
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})
>>> dataset = lance.write_dataset(table, "example")
>>> dataset.alter_columns({"path": "a", "name": "x"},
...                       {"path": "b", "nullable": True})
>>> dataset.to_table().to_pandas()
   x  b
0  1  a
1  2  b
2  3  c
>>> dataset.alter_columns({"path": "x", "data_type": pa.int32()})
>>> dataset.schema
x: int32
b: string

```

checkout\_version(_[version](https://lancedb.github.io/lance/api/python/LanceDataset.checkout_version.html#p-version "lance.LanceDataset.checkout_version.version — The version to check out."):int\|str_)→[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.checkout_version "Link to this definition")

Load the given version of the dataset.

Unlike the [`dataset()`](https://lancedb.github.io/lance/api/python/dataset.html "lance.dataset — Opens the Lance dataset from the address specified.") constructor, this will re-use the
current cache.
This is a no-op if the dataset is already at the given version.

Parameters:version : int \| str, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.checkout_version.version "Permalink to this definition")

The version to check out. A version number (int) or a tag
(str) can be provided.

Return type:

[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")

cleanup\_old\_versions(_[older\_than](https://lancedb.github.io/lance/api/python/LanceDataset.cleanup_old_versions.html#p-older_than "lance.LanceDataset.cleanup_old_versions.older_than — Only versions older than this will be removed."):timedelta\|None= `None`_, _\*_, _[delete\_unverified](https://lancedb.github.io/lance/api/python/LanceDataset.cleanup_old_versions.html#p-delete_unverified "lance.LanceDataset.cleanup_old_versions.delete_unverified — Files leftover from a failed transaction may appear to be part of an in-progress operation (e.g."):bool= `False`_, _[error\_if\_tagged\_old\_versions](https://lancedb.github.io/lance/api/python/LanceDataset.cleanup_old_versions.html#p-error_if_tagged_old_versions "lance.LanceDataset.cleanup_old_versions.error_if_tagged_old_versions — Some versions may have tags associated with them."):bool= `True`_)→CleanupStats [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.cleanup_old_versions "Link to this definition")

Cleans up old versions of the dataset.

Some dataset changes, such as overwriting, leave behind data that is not
referenced by the latest dataset version. The old data is left in place
to allow the dataset to be restored back to an older version.

This method will remove older versions and any data files they reference.
Once this cleanup task has run you will not be able to checkout or restore
these older versions.

Parameters:older\_than : timedelta, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.cleanup_old_versions.older_than "Permalink to this definition")

Only versions older than this will be removed. If not specified, this
will default to two weeks.

delete\_unverified : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.cleanup_old_versions.delete_unverified "Permalink to this definition")

Files leftover from a failed transaction may appear to be part of an
in-progress operation (e.g. appending new data) and these files will
not be deleted unless they are at least 7 days old. If delete\_unverified
is True then these files will be deleted regardless of their age.

This should only be set to True if you can guarantee that no other process
is currently working on this dataset. Otherwise the dataset could be put
into a corrupted state.

error\_if\_tagged\_old\_versions : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.cleanup_old_versions.error_if_tagged_old_versions "Permalink to this definition")

Some versions may have tags associated with them. Tagged versions will
not be cleaned up, regardless of how old they are. If this argument
is set to True (the default), an exception will be raised if any
tagged versions match the parameters. Otherwise, tagged versions will
be ignored without any error and only untagged versions will be
cleaned up.

_static_ commit(_[base\_uri](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html#p-base_uri "lance.LanceDataset.commit.base_uri — The base uri of the dataset, or the dataset object itself."):str\|Path\| [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[operation](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html#p-operation "lance.LanceDataset.commit.operation — The operation to apply to the dataset."):[LanceOperation.BaseOperation](https://lancedb.github.io/lance/api/python/LanceOperation.BaseOperation.html "lance.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") \| [Transaction](https://lancedb.github.io/lance/api/python/Transaction.html "lance.Transaction — Initialize self.  See help(type(self)) for accurate signature.")_, _[blobs\_op](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html "lance.LanceDataset.commit.blobs_op"):[LanceOperation.BaseOperation](https://lancedb.github.io/lance/api/python/LanceOperation.BaseOperation.html "lance.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") \|None= `None`_, _[read\_version](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html#p-read_version "lance.LanceDataset.commit.read_version — The version of the dataset that was used as the base for the changes. This is not needed for overwrite or restore operations."):int\|None= `None`_, _[commit\_lock](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html#p-commit_lock "lance.LanceDataset.commit.commit_lock — A custom commit lock."):CommitLock\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html#p-storage_options "lance.LanceDataset.commit.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[enable\_v2\_manifest\_paths](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html#p-enable_v2_manifest_paths "lance.LanceDataset.commit.enable_v2_manifest_paths — If True, and this is a new dataset, uses the new V2 manifest paths. These paths provide more efficient opening of datasets with many versions on object stores."):bool\|None= `None`_, _[detached](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html#p-detached "lance.LanceDataset.commit.detached — If True, then the commit will not be part of the dataset lineage."):bool\|None= `False`_, _[max\_retries](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html#p-max_retries "lance.LanceDataset.commit.max_retries — The maximum number of retries to perform when committing the dataset."):int= `20`_)→[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit "Link to this definition")

Create a new version of dataset

This method is an advanced method which allows users to describe a change
that has been made to the data files. This method is not needed when using
Lance to apply changes (e.g. when using [`LanceDataset`](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") or
[`write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").)

It’s current purpose is to allow for changes being made in a distributed
environment where no single process is doing all of the work. For example,
a distributed bulk update or a distributed bulk modify operation.

Once all of the changes have been made, this method can be called to make
the changes visible by updating the dataset manifest.

Warning

This is an advanced API and doesn’t provide the same level of validation
as the other APIs. For example, it’s the responsibility of the caller to
ensure that the fragments are valid for the schema.

Parameters:base\_uri : str, Path, or [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit.base_uri "Permalink to this definition")

The base uri of the dataset, or the dataset object itself. Using
the dataset object can be more efficient because it can re-use the
file metadata cache.

operation : [BaseOperation](https://lancedb.github.io/lance/api/python/LanceOperation.BaseOperation.html "lance.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit.operation "Permalink to this definition")

The operation to apply to the dataset. This describes what changes
have been made. See available operations under [`LanceOperation`](https://lancedb.github.io/lance/api/python/LanceOperation.html "lance.LanceOperation — Base class for operations that can be applied to a dataset.").

read\_version : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit.read_version "Permalink to this definition")

The version of the dataset that was used as the base for the changes.
This is not needed for overwrite or restore operations.

commit\_lock : CommitLock, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit.commit_lock "Permalink to this definition")

A custom commit lock. Only needed if your object store does not support
atomic commits. See the user guide for more details.

storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit.storage_options "Permalink to this definition")

Extra options that make sense for a particular storage connection. This is
used to store connection parameters like credentials, endpoint, etc.

enable\_v2\_manifest\_paths : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit.enable_v2_manifest_paths "Permalink to this definition")

If True, and this is a new dataset, uses the new V2 manifest paths.
These paths provide more efficient opening of datasets with many
versions on object stores. This parameter has no effect if the dataset
already exists. To migrate an existing dataset, instead use the
[`migrate_manifest_paths_v2()`](https://lancedb.github.io/lance/api/python/LanceDataset.migrate_manifest_paths_v2.html "lance.LanceDataset.migrate_manifest_paths_v2 — Migrate the manifest paths to the new format.") method. Default is False. WARNING:
turning this on will make the dataset unreadable for older versions
of Lance (prior to 0.17.0).

detached : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit.detached "Permalink to this definition")

If True, then the commit will not be part of the dataset lineage. It will
never show up as the latest dataset and the only way to check it out in the
future will be to specifically check it out by version. The version will be
a random version that is only unique amongst detached commits. The caller
should store this somewhere as there will be no other way to obtain it in
the future.

max\_retries : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit.max_retries "Permalink to this definition")

The maximum number of retries to perform when committing the dataset.

Returns:

A new version of Lance Dataset.

Return type:

[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")

Examples

Creating a new dataset with the [`LanceOperation.Overwrite`](https://lancedb.github.io/lance/api/python/LanceOperation.Overwrite.html "lance.LanceOperation.Overwrite — Overwrite or create a new dataset.") operation:

```
>>> import lance
>>> import pyarrow as pa
>>> tab1 = pa.table({"a": [1, 2], "b": ["a", "b"]})
>>> tab2 = pa.table({"a": [3, 4], "b": ["c", "d"]})
>>> fragment1 = lance.fragment.LanceFragment.create("example", tab1)
>>> fragment2 = lance.fragment.LanceFragment.create("example", tab2)
>>> fragments = [fragment1, fragment2]
>>> operation = lance.LanceOperation.Overwrite(tab1.schema, fragments)
>>> dataset = lance.LanceDataset.commit("example", operation)
>>> dataset.to_table().to_pandas()
   a  b
0  1  a
1  2  b
2  3  c
3  4  d

```

_static_ commit\_batch(_[dest](https://lancedb.github.io/lance/api/python/LanceDataset.commit_batch.html#p-dest "lance.LanceDataset.commit_batch.dest — The base uri of the dataset, or the dataset object itself."):str\|Path\| [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[transactions](https://lancedb.github.io/lance/api/python/LanceDataset.commit_batch.html#p-transactions "lance.LanceDataset.commit_batch.transactions — The transactions to apply to the dataset."):collections.abc.Sequence\[ [Transaction](https://lancedb.github.io/lance/api/python/Transaction.html "lance.Transaction — Initialize self.  See help(type(self)) for accurate signature.")\]_, _[commit\_lock](https://lancedb.github.io/lance/api/python/LanceDataset.commit_batch.html#p-commit_lock "lance.LanceDataset.commit_batch.commit_lock — A custom commit lock."):CommitLock\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python/LanceDataset.commit_batch.html#p-storage_options "lance.LanceDataset.commit_batch.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[enable\_v2\_manifest\_paths](https://lancedb.github.io/lance/api/python/LanceDataset.commit_batch.html#p-enable_v2_manifest_paths "lance.LanceDataset.commit_batch.enable_v2_manifest_paths — If True, and this is a new dataset, uses the new V2 manifest paths. These paths provide more efficient opening of datasets with many versions on object stores."):bool\|None= `None`_, _[detached](https://lancedb.github.io/lance/api/python/LanceDataset.commit_batch.html#p-detached "lance.LanceDataset.commit_batch.detached — If True, then the commit will not be part of the dataset lineage."):bool\|None= `False`_, _[max\_retries](https://lancedb.github.io/lance/api/python/LanceDataset.commit_batch.html#p-max_retries "lance.LanceDataset.commit_batch.max_retries — The maximum number of retries to perform when committing the dataset."):int= `20`_)→[BulkCommitResult](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.BulkCommitResult "lance.dataset.BulkCommitResult — dataset : LanceDataset      merged : Transaction") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit_batch "Link to this definition")

Create a new version of dataset with multiple transactions.

This method is an advanced method which allows users to describe a change
that has been made to the data files. This method is not needed when using
Lance to apply changes (e.g. when using [`LanceDataset`](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") or
[`write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").)

Parameters:dest : str, Path, or [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit_batch.dest "Permalink to this definition")

The base uri of the dataset, or the dataset object itself. Using
the dataset object can be more efficient because it can re-use the
file metadata cache.

transactions : Iterable\[ [Transaction](https://lancedb.github.io/lance/api/python/Transaction.html "lance.Transaction — Initialize self.  See help(type(self)) for accurate signature.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit_batch.transactions "Permalink to this definition")

The transactions to apply to the dataset. These will be merged into
a single transaction and applied to the dataset. Note: Only append
transactions are currently supported. Other transaction types will be
supported in the future.

commit\_lock : CommitLock, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit_batch.commit_lock "Permalink to this definition")

A custom commit lock. Only needed if your object store does not support
atomic commits. See the user guide for more details.

storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit_batch.storage_options "Permalink to this definition")

Extra options that make sense for a particular storage connection. This is
used to store connection parameters like credentials, endpoint, etc.

enable\_v2\_manifest\_paths : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit_batch.enable_v2_manifest_paths "Permalink to this definition")

If True, and this is a new dataset, uses the new V2 manifest paths.
These paths provide more efficient opening of datasets with many
versions on object stores. This parameter has no effect if the dataset
already exists. To migrate an existing dataset, instead use the
[`migrate_manifest_paths_v2()`](https://lancedb.github.io/lance/api/python/LanceDataset.migrate_manifest_paths_v2.html "lance.LanceDataset.migrate_manifest_paths_v2 — Migrate the manifest paths to the new format.") method. Default is False. WARNING:
turning this on will make the dataset unreadable for older versions
of Lance (prior to 0.17.0).

detached : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit_batch.detached "Permalink to this definition")

If True, then the commit will not be part of the dataset lineage. It will
never show up as the latest dataset and the only way to check it out in the
future will be to specifically check it out by version. The version will be
a random version that is only unique amongst detached commits. The caller
should store this somewhere as there will be no other way to obtain it in
the future.

max\_retries : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.commit_batch.max_retries "Permalink to this definition")

The maximum number of retries to perform when committing the dataset.

Returns:

dataset: LanceDataset

A new version of Lance Dataset.

merged: Transaction

The merged transaction that was applied to the dataset.

Return type:

dict with keys

count\_rows(_[filter](https://lancedb.github.io/lance/api/python/LanceDataset.count_rows.html "lance.LanceDataset.count_rows.filter"):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceDataset.count_rows.html#p-kwargs "lance.LanceDataset.count_rows.kwargs — See py:method:scanner method for full parameter description.")_)→int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.count_rows "Link to this definition")

Count rows matching the scanner filter.

Parameters:\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.count_rows.kwargs "Permalink to this definition")

See py:method:scanner method for full parameter description.

Returns:

**count** – The total number of rows in the dataset.

Return type:

int

create\_index(_[column](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-column "lance.LanceDataset.create_index.column — The column to be indexed."):str\|list\[str\]_, _[index\_type](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-index_type "lance.LanceDataset.create_index.index_type — The type of the index. \"IVF_PQ, IVF_HNSW_PQ and IVF_HNSW_SQ\" are supported now."):str_, _[name](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-name "lance.LanceDataset.create_index.name — The index name."):str\|None= `None`_, _[metric](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-metric "lance.LanceDataset.create_index.metric — The distance metric type, i.e., \"L2\" (alias to \"euclidean\"), \"cosine\" or \"dot\" (dot product)."):str= `'L2'`_, _[replace](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-replace "lance.LanceDataset.create_index.replace — Replace the existing index if it exists."):bool= `False`_, _[num\_partitions](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-num_partitions "lance.LanceDataset.create_index.num_partitions — The number of partitions of IVF (Inverted File Index)."):int\|None= `None`_, _[ivf\_centroids](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-ivf_centroids "lance.LanceDataset.create_index.ivf_centroids — It can be either np.ndarray, pyarrow.FixedSizeListArray or pyarrow.FixedShapeTensorArray. A num_partitions x dimension array of existing K-mean centroids for IVF clustering."):np.ndarray\|pa.FixedSizeListArray\|pa.FixedShapeTensorArray\|None= `None`_, _[pq\_codebook](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-pq_codebook "lance.LanceDataset.create_index.pq_codebook — It can be np.ndarray, pyarrow.FixedSizeListArray, or pyarrow.FixedShapeTensorArray. A num_sub_vectors x (2 ^ nbits * dimensions // num_sub_vectors) array of K-mean centroids for PQ codebook."):np.ndarray\|pa.FixedSizeListArray\|pa.FixedShapeTensorArray\|None= `None`_, _[num\_sub\_vectors](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-num_sub_vectors "lance.LanceDataset.create_index.num_sub_vectors — The number of sub-vectors for PQ (Product Quantization)."):int\|None= `None`_, _[accelerator](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-accelerator "lance.LanceDataset.create_index.accelerator — If set, use an accelerator to speed up the training process. Accepted accelerator: \"cuda\" (Nvidia GPU) and \"mps\" (Apple Silicon GPU). If not set, use the CPU."):str\|'torch.Device'\|None= `None`_, _[index\_cache\_size](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-index_cache_size "lance.LanceDataset.create_index.index_cache_size — The size of the index cache in number of entries."):int\|None= `None`_, _[shuffle\_partition\_batches](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-shuffle_partition_batches "lance.LanceDataset.create_index.shuffle_partition_batches — The number of batches, using the row group size of the dataset, to include in each shuffle partition."):int\|None= `None`_, _[shuffle\_partition\_concurrency](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-shuffle_partition_concurrency "lance.LanceDataset.create_index.shuffle_partition_concurrency — The number of shuffle partitions to process concurrently."):int\|None= `None`_, _[ivf\_centroids\_file](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html "lance.LanceDataset.create_index.ivf_centroids_file"):str\|None= `None`_, _[precomputed\_partition\_dataset](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html "lance.LanceDataset.create_index.precomputed_partition_dataset"):str\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-storage_options "lance.LanceDataset.create_index.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[filter\_nan](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-filter_nan "lance.LanceDataset.create_index.filter_nan — Defaults to True."):bool= `True`_, _[one\_pass\_ivfpq](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-one_pass_ivfpq "lance.LanceDataset.create_index.one_pass_ivfpq — Defaults to False."):bool= `False`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceDataset.create_index.html#p-kwargs "lance.LanceDataset.create_index.kwargs — Parameters passed to the index building process.")_)→[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index "Link to this definition")

Create index on column.

**Experimental API**

Parameters:column : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.column "Permalink to this definition")

The column to be indexed.

index\_type : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.index_type "Permalink to this definition")

The type of the index.
`"IVF_PQ, IVF_HNSW_PQ and IVF_HNSW_SQ"` are supported now.

name : str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.name "Permalink to this definition")

The index name. If not provided, it will be generated from the
column name.

metric : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.metric "Permalink to this definition")

The distance metric type, i.e., “L2” (alias to “euclidean”), “cosine”
or “dot” (dot product). Default is “L2”.

replace : bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.replace "Permalink to this definition")

Replace the existing index if it exists.

num\_partitions : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.num_partitions "Permalink to this definition")

The number of partitions of IVF (Inverted File Index).

ivf\_centroids : optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.ivf_centroids "Permalink to this definition")

It can be either `np.ndarray`,
[`pyarrow.FixedSizeListArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedSizeListArray.html#pyarrow.FixedSizeListArray "(in Apache Arrow v20.0.0)") or
[`pyarrow.FixedShapeTensorArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedShapeTensorArray.html#pyarrow.FixedShapeTensorArray "(in Apache Arrow v20.0.0)").
A `num_partitions x dimension` array of existing K-mean centroids
for IVF clustering. If not provided, a new KMeans model will be trained.

pq\_codebook : optional, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.pq_codebook "Permalink to this definition")

It can be `np.ndarray`, [`pyarrow.FixedSizeListArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedSizeListArray.html#pyarrow.FixedSizeListArray "(in Apache Arrow v20.0.0)"),
or [`pyarrow.FixedShapeTensorArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedShapeTensorArray.html#pyarrow.FixedShapeTensorArray "(in Apache Arrow v20.0.0)").
A `num_sub_vectors x (2 ^ nbits * dimensions // num_sub_vectors)`
array of K-mean centroids for PQ codebook.

Note: `nbits` is always 8 for now.
If not provided, a new PQ model will be trained.

num\_sub\_vectors : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.num_sub_vectors "Permalink to this definition")

The number of sub-vectors for PQ (Product Quantization).

accelerator:str\|'torch.Device'\|None= `None` [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.accelerator "Permalink to this definition")

If set, use an accelerator to speed up the training process.
Accepted accelerator: “cuda” (Nvidia GPU) and “mps” (Apple Silicon GPU).
If not set, use the CPU.

index\_cache\_size : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.index_cache_size "Permalink to this definition")

The size of the index cache in number of entries. Default value is 256.

shuffle\_partition\_batches : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.shuffle_partition_batches "Permalink to this definition")

The number of batches, using the row group size of the dataset, to include
in each shuffle partition. Default value is 10240.

Assuming the row group size is 1024, each shuffle partition will hold
10240 \* 1024 = 10,485,760 rows. By making this value smaller, this shuffle
will consume less memory but will take longer to complete, and vice versa.

shuffle\_partition\_concurrency : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.shuffle_partition_concurrency "Permalink to this definition")

The number of shuffle partitions to process concurrently. Default value is 2

By making this value smaller, this shuffle will consume less memory but will
take longer to complete, and vice versa.

storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.storage_options "Permalink to this definition")

Extra options that make sense for a particular storage connection. This is
used to store connection parameters like credentials, endpoint, etc.

filter\_nan : bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.filter_nan "Permalink to this definition")

Defaults to True. False is UNSAFE, and will cause a crash if any null/nan
values are present (and otherwise will not). Disables the null filter used
for nullable columns. Obtains a small speed boost.

one\_pass\_ivfpq : bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.one_pass_ivfpq "Permalink to this definition")

Defaults to False. If enabled, index type must be “IVF\_PQ”. Reduces disk IO.

\*\*kwargs [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_index.kwargs "Permalink to this definition")

Parameters passed to the index building process.

The SQ (Scalar Quantization) is available for only `IVF_HNSW_SQ` index type,
this quantization method is used to reduce the memory usage of the index,
it maps the float vectors to integer vectors, each integer is of `num_bits`,
now only 8 bits are supported.

If `index_type` is “IVF\_\*”, then the following parameters are required:

num\_partitions

If `index_type` is with “PQ”, then the following parameters are required:

num\_sub\_vectors

Optional parameters for IVF\_PQ:

> - ivf\_centroids
>
> Existing K-mean centroids for IVF clustering.
>
> - num\_bits
>
> The number of bits for PQ (Product Quantization). Default is 8.
> Only 4, 8 are supported.

Optional parameters for IVF\_HNSW\_\*:max\_level

Int, the maximum number of levels in the graph.

m

Int, the number of edges per node in the graph.

ef\_construction

Int, the number of nodes to examine during the construction.

Examples

```
import lance

dataset = lance.dataset("/tmp/sift.lance")
dataset.create_index(
    "vector",
    "IVF_PQ",
    num_partitions=256,
    num_sub_vectors=16
)

```

```
import lance

dataset = lance.dataset("/tmp/sift.lance")
dataset.create_index(
    "vector",
    "IVF_HNSW_SQ",
    num_partitions=256,
)

```

Experimental Accelerator (GPU) support:

- _accelerate_: use GPU to train IVF partitions.

Only supports CUDA (Nvidia) or MPS (Apple) currently.
Requires PyTorch being installed.


```
import lance

dataset = lance.dataset("/tmp/sift.lance")
dataset.create_index(
    "vector",
    "IVF_PQ",
    num_partitions=256,
    num_sub_vectors=16,
    accelerator="cuda"
)

```

References

- [Faiss Index](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

- IVF introduced in [Video Google: a text retrieval approach to object matching\\
in videos](https://ieeexplore.ieee.org/abstract/document/1238663)

- [Product quantization for nearest neighbor search](https://hal.inria.fr/inria-00514462v2/document)


create\_scalar\_index(_[column](https://lancedb.github.io/lance/api/python/LanceDataset.create_scalar_index.html#p-column "lance.LanceDataset.create_scalar_index.column — The column to be indexed."):str_, _[index\_type](https://lancedb.github.io/lance/api/python/LanceDataset.create_scalar_index.html#p-index_type "lance.LanceDataset.create_scalar_index.index_type — The type of the index."):'BTREE'\|'BITMAP'\|'LABEL\_LIST'\|'INVERTED'\|'FTS'\|'NGRAM'_, _[name](https://lancedb.github.io/lance/api/python/LanceDataset.create_scalar_index.html#p-name "lance.LanceDataset.create_scalar_index.name — The index name."):str\|None= `None`_, _\*_, _[replace](https://lancedb.github.io/lance/api/python/LanceDataset.create_scalar_index.html#p-replace "lance.LanceDataset.create_scalar_index.replace — Replace the existing index if it exists."):bool= `True`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceDataset.create_scalar_index.html "lance.LanceDataset.create_scalar_index.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_scalar_index "Link to this definition")

Create a scalar index on a column.

Scalar indices, like vector indices, can be used to speed up scans. A scalar
index can speed up scans that contain filter expressions on the indexed column.
For example, the following scan will be faster if the column `my_col` has
a scalar index:

```
import lance

dataset = lance.dataset("/tmp/images.lance")
my_table = dataset.scanner(filter="my_col != 7").to_table()

```

Vector search with pre-filers can also benefit from scalar indices. For example,

```
import lance

dataset = lance.dataset("/tmp/images.lance")
my_table = dataset.scanner(
    nearest=dict(
       column="vector",
       q=[1, 2, 3, 4],
       k=10,
    )
    filter="my_col != 7",
    prefilter=True
)

```

There are 5 types of scalar indices available today.

- `BTREE`. The most common type is `BTREE`. This index is inspired
by the btree data structure although only the first few layers of the btree
are cached in memory. It will
perform well on columns with a large number of unique values and few rows per
value.

- `BITMAP`. This index stores a bitmap for each unique value in the column.
This index is useful for columns with a small number of unique values and
many rows per value.

- `LABEL_LIST`. A special index that is used to index list
columns whose values have small cardinality. For example, a column that
contains lists of tags (e.g. `["tag1", "tag2", "tag3"]`) can be indexed
with a `LABEL_LIST` index. This index can only speedup queries with
`array_has_any` or `array_has_all` filters.

- `NGRAM`. A special index that is used to index string columns. This index
creates a bitmap for each ngram in the string. By default we use trigrams.
This index can currently speed up queries using the `contains` function
in filters.

- `FTS/INVERTED`. It is used to index document columns. This index
can conduct full-text searches. For example, a column that contains any word
of query string “hello world”. The results will be ranked by BM25.


Note that the `LANCE_BYPASS_SPILLING` environment variable can be used to
bypass spilling to disk. Setting this to true can avoid memory exhaustion
issues (see [https://github.com/apache/datafusion/issues/10073](https://github.com/apache/datafusion/issues/10073) for more info).

**Experimental API**

Parameters:column : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_scalar_index.column "Permalink to this definition")

The column to be indexed. Must be a boolean, integer, float,
or string column.

index\_type : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_scalar_index.index_type "Permalink to this definition")

The type of the index. One of `"BTREE"`, `"BITMAP"`,
`"LABEL_LIST"`, `"NGRAM"`, `"FTS"` or `"INVERTED"`.

name : str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_scalar_index.name "Permalink to this definition")

The index name. If not provided, it will be generated from the
column name.

replace : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.create_scalar_index.replace "Permalink to this definition")

Replace the existing index if it exists.

with\_position : bool, default True

This is for the `INVERTED` index. If True, the index will store the
positions of the words in the document, so that you can conduct phrase
query. This will significantly increase the index size.
It won’t impact the performance of non-phrase queries even if it is set to
True.

base\_tokenizer : str, default "simple"

This is for the `INVERTED` index. The base tokenizer to use. The value
can be:
\\* “simple”: splits tokens on whitespace and punctuation.
\\* “whitespace”: splits tokens on whitespace.
\\* “raw”: no tokenization.

language : str, default "English"

This is for the `INVERTED` index. The language for stemming
and stop words. This is only used when stem or remove\_stop\_words is true

max\_token\_length : Optional\[int\], default 40

This is for the `INVERTED` index. The maximum token length.
Any token longer than this will be removed.

lower\_case : bool, default True

This is for the `INVERTED` index. If True, the index will convert all
text to lowercase.

stem : bool, default False

This is for the `INVERTED` index. If True, the index will stem the
tokens.

remove\_stop\_words : bool, default False

This is for the `INVERTED` index. If True, the index will remove
stop words.

ascii\_folding : bool, default False

This is for the `INVERTED` index. If True, the index will convert
non-ascii characters to ascii characters if possible.
This would remove accents like “é” -> “e”.

Examples

```
import lance

dataset = lance.dataset("/tmp/images.lance")
dataset.create_index(
    "category",
    "BTREE",
)

```

Scalar indices can only speed up scans for basic filters using
equality, comparison, range (e.g. `my_col BETWEEN 0 AND 100`), and set
membership (e.g. my\_col IN (0, 1, 2))

Scalar indices can be used if the filter contains multiple indexed columns and
the filter criteria are AND’d or OR’d together
(e.g. `my_col < 0 AND other_col> 100`)

Scalar indices may be used if the filter contains non-indexed columns but,
depending on the structure of the filter, they may not be usable. For example,
if the column `not_indexed` does not have a scalar index then the filter
`my_col = 0 OR not_indexed = 1` will not be able to use any scalar index on
`my_col`.

To determine if a scan is making use of a scalar index you can use
`explain_plan` to look at the query plan that lance has created. Queries
that use scalar indices will either have a `ScalarIndexQuery` relation or a
`MaterializeIndex` operator.

_property_ data\_storage\_version:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.data_storage_version "Link to this definition")

The version of the data storage format this dataset is using

delete(_[predicate](https://lancedb.github.io/lance/api/python/LanceDataset.delete.html#p-predicate "lance.LanceDataset.delete.predicate — The predicate to use to select rows to delete."):str\| [Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.delete "Link to this definition")

Delete rows from the dataset.

This marks rows as deleted, but does not physically remove them from the
files. This keeps the existing indexes still valid.

Parameters:predicate : str or pa.compute.Expression [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.delete.predicate "Permalink to this definition")

The predicate to use to select rows to delete. May either be a SQL
string or a pyarrow Expression.

Examples

```
>>> import lance
>>> import pyarrow as pa
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})
>>> dataset = lance.write_dataset(table, "example")
>>> dataset.delete("a = 1 or b in ('a', 'b')")
>>> dataset.to_table()
pyarrow.Table
a: int64
b: string
----
a: [[3]]
b: [["c"]]

```

_static_ drop(_[base\_uri](https://lancedb.github.io/lance/api/python/LanceDataset.drop.html "lance.LanceDataset.drop.base_uri"):str\|Path_, _[storage\_options](https://lancedb.github.io/lance/api/python/LanceDataset.drop.html "lance.LanceDataset.drop.storage_options"):dict\[str,str\]\|None= `None`_)→None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.drop "Link to this definition")drop\_columns(_[columns](https://lancedb.github.io/lance/api/python/LanceDataset.drop_columns.html#p-columns "lance.LanceDataset.drop_columns.columns — The names of the columns to drop."):list\[str\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.drop_columns "Link to this definition")

Drop one or more columns from the dataset

This is a metadata-only operation and does not remove the data from the
underlying storage. In order to remove the data, you must subsequently
call `compact_files` to rewrite the data without the removed columns and
then call `cleanup_old_versions` to remove the old files.

Parameters:columns : list of str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.drop_columns.columns "Permalink to this definition")

The names of the columns to drop. These can be nested column references
(e.g. “a.b.c”) or top-level column names (e.g. “a”).

Examples

```
>>> import lance
>>> import pyarrow as pa
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})
>>> dataset = lance.write_dataset(table, "example")
>>> dataset.drop_columns(["a"])
>>> dataset.to_table().to_pandas()
   b
0  a
1  b
2  c

```

drop\_index(_[name](https://lancedb.github.io/lance/api/python/LanceDataset.drop_index.html "lance.LanceDataset.drop_index.name"):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.drop_index "Link to this definition")

Drops an index from the dataset

Note: Indices are dropped by “index name”. This is not the same as the field
name. If you did not specify a name when you created the index then a name was
generated for you. You can use the list\_indices method to get the names of
the indices.

get\_fragment(_[fragment\_id](https://lancedb.github.io/lance/api/python/LanceDataset.get_fragment.html "lance.LanceDataset.get_fragment.fragment_id"):int_)→[LanceFragment](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment — Count rows matching the scanner filter.") \|None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.get_fragment "Link to this definition")

Get the fragment with fragment id.

get\_fragments(_[filter](https://lancedb.github.io/lance/api/python/LanceDataset.get_fragments.html "lance.LanceDataset.get_fragments.filter"):Expression\|None= `None`_)→list\[ [LanceFragment](https://lancedb.github.io/lance/api/python/LanceFragment.html "lance.LanceFragment — Initialize self.  See help(type(self)) for accurate signature.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.get_fragments "Link to this definition")

Get all fragments from the dataset.

Note: filter is not supported yet.

_property_ has\_index [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.has_index "Link to this definition")head(_[num\_rows](https://lancedb.github.io/lance/api/python/LanceDataset.head.html#p-num_rows "lance.LanceDataset.head.num_rows — The number of rows to load.")_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceDataset.head.html#p-kwargs "lance.LanceDataset.head.kwargs — See scanner() method for full parameter description.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.head "Link to this definition")

Load the first N rows of the dataset.

Parameters:num\_rows : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.head.num_rows "Permalink to this definition")

The number of rows to load.

\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.head.kwargs "Permalink to this definition")

See scanner() method for full parameter description.

Returns:

**table**

Return type:

Table

index\_statistics(_[index\_name](https://lancedb.github.io/lance/api/python/LanceDataset.index_statistics.html "lance.LanceDataset.index_statistics.index_name"):str_)→dict\[str,Any\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.index_statistics "Link to this definition")insert(_[data](https://lancedb.github.io/lance/api/python/LanceDataset.insert.html "lance.LanceDataset.insert.data"):ReaderLike_, _\*_, _[mode](https://lancedb.github.io/lance/api/python/LanceDataset.insert.html#p-mode "lance.LanceDataset.insert.mode — create - create a new dataset (raises if uri already exists). overwrite - create a new snapshot version append - create a new version that is the concat of the input the latest version (raises if uri does not exist)") = `'append'`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceDataset.insert.html#p-kwargs "lance.LanceDataset.insert.kwargs — Additional keyword arguments to pass to write_dataset().")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.insert "Link to this definition")

Insert data into the dataset.

Parameters:data\_obj : Reader-like

The data to be written. Acceptable types are:
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner, or RecordBatchReader
\- Huggingface dataset

mode : str, default 'append' [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.insert.mode "Permalink to this definition")

The mode to use when writing the data. Options are:

**create** \- create a new dataset (raises if uri already exists).
**overwrite** \- create a new snapshot version
**append** \- create a new version that is the concat of the input the
latest version (raises if uri does not exist)

\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.insert.kwargs "Permalink to this definition")

Additional keyword arguments to pass to [`write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").

join(_[right\_dataset](https://lancedb.github.io/lance/api/python/LanceDataset.join.html "lance.LanceDataset.join.right_dataset")_, _[keys](https://lancedb.github.io/lance/api/python/LanceDataset.join.html "lance.LanceDataset.join.keys")_, _[right\_keys](https://lancedb.github.io/lance/api/python/LanceDataset.join.html "lance.LanceDataset.join.right_keys") = `None`_, _[join\_type](https://lancedb.github.io/lance/api/python/LanceDataset.join.html "lance.LanceDataset.join.join_type") = `'left outer'`_, _[left\_suffix](https://lancedb.github.io/lance/api/python/LanceDataset.join.html "lance.LanceDataset.join.left_suffix") = `None`_, _[right\_suffix](https://lancedb.github.io/lance/api/python/LanceDataset.join.html "lance.LanceDataset.join.right_suffix") = `None`_, _[coalesce\_keys](https://lancedb.github.io/lance/api/python/LanceDataset.join.html "lance.LanceDataset.join.coalesce_keys") = `True`_, _[use\_threads](https://lancedb.github.io/lance/api/python/LanceDataset.join.html "lance.LanceDataset.join.use_threads") = `True`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.join "Link to this definition")

Not implemented (just override pyarrow dataset to prevent segfault)

_property_ lance\_schema:LanceSchema [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.lance_schema "Link to this definition")

The LanceSchema for this dataset

_property_ latest\_version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.latest_version "Link to this definition")

Returns the latest version of the dataset.

list\_indices()→list\[ [Index](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index "lance.dataset.Index — fields : List[str]      fragment_ids : Set[int]      name : str      type : str      uuid : str      version : int")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.list_indices "Link to this definition")_property_ max\_field\_id:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.max_field_id "Link to this definition")

The max\_field\_id in manifest

merge(_[data\_obj](https://lancedb.github.io/lance/api/python/LanceDataset.merge.html#p-data_obj "lance.LanceDataset.merge.data_obj — The data to be merged."):ReaderLike_, _[left\_on](https://lancedb.github.io/lance/api/python/LanceDataset.merge.html#p-left_on "lance.LanceDataset.merge.left_on — The name of the column in the dataset to join on."):str_, _[right\_on](https://lancedb.github.io/lance/api/python/LanceDataset.merge.html#p-right_on "lance.LanceDataset.merge.right_on — The name of the column in data_obj to join on."):str\|None= `None`_, _[schema](https://lancedb.github.io/lance/api/python/LanceDataset.merge.html "lance.LanceDataset.merge.schema") = `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.merge "Link to this definition")

Merge another dataset into this one.

Performs a left join, where the dataset is the left side and data\_obj
is the right side. Rows existing in the dataset but not on the left will
be filled with null values, unless Lance doesn’t support null values for
some types, in which case an error will be raised.

Parameters:data\_obj : Reader-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.merge.data_obj "Permalink to this definition")

The data to be merged. Acceptable types are:
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner,
Iterator\[RecordBatch\], or RecordBatchReader

left\_on : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.merge.left_on "Permalink to this definition")

The name of the column in the dataset to join on.

right\_on : str or None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.merge.right_on "Permalink to this definition")

The name of the column in data\_obj to join on. If None, defaults to
left\_on.

Examples

```
>>> import lance
>>> import pyarrow as pa
>>> df = pa.table({'x': [1, 2, 3], 'y': ['a', 'b', 'c']})
>>> dataset = lance.write_dataset(df, "dataset")
>>> dataset.to_table().to_pandas()
   x  y
0  1  a
1  2  b
2  3  c
>>> new_df = pa.table({'x': [1, 2, 3], 'z': ['d', 'e', 'f']})
>>> dataset.merge(new_df, 'x')
>>> dataset.to_table().to_pandas()
   x  y  z
0  1  a  d
1  2  b  e
2  3  c  f

```

See also

[`LanceDataset.add_columns`](https://lancedb.github.io/lance/api/python/LanceDataset.add_columns.html "lance.LanceDataset.add_columns — Add new columns with defined values.")

Add new columns by computing batch-by-batch.

merge\_insert(_[on](https://lancedb.github.io/lance/api/python/LanceDataset.merge_insert.html#p-on "lance.LanceDataset.merge_insert.on — A column (or columns) to join on."):str\|Iterable\[str\]_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.merge_insert "Link to this definition")

Returns a builder that can be used to create a “merge insert” operation

This operation can add rows, update rows, and remove rows in a single
transaction. It is a very generic tool that can be used to create
behaviors like “insert if not exists”, “update or insert (i.e. upsert)”,
or even replace a portion of existing data with new data (e.g. replace
all data where month=”january”)

The merge insert operation works by combining new data from a
**source table** with existing data in a **target table** by using a
join. There are three categories of records.

“Matched” records are records that exist in both the source table and
the target table. “Not matched” records exist only in the source table
(e.g. these are new data). “Not matched by source” records exist only
in the target table (this is old data).

The builder returned by this method can be used to customize what
should happen for each category of data.

Please note that the data will be reordered as part of this
operation. This is because updated rows will be deleted from the
dataset and then reinserted at the end with the new values. The
order of the newly inserted rows may fluctuate randomly because a
hash-join operation is used internally.

Parameters:on : Union\[str, Iterable\[str\]\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.merge_insert.on "Permalink to this definition")

A column (or columns) to join on. This is how records from the
source table and target table are matched. Typically this is some
kind of key or id column.

Examples

Use when\_matched\_update\_all() and when\_not\_matched\_insert\_all() to
perform an “upsert” operation. This will update rows that already exist
in the dataset and insert rows that do not exist.

```
>>> import lance
>>> import pyarrow as pa
>>> table = pa.table({"a": [2, 1, 3], "b": ["a", "b", "c"]})
>>> dataset = lance.write_dataset(table, "example")
>>> new_table = pa.table({"a": [2, 3, 4], "b": ["x", "y", "z"]})
>>> # Perform a "upsert" operation
>>> dataset.merge_insert("a")     \
...             .when_matched_update_all()     \
...             .when_not_matched_insert_all() \
...             .execute(new_table)
{'num_inserted_rows': 1, 'num_updated_rows': 2, 'num_deleted_rows': 0}
>>> dataset.to_table().sort_by("a").to_pandas()
   a  b
0  1  b
1  2  x
2  3  y
3  4  z

```

Use when\_not\_matched\_insert\_all() to perform an “insert if not exists”
operation. This will only insert rows that do not already exist in the
dataset.

```
>>> import lance
>>> import pyarrow as pa
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})
>>> dataset = lance.write_dataset(table, "example2")
>>> new_table = pa.table({"a": [2, 3, 4], "b": ["x", "y", "z"]})
>>> # Perform an "insert if not exists" operation
>>> dataset.merge_insert("a")     \
...             .when_not_matched_insert_all() \
...             .execute(new_table)
{'num_inserted_rows': 1, 'num_updated_rows': 0, 'num_deleted_rows': 0}
>>> dataset.to_table().sort_by("a").to_pandas()
   a  b
0  1  a
1  2  b
2  3  c
3  4  z

```

You are not required to provide all the columns. If you only want to
update a subset of columns, you can omit columns you don’t want to
update. Omitted columns will keep their existing values if they are
updated, or will be null if they are inserted.

```
>>> import lance
>>> import pyarrow as pa
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"], \
...                   "c": ["x", "y", "z"]})
>>> dataset = lance.write_dataset(table, "example3")
>>> new_table = pa.table({"a": [2, 3, 4], "b": ["x", "y", "z"]})
>>> # Perform an "upsert" operation, only updating column "a"
>>> dataset.merge_insert("a")     \
...             .when_matched_update_all()     \
...             .when_not_matched_insert_all() \
...             .execute(new_table)
{'num_inserted_rows': 1, 'num_updated_rows': 2, 'num_deleted_rows': 0}
>>> dataset.to_table().sort_by("a").to_pandas()
   a  b     c
0  1  a     x
1  2  x     y
2  3  y     z
3  4  z  None

```

migrate\_manifest\_paths\_v2() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.migrate_manifest_paths_v2 "Link to this definition")

Migrate the manifest paths to the new format.

This will update the manifest to use the new v2 format for paths.

This function is idempotent, and can be run multiple times without
changing the state of the object store.

DANGER: this should not be run while other concurrent operations are happening.
And it should also run until completion before resuming other operations.

_property_ optimize:[DatasetOptimizer](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer "lance.dataset.DatasetOptimizer — Compacts small files in the dataset, reducing total number of files.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.optimize "Link to this definition")_property_ partition\_expression [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.partition_expression "Link to this definition")

Not implemented (just override pyarrow dataset to prevent segfault)

prewarm\_index(_[name](https://lancedb.github.io/lance/api/python/LanceDataset.prewarm_index.html#p-name "lance.LanceDataset.prewarm_index.name — The name of the index to prewarm."):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.prewarm_index "Link to this definition")

Prewarm an index

This will load the entire index into memory. This can help avoid cold start
issues with index queries. If the index does not fit in the index cache, then
this will result in wasted I/O.

Parameters:name : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.prewarm_index.name "Permalink to this definition")

The name of the index to prewarm.

replace\_field\_metadata(_[field\_name](https://lancedb.github.io/lance/api/python/LanceDataset.replace_field_metadata.html#p-field_name "lance.LanceDataset.replace_field_metadata.field_name — The name of the field to replace the metadata for"):str_, _[new\_metadata](https://lancedb.github.io/lance/api/python/LanceDataset.replace_field_metadata.html#p-new_metadata "lance.LanceDataset.replace_field_metadata.new_metadata — The new metadata to set"):dict\[str,str\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.replace_field_metadata "Link to this definition")

Replace the metadata of a field in the schema

Parameters:field\_name : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.replace_field_metadata.field_name "Permalink to this definition")

The name of the field to replace the metadata for

new\_metadata : dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.replace_field_metadata.new_metadata "Permalink to this definition")

The new metadata to set

replace\_schema(_[schema](https://lancedb.github.io/lance/api/python/LanceDataset.replace_schema.html "lance.LanceDataset.replace_schema.schema"):[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.replace_schema "Link to this definition")

Not implemented (just override pyarrow dataset to prevent segfault)

See [:py:method:\`replace\_schema\_metadata\`](https://lancedb.github.io/lance/api/py_modules.html#id5) or [:py:method:\`replace\_field\_metadata\`](https://lancedb.github.io/lance/api/py_modules.html#id7)

replace\_schema\_metadata(_[new\_metadata](https://lancedb.github.io/lance/api/python/LanceDataset.replace_schema_metadata.html#p-new_metadata "lance.LanceDataset.replace_schema_metadata.new_metadata — The new metadata to set"):dict\[str,str\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.replace_schema_metadata "Link to this definition")

Replace the schema metadata of the dataset

Parameters:new\_metadata : dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.replace_schema_metadata.new_metadata "Permalink to this definition")

The new metadata to set

restore() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.restore "Link to this definition")

Restore the currently checked out version as the latest version of the dataset.

This creates a new commit.

sample(_[num\_rows](https://lancedb.github.io/lance/api/python/LanceDataset.sample.html#p-num_rows "lance.LanceDataset.sample.num_rows — number of rows to retrieve"):int_, _[columns](https://lancedb.github.io/lance/api/python/LanceDataset.sample.html#p-columns "lance.LanceDataset.sample.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[randomize\_order](https://lancedb.github.io/lance/api/python/LanceDataset.sample.html "lance.LanceDataset.sample.randomize_order"):bool= `True`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceDataset.sample.html#p-kwargs "lance.LanceDataset.sample.kwargs — see scanner() method for full parameter description.")_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.sample "Link to this definition")

Select a random sample of data

Parameters:num\_rows : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.sample.num_rows "Permalink to this definition")

number of rows to retrieve

columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.sample.columns "Permalink to this definition")

List of column names to be fetched.
Or a dictionary of column names to SQL expressions.
All columns are fetched if None or unspecified.

\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.sample.kwargs "Permalink to this definition")

see scanner() method for full parameter description.

Returns:

**table**

Return type:

Table

scanner(_[columns](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-columns "lance.LanceDataset.scanner.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-filter "lance.LanceDataset.scanner.filter — Expression or str that is a valid SQL where clause."):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-limit "lance.LanceDataset.scanner.limit — Fetch up to this many rows."):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-offset "lance.LanceDataset.scanner.offset — Fetch starting with this row."):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-nearest "lance.LanceDataset.scanner.nearest — Get the rows corresponding to the K most similar vectors."):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-batch_size "lance.LanceDataset.scanner.batch_size — The target size of batches returned."):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-batch_readahead "lance.LanceDataset.scanner.batch_readahead — The number of batches to read ahead."):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-fragment_readahead "lance.LanceDataset.scanner.fragment_readahead — The number of fragments to read ahead."):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-scan_in_order "lance.LanceDataset.scanner.scan_in_order — Whether to read the fragments and batches in order."):bool\|None= `None`_, _[fragments](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-fragments "lance.LanceDataset.scanner.fragments — If specified, only scan these fragments."):Iterable\[ [LanceFragment](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment — Count rows matching the scanner filter.")\]\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-full_text_query "lance.LanceDataset.scanner.full_text_query — query string to search for, the results will be ranked by BM25. e.g."):str\|dict\|FullTextQuery\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-prefilter "lance.LanceDataset.scanner.prefilter — If True then the filter will be applied before the vector query is run. This will generate more correct results but it may be a more costly query."):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html "lance.LanceDataset.scanner.with_row_id"):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html "lance.LanceDataset.scanner.with_row_address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html "lance.LanceDataset.scanner.use_stats"):bool\|None= `None`_, _[fast\_search](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-fast_search "lance.LanceDataset.scanner.fast_search — If True, then the search will only be performed on the indexed data, which yields faster search time."):bool\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-io_buffer_size "lance.LanceDataset.scanner.io_buffer_size — The size of the IO buffer."):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-late_materialization "lance.LanceDataset.scanner.late_materialization — Allows custom control over late materialization."):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-use_scalar_index "lance.LanceDataset.scanner.use_scalar_index — Lance will automatically use scalar indices to optimize a query."):bool\|None= `None`_, _[include\_deleted\_rows](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-include_deleted_rows "lance.LanceDataset.scanner.include_deleted_rows — If True, then rows that have been deleted, but are still present in the fragment, will be returned."):bool\|None= `None`_, _[scan\_stats\_callback](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html#p-scan_stats_callback "lance.LanceDataset.scanner.scan_stats_callback — A callback function that will be called with the scan statistics after the scan is complete."):Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics "_lib.ScanStatistics")\],None\]\|None= `None`_, _[strict\_batch\_size](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html "lance.LanceDataset.scanner.strict_batch_size"):bool\|None= `None`_)→[LanceScanner](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner "lance.dataset.LanceScanner — Execute the plan for this scanner and display with runtime metrics.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner "Link to this definition")

Return a Scanner that can support various pushdowns.

Parameters:columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.columns "Permalink to this definition")

List of column names to be fetched.
Or a dictionary of column names to SQL expressions.
All columns are fetched if None or unspecified.

filter : pa.compute.Expression or str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.filter "Permalink to this definition")

Expression or str that is a valid SQL where clause. See
[Lance filter pushdown](https://lancedb.github.io/lance/introduction/read_and_write.html#filter-push-down)
for valid SQL expressions.

limit : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.limit "Permalink to this definition")

Fetch up to this many rows. All rows if None or unspecified.

offset : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.offset "Permalink to this definition")

Fetch starting with this row. 0 if None or unspecified.

nearest : dict, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.nearest "Permalink to this definition")

Get the rows corresponding to the K most similar vectors. Example:

```
{
    "column": <embedding col name>,
    "q": <query vector as pa.Float32Array>,
    "k": 10,
    "minimum_nprobes": 20,
    "maximum_nprobes": 50,
    "refine_factor": 1
}

```

batch\_size : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.batch_size "Permalink to this definition")

The target size of batches returned. In some cases batches can be up to
twice this size (but never larger than this). In some cases batches can
be smaller than this size.

io\_buffer\_size : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.io_buffer_size "Permalink to this definition")

The size of the IO buffer. See `ScannerBuilder.io_buffer_size`
for more information.

batch\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.batch_readahead "Permalink to this definition")

The number of batches to read ahead.

fragment\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.fragment_readahead "Permalink to this definition")

The number of fragments to read ahead.

scan\_in\_order : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.scan_in_order "Permalink to this definition")

Whether to read the fragments and batches in order. If false,
throughput may be higher, but batches will be returned out of order
and memory use might increase.

fragments : iterable of [LanceFragment](https://lancedb.github.io/lance/api/python/LanceFragment.html "lance.LanceFragment — Initialize self.  See help(type(self)) for accurate signature."), default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.fragments "Permalink to this definition")

If specified, only scan these fragments. If scan\_in\_order is True, then
the fragments will be scanned in the order given.

prefilter : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.prefilter "Permalink to this definition")

If True then the filter will be applied before the vector query is run.
This will generate more correct results but it may be a more costly
query. It’s generally good when the filter is highly selective.

If False then the filter will be applied after the vector query is run.
This will perform well but the results may have fewer than the requested
number of rows (or be empty) if the rows closest to the query do not
match the filter. It’s generally good when the filter is not very
selective.

use\_scalar\_index : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.use_scalar_index "Permalink to this definition")

Lance will automatically use scalar indices to optimize a query. In some
corner cases this can make query performance worse and this parameter can
be used to disable scalar indices in these cases.

late\_materialization : bool or List\[str\], default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.late_materialization "Permalink to this definition")

Allows custom control over late materialization. Late materialization
fetches non-query columns using a take operation after the filter. This
is useful when there are few results or columns are very large.

Early materialization can be better when there are many results or the
columns are very narrow.

If True, then all columns are late materialized.
If False, then all columns are early materialized.
If a list of strings, then only the columns in the list are
late materialized.

The default uses a heuristic that assumes filters will select about 0.1%
of the rows. If your filter is more selective (e.g. find by id) you may
want to set this to True. If your filter is not very selective (e.g.
matches 20% of the rows) you may want to set this to False.

full\_text\_query : str or dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.full_text_query "Permalink to this definition")

query string to search for, the results will be ranked by BM25.
e.g. “hello world”, would match documents containing “hello” or “world”.
or a dictionary with the following keys:

- columns: list\[str\]

The columns to search,
currently only supports a single column in the columns list.

- query: str

The query string to search for.


fast\_search : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.fast_search "Permalink to this definition")

If True, then the search will only be performed on the indexed data, which
yields faster search time.

scan\_stats\_callback : Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/python/ScanStatistics.html "lance.ScanStatistics — Statistics about the scan.")\], None\], default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.scan_stats_callback "Permalink to this definition")

A callback function that will be called with the scan statistics after the
scan is complete. Errors raised by the callback will be logged but not
re-raised.

include\_deleted\_rows : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.scanner.include_deleted_rows "Permalink to this definition")

If True, then rows that have been deleted, but are still present in the
fragment, will be returned. These rows will have the \_rowid column set
to null. All other columns will reflect the value stored on disk and may
not be null.

Note: if this is a search operation, or a take operation (including scalar
indexed scans) then deleted rows cannot be returned.

Note

For now, if BOTH filter and nearest is specified, then:

1. nearest is executed first.

2. The results are filtered afterwards.


For debugging ANN results, you can choose to not use the index
even if present by specifying `use_index=False`. For example,
the following will always return exact KNN results:

```
dataset.to_table(nearest={
    "column": "vector",
    "k": 10,
    "q": <query vector>,
    "use_index": False
}

```

_property_ schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.schema "Link to this definition")

The pyarrow Schema for this dataset

session()→\_Session [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.session "Link to this definition")

Return the dataset session, which holds the dataset’s state.

_property_ stats:[LanceStats](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats "lance.dataset.LanceStats — Statistics about a LanceDataset.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.stats "Link to this definition")

**Experimental API**

_property_ tags:[Tags](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags "lance.dataset.Tags — Dataset tag manager.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.tags "Link to this definition")

Tag management for the dataset.

Similar to Git, tags are a way to add metadata to a specific version of the
dataset.

Warning

Tagged versions are exempted from the [`cleanup_old_versions()`](https://lancedb.github.io/lance/api/python/LanceDataset.cleanup_old_versions.html "lance.LanceDataset.cleanup_old_versions — Cleans up old versions of the dataset.")
process.

To remove a version that has been tagged, you must first
`delete()` the associated tag.

Examples

```
ds = lance.open("dataset.lance")
ds.tags.create("v2-prod-20250203", 10)

tags = ds.tags.list()

```

take(_[indices](https://lancedb.github.io/lance/api/python/LanceDataset.take.html#p-indices "lance.LanceDataset.take.indices — indices of rows to select in the dataset."):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)")_, _[columns](https://lancedb.github.io/lance/api/python/LanceDataset.take.html#p-columns "lance.LanceDataset.take.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.take "Link to this definition")

Select rows of data by index.

Parameters:indices : Array or array-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.take.indices "Permalink to this definition")

indices of rows to select in the dataset.

columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.take.columns "Permalink to this definition")

List of column names to be fetched.
Or a dictionary of column names to SQL expressions.
All columns are fetched if None or unspecified.

Returns:

**table**

Return type:

[pyarrow.Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)")

take\_blobs(_[blob\_column](https://lancedb.github.io/lance/api/python/LanceDataset.take_blobs.html "lance.LanceDataset.take_blobs.blob_column"):str_, _[ids](https://lancedb.github.io/lance/api/python/LanceDataset.take_blobs.html "lance.LanceDataset.take_blobs.ids"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_, _[addresses](https://lancedb.github.io/lance/api/python/LanceDataset.take_blobs.html "lance.LanceDataset.take_blobs.addresses"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_, _[indices](https://lancedb.github.io/lance/api/python/LanceDataset.take_blobs.html "lance.LanceDataset.take_blobs.indices"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_)→list\[ [BlobFile](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile "lance.blob.BlobFile")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.take_blobs "Link to this definition")

Select blobs by row IDs.

Instead of loading large binary blob data into memory before processing it,
this API allows you to open binary blob data as a regular Python file-like
object. For more details, see [`lance.BlobFile`](https://lancedb.github.io/lance/api/python/BlobFile.html "lance.BlobFile — Represents a blob in a Lance dataset as a file-like object.").

Exactly one of ids, addresses, or indices must be specified.
:param blob\_column: The name of the blob column to select.
:type blob\_column: str
:param ids: row IDs to select in the dataset.
:type ids: Integer Array or array-like
:param addresses: The (unstable) row addresses to select in the dataset.
:type addresses: Integer Array or array-like
:param indices: The offset / indices of the row in the dataset.
:type indices: Integer Array or array-like

Returns:

**blob\_files**

Return type:

List\[ [BlobFile](https://lancedb.github.io/lance/api/python/BlobFile.html "lance.BlobFile — Represents a blob in a Lance dataset as a file-like object.")\]

to\_batches(_[columns](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.columns"):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.filter"):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.limit"):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.offset"):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.nearest"):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.batch_size"):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.batch_readahead"):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.fragment_readahead"):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.scan_in_order"):bool\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.prefilter"):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.with_row_id"):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.with_row_address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.use_stats"):bool\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.full_text_query"):str\|dict\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.io_buffer_size"):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.late_materialization"):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.use_scalar_index"):bool\|None= `None`_, _[strict\_batch\_size](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches.strict_batch_size"):bool\|None= `None`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html#p-kwargs "lance.LanceDataset.to_batches.kwargs — Arguments for scanner().")_)→Iterator\[ [RecordBatch](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html#pyarrow.RecordBatch "(in Apache Arrow v20.0.0)")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_batches "Link to this definition")

Read the dataset as materialized record batches.

Parameters:\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_batches.kwargs "Permalink to this definition")

Arguments for [`scanner()`](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html "lance.LanceDataset.scanner — Return a Scanner that can support various pushdowns.").

Returns:

**record\_batches**

Return type:

Iterator of [`RecordBatch`](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html#pyarrow.RecordBatch "(in Apache Arrow v20.0.0)")

to\_table(_[columns](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-columns "lance.LanceDataset.to_table.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-filter "lance.LanceDataset.to_table.filter — Expression or str that is a valid SQL where clause."):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-limit "lance.LanceDataset.to_table.limit — Fetch up to this many rows."):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-offset "lance.LanceDataset.to_table.offset — Fetch starting with this row."):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-nearest "lance.LanceDataset.to_table.nearest — Get the rows corresponding to the K most similar vectors."):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-batch_size "lance.LanceDataset.to_table.batch_size — The number of rows to read at a time."):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-batch_readahead "lance.LanceDataset.to_table.batch_readahead — The number of batches to read ahead."):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-fragment_readahead "lance.LanceDataset.to_table.fragment_readahead — The number of fragments to read ahead."):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-scan_in_order "lance.LanceDataset.to_table.scan_in_order — Whether to read the fragments and batches in order."):bool\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-prefilter "lance.LanceDataset.to_table.prefilter — Run filter before the vector search."):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-with_row_id "lance.LanceDataset.to_table.with_row_id — Return row ID."):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-with_row_address "lance.LanceDataset.to_table.with_row_address — Return row address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-use_stats "lance.LanceDataset.to_table.use_stats — Use stats pushdown during filters."):bool\|None= `None`_, _[fast\_search](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-fast_search "lance.LanceDataset.to_table.fast_search"):bool\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-full_text_query "lance.LanceDataset.to_table.full_text_query — query string to search for, the results will be ranked by BM25. e.g."):str\|dict\|FullTextQuery\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-io_buffer_size "lance.LanceDataset.to_table.io_buffer_size — The size of the IO buffer."):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-late_materialization "lance.LanceDataset.to_table.late_materialization — Allows custom control over late materialization."):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-use_scalar_index "lance.LanceDataset.to_table.use_scalar_index — Allows custom control over scalar index usage."):bool\|None= `None`_, _[include\_deleted\_rows](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html#p-include_deleted_rows "lance.LanceDataset.to_table.include_deleted_rows — If True, then rows that have been deleted, but are still present in the fragment, will be returned."):bool\|None= `None`_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table "Link to this definition")

Read the data into memory as a [`pyarrow.Table`](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)")

Parameters:columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.columns "Permalink to this definition")

List of column names to be fetched.
Or a dictionary of column names to SQL expressions.
All columns are fetched if None or unspecified.

filter : pa.compute.Expression or str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.filter "Permalink to this definition")

Expression or str that is a valid SQL where clause. See
[Lance filter pushdown](https://lancedb.github.io/lance/introduction/read_and_write.html#filter-push-down)
for valid SQL expressions.

limit : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.limit "Permalink to this definition")

Fetch up to this many rows. All rows if None or unspecified.

offset : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.offset "Permalink to this definition")

Fetch starting with this row. 0 if None or unspecified.

nearest : dict, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.nearest "Permalink to this definition")

Get the rows corresponding to the K most similar vectors. Example:

```
{
    "column": <embedding col name>,
    "q": <query vector as pa.Float32Array>,
    "k": 10,
    "metric": "cosine",
    "minimum_nprobes": 20,
    "maximum_nprobes": 50,
    "refine_factor": 1
}

```

batch\_size : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.batch_size "Permalink to this definition")

The number of rows to read at a time.

io\_buffer\_size : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.io_buffer_size "Permalink to this definition")

The size of the IO buffer. See `ScannerBuilder.io_buffer_size`
for more information.

batch\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.batch_readahead "Permalink to this definition")

The number of batches to read ahead.

fragment\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.fragment_readahead "Permalink to this definition")

The number of fragments to read ahead.

scan\_in\_order : bool, optional, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.scan_in_order "Permalink to this definition")

Whether to read the fragments and batches in order. If false,
throughput may be higher, but batches will be returned out of order
and memory use might increase.

prefilter : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.prefilter "Permalink to this definition")

Run filter before the vector search.

late\_materialization : bool or List\[str\], default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.late_materialization "Permalink to this definition")

Allows custom control over late materialization. See
`ScannerBuilder.late_materialization` for more information.

use\_scalar\_index : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.use_scalar_index "Permalink to this definition")

Allows custom control over scalar index usage. See
`ScannerBuilder.use_scalar_index` for more information.

with\_row\_id : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.with_row_id "Permalink to this definition")

Return row ID.

with\_row\_address : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.with_row_address "Permalink to this definition")

Return row address

use\_stats : bool, optional, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.use_stats "Permalink to this definition")

Use stats pushdown during filters.

fast\_search : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.fast_search "Permalink to this definition")

full\_text\_query : str or dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.full_text_query "Permalink to this definition")

query string to search for, the results will be ranked by BM25.
e.g. “hello world”, would match documents contains “hello” or “world”.
or a dictionary with the following keys:

- columns: list\[str\]

The columns to search,
currently only supports a single column in the columns list.

- query: str

The query string to search for.


include\_deleted\_rows : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.to_table.include_deleted_rows "Permalink to this definition")

If True, then rows that have been deleted, but are still present in the
fragment, will be returned. These rows will have the \_rowid column set
to null. All other columns will reflect the value stored on disk and may
not be null.

Note: if this is a search operation, or a take operation (including scalar
indexed scans) then deleted rows cannot be returned.

Notes

If BOTH filter and nearest is specified, then:

1. nearest is executed first.

2. The results are filtered afterward, unless pre-filter sets to True.


update(_[updates](https://lancedb.github.io/lance/api/python/LanceDataset.update.html#p-updates "lance.LanceDataset.update.updates — A mapping of column names to a SQL expression."):dict\[str,str\]_, _[where](https://lancedb.github.io/lance/api/python/LanceDataset.update.html#p-where "lance.LanceDataset.update.where — A SQL predicate indicating which rows should be updated."):str\|None= `None`_)→[UpdateResult](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.UpdateResult "lance.dataset.UpdateResult — num_rows_updated : int") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.update "Link to this definition")

Update column values for rows matching where.

Parameters:updates : dict of str to str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.update.updates "Permalink to this definition")

A mapping of column names to a SQL expression.

where : str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.update.where "Permalink to this definition")

A SQL predicate indicating which rows should be updated.

Returns:

**updates** – A dictionary containing the number of rows updated.

Return type:

dict

Examples

```
>>> import lance
>>> import pyarrow as pa
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})
>>> dataset = lance.write_dataset(table, "example")
>>> update_stats = dataset.update(dict(a = 'a + 2'), where="b != 'a'")
>>> update_stats["num_updated_rows"] = 2
>>> dataset.to_table().to_pandas()
   a  b
0  1  a
1  4  b
2  5  c

```

_property_ uri:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.uri "Link to this definition")

The location of the data

validate() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.validate "Link to this definition")

Validate the dataset.

This checks the integrity of the dataset and will raise an exception if
the dataset is corrupted.

_property_ version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.version "Link to this definition")

Returns the currently checked out version of the dataset

versions() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceDataset.versions "Link to this definition")

Return all versions in this dataset.

_class_ lance.LanceFragment(_[dataset](https://lancedb.github.io/lance/api/python/LanceFragment.__init__.html "lance.LanceFragment.__init__.dataset"):[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[fragment\_id](https://lancedb.github.io/lance/api/python/LanceFragment.__init__.html "lance.LanceFragment.__init__.fragment_id"):int\|None_, _\*_, _[fragment](https://lancedb.github.io/lance/api/python/LanceFragment.__init__.html "lance.LanceFragment.__init__.fragment"):\_Fragment\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment "Link to this definition")count\_rows(_[self](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.self")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.count_rows "Link to this definition")

Count rows matching the scanner filter.

Parameters:filter : Expression, default None

Scan will return only the rows matching the filter.
If possible the predicate will be pushed down to exploit the
partition information or internal metadata found in the data
source, e.g. Parquet statistics. Otherwise filters the loaded
RecordBatches before yielding them.

batch\_size : int, default 131\_072

The maximum row count for scanned record batches. If scanned
record batches are overflowing memory then this method can be
called to reduce their size.

batch\_readahead : int, default 16

The number of batches to read ahead in a file. This might not work
for all file formats. Increasing this number will increase
RAM usage but could also improve IO utilization.

fragment\_readahead : int, default 4

The number of files to read ahead. Increasing this number will increase
RAM usage but could also improve IO utilization.

fragment\_scan\_options : FragmentScanOptions, default None

Options specific to a particular scan and fragment type, which
can change between different scans of the same dataset.

use\_threads : bool, default True

If enabled, then maximum parallelism will be used determined by
the number of available CPU cores.

cache\_metadata : bool, default True

If enabled, metadata may be cached when scanning to speed up
repeated scans.

memory\_pool : MemoryPool, default None

For memory allocations, if required. If not specified, uses the
default pool.

Returns:

**count**

Return type:

int

_static_ create(_[dataset\_uri](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-dataset_uri "lance.LanceFragment.create.dataset_uri — The URI of the dataset."):str\|Path_, _[data](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-data "lance.LanceFragment.create.data — The data to be written to the fragment."):ReaderLike_, _[fragment\_id](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-fragment_id "lance.LanceFragment.create.fragment_id — The ID of the fragment."):int\|None= `None`_, _[schema](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-schema "lance.LanceFragment.create.schema — The schema of the data."):pa.Schema\|None= `None`_, _[max\_rows\_per\_group](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-max_rows_per_group "lance.LanceFragment.create.max_rows_per_group — The maximum number of rows per group in the data file."):int= `1024`_, _[progress](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-progress "lance.LanceFragment.create.progress — Experimental API."):FragmentWriteProgress\|None= `None`_, _[mode](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-mode "lance.LanceFragment.create.mode — The write mode."):str= `'append'`_, _\*_, _[data\_storage\_version](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-data_storage_version "lance.LanceFragment.create.data_storage_version — The version of the data storage format to use."):str\|None= `None`_, _[use\_legacy\_format](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-use_legacy_format "lance.LanceFragment.create.use_legacy_format — Deprecated parameter."):bool\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python/LanceFragment.create.html#p-storage_options "lance.LanceFragment.create.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_)→[FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create "Link to this definition")

Create a [`FragmentMetadata`](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.") from the given data.

This can be used if the dataset is not yet created.

Warning

Internal API. This method is not intended to be used by end users.

Parameters:dataset\_uri : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.dataset_uri "Permalink to this definition")

The URI of the dataset.

fragment\_id : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.fragment_id "Permalink to this definition")

The ID of the fragment.

data : pa.Table or pa.RecordBatchReader [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.data "Permalink to this definition")

The data to be written to the fragment.

schema : pa.Schema, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.schema "Permalink to this definition")

The schema of the data. If not specified, the schema will be inferred
from the data.

max\_rows\_per\_group : int, default 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.max_rows_per_group "Permalink to this definition")

The maximum number of rows per group in the data file.

progress : FragmentWriteProgress, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.progress "Permalink to this definition")

_Experimental API_. Progress tracking for writing the fragment. Pass
a custom class that defines hooks to be called when each fragment is
starting to write and finishing writing.

mode : str, default "append" [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.mode "Permalink to this definition")

The write mode. If “append” is specified, the data will be checked
against the existing dataset’s schema. Otherwise, pass “create” or
“overwrite” to assign new field ids to the schema.

data\_storage\_version : optional, str, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.data_storage_version "Permalink to this definition")

The version of the data storage format to use. Newer versions are more
efficient but require newer versions of lance to read. The default (None)
will use the latest stable version. See the user guide for more details.

use\_legacy\_format : bool, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.use_legacy_format "Permalink to this definition")

Deprecated parameter. Use data\_storage\_version instead.

storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create.storage_options "Permalink to this definition")

Extra options that make sense for a particular storage connection. This is
used to store connection parameters like credentials, endpoint, etc.

See also

[`lance.dataset.LanceOperation.Overwrite`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Overwrite "lance.dataset.LanceOperation.Overwrite — Overwrite or create a new dataset.")

The operation used to create a new dataset or overwrite one using fragments created with this API. See the doc page for an example of using this API.

[`lance.dataset.LanceOperation.Append`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Append "lance.dataset.LanceOperation.Append — Append new rows to the dataset.")

The operation used to append fragments created with this API to an existing dataset. See the doc page for an example of using this API.

Return type:

[FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")

_static_ create\_from\_file(_[filename](https://lancedb.github.io/lance/api/python/LanceFragment.create_from_file.html#p-filename "lance.LanceFragment.create_from_file.filename — The filename of the datafile."):str_, _[dataset](https://lancedb.github.io/lance/api/python/LanceFragment.create_from_file.html#p-dataset "lance.LanceFragment.create_from_file.dataset — The dataset that the fragment belongs to."):[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[fragment\_id](https://lancedb.github.io/lance/api/python/LanceFragment.create_from_file.html#p-fragment_id "lance.LanceFragment.create_from_file.fragment_id — The ID of the fragment."):int_)→[FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create_from_file "Link to this definition")

Create a fragment from the given datafile uri.

This can be used if the datafile is loss from dataset.

Warning

Internal API. This method is not intended to be used by end users.

Parameters:filename : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create_from_file.filename "Permalink to this definition")

The filename of the datafile.

dataset : [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create_from_file.dataset "Permalink to this definition")

The dataset that the fragment belongs to.

fragment\_id : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.create_from_file.fragment_id "Permalink to this definition")

The ID of the fragment.

data\_files() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.data_files "Link to this definition")

Return the data files of this fragment.

delete(_[predicate](https://lancedb.github.io/lance/api/python/LanceFragment.delete.html#p-predicate "lance.LanceFragment.delete.predicate — A SQL predicate that specifies the rows to delete."):str_)→[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") \|None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.delete "Link to this definition")

Delete rows from this Fragment.

This will add or update the deletion file of this fragment. It does not
modify or delete the data files of this fragment. If no rows are left after
the deletion, this method will return None.

Warning

Internal API. This method is not intended to be used by end users.

Parameters:predicate : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.delete.predicate "Permalink to this definition")

A SQL predicate that specifies the rows to delete.

Returns:

A new fragment containing the new deletion file, or None if no rows left.

Return type:

[FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.") or None

Examples

```
>>> import lance
>>> import pyarrow as pa
>>> tab = pa.table({"a": [1, 2, 3], "b": [4, 5, 6]})
>>> dataset = lance.write_dataset(tab, "dataset")
>>> frag = dataset.get_fragment(0)
>>> frag.delete("a > 1")
FragmentMetadata(id=0, files=[DataFile(path='...', fields=[0, 1], ...), ...)\
>>> frag.delete("a > 0") is None\
True\
\
```\
\
See also\
\
[`lance.dataset.LanceOperation.Delete`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete "lance.dataset.LanceOperation.Delete — Remove fragments or rows from the dataset.")\
\
The operation used to commit these changes to a dataset. See the doc page for an example of using this API.\
\
deletion\_file() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.deletion_file "Link to this definition")\
\
Return the deletion file, if any\
\
_property_ fragment\_id [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.fragment_id "Link to this definition")head(_[self](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.self")_, _[intnum\_rows](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.int num_rows")_, _[columns=None](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.columns=None")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/python/LanceFragment.head.html "lance.LanceFragment.head.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.head "Link to this definition")\
\
Load the first N rows of the fragment.\
\
Parameters:num\_rows : int\
\
The number of rows to load.\
\
columns : list of str, default None\
\
The columns to project. This can be a list of column names to\
include (order and duplicates will be preserved), or a dictionary\
with {new\_column\_name: expression} values for more advanced\
projections.\
\
The list of columns or expressions may use the special fields\
\_\_batch\_index (the index of the batch within the fragment),\
\_\_fragment\_index (the index of the fragment within the dataset),\
\_\_last\_in\_fragment (whether the batch is last in fragment), and\
\_\_filename (the name of the source file or a description of the\
source fragment).\
\
The columns will be passed down to Datasets and corresponding data\
fragments to avoid loading, copying, and deserializing columns\
that will not be required further down the compute chain.\
By default all of the available columns are projected. Raises\
an exception if any of the referenced column names does not exist\
in the dataset’s Schema.\
\
filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Return type:\
\
Table\
\
merge(_[data\_obj](https://lancedb.github.io/lance/api/python/LanceFragment.merge.html#p-data_obj "lance.LanceFragment.merge.data_obj — The data to be merged."):ReaderLike_, _[left\_on](https://lancedb.github.io/lance/api/python/LanceFragment.merge.html#p-left_on "lance.LanceFragment.merge.left_on — The name of the column in the dataset to join on."):str_, _[right\_on](https://lancedb.github.io/lance/api/python/LanceFragment.merge.html#p-right_on "lance.LanceFragment.merge.right_on — The name of the column in data_obj to join on."):str\|None= `None`_, _[schema](https://lancedb.github.io/lance/api/python/LanceFragment.merge.html "lance.LanceFragment.merge.schema") = `None`_)→tuple\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment."),LanceSchema\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.merge "Link to this definition")\
\
Merge another dataset into this fragment.\
\
Performs a left join, where the fragment is the left side and data\_obj\
is the right side. Rows existing in the dataset but not on the left will\
be filled with null values, unless Lance doesn’t support null values for\
some types, in which case an error will be raised.\
\
Parameters:data\_obj : Reader-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.merge.data_obj "Permalink to this definition")\
\
The data to be merged. Acceptable types are:\
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner,\
Iterator\[RecordBatch\], or RecordBatchReader\
\
left\_on : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.merge.left_on "Permalink to this definition")\
\
The name of the column in the dataset to join on.\
\
right\_on : str or None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.merge.right_on "Permalink to this definition")\
\
The name of the column in data\_obj to join on. If None, defaults to\
left\_on.\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> df = pa.table({'x': [1, 2, 3], 'y': ['a', 'b', 'c']})\
>>> dataset = lance.write_dataset(df, "dataset")\
>>> dataset.to_table().to_pandas()\
   x  y\
0  1  a\
1  2  b\
2  3  c\
>>> fragments = dataset.get_fragments()\
>>> new_df = pa.table({'x': [1, 2, 3], 'z': ['d', 'e', 'f']})\
>>> merged = []\
>>> schema = None\
>>> for f in fragments:\
...     f, schema = f.merge(new_df, 'x')\
...     merged.append(f)\
>>> merge = lance.LanceOperation.Merge(merged, schema)\
>>> dataset = lance.LanceDataset.commit("dataset", merge, read_version=1)\
>>> dataset.to_table().to_pandas()\
   x  y  z\
0  1  a  d\
1  2  b  e\
2  3  c  f\
\
```\
\
See also\
\
`LanceDataset.merge_columns`\
\
Add columns to this Fragment.\
\
Returns:\
\
A new fragment with the merged column(s) and the final schema.\
\
Return type:\
\
Tuple\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment."), LanceSchema\]\
\
merge\_columns(_[value\_func](https://lancedb.github.io/lance/api/python/LanceFragment.merge_columns.html "lance.LanceFragment.merge_columns.value_func"):dict\[str,str\]\|BatchUDF\|ReaderLike\|collections.abc.Callable\[\[pa.RecordBatch\],pa.RecordBatch\]_, _[columns](https://lancedb.github.io/lance/api/python/LanceFragment.merge_columns.html "lance.LanceFragment.merge_columns.columns"):list\[str\]\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python/LanceFragment.merge_columns.html "lance.LanceFragment.merge_columns.batch_size"):int\|None= `None`_, _[reader\_schema](https://lancedb.github.io/lance/api/python/LanceFragment.merge_columns.html "lance.LanceFragment.merge_columns.reader_schema"):pa.Schema\|None= `None`_)→tuple\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment."),LanceSchema\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.merge_columns "Link to this definition")\
\
Add columns to this Fragment.\
\
Warning\
\
Internal API. This method is not intended to be used by end users.\
\
The parameters and their interpretation are the same as in the\
[`lance.dataset.LanceDataset.add_columns()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.add_columns "lance.dataset.LanceDataset.add_columns — Add new columns with defined values.") operation.\
\
The only difference is that, instead of modifying the dataset, a new\
fragment is created. The new schema of the fragment is returned as well.\
These can be used in a later operation to commit the changes to the dataset.\
\
See also\
\
[`lance.dataset.LanceOperation.Merge`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Merge "lance.dataset.LanceOperation.Merge — Operation that adds columns. Unlike Overwrite, this should not change the structure of the fragments, allowing existing indices to be kept.")\
\
The operation used to commit these changes to the dataset. See the doc page for an example of using this API.\
\
Returns:\
\
A new fragment with the added column(s) and the final schema.\
\
Return type:\
\
Tuple\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment."), LanceSchema\]\
\
_property_ metadata:[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.metadata "Link to this definition")\
\
Return the metadata of this fragment.\
\
Return type:\
\
[FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\
\
_property_ num\_deletions:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.num_deletions "Link to this definition")\
\
Return the number of deleted rows in this fragment.\
\
_property_ partition\_expression:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.partition_expression "Link to this definition")\
\
An Expression which evaluates to true for all data viewed by this\
Fragment.\
\
_property_ physical\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.physical_rows "Link to this definition")\
\
Return the number of rows originally in this fragment.\
\
To get the number of rows after deletions, use\
[`count_rows()`](https://lancedb.github.io/lance/api/python/LanceFragment.count_rows.html "lance.LanceFragment.count_rows — Count rows matching the scanner filter.") instead.\
\
_property_ physical\_schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.physical_schema "Link to this definition")\
\
Return the physical schema of this Fragment. This schema can be\
different from the dataset read schema.\
\
scanner(_\*_, _[columns](https://lancedb.github.io/lance/api/python/LanceFragment.scanner.html "lance.LanceFragment.scanner.columns"):list\[str\]\|dict\[str,str\]\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python/LanceFragment.scanner.html "lance.LanceFragment.scanner.batch_size"):int\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python/LanceFragment.scanner.html "lance.LanceFragment.scanner.filter"):str\|pa.compute.Expression\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python/LanceFragment.scanner.html "lance.LanceFragment.scanner.limit"):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python/LanceFragment.scanner.html "lance.LanceFragment.scanner.offset"):int\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python/LanceFragment.scanner.html "lance.LanceFragment.scanner.with_row_id"):bool= `False`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python/LanceFragment.scanner.html "lance.LanceFragment.scanner.with_row_address"):bool= `False`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python/LanceFragment.scanner.html "lance.LanceFragment.scanner.batch_readahead"):int= `16`_)→[LanceScanner](https://lancedb.github.io/lance/api/python/LanceScanner.html "lance.LanceScanner — Initialize self.  See help(type(self)) for accurate signature.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.scanner "Link to this definition")\
\
See Dataset::scanner for details\
\
_property_ schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.schema "Link to this definition")\
\
Return the schema of this fragment.\
\
take(_[self](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.self")_, _[indices](https://lancedb.github.io/lance/api/python/LanceFragment.take.html#p-indices "lance.LanceFragment.take.indices — The indices of row to select in the dataset.")_, _[columns=None](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.columns=None")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/python/LanceFragment.take.html "lance.LanceFragment.take.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.take "Link to this definition")\
\
Select rows of data by index.\
\
Parameters:indices : Array or array-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.take.indices "Permalink to this definition")\
\
The indices of row to select in the dataset.\
\
columns : list of str, default None\
\
The columns to project. This can be a list of column names to\
include (order and duplicates will be preserved), or a dictionary\
with {new\_column\_name: expression} values for more advanced\
projections.\
\
The list of columns or expressions may use the special fields\
\_\_batch\_index (the index of the batch within the fragment),\
\_\_fragment\_index (the index of the fragment within the dataset),\
\_\_last\_in\_fragment (whether the batch is last in fragment), and\
\_\_filename (the name of the source file or a description of the\
source fragment).\
\
The columns will be passed down to Datasets and corresponding data\
fragments to avoid loading, copying, and deserializing columns\
that will not be required further down the compute chain.\
By default all of the available columns are projected. Raises\
an exception if any of the referenced column names does not exist\
in the dataset’s Schema.\
\
filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Return type:\
\
Table\
\
to\_batches(_[self](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.self")_, _[Schemaschema=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.Schema schema=None")_, _[columns=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.columns=None")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_batches.html "lance.LanceFragment.to_batches.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.to_batches "Link to this definition")\
\
Read the fragment as materialized record batches.\
\
Parameters:schema : Schema, optional\
\
Concrete schema to use for scanning.\
\
columns : list of str, default None\
\
The columns to project. This can be a list of column names to\
include (order and duplicates will be preserved), or a dictionary\
with {new\_column\_name: expression} values for more advanced\
projections.\
\
The list of columns or expressions may use the special fields\
\_\_batch\_index (the index of the batch within the fragment),\
\_\_fragment\_index (the index of the fragment within the dataset),\
\_\_last\_in\_fragment (whether the batch is last in fragment), and\
\_\_filename (the name of the source file or a description of the\
source fragment).\
\
The columns will be passed down to Datasets and corresponding data\
fragments to avoid loading, copying, and deserializing columns\
that will not be required further down the compute chain.\
By default all of the available columns are projected. Raises\
an exception if any of the referenced column names does not exist\
in the dataset’s Schema.\
\
filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Returns:\
\
**record\_batches**\
\
Return type:\
\
iterator of RecordBatch\
\
to\_table(_[self](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.self")_, _[Schemaschema=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.Schema schema=None")_, _[columns=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.columns=None")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/python/LanceFragment.to_table.html "lance.LanceFragment.to_table.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceFragment.to_table "Link to this definition")\
\
Convert this Fragment into a Table.\
\
Use this convenience utility with care. This will serially materialize\
the Scan result in memory before creating the Table.\
\
Parameters:schema : Schema, optional\
\
Concrete schema to use for scanning.\
\
columns : list of str, default None\
\
The columns to project. This can be a list of column names to\
include (order and duplicates will be preserved), or a dictionary\
with {new\_column\_name: expression} values for more advanced\
projections.\
\
The list of columns or expressions may use the special fields\
\_\_batch\_index (the index of the batch within the fragment),\
\_\_fragment\_index (the index of the fragment within the dataset),\
\_\_last\_in\_fragment (whether the batch is last in fragment), and\
\_\_filename (the name of the source file or a description of the\
source fragment).\
\
The columns will be passed down to Datasets and corresponding data\
fragments to avoid loading, copying, and deserializing columns\
that will not be required further down the compute chain.\
By default all of the available columns are projected. Raises\
an exception if any of the referenced column names does not exist\
in the dataset’s Schema.\
\
filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Returns:\
\
**table**\
\
Return type:\
\
Table\
\
_class_ lance.LanceOperation [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation "Link to this definition")_class_ Append(_[fragments](https://lancedb.github.io/lance/api/python/LanceOperation.Append.__init__.html "lance.LanceOperation.Append.__init__.fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Append "Link to this definition")\
\
Append new rows to the dataset.\
\
fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Append.fragments "Link to this definition")\
\
The fragments that contain the new rows.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
Warning\
\
This is an advanced API for distributed operations. To append to a\
dataset on a single machine, use [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").\
\
Examples\
\
To append new rows to a dataset, first use\
[`lance.fragment.LanceFragment.create()`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create "lance.fragment.LanceFragment.create — Create a FragmentMetadata from the given data.") to create fragments. Then\
collect the fragment metadata into a list and pass it to this class.\
Finally, pass the operation to the [`LanceDataset.commit()`](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html "lance.LanceDataset.commit — Create a new version of dataset")\
method to create the new dataset.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> tab1 = pa.table({"a": [1, 2], "b": ["a", "b"]})\
>>> dataset = lance.write_dataset(tab1, "example")\
>>> tab2 = pa.table({"a": [3, 4], "b": ["c", "d"]})\
>>> fragment = lance.fragment.LanceFragment.create("example", tab2)\
>>> operation = lance.LanceOperation.Append([fragment])\
>>> dataset = lance.LanceDataset.commit("example", operation,\
...                                     read_version=dataset.version)\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
\
```\
\
fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id10 "Link to this definition")_class_ BaseOperation [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.BaseOperation "Link to this definition")\
\
Base class for operations that can be applied to a dataset.\
\
See available operations under [`LanceOperation`](https://lancedb.github.io/lance/api/python/LanceOperation.html "lance.LanceOperation — Base class for operations that can be applied to a dataset.").\
\
_class_ CreateIndex(_[uuid](https://lancedb.github.io/lance/api/python/LanceOperation.CreateIndex.__init__.html "lance.LanceOperation.CreateIndex.__init__.uuid"):str_, _[name](https://lancedb.github.io/lance/api/python/LanceOperation.CreateIndex.__init__.html "lance.LanceOperation.CreateIndex.__init__.name"):str_, _[fields](https://lancedb.github.io/lance/api/python/LanceOperation.CreateIndex.__init__.html "lance.LanceOperation.CreateIndex.__init__.fields"):list\[int\]_, _[dataset\_version](https://lancedb.github.io/lance/api/python/LanceOperation.CreateIndex.__init__.html "lance.LanceOperation.CreateIndex.__init__.dataset_version"):int_, _[fragment\_ids](https://lancedb.github.io/lance/api/python/LanceOperation.CreateIndex.__init__.html "lance.LanceOperation.CreateIndex.__init__.fragment_ids"):set\[int\]_, _[index\_version](https://lancedb.github.io/lance/api/python/LanceOperation.CreateIndex.__init__.html "lance.LanceOperation.CreateIndex.__init__.index_version"):int_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.CreateIndex "Link to this definition")\
\
Operation that creates an index on the dataset.\
\
dataset\_version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.CreateIndex.dataset_version "Link to this definition")fields:List\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.CreateIndex.fields "Link to this definition")fragment\_ids:Set\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.CreateIndex.fragment_ids "Link to this definition")index\_version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.CreateIndex.index_version "Link to this definition")name:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.CreateIndex.name "Link to this definition")uuid:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.CreateIndex.uuid "Link to this definition")_class_ DataReplacement(_[replacements](https://lancedb.github.io/lance/api/python/LanceOperation.DataReplacement.__init__.html "lance.LanceOperation.DataReplacement.__init__.replacements"):list\[ [DataReplacementGroup](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup "lance.dataset.LanceOperation.DataReplacementGroup — Group of data replacements")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.DataReplacement "Link to this definition")\
\
Operation that replaces existing datafiles in the dataset.\
\
replacements:List\[ [DataReplacementGroup](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup "lance.dataset.LanceOperation.DataReplacementGroup — Group of data replacements")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.DataReplacement.replacements "Link to this definition")_class_ DataReplacementGroup(_[fragment\_id](https://lancedb.github.io/lance/api/python/LanceOperation.DataReplacementGroup.__init__.html "lance.LanceOperation.DataReplacementGroup.__init__.fragment_id"):int_, _[new\_file](https://lancedb.github.io/lance/api/python/LanceOperation.DataReplacementGroup.__init__.html "lance.LanceOperation.DataReplacementGroup.__init__.new_file"):[DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.DataReplacementGroup "Link to this definition")\
\
Group of data replacements\
\
fragment\_id:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.DataReplacementGroup.fragment_id "Link to this definition")new\_file:[DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.DataReplacementGroup.new_file "Link to this definition")_class_ Delete(_[updated\_fragments](https://lancedb.github.io/lance/api/python/LanceOperation.Delete.__init__.html "lance.LanceOperation.Delete.__init__.updated_fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[deleted\_fragment\_ids](https://lancedb.github.io/lance/api/python/LanceOperation.Delete.__init__.html "lance.LanceOperation.Delete.__init__.deleted_fragment_ids"):Iterable\[int\]_, _[predicate](https://lancedb.github.io/lance/api/python/LanceOperation.Delete.__init__.html "lance.LanceOperation.Delete.__init__.predicate"):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Delete "Link to this definition")\
\
Remove fragments or rows from the dataset.\
\
updated\_fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Delete.updated_fragments "Link to this definition")\
\
The fragments that have been updated with new deletion vectors.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
deleted\_fragment\_ids [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Delete.deleted_fragment_ids "Link to this definition")\
\
The ids of the fragments that have been deleted entirely. These are\
the fragments where [`LanceFragment.delete()`](https://lancedb.github.io/lance/api/python/LanceFragment.delete.html "lance.LanceFragment.delete — Delete rows from this Fragment.") returned None.\
\
Type:\
\
list\[int\]\
\
predicate [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Delete.predicate "Link to this definition")\
\
The original SQL predicate used to select the rows to delete.\
\
Type:\
\
str\
\
Warning\
\
This is an advanced API for distributed operations. To delete rows from\
dataset on a single machine, use [`lance.LanceDataset.delete()`](https://lancedb.github.io/lance/api/python/LanceDataset.delete.html "lance.LanceDataset.delete — Delete rows from the dataset.").\
\
Examples\
\
To delete rows from a dataset, call [`lance.fragment.LanceFragment.delete()`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.delete "lance.fragment.LanceFragment.delete — Delete rows from this Fragment.")\
on each of the fragments. If that returns a new fragment, add that to\
the `updated_fragments` list. If it returns None, that means the whole\
fragment was deleted, so add the fragment id to the `deleted_fragment_ids`.\
Finally, pass the operation to the [`LanceDataset.commit()`](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html "lance.LanceDataset.commit — Create a new version of dataset") method to\
complete the deletion operation.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [1, 2], "b": ["a", "b"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> table = pa.table({"a": [3, 4], "b": ["c", "d"]})\
>>> dataset = lance.write_dataset(table, "example", mode="append")\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
>>> predicate = "a >= 2"\
>>> updated_fragments = []\
>>> deleted_fragment_ids = []\
>>> for fragment in dataset.get_fragments():\
...     new_fragment = fragment.delete(predicate)\
...     if new_fragment is not None:\
...         updated_fragments.append(new_fragment)\
...     else:\
...         deleted_fragment_ids.append(fragment.fragment_id)\
>>> operation = lance.LanceOperation.Delete(updated_fragments,\
...                                         deleted_fragment_ids,\
...                                         predicate)\
>>> dataset = lance.LanceDataset.commit("example", operation,\
...                                     read_version=dataset.version)\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
\
```\
\
deleted\_fragment\_ids:Iterable\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id11 "Link to this definition")predicate:str [¶](https://lancedb.github.io/lance/api/py_modules.html#id12 "Link to this definition")updated\_fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id13 "Link to this definition")_class_ Merge(_[fragments](https://lancedb.github.io/lance/api/python/LanceOperation.Merge.__init__.html "lance.LanceOperation.Merge.__init__.fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[schema](https://lancedb.github.io/lance/api/python/LanceOperation.Merge.__init__.html "lance.LanceOperation.Merge.__init__.schema"):LanceSchema\| [Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Merge "Link to this definition")\
\
Operation that adds columns. Unlike Overwrite, this should not change\
the structure of the fragments, allowing existing indices to be kept.\
\
fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Merge.fragments "Link to this definition")\
\
The fragments that make up the new dataset.\
\
Type:\
\
iterable of [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\
\
schema [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Merge.schema "Link to this definition")\
\
The schema of the new dataset. Passing a LanceSchema is preferred,\
and passing a pyarrow.Schema is deprecated.\
\
Type:\
\
LanceSchema or [pyarrow.Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")\
\
Warning\
\
This is an advanced API for distributed operations. To overwrite or\
create new dataset on a single machine, use [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").\
\
Examples\
\
To add new columns to a dataset, first define a method that will create\
the new columns based on the existing columns. Then use\
`lance.fragment.LanceFragment.add_columns()`\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> import pyarrow.compute as pc\
>>> table = pa.table({"a": [1, 2, 3, 4], "b": ["a", "b", "c", "d"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
>>> def double_a(batch: pa.RecordBatch) -> pa.RecordBatch:\
...     doubled = pc.multiply(batch["a"], 2)\
...     return pa.record_batch([doubled], ["a_doubled"])\
>>> fragments = []\
>>> for fragment in dataset.get_fragments():\
...     new_fragment, new_schema = fragment.merge_columns(double_a,\
...                                                       columns=['a'])\
...     fragments.append(new_fragment)\
>>> operation = lance.LanceOperation.Merge(fragments, new_schema)\
>>> dataset = lance.LanceDataset.commit("example", operation,\
...                                     read_version=dataset.version)\
>>> dataset.to_table().to_pandas()\
   a  b  a_doubled\
0  1  a          2\
1  2  b          4\
2  3  c          6\
3  4  d          8\
\
```\
\
fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id14 "Link to this definition")schema:LanceSchema\| [Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#id15 "Link to this definition")_class_ Overwrite(_[new\_schema](https://lancedb.github.io/lance/api/python/LanceOperation.Overwrite.__init__.html "lance.LanceOperation.Overwrite.__init__.new_schema"):LanceSchema\| [Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_, _[fragments](https://lancedb.github.io/lance/api/python/LanceOperation.Overwrite.__init__.html "lance.LanceOperation.Overwrite.__init__.fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Overwrite "Link to this definition")\
\
Overwrite or create a new dataset.\
\
new\_schema [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Overwrite.new_schema "Link to this definition")\
\
The schema of the new dataset.\
\
Type:\
\
[pyarrow.Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")\
\
fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Overwrite.fragments "Link to this definition")\
\
The fragments that make up the new dataset.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
Warning\
\
This is an advanced API for distributed operations. To overwrite or\
create new dataset on a single machine, use [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").\
\
Examples\
\
To create or overwrite a dataset, first use\
[`lance.fragment.LanceFragment.create()`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create "lance.fragment.LanceFragment.create — Create a FragmentMetadata from the given data.") to create fragments. Then\
collect the fragment metadata into a list and pass it along with the\
schema to this class. Finally, pass the operation to the\
[`LanceDataset.commit()`](https://lancedb.github.io/lance/api/python/LanceDataset.commit.html "lance.LanceDataset.commit — Create a new version of dataset") method to create the new dataset.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> tab1 = pa.table({"a": [1, 2], "b": ["a", "b"]})\
>>> tab2 = pa.table({"a": [3, 4], "b": ["c", "d"]})\
>>> fragment1 = lance.fragment.LanceFragment.create("example", tab1)\
>>> fragment2 = lance.fragment.LanceFragment.create("example", tab2)\
>>> fragments = [fragment1, fragment2]\
>>> operation = lance.LanceOperation.Overwrite(tab1.schema, fragments)\
>>> dataset = lance.LanceDataset.commit("example", operation)\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
\
```\
\
fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id16 "Link to this definition")new\_schema:LanceSchema\| [Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#id17 "Link to this definition")_class_ Project(_[schema](https://lancedb.github.io/lance/api/python/LanceOperation.Project.__init__.html "lance.LanceOperation.Project.__init__.schema"):LanceSchema_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Project "Link to this definition")\
\
Operation that project columns.\
Use this operator for drop column or rename/swap column.\
\
schema [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Project.schema "Link to this definition")\
\
The lance schema of the new dataset.\
\
Type:\
\
LanceSchema\
\
Examples\
\
Use the projece operator to swap column:\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> import pyarrow.compute as pc\
>>> from lance.schema import LanceSchema\
>>> table = pa.table({"a": [1, 2], "b": ["a", "b"], "b1": ["c", "d"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> dataset.to_table().to_pandas()\
   a  b b1\
0  1  a  c\
1  2  b  d\
>>>\
>>> ## rename column `b` into `b0` and rename b1 into `b`\
>>> table = pa.table({"a": [3, 4], "b0": ["a", "b"], "b": ["c", "d"]})\
>>> lance_schema = LanceSchema.from_pyarrow(table.schema)\
>>> operation = lance.LanceOperation.Project(lance_schema)\
>>> dataset = lance.LanceDataset.commit("example", operation, read_version=1)\
>>> dataset.to_table().to_pandas()\
   a b0  b\
0  1  a  c\
1  2  b  d\
\
```\
\
schema:LanceSchema [¶](https://lancedb.github.io/lance/api/py_modules.html#id18 "Link to this definition")_class_ Restore(_[version](https://lancedb.github.io/lance/api/python/LanceOperation.Restore.__init__.html "lance.LanceOperation.Restore.__init__.version"):int_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Restore "Link to this definition")\
\
Operation that restores a previous version of the dataset.\
\
version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Restore.version "Link to this definition")_class_ Rewrite(_[groups](https://lancedb.github.io/lance/api/python/LanceOperation.Rewrite.__init__.html "lance.LanceOperation.Rewrite.__init__.groups"):Iterable\[ [RewriteGroup](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup "lance.dataset.LanceOperation.RewriteGroup — Collection of rewritten files")\]_, _[rewritten\_indices](https://lancedb.github.io/lance/api/python/LanceOperation.Rewrite.__init__.html "lance.LanceOperation.Rewrite.__init__.rewritten_indices"):Iterable\[ [RewrittenIndex](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex "lance.dataset.LanceOperation.RewrittenIndex — An index that has been rewritten")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Rewrite "Link to this definition")\
\
Operation that rewrites one or more files and indices into one\
or more files and indices.\
\
groups [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Rewrite.groups "Link to this definition")\
\
Groups of files that have been rewritten.\
\
Type:\
\
list\[ [RewriteGroup](https://lancedb.github.io/lance/api/python/LanceOperation.RewriteGroup.html "lance.LanceOperation.RewriteGroup — Collection of rewritten files")\]\
\
rewritten\_indices [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Rewrite.rewritten_indices "Link to this definition")\
\
Indices that have been rewritten.\
\
Type:\
\
list\[ [RewrittenIndex](https://lancedb.github.io/lance/api/python/LanceOperation.RewrittenIndex.html "lance.LanceOperation.RewrittenIndex — An index that has been rewritten")\]\
\
Warning\
\
This is an advanced API not intended for general use.\
\
groups:Iterable\[ [RewriteGroup](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup "lance.dataset.LanceOperation.RewriteGroup — Collection of rewritten files")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id19 "Link to this definition")rewritten\_indices:Iterable\[ [RewrittenIndex](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex "lance.dataset.LanceOperation.RewrittenIndex — An index that has been rewritten")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id20 "Link to this definition")_class_ RewriteGroup(_[old\_fragments](https://lancedb.github.io/lance/api/python/LanceOperation.RewriteGroup.__init__.html "lance.LanceOperation.RewriteGroup.__init__.old_fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[new\_fragments](https://lancedb.github.io/lance/api/python/LanceOperation.RewriteGroup.__init__.html "lance.LanceOperation.RewriteGroup.__init__.new_fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.RewriteGroup "Link to this definition")\
\
Collection of rewritten files\
\
new\_fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.RewriteGroup.new_fragments "Link to this definition")old\_fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.RewriteGroup.old_fragments "Link to this definition")_class_ RewrittenIndex(_[old\_id](https://lancedb.github.io/lance/api/python/LanceOperation.RewrittenIndex.__init__.html "lance.LanceOperation.RewrittenIndex.__init__.old_id"):str_, _[new\_id](https://lancedb.github.io/lance/api/python/LanceOperation.RewrittenIndex.__init__.html "lance.LanceOperation.RewrittenIndex.__init__.new_id"):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.RewrittenIndex "Link to this definition")\
\
An index that has been rewritten\
\
new\_id:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.RewrittenIndex.new_id "Link to this definition")old\_id:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.RewrittenIndex.old_id "Link to this definition")_class_ Update(_[removed\_fragment\_ids](https://lancedb.github.io/lance/api/python/LanceOperation.Update.__init__.html "lance.LanceOperation.Update.__init__.removed_fragment_ids"):list\[int\]_, _[updated\_fragments](https://lancedb.github.io/lance/api/python/LanceOperation.Update.__init__.html "lance.LanceOperation.Update.__init__.updated_fragments"):list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[new\_fragments](https://lancedb.github.io/lance/api/python/LanceOperation.Update.__init__.html "lance.LanceOperation.Update.__init__.new_fragments"):list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[fields\_modified](https://lancedb.github.io/lance/api/python/LanceOperation.Update.__init__.html "lance.LanceOperation.Update.__init__.fields_modified"):list\[int\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Update "Link to this definition")\
\
Operation that updates rows in the dataset.\
\
removed\_fragment\_ids [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Update.removed_fragment_ids "Link to this definition")\
\
The ids of the fragments that have been removed entirely.\
\
Type:\
\
list\[int\]\
\
updated\_fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Update.updated_fragments "Link to this definition")\
\
The fragments that have been updated with new deletion vectors.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
new\_fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Update.new_fragments "Link to this definition")\
\
The fragments that contain the new rows.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
fields\_modified [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceOperation.Update.fields_modified "Link to this definition")\
\
If any fields are modified in updated\_fragments, then they must be\
listed here so those fragments can be removed from indices covering\
those fields.\
\
Type:\
\
list\[int\]\
\
fields\_modified:List\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id21 "Link to this definition")new\_fragments:List\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id22 "Link to this definition")removed\_fragment\_ids:List\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id23 "Link to this definition")updated\_fragments:List\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id24 "Link to this definition")_class_ lance.LanceScanner(_[scanner](https://lancedb.github.io/lance/api/python/LanceScanner.__init__.html "lance.LanceScanner.__init__.scanner"):\_Scanner_, _[dataset](https://lancedb.github.io/lance/api/python/LanceScanner.__init__.html "lance.LanceScanner.__init__.dataset"):[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner "Link to this definition")analyze\_plan()→str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.analyze_plan "Link to this definition")\
\
Execute the plan for this scanner and display with runtime metrics.\
\
Parameters:verbose : bool, default False\
\
Use a verbose output format.\
\
Returns:\
\
**plan**\
\
Return type:\
\
str\
\
count\_rows() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.count_rows "Link to this definition")\
\
Count rows matching the scanner filter.\
\
Returns:\
\
**count**\
\
Return type:\
\
int\
\
_property_ dataset\_schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.dataset_schema "Link to this definition")\
\
The schema with which batches will be read from fragments.\
\
explain\_plan(_[verbose](https://lancedb.github.io/lance/api/python/LanceScanner.explain_plan.html#p-verbose "lance.LanceScanner.explain_plan.verbose — Use a verbose output format.") = `False`_)→str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.explain_plan "Link to this definition")\
\
Return the execution plan for this scanner.\
\
Parameters:verbose : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.explain_plan.verbose "Permalink to this definition")\
\
Use a verbose output format.\
\
Returns:\
\
**plan**\
\
Return type:\
\
str\
\
_static_ from\_batches(_\* [args](https://lancedb.github.io/lance/api/python/LanceScanner.from_batches.html "lance.LanceScanner.from_batches.args")_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceScanner.from_batches.html "lance.LanceScanner.from_batches.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.from_batches "Link to this definition")\
\
Not implemented\
\
_static_ from\_dataset(_\* [args](https://lancedb.github.io/lance/api/python/LanceScanner.from_dataset.html "lance.LanceScanner.from_dataset.args")_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceScanner.from_dataset.html "lance.LanceScanner.from_dataset.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.from_dataset "Link to this definition")\
\
Not implemented\
\
_static_ from\_fragment(_\* [args](https://lancedb.github.io/lance/api/python/LanceScanner.from_fragment.html "lance.LanceScanner.from_fragment.args")_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python/LanceScanner.from_fragment.html "lance.LanceScanner.from_fragment.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.from_fragment "Link to this definition")\
\
Not implemented\
\
head(_[num\_rows](https://lancedb.github.io/lance/api/python/LanceScanner.head.html#p-num_rows "lance.LanceScanner.head.num_rows — The number of rows to load.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.head "Link to this definition")\
\
Load the first N rows of the dataset.\
\
Parameters:num\_rows : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.head.num_rows "Permalink to this definition")\
\
The number of rows to load.\
\
Return type:\
\
Table\
\
_property_ projected\_schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.projected_schema "Link to this definition")\
\
The materialized schema of the data, accounting for projections.\
\
This is the schema of any data returned from the scanner.\
\
scan\_batches() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.scan_batches "Link to this definition")\
\
Consume a Scanner in record batches with corresponding fragments.\
\
Returns:\
\
**record\_batches**\
\
Return type:\
\
iterator of TaggedRecordBatch\
\
take(_[indices](https://lancedb.github.io/lance/api/python/LanceScanner.take.html "lance.LanceScanner.take.indices")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.take "Link to this definition")\
\
Not implemented\
\
to\_batches(_[self](https://lancedb.github.io/lance/api/python/LanceScanner.to_batches.html "lance.LanceScanner.to_batches.self")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.to_batches "Link to this definition")\
\
Consume a Scanner in record batches.\
\
Returns:\
\
**record\_batches**\
\
Return type:\
\
iterator of RecordBatch\
\
to\_reader(_[self](https://lancedb.github.io/lance/api/python/LanceScanner.to_reader.html "lance.LanceScanner.to_reader.self")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.to_reader "Link to this definition")\
\
Consume this scanner as a RecordBatchReader.\
\
Return type:\
\
RecordBatchReader\
\
to\_table()→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.LanceScanner.to_table "Link to this definition")\
\
Read the data into memory and return a pyarrow Table.\
\
_class_ lance.MergeInsertBuilder(_[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder "lance.MergeInsertBuilder.__init__.dataset")_, _[on](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder "lance.MergeInsertBuilder.__init__.on")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder "Link to this definition")conflict\_retries(_[max\_retries](https://lancedb.github.io/lance/api/python/MergeInsertBuilder.conflict_retries.html "lance.MergeInsertBuilder.conflict_retries.max_retries"):int_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.conflict_retries "Link to this definition")\
\
Set number of times to retry the operation if there is contention.\
\
If this is set > 0, then the operation will keep a copy of the input data\
either in memory or on disk (depending on the size of the data) and will\
retry the operation if there is contention.\
\
Default is 10.\
\
execute(_[data\_obj](https://lancedb.github.io/lance/api/python/MergeInsertBuilder.execute.html#p-data_obj "lance.MergeInsertBuilder.execute.data_obj — The new data to use as the source table for the operation."):ReaderLike_, _\*_, _[schema](https://lancedb.github.io/lance/api/python/MergeInsertBuilder.execute.html#p-schema "lance.MergeInsertBuilder.execute.schema — The schema of the data."):pa.Schema\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.execute "Link to this definition")\
\
Executes the merge insert operation\
\
This function updates the original dataset and returns a dictionary with\
information about merge statistics - i.e. the number of inserted, updated,\
and deleted rows.\
\
Parameters:data\_obj : ReaderLike [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.execute.data_obj "Permalink to this definition")\
\
The new data to use as the source table for the operation. This parameter\
can be any source of data (e.g. table / dataset) that\
[`write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") accepts.\
\
schema : Optional\[pa.Schema\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.execute.schema "Permalink to this definition")\
\
The schema of the data. This only needs to be supplied whenever the data\
source is some kind of generator.\
\
execute\_uncommitted(_[data\_obj](https://lancedb.github.io/lance/api/python/MergeInsertBuilder.execute_uncommitted.html#p-data_obj "lance.MergeInsertBuilder.execute_uncommitted.data_obj — The new data to use as the source table for the operation."):ReaderLike_, _\*_, _[schema](https://lancedb.github.io/lance/api/python/MergeInsertBuilder.execute_uncommitted.html#p-schema "lance.MergeInsertBuilder.execute_uncommitted.schema — The schema of the data."):pa.Schema\|None= `None`_)→tuple\[ [Transaction](https://lancedb.github.io/lance/api/python/Transaction.html "lance.Transaction — Initialize self.  See help(type(self)) for accurate signature."),dict\[str,Any\]\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.execute_uncommitted "Link to this definition")\
\
Executes the merge insert operation without committing\
\
This function updates the original dataset and returns a dictionary with\
information about merge statistics - i.e. the number of inserted, updated,\
and deleted rows.\
\
Parameters:data\_obj : ReaderLike [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.execute_uncommitted.data_obj "Permalink to this definition")\
\
The new data to use as the source table for the operation. This parameter\
can be any source of data (e.g. table / dataset) that\
[`write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") accepts.\
\
schema : Optional\[pa.Schema\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.execute_uncommitted.schema "Permalink to this definition")\
\
The schema of the data. This only needs to be supplied whenever the data\
source is some kind of generator.\
\
retry\_timeout(_[timeout](https://lancedb.github.io/lance/api/python/MergeInsertBuilder.retry_timeout.html "lance.MergeInsertBuilder.retry_timeout.timeout"):timedelta_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.retry_timeout "Link to this definition")\
\
Set the timeout used to limit retries.\
\
This is the maximum time to spend on the operation before giving up. At\
least one attempt will be made, regardless of how long it takes to complete.\
Subsequent attempts will be cancelled once this timeout is reached. If\
the timeout has been reached during the first attempt, the operation\
will be cancelled immediately before making a second attempt.\
\
The default is 30 seconds.\
\
when\_matched\_update\_all(_[condition](https://lancedb.github.io/lance/api/python/MergeInsertBuilder.when_matched_update_all.html "lance.MergeInsertBuilder.when_matched_update_all.condition"):str\|None= `None`_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.when_matched_update_all "Link to this definition")\
\
Configure the operation to update matched rows\
\
After this method is called, when the merge insert operation executes,\
any rows that match both the source table and the target table will be\
updated. The rows from the target table will be removed and the rows\
from the source table will be added.\
\
An optional condition may be specified. This should be an SQL filter\
and, if present, then only matched rows that also satisfy this filter will\
be updated. The SQL filter should use the prefix target. to refer to\
columns in the target table and the prefix source. to refer to columns\
in the source table. For example, source.last\_update < target.last\_update.\
\
If a condition is specified and rows do not satisfy the condition then these\
rows will not be updated. Failure to satisfy the filter does not cause\
a “matched” row to become a “not matched” row.\
\
when\_not\_matched\_by\_source\_delete(_[expr](https://lancedb.github.io/lance/api/python/MergeInsertBuilder.when_not_matched_by_source_delete.html "lance.MergeInsertBuilder.when_not_matched_by_source_delete.expr"):str\|None= `None`_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.when_not_matched_by_source_delete "Link to this definition")\
\
Configure the operation to delete source rows that do not match\
\
After this method is called, when the merge insert operation executes,\
any rows that exist only in the target table will be deleted. An\
optional filter can be specified to limit the scope of the delete\
operation. If given (as an SQL filter) then only rows which match\
the filter will be deleted.\
\
when\_not\_matched\_insert\_all()→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.MergeInsertBuilder.when_not_matched_insert_all "Link to this definition")\
\
Configure the operation to insert not matched rows\
\
After this method is called, when the merge insert operation executes,\
any rows that exist only in the source table will be inserted into\
the target table.\
\
_class_ lance.ScanStatistics [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics "Link to this definition")\
\
Statistics about the scan.\
\
bytes\_read [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics.bytes_read "Link to this definition")\
\
Number of bytes read from disk\
\
indices\_loaded [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics.indices_loaded "Link to this definition")\
\
Number of indices loaded\
\
iops [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics.iops "Link to this definition")\
\
Number of IO operations performed. This may be slightly higher than\
the actual number due to coalesced I/O\
\
parts\_loaded [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics.parts_loaded "Link to this definition")\
\
Number of index partitions loaded\
\
_class_ lance.Transaction(_[read\_version:'int'](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction "lance.Transaction.__init__.read_version: 'int'")_, _[operation:'LanceOperation.BaseOperation'](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction "lance.Transaction.__init__.operation: 'LanceOperation.BaseOperation'")_, _[uuid:'str'=<factory>](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction "lance.Transaction.__init__.uuid: 'str' = <factory>")_, _[blobs\_op:'Optional\[LanceOperation.BaseOperation\]'=None](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction "lance.Transaction.__init__.blobs_op: 'Optional[LanceOperation.BaseOperation]' = None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction "Link to this definition")blobs\_op:[BaseOperation](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.BaseOperation "lance.dataset.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") \|None=`None` [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction.blobs_op "Link to this definition")operation:[BaseOperation](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.BaseOperation "lance.dataset.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction.operation "Link to this definition")read\_version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction.read_version "Link to this definition")uuid:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.Transaction.uuid "Link to this definition")lance.batch\_udf(_[output\_schema](https://lancedb.github.io/lance/api/python/batch_udf.html#p-output_schema "lance.batch_udf.output_schema — The schema of the output RecordBatch.") = `None`_, _[checkpoint\_file](https://lancedb.github.io/lance/api/python/batch_udf.html#p-checkpoint_file "lance.batch_udf.checkpoint_file — If specified, this file will be used as a cache for unsaved results of this UDF.") = `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.batch_udf "Link to this definition")\
\
Create a user defined function (UDF) that adds columns to a dataset.\
\
This function is used to add columns to a dataset. It takes a function that\
takes a single argument, a RecordBatch, and returns a RecordBatch. The\
function is called once for each batch in the dataset. The function should\
not modify the input batch, but instead create a new batch with the new\
columns added.\
\
Parameters:output\_schema : Schema, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.batch_udf.output_schema "Permalink to this definition")\
\
The schema of the output RecordBatch. This is used to validate the\
output of the function. If not provided, the schema of the first output\
RecordBatch will be used.\
\
checkpoint\_file : str or Path, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.batch_udf.checkpoint_file "Permalink to this definition")\
\
If specified, this file will be used as a cache for unsaved results of\
this UDF. If the process fails, and you call add\_columns again with this\
same file, it will resume from the last saved state. This is useful for\
long running processes that may fail and need to be resumed. This file\
may get very large. It will hold up to an entire data files’ worth of\
results on disk, which can be multiple gigabytes of data.\
\
Return type:\
\
AddColumnsUDF\
\
lance.bytes\_read\_counter() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.bytes_read_counter "Link to this definition")lance.dataset(_[uri](https://lancedb.github.io/lance/api/python/dataset.html#p-uri "lance.dataset.uri — Address to the Lance dataset."):str\|Path_, _[version](https://lancedb.github.io/lance/api/python/dataset.html#p-version "lance.dataset.version — If specified, load a specific version of the Lance dataset."):int\|str\|None= `None`_, _[asof](https://lancedb.github.io/lance/api/python/dataset.html#p-asof "lance.dataset.asof — If specified, find the latest version created on or earlier than the given argument value."):ts\_types\|None= `None`_, _[block\_size](https://lancedb.github.io/lance/api/python/dataset.html#p-block_size "lance.dataset.block_size — Block size in bytes."):int\|None= `None`_, _[commit\_lock](https://lancedb.github.io/lance/api/python/dataset.html#p-commit_lock "lance.dataset.commit_lock — A custom commit lock."):CommitLock\|None= `None`_, _[index\_cache\_size](https://lancedb.github.io/lance/api/python/dataset.html#p-index_cache_size "lance.dataset.index_cache_size — Index cache size."):int\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python/dataset.html#p-storage_options "lance.dataset.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[default\_scan\_options](https://lancedb.github.io/lance/api/python/dataset.html#p-default_scan_options "lance.dataset.default_scan_options — Default scan options that are used when scanning the dataset."):dict\[str,str\]\|None= `None`_)→[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset "Link to this definition")\
\
Opens the Lance dataset from the address specified.\
\
Parameters:uri : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.uri "Permalink to this definition")\
\
Address to the Lance dataset. It can be a local file path /tmp/data.lance,\
or a cloud object store URI, i.e., s3://bucket/data.lance.\
\
version : optional, int \| str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.version "Permalink to this definition")\
\
If specified, load a specific version of the Lance dataset. Else, loads the\
latest version. A version number (int) or a tag (str) can be provided.\
\
asof : optional, datetime or str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.asof "Permalink to this definition")\
\
If specified, find the latest version created on or earlier than the given\
argument value. If a version is already specified, this arg is ignored.\
\
block\_size : optional, int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.block_size "Permalink to this definition")\
\
Block size in bytes. Provide a hint for the size of the minimal I/O request.\
\
commit\_lock : optional, lance.commit.CommitLock [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.commit_lock "Permalink to this definition")\
\
A custom commit lock. Only needed if your object store does not support\
atomic commits. See the user guide for more details.\
\
index\_cache\_size : optional, int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.index_cache_size "Permalink to this definition")\
\
Index cache size. Index cache is a LRU cache with TTL. This number specifies the\
number of index pages, for example, IVF partitions, to be cached in\
the host memory. Default value is `256`.\
\
Roughly, for an `IVF_PQ` partition with `n` rows, the size of each index\
page equals the combination of the pq code ( `nd.array([n,pq], dtype=uint8))`\
and the row ids ( `nd.array([n], dtype=uint64)`).\
Approximately, `n = Total Rows / number of IVF partitions`.\
`pq = number of PQ sub-vectors`.\
\
storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.storage_options "Permalink to this definition")\
\
Extra options that make sense for a particular storage connection. This is\
used to store connection parameters like credentials, endpoint, etc.\
\
default\_scan\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.default_scan_options "Permalink to this definition")\
\
Default scan options that are used when scanning the dataset. This accepts\
the same arguments described in [`lance.LanceDataset.scanner()`](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html "lance.LanceDataset.scanner — Return a Scanner that can support various pushdowns."). The\
arguments will be applied to any scan operation.\
\
This can be useful to supply defaults for common parameters such as\
`batch_size`.\
\
It can also be used to create a view of the dataset that includes meta\
fields such as `_rowid` or `_rowaddr`. If `default_scan_options` is\
provided then the schema returned by [`lance.LanceDataset.schema()`](https://lancedb.github.io/lance/api/python/LanceDataset.schema.html "lance.LanceDataset.schema — The pyarrow Schema for this dataset") will\
include these fields if the appropriate scan options are set.\
\
lance.iops\_counter() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.iops_counter "Link to this definition")lance.json\_to\_schema(_[schema\_json](https://lancedb.github.io/lance/api/python/json_to_schema.html#p-schema_json "lance.json_to_schema.schema_json — The JSON payload to convert to a PyArrow Schema."):dict\[str,Any\]_)→[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.json_to_schema "Link to this definition")\
\
Converts a JSON string to a PyArrow schema.\
\
Parameters:schema\_json : Dict\[str, Any\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.json_to_schema.schema_json "Permalink to this definition")\
\
The JSON payload to convert to a PyArrow Schema.\
\
lance.schema\_to\_json(_[schema](https://lancedb.github.io/lance/api/python/schema_to_json.html "lance.schema_to_json.schema"):[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_)→dict\[str,Any\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.schema_to_json "Link to this definition")\
\
Converts a pyarrow schema to a JSON string.\
\
lance.set\_logger(_[file\_path](https://lancedb.github.io/lance/api/python/set_logger.html "lance.set_logger.file_path") = `'pylance.log'`_, _[name](https://lancedb.github.io/lance/api/python/set_logger.html "lance.set_logger.name") = `'pylance'`_, _[level](https://lancedb.github.io/lance/api/python/set_logger.html "lance.set_logger.level") = `20`_, _[format\_string](https://lancedb.github.io/lance/api/python/set_logger.html "lance.set_logger.format_string") = `None`_, _[log\_handler](https://lancedb.github.io/lance/api/python/set_logger.html "lance.set_logger.log_handler") = `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.set_logger "Link to this definition")lance.write\_dataset(_[data\_obj](https://lancedb.github.io/lance/api/python/write_dataset.html#p-data_obj "lance.write_dataset.data_obj — The data to be written."):ReaderLike_, _[uri](https://lancedb.github.io/lance/api/python/write_dataset.html#p-uri "lance.write_dataset.uri — Where to write the dataset to (directory)."):str\|Path\| [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[schema](https://lancedb.github.io/lance/api/python/write_dataset.html#p-schema "lance.write_dataset.schema — If specified and the input is a pandas DataFrame, use this schema instead of the default pandas to arrow table conversion."):pa.Schema\|None= `None`_, _[mode](https://lancedb.github.io/lance/api/python/write_dataset.html#p-mode "lance.write_dataset.mode — create - create a new dataset (raises if uri already exists). overwrite - create a new snapshot version append - create a new version that is the concat of the input the latest version (raises if uri does not exist)"):str= `'create'`_, _\*_, _[max\_rows\_per\_file](https://lancedb.github.io/lance/api/python/write_dataset.html#p-max_rows_per_file "lance.write_dataset.max_rows_per_file — The max number of rows to write before starting a new file"):int= `1048576`_, _[max\_rows\_per\_group](https://lancedb.github.io/lance/api/python/write_dataset.html#p-max_rows_per_group "lance.write_dataset.max_rows_per_group — The max number of rows before starting a new group (in the same file)"):int= `1024`_, _[max\_bytes\_per\_file](https://lancedb.github.io/lance/api/python/write_dataset.html#p-max_bytes_per_file "lance.write_dataset.max_bytes_per_file — The max number of bytes to write before starting a new file."):int= `96636764160`_, _[commit\_lock](https://lancedb.github.io/lance/api/python/write_dataset.html#p-commit_lock "lance.write_dataset.commit_lock — A custom commit lock."):CommitLock\|None= `None`_, _[progress](https://lancedb.github.io/lance/api/python/write_dataset.html#p-progress "lance.write_dataset.progress — Experimental API."):FragmentWriteProgress\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python/write_dataset.html#p-storage_options "lance.write_dataset.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[data\_storage\_version](https://lancedb.github.io/lance/api/python/write_dataset.html#p-data_storage_version "lance.write_dataset.data_storage_version — The version of the data storage format to use."):str\|None= `None`_, _[use\_legacy\_format](https://lancedb.github.io/lance/api/python/write_dataset.html#p-use_legacy_format "lance.write_dataset.use_legacy_format — Deprecated method for setting the data storage version."):bool\|None= `None`_, _[enable\_v2\_manifest\_paths](https://lancedb.github.io/lance/api/python/write_dataset.html#p-enable_v2_manifest_paths "lance.write_dataset.enable_v2_manifest_paths — If True, and this is a new dataset, uses the new V2 manifest paths. These paths provide more efficient opening of datasets with many versions on object stores."):bool= `False`_, _[enable\_move\_stable\_row\_ids](https://lancedb.github.io/lance/api/python/write_dataset.html#p-enable_move_stable_row_ids "lance.write_dataset.enable_move_stable_row_ids — Experimental parameter: if set to true, the writer will use move-stable row ids. These row ids are stable after compaction operations, but not after updates. This makes compaction more efficient, since with stable row ids no secondary indices need to be updated to point to new row ids."):bool= `False`_, _[auto\_cleanup\_options](https://lancedb.github.io/lance/api/python/write_dataset.html#p-auto_cleanup_options "lance.write_dataset.auto_cleanup_options — Config options for automatic cleanup of the dataset. If set, and this is a new dataset, old dataset versions will be automatically cleaned up according to this parameter. To add autocleaning to an existing dataset, use Dataset::update_config to set lance.auto_cleanup.interval and lance.auto_cleanup.older_than. Both parameters must be set to invoke autocleaning. If you do not set this parameter(default behavior), then no autocleaning will be performed. Note: this option only takes effect when creating a new dataset, it has no effect on existing datasets."):[AutoCleanupConfig](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AutoCleanupConfig "lance.dataset.AutoCleanupConfig — interval : int      older_than_seconds : int") \|None= `None`_)→[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset "Link to this definition")\
\
Write a given data\_obj to the given uri\
\
Parameters:data\_obj : Reader-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.data_obj "Permalink to this definition")\
\
The data to be written. Acceptable types are:\
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner, or RecordBatchReader\
\- Huggingface dataset\
\
uri : str, Path, or [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.uri "Permalink to this definition")\
\
Where to write the dataset to (directory). If a LanceDataset is passed,\
the session will be reused.\
\
schema : Schema, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.schema "Permalink to this definition")\
\
If specified and the input is a pandas DataFrame, use this schema\
instead of the default pandas to arrow table conversion.\
\
mode : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.mode "Permalink to this definition")\
\
**create** \- create a new dataset (raises if uri already exists).\
**overwrite** \- create a new snapshot version\
**append** \- create a new version that is the concat of the input the\
latest version (raises if uri does not exist)\
\
max\_rows\_per\_file : int, default 1024 \* 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.max_rows_per_file "Permalink to this definition")\
\
The max number of rows to write before starting a new file\
\
max\_rows\_per\_group : int, default 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.max_rows_per_group "Permalink to this definition")\
\
The max number of rows before starting a new group (in the same file)\
\
max\_bytes\_per\_file : int, default 90 \* 1024 \* 1024 \* 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.max_bytes_per_file "Permalink to this definition")\
\
The max number of bytes to write before starting a new file. This is a\
soft limit. This limit is checked after each group is written, which\
means larger groups may cause this to be overshot meaningfully. This\
defaults to 90 GB, since we have a hard limit of 100 GB per file on\
object stores.\
\
commit\_lock : CommitLock, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.commit_lock "Permalink to this definition")\
\
A custom commit lock. Only needed if your object store does not support\
atomic commits. See the user guide for more details.\
\
progress : FragmentWriteProgress, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.progress "Permalink to this definition")\
\
_Experimental API_. Progress tracking for writing the fragment. Pass\
a custom class that defines hooks to be called when each fragment is\
starting to write and finishing writing.\
\
storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.storage_options "Permalink to this definition")\
\
Extra options that make sense for a particular storage connection. This is\
used to store connection parameters like credentials, endpoint, etc.\
\
data\_storage\_version : optional, str, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.data_storage_version "Permalink to this definition")\
\
The version of the data storage format to use. Newer versions are more\
efficient but require newer versions of lance to read. The default (None)\
will use the latest stable version. See the user guide for more details.\
\
use\_legacy\_format : optional, bool, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.use_legacy_format "Permalink to this definition")\
\
Deprecated method for setting the data storage version. Use the\
data\_storage\_version parameter instead.\
\
enable\_v2\_manifest\_paths : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.enable_v2_manifest_paths "Permalink to this definition")\
\
If True, and this is a new dataset, uses the new V2 manifest paths.\
These paths provide more efficient opening of datasets with many\
versions on object stores. This parameter has no effect if the dataset\
already exists. To migrate an existing dataset, instead use the\
[`LanceDataset.migrate_manifest_paths_v2()`](https://lancedb.github.io/lance/api/python/LanceDataset.migrate_manifest_paths_v2.html "lance.LanceDataset.migrate_manifest_paths_v2 — Migrate the manifest paths to the new format.") method. Default is False.\
\
enable\_move\_stable\_row\_ids : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.enable_move_stable_row_ids "Permalink to this definition")\
\
Experimental parameter: if set to true, the writer will use move-stable row ids.\
These row ids are stable after compaction operations, but not after updates.\
This makes compaction more efficient, since with stable row ids no\
secondary indices need to be updated to point to new row ids.\
\
auto\_cleanup\_options : optional, [AutoCleanupConfig](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AutoCleanupConfig "lance.dataset.AutoCleanupConfig — interval : int      older_than_seconds : int") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.write_dataset.auto_cleanup_options "Permalink to this definition")\
\
Config options for automatic cleanup of the dataset.\
If set, and this is a new dataset, old dataset versions will be automatically\
cleaned up according to this parameter.\
To add autocleaning to an existing dataset, use Dataset::update\_config to set\
lance.auto\_cleanup.interval and lance.auto\_cleanup.older\_than.\
Both parameters must be set to invoke autocleaning.\
If you do not set this parameter(default behavior),\
then no autocleaning will be performed.\
Note: this option only takes effect when creating a new dataset,\
it has no effect on existing datasets.\
\
_class_ lance.dataset.AlterColumn [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AlterColumn "Link to this definition")data\_type:[DataType](https://arrow.apache.org/docs/python/generated/pyarrow.DataType.html#pyarrow.DataType "(in Apache Arrow v20.0.0)") \|None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AlterColumn.data_type "Link to this definition")name:str\|None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AlterColumn.name "Link to this definition")nullable:bool\|None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AlterColumn.nullable "Link to this definition")path:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AlterColumn.path "Link to this definition")_class_ lance.dataset.AutoCleanupConfig [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AutoCleanupConfig "Link to this definition")interval:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AutoCleanupConfig.interval "Link to this definition")older\_than\_seconds:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AutoCleanupConfig.older_than_seconds "Link to this definition")_class_ lance.dataset.BulkCommitResult [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.BulkCommitResult "Link to this definition")dataset:[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.BulkCommitResult.dataset "Link to this definition")merged:[Transaction](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction — blobs_op : BaseOperation | None = None      operation : BaseOperation      read_version : int      uuid : str") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.BulkCommitResult.merged "Link to this definition")_class_ lance.dataset.DataStatistics(_[fields](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DataStatistics "lance.dataset.DataStatistics.__init__.fields"):[FieldStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics "lance.dataset.FieldStatistics — Statistics about a field in the dataset")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DataStatistics "Link to this definition")\
\
Statistics about the data in the dataset\
\
fields:[FieldStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics "lance.dataset.FieldStatistics — Statistics about a field in the dataset") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DataStatistics.fields "Link to this definition")\
\
Statistics about the fields in the dataset\
\
_class_ lance.dataset.DatasetOptimizer(_[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer "lance.dataset.DatasetOptimizer.__init__.dataset"):[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer "Link to this definition")compact\_files(_\*_, _[target\_rows\_per\_fragment](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.target_rows_per_fragment "lance.dataset.DatasetOptimizer.compact_files.target_rows_per_fragment — The target number of rows per fragment."):int= `1048576`_, _[max\_rows\_per\_group](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.max_rows_per_group "lance.dataset.DatasetOptimizer.compact_files.max_rows_per_group — Max number of rows per group."):int= `1024`_, _[max\_bytes\_per\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.max_bytes_per_file "lance.dataset.DatasetOptimizer.compact_files.max_bytes_per_file — Max number of bytes in a single file."):int\|None= `None`_, _[materialize\_deletions](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.materialize_deletions "lance.dataset.DatasetOptimizer.compact_files.materialize_deletions — Whether to compact fragments with soft deleted rows so they are no longer present in the file."):bool= `True`_, _[materialize\_deletions\_threshold](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.materialize_deletions_threshold "lance.dataset.DatasetOptimizer.compact_files.materialize_deletions_threshold — The fraction of original rows that are soft deleted in a fragment before the fragment is a candidate for compaction."):float= `0.1`_, _[num\_threads](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.num_threads "lance.dataset.DatasetOptimizer.compact_files.num_threads — The number of threads to use when performing compaction."):int\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.batch_size "lance.dataset.DatasetOptimizer.compact_files.batch_size — The batch size to use when scanning input fragments."):int\|None= `None`_)→CompactionMetrics [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files "Link to this definition")\
\
Compacts small files in the dataset, reducing total number of files.\
\
This does a few things:\
\
- Removes deleted rows from fragments\
\
- Removes dropped columns from fragments\
\
- Merges small fragments into larger ones\
\
\
This method preserves the insertion order of the dataset. This may mean\
it leaves small fragments in the dataset if they are not adjacent to\
other fragments that need compaction. For example, if you have fragments\
with row counts 5 million, 100, and 5 million, the middle fragment will\
not be compacted because the fragments it is adjacent to do not need\
compaction.\
\
Parameters:target\_rows\_per\_fragment : int, default 1024\*1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.target_rows_per_fragment "Permalink to this definition")\
\
The target number of rows per fragment. This is the number of rows\
that will be in each fragment after compaction.\
\
max\_rows\_per\_group : int, default 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.max_rows_per_group "Permalink to this definition")\
\
Max number of rows per group. This does not affect which fragments\
need compaction, but does affect how they are re-written if selected.\
\
This setting only affects datasets using the legacy storage format.\
The newer format does not require row groups.\
\
max\_bytes\_per\_file : Optional\[int\], default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.max_bytes_per_file "Permalink to this definition")\
\
Max number of bytes in a single file. This does not affect which\
fragments need compaction, but does affect how they are re-written if\
selected. If this value is too small you may end up with fragments\
that are smaller than target\_rows\_per\_fragment.\
\
The default will use the default from `write_dataset`.\
\
materialize\_deletions : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.materialize_deletions "Permalink to this definition")\
\
Whether to compact fragments with soft deleted rows so they are no\
longer present in the file.\
\
materialize\_deletions\_threshold : float, default 0.1 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.materialize_deletions_threshold "Permalink to this definition")\
\
The fraction of original rows that are soft deleted in a fragment\
before the fragment is a candidate for compaction.\
\
num\_threads : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.num_threads "Permalink to this definition")\
\
The number of threads to use when performing compaction. If not\
specified, defaults to the number of cores on the machine.\
\
batch\_size : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files.batch_size "Permalink to this definition")\
\
The batch size to use when scanning input fragments. You may want\
to reduce this if you are running out of memory during compaction.\
\
The default will use the same default from `scanner`.\
\
Returns:\
\
Metrics about the compaction process\
\
Return type:\
\
CompactionMetrics\
\
See also\
\
`lance.optimize.Compaction`\
\
optimize\_indices(_\*\* [kwargs](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.optimize_indices "lance.dataset.DatasetOptimizer.optimize_indices.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.optimize_indices "Link to this definition")\
\
Optimizes index performance.\
\
As new data arrives it is not added to existing indexes automatically.\
When searching we need to perform an indexed search of the old data plus\
an expensive unindexed search on the new data. As the amount of new\
unindexed data grows this can have an impact on search latency.\
This function will add the new data to existing indexes, restoring the\
performance. This function does not retrain the index, it only assigns\
the new data to existing partitions. This means an update is much quicker\
than retraining the entire index but may have less accuracy (especially\
if the new data exhibits new patterns, concepts, or trends)\
\
Parameters:num\_indices\_to\_merge : int, default 1\
\
The number of indices to merge.\
If set to 0, new delta index will be created.\
\
index\_names : List\[str\], default None\
\
The names of the indices to optimize.\
If None, all indices will be optimized.\
\
retrain : bool, default False\
\
Whether to retrain the whole index.\
If true, the index will be retrained based on the current data,\
num\_indices\_to\_merge will be ignored,\
and all indices will be merged into one.\
\
This is useful when the data distribution has changed significantly,\
and we want to retrain the index to improve the search quality.\
This would be faster than re-create the index from scratch.\
\
_class_ lance.dataset.DatasetStats [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetStats "Link to this definition")num\_deleted\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetStats.num_deleted_rows "Link to this definition")num\_fragments:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetStats.num_fragments "Link to this definition")num\_small\_files:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetStats.num_small_files "Link to this definition")_class_ lance.dataset.ExecuteResult [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ExecuteResult "Link to this definition")num\_deleted\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ExecuteResult.num_deleted_rows "Link to this definition")num\_inserted\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ExecuteResult.num_inserted_rows "Link to this definition")num\_updated\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ExecuteResult.num_updated_rows "Link to this definition")_class_ lance.dataset.FieldStatistics(_[id](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics "lance.dataset.FieldStatistics.__init__.id"):int_, _[bytes\_on\_disk](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics "lance.dataset.FieldStatistics.__init__.bytes_on_disk"):int_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics "Link to this definition")\
\
Statistics about a field in the dataset\
\
bytes\_on\_disk:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics.bytes_on_disk "Link to this definition")\
\
(possibly compressed) bytes on disk used to store the field\
\
id:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.FieldStatistics.id "Link to this definition")\
\
id of the field\
\
_class_ lance.dataset.Index [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index "Link to this definition")fields:List\[str\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index.fields "Link to this definition")fragment\_ids:Set\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index.fragment_ids "Link to this definition")name:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index.name "Link to this definition")type:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index.type "Link to this definition")uuid:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index.uuid "Link to this definition")version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index.version "Link to this definition")_class_ lance.dataset.LanceDataset(_[uri](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.uri"):str\|Path_, _[version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.version"):int\|str\|None= `None`_, _[block\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.block_size"):int\|None= `None`_, _[index\_cache\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.index_cache_size"):int\|None= `None`_, _[metadata\_cache\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.metadata_cache_size"):int\|None= `None`_, _[commit\_lock](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.commit_lock"):CommitLock\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.storage_options"):dict\[str,str\]\|None= `None`_, _[serialized\_manifest](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.serialized_manifest"):bytes\|None= `None`_, _[default\_scan\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset.__init__.default_scan_options"):dict\[str,Any\]\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "Link to this definition")\
\
A Lance Dataset in Lance format where the data is stored at the given uri.\
\
add\_columns(_[transforms](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.transforms "lance.dataset.LanceDataset.add_columns.transforms — If this is a dictionary, then the keys are the names of the new columns and the values are SQL expression strings."):dict\[str,str\]\|BatchUDF\|ReaderLike\| [pyarrow.Field](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)") \|list\[ [pyarrow.Field](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)")\]\| [pyarrow.Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_, _[read\_columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.read_columns "lance.dataset.LanceDataset.add_columns.read_columns — The names of the columns that the UDF will read."):list\[str\]\|None= `None`_, _[reader\_schema](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.reader_schema "lance.dataset.LanceDataset.add_columns.reader_schema — Only valid if transforms is a ReaderLike object."):pa.Schema\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.batch_size "lance.dataset.LanceDataset.add_columns.batch_size — The number of rows to read at a time from the source dataset when applying the transform."):int\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.add_columns "Link to this definition")\
\
Add new columns with defined values.\
\
There are several ways to specify the new columns. First, you can provide\
SQL expressions for each new column. Second you can provide a UDF that\
takes a batch of existing data and returns a new batch with the new\
columns. These new columns will be appended to the dataset.\
\
You can also provide a RecordBatchReader which will read the new column\
values from some external source. This is often useful when the new column\
values have already been staged to files (often by some distributed process)\
\
See the `lance.add_columns_udf()` decorator for more information on\
writing UDFs.\
\
Parameters:transforms : dict or AddColumnsUDF or ReaderLike [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.add_columns.transforms "Permalink to this definition")\
\
If this is a dictionary, then the keys are the names of the new\
columns and the values are SQL expression strings. These strings can\
reference existing columns in the dataset.\
If this is a AddColumnsUDF, then it is a UDF that takes a batch of\
existing data and returns a new batch with the new columns.\
If this is [`pyarrow.Field`](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)") or [`pyarrow.Schema`](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)"), it adds\
all NULL columns with the given schema, in a metadata-only operation.\
\
read\_columns : list of str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.add_columns.read_columns "Permalink to this definition")\
\
The names of the columns that the UDF will read. If None, then the\
UDF will read all columns. This is only used when transforms is a\
UDF. Otherwise, the read columns are inferred from the SQL expressions.\
\
reader\_schema : pa.Schema, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.add_columns.reader_schema "Permalink to this definition")\
\
Only valid if transforms is a ReaderLike object. This will be used to\
determine the schema of the reader.\
\
batch\_size : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.add_columns.batch_size "Permalink to this definition")\
\
The number of rows to read at a time from the source dataset when applying\
the transform. This is ignored if the dataset is a v1 dataset.\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [1, 2, 3]})\
>>> dataset = lance.write_dataset(table, "my_dataset")\
>>> @lance.batch_udf()\
... def double_a(batch):\
...     df = batch.to_pandas()\
...     return pd.DataFrame({'double_a': 2 * df['a']})\
>>> dataset.add_columns(double_a)\
>>> dataset.to_table().to_pandas()\
   a  double_a\
0  1         2\
1  2         4\
2  3         6\
>>> dataset.add_columns({"triple_a": "a * 3"})\
>>> dataset.to_table().to_pandas()\
   a  double_a  triple_a\
0  1         2         3\
1  2         4         6\
2  3         6         9\
\
```\
\
See also\
\
[`LanceDataset.merge`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge "lance.dataset.LanceDataset.merge — Merge another dataset into this one.")\
\
Merge a pre-computed set of columns into the dataset.\
\
alter\_columns(_\* [alterations](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.alter_columns.alterations "lance.dataset.LanceDataset.alter_columns.alterations — A sequence of dictionaries, each with the following keys:"):Iterable\[ [AlterColumn](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AlterColumn "lance.dataset.AlterColumn — data_type : DataType | None      name : str | None      nullable : bool | None      path : str")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.alter_columns "Link to this definition")\
\
Alter column name, data type, and nullability.\
\
Columns that are renamed can keep any indices that are on them. If a\
column has an IVF\_PQ index, it can be kept if the column is casted to\
another type. However, other index types don’t support casting at this\
time.\
\
Column types can be upcasted (such as int32 to int64) or downcasted\
(such as int64 to int32). However, downcasting will fail if there are\
any values that cannot be represented in the new type. In general,\
columns can be casted to same general type: integers to integers,\
floats to floats, and strings to strings. However, strings, binary, and\
list columns can be casted between their size variants. For example,\
string to large string, binary to large binary, and list to large list.\
\
Columns that are renamed can keep any indices that are on them. However, if\
the column is casted to a different type, its indices will be dropped.\
\
Parameters:alterations : Iterable\[Dict\[str, Any\]\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.alter_columns.alterations "Permalink to this definition")\
\
A sequence of dictionaries, each with the following keys:\
\
- ”path”: str\
\
The column path to alter. For a top-level column, this is the name.\
For a nested column, this is the dot-separated path, e.g. “a.b.c”.\
\
- ”name”: str, optional\
\
The new name of the column. If not specified, the column name is\
not changed.\
\
- ”nullable”: bool, optional\
\
Whether the column should be nullable. If not specified, the column\
nullability is not changed. Only non-nullable columns can be changed\
to nullable. Currently, you cannot change a nullable column to\
non-nullable.\
\
- ”data\_type”: pyarrow.DataType, optional\
\
The new data type to cast the column to. If not specified, the column\
data type is not changed.\
\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> schema = pa.schema([pa.field('a', pa.int64()),\
...                     pa.field('b', pa.string(), nullable=False)])\
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> dataset.alter_columns({"path": "a", "name": "x"},\
...                       {"path": "b", "nullable": True})\
>>> dataset.to_table().to_pandas()\
   x  b\
0  1  a\
1  2  b\
2  3  c\
>>> dataset.alter_columns({"path": "x", "data_type": pa.int32()})\
>>> dataset.schema\
x: int32\
b: string\
\
```\
\
checkout\_version(_[version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.checkout_version.version "lance.dataset.LanceDataset.checkout_version.version — The version to check out."):int\|str_)→[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.checkout_version "Link to this definition")\
\
Load the given version of the dataset.\
\
Unlike the `dataset()` constructor, this will re-use the\
current cache.\
This is a no-op if the dataset is already at the given version.\
\
Parameters:version : int \| str, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.checkout_version.version "Permalink to this definition")\
\
The version to check out. A version number (int) or a tag\
(str) can be provided.\
\
Return type:\
\
[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")\
\
cleanup\_old\_versions(_[older\_than](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.cleanup_old_versions.older_than "lance.dataset.LanceDataset.cleanup_old_versions.older_than — Only versions older than this will be removed."):timedelta\|None= `None`_, _\*_, _[delete\_unverified](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.cleanup_old_versions.delete_unverified "lance.dataset.LanceDataset.cleanup_old_versions.delete_unverified — Files leftover from a failed transaction may appear to be part of an in-progress operation (e.g."):bool= `False`_, _[error\_if\_tagged\_old\_versions](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.cleanup_old_versions.error_if_tagged_old_versions "lance.dataset.LanceDataset.cleanup_old_versions.error_if_tagged_old_versions — Some versions may have tags associated with them."):bool= `True`_)→CleanupStats [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.cleanup_old_versions "Link to this definition")\
\
Cleans up old versions of the dataset.\
\
Some dataset changes, such as overwriting, leave behind data that is not\
referenced by the latest dataset version. The old data is left in place\
to allow the dataset to be restored back to an older version.\
\
This method will remove older versions and any data files they reference.\
Once this cleanup task has run you will not be able to checkout or restore\
these older versions.\
\
Parameters:older\_than : timedelta, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.cleanup_old_versions.older_than "Permalink to this definition")\
\
Only versions older than this will be removed. If not specified, this\
will default to two weeks.\
\
delete\_unverified : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.cleanup_old_versions.delete_unverified "Permalink to this definition")\
\
Files leftover from a failed transaction may appear to be part of an\
in-progress operation (e.g. appending new data) and these files will\
not be deleted unless they are at least 7 days old. If delete\_unverified\
is True then these files will be deleted regardless of their age.\
\
This should only be set to True if you can guarantee that no other process\
is currently working on this dataset. Otherwise the dataset could be put\
into a corrupted state.\
\
error\_if\_tagged\_old\_versions : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.cleanup_old_versions.error_if_tagged_old_versions "Permalink to this definition")\
\
Some versions may have tags associated with them. Tagged versions will\
not be cleaned up, regardless of how old they are. If this argument\
is set to True (the default), an exception will be raised if any\
tagged versions match the parameters. Otherwise, tagged versions will\
be ignored without any error and only untagged versions will be\
cleaned up.\
\
_static_ commit(_[base\_uri](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.base_uri "lance.dataset.LanceDataset.commit.base_uri — The base uri of the dataset, or the dataset object itself."):str\|Path\| [LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[operation](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.operation "lance.dataset.LanceDataset.commit.operation — The operation to apply to the dataset."):[LanceOperation.BaseOperation](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.BaseOperation "lance.dataset.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") \| [Transaction](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction — blobs_op : BaseOperation | None = None      operation : BaseOperation      read_version : int      uuid : str")_, _[blobs\_op](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit "lance.dataset.LanceDataset.commit.blobs_op"):[LanceOperation.BaseOperation](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.BaseOperation "lance.dataset.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") \|None= `None`_, _[read\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.read_version "lance.dataset.LanceDataset.commit.read_version — The version of the dataset that was used as the base for the changes. This is not needed for overwrite or restore operations."):int\|None= `None`_, _[commit\_lock](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.commit_lock "lance.dataset.LanceDataset.commit.commit_lock — A custom commit lock."):CommitLock\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.storage_options "lance.dataset.LanceDataset.commit.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[enable\_v2\_manifest\_paths](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.enable_v2_manifest_paths "lance.dataset.LanceDataset.commit.enable_v2_manifest_paths — If True, and this is a new dataset, uses the new V2 manifest paths. These paths provide more efficient opening of datasets with many versions on object stores."):bool\|None= `None`_, _[detached](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.detached "lance.dataset.LanceDataset.commit.detached — If True, then the commit will not be part of the dataset lineage."):bool\|None= `False`_, _[max\_retries](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.max_retries "lance.dataset.LanceDataset.commit.max_retries — The maximum number of retries to perform when committing the dataset."):int= `20`_)→[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit "Link to this definition")\
\
Create a new version of dataset\
\
This method is an advanced method which allows users to describe a change\
that has been made to the data files. This method is not needed when using\
Lance to apply changes (e.g. when using [`LanceDataset`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") or\
[`write_dataset()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset "lance.dataset.write_dataset — Write a given data_obj to the given uri").)\
\
It’s current purpose is to allow for changes being made in a distributed\
environment where no single process is doing all of the work. For example,\
a distributed bulk update or a distributed bulk modify operation.\
\
Once all of the changes have been made, this method can be called to make\
the changes visible by updating the dataset manifest.\
\
Warning\
\
This is an advanced API and doesn’t provide the same level of validation\
as the other APIs. For example, it’s the responsibility of the caller to\
ensure that the fragments are valid for the schema.\
\
Parameters:base\_uri : str, Path, or [LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.base_uri "Permalink to this definition")\
\
The base uri of the dataset, or the dataset object itself. Using\
the dataset object can be more efficient because it can re-use the\
file metadata cache.\
\
operation : [BaseOperation](https://lancedb.github.io/lance/api/python/LanceOperation.BaseOperation.html "lance.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.operation "Permalink to this definition")\
\
The operation to apply to the dataset. This describes what changes\
have been made. See available operations under [`LanceOperation`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation "lance.dataset.LanceOperation — Append new rows to the dataset.").\
\
read\_version : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.read_version "Permalink to this definition")\
\
The version of the dataset that was used as the base for the changes.\
This is not needed for overwrite or restore operations.\
\
commit\_lock : CommitLock, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.commit_lock "Permalink to this definition")\
\
A custom commit lock. Only needed if your object store does not support\
atomic commits. See the user guide for more details.\
\
storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.storage_options "Permalink to this definition")\
\
Extra options that make sense for a particular storage connection. This is\
used to store connection parameters like credentials, endpoint, etc.\
\
enable\_v2\_manifest\_paths : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.enable_v2_manifest_paths "Permalink to this definition")\
\
If True, and this is a new dataset, uses the new V2 manifest paths.\
These paths provide more efficient opening of datasets with many\
versions on object stores. This parameter has no effect if the dataset\
already exists. To migrate an existing dataset, instead use the\
[`migrate_manifest_paths_v2()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.migrate_manifest_paths_v2 "lance.dataset.LanceDataset.migrate_manifest_paths_v2 — Migrate the manifest paths to the new format.") method. Default is False. WARNING:\
turning this on will make the dataset unreadable for older versions\
of Lance (prior to 0.17.0).\
\
detached : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.detached "Permalink to this definition")\
\
If True, then the commit will not be part of the dataset lineage. It will\
never show up as the latest dataset and the only way to check it out in the\
future will be to specifically check it out by version. The version will be\
a random version that is only unique amongst detached commits. The caller\
should store this somewhere as there will be no other way to obtain it in\
the future.\
\
max\_retries : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit.max_retries "Permalink to this definition")\
\
The maximum number of retries to perform when committing the dataset.\
\
Returns:\
\
A new version of Lance Dataset.\
\
Return type:\
\
[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")\
\
Examples\
\
Creating a new dataset with the [`LanceOperation.Overwrite`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Overwrite "lance.dataset.LanceOperation.Overwrite — Overwrite or create a new dataset.") operation:\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> tab1 = pa.table({"a": [1, 2], "b": ["a", "b"]})\
>>> tab2 = pa.table({"a": [3, 4], "b": ["c", "d"]})\
>>> fragment1 = lance.fragment.LanceFragment.create("example", tab1)\
>>> fragment2 = lance.fragment.LanceFragment.create("example", tab2)\
>>> fragments = [fragment1, fragment2]\
>>> operation = lance.LanceOperation.Overwrite(tab1.schema, fragments)\
>>> dataset = lance.LanceDataset.commit("example", operation)\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
\
```\
\
_static_ commit\_batch(_[dest](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.dest "lance.dataset.LanceDataset.commit_batch.dest — The base uri of the dataset, or the dataset object itself."):str\|Path\| [LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[transactions](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.transactions "lance.dataset.LanceDataset.commit_batch.transactions — The transactions to apply to the dataset."):collections.abc.Sequence\[ [Transaction](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction — blobs_op : BaseOperation | None = None      operation : BaseOperation      read_version : int      uuid : str")\]_, _[commit\_lock](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.commit_lock "lance.dataset.LanceDataset.commit_batch.commit_lock — A custom commit lock."):CommitLock\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.storage_options "lance.dataset.LanceDataset.commit_batch.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[enable\_v2\_manifest\_paths](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.enable_v2_manifest_paths "lance.dataset.LanceDataset.commit_batch.enable_v2_manifest_paths — If True, and this is a new dataset, uses the new V2 manifest paths. These paths provide more efficient opening of datasets with many versions on object stores."):bool\|None= `None`_, _[detached](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.detached "lance.dataset.LanceDataset.commit_batch.detached — If True, then the commit will not be part of the dataset lineage."):bool\|None= `False`_, _[max\_retries](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.max_retries "lance.dataset.LanceDataset.commit_batch.max_retries — The maximum number of retries to perform when committing the dataset."):int= `20`_)→[BulkCommitResult](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.BulkCommitResult "lance.dataset.BulkCommitResult — dataset : LanceDataset      merged : Transaction") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch "Link to this definition")\
\
Create a new version of dataset with multiple transactions.\
\
This method is an advanced method which allows users to describe a change\
that has been made to the data files. This method is not needed when using\
Lance to apply changes (e.g. when using [`LanceDataset`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") or\
[`write_dataset()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset "lance.dataset.write_dataset — Write a given data_obj to the given uri").)\
\
Parameters:dest : str, Path, or [LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.dest "Permalink to this definition")\
\
The base uri of the dataset, or the dataset object itself. Using\
the dataset object can be more efficient because it can re-use the\
file metadata cache.\
\
transactions : Iterable\[ [Transaction](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction — blobs_op : BaseOperation | None = None      operation : BaseOperation      read_version : int      uuid : str")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.transactions "Permalink to this definition")\
\
The transactions to apply to the dataset. These will be merged into\
a single transaction and applied to the dataset. Note: Only append\
transactions are currently supported. Other transaction types will be\
supported in the future.\
\
commit\_lock : CommitLock, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.commit_lock "Permalink to this definition")\
\
A custom commit lock. Only needed if your object store does not support\
atomic commits. See the user guide for more details.\
\
storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.storage_options "Permalink to this definition")\
\
Extra options that make sense for a particular storage connection. This is\
used to store connection parameters like credentials, endpoint, etc.\
\
enable\_v2\_manifest\_paths : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.enable_v2_manifest_paths "Permalink to this definition")\
\
If True, and this is a new dataset, uses the new V2 manifest paths.\
These paths provide more efficient opening of datasets with many\
versions on object stores. This parameter has no effect if the dataset\
already exists. To migrate an existing dataset, instead use the\
[`migrate_manifest_paths_v2()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.migrate_manifest_paths_v2 "lance.dataset.LanceDataset.migrate_manifest_paths_v2 — Migrate the manifest paths to the new format.") method. Default is False. WARNING:\
turning this on will make the dataset unreadable for older versions\
of Lance (prior to 0.17.0).\
\
detached : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.detached "Permalink to this definition")\
\
If True, then the commit will not be part of the dataset lineage. It will\
never show up as the latest dataset and the only way to check it out in the\
future will be to specifically check it out by version. The version will be\
a random version that is only unique amongst detached commits. The caller\
should store this somewhere as there will be no other way to obtain it in\
the future.\
\
max\_retries : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit_batch.max_retries "Permalink to this definition")\
\
The maximum number of retries to perform when committing the dataset.\
\
Returns:\
\
dataset: LanceDataset\
\
A new version of Lance Dataset.\
\
merged: Transaction\
\
The merged transaction that was applied to the dataset.\
\
Return type:\
\
dict with keys\
\
count\_rows(_[filter](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.count_rows "lance.dataset.LanceDataset.count_rows.filter"):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.count_rows.kwargs "lance.dataset.LanceDataset.count_rows.kwargs — See py:method:scanner method for full parameter description.")_)→int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.count_rows "Link to this definition")\
\
Count rows matching the scanner filter.\
\
Parameters:\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.count_rows.kwargs "Permalink to this definition")\
\
See py:method:scanner method for full parameter description.\
\
Returns:\
\
**count** – The total number of rows in the dataset.\
\
Return type:\
\
int\
\
create\_index(_[column](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.column "lance.dataset.LanceDataset.create_index.column — The column to be indexed."):str\|list\[str\]_, _[index\_type](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.index_type "lance.dataset.LanceDataset.create_index.index_type — The type of the index. \"IVF_PQ, IVF_HNSW_PQ and IVF_HNSW_SQ\" are supported now."):str_, _[name](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.name "lance.dataset.LanceDataset.create_index.name — The index name."):str\|None= `None`_, _[metric](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.metric "lance.dataset.LanceDataset.create_index.metric — The distance metric type, i.e., \"L2\" (alias to \"euclidean\"), \"cosine\" or \"dot\" (dot product)."):str= `'L2'`_, _[replace](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.replace "lance.dataset.LanceDataset.create_index.replace — Replace the existing index if it exists."):bool= `False`_, _[num\_partitions](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.num_partitions "lance.dataset.LanceDataset.create_index.num_partitions — The number of partitions of IVF (Inverted File Index)."):int\|None= `None`_, _[ivf\_centroids](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.ivf_centroids "lance.dataset.LanceDataset.create_index.ivf_centroids — It can be either np.ndarray, pyarrow.FixedSizeListArray or pyarrow.FixedShapeTensorArray. A num_partitions x dimension array of existing K-mean centroids for IVF clustering."):np.ndarray\|pa.FixedSizeListArray\|pa.FixedShapeTensorArray\|None= `None`_, _[pq\_codebook](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.pq_codebook "lance.dataset.LanceDataset.create_index.pq_codebook — It can be np.ndarray, pyarrow.FixedSizeListArray, or pyarrow.FixedShapeTensorArray. A num_sub_vectors x (2 ^ nbits * dimensions // num_sub_vectors) array of K-mean centroids for PQ codebook."):np.ndarray\|pa.FixedSizeListArray\|pa.FixedShapeTensorArray\|None= `None`_, _[num\_sub\_vectors](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.num_sub_vectors "lance.dataset.LanceDataset.create_index.num_sub_vectors — The number of sub-vectors for PQ (Product Quantization)."):int\|None= `None`_, _[accelerator](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.accelerator "lance.dataset.LanceDataset.create_index.accelerator — If set, use an accelerator to speed up the training process. Accepted accelerator: \"cuda\" (Nvidia GPU) and \"mps\" (Apple Silicon GPU). If not set, use the CPU."):str\|'torch.Device'\|None= `None`_, _[index\_cache\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.index_cache_size "lance.dataset.LanceDataset.create_index.index_cache_size — The size of the index cache in number of entries."):int\|None= `None`_, _[shuffle\_partition\_batches](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.shuffle_partition_batches "lance.dataset.LanceDataset.create_index.shuffle_partition_batches — The number of batches, using the row group size of the dataset, to include in each shuffle partition."):int\|None= `None`_, _[shuffle\_partition\_concurrency](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.shuffle_partition_concurrency "lance.dataset.LanceDataset.create_index.shuffle_partition_concurrency — The number of shuffle partitions to process concurrently."):int\|None= `None`_, _[ivf\_centroids\_file](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.create_index.ivf_centroids_file"):str\|None= `None`_, _[precomputed\_partition\_dataset](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.create_index.precomputed_partition_dataset"):str\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.storage_options "lance.dataset.LanceDataset.create_index.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[filter\_nan](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.filter_nan "lance.dataset.LanceDataset.create_index.filter_nan — Defaults to True."):bool= `True`_, _[one\_pass\_ivfpq](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.one_pass_ivfpq "lance.dataset.LanceDataset.create_index.one_pass_ivfpq — Defaults to False."):bool= `False`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.kwargs "lance.dataset.LanceDataset.create_index.kwargs — Parameters passed to the index building process.")_)→[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index "Link to this definition")\
\
Create index on column.\
\
**Experimental API**\
\
Parameters:column : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.column "Permalink to this definition")\
\
The column to be indexed.\
\
index\_type : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.index_type "Permalink to this definition")\
\
The type of the index.\
`"IVF_PQ, IVF_HNSW_PQ and IVF_HNSW_SQ"` are supported now.\
\
name : str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.name "Permalink to this definition")\
\
The index name. If not provided, it will be generated from the\
column name.\
\
metric : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.metric "Permalink to this definition")\
\
The distance metric type, i.e., “L2” (alias to “euclidean”), “cosine”\
or “dot” (dot product). Default is “L2”.\
\
replace : bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.replace "Permalink to this definition")\
\
Replace the existing index if it exists.\
\
num\_partitions : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.num_partitions "Permalink to this definition")\
\
The number of partitions of IVF (Inverted File Index).\
\
ivf\_centroids : optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.ivf_centroids "Permalink to this definition")\
\
It can be either `np.ndarray`,\
[`pyarrow.FixedSizeListArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedSizeListArray.html#pyarrow.FixedSizeListArray "(in Apache Arrow v20.0.0)") or\
[`pyarrow.FixedShapeTensorArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedShapeTensorArray.html#pyarrow.FixedShapeTensorArray "(in Apache Arrow v20.0.0)").\
A `num_partitions x dimension` array of existing K-mean centroids\
for IVF clustering. If not provided, a new KMeans model will be trained.\
\
pq\_codebook : optional, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.pq_codebook "Permalink to this definition")\
\
It can be `np.ndarray`, [`pyarrow.FixedSizeListArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedSizeListArray.html#pyarrow.FixedSizeListArray "(in Apache Arrow v20.0.0)"),\
or [`pyarrow.FixedShapeTensorArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedShapeTensorArray.html#pyarrow.FixedShapeTensorArray "(in Apache Arrow v20.0.0)").\
A `num_sub_vectors x (2 ^ nbits * dimensions // num_sub_vectors)`\
array of K-mean centroids for PQ codebook.\
\
Note: `nbits` is always 8 for now.\
If not provided, a new PQ model will be trained.\
\
num\_sub\_vectors : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.num_sub_vectors "Permalink to this definition")\
\
The number of sub-vectors for PQ (Product Quantization).\
\
accelerator:str\|'torch.Device'\|None= `None` [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.accelerator "Permalink to this definition")\
\
If set, use an accelerator to speed up the training process.\
Accepted accelerator: “cuda” (Nvidia GPU) and “mps” (Apple Silicon GPU).\
If not set, use the CPU.\
\
index\_cache\_size : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.index_cache_size "Permalink to this definition")\
\
The size of the index cache in number of entries. Default value is 256.\
\
shuffle\_partition\_batches : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.shuffle_partition_batches "Permalink to this definition")\
\
The number of batches, using the row group size of the dataset, to include\
in each shuffle partition. Default value is 10240.\
\
Assuming the row group size is 1024, each shuffle partition will hold\
10240 \* 1024 = 10,485,760 rows. By making this value smaller, this shuffle\
will consume less memory but will take longer to complete, and vice versa.\
\
shuffle\_partition\_concurrency : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.shuffle_partition_concurrency "Permalink to this definition")\
\
The number of shuffle partitions to process concurrently. Default value is 2\
\
By making this value smaller, this shuffle will consume less memory but will\
take longer to complete, and vice versa.\
\
storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.storage_options "Permalink to this definition")\
\
Extra options that make sense for a particular storage connection. This is\
used to store connection parameters like credentials, endpoint, etc.\
\
filter\_nan : bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.filter_nan "Permalink to this definition")\
\
Defaults to True. False is UNSAFE, and will cause a crash if any null/nan\
values are present (and otherwise will not). Disables the null filter used\
for nullable columns. Obtains a small speed boost.\
\
one\_pass\_ivfpq : bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.one_pass_ivfpq "Permalink to this definition")\
\
Defaults to False. If enabled, index type must be “IVF\_PQ”. Reduces disk IO.\
\
\*\*kwargs [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_index.kwargs "Permalink to this definition")\
\
Parameters passed to the index building process.\
\
The SQ (Scalar Quantization) is available for only `IVF_HNSW_SQ` index type,\
this quantization method is used to reduce the memory usage of the index,\
it maps the float vectors to integer vectors, each integer is of `num_bits`,\
now only 8 bits are supported.\
\
If `index_type` is “IVF\_\*”, then the following parameters are required:\
\
num\_partitions\
\
If `index_type` is with “PQ”, then the following parameters are required:\
\
num\_sub\_vectors\
\
Optional parameters for IVF\_PQ:\
\
> - ivf\_centroids\
>\
> Existing K-mean centroids for IVF clustering.\
>\
> - num\_bits\
>\
> The number of bits for PQ (Product Quantization). Default is 8.\
> Only 4, 8 are supported.\
\
Optional parameters for IVF\_HNSW\_\*:max\_level\
\
Int, the maximum number of levels in the graph.\
\
m\
\
Int, the number of edges per node in the graph.\
\
ef\_construction\
\
Int, the number of nodes to examine during the construction.\
\
Examples\
\
```\
import lance\
\
dataset = lance.dataset("/tmp/sift.lance")\
dataset.create_index(\
    "vector",\
    "IVF_PQ",\
    num_partitions=256,\
    num_sub_vectors=16\
)\
\
```\
\
```\
import lance\
\
dataset = lance.dataset("/tmp/sift.lance")\
dataset.create_index(\
    "vector",\
    "IVF_HNSW_SQ",\
    num_partitions=256,\
)\
\
```\
\
Experimental Accelerator (GPU) support:\
\
- _accelerate_: use GPU to train IVF partitions.\
\
Only supports CUDA (Nvidia) or MPS (Apple) currently.\
Requires PyTorch being installed.\
\
\
```\
import lance\
\
dataset = lance.dataset("/tmp/sift.lance")\
dataset.create_index(\
    "vector",\
    "IVF_PQ",\
    num_partitions=256,\
    num_sub_vectors=16,\
    accelerator="cuda"\
)\
\
```\
\
References\
\
- [Faiss Index](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)\
\
- IVF introduced in [Video Google: a text retrieval approach to object matching\\
in videos](https://ieeexplore.ieee.org/abstract/document/1238663)\
\
- [Product quantization for nearest neighbor search](https://hal.inria.fr/inria-00514462v2/document)\
\
\
create\_scalar\_index(_[column](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.column "lance.dataset.LanceDataset.create_scalar_index.column — The column to be indexed."):str_, _[index\_type](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.index_type "lance.dataset.LanceDataset.create_scalar_index.index_type — The type of the index."):'BTREE'\|'BITMAP'\|'LABEL\_LIST'\|'INVERTED'\|'FTS'\|'NGRAM'_, _[name](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.name "lance.dataset.LanceDataset.create_scalar_index.name — The index name."):str\|None= `None`_, _\*_, _[replace](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.replace "lance.dataset.LanceDataset.create_scalar_index.replace — Replace the existing index if it exists."):bool= `True`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.create_scalar_index.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_scalar_index "Link to this definition")\
\
Create a scalar index on a column.\
\
Scalar indices, like vector indices, can be used to speed up scans. A scalar\
index can speed up scans that contain filter expressions on the indexed column.\
For example, the following scan will be faster if the column `my_col` has\
a scalar index:\
\
```\
import lance\
\
dataset = lance.dataset("/tmp/images.lance")\
my_table = dataset.scanner(filter="my_col != 7").to_table()\
\
```\
\
Vector search with pre-filers can also benefit from scalar indices. For example,\
\
```\
import lance\
\
dataset = lance.dataset("/tmp/images.lance")\
my_table = dataset.scanner(\
    nearest=dict(\
       column="vector",\
       q=[1, 2, 3, 4],\
       k=10,\
    )\
    filter="my_col != 7",\
    prefilter=True\
)\
\
```\
\
There are 5 types of scalar indices available today.\
\
- `BTREE`. The most common type is `BTREE`. This index is inspired\
by the btree data structure although only the first few layers of the btree\
are cached in memory. It will\
perform well on columns with a large number of unique values and few rows per\
value.\
\
- `BITMAP`. This index stores a bitmap for each unique value in the column.\
This index is useful for columns with a small number of unique values and\
many rows per value.\
\
- `LABEL_LIST`. A special index that is used to index list\
columns whose values have small cardinality. For example, a column that\
contains lists of tags (e.g. `["tag1", "tag2", "tag3"]`) can be indexed\
with a `LABEL_LIST` index. This index can only speedup queries with\
`array_has_any` or `array_has_all` filters.\
\
- `NGRAM`. A special index that is used to index string columns. This index\
creates a bitmap for each ngram in the string. By default we use trigrams.\
This index can currently speed up queries using the `contains` function\
in filters.\
\
- `FTS/INVERTED`. It is used to index document columns. This index\
can conduct full-text searches. For example, a column that contains any word\
of query string “hello world”. The results will be ranked by BM25.\
\
\
Note that the `LANCE_BYPASS_SPILLING` environment variable can be used to\
bypass spilling to disk. Setting this to true can avoid memory exhaustion\
issues (see [https://github.com/apache/datafusion/issues/10073](https://github.com/apache/datafusion/issues/10073) for more info).\
\
**Experimental API**\
\
Parameters:column : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_scalar_index.column "Permalink to this definition")\
\
The column to be indexed. Must be a boolean, integer, float,\
or string column.\
\
index\_type : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_scalar_index.index_type "Permalink to this definition")\
\
The type of the index. One of `"BTREE"`, `"BITMAP"`,\
`"LABEL_LIST"`, `"NGRAM"`, `"FTS"` or `"INVERTED"`.\
\
name : str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_scalar_index.name "Permalink to this definition")\
\
The index name. If not provided, it will be generated from the\
column name.\
\
replace : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.create_scalar_index.replace "Permalink to this definition")\
\
Replace the existing index if it exists.\
\
with\_position : bool, default True\
\
This is for the `INVERTED` index. If True, the index will store the\
positions of the words in the document, so that you can conduct phrase\
query. This will significantly increase the index size.\
It won’t impact the performance of non-phrase queries even if it is set to\
True.\
\
base\_tokenizer : str, default "simple"\
\
This is for the `INVERTED` index. The base tokenizer to use. The value\
can be:\
\\* “simple”: splits tokens on whitespace and punctuation.\
\\* “whitespace”: splits tokens on whitespace.\
\\* “raw”: no tokenization.\
\
language : str, default "English"\
\
This is for the `INVERTED` index. The language for stemming\
and stop words. This is only used when stem or remove\_stop\_words is true\
\
max\_token\_length : Optional\[int\], default 40\
\
This is for the `INVERTED` index. The maximum token length.\
Any token longer than this will be removed.\
\
lower\_case : bool, default True\
\
This is for the `INVERTED` index. If True, the index will convert all\
text to lowercase.\
\
stem : bool, default False\
\
This is for the `INVERTED` index. If True, the index will stem the\
tokens.\
\
remove\_stop\_words : bool, default False\
\
This is for the `INVERTED` index. If True, the index will remove\
stop words.\
\
ascii\_folding : bool, default False\
\
This is for the `INVERTED` index. If True, the index will convert\
non-ascii characters to ascii characters if possible.\
This would remove accents like “é” -> “e”.\
\
Examples\
\
```\
import lance\
\
dataset = lance.dataset("/tmp/images.lance")\
dataset.create_index(\
    "category",\
    "BTREE",\
)\
\
```\
\
Scalar indices can only speed up scans for basic filters using\
equality, comparison, range (e.g. `my_col BETWEEN 0 AND 100`), and set\
membership (e.g. my\_col IN (0, 1, 2))\
\
Scalar indices can be used if the filter contains multiple indexed columns and\
the filter criteria are AND’d or OR’d together\
(e.g. `my_col < 0 AND other_col> 100`)\
\
Scalar indices may be used if the filter contains non-indexed columns but,\
depending on the structure of the filter, they may not be usable. For example,\
if the column `not_indexed` does not have a scalar index then the filter\
`my_col = 0 OR not_indexed = 1` will not be able to use any scalar index on\
`my_col`.\
\
To determine if a scan is making use of a scalar index you can use\
`explain_plan` to look at the query plan that lance has created. Queries\
that use scalar indices will either have a `ScalarIndexQuery` relation or a\
`MaterializeIndex` operator.\
\
_property_ data\_storage\_version:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.data_storage_version "Link to this definition")\
\
The version of the data storage format this dataset is using\
\
delete(_[predicate](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.delete.predicate "lance.dataset.LanceDataset.delete.predicate — The predicate to use to select rows to delete."):str\| [Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.delete "Link to this definition")\
\
Delete rows from the dataset.\
\
This marks rows as deleted, but does not physically remove them from the\
files. This keeps the existing indexes still valid.\
\
Parameters:predicate : str or pa.compute.Expression [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.delete.predicate "Permalink to this definition")\
\
The predicate to use to select rows to delete. May either be a SQL\
string or a pyarrow Expression.\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> dataset.delete("a = 1 or b in ('a', 'b')")\
>>> dataset.to_table()\
pyarrow.Table\
a: int64\
b: string\
----\
a: [[3]]\
b: [["c"]]\
\
```\
\
_static_ drop(_[base\_uri](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.drop "lance.dataset.LanceDataset.drop.base_uri"):str\|Path_, _[storage\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.drop "lance.dataset.LanceDataset.drop.storage_options"):dict\[str,str\]\|None= `None`_)→None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.drop "Link to this definition")drop\_columns(_[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.drop_columns.columns "lance.dataset.LanceDataset.drop_columns.columns — The names of the columns to drop."):list\[str\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.drop_columns "Link to this definition")\
\
Drop one or more columns from the dataset\
\
This is a metadata-only operation and does not remove the data from the\
underlying storage. In order to remove the data, you must subsequently\
call `compact_files` to rewrite the data without the removed columns and\
then call `cleanup_old_versions` to remove the old files.\
\
Parameters:columns : list of str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.drop_columns.columns "Permalink to this definition")\
\
The names of the columns to drop. These can be nested column references\
(e.g. “a.b.c”) or top-level column names (e.g. “a”).\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> dataset.drop_columns(["a"])\
>>> dataset.to_table().to_pandas()\
   b\
0  a\
1  b\
2  c\
\
```\
\
drop\_index(_[name](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.drop_index.name"):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.drop_index "Link to this definition")\
\
Drops an index from the dataset\
\
Note: Indices are dropped by “index name”. This is not the same as the field\
name. If you did not specify a name when you created the index then a name was\
generated for you. You can use the list\_indices method to get the names of\
the indices.\
\
get\_fragment(_[fragment\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.get_fragment "lance.dataset.LanceDataset.get_fragment.fragment_id"):int_)→[LanceFragment](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment — Count rows matching the scanner filter.") \|None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.get_fragment "Link to this definition")\
\
Get the fragment with fragment id.\
\
get\_fragments(_[filter](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.get_fragments "lance.dataset.LanceDataset.get_fragments.filter"):Expression\|None= `None`_)→list\[ [LanceFragment](https://lancedb.github.io/lance/api/python/LanceFragment.html "lance.LanceFragment — Initialize self.  See help(type(self)) for accurate signature.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.get_fragments "Link to this definition")\
\
Get all fragments from the dataset.\
\
Note: filter is not supported yet.\
\
_property_ has\_index [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.has_index "Link to this definition")head(_[num\_rows](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.head.num_rows "lance.dataset.LanceDataset.head.num_rows — The number of rows to load.")_, _\*\* [kwargs](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.head.kwargs "lance.dataset.LanceDataset.head.kwargs — See scanner() method for full parameter description.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.head "Link to this definition")\
\
Load the first N rows of the dataset.\
\
Parameters:num\_rows : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.head.num_rows "Permalink to this definition")\
\
The number of rows to load.\
\
\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.head.kwargs "Permalink to this definition")\
\
See scanner() method for full parameter description.\
\
Returns:\
\
**table**\
\
Return type:\
\
Table\
\
index\_statistics(_[index\_name](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.index_statistics "lance.dataset.LanceDataset.index_statistics.index_name"):str_)→dict\[str,Any\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.index_statistics "Link to this definition")insert(_[data](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.insert.data"):ReaderLike_, _\*_, _[mode](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.insert.mode "lance.dataset.LanceDataset.insert.mode — create - create a new dataset (raises if uri already exists). overwrite - create a new snapshot version append - create a new version that is the concat of the input the latest version (raises if uri does not exist)") = `'append'`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.insert.kwargs "lance.dataset.LanceDataset.insert.kwargs — Additional keyword arguments to pass to write_dataset().")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.insert "Link to this definition")\
\
Insert data into the dataset.\
\
Parameters:data\_obj : Reader-like\
\
The data to be written. Acceptable types are:\
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner, or RecordBatchReader\
\- Huggingface dataset\
\
mode : str, default 'append' [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.insert.mode "Permalink to this definition")\
\
The mode to use when writing the data. Options are:\
\
**create** \- create a new dataset (raises if uri already exists).\
**overwrite** \- create a new snapshot version\
**append** \- create a new version that is the concat of the input the\
latest version (raises if uri does not exist)\
\
\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.insert.kwargs "Permalink to this definition")\
\
Additional keyword arguments to pass to [`write_dataset()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset "lance.dataset.write_dataset — Write a given data_obj to the given uri").\
\
join(_[right\_dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "lance.dataset.LanceDataset.join.right_dataset")_, _[keys](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "lance.dataset.LanceDataset.join.keys")_, _[right\_keys](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "lance.dataset.LanceDataset.join.right_keys") = `None`_, _[join\_type](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "lance.dataset.LanceDataset.join.join_type") = `'left outer'`_, _[left\_suffix](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "lance.dataset.LanceDataset.join.left_suffix") = `None`_, _[right\_suffix](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "lance.dataset.LanceDataset.join.right_suffix") = `None`_, _[coalesce\_keys](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "lance.dataset.LanceDataset.join.coalesce_keys") = `True`_, _[use\_threads](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "lance.dataset.LanceDataset.join.use_threads") = `True`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.join "Link to this definition")\
\
Not implemented (just override pyarrow dataset to prevent segfault)\
\
_property_ lance\_schema:LanceSchema [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.lance_schema "Link to this definition")\
\
The LanceSchema for this dataset\
\
_property_ latest\_version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.latest_version "Link to this definition")\
\
Returns the latest version of the dataset.\
\
list\_indices()→list\[ [Index](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Index "lance.dataset.Index — fields : List[str]      fragment_ids : Set[int]      name : str      type : str      uuid : str      version : int")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.list_indices "Link to this definition")_property_ max\_field\_id:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.max_field_id "Link to this definition")\
\
The max\_field\_id in manifest\
\
merge(_[data\_obj](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge.data_obj "lance.dataset.LanceDataset.merge.data_obj — The data to be merged."):ReaderLike_, _[left\_on](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge.left_on "lance.dataset.LanceDataset.merge.left_on — The name of the column in the dataset to join on."):str_, _[right\_on](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge.right_on "lance.dataset.LanceDataset.merge.right_on — The name of the column in data_obj to join on."):str\|None= `None`_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge "lance.dataset.LanceDataset.merge.schema") = `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge "Link to this definition")\
\
Merge another dataset into this one.\
\
Performs a left join, where the dataset is the left side and data\_obj\
is the right side. Rows existing in the dataset but not on the left will\
be filled with null values, unless Lance doesn’t support null values for\
some types, in which case an error will be raised.\
\
Parameters:data\_obj : Reader-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge.data_obj "Permalink to this definition")\
\
The data to be merged. Acceptable types are:\
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner,\
Iterator\[RecordBatch\], or RecordBatchReader\
\
left\_on : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge.left_on "Permalink to this definition")\
\
The name of the column in the dataset to join on.\
\
right\_on : str or None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge.right_on "Permalink to this definition")\
\
The name of the column in data\_obj to join on. If None, defaults to\
left\_on.\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> df = pa.table({'x': [1, 2, 3], 'y': ['a', 'b', 'c']})\
>>> dataset = lance.write_dataset(df, "dataset")\
>>> dataset.to_table().to_pandas()\
   x  y\
0  1  a\
1  2  b\
2  3  c\
>>> new_df = pa.table({'x': [1, 2, 3], 'z': ['d', 'e', 'f']})\
>>> dataset.merge(new_df, 'x')\
>>> dataset.to_table().to_pandas()\
   x  y  z\
0  1  a  d\
1  2  b  e\
2  3  c  f\
\
```\
\
See also\
\
[`LanceDataset.add_columns`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.add_columns "lance.dataset.LanceDataset.add_columns — Add new columns with defined values.")\
\
Add new columns by computing batch-by-batch.\
\
merge\_insert(_[on](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge_insert.on "lance.dataset.LanceDataset.merge_insert.on — A column (or columns) to join on."):str\|Iterable\[str\]_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge_insert "Link to this definition")\
\
Returns a builder that can be used to create a “merge insert” operation\
\
This operation can add rows, update rows, and remove rows in a single\
transaction. It is a very generic tool that can be used to create\
behaviors like “insert if not exists”, “update or insert (i.e. upsert)”,\
or even replace a portion of existing data with new data (e.g. replace\
all data where month=”january”)\
\
The merge insert operation works by combining new data from a\
**source table** with existing data in a **target table** by using a\
join. There are three categories of records.\
\
“Matched” records are records that exist in both the source table and\
the target table. “Not matched” records exist only in the source table\
(e.g. these are new data). “Not matched by source” records exist only\
in the target table (this is old data).\
\
The builder returned by this method can be used to customize what\
should happen for each category of data.\
\
Please note that the data will be reordered as part of this\
operation. This is because updated rows will be deleted from the\
dataset and then reinserted at the end with the new values. The\
order of the newly inserted rows may fluctuate randomly because a\
hash-join operation is used internally.\
\
Parameters:on : Union\[str, Iterable\[str\]\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge_insert.on "Permalink to this definition")\
\
A column (or columns) to join on. This is how records from the\
source table and target table are matched. Typically this is some\
kind of key or id column.\
\
Examples\
\
Use when\_matched\_update\_all() and when\_not\_matched\_insert\_all() to\
perform an “upsert” operation. This will update rows that already exist\
in the dataset and insert rows that do not exist.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [2, 1, 3], "b": ["a", "b", "c"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> new_table = pa.table({"a": [2, 3, 4], "b": ["x", "y", "z"]})\
>>> # Perform a "upsert" operation\
>>> dataset.merge_insert("a")     \\
...             .when_matched_update_all()     \\
...             .when_not_matched_insert_all() \\
...             .execute(new_table)\
{'num_inserted_rows': 1, 'num_updated_rows': 2, 'num_deleted_rows': 0}\
>>> dataset.to_table().sort_by("a").to_pandas()\
   a  b\
0  1  b\
1  2  x\
2  3  y\
3  4  z\
\
```\
\
Use when\_not\_matched\_insert\_all() to perform an “insert if not exists”\
operation. This will only insert rows that do not already exist in the\
dataset.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})\
>>> dataset = lance.write_dataset(table, "example2")\
>>> new_table = pa.table({"a": [2, 3, 4], "b": ["x", "y", "z"]})\
>>> # Perform an "insert if not exists" operation\
>>> dataset.merge_insert("a")     \\
...             .when_not_matched_insert_all() \\
...             .execute(new_table)\
{'num_inserted_rows': 1, 'num_updated_rows': 0, 'num_deleted_rows': 0}\
>>> dataset.to_table().sort_by("a").to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  z\
\
```\
\
You are not required to provide all the columns. If you only want to\
update a subset of columns, you can omit columns you don’t want to\
update. Omitted columns will keep their existing values if they are\
updated, or will be null if they are inserted.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"], \\
...                   "c": ["x", "y", "z"]})\
>>> dataset = lance.write_dataset(table, "example3")\
>>> new_table = pa.table({"a": [2, 3, 4], "b": ["x", "y", "z"]})\
>>> # Perform an "upsert" operation, only updating column "a"\
>>> dataset.merge_insert("a")     \\
...             .when_matched_update_all()     \\
...             .when_not_matched_insert_all() \\
...             .execute(new_table)\
{'num_inserted_rows': 1, 'num_updated_rows': 2, 'num_deleted_rows': 0}\
>>> dataset.to_table().sort_by("a").to_pandas()\
   a  b     c\
0  1  a     x\
1  2  x     y\
2  3  y     z\
3  4  z  None\
\
```\
\
migrate\_manifest\_paths\_v2() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.migrate_manifest_paths_v2 "Link to this definition")\
\
Migrate the manifest paths to the new format.\
\
This will update the manifest to use the new v2 format for paths.\
\
This function is idempotent, and can be run multiple times without\
changing the state of the object store.\
\
DANGER: this should not be run while other concurrent operations are happening.\
And it should also run until completion before resuming other operations.\
\
_property_ optimize:[DatasetOptimizer](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer "lance.dataset.DatasetOptimizer — Compacts small files in the dataset, reducing total number of files.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.optimize "Link to this definition")_property_ partition\_expression [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.partition_expression "Link to this definition")\
\
Not implemented (just override pyarrow dataset to prevent segfault)\
\
prewarm\_index(_[name](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.prewarm_index.name "lance.dataset.LanceDataset.prewarm_index.name — The name of the index to prewarm."):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.prewarm_index "Link to this definition")\
\
Prewarm an index\
\
This will load the entire index into memory. This can help avoid cold start\
issues with index queries. If the index does not fit in the index cache, then\
this will result in wasted I/O.\
\
Parameters:name : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.prewarm_index.name "Permalink to this definition")\
\
The name of the index to prewarm.\
\
replace\_field\_metadata(_[field\_name](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_field_metadata.field_name "lance.dataset.LanceDataset.replace_field_metadata.field_name — The name of the field to replace the metadata for"):str_, _[new\_metadata](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_field_metadata.new_metadata "lance.dataset.LanceDataset.replace_field_metadata.new_metadata — The new metadata to set"):dict\[str,str\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_field_metadata "Link to this definition")\
\
Replace the metadata of a field in the schema\
\
Parameters:field\_name : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_field_metadata.field_name "Permalink to this definition")\
\
The name of the field to replace the metadata for\
\
new\_metadata : dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_field_metadata.new_metadata "Permalink to this definition")\
\
The new metadata to set\
\
replace\_schema(_[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_schema "lance.dataset.LanceDataset.replace_schema.schema"):[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_schema "Link to this definition")\
\
Not implemented (just override pyarrow dataset to prevent segfault)\
\
See [:py:method:\`replace\_schema\_metadata\`](https://lancedb.github.io/lance/api/py_modules.html#id28) or [:py:method:\`replace\_field\_metadata\`](https://lancedb.github.io/lance/api/py_modules.html#id30)\
\
replace\_schema\_metadata(_[new\_metadata](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_schema_metadata.new_metadata "lance.dataset.LanceDataset.replace_schema_metadata.new_metadata — The new metadata to set"):dict\[str,str\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_schema_metadata "Link to this definition")\
\
Replace the schema metadata of the dataset\
\
Parameters:new\_metadata : dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.replace_schema_metadata.new_metadata "Permalink to this definition")\
\
The new metadata to set\
\
restore() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.restore "Link to this definition")\
\
Restore the currently checked out version as the latest version of the dataset.\
\
This creates a new commit.\
\
sample(_[num\_rows](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.sample.num_rows "lance.dataset.LanceDataset.sample.num_rows — number of rows to retrieve"):int_, _[columns](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.sample.columns "lance.dataset.LanceDataset.sample.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[randomize\_order](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.sample "lance.dataset.LanceDataset.sample.randomize_order"):bool= `True`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.sample.kwargs "lance.dataset.LanceDataset.sample.kwargs — see scanner() method for full parameter description.")_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.sample "Link to this definition")\
\
Select a random sample of data\
\
Parameters:num\_rows : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.sample.num_rows "Permalink to this definition")\
\
number of rows to retrieve\
\
columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.sample.columns "Permalink to this definition")\
\
List of column names to be fetched.\
Or a dictionary of column names to SQL expressions.\
All columns are fetched if None or unspecified.\
\
\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.sample.kwargs "Permalink to this definition")\
\
see scanner() method for full parameter description.\
\
Returns:\
\
**table**\
\
Return type:\
\
Table\
\
scanner(_[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.columns "lance.dataset.LanceDataset.scanner.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.filter "lance.dataset.LanceDataset.scanner.filter — Duplicate explicit target name: \"lance filter pushdown\"."):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.limit "lance.dataset.LanceDataset.scanner.limit — Fetch up to this many rows."):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.offset "lance.dataset.LanceDataset.scanner.offset — Fetch starting with this row."):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.nearest "lance.dataset.LanceDataset.scanner.nearest — Get the rows corresponding to the K most similar vectors."):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_size "lance.dataset.LanceDataset.scanner.batch_size — The target size of batches returned."):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_readahead "lance.dataset.LanceDataset.scanner.batch_readahead — The number of batches to read ahead."):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragment_readahead "lance.dataset.LanceDataset.scanner.fragment_readahead — The number of fragments to read ahead."):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_in_order "lance.dataset.LanceDataset.scanner.scan_in_order — Whether to read the fragments and batches in order."):bool\|None= `None`_, _[fragments](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragments "lance.dataset.LanceDataset.scanner.fragments — If specified, only scan these fragments."):Iterable\[ [LanceFragment](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment — Count rows matching the scanner filter.")\]\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.full_text_query "lance.dataset.LanceDataset.scanner.full_text_query — query string to search for, the results will be ranked by BM25. e.g."):str\|dict\|FullTextQuery\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.prefilter "lance.dataset.LanceDataset.scanner.prefilter — If True then the filter will be applied before the vector query is run. This will generate more correct results but it may be a more costly query."):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.scanner.with_row_id"):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.scanner.with_row_address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.scanner.use_stats"):bool\|None= `None`_, _[fast\_search](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fast_search "lance.dataset.LanceDataset.scanner.fast_search — If True, then the search will only be performed on the indexed data, which yields faster search time."):bool\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.io_buffer_size "lance.dataset.LanceDataset.scanner.io_buffer_size — The size of the IO buffer."):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.late_materialization "lance.dataset.LanceDataset.scanner.late_materialization — Allows custom control over late materialization."):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.use_scalar_index "lance.dataset.LanceDataset.scanner.use_scalar_index — Lance will automatically use scalar indices to optimize a query."):bool\|None= `None`_, _[include\_deleted\_rows](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.include_deleted_rows "lance.dataset.LanceDataset.scanner.include_deleted_rows — If True, then rows that have been deleted, but are still present in the fragment, will be returned."):bool\|None= `None`_, _[scan\_stats\_callback](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_stats_callback "lance.dataset.LanceDataset.scanner.scan_stats_callback — A callback function that will be called with the scan statistics after the scan is complete."):Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics "_lib.ScanStatistics")\],None\]\|None= `None`_, _[strict\_batch\_size](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.scanner.strict_batch_size"):bool\|None= `None`_)→[LanceScanner](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner "lance.dataset.LanceScanner — Execute the plan for this scanner and display with runtime metrics.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner "Link to this definition")\
\
Return a Scanner that can support various pushdowns.\
\
Parameters:columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.columns "Permalink to this definition")\
\
List of column names to be fetched.\
Or a dictionary of column names to SQL expressions.\
All columns are fetched if None or unspecified.\
\
filter : pa.compute.Expression or str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.filter "Permalink to this definition")\
\
Expression or str that is a valid SQL where clause. See\
[Lance filter pushdown](https://lancedb.github.io/lance/introduction/read_and_write.html#filter-push-down)\
for valid SQL expressions.\
\
limit : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.limit "Permalink to this definition")\
\
Fetch up to this many rows. All rows if None or unspecified.\
\
offset : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.offset "Permalink to this definition")\
\
Fetch starting with this row. 0 if None or unspecified.\
\
nearest : dict, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.nearest "Permalink to this definition")\
\
Get the rows corresponding to the K most similar vectors. Example:\
\
```\
{\
    "column": <embedding col name>,\
    "q": <query vector as pa.Float32Array>,\
    "k": 10,\
    "minimum_nprobes": 20,\
    "maximum_nprobes": 50,\
    "refine_factor": 1\
}\
\
```\
\
batch\_size : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.batch_size "Permalink to this definition")\
\
The target size of batches returned. In some cases batches can be up to\
twice this size (but never larger than this). In some cases batches can\
be smaller than this size.\
\
io\_buffer\_size : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.io_buffer_size "Permalink to this definition")\
\
The size of the IO buffer. See `ScannerBuilder.io_buffer_size`\
for more information.\
\
batch\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.batch_readahead "Permalink to this definition")\
\
The number of batches to read ahead.\
\
fragment\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.fragment_readahead "Permalink to this definition")\
\
The number of fragments to read ahead.\
\
scan\_in\_order : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.scan_in_order "Permalink to this definition")\
\
Whether to read the fragments and batches in order. If false,\
throughput may be higher, but batches will be returned out of order\
and memory use might increase.\
\
fragments : iterable of [LanceFragment](https://lancedb.github.io/lance/api/python/LanceFragment.html "lance.LanceFragment — Initialize self.  See help(type(self)) for accurate signature."), default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.fragments "Permalink to this definition")\
\
If specified, only scan these fragments. If scan\_in\_order is True, then\
the fragments will be scanned in the order given.\
\
prefilter : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.prefilter "Permalink to this definition")\
\
If True then the filter will be applied before the vector query is run.\
This will generate more correct results but it may be a more costly\
query. It’s generally good when the filter is highly selective.\
\
If False then the filter will be applied after the vector query is run.\
This will perform well but the results may have fewer than the requested\
number of rows (or be empty) if the rows closest to the query do not\
match the filter. It’s generally good when the filter is not very\
selective.\
\
use\_scalar\_index : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.use_scalar_index "Permalink to this definition")\
\
Lance will automatically use scalar indices to optimize a query. In some\
corner cases this can make query performance worse and this parameter can\
be used to disable scalar indices in these cases.\
\
late\_materialization : bool or List\[str\], default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.late_materialization "Permalink to this definition")\
\
Allows custom control over late materialization. Late materialization\
fetches non-query columns using a take operation after the filter. This\
is useful when there are few results or columns are very large.\
\
Early materialization can be better when there are many results or the\
columns are very narrow.\
\
If True, then all columns are late materialized.\
If False, then all columns are early materialized.\
If a list of strings, then only the columns in the list are\
late materialized.\
\
The default uses a heuristic that assumes filters will select about 0.1%\
of the rows. If your filter is more selective (e.g. find by id) you may\
want to set this to True. If your filter is not very selective (e.g.\
matches 20% of the rows) you may want to set this to False.\
\
full\_text\_query : str or dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.full_text_query "Permalink to this definition")\
\
query string to search for, the results will be ranked by BM25.\
e.g. “hello world”, would match documents containing “hello” or “world”.\
or a dictionary with the following keys:\
\
- columns: list\[str\]\
\
The columns to search,\
currently only supports a single column in the columns list.\
\
- query: str\
\
The query string to search for.\
\
\
fast\_search : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.fast_search "Permalink to this definition")\
\
If True, then the search will only be performed on the indexed data, which\
yields faster search time.\
\
scan\_stats\_callback : Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/python/ScanStatistics.html "lance.ScanStatistics — Statistics about the scan.")\], None\], default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.scan_stats_callback "Permalink to this definition")\
\
A callback function that will be called with the scan statistics after the\
scan is complete. Errors raised by the callback will be logged but not\
re-raised.\
\
include\_deleted\_rows : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner.include_deleted_rows "Permalink to this definition")\
\
If True, then rows that have been deleted, but are still present in the\
fragment, will be returned. These rows will have the \_rowid column set\
to null. All other columns will reflect the value stored on disk and may\
not be null.\
\
Note: if this is a search operation, or a take operation (including scalar\
indexed scans) then deleted rows cannot be returned.\
\
Note\
\
For now, if BOTH filter and nearest is specified, then:\
\
1. nearest is executed first.\
\
2. The results are filtered afterwards.\
\
\
For debugging ANN results, you can choose to not use the index\
even if present by specifying `use_index=False`. For example,\
the following will always return exact KNN results:\
\
```\
dataset.to_table(nearest={\
    "column": "vector",\
    "k": 10,\
    "q": <query vector>,\
    "use_index": False\
}\
\
```\
\
_property_ schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.schema "Link to this definition")\
\
The pyarrow Schema for this dataset\
\
session()→\_Session [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.session "Link to this definition")\
\
Return the dataset session, which holds the dataset’s state.\
\
_property_ stats:[LanceStats](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats "lance.dataset.LanceStats — Statistics about a LanceDataset.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.stats "Link to this definition")\
\
**Experimental API**\
\
_property_ tags:[Tags](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags "lance.dataset.Tags — Dataset tag manager.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.tags "Link to this definition")\
\
Tag management for the dataset.\
\
Similar to Git, tags are a way to add metadata to a specific version of the\
dataset.\
\
Warning\
\
Tagged versions are exempted from the [`cleanup_old_versions()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.cleanup_old_versions "lance.dataset.LanceDataset.cleanup_old_versions — Cleans up old versions of the dataset.")\
process.\
\
To remove a version that has been tagged, you must first\
[`delete()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.delete "lance.dataset.Tags.delete — Delete tag from the dataset.") the associated tag.\
\
Examples\
\
```\
ds = lance.open("dataset.lance")\
ds.tags.create("v2-prod-20250203", 10)\
\
tags = ds.tags.list()\
\
```\
\
take(_[indices](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.take.indices "lance.dataset.LanceDataset.take.indices — indices of rows to select in the dataset."):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)")_, _[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.take.columns "lance.dataset.LanceDataset.take.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.take "Link to this definition")\
\
Select rows of data by index.\
\
Parameters:indices : Array or array-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.take.indices "Permalink to this definition")\
\
indices of rows to select in the dataset.\
\
columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.take.columns "Permalink to this definition")\
\
List of column names to be fetched.\
Or a dictionary of column names to SQL expressions.\
All columns are fetched if None or unspecified.\
\
Returns:\
\
**table**\
\
Return type:\
\
[pyarrow.Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)")\
\
take\_blobs(_[blob\_column](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.take_blobs.blob_column"):str_, _[ids](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.take_blobs.ids"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_, _[addresses](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.take_blobs.addresses"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_, _[indices](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.take_blobs.indices"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_)→list\[ [BlobFile](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile "lance.blob.BlobFile")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.take_blobs "Link to this definition")\
\
Select blobs by row IDs.\
\
Instead of loading large binary blob data into memory before processing it,\
this API allows you to open binary blob data as a regular Python file-like\
object. For more details, see [`lance.BlobFile`](https://lancedb.github.io/lance/api/python/BlobFile.html "lance.BlobFile — Represents a blob in a Lance dataset as a file-like object.").\
\
Exactly one of ids, addresses, or indices must be specified.\
:param blob\_column: The name of the blob column to select.\
:type blob\_column: str\
:param ids: row IDs to select in the dataset.\
:type ids: Integer Array or array-like\
:param addresses: The (unstable) row addresses to select in the dataset.\
:type addresses: Integer Array or array-like\
:param indices: The offset / indices of the row in the dataset.\
:type indices: Integer Array or array-like\
\
Returns:\
\
**blob\_files**\
\
Return type:\
\
List\[ [BlobFile](https://lancedb.github.io/lance/api/python/BlobFile.html "lance.BlobFile — Represents a blob in a Lance dataset as a file-like object.")\]\
\
to\_batches(_[columns](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.columns"):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.filter"):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.limit"):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.offset"):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.nearest"):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.batch_size"):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.batch_readahead"):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.fragment_readahead"):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.scan_in_order"):bool\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.prefilter"):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.with_row_id"):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.with_row_address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.use_stats"):bool\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.full_text_query"):str\|dict\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.io_buffer_size"):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.late_materialization"):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.use_scalar_index"):bool\|None= `None`_, _[strict\_batch\_size](https://lancedb.github.io/lance/api/python.html "lance.dataset.LanceDataset.to_batches.strict_batch_size"):bool\|None= `None`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_batches.kwargs "lance.dataset.LanceDataset.to_batches.kwargs — Arguments for scanner().")_)→Iterator\[ [RecordBatch](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html#pyarrow.RecordBatch "(in Apache Arrow v20.0.0)")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_batches "Link to this definition")\
\
Read the dataset as materialized record batches.\
\
Parameters:\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_batches.kwargs "Permalink to this definition")\
\
Arguments for [`scanner()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner "lance.dataset.LanceDataset.scanner — Return a Scanner that can support various pushdowns.").\
\
Returns:\
\
**record\_batches**\
\
Return type:\
\
Iterator of [`RecordBatch`](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html#pyarrow.RecordBatch "(in Apache Arrow v20.0.0)")\
\
to\_table(_[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.columns "lance.dataset.LanceDataset.to_table.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.filter "lance.dataset.LanceDataset.to_table.filter — Duplicate explicit target name: \"lance filter pushdown\"."):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.limit "lance.dataset.LanceDataset.to_table.limit — Fetch up to this many rows."):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.offset "lance.dataset.LanceDataset.to_table.offset — Fetch starting with this row."):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.nearest "lance.dataset.LanceDataset.to_table.nearest — Get the rows corresponding to the K most similar vectors."):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.batch_size "lance.dataset.LanceDataset.to_table.batch_size — The number of rows to read at a time."):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.batch_readahead "lance.dataset.LanceDataset.to_table.batch_readahead — The number of batches to read ahead."):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.fragment_readahead "lance.dataset.LanceDataset.to_table.fragment_readahead — The number of fragments to read ahead."):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.scan_in_order "lance.dataset.LanceDataset.to_table.scan_in_order — Whether to read the fragments and batches in order."):bool\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.prefilter "lance.dataset.LanceDataset.to_table.prefilter — Run filter before the vector search."):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.with_row_id "lance.dataset.LanceDataset.to_table.with_row_id — Return row ID."):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.with_row_address "lance.dataset.LanceDataset.to_table.with_row_address — Return row address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.use_stats "lance.dataset.LanceDataset.to_table.use_stats — Use stats pushdown during filters."):bool\|None= `None`_, _[fast\_search](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.fast_search "lance.dataset.LanceDataset.to_table.fast_search"):bool\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.full_text_query "lance.dataset.LanceDataset.to_table.full_text_query — query string to search for, the results will be ranked by BM25. e.g."):str\|dict\|FullTextQuery\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.io_buffer_size "lance.dataset.LanceDataset.to_table.io_buffer_size — The size of the IO buffer."):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.late_materialization "lance.dataset.LanceDataset.to_table.late_materialization — Allows custom control over late materialization."):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.use_scalar_index "lance.dataset.LanceDataset.to_table.use_scalar_index — Allows custom control over scalar index usage."):bool\|None= `None`_, _[include\_deleted\_rows](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.include_deleted_rows "lance.dataset.LanceDataset.to_table.include_deleted_rows — If True, then rows that have been deleted, but are still present in the fragment, will be returned."):bool\|None= `None`_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table "Link to this definition")\
\
Read the data into memory as a [`pyarrow.Table`](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)")\
\
Parameters:columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.columns "Permalink to this definition")\
\
List of column names to be fetched.\
Or a dictionary of column names to SQL expressions.\
All columns are fetched if None or unspecified.\
\
filter : pa.compute.Expression or str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.filter "Permalink to this definition")\
\
Expression or str that is a valid SQL where clause. See\
[Lance filter pushdown](https://lancedb.github.io/lance/introduction/read_and_write.html#filter-push-down)\
for valid SQL expressions.\
\
limit : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.limit "Permalink to this definition")\
\
Fetch up to this many rows. All rows if None or unspecified.\
\
offset : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.offset "Permalink to this definition")\
\
Fetch starting with this row. 0 if None or unspecified.\
\
nearest : dict, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.nearest "Permalink to this definition")\
\
Get the rows corresponding to the K most similar vectors. Example:\
\
```\
{\
    "column": <embedding col name>,\
    "q": <query vector as pa.Float32Array>,\
    "k": 10,\
    "metric": "cosine",\
    "minimum_nprobes": 20,\
    "maximum_nprobes": 50,\
    "refine_factor": 1\
}\
\
```\
\
batch\_size : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.batch_size "Permalink to this definition")\
\
The number of rows to read at a time.\
\
io\_buffer\_size : int, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.io_buffer_size "Permalink to this definition")\
\
The size of the IO buffer. See `ScannerBuilder.io_buffer_size`\
for more information.\
\
batch\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.batch_readahead "Permalink to this definition")\
\
The number of batches to read ahead.\
\
fragment\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.fragment_readahead "Permalink to this definition")\
\
The number of fragments to read ahead.\
\
scan\_in\_order : bool, optional, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.scan_in_order "Permalink to this definition")\
\
Whether to read the fragments and batches in order. If false,\
throughput may be higher, but batches will be returned out of order\
and memory use might increase.\
\
prefilter : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.prefilter "Permalink to this definition")\
\
Run filter before the vector search.\
\
late\_materialization : bool or List\[str\], default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.late_materialization "Permalink to this definition")\
\
Allows custom control over late materialization. See\
`ScannerBuilder.late_materialization` for more information.\
\
use\_scalar\_index : bool, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.use_scalar_index "Permalink to this definition")\
\
Allows custom control over scalar index usage. See\
`ScannerBuilder.use_scalar_index` for more information.\
\
with\_row\_id : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.with_row_id "Permalink to this definition")\
\
Return row ID.\
\
with\_row\_address : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.with_row_address "Permalink to this definition")\
\
Return row address\
\
use\_stats : bool, optional, default True [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.use_stats "Permalink to this definition")\
\
Use stats pushdown during filters.\
\
fast\_search : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.fast_search "Permalink to this definition")\
\
full\_text\_query : str or dict, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.full_text_query "Permalink to this definition")\
\
query string to search for, the results will be ranked by BM25.\
e.g. “hello world”, would match documents contains “hello” or “world”.\
or a dictionary with the following keys:\
\
- columns: list\[str\]\
\
The columns to search,\
currently only supports a single column in the columns list.\
\
- query: str\
\
The query string to search for.\
\
\
include\_deleted\_rows : bool, optional, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.to_table.include_deleted_rows "Permalink to this definition")\
\
If True, then rows that have been deleted, but are still present in the\
fragment, will be returned. These rows will have the \_rowid column set\
to null. All other columns will reflect the value stored on disk and may\
not be null.\
\
Note: if this is a search operation, or a take operation (including scalar\
indexed scans) then deleted rows cannot be returned.\
\
Notes\
\
If BOTH filter and nearest is specified, then:\
\
1. nearest is executed first.\
\
2. The results are filtered afterward, unless pre-filter sets to True.\
\
\
update(_[updates](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.update.updates "lance.dataset.LanceDataset.update.updates — A mapping of column names to a SQL expression."):dict\[str,str\]_, _[where](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.update.where "lance.dataset.LanceDataset.update.where — A SQL predicate indicating which rows should be updated."):str\|None= `None`_)→[UpdateResult](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.UpdateResult "lance.dataset.UpdateResult — num_rows_updated : int") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.update "Link to this definition")\
\
Update column values for rows matching where.\
\
Parameters:updates : dict of str to str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.update.updates "Permalink to this definition")\
\
A mapping of column names to a SQL expression.\
\
where : str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.update.where "Permalink to this definition")\
\
A SQL predicate indicating which rows should be updated.\
\
Returns:\
\
**updates** – A dictionary containing the number of rows updated.\
\
Return type:\
\
dict\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [1, 2, 3], "b": ["a", "b", "c"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> update_stats = dataset.update(dict(a = 'a + 2'), where="b != 'a'")\
>>> update_stats["num_updated_rows"] = 2\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  4  b\
2  5  c\
\
```\
\
_property_ uri:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.uri "Link to this definition")\
\
The location of the data\
\
validate() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.validate "Link to this definition")\
\
Validate the dataset.\
\
This checks the integrity of the dataset and will raise an exception if\
the dataset is corrupted.\
\
_property_ version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.version "Link to this definition")\
\
Returns the currently checked out version of the dataset\
\
versions() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.versions "Link to this definition")\
\
Return all versions in this dataset.\
\
_class_ lance.dataset.LanceOperation [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation "Link to this definition")_class_ Append(_[fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Append "lance.dataset.LanceOperation.Append.__init__.fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Append "Link to this definition")\
\
Append new rows to the dataset.\
\
fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Append.fragments "Link to this definition")\
\
The fragments that contain the new rows.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
Warning\
\
This is an advanced API for distributed operations. To append to a\
dataset on a single machine, use [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").\
\
Examples\
\
To append new rows to a dataset, first use\
[`lance.fragment.LanceFragment.create()`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create "lance.fragment.LanceFragment.create — Create a FragmentMetadata from the given data.") to create fragments. Then\
collect the fragment metadata into a list and pass it to this class.\
Finally, pass the operation to the [`LanceDataset.commit()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit "lance.dataset.LanceDataset.commit — Create a new version of dataset")\
method to create the new dataset.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> tab1 = pa.table({"a": [1, 2], "b": ["a", "b"]})\
>>> dataset = lance.write_dataset(tab1, "example")\
>>> tab2 = pa.table({"a": [3, 4], "b": ["c", "d"]})\
>>> fragment = lance.fragment.LanceFragment.create("example", tab2)\
>>> operation = lance.LanceOperation.Append([fragment])\
>>> dataset = lance.LanceDataset.commit("example", operation,\
...                                     read_version=dataset.version)\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
\
```\
\
fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id34 "Link to this definition")_class_ BaseOperation [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.BaseOperation "Link to this definition")\
\
Base class for operations that can be applied to a dataset.\
\
See available operations under [`LanceOperation`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation "lance.dataset.LanceOperation — Append new rows to the dataset.").\
\
_class_ CreateIndex(_[uuid](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex "lance.dataset.LanceOperation.CreateIndex.__init__.uuid"):str_, _[name](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex "lance.dataset.LanceOperation.CreateIndex.__init__.name"):str_, _[fields](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex "lance.dataset.LanceOperation.CreateIndex.__init__.fields"):list\[int\]_, _[dataset\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex "lance.dataset.LanceOperation.CreateIndex.__init__.dataset_version"):int_, _[fragment\_ids](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex "lance.dataset.LanceOperation.CreateIndex.__init__.fragment_ids"):set\[int\]_, _[index\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex "lance.dataset.LanceOperation.CreateIndex.__init__.index_version"):int_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex "Link to this definition")\
\
Operation that creates an index on the dataset.\
\
dataset\_version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex.dataset_version "Link to this definition")fields:List\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex.fields "Link to this definition")fragment\_ids:Set\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex.fragment_ids "Link to this definition")index\_version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex.index_version "Link to this definition")name:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex.name "Link to this definition")uuid:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.CreateIndex.uuid "Link to this definition")_class_ DataReplacement(_[replacements](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacement "lance.dataset.LanceOperation.DataReplacement.__init__.replacements"):list\[ [DataReplacementGroup](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup "lance.dataset.LanceOperation.DataReplacementGroup — Group of data replacements")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacement "Link to this definition")\
\
Operation that replaces existing datafiles in the dataset.\
\
replacements:List\[ [DataReplacementGroup](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup "lance.dataset.LanceOperation.DataReplacementGroup — Group of data replacements")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacement.replacements "Link to this definition")_class_ DataReplacementGroup(_[fragment\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup "lance.dataset.LanceOperation.DataReplacementGroup.__init__.fragment_id"):int_, _[new\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup "lance.dataset.LanceOperation.DataReplacementGroup.__init__.new_file"):[DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup "Link to this definition")\
\
Group of data replacements\
\
fragment\_id:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup.fragment_id "Link to this definition")new\_file:[DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.DataReplacementGroup.new_file "Link to this definition")_class_ Delete(_[updated\_fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete "lance.dataset.LanceOperation.Delete.__init__.updated_fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[deleted\_fragment\_ids](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete "lance.dataset.LanceOperation.Delete.__init__.deleted_fragment_ids"):Iterable\[int\]_, _[predicate](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete "lance.dataset.LanceOperation.Delete.__init__.predicate"):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete "Link to this definition")\
\
Remove fragments or rows from the dataset.\
\
updated\_fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete.updated_fragments "Link to this definition")\
\
The fragments that have been updated with new deletion vectors.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
deleted\_fragment\_ids [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete.deleted_fragment_ids "Link to this definition")\
\
The ids of the fragments that have been deleted entirely. These are\
the fragments where `LanceFragment.delete()` returned None.\
\
Type:\
\
list\[int\]\
\
predicate [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete.predicate "Link to this definition")\
\
The original SQL predicate used to select the rows to delete.\
\
Type:\
\
str\
\
Warning\
\
This is an advanced API for distributed operations. To delete rows from\
dataset on a single machine, use [`lance.LanceDataset.delete()`](https://lancedb.github.io/lance/api/python/LanceDataset.delete.html "lance.LanceDataset.delete — Delete rows from the dataset.").\
\
Examples\
\
To delete rows from a dataset, call [`lance.fragment.LanceFragment.delete()`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.delete "lance.fragment.LanceFragment.delete — Delete rows from this Fragment.")\
on each of the fragments. If that returns a new fragment, add that to\
the `updated_fragments` list. If it returns None, that means the whole\
fragment was deleted, so add the fragment id to the `deleted_fragment_ids`.\
Finally, pass the operation to the [`LanceDataset.commit()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit "lance.dataset.LanceDataset.commit — Create a new version of dataset") method to\
complete the deletion operation.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> table = pa.table({"a": [1, 2], "b": ["a", "b"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> table = pa.table({"a": [3, 4], "b": ["c", "d"]})\
>>> dataset = lance.write_dataset(table, "example", mode="append")\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
>>> predicate = "a >= 2"\
>>> updated_fragments = []\
>>> deleted_fragment_ids = []\
>>> for fragment in dataset.get_fragments():\
...     new_fragment = fragment.delete(predicate)\
...     if new_fragment is not None:\
...         updated_fragments.append(new_fragment)\
...     else:\
...         deleted_fragment_ids.append(fragment.fragment_id)\
>>> operation = lance.LanceOperation.Delete(updated_fragments,\
...                                         deleted_fragment_ids,\
...                                         predicate)\
>>> dataset = lance.LanceDataset.commit("example", operation,\
...                                     read_version=dataset.version)\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
\
```\
\
deleted\_fragment\_ids:Iterable\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id35 "Link to this definition")predicate:str [¶](https://lancedb.github.io/lance/api/py_modules.html#id36 "Link to this definition")updated\_fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id37 "Link to this definition")_class_ Merge(_[fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Merge "lance.dataset.LanceOperation.Merge.__init__.fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Merge "lance.dataset.LanceOperation.Merge.__init__.schema"):LanceSchema\| [Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Merge "Link to this definition")\
\
Operation that adds columns. Unlike Overwrite, this should not change\
the structure of the fragments, allowing existing indices to be kept.\
\
fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Merge.fragments "Link to this definition")\
\
The fragments that make up the new dataset.\
\
Type:\
\
iterable of [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\
\
schema [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Merge.schema "Link to this definition")\
\
The schema of the new dataset. Passing a LanceSchema is preferred,\
and passing a pyarrow.Schema is deprecated.\
\
Type:\
\
LanceSchema or [pyarrow.Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")\
\
Warning\
\
This is an advanced API for distributed operations. To overwrite or\
create new dataset on a single machine, use [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").\
\
Examples\
\
To add new columns to a dataset, first define a method that will create\
the new columns based on the existing columns. Then use\
`lance.fragment.LanceFragment.add_columns()`\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> import pyarrow.compute as pc\
>>> table = pa.table({"a": [1, 2, 3, 4], "b": ["a", "b", "c", "d"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
>>> def double_a(batch: pa.RecordBatch) -> pa.RecordBatch:\
...     doubled = pc.multiply(batch["a"], 2)\
...     return pa.record_batch([doubled], ["a_doubled"])\
>>> fragments = []\
>>> for fragment in dataset.get_fragments():\
...     new_fragment, new_schema = fragment.merge_columns(double_a,\
...                                                       columns=['a'])\
...     fragments.append(new_fragment)\
>>> operation = lance.LanceOperation.Merge(fragments, new_schema)\
>>> dataset = lance.LanceDataset.commit("example", operation,\
...                                     read_version=dataset.version)\
>>> dataset.to_table().to_pandas()\
   a  b  a_doubled\
0  1  a          2\
1  2  b          4\
2  3  c          6\
3  4  d          8\
\
```\
\
fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id38 "Link to this definition")schema:LanceSchema\| [Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#id39 "Link to this definition")_class_ Overwrite(_[new\_schema](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Overwrite "lance.dataset.LanceOperation.Overwrite.__init__.new_schema"):LanceSchema\| [Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_, _[fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Overwrite "lance.dataset.LanceOperation.Overwrite.__init__.fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Overwrite "Link to this definition")\
\
Overwrite or create a new dataset.\
\
new\_schema [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Overwrite.new_schema "Link to this definition")\
\
The schema of the new dataset.\
\
Type:\
\
[pyarrow.Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")\
\
fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Overwrite.fragments "Link to this definition")\
\
The fragments that make up the new dataset.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
Warning\
\
This is an advanced API for distributed operations. To overwrite or\
create new dataset on a single machine, use [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri").\
\
Examples\
\
To create or overwrite a dataset, first use\
[`lance.fragment.LanceFragment.create()`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create "lance.fragment.LanceFragment.create — Create a FragmentMetadata from the given data.") to create fragments. Then\
collect the fragment metadata into a list and pass it along with the\
schema to this class. Finally, pass the operation to the\
[`LanceDataset.commit()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.commit "lance.dataset.LanceDataset.commit — Create a new version of dataset") method to create the new dataset.\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> tab1 = pa.table({"a": [1, 2], "b": ["a", "b"]})\
>>> tab2 = pa.table({"a": [3, 4], "b": ["c", "d"]})\
>>> fragment1 = lance.fragment.LanceFragment.create("example", tab1)\
>>> fragment2 = lance.fragment.LanceFragment.create("example", tab2)\
>>> fragments = [fragment1, fragment2]\
>>> operation = lance.LanceOperation.Overwrite(tab1.schema, fragments)\
>>> dataset = lance.LanceDataset.commit("example", operation)\
>>> dataset.to_table().to_pandas()\
   a  b\
0  1  a\
1  2  b\
2  3  c\
3  4  d\
\
```\
\
fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id40 "Link to this definition")new\_schema:LanceSchema\| [Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#id41 "Link to this definition")_class_ Project(_[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Project "lance.dataset.LanceOperation.Project.__init__.schema"):LanceSchema_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Project "Link to this definition")\
\
Operation that project columns.\
Use this operator for drop column or rename/swap column.\
\
schema [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Project.schema "Link to this definition")\
\
The lance schema of the new dataset.\
\
Type:\
\
LanceSchema\
\
Examples\
\
Use the projece operator to swap column:\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> import pyarrow.compute as pc\
>>> from lance.schema import LanceSchema\
>>> table = pa.table({"a": [1, 2], "b": ["a", "b"], "b1": ["c", "d"]})\
>>> dataset = lance.write_dataset(table, "example")\
>>> dataset.to_table().to_pandas()\
   a  b b1\
0  1  a  c\
1  2  b  d\
>>>\
>>> ## rename column `b` into `b0` and rename b1 into `b`\
>>> table = pa.table({"a": [3, 4], "b0": ["a", "b"], "b": ["c", "d"]})\
>>> lance_schema = LanceSchema.from_pyarrow(table.schema)\
>>> operation = lance.LanceOperation.Project(lance_schema)\
>>> dataset = lance.LanceDataset.commit("example", operation, read_version=1)\
>>> dataset.to_table().to_pandas()\
   a b0  b\
0  1  a  c\
1  2  b  d\
\
```\
\
schema:LanceSchema [¶](https://lancedb.github.io/lance/api/py_modules.html#id42 "Link to this definition")_class_ Restore(_[version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Restore "lance.dataset.LanceOperation.Restore.__init__.version"):int_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Restore "Link to this definition")\
\
Operation that restores a previous version of the dataset.\
\
version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Restore.version "Link to this definition")_class_ Rewrite(_[groups](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Rewrite "lance.dataset.LanceOperation.Rewrite.__init__.groups"):Iterable\[ [RewriteGroup](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup "lance.dataset.LanceOperation.RewriteGroup — Collection of rewritten files")\]_, _[rewritten\_indices](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Rewrite "lance.dataset.LanceOperation.Rewrite.__init__.rewritten_indices"):Iterable\[ [RewrittenIndex](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex "lance.dataset.LanceOperation.RewrittenIndex — An index that has been rewritten")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Rewrite "Link to this definition")\
\
Operation that rewrites one or more files and indices into one\
or more files and indices.\
\
groups [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Rewrite.groups "Link to this definition")\
\
Groups of files that have been rewritten.\
\
Type:\
\
list\[ [RewriteGroup](https://lancedb.github.io/lance/api/python/LanceOperation.RewriteGroup.html "lance.LanceOperation.RewriteGroup — Collection of rewritten files")\]\
\
rewritten\_indices [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Rewrite.rewritten_indices "Link to this definition")\
\
Indices that have been rewritten.\
\
Type:\
\
list\[ [RewrittenIndex](https://lancedb.github.io/lance/api/python/LanceOperation.RewrittenIndex.html "lance.LanceOperation.RewrittenIndex — An index that has been rewritten")\]\
\
Warning\
\
This is an advanced API not intended for general use.\
\
groups:Iterable\[ [RewriteGroup](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup "lance.dataset.LanceOperation.RewriteGroup — Collection of rewritten files")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id43 "Link to this definition")rewritten\_indices:Iterable\[ [RewrittenIndex](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex "lance.dataset.LanceOperation.RewrittenIndex — An index that has been rewritten")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id44 "Link to this definition")_class_ RewriteGroup(_[old\_fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup "lance.dataset.LanceOperation.RewriteGroup.__init__.old_fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[new\_fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup "lance.dataset.LanceOperation.RewriteGroup.__init__.new_fragments"):Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup "Link to this definition")\
\
Collection of rewritten files\
\
new\_fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup.new_fragments "Link to this definition")old\_fragments:Iterable\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewriteGroup.old_fragments "Link to this definition")_class_ RewrittenIndex(_[old\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex "lance.dataset.LanceOperation.RewrittenIndex.__init__.old_id"):str_, _[new\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex "lance.dataset.LanceOperation.RewrittenIndex.__init__.new_id"):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex "Link to this definition")\
\
An index that has been rewritten\
\
new\_id:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex.new_id "Link to this definition")old\_id:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.RewrittenIndex.old_id "Link to this definition")_class_ Update(_[removed\_fragment\_ids](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update "lance.dataset.LanceOperation.Update.__init__.removed_fragment_ids"):list\[int\]_, _[updated\_fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update "lance.dataset.LanceOperation.Update.__init__.updated_fragments"):list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[new\_fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update "lance.dataset.LanceOperation.Update.__init__.new_fragments"):list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]_, _[fields\_modified](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update "lance.dataset.LanceOperation.Update.__init__.fields_modified"):list\[int\]_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update "Link to this definition")\
\
Operation that updates rows in the dataset.\
\
removed\_fragment\_ids [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update.removed_fragment_ids "Link to this definition")\
\
The ids of the fragments that have been removed entirely.\
\
Type:\
\
list\[int\]\
\
updated\_fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update.updated_fragments "Link to this definition")\
\
The fragments that have been updated with new deletion vectors.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
new\_fragments [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update.new_fragments "Link to this definition")\
\
The fragments that contain the new rows.\
\
Type:\
\
list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/python/FragmentMetadata.html "lance.FragmentMetadata — Metadata for a fragment.")\]\
\
fields\_modified [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Update.fields_modified "Link to this definition")\
\
If any fields are modified in updated\_fragments, then they must be\
listed here so those fragments can be removed from indices covering\
those fields.\
\
Type:\
\
list\[int\]\
\
fields\_modified:List\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id45 "Link to this definition")new\_fragments:List\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id46 "Link to this definition")removed\_fragment\_ids:List\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id47 "Link to this definition")updated\_fragments:List\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id48 "Link to this definition")_class_ lance.dataset.LanceScanner(_[scanner](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner "lance.dataset.LanceScanner.__init__.scanner"):\_Scanner_, _[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner "lance.dataset.LanceScanner.__init__.dataset"):[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner "Link to this definition")analyze\_plan()→str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.analyze_plan "Link to this definition")\
\
Execute the plan for this scanner and display with runtime metrics.\
\
Parameters:verbose : bool, default False\
\
Use a verbose output format.\
\
Returns:\
\
**plan**\
\
Return type:\
\
str\
\
count\_rows() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.count_rows "Link to this definition")\
\
Count rows matching the scanner filter.\
\
Returns:\
\
**count**\
\
Return type:\
\
int\
\
_property_ dataset\_schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.dataset_schema "Link to this definition")\
\
The schema with which batches will be read from fragments.\
\
explain\_plan(_[verbose](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.explain_plan.verbose "lance.dataset.LanceScanner.explain_plan.verbose — Use a verbose output format.") = `False`_)→str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.explain_plan "Link to this definition")\
\
Return the execution plan for this scanner.\
\
Parameters:verbose : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.explain_plan.verbose "Permalink to this definition")\
\
Use a verbose output format.\
\
Returns:\
\
**plan**\
\
Return type:\
\
str\
\
_static_ from\_batches(_\* [args](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_batches "lance.dataset.LanceScanner.from_batches.args")_, _\*\* [kwargs](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_batches "lance.dataset.LanceScanner.from_batches.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_batches "Link to this definition")\
\
Not implemented\
\
_static_ from\_dataset(_\* [args](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_dataset "lance.dataset.LanceScanner.from_dataset.args")_, _\*\* [kwargs](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_dataset "lance.dataset.LanceScanner.from_dataset.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_dataset "Link to this definition")\
\
Not implemented\
\
_static_ from\_fragment(_\* [args](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_fragment "lance.dataset.LanceScanner.from_fragment.args")_, _\*\* [kwargs](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_fragment "lance.dataset.LanceScanner.from_fragment.kwargs")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.from_fragment "Link to this definition")\
\
Not implemented\
\
head(_[num\_rows](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.head.num_rows "lance.dataset.LanceScanner.head.num_rows — The number of rows to load.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.head "Link to this definition")\
\
Load the first N rows of the dataset.\
\
Parameters:num\_rows : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.head.num_rows "Permalink to this definition")\
\
The number of rows to load.\
\
Return type:\
\
Table\
\
_property_ projected\_schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.projected_schema "Link to this definition")\
\
The materialized schema of the data, accounting for projections.\
\
This is the schema of any data returned from the scanner.\
\
scan\_batches() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.scan_batches "Link to this definition")\
\
Consume a Scanner in record batches with corresponding fragments.\
\
Returns:\
\
**record\_batches**\
\
Return type:\
\
iterator of TaggedRecordBatch\
\
take(_[indices](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.take "lance.dataset.LanceScanner.take.indices")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.take "Link to this definition")\
\
Not implemented\
\
to\_batches(_[self](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.to_batches "lance.dataset.LanceScanner.to_batches.self")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.to_batches "Link to this definition")\
\
Consume a Scanner in record batches.\
\
Returns:\
\
**record\_batches**\
\
Return type:\
\
iterator of RecordBatch\
\
to\_reader(_[self](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.to_reader "lance.dataset.LanceScanner.to_reader.self")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.to_reader "Link to this definition")\
\
Consume this scanner as a RecordBatchReader.\
\
Return type:\
\
RecordBatchReader\
\
to\_table()→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner.to_table "Link to this definition")\
\
Read the data into memory and return a pyarrow Table.\
\
_class_ lance.dataset.LanceStats(_[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats "lance.dataset.LanceStats.__init__.dataset"):\_Dataset_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats "Link to this definition")\
\
Statistics about a LanceDataset.\
\
data\_stats()→[DataStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DataStatistics "lance.dataset.DataStatistics — Statistics about the data in the dataset") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats.data_stats "Link to this definition")\
\
Statistics about the data in the dataset.\
\
dataset\_stats(_[max\_rows\_per\_group](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats.dataset_stats "lance.dataset.LanceStats.dataset_stats.max_rows_per_group"):int= `1024`_)→[DatasetStats](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetStats "lance.dataset.DatasetStats — num_deleted_rows : int      num_fragments : int      num_small_files : int") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats.dataset_stats "Link to this definition")\
\
Statistics about the dataset.\
\
index\_stats(_[index\_name](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats.index_stats.index_name "lance.dataset.LanceStats.index_stats.index_name — The name of the index to get statistics for."):str_)→dict\[str,Any\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats.index_stats "Link to this definition")\
\
Statistics about an index.\
\
Parameters:index\_name : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceStats.index_stats.index_name "Permalink to this definition")\
\
The name of the index to get statistics for.\
\
_class_ lance.dataset.MergeInsertBuilder(_[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder.__init__.dataset")_, _[on](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder.__init__.on")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "Link to this definition")conflict\_retries(_[max\_retries](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.conflict_retries "lance.dataset.MergeInsertBuilder.conflict_retries.max_retries"):int_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.conflict_retries "Link to this definition")\
\
Set number of times to retry the operation if there is contention.\
\
If this is set > 0, then the operation will keep a copy of the input data\
either in memory or on disk (depending on the size of the data) and will\
retry the operation if there is contention.\
\
Default is 10.\
\
execute(_[data\_obj](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute.data_obj "lance.dataset.MergeInsertBuilder.execute.data_obj — The new data to use as the source table for the operation."):ReaderLike_, _\*_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute.schema "lance.dataset.MergeInsertBuilder.execute.schema — The schema of the data."):pa.Schema\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute "Link to this definition")\
\
Executes the merge insert operation\
\
This function updates the original dataset and returns a dictionary with\
information about merge statistics - i.e. the number of inserted, updated,\
and deleted rows.\
\
Parameters:data\_obj : ReaderLike [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute.data_obj "Permalink to this definition")\
\
The new data to use as the source table for the operation. This parameter\
can be any source of data (e.g. table / dataset) that\
[`write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") accepts.\
\
schema : Optional\[pa.Schema\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute.schema "Permalink to this definition")\
\
The schema of the data. This only needs to be supplied whenever the data\
source is some kind of generator.\
\
execute\_uncommitted(_[data\_obj](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute_uncommitted.data_obj "lance.dataset.MergeInsertBuilder.execute_uncommitted.data_obj — The new data to use as the source table for the operation."):ReaderLike_, _\*_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute_uncommitted.schema "lance.dataset.MergeInsertBuilder.execute_uncommitted.schema — The schema of the data."):pa.Schema\|None= `None`_)→tuple\[ [Transaction](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction — blobs_op : BaseOperation | None = None      operation : BaseOperation      read_version : int      uuid : str"),dict\[str,Any\]\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute_uncommitted "Link to this definition")\
\
Executes the merge insert operation without committing\
\
This function updates the original dataset and returns a dictionary with\
information about merge statistics - i.e. the number of inserted, updated,\
and deleted rows.\
\
Parameters:data\_obj : ReaderLike [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute_uncommitted.data_obj "Permalink to this definition")\
\
The new data to use as the source table for the operation. This parameter\
can be any source of data (e.g. table / dataset) that\
[`write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") accepts.\
\
schema : Optional\[pa.Schema\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.execute_uncommitted.schema "Permalink to this definition")\
\
The schema of the data. This only needs to be supplied whenever the data\
source is some kind of generator.\
\
retry\_timeout(_[timeout](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.retry_timeout "lance.dataset.MergeInsertBuilder.retry_timeout.timeout"):timedelta_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.retry_timeout "Link to this definition")\
\
Set the timeout used to limit retries.\
\
This is the maximum time to spend on the operation before giving up. At\
least one attempt will be made, regardless of how long it takes to complete.\
Subsequent attempts will be cancelled once this timeout is reached. If\
the timeout has been reached during the first attempt, the operation\
will be cancelled immediately before making a second attempt.\
\
The default is 30 seconds.\
\
when\_matched\_update\_all(_[condition](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.when_matched_update_all "lance.dataset.MergeInsertBuilder.when_matched_update_all.condition"):str\|None= `None`_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.when_matched_update_all "Link to this definition")\
\
Configure the operation to update matched rows\
\
After this method is called, when the merge insert operation executes,\
any rows that match both the source table and the target table will be\
updated. The rows from the target table will be removed and the rows\
from the source table will be added.\
\
An optional condition may be specified. This should be an SQL filter\
and, if present, then only matched rows that also satisfy this filter will\
be updated. The SQL filter should use the prefix target. to refer to\
columns in the target table and the prefix source. to refer to columns\
in the source table. For example, source.last\_update < target.last\_update.\
\
If a condition is specified and rows do not satisfy the condition then these\
rows will not be updated. Failure to satisfy the filter does not cause\
a “matched” row to become a “not matched” row.\
\
when\_not\_matched\_by\_source\_delete(_[expr](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.when_not_matched_by_source_delete "lance.dataset.MergeInsertBuilder.when_not_matched_by_source_delete.expr"):str\|None= `None`_)→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.when_not_matched_by_source_delete "Link to this definition")\
\
Configure the operation to delete source rows that do not match\
\
After this method is called, when the merge insert operation executes,\
any rows that exist only in the target table will be deleted. An\
optional filter can be specified to limit the scope of the delete\
operation. If given (as an SQL filter) then only rows which match\
the filter will be deleted.\
\
when\_not\_matched\_insert\_all()→[MergeInsertBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder "lance.dataset.MergeInsertBuilder — Set number of times to retry the operation if there is contention.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.MergeInsertBuilder.when_not_matched_insert_all "Link to this definition")\
\
Configure the operation to insert not matched rows\
\
After this method is called, when the merge insert operation executes,\
any rows that exist only in the source table will be inserted into\
the target table.\
\
_class_ lance.dataset.ScannerBuilder(_[ds](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder.__init__.ds"):[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "Link to this definition")apply\_defaults(_[default\_opts](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.apply_defaults "lance.dataset.ScannerBuilder.apply_defaults.default_opts"):dict\[str,Any\]_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.apply_defaults "Link to this definition")batch\_readahead(_[nbatches](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.batch_readahead "lance.dataset.ScannerBuilder.batch_readahead.nbatches"):int\|None= `None`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.batch_readahead "Link to this definition")\
\
This parameter is ignored when reading v2 files\
\
batch\_size(_[batch\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.batch_size "lance.dataset.ScannerBuilder.batch_size.batch_size"):int_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.batch_size "Link to this definition")\
\
Set batch size for Scanner\
\
columns(_[cols](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.columns "lance.dataset.ScannerBuilder.columns.cols"):list\[str\]\|dict\[str,str\]\|None= `None`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.columns "Link to this definition")fast\_search(_[flag](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.fast_search "lance.dataset.ScannerBuilder.fast_search.flag"):bool_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.fast_search "Link to this definition")\
\
Enable fast search, which only perform search on the indexed data.\
\
Users can use Table::optimize() or create\_index() to include the new data\
into index, thus make new data searchable.\
\
filter(_[filter](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.filter "lance.dataset.ScannerBuilder.filter.filter"):str\| [Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)")_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.filter "Link to this definition")fragment\_readahead(_[nfragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.fragment_readahead "lance.dataset.ScannerBuilder.fragment_readahead.nfragments"):int\|None= `None`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.fragment_readahead "Link to this definition")full\_text\_search(_[query](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.full_text_search.query "lance.dataset.ScannerBuilder.full_text_search.query — If str, the query string to search for, a match query would be performed. If Query, the query object to search for, and the columns parameter will be ignored."):str\|FullTextQuery_, _[columns](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.full_text_search.columns "lance.dataset.ScannerBuilder.full_text_search.columns — The columns to search in."):list\[str\]\|None= `None`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.full_text_search "Link to this definition")\
\
Filter rows by full text searching. _Experimental API_,\
may remove it after we support to do this within filter SQL-like expression\
\
Must create inverted index on the given column before searching,\
\
Parameters:query : str \| Query [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.full_text_search.query "Permalink to this definition")\
\
If str, the query string to search for, a match query would be performed.\
If Query, the query object to search for,\
and the columns parameter will be ignored.\
\
columns : list of str, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.full_text_search.columns "Permalink to this definition")\
\
The columns to search in. If None, search in all indexed columns.\
\
include\_deleted\_rows(_[flag](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.include_deleted_rows "lance.dataset.ScannerBuilder.include_deleted_rows.flag"):bool_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.include_deleted_rows "Link to this definition")\
\
Include deleted rows\
\
Rows which have been deleted, but are still present in the fragment, will be\
returned. These rows will have all columns (except \_rowaddr) set to null\
\
io\_buffer\_size(_[io\_buffer\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.io_buffer_size "lance.dataset.ScannerBuilder.io_buffer_size.io_buffer_size"):int_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.io_buffer_size "Link to this definition")\
\
Set the I/O buffer size for the Scanner\
\
This is the amount of RAM that will be reserved for holding I/O received from\
storage before it is processed. This is used to control the amount of memory\
used by the scanner. If the buffer is full then the scanner will block until\
the buffer is processed.\
\
Generally this should scale with the number of concurrent I/O threads. The\
default is 2GiB which comfortably provides enough space for somewhere between\
32 and 256 concurrent I/O threads.\
\
This value is not a hard cap on the amount of RAM the scanner will use. Some\
space is used for the compute (which can be controlled by the batch size) and\
Lance does not keep track of memory after it is returned to the user.\
\
Currently, if there is a single batch of data which is larger than the io buffer\
size then the scanner will deadlock. This is a known issue and will be fixed in\
a future release.\
\
This parameter is only used when reading v2 files\
\
late\_materialization(_[late\_materialization](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.late_materialization "lance.dataset.ScannerBuilder.late_materialization.late_materialization"):bool\|list\[str\]_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.late_materialization "Link to this definition")limit(_[n](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.limit "lance.dataset.ScannerBuilder.limit.n"):int\|None= `None`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.limit "Link to this definition")nearest(_[column](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.column"):str_, _[q](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.q"):QueryVectorLike_, _[k](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.k"):int\|None= `None`_, _[metric](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.metric"):str\|None= `None`_, _[nprobes](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.nprobes"):int\|None= `None`_, _[minimum\_nprobes](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.minimum_nprobes"):int\|None= `None`_, _[maximum\_nprobes](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.maximum_nprobes"):int\|None= `None`_, _[refine\_factor](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.refine_factor"):int\|None= `None`_, _[use\_index](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.use_index"):bool= `True`_, _[ef](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "lance.dataset.ScannerBuilder.nearest.ef"):int\|None= `None`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.nearest "Link to this definition")offset(_[n](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.offset "lance.dataset.ScannerBuilder.offset.n"):int\|None= `None`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.offset "Link to this definition")prefilter(_[prefilter](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.prefilter "lance.dataset.ScannerBuilder.prefilter.prefilter"):bool_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.prefilter "Link to this definition")scan\_in\_order(_[scan\_in\_order](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.scan_in_order "lance.dataset.ScannerBuilder.scan_in_order.scan_in_order"):bool= `True`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.scan_in_order "Link to this definition")\
\
Whether to scan the dataset in order of fragments and batches.\
\
If set to False, the scanner may read fragments concurrently and yield\
batches out of order. This may improve performance since it allows more\
concurrency in the scan, but can also use more memory.\
\
This parameter is ignored when using v2 files. In the v2 file format\
there is no penalty to scanning in order and so all scans will scan in\
order.\
\
scan\_stats\_callback(_[callback](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.scan_stats_callback "lance.dataset.ScannerBuilder.scan_stats_callback.callback"):Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics "_lib.ScanStatistics")\],None\]_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.scan_stats_callback "Link to this definition")\
\
Set a callback function that will be called with the scan statistics after the\
scan is complete. Errors raised by the callback will be logged but not\
re-raised.\
\
strict\_batch\_size(_[strict\_batch\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.strict_batch_size "lance.dataset.ScannerBuilder.strict_batch_size.strict_batch_size"):bool= `False`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.strict_batch_size "Link to this definition")\
\
If True, then all batches except the last batch will have exactly\
batch\_size rows.\
By default, it is false.\
If this is true then small batches will need to be merged together\
which will require a data copy and incur a (typically very small)\
performance penalty.\
\
to\_scanner()→[LanceScanner](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner "lance.dataset.LanceScanner — Execute the plan for this scanner and display with runtime metrics.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.to_scanner "Link to this definition")use\_scalar\_index(_[use\_scalar\_index](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.use_scalar_index "lance.dataset.ScannerBuilder.use_scalar_index.use_scalar_index"):bool= `True`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.use_scalar_index "Link to this definition")\
\
Set whether scalar indices should be used in a query\
\
Scans will use scalar indices, when available, to optimize queries with filters.\
However, in some corner cases, scalar indices may make performance worse. This\
parameter allows users to disable scalar indices in these cases.\
\
use\_stats(_[use\_stats](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.use_stats "lance.dataset.ScannerBuilder.use_stats.use_stats"):bool= `True`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.use_stats "Link to this definition")\
\
Enable use of statistics for query planning.\
\
Disabling statistics is used for debugging and benchmarking purposes.\
This should be left on for normal use.\
\
with\_fragments(_[fragments](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.with_fragments "lance.dataset.ScannerBuilder.with_fragments.fragments"):Iterable\[ [LanceFragment](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment — Count rows matching the scanner filter.")\]\|None_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.with_fragments "Link to this definition")with\_row\_address(_[with\_row\_address](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.with_row_address "lance.dataset.ScannerBuilder.with_row_address.with_row_address"):bool= `True`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.with_row_address "Link to this definition")\
\
Enables returns with row addresses.\
\
Row addresses are a unique but unstable identifier for each row in the\
dataset that consists of the fragment id (upper 32 bits) and the row\
offset in the fragment (lower 32 bits). Row IDs are generally preferred\
since they do not change when a row is modified or compacted. However,\
row addresses may be useful in some advanced use cases.\
\
with\_row\_id(_[with\_row\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.with_row_id "lance.dataset.ScannerBuilder.with_row_id.with_row_id"):bool= `True`_)→[ScannerBuilder](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder "lance.dataset.ScannerBuilder — This parameter is ignored when reading v2 files") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.ScannerBuilder.with_row_id "Link to this definition")\
\
Enable returns with row IDs.\
\
_class_ lance.dataset.Tag [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tag "Link to this definition")manifest\_size:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tag.manifest_size "Link to this definition")version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tag.version "Link to this definition")_class_ lance.dataset.Tags(_[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags "lance.dataset.Tags.__init__.dataset"):\_Dataset_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags "Link to this definition")\
\
Dataset tag manager.\
\
create(_[tag](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.create.tag "lance.dataset.Tags.create.tag — The name of the tag to create."):str_, _[version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.create.version "lance.dataset.Tags.create.version — The dataset version to tag."):int_)→None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.create "Link to this definition")\
\
Create a tag for a given dataset version.\
\
Parameters:tag : str, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.create.tag "Permalink to this definition")\
\
The name of the tag to create. This name must be unique among all tag\
names for the dataset.\
\
version : int, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.create.version "Permalink to this definition")\
\
The dataset version to tag.\
\
delete(_[tag](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.delete.tag "lance.dataset.Tags.delete.tag — The name of the tag to delete."):str_)→None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.delete "Link to this definition")\
\
Delete tag from the dataset.\
\
Parameters:tag : str, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.delete.tag "Permalink to this definition")\
\
The name of the tag to delete.\
\
list()→dict\[str, [Tag](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tag "lance.dataset.Tag — manifest_size : int      version : int")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.list "Link to this definition")\
\
List all dataset tags.\
\
Returns:\
\
A dictionary mapping tag names to version numbers.\
\
Return type:\
\
dict\[str, [Tag](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tag "lance.dataset.Tag — manifest_size : int      version : int")\]\
\
update(_[tag](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.update.tag "lance.dataset.Tags.update.tag — The name of the tag to update."):str_, _[version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.update.version "lance.dataset.Tags.update.version — The new dataset version to tag."):int_)→None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.update "Link to this definition")\
\
Update tag to a new version.\
\
Parameters:tag : str, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.update.tag "Permalink to this definition")\
\
The name of the tag to update.\
\
version : int, [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Tags.update.version "Permalink to this definition")\
\
The new dataset version to tag.\
\
_class_ lance.dataset.Transaction(_[read\_version:'int'](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction.__init__.read_version: 'int'")_, _[operation:'LanceOperation.BaseOperation'](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction.__init__.operation: 'LanceOperation.BaseOperation'")_, _[uuid:'str'=<factory>](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction.__init__.uuid: 'str' = <factory>")_, _[blobs\_op:'Optional\[LanceOperation.BaseOperation\]'=None](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "lance.dataset.Transaction.__init__.blobs_op: 'Optional[LanceOperation.BaseOperation]' = None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction "Link to this definition")blobs\_op:[BaseOperation](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.BaseOperation "lance.dataset.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") \|None=`None` [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction.blobs_op "Link to this definition")operation:[BaseOperation](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.BaseOperation "lance.dataset.LanceOperation.BaseOperation — Base class for operations that can be applied to a dataset.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction.operation "Link to this definition")read\_version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction.read_version "Link to this definition")uuid:str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Transaction.uuid "Link to this definition")_class_ lance.dataset.UpdateResult [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.UpdateResult "Link to this definition")num\_rows\_updated:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.UpdateResult.num_rows_updated "Link to this definition")_class_ lance.dataset.VectorIndexReader(_[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.__init__.dataset "lance.dataset.VectorIndexReader.__init__.dataset — The dataset containing the index."):[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[index\_name](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.__init__.index_name "lance.dataset.VectorIndexReader.__init__.index_name — The name of the vector index to read."):str_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader "Link to this definition")\
\
This class allows you to initialize a reader for a specific vector index,\
retrieve the number of partitions,\
access the centroids of the index,\
and read specific partitions of the index.\
\
Parameters:dataset : [LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.__init__.dataset "Permalink to this definition")\
\
The dataset containing the index.\
\
index\_name : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.__init__.index_name "Permalink to this definition")\
\
The name of the vector index to read.\
\
Examples\
\
```\
import lance\
from lance.dataset import VectorIndexReader\
import numpy as np\
import pyarrow as pa\
vectors = np.random.rand(256, 2)\
data = pa.table({"vector": pa.array(vectors.tolist(),\
    type=pa.list_(pa.float32(), 2))})\
dataset = lance.write_dataset(data, "/tmp/index_reader_demo")\
dataset.create_index("vector", index_type="IVF_PQ",\
    num_partitions=4, num_sub_vectors=2)\
reader = VectorIndexReader(dataset, "vector_idx")\
assert reader.num_partitions() == 4\
partition = reader.read_partition(0)\
assert "_rowid" in partition.column_names\
\
```\
\
# Exceptions [¶](https://lancedb.github.io/lance/api/py_modules.html\#exceptions "Link to this heading")\
\
ValueError\
\
If the specified index is not a vector index.\
\
centroids()→[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.2)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.centroids "Link to this definition")\
\
Returns the centroids of the index\
\
Returns:\
\
The centroids of IVF\
with shape (num\_partitions, dim)\
\
Return type:\
\
np.ndarray\
\
num\_partitions()→int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.num_partitions "Link to this definition")\
\
Returns the number of partitions in the dataset.\
\
Returns:\
\
The number of partitions.\
\
Return type:\
\
int\
\
read\_partition(_[partition\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.read_partition.partition_id "lance.dataset.VectorIndexReader.read_partition.partition_id — The id of the partition to read"):int_, _\*_, _[with\_vector](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.read_partition.with_vector "lance.dataset.VectorIndexReader.read_partition.with_vector — Whether to include the vector column in the reader, for IVF_PQ, the vector column is PQ codes"):bool= `False`_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.read_partition "Link to this definition")\
\
Returns a pyarrow table for the given IVF partition\
\
Parameters:partition\_id : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.read_partition.partition_id "Permalink to this definition")\
\
The id of the partition to read\
\
with\_vector : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.VectorIndexReader.read_partition.with_vector "Permalink to this definition")\
\
Whether to include the vector column in the reader,\
for IVF\_PQ, the vector column is PQ codes\
\
Returns:\
\
A pyarrow table for the given partition,\
containing the row IDs, and quantized vectors (if with\_vector is True).\
\
Return type:\
\
pa.Table\
\
_class_ lance.dataset.Version [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Version "Link to this definition")metadata:Dict\[str,str\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Version.metadata "Link to this definition")timestamp:int\|datetime [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Version.timestamp "Link to this definition")version:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.Version.version "Link to this definition")lance.dataset.write\_dataset(_[data\_obj](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.data_obj "lance.dataset.write_dataset.data_obj — The data to be written."):ReaderLike_, _[uri](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.uri "lance.dataset.write_dataset.uri — Where to write the dataset to (directory)."):str\|Path\| [LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.schema "lance.dataset.write_dataset.schema — If specified and the input is a pandas DataFrame, use this schema instead of the default pandas to arrow table conversion."):pa.Schema\|None= `None`_, _[mode](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.mode "lance.dataset.write_dataset.mode — create - create a new dataset (raises if uri already exists). overwrite - create a new snapshot version append - create a new version that is the concat of the input the latest version (raises if uri does not exist)"):str= `'create'`_, _\*_, _[max\_rows\_per\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.max_rows_per_file "lance.dataset.write_dataset.max_rows_per_file — The max number of rows to write before starting a new file"):int= `1048576`_, _[max\_rows\_per\_group](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.max_rows_per_group "lance.dataset.write_dataset.max_rows_per_group — The max number of rows before starting a new group (in the same file)"):int= `1024`_, _[max\_bytes\_per\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.max_bytes_per_file "lance.dataset.write_dataset.max_bytes_per_file — The max number of bytes to write before starting a new file."):int= `96636764160`_, _[commit\_lock](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.commit_lock "lance.dataset.write_dataset.commit_lock — A custom commit lock."):CommitLock\|None= `None`_, _[progress](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.progress "lance.dataset.write_dataset.progress — Experimental API."):FragmentWriteProgress\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.storage_options "lance.dataset.write_dataset.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[data\_storage\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.data_storage_version "lance.dataset.write_dataset.data_storage_version — The version of the data storage format to use."):str\|None= `None`_, _[use\_legacy\_format](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.use_legacy_format "lance.dataset.write_dataset.use_legacy_format — Deprecated method for setting the data storage version."):bool\|None= `None`_, _[enable\_v2\_manifest\_paths](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.enable_v2_manifest_paths "lance.dataset.write_dataset.enable_v2_manifest_paths — If True, and this is a new dataset, uses the new V2 manifest paths. These paths provide more efficient opening of datasets with many versions on object stores."):bool= `False`_, _[enable\_move\_stable\_row\_ids](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.enable_move_stable_row_ids "lance.dataset.write_dataset.enable_move_stable_row_ids — Experimental parameter: if set to true, the writer will use move-stable row ids. These row ids are stable after compaction operations, but not after updates. This makes compaction more efficient, since with stable row ids no secondary indices need to be updated to point to new row ids."):bool= `False`_, _[auto\_cleanup\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.auto_cleanup_options "lance.dataset.write_dataset.auto_cleanup_options — Config options for automatic cleanup of the dataset. If set, and this is a new dataset, old dataset versions will be automatically cleaned up according to this parameter. To add autocleaning to an existing dataset, use Dataset::update_config to set lance.auto_cleanup.interval and lance.auto_cleanup.older_than. Both parameters must be set to invoke autocleaning. If you do not set this parameter(default behavior), then no autocleaning will be performed. Note: this option only takes effect when creating a new dataset, it has no effect on existing datasets."):[AutoCleanupConfig](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AutoCleanupConfig "lance.dataset.AutoCleanupConfig — interval : int      older_than_seconds : int") \|None= `None`_)→[LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset "Link to this definition")\
\
Write a given data\_obj to the given uri\
\
Parameters:data\_obj : Reader-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.data_obj "Permalink to this definition")\
\
The data to be written. Acceptable types are:\
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner, or RecordBatchReader\
\- Huggingface dataset\
\
uri : str, Path, or [LanceDataset](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset "lance.dataset.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.uri "Permalink to this definition")\
\
Where to write the dataset to (directory). If a LanceDataset is passed,\
the session will be reused.\
\
schema : Schema, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.schema "Permalink to this definition")\
\
If specified and the input is a pandas DataFrame, use this schema\
instead of the default pandas to arrow table conversion.\
\
mode : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.mode "Permalink to this definition")\
\
**create** \- create a new dataset (raises if uri already exists).\
**overwrite** \- create a new snapshot version\
**append** \- create a new version that is the concat of the input the\
latest version (raises if uri does not exist)\
\
max\_rows\_per\_file : int, default 1024 \* 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.max_rows_per_file "Permalink to this definition")\
\
The max number of rows to write before starting a new file\
\
max\_rows\_per\_group : int, default 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.max_rows_per_group "Permalink to this definition")\
\
The max number of rows before starting a new group (in the same file)\
\
max\_bytes\_per\_file : int, default 90 \* 1024 \* 1024 \* 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.max_bytes_per_file "Permalink to this definition")\
\
The max number of bytes to write before starting a new file. This is a\
soft limit. This limit is checked after each group is written, which\
means larger groups may cause this to be overshot meaningfully. This\
defaults to 90 GB, since we have a hard limit of 100 GB per file on\
object stores.\
\
commit\_lock : CommitLock, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.commit_lock "Permalink to this definition")\
\
A custom commit lock. Only needed if your object store does not support\
atomic commits. See the user guide for more details.\
\
progress : FragmentWriteProgress, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.progress "Permalink to this definition")\
\
_Experimental API_. Progress tracking for writing the fragment. Pass\
a custom class that defines hooks to be called when each fragment is\
starting to write and finishing writing.\
\
storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.storage_options "Permalink to this definition")\
\
Extra options that make sense for a particular storage connection. This is\
used to store connection parameters like credentials, endpoint, etc.\
\
data\_storage\_version : optional, str, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.data_storage_version "Permalink to this definition")\
\
The version of the data storage format to use. Newer versions are more\
efficient but require newer versions of lance to read. The default (None)\
will use the latest stable version. See the user guide for more details.\
\
use\_legacy\_format : optional, bool, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.use_legacy_format "Permalink to this definition")\
\
Deprecated method for setting the data storage version. Use the\
data\_storage\_version parameter instead.\
\
enable\_v2\_manifest\_paths : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.enable_v2_manifest_paths "Permalink to this definition")\
\
If True, and this is a new dataset, uses the new V2 manifest paths.\
These paths provide more efficient opening of datasets with many\
versions on object stores. This parameter has no effect if the dataset\
already exists. To migrate an existing dataset, instead use the\
[`LanceDataset.migrate_manifest_paths_v2()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.migrate_manifest_paths_v2 "lance.dataset.LanceDataset.migrate_manifest_paths_v2 — Migrate the manifest paths to the new format.") method. Default is False.\
\
enable\_move\_stable\_row\_ids : bool, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.enable_move_stable_row_ids "Permalink to this definition")\
\
Experimental parameter: if set to true, the writer will use move-stable row ids.\
These row ids are stable after compaction operations, but not after updates.\
This makes compaction more efficient, since with stable row ids no\
secondary indices need to be updated to point to new row ids.\
\
auto\_cleanup\_options : optional, [AutoCleanupConfig](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.AutoCleanupConfig "lance.dataset.AutoCleanupConfig — interval : int      older_than_seconds : int") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset.auto_cleanup_options "Permalink to this definition")\
\
Config options for automatic cleanup of the dataset.\
If set, and this is a new dataset, old dataset versions will be automatically\
cleaned up according to this parameter.\
To add autocleaning to an existing dataset, use Dataset::update\_config to set\
lance.auto\_cleanup.interval and lance.auto\_cleanup.older\_than.\
Both parameters must be set to invoke autocleaning.\
If you do not set this parameter(default behavior),\
then no autocleaning will be performed.\
Note: this option only takes effect when creating a new dataset,\
it has no effect on existing datasets.\
\
Dataset Fragment\
\
_class_ lance.fragment.DataFile(_[path](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile.__init__.path"):str_, _[fields](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile.__init__.fields"):list\[int\]_, _[column\_indices](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile.__init__.column_indices"):list\[int\]= `None`_, _[file\_major\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile.__init__.file_major_version"):int= `0`_, _[file\_minor\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile.__init__.file_minor_version"):int= `0`_, _[file\_size\_bytes](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile.__init__.file_size_bytes"):int\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "Link to this definition")\
\
A data file in a fragment.\
\
path [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile.path "Link to this definition")\
\
The path to the data file.\
\
Type:\
\
str\
\
fields [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile.fields "Link to this definition")\
\
The field ids of the columns in this file.\
\
Type:\
\
List\[int\]\
\
column\_indices [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile.column_indices "Link to this definition")\
\
The column indices where the fields are stored in the file. Will have\
the same length as fields.\
\
Type:\
\
List\[int\]\
\
file\_major\_version [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile.file_major_version "Link to this definition")\
\
The major version of the data storage format.\
\
Type:\
\
int\
\
file\_minor\_version [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile.file_minor_version "Link to this definition")\
\
The minor version of the data storage format.\
\
Type:\
\
int\
\
file\_size\_bytes [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile.file_size_bytes "Link to this definition")\
\
The size of the data file in bytes, if available.\
\
Type:\
\
Optional\[int\]\
\
column\_indices:List\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id49 "Link to this definition")field\_ids()→list\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile.field_ids "Link to this definition")fields:List\[int\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id50 "Link to this definition")file\_major\_version:int=`0` [¶](https://lancedb.github.io/lance/api/py_modules.html#id51 "Link to this definition")file\_minor\_version:int=`0` [¶](https://lancedb.github.io/lance/api/py_modules.html#id52 "Link to this definition")file\_size\_bytes:int\|None=`None` [¶](https://lancedb.github.io/lance/api/py_modules.html#id53 "Link to this definition")_property_ path:str [¶](https://lancedb.github.io/lance/api/py_modules.html#id54 "Link to this definition")_class_ lance.fragment.DeletionFile(_[read\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile.__init__.read_version")_, _[id](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile.__init__.id")_, _[file\_type](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile.__init__.file_type")_, _[num\_deleted\_rows](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile.__init__.num_deleted_rows")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "Link to this definition")asdict() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.asdict "Link to this definition")file\_type [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.file_type "Link to this definition")_static_ from\_json(_[json](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.from_json "lance.fragment.DeletionFile.from_json.json")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.from_json "Link to this definition")id [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.id "Link to this definition")json() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.json "Link to this definition")num\_deleted\_rows [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.num_deleted_rows "Link to this definition")path(_[fragment\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.path "lance.fragment.DeletionFile.path.fragment_id")_, _[base\_uri](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.path "lance.fragment.DeletionFile.path.base_uri") = `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.path "Link to this definition")read\_version [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile.read_version "Link to this definition")_class_ lance.fragment.FragmentMetadata(_[id](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata.__init__.id"):int_, _[files](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata.__init__.files"):list\[ [DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")\]_, _[physical\_rows](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata.__init__.physical_rows"):int_, _[deletion\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata.__init__.deletion_file"):[DeletionFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile — asdict()      file_type      static from_json(json)      id      json()      num_deleted_rows      path(fragment_id, base_uri=None)      read_version") \|None= `None`_, _[row\_id\_meta](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata.__init__.row_id_meta"):[RowIdMeta](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta "lance.fragment.RowIdMeta — asdict()      static from_json(json)      json()") \|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "Link to this definition")\
\
Metadata for a fragment.\
\
id [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.id "Link to this definition")\
\
The ID of the fragment.\
\
Type:\
\
int\
\
files [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.files "Link to this definition")\
\
The data files of the fragment. Each data file must have the same number\
of rows. Each file stores a different subset of the columns.\
\
Type:\
\
List\[ [DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")\]\
\
physical\_rows [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.physical_rows "Link to this definition")\
\
The number of rows originally in this fragment. This is the number of rows\
in the data files before deletions.\
\
Type:\
\
int\
\
deletion\_file [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.deletion_file "Link to this definition")\
\
The deletion file, if any.\
\
Type:\
\
Optional\[ [DeletionFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile — asdict()      file_type      static from_json(json)      id      json()      num_deleted_rows      path(fragment_id, base_uri=None)      read_version")\]\
\
row\_id\_meta [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.row_id_meta "Link to this definition")\
\
The row id metadata, if any.\
\
Type:\
\
Optional\[ [RowIdMeta](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta "lance.fragment.RowIdMeta — asdict()      static from_json(json)      json()")\]\
\
data\_files()→list\[ [DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.data_files "Link to this definition")deletion\_file:[DeletionFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DeletionFile "lance.fragment.DeletionFile — asdict()      file_type      static from_json(json)      id      json()      num_deleted_rows      path(fragment_id, base_uri=None)      read_version") \|None=`None` [¶](https://lancedb.github.io/lance/api/py_modules.html#id55 "Link to this definition")files:List\[ [DataFile](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.DataFile "lance.fragment.DataFile — A data file in a fragment.")\] [¶](https://lancedb.github.io/lance/api/py_modules.html#id56 "Link to this definition")_static_ from\_json(_[json\_data](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.from_json "lance.fragment.FragmentMetadata.from_json.json_data"):str_)→[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.from_json "Link to this definition")id:int [¶](https://lancedb.github.io/lance/api/py_modules.html#id57 "Link to this definition")_property_ num\_deletions:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.num_deletions "Link to this definition")\
\
The number of rows that have been deleted from this fragment.\
\
_property_ num\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.num_rows "Link to this definition")\
\
The number of rows in this fragment after deletions.\
\
physical\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#id58 "Link to this definition")row\_id\_meta:[RowIdMeta](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta "lance.fragment.RowIdMeta — asdict()      static from_json(json)      json()") \|None=`None` [¶](https://lancedb.github.io/lance/api/py_modules.html#id59 "Link to this definition")to\_json()→dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata.to_json "Link to this definition")\
\
Get this as a simple JSON-serializable dictionary.\
\
_class_ lance.fragment.LanceFragment(_[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment.__init__.dataset"):[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[fragment\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment.__init__.fragment_id"):int\|None_, _\*_, _[fragment](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment.__init__.fragment"):\_Fragment\|None= `None`_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "Link to this definition")count\_rows(_[self](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.self")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "Link to this definition")\
\
Count rows matching the scanner filter.\
\
Parameters:filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Returns:\
\
**count**\
\
Return type:\
\
int\
\
_static_ create(_[dataset\_uri](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.dataset_uri "lance.fragment.LanceFragment.create.dataset_uri — The URI of the dataset."):str\|Path_, _[data](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.data "lance.fragment.LanceFragment.create.data — The data to be written to the fragment."):ReaderLike_, _[fragment\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.fragment_id "lance.fragment.LanceFragment.create.fragment_id — The ID of the fragment."):int\|None= `None`_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.schema "lance.fragment.LanceFragment.create.schema — The schema of the data."):pa.Schema\|None= `None`_, _[max\_rows\_per\_group](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.max_rows_per_group "lance.fragment.LanceFragment.create.max_rows_per_group — The maximum number of rows per group in the data file."):int= `1024`_, _[progress](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.progress "lance.fragment.LanceFragment.create.progress — Experimental API."):FragmentWriteProgress\|None= `None`_, _[mode](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.mode "lance.fragment.LanceFragment.create.mode — The write mode."):str= `'append'`_, _\*_, _[data\_storage\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.data_storage_version "lance.fragment.LanceFragment.create.data_storage_version — The version of the data storage format to use."):str\|None= `None`_, _[use\_legacy\_format](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.use_legacy_format "lance.fragment.LanceFragment.create.use_legacy_format — Deprecated parameter."):bool\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.storage_options "lance.fragment.LanceFragment.create.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_)→[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create "Link to this definition")\
\
Create a [`FragmentMetadata`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") from the given data.\
\
This can be used if the dataset is not yet created.\
\
Warning\
\
Internal API. This method is not intended to be used by end users.\
\
Parameters:dataset\_uri : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.dataset_uri "Permalink to this definition")\
\
The URI of the dataset.\
\
fragment\_id : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.fragment_id "Permalink to this definition")\
\
The ID of the fragment.\
\
data : pa.Table or pa.RecordBatchReader [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.data "Permalink to this definition")\
\
The data to be written to the fragment.\
\
schema : pa.Schema, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.schema "Permalink to this definition")\
\
The schema of the data. If not specified, the schema will be inferred\
from the data.\
\
max\_rows\_per\_group : int, default 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.max_rows_per_group "Permalink to this definition")\
\
The maximum number of rows per group in the data file.\
\
progress : FragmentWriteProgress, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.progress "Permalink to this definition")\
\
_Experimental API_. Progress tracking for writing the fragment. Pass\
a custom class that defines hooks to be called when each fragment is\
starting to write and finishing writing.\
\
mode : str, default "append" [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.mode "Permalink to this definition")\
\
The write mode. If “append” is specified, the data will be checked\
against the existing dataset’s schema. Otherwise, pass “create” or\
“overwrite” to assign new field ids to the schema.\
\
data\_storage\_version : optional, str, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.data_storage_version "Permalink to this definition")\
\
The version of the data storage format to use. Newer versions are more\
efficient but require newer versions of lance to read. The default (None)\
will use the latest stable version. See the user guide for more details.\
\
use\_legacy\_format : bool, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.use_legacy_format "Permalink to this definition")\
\
Deprecated parameter. Use data\_storage\_version instead.\
\
storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create.storage_options "Permalink to this definition")\
\
Extra options that make sense for a particular storage connection. This is\
used to store connection parameters like credentials, endpoint, etc.\
\
See also\
\
[`lance.dataset.LanceOperation.Overwrite`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Overwrite "lance.dataset.LanceOperation.Overwrite — Overwrite or create a new dataset.")\
\
The operation used to create a new dataset or overwrite one using fragments created with this API. See the doc page for an example of using this API.\
\
[`lance.dataset.LanceOperation.Append`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Append "lance.dataset.LanceOperation.Append — Append new rows to the dataset.")\
\
The operation used to append fragments created with this API to an existing dataset. See the doc page for an example of using this API.\
\
Return type:\
\
[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\
\
_static_ create\_from\_file(_[filename](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create_from_file.filename "lance.fragment.LanceFragment.create_from_file.filename — The filename of the datafile."):str_, _[dataset](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create_from_file.dataset "lance.fragment.LanceFragment.create_from_file.dataset — The dataset that the fragment belongs to."):[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[fragment\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create_from_file.fragment_id "lance.fragment.LanceFragment.create_from_file.fragment_id — The ID of the fragment."):int_)→[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create_from_file "Link to this definition")\
\
Create a fragment from the given datafile uri.\
\
This can be used if the datafile is loss from dataset.\
\
Warning\
\
Internal API. This method is not intended to be used by end users.\
\
Parameters:filename : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create_from_file.filename "Permalink to this definition")\
\
The filename of the datafile.\
\
dataset : [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create_from_file.dataset "Permalink to this definition")\
\
The dataset that the fragment belongs to.\
\
fragment\_id : int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.create_from_file.fragment_id "Permalink to this definition")\
\
The ID of the fragment.\
\
data\_files() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.data_files "Link to this definition")\
\
Return the data files of this fragment.\
\
delete(_[predicate](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.delete.predicate "lance.fragment.LanceFragment.delete.predicate — A SQL predicate that specifies the rows to delete."):str_)→[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") \|None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.delete "Link to this definition")\
\
Delete rows from this Fragment.\
\
This will add or update the deletion file of this fragment. It does not\
modify or delete the data files of this fragment. If no rows are left after\
the deletion, this method will return None.\
\
Warning\
\
Internal API. This method is not intended to be used by end users.\
\
Parameters:predicate : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.delete.predicate "Permalink to this definition")\
\
A SQL predicate that specifies the rows to delete.\
\
Returns:\
\
A new fragment containing the new deletion file, or None if no rows left.\
\
Return type:\
\
[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") or None\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> tab = pa.table({"a": [1, 2, 3], "b": [4, 5, 6]})\
>>> dataset = lance.write_dataset(tab, "dataset")\
>>> frag = dataset.get_fragment(0)\
>>> frag.delete("a > 1")\
FragmentMetadata(id=0, files=[DataFile(path='...', fields=[0, 1], ...), ...)\
>>> frag.delete("a > 0") is None\
True\
\
```\
\
See also\
\
[`lance.dataset.LanceOperation.Delete`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Delete "lance.dataset.LanceOperation.Delete — Remove fragments or rows from the dataset.")\
\
The operation used to commit these changes to a dataset. See the doc page for an example of using this API.\
\
deletion\_file() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.deletion_file "Link to this definition")\
\
Return the deletion file, if any\
\
_property_ fragment\_id [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.fragment_id "Link to this definition")head(_[self](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.self")_, _[intnum\_rows](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.int num_rows")_, _[columns=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.columns=None")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "lance.fragment.LanceFragment.head.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.head "Link to this definition")\
\
Load the first N rows of the fragment.\
\
Parameters:num\_rows : int\
\
The number of rows to load.\
\
columns : list of str, default None\
\
The columns to project. This can be a list of column names to\
include (order and duplicates will be preserved), or a dictionary\
with {new\_column\_name: expression} values for more advanced\
projections.\
\
The list of columns or expressions may use the special fields\
\_\_batch\_index (the index of the batch within the fragment),\
\_\_fragment\_index (the index of the fragment within the dataset),\
\_\_last\_in\_fragment (whether the batch is last in fragment), and\
\_\_filename (the name of the source file or a description of the\
source fragment).\
\
The columns will be passed down to Datasets and corresponding data\
fragments to avoid loading, copying, and deserializing columns\
that will not be required further down the compute chain.\
By default all of the available columns are projected. Raises\
an exception if any of the referenced column names does not exist\
in the dataset’s Schema.\
\
filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Return type:\
\
Table\
\
merge(_[data\_obj](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge.data_obj "lance.fragment.LanceFragment.merge.data_obj — The data to be merged."):ReaderLike_, _[left\_on](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge.left_on "lance.fragment.LanceFragment.merge.left_on — The name of the column in the dataset to join on."):str_, _[right\_on](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge.right_on "lance.fragment.LanceFragment.merge.right_on — The name of the column in data_obj to join on."):str\|None= `None`_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge "lance.fragment.LanceFragment.merge.schema") = `None`_)→tuple\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment."),LanceSchema\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge "Link to this definition")\
\
Merge another dataset into this fragment.\
\
Performs a left join, where the fragment is the left side and data\_obj\
is the right side. Rows existing in the dataset but not on the left will\
be filled with null values, unless Lance doesn’t support null values for\
some types, in which case an error will be raised.\
\
Parameters:data\_obj : Reader-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge.data_obj "Permalink to this definition")\
\
The data to be merged. Acceptable types are:\
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner,\
Iterator\[RecordBatch\], or RecordBatchReader\
\
left\_on : str [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge.left_on "Permalink to this definition")\
\
The name of the column in the dataset to join on.\
\
right\_on : str or None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge.right_on "Permalink to this definition")\
\
The name of the column in data\_obj to join on. If None, defaults to\
left\_on.\
\
Examples\
\
```\
>>> import lance\
>>> import pyarrow as pa\
>>> df = pa.table({'x': [1, 2, 3], 'y': ['a', 'b', 'c']})\
>>> dataset = lance.write_dataset(df, "dataset")\
>>> dataset.to_table().to_pandas()\
   x  y\
0  1  a\
1  2  b\
2  3  c\
>>> fragments = dataset.get_fragments()\
>>> new_df = pa.table({'x': [1, 2, 3], 'z': ['d', 'e', 'f']})\
>>> merged = []\
>>> schema = None\
>>> for f in fragments:\
...     f, schema = f.merge(new_df, 'x')\
...     merged.append(f)\
>>> merge = lance.LanceOperation.Merge(merged, schema)\
>>> dataset = lance.LanceDataset.commit("dataset", merge, read_version=1)\
>>> dataset.to_table().to_pandas()\
   x  y  z\
0  1  a  d\
1  2  b  e\
2  3  c  f\
\
```\
\
See also\
\
`LanceDataset.merge_columns`\
\
Add columns to this Fragment.\
\
Returns:\
\
A new fragment with the merged column(s) and the final schema.\
\
Return type:\
\
Tuple\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment."), LanceSchema\]\
\
merge\_columns(_[value\_func](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge_columns "lance.fragment.LanceFragment.merge_columns.value_func"):dict\[str,str\]\|BatchUDF\|ReaderLike\|collections.abc.Callable\[\[pa.RecordBatch\],pa.RecordBatch\]_, _[columns](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge_columns "lance.fragment.LanceFragment.merge_columns.columns"):list\[str\]\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge_columns "lance.fragment.LanceFragment.merge_columns.batch_size"):int\|None= `None`_, _[reader\_schema](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge_columns "lance.fragment.LanceFragment.merge_columns.reader_schema"):pa.Schema\|None= `None`_)→tuple\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment."),LanceSchema\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.merge_columns "Link to this definition")\
\
Add columns to this Fragment.\
\
Warning\
\
Internal API. This method is not intended to be used by end users.\
\
The parameters and their interpretation are the same as in the\
[`lance.dataset.LanceDataset.add_columns()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.add_columns "lance.dataset.LanceDataset.add_columns — Add new columns with defined values.") operation.\
\
The only difference is that, instead of modifying the dataset, a new\
fragment is created. The new schema of the fragment is returned as well.\
These can be used in a later operation to commit the changes to the dataset.\
\
See also\
\
[`lance.dataset.LanceOperation.Merge`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceOperation.Merge "lance.dataset.LanceOperation.Merge — Operation that adds columns. Unlike Overwrite, this should not change the structure of the fragments, allowing existing indices to be kept.")\
\
The operation used to commit these changes to the dataset. See the doc page for an example of using this API.\
\
Returns:\
\
A new fragment with the added column(s) and the final schema.\
\
Return type:\
\
Tuple\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment."), LanceSchema\]\
\
_property_ metadata:[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.metadata "Link to this definition")\
\
Return the metadata of this fragment.\
\
Return type:\
\
[FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\
\
_property_ num\_deletions:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.num_deletions "Link to this definition")\
\
Return the number of deleted rows in this fragment.\
\
_property_ partition\_expression:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.partition_expression "Link to this definition")\
\
An Expression which evaluates to true for all data viewed by this\
Fragment.\
\
_property_ physical\_rows:int [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.physical_rows "Link to this definition")\
\
Return the number of rows originally in this fragment.\
\
To get the number of rows after deletions, use\
[`count_rows()`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.count_rows "lance.fragment.LanceFragment.count_rows — Count rows matching the scanner filter.") instead.\
\
_property_ physical\_schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.physical_schema "Link to this definition")\
\
Return the physical schema of this Fragment. This schema can be\
different from the dataset read schema.\
\
scanner(_\*_, _[columns](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "lance.fragment.LanceFragment.scanner.columns"):list\[str\]\|dict\[str,str\]\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "lance.fragment.LanceFragment.scanner.batch_size"):int\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "lance.fragment.LanceFragment.scanner.filter"):str\|pa.compute.Expression\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "lance.fragment.LanceFragment.scanner.limit"):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "lance.fragment.LanceFragment.scanner.offset"):int\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "lance.fragment.LanceFragment.scanner.with_row_id"):bool= `False`_, _[with\_row\_address](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "lance.fragment.LanceFragment.scanner.with_row_address"):bool= `False`_, _[batch\_readahead](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "lance.fragment.LanceFragment.scanner.batch_readahead"):int= `16`_)→[LanceScanner](https://lancedb.github.io/lance/api/python/LanceScanner.html "lance.LanceScanner — Initialize self.  See help(type(self)) for accurate signature.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.scanner "Link to this definition")\
\
See Dataset::scanner for details\
\
_property_ schema:[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.schema "Link to this definition")\
\
Return the schema of this fragment.\
\
take(_[self](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.self")_, _[indices](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take.indices "lance.fragment.LanceFragment.take.indices — The indices of row to select in the dataset.")_, _[columns=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.columns=None")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "lance.fragment.LanceFragment.take.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take "Link to this definition")\
\
Select rows of data by index.\
\
Parameters:indices : Array or array-like [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.take.indices "Permalink to this definition")\
\
The indices of row to select in the dataset.\
\
columns : list of str, default None\
\
The columns to project. This can be a list of column names to\
include (order and duplicates will be preserved), or a dictionary\
with {new\_column\_name: expression} values for more advanced\
projections.\
\
The list of columns or expressions may use the special fields\
\_\_batch\_index (the index of the batch within the fragment),\
\_\_fragment\_index (the index of the fragment within the dataset),\
\_\_last\_in\_fragment (whether the batch is last in fragment), and\
\_\_filename (the name of the source file or a description of the\
source fragment).\
\
The columns will be passed down to Datasets and corresponding data\
fragments to avoid loading, copying, and deserializing columns\
that will not be required further down the compute chain.\
By default all of the available columns are projected. Raises\
an exception if any of the referenced column names does not exist\
in the dataset’s Schema.\
\
filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Return type:\
\
Table\
\
to\_batches(_[self](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.self")_, _[Schemaschema=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.Schema schema=None")_, _[columns=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.columns=None")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "lance.fragment.LanceFragment.to_batches.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_batches "Link to this definition")\
\
Read the fragment as materialized record batches.\
\
Parameters:schema : Schema, optional\
\
Concrete schema to use for scanning.\
\
columns : list of str, default None\
\
The columns to project. This can be a list of column names to\
include (order and duplicates will be preserved), or a dictionary\
with {new\_column\_name: expression} values for more advanced\
projections.\
\
The list of columns or expressions may use the special fields\
\_\_batch\_index (the index of the batch within the fragment),\
\_\_fragment\_index (the index of the fragment within the dataset),\
\_\_last\_in\_fragment (whether the batch is last in fragment), and\
\_\_filename (the name of the source file or a description of the\
source fragment).\
\
The columns will be passed down to Datasets and corresponding data\
fragments to avoid loading, copying, and deserializing columns\
that will not be required further down the compute chain.\
By default all of the available columns are projected. Raises\
an exception if any of the referenced column names does not exist\
in the dataset’s Schema.\
\
filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Returns:\
\
**record\_batches**\
\
Return type:\
\
iterator of RecordBatch\
\
to\_table(_[self](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.self")_, _[Schemaschema=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.Schema schema=None")_, _[columns=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.columns=None")_, _[Expressionfilter=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.Expression filter=None")_, _[intbatch\_size=\_DEFAULT\_BATCH\_SIZE](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.int batch_size=_DEFAULT_BATCH_SIZE")_, _[intbatch\_readahead=\_DEFAULT\_BATCH\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.int batch_readahead=_DEFAULT_BATCH_READAHEAD")_, _[intfragment\_readahead=\_DEFAULT\_FRAGMENT\_READAHEAD](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.int fragment_readahead=_DEFAULT_FRAGMENT_READAHEAD")_, _[FragmentScanOptionsfragment\_scan\_options=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.FragmentScanOptions fragment_scan_options=None")_, _[booluse\_threads=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.bool use_threads=True")_, _[boolcache\_metadata=True](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.bool cache_metadata=True")_, _[MemoryPoolmemory\_pool=None](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "lance.fragment.LanceFragment.to_table.MemoryPool memory_pool=None")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment.to_table "Link to this definition")\
\
Convert this Fragment into a Table.\
\
Use this convenience utility with care. This will serially materialize\
the Scan result in memory before creating the Table.\
\
Parameters:schema : Schema, optional\
\
Concrete schema to use for scanning.\
\
columns : list of str, default None\
\
The columns to project. This can be a list of column names to\
include (order and duplicates will be preserved), or a dictionary\
with {new\_column\_name: expression} values for more advanced\
projections.\
\
The list of columns or expressions may use the special fields\
\_\_batch\_index (the index of the batch within the fragment),\
\_\_fragment\_index (the index of the fragment within the dataset),\
\_\_last\_in\_fragment (whether the batch is last in fragment), and\
\_\_filename (the name of the source file or a description of the\
source fragment).\
\
The columns will be passed down to Datasets and corresponding data\
fragments to avoid loading, copying, and deserializing columns\
that will not be required further down the compute chain.\
By default all of the available columns are projected. Raises\
an exception if any of the referenced column names does not exist\
in the dataset’s Schema.\
\
filter : Expression, default None\
\
Scan will return only the rows matching the filter.\
If possible the predicate will be pushed down to exploit the\
partition information or internal metadata found in the data\
source, e.g. Parquet statistics. Otherwise filters the loaded\
RecordBatches before yielding them.\
\
batch\_size : int, default 131\_072\
\
The maximum row count for scanned record batches. If scanned\
record batches are overflowing memory then this method can be\
called to reduce their size.\
\
batch\_readahead : int, default 16\
\
The number of batches to read ahead in a file. This might not work\
for all file formats. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_readahead : int, default 4\
\
The number of files to read ahead. Increasing this number will increase\
RAM usage but could also improve IO utilization.\
\
fragment\_scan\_options : FragmentScanOptions, default None\
\
Options specific to a particular scan and fragment type, which\
can change between different scans of the same dataset.\
\
use\_threads : bool, default True\
\
If enabled, then maximum parallelism will be used determined by\
the number of available CPU cores.\
\
cache\_metadata : bool, default True\
\
If enabled, metadata may be cached when scanning to speed up\
repeated scans.\
\
memory\_pool : MemoryPool, default None\
\
For memory allocations, if required. If not specified, uses the\
default pool.\
\
Returns:\
\
**table**\
\
Return type:\
\
Table\
\
_class_ lance.fragment.RowIdMeta [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta "Link to this definition")asdict() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta.asdict "Link to this definition")_static_ from\_json(_[json](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta.from_json "lance.fragment.RowIdMeta.from_json.json")_) [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta.from_json "Link to this definition")json() [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.RowIdMeta.json "Link to this definition")lance.fragment.write\_fragments(_[data](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.data "lance.fragment.write_fragments.data — The data to be written to the fragment."):ReaderLike_, _[dataset\_uri](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.dataset_uri "lance.fragment.write_fragments.dataset_uri — The URI of the dataset or the dataset object."):str\|Path\| [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.schema "lance.fragment.write_fragments.schema — The schema of the data."):[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") \|None= `None`_, _\*_, _[return\_transaction](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.return_transaction "lance.fragment.write_fragments.return_transaction — If it's true, the transaction will be returned."):True_, _[mode](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.mode "lance.fragment.write_fragments.mode — The write mode."):str= `'append'`_, _[max\_rows\_per\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_rows_per_file "lance.fragment.write_fragments.max_rows_per_file — The maximum number of rows per data file."):int= `1024 * 1024`_, _[max\_rows\_per\_group](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_rows_per_group "lance.fragment.write_fragments.max_rows_per_group — The maximum number of rows per group in the data file."):int= `1024`_, _[max\_bytes\_per\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_bytes_per_file "lance.fragment.write_fragments.max_bytes_per_file — The max number of bytes to write before starting a new file."):int= `DEFAULT_MAX_BYTES_PER_FILE`_, _[progress](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.progress "lance.fragment.write_fragments.progress — Experimental API."):FragmentWriteProgress\|None= `None`_, _[data\_storage\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.data_storage_version "lance.fragment.write_fragments.data_storage_version — The version of the data storage format to use."):str\|None= `None`_, _[use\_legacy\_format](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.use_legacy_format "lance.fragment.write_fragments.use_legacy_format — Deprecated method for setting the data storage version."):bool\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.storage_options "lance.fragment.write_fragments.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[enable\_move\_stable\_row\_ids](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.enable_move_stable_row_ids "lance.fragment.write_fragments.enable_move_stable_row_ids — Experimental: if set to true, the writer will use move-stable row ids. These row ids are stable after compaction operations, but not after updates. This makes compaction more efficient, since with stable row ids no secondary indices need to be updated to point to new row ids."):bool= `False`_)→[Transaction](https://lancedb.github.io/lance/api/python/Transaction.html "lance.Transaction — Initialize self.  See help(type(self)) for accurate signature.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments "Link to this definition")lance.fragment.write\_fragments(_[data](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.data "lance.fragment.write_fragments.data — The data to be written to the fragment."):ReaderLike_, _[dataset\_uri](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.dataset_uri "lance.fragment.write_fragments.dataset_uri — The URI of the dataset or the dataset object."):str\|Path\| [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")_, _[schema](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.schema "lance.fragment.write_fragments.schema — The schema of the data."):[Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") \|None= `None`_, _\*_, _[return\_transaction](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.return_transaction "lance.fragment.write_fragments.return_transaction — If it's true, the transaction will be returned."):False= `False`_, _[mode](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.mode "lance.fragment.write_fragments.mode — The write mode."):str= `'append'`_, _[max\_rows\_per\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_rows_per_file "lance.fragment.write_fragments.max_rows_per_file — The maximum number of rows per data file."):int= `1024 * 1024`_, _[max\_rows\_per\_group](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_rows_per_group "lance.fragment.write_fragments.max_rows_per_group — The maximum number of rows per group in the data file."):int= `1024`_, _[max\_bytes\_per\_file](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_bytes_per_file "lance.fragment.write_fragments.max_bytes_per_file — The max number of bytes to write before starting a new file."):int= `DEFAULT_MAX_BYTES_PER_FILE`_, _[progress](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.progress "lance.fragment.write_fragments.progress — Experimental API."):FragmentWriteProgress\|None= `None`_, _[data\_storage\_version](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.data_storage_version "lance.fragment.write_fragments.data_storage_version — The version of the data storage format to use."):str\|None= `None`_, _[use\_legacy\_format](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.use_legacy_format "lance.fragment.write_fragments.use_legacy_format — Deprecated method for setting the data storage version."):bool\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.storage_options "lance.fragment.write_fragments.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[enable\_move\_stable\_row\_ids](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.enable_move_stable_row_ids "lance.fragment.write_fragments.enable_move_stable_row_ids — Experimental: if set to true, the writer will use move-stable row ids. These row ids are stable after compaction operations, but not after updates. This makes compaction more efficient, since with stable row ids no secondary indices need to be updated to point to new row ids."):bool= `False`_)→list\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\]\
\
Write data into one or more fragments.\
\
Warning\
\
This is a low-level API intended for manually implementing distributed\
writes. For most users, [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") is the recommended API.\
\
Parameters:data : pa.Table or pa.RecordBatchReader [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.data "Permalink to this definition")\
\
The data to be written to the fragment.\
\
dataset\_uri : str, Path, or [LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.") [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.dataset_uri "Permalink to this definition")\
\
The URI of the dataset or the dataset object.\
\
schema : pa.Schema, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.schema "Permalink to this definition")\
\
The schema of the data. If not specified, the schema will be inferred\
from the data.\
\
return\_transaction : bool, default False [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.return_transaction "Permalink to this definition")\
\
If it’s true, the transaction will be returned.\
\
mode : str, default "append" [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.mode "Permalink to this definition")\
\
The write mode. If “append” is specified, the data will be checked\
against the existing dataset’s schema. Otherwise, pass “create” or\
“overwrite” to assign new field ids to the schema.\
\
max\_rows\_per\_file : int, default 1024 \* 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_rows_per_file "Permalink to this definition")\
\
The maximum number of rows per data file.\
\
max\_rows\_per\_group : int, default 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_rows_per_group "Permalink to this definition")\
\
The maximum number of rows per group in the data file.\
\
max\_bytes\_per\_file : int, default 90 \* 1024 \* 1024 \* 1024 [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.max_bytes_per_file "Permalink to this definition")\
\
The max number of bytes to write before starting a new file. This is a\
soft limit. This limit is checked after each group is written, which\
means larger groups may cause this to be overshot meaningfully. This\
defaults to 90 GB, since we have a hard limit of 100 GB per file on\
object stores.\
\
progress : FragmentWriteProgress, optional [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.progress "Permalink to this definition")\
\
_Experimental API_. Progress tracking for writing the fragment. Pass\
a custom class that defines hooks to be called when each fragment is\
starting to write and finishing writing.\
\
data\_storage\_version : optional, str, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.data_storage_version "Permalink to this definition")\
\
The version of the data storage format to use. Newer versions are more\
efficient but require newer versions of lance to read. The default (None)\
will use the 2.0 version. See the user guide for more details.\
\
use\_legacy\_format : optional, bool, default None [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.use_legacy_format "Permalink to this definition")\
\
Deprecated method for setting the data storage version. Use the\
data\_storage\_version parameter instead.\
\
storage\_options : Optional\[Dict\[str, str\]\] [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.storage_options "Permalink to this definition")\
\
Extra options that make sense for a particular storage connection. This is\
used to store connection parameters like credentials, endpoint, etc.\
\
enable\_move\_stable\_row\_ids : bool [¶](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.write_fragments.enable_move_stable_row_ids "Permalink to this definition")\
\
Experimental: if set to true, the writer will use move-stable row ids.\
These row ids are stable after compaction operations, but not after updates.\
This makes compaction more efficient, since with stable row ids no\
secondary indices need to be updated to point to new row ids.\
\
Returns:\
\
If return\_transaction is False:\
\
a list of [`FragmentMetadata`](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.") for the fragments written. The\
fragment ids are left as zero meaning they are not yet specified. They\
will be assigned when the fragments are committed to a dataset.\
\
If return\_transaction is True:\
\
The write transaction. The type of transaction will correspond to\
the mode parameter specified. This transaction can be passed to\
`LanceDataset.commit()`.\
\
Return type:\
\
List\[ [FragmentMetadata](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.FragmentMetadata "lance.fragment.FragmentMetadata — Metadata for a fragment.")\] \| [Transaction](https://lancedb.github.io/lance/api/python/Transaction.html "lance.Transaction — Initialize self.  See help(type(self)) for accurate signature.")