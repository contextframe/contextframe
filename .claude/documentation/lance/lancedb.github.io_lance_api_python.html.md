---
url: "https://lancedb.github.io/lance/api/python.html"
title: "Python APIs - Lance  documentation"
---

[Skip to content](https://lancedb.github.io/lance/api/python.html#lance-dataset)

# Python APIs [¶](https://lancedb.github.io/lance/api/python.html\#python-apis "Link to this heading")

`Lance` is a columnar format that is specifically designed for efficient
multi-modal data processing.

## Lance Dataset [¶](https://lancedb.github.io/lance/api/python.html\#lance-dataset "Link to this heading")

The core of Lance is the `LanceDataset` class. User can open a dataset by using
[`lance.dataset()`](https://lancedb.github.io/lance/api/python/dataset.html "lance.dataset — Opens the Lance dataset from the address specified.").

lance.dataset(_[uri](https://lancedb.github.io/lance/api/python/dataset.html#p-uri "lance.dataset.uri — Address to the Lance dataset."):str\|Path_, _[version](https://lancedb.github.io/lance/api/python/dataset.html#p-version "lance.dataset.version — If specified, load a specific version of the Lance dataset."):int\|str\|None= `None`_, _[asof](https://lancedb.github.io/lance/api/python/dataset.html#p-asof "lance.dataset.asof — If specified, find the latest version created on or earlier than the given argument value."):ts\_types\|None= `None`_, _[block\_size](https://lancedb.github.io/lance/api/python/dataset.html#p-block_size "lance.dataset.block_size — Block size in bytes."):int\|None= `None`_, _[commit\_lock](https://lancedb.github.io/lance/api/python/dataset.html#p-commit_lock "lance.dataset.commit_lock — A custom commit lock."):CommitLock\|None= `None`_, _[index\_cache\_size](https://lancedb.github.io/lance/api/python/dataset.html#p-index_cache_size "lance.dataset.index_cache_size — Index cache size."):int\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python/dataset.html#p-storage_options "lance.dataset.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[default\_scan\_options](https://lancedb.github.io/lance/api/python/dataset.html#p-default_scan_options "lance.dataset.default_scan_options — Default scan options that are used when scanning the dataset."):dict\[str,str\]\|None= `None`_)→[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")

Opens the Lance dataset from the address specified.

Parameters:uri : str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.uri "Permalink to this definition")

Address to the Lance dataset. It can be a local file path /tmp/data.lance,
or a cloud object store URI, i.e., s3://bucket/data.lance.

version : optional, int \| str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.version "Permalink to this definition")

If specified, load a specific version of the Lance dataset. Else, loads the
latest version. A version number (int) or a tag (str) can be provided.

asof : optional, datetime or str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.asof "Permalink to this definition")

If specified, find the latest version created on or earlier than the given
argument value. If a version is already specified, this arg is ignored.

block\_size : optional, int [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.block_size "Permalink to this definition")

Block size in bytes. Provide a hint for the size of the minimal I/O request.

commit\_lock : optional, lance.commit.CommitLock [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.commit_lock "Permalink to this definition")

A custom commit lock. Only needed if your object store does not support
atomic commits. See the user guide for more details.

index\_cache\_size : optional, int [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.index_cache_size "Permalink to this definition")

Index cache size. Index cache is a LRU cache with TTL. This number specifies the
number of index pages, for example, IVF partitions, to be cached in
the host memory. Default value is `256`.

Roughly, for an `IVF_PQ` partition with `n` rows, the size of each index
page equals the combination of the pq code ( `nd.array([n,pq], dtype=uint8))`
and the row ids ( `nd.array([n], dtype=uint64)`).
Approximately, `n = Total Rows / number of IVF partitions`.
`pq = number of PQ sub-vectors`.

storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.storage_options "Permalink to this definition")

Extra options that make sense for a particular storage connection. This is
used to store connection parameters like credentials, endpoint, etc.

default\_scan\_options : optional, dict [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.default_scan_options "Permalink to this definition")

Default scan options that are used when scanning the dataset. This accepts
the same arguments described in [`lance.LanceDataset.scanner()`](https://lancedb.github.io/lance/api/python/LanceDataset.scanner.html "lance.LanceDataset.scanner — Return a Scanner that can support various pushdowns."). The
arguments will be applied to any scan operation.

This can be useful to supply defaults for common parameters such as
`batch_size`.

It can also be used to create a view of the dataset that includes meta
fields such as `_rowid` or `_rowaddr`. If `default_scan_options` is
provided then the schema returned by [`lance.LanceDataset.schema()`](https://lancedb.github.io/lance/api/python/LanceDataset.schema.html "lance.LanceDataset.schema — The pyarrow Schema for this dataset") will
include these fields if the appropriate scan options are set.

### Basic IOs [¶](https://lancedb.github.io/lance/api/python.html\#basic-ios "Link to this heading")

The following functions are used to read and write data in Lance format.

LanceDataset.insert(_[data](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.insert.data"):ReaderLike_, _\*_, _[mode](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.insert.mode "lance.dataset.LanceDataset.insert.mode — create - create a new dataset (raises if uri already exists). overwrite - create a new snapshot version append - create a new version that is the concat of the input the latest version (raises if uri does not exist)") = `'append'`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.insert.kwargs "lance.dataset.LanceDataset.insert.kwargs — Additional keyword arguments to pass to write_dataset().")_)

Insert data into the dataset.

Parameters:data\_obj : Reader-like

The data to be written. Acceptable types are:
\- Pandas DataFrame, Pyarrow Table, Dataset, Scanner, or RecordBatchReader
\- Huggingface dataset

mode : str, default 'append' [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.insert.mode "Permalink to this definition")

The mode to use when writing the data. Options are:

**create** \- create a new dataset (raises if uri already exists).
**overwrite** \- create a new snapshot version
**append** \- create a new version that is the concat of the input the
latest version (raises if uri does not exist)

\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.insert.kwargs "Permalink to this definition")

Additional keyword arguments to pass to [`write_dataset()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.write_dataset "lance.dataset.write_dataset — Write a given data_obj to the given uri").

LanceDataset.scanner(_[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.columns "lance.dataset.LanceDataset.scanner.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.filter "lance.dataset.LanceDataset.scanner.filter — Duplicate explicit target name: \"lance filter pushdown\"."):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.limit "lance.dataset.LanceDataset.scanner.limit — Fetch up to this many rows."):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.offset "lance.dataset.LanceDataset.scanner.offset — Fetch starting with this row."):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.nearest "lance.dataset.LanceDataset.scanner.nearest — Get the rows corresponding to the K most similar vectors."):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_size "lance.dataset.LanceDataset.scanner.batch_size — The target size of batches returned."):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_readahead "lance.dataset.LanceDataset.scanner.batch_readahead — The number of batches to read ahead."):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragment_readahead "lance.dataset.LanceDataset.scanner.fragment_readahead — The number of fragments to read ahead."):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_in_order "lance.dataset.LanceDataset.scanner.scan_in_order — Whether to read the fragments and batches in order."):bool\|None= `None`_, _[fragments](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragments "lance.dataset.LanceDataset.scanner.fragments — If specified, only scan these fragments."):Iterable\[ [LanceFragment](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment — Count rows matching the scanner filter.")\]\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.full_text_query "lance.dataset.LanceDataset.scanner.full_text_query — query string to search for, the results will be ranked by BM25. e.g."):str\|dict\|FullTextQuery\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.prefilter "lance.dataset.LanceDataset.scanner.prefilter — If True then the filter will be applied before the vector query is run. This will generate more correct results but it may be a more costly query."):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.scanner.with_row_id"):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.scanner.with_row_address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.scanner.use_stats"):bool\|None= `None`_, _[fast\_search](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fast_search "lance.dataset.LanceDataset.scanner.fast_search — If True, then the search will only be performed on the indexed data, which yields faster search time."):bool\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.io_buffer_size "lance.dataset.LanceDataset.scanner.io_buffer_size — The size of the IO buffer."):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.late_materialization "lance.dataset.LanceDataset.scanner.late_materialization — Allows custom control over late materialization."):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.use_scalar_index "lance.dataset.LanceDataset.scanner.use_scalar_index — Lance will automatically use scalar indices to optimize a query."):bool\|None= `None`_, _[include\_deleted\_rows](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.include_deleted_rows "lance.dataset.LanceDataset.scanner.include_deleted_rows — If True, then rows that have been deleted, but are still present in the fragment, will be returned."):bool\|None= `None`_, _[scan\_stats\_callback](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_stats_callback "lance.dataset.LanceDataset.scanner.scan_stats_callback — A callback function that will be called with the scan statistics after the scan is complete."):Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics "_lib.ScanStatistics")\],None\]\|None= `None`_, _[strict\_batch\_size](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.scanner.strict_batch_size"):bool\|None= `None`_)→[LanceScanner](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner "lance.dataset.LanceScanner — Execute the plan for this scanner and display with runtime metrics.")

Return a Scanner that can support various pushdowns.

Parameters:columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.columns "Permalink to this definition")

List of column names to be fetched.
Or a dictionary of column names to SQL expressions.
All columns are fetched if None or unspecified.

filter : pa.compute.Expression or str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.filter "Permalink to this definition")

Expression or str that is a valid SQL where clause. See
[Lance filter pushdown](https://lancedb.github.io/lance/introduction/read_and_write.html#filter-push-down)
for valid SQL expressions.

limit : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.limit "Permalink to this definition")

Fetch up to this many rows. All rows if None or unspecified.

offset : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.offset "Permalink to this definition")

Fetch starting with this row. 0 if None or unspecified.

nearest : dict, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.nearest "Permalink to this definition")

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

batch\_size : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_size "Permalink to this definition")

The target size of batches returned. In some cases batches can be up to
twice this size (but never larger than this). In some cases batches can
be smaller than this size.

io\_buffer\_size : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.io_buffer_size "Permalink to this definition")

The size of the IO buffer. See `ScannerBuilder.io_buffer_size`
for more information.

batch\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_readahead "Permalink to this definition")

The number of batches to read ahead.

fragment\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragment_readahead "Permalink to this definition")

The number of fragments to read ahead.

scan\_in\_order : bool, default True [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_in_order "Permalink to this definition")

Whether to read the fragments and batches in order. If false,
throughput may be higher, but batches will be returned out of order
and memory use might increase.

fragments : iterable of [LanceFragment](https://lancedb.github.io/lance/api/python/LanceFragment.html "lance.LanceFragment — Initialize self.  See help(type(self)) for accurate signature."), default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragments "Permalink to this definition")

If specified, only scan these fragments. If scan\_in\_order is True, then
the fragments will be scanned in the order given.

prefilter : bool, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.prefilter "Permalink to this definition")

If True then the filter will be applied before the vector query is run.
This will generate more correct results but it may be a more costly
query. It’s generally good when the filter is highly selective.

If False then the filter will be applied after the vector query is run.
This will perform well but the results may have fewer than the requested
number of rows (or be empty) if the rows closest to the query do not
match the filter. It’s generally good when the filter is not very
selective.

use\_scalar\_index : bool, default True [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.use_scalar_index "Permalink to this definition")

Lance will automatically use scalar indices to optimize a query. In some
corner cases this can make query performance worse and this parameter can
be used to disable scalar indices in these cases.

late\_materialization : bool or List\[str\], default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.late_materialization "Permalink to this definition")

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

full\_text\_query : str or dict, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.full_text_query "Permalink to this definition")

query string to search for, the results will be ranked by BM25.
e.g. “hello world”, would match documents containing “hello” or “world”.
or a dictionary with the following keys:

- columns: list\[str\]

The columns to search,
currently only supports a single column in the columns list.

- query: str

The query string to search for.


fast\_search : bool, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fast_search "Permalink to this definition")

If True, then the search will only be performed on the indexed data, which
yields faster search time.

scan\_stats\_callback : Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/python/ScanStatistics.html "lance.ScanStatistics — Statistics about the scan.")\], None\], default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_stats_callback "Permalink to this definition")

A callback function that will be called with the scan statistics after the
scan is complete. Errors raised by the callback will be logged but not
re-raised.

include\_deleted\_rows : bool, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.include_deleted_rows "Permalink to this definition")

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

LanceDataset.to\_batches(_[columns](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.columns"):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.filter"):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.limit"):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.offset"):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.nearest"):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.batch_size"):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.batch_readahead"):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.fragment_readahead"):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.scan_in_order"):bool\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.prefilter"):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.with_row_id"):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.with_row_address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.use_stats"):bool\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.full_text_query"):str\|dict\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.io_buffer_size"):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.late_materialization"):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.use_scalar_index"):bool\|None= `None`_, _[strict\_batch\_size](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.to_batches.strict_batch_size"):bool\|None= `None`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_batches.kwargs "lance.dataset.LanceDataset.to_batches.kwargs — Arguments for scanner().")_)→Iterator\[ [RecordBatch](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html#pyarrow.RecordBatch "(in Apache Arrow v20.0.0)")\]

Read the dataset as materialized record batches.

Parameters:\*\*kwargs : dict, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_batches.kwargs "Permalink to this definition")

Arguments for [`scanner()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.scanner "lance.dataset.LanceDataset.scanner — Return a Scanner that can support various pushdowns.").

Returns:

**record\_batches**

Return type:

Iterator of [`RecordBatch`](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html#pyarrow.RecordBatch "(in Apache Arrow v20.0.0)")

LanceDataset.to\_table(_[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.columns "lance.dataset.LanceDataset.to_table.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.filter "lance.dataset.LanceDataset.to_table.filter — Duplicate explicit target name: \"lance filter pushdown\"."):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.limit "lance.dataset.LanceDataset.to_table.limit — Fetch up to this many rows."):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.offset "lance.dataset.LanceDataset.to_table.offset — Fetch starting with this row."):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.nearest "lance.dataset.LanceDataset.to_table.nearest — Get the rows corresponding to the K most similar vectors."):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.batch_size "lance.dataset.LanceDataset.to_table.batch_size — The number of rows to read at a time."):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.batch_readahead "lance.dataset.LanceDataset.to_table.batch_readahead — The number of batches to read ahead."):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.fragment_readahead "lance.dataset.LanceDataset.to_table.fragment_readahead — The number of fragments to read ahead."):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.scan_in_order "lance.dataset.LanceDataset.to_table.scan_in_order — Whether to read the fragments and batches in order."):bool\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.prefilter "lance.dataset.LanceDataset.to_table.prefilter — Run filter before the vector search."):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.with_row_id "lance.dataset.LanceDataset.to_table.with_row_id — Return row ID."):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.with_row_address "lance.dataset.LanceDataset.to_table.with_row_address — Return row address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.use_stats "lance.dataset.LanceDataset.to_table.use_stats — Use stats pushdown during filters."):bool\|None= `None`_, _[fast\_search](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.fast_search "lance.dataset.LanceDataset.to_table.fast_search"):bool\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.full_text_query "lance.dataset.LanceDataset.to_table.full_text_query — query string to search for, the results will be ranked by BM25. e.g."):str\|dict\|FullTextQuery\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.io_buffer_size "lance.dataset.LanceDataset.to_table.io_buffer_size — The size of the IO buffer."):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.late_materialization "lance.dataset.LanceDataset.to_table.late_materialization — Allows custom control over late materialization."):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.use_scalar_index "lance.dataset.LanceDataset.to_table.use_scalar_index — Allows custom control over scalar index usage."):bool\|None= `None`_, _[include\_deleted\_rows](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.include_deleted_rows "lance.dataset.LanceDataset.to_table.include_deleted_rows — If True, then rows that have been deleted, but are still present in the fragment, will be returned."):bool\|None= `None`_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)")

Read the data into memory as a [`pyarrow.Table`](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)")

Parameters:columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.columns "Permalink to this definition")

List of column names to be fetched.
Or a dictionary of column names to SQL expressions.
All columns are fetched if None or unspecified.

filter : pa.compute.Expression or str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.filter "Permalink to this definition")

Expression or str that is a valid SQL where clause. See
[Lance filter pushdown](https://lancedb.github.io/lance/introduction/read_and_write.html#filter-push-down)
for valid SQL expressions.

limit : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.limit "Permalink to this definition")

Fetch up to this many rows. All rows if None or unspecified.

offset : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.offset "Permalink to this definition")

Fetch starting with this row. 0 if None or unspecified.

nearest : dict, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.nearest "Permalink to this definition")

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

batch\_size : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.batch_size "Permalink to this definition")

The number of rows to read at a time.

io\_buffer\_size : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.io_buffer_size "Permalink to this definition")

The size of the IO buffer. See `ScannerBuilder.io_buffer_size`
for more information.

batch\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.batch_readahead "Permalink to this definition")

The number of batches to read ahead.

fragment\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.fragment_readahead "Permalink to this definition")

The number of fragments to read ahead.

scan\_in\_order : bool, optional, default True [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.scan_in_order "Permalink to this definition")

Whether to read the fragments and batches in order. If false,
throughput may be higher, but batches will be returned out of order
and memory use might increase.

prefilter : bool, optional, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.prefilter "Permalink to this definition")

Run filter before the vector search.

late\_materialization : bool or List\[str\], default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.late_materialization "Permalink to this definition")

Allows custom control over late materialization. See
`ScannerBuilder.late_materialization` for more information.

use\_scalar\_index : bool, default True [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.use_scalar_index "Permalink to this definition")

Allows custom control over scalar index usage. See
`ScannerBuilder.use_scalar_index` for more information.

with\_row\_id : bool, optional, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.with_row_id "Permalink to this definition")

Return row ID.

with\_row\_address : bool, optional, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.with_row_address "Permalink to this definition")

Return row address

use\_stats : bool, optional, default True [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.use_stats "Permalink to this definition")

Use stats pushdown during filters.

fast\_search : bool, optional, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.fast_search "Permalink to this definition")

full\_text\_query : str or dict, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.full_text_query "Permalink to this definition")

query string to search for, the results will be ranked by BM25.
e.g. “hello world”, would match documents contains “hello” or “world”.
or a dictionary with the following keys:

- columns: list\[str\]

The columns to search,
currently only supports a single column in the columns list.

- query: str

The query string to search for.


include\_deleted\_rows : bool, optional, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.to_table.include_deleted_rows "Permalink to this definition")

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


### Random Access [¶](https://lancedb.github.io/lance/api/python.html\#random-access "Link to this heading")

Lance stands out with its super fast random access, unlike other columnar formats.

LanceDataset.take(_[indices](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.take.indices "lance.dataset.LanceDataset.take.indices — indices of rows to select in the dataset."):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)")_, _[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.take.columns "lance.dataset.LanceDataset.take.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_)→[Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)")

Select rows of data by index.

Parameters:indices : Array or array-like [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.take.indices "Permalink to this definition")

indices of rows to select in the dataset.

columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.take.columns "Permalink to this definition")

List of column names to be fetched.
Or a dictionary of column names to SQL expressions.
All columns are fetched if None or unspecified.

Returns:

**table**

Return type:

[pyarrow.Table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)")

LanceDataset.take\_blobs(_[blob\_column](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.take_blobs.blob_column"):str_, _[ids](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.take_blobs.ids"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_, _[addresses](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.take_blobs.addresses"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_, _[indices](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.take_blobs.indices"):list\[int\]\| [Array](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html#pyarrow.Array "(in Apache Arrow v20.0.0)") \|None= `None`_)→list\[ [BlobFile](https://lancedb.github.io/lance/api/py_modules.html#lance.BlobFile "lance.blob.BlobFile")\]

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

### Schema Evolution [¶](https://lancedb.github.io/lance/api/python.html\#schema-evolution "Link to this heading")

Lance supports schema evolution, which means that you can add new columns to the dataset
cheaply.

LanceDataset.add\_columns(_[transforms](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.transforms "lance.dataset.LanceDataset.add_columns.transforms — If this is a dictionary, then the keys are the names of the new columns and the values are SQL expression strings."):dict\[str,str\]\|BatchUDF\|ReaderLike\| [pyarrow.Field](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)") \|list\[ [pyarrow.Field](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)")\]\| [pyarrow.Schema](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)")_, _[read\_columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.read_columns "lance.dataset.LanceDataset.add_columns.read_columns — The names of the columns that the UDF will read."):list\[str\]\|None= `None`_, _[reader\_schema](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.reader_schema "lance.dataset.LanceDataset.add_columns.reader_schema — Only valid if transforms is a ReaderLike object."):pa.Schema\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.batch_size "lance.dataset.LanceDataset.add_columns.batch_size — The number of rows to read at a time from the source dataset when applying the transform."):int\|None= `None`_)

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

Parameters:transforms : dict or AddColumnsUDF or ReaderLike [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.transforms "Permalink to this definition")

If this is a dictionary, then the keys are the names of the new
columns and the values are SQL expression strings. These strings can
reference existing columns in the dataset.
If this is a AddColumnsUDF, then it is a UDF that takes a batch of
existing data and returns a new batch with the new columns.
If this is [`pyarrow.Field`](https://arrow.apache.org/docs/python/generated/pyarrow.Field.html#pyarrow.Field "(in Apache Arrow v20.0.0)") or [`pyarrow.Schema`](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)"), it adds
all NULL columns with the given schema, in a metadata-only operation.

read\_columns : list of str, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.read_columns "Permalink to this definition")

The names of the columns that the UDF will read. If None, then the
UDF will read all columns. This is only used when transforms is a
UDF. Otherwise, the read columns are inferred from the SQL expressions.

reader\_schema : pa.Schema, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.reader_schema "Permalink to this definition")

Only valid if transforms is a ReaderLike object. This will be used to
determine the schema of the reader.

batch\_size : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.add_columns.batch_size "Permalink to this definition")

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

[`LanceDataset.merge`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.merge "lance.dataset.LanceDataset.merge — Merge another dataset into this one.")

Merge a pre-computed set of columns into the dataset.

LanceDataset.drop\_columns(_[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.drop_columns.columns "lance.dataset.LanceDataset.drop_columns.columns — The names of the columns to drop."):list\[str\]_)

Drop one or more columns from the dataset

This is a metadata-only operation and does not remove the data from the
underlying storage. In order to remove the data, you must subsequently
call `compact_files` to rewrite the data without the removed columns and
then call `cleanup_old_versions` to remove the old files.

Parameters:columns : list of str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.drop_columns.columns "Permalink to this definition")

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

### Indexing and Searching [¶](https://lancedb.github.io/lance/api/python.html\#indexing-and-searching "Link to this heading")

LanceDataset.create\_index(_[column](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.column "lance.dataset.LanceDataset.create_index.column — The column to be indexed."):str\|list\[str\]_, _[index\_type](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.index_type "lance.dataset.LanceDataset.create_index.index_type — The type of the index. \"IVF_PQ, IVF_HNSW_PQ and IVF_HNSW_SQ\" are supported now."):str_, _[name](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.name "lance.dataset.LanceDataset.create_index.name — The index name."):str\|None= `None`_, _[metric](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.metric "lance.dataset.LanceDataset.create_index.metric — The distance metric type, i.e., \"L2\" (alias to \"euclidean\"), \"cosine\" or \"dot\" (dot product)."):str= `'L2'`_, _[replace](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.replace "lance.dataset.LanceDataset.create_index.replace — Replace the existing index if it exists."):bool= `False`_, _[num\_partitions](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.num_partitions "lance.dataset.LanceDataset.create_index.num_partitions — The number of partitions of IVF (Inverted File Index)."):int\|None= `None`_, _[ivf\_centroids](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.ivf_centroids "lance.dataset.LanceDataset.create_index.ivf_centroids — It can be either np.ndarray, pyarrow.FixedSizeListArray or pyarrow.FixedShapeTensorArray. A num_partitions x dimension array of existing K-mean centroids for IVF clustering."):np.ndarray\|pa.FixedSizeListArray\|pa.FixedShapeTensorArray\|None= `None`_, _[pq\_codebook](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.pq_codebook "lance.dataset.LanceDataset.create_index.pq_codebook — It can be np.ndarray, pyarrow.FixedSizeListArray, or pyarrow.FixedShapeTensorArray. A num_sub_vectors x (2 ^ nbits * dimensions // num_sub_vectors) array of K-mean centroids for PQ codebook."):np.ndarray\|pa.FixedSizeListArray\|pa.FixedShapeTensorArray\|None= `None`_, _[num\_sub\_vectors](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.num_sub_vectors "lance.dataset.LanceDataset.create_index.num_sub_vectors — The number of sub-vectors for PQ (Product Quantization)."):int\|None= `None`_, _[accelerator](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.accelerator "lance.dataset.LanceDataset.create_index.accelerator — If set, use an accelerator to speed up the training process. Accepted accelerator: \"cuda\" (Nvidia GPU) and \"mps\" (Apple Silicon GPU). If not set, use the CPU."):str\|'torch.Device'\|None= `None`_, _[index\_cache\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.index_cache_size "lance.dataset.LanceDataset.create_index.index_cache_size — The size of the index cache in number of entries."):int\|None= `None`_, _[shuffle\_partition\_batches](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.shuffle_partition_batches "lance.dataset.LanceDataset.create_index.shuffle_partition_batches — The number of batches, using the row group size of the dataset, to include in each shuffle partition."):int\|None= `None`_, _[shuffle\_partition\_concurrency](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.shuffle_partition_concurrency "lance.dataset.LanceDataset.create_index.shuffle_partition_concurrency — The number of shuffle partitions to process concurrently."):int\|None= `None`_, _[ivf\_centroids\_file](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.create_index.ivf_centroids_file"):str\|None= `None`_, _[precomputed\_partition\_dataset](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.create_index.precomputed_partition_dataset"):str\|None= `None`_, _[storage\_options](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.storage_options "lance.dataset.LanceDataset.create_index.storage_options — Extra options that make sense for a particular storage connection."):dict\[str,str\]\|None= `None`_, _[filter\_nan](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.filter_nan "lance.dataset.LanceDataset.create_index.filter_nan — Defaults to True."):bool= `True`_, _[one\_pass\_ivfpq](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.one_pass_ivfpq "lance.dataset.LanceDataset.create_index.one_pass_ivfpq — Defaults to False."):bool= `False`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.kwargs "lance.dataset.LanceDataset.create_index.kwargs — Parameters passed to the index building process.")_)→[LanceDataset](https://lancedb.github.io/lance/api/python/LanceDataset.html "lance.LanceDataset — A Lance Dataset in Lance format where the data is stored at the given uri.")

Create index on column.

**Experimental API**

Parameters:column : str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.column "Permalink to this definition")

The column to be indexed.

index\_type : str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.index_type "Permalink to this definition")

The type of the index.
`"IVF_PQ, IVF_HNSW_PQ and IVF_HNSW_SQ"` are supported now.

name : str, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.name "Permalink to this definition")

The index name. If not provided, it will be generated from the
column name.

metric : str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.metric "Permalink to this definition")

The distance metric type, i.e., “L2” (alias to “euclidean”), “cosine”
or “dot” (dot product). Default is “L2”.

replace : bool [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.replace "Permalink to this definition")

Replace the existing index if it exists.

num\_partitions : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.num_partitions "Permalink to this definition")

The number of partitions of IVF (Inverted File Index).

ivf\_centroids : optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.ivf_centroids "Permalink to this definition")

It can be either `np.ndarray`,
[`pyarrow.FixedSizeListArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedSizeListArray.html#pyarrow.FixedSizeListArray "(in Apache Arrow v20.0.0)") or
[`pyarrow.FixedShapeTensorArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedShapeTensorArray.html#pyarrow.FixedShapeTensorArray "(in Apache Arrow v20.0.0)").
A `num_partitions x dimension` array of existing K-mean centroids
for IVF clustering. If not provided, a new KMeans model will be trained.

pq\_codebook : optional, [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.pq_codebook "Permalink to this definition")

It can be `np.ndarray`, [`pyarrow.FixedSizeListArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedSizeListArray.html#pyarrow.FixedSizeListArray "(in Apache Arrow v20.0.0)"),
or [`pyarrow.FixedShapeTensorArray`](https://arrow.apache.org/docs/python/generated/pyarrow.FixedShapeTensorArray.html#pyarrow.FixedShapeTensorArray "(in Apache Arrow v20.0.0)").
A `num_sub_vectors x (2 ^ nbits * dimensions // num_sub_vectors)`
array of K-mean centroids for PQ codebook.

Note: `nbits` is always 8 for now.
If not provided, a new PQ model will be trained.

num\_sub\_vectors : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.num_sub_vectors "Permalink to this definition")

The number of sub-vectors for PQ (Product Quantization).

accelerator:str\|'torch.Device'\|None= `None` [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.accelerator "Permalink to this definition")

If set, use an accelerator to speed up the training process.
Accepted accelerator: “cuda” (Nvidia GPU) and “mps” (Apple Silicon GPU).
If not set, use the CPU.

index\_cache\_size : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.index_cache_size "Permalink to this definition")

The size of the index cache in number of entries. Default value is 256.

shuffle\_partition\_batches : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.shuffle_partition_batches "Permalink to this definition")

The number of batches, using the row group size of the dataset, to include
in each shuffle partition. Default value is 10240.

Assuming the row group size is 1024, each shuffle partition will hold
10240 \* 1024 = 10,485,760 rows. By making this value smaller, this shuffle
will consume less memory but will take longer to complete, and vice versa.

shuffle\_partition\_concurrency : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.shuffle_partition_concurrency "Permalink to this definition")

The number of shuffle partitions to process concurrently. Default value is 2

By making this value smaller, this shuffle will consume less memory but will
take longer to complete, and vice versa.

storage\_options : optional, dict [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.storage_options "Permalink to this definition")

Extra options that make sense for a particular storage connection. This is
used to store connection parameters like credentials, endpoint, etc.

filter\_nan : bool [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.filter_nan "Permalink to this definition")

Defaults to True. False is UNSAFE, and will cause a crash if any null/nan
values are present (and otherwise will not). Disables the null filter used
for nullable columns. Obtains a small speed boost.

one\_pass\_ivfpq : bool [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.one_pass_ivfpq "Permalink to this definition")

Defaults to False. If enabled, index type must be “IVF\_PQ”. Reduces disk IO.

\*\*kwargs [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_index.kwargs "Permalink to this definition")

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


LanceDataset.create\_scalar\_index(_[column](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.column "lance.dataset.LanceDataset.create_scalar_index.column — The column to be indexed."):str_, _[index\_type](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.index_type "lance.dataset.LanceDataset.create_scalar_index.index_type — The type of the index."):'BTREE'\|'BITMAP'\|'LABEL\_LIST'\|'INVERTED'\|'FTS'\|'NGRAM'_, _[name](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.name "lance.dataset.LanceDataset.create_scalar_index.name — The index name."):str\|None= `None`_, _\*_, _[replace](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.replace "lance.dataset.LanceDataset.create_scalar_index.replace — Replace the existing index if it exists."):bool= `True`_, _\*\* [kwargs](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.create_scalar_index.kwargs")_)

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

Parameters:column : str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.column "Permalink to this definition")

The column to be indexed. Must be a boolean, integer, float,
or string column.

index\_type : str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.index_type "Permalink to this definition")

The type of the index. One of `"BTREE"`, `"BITMAP"`,
`"LABEL_LIST"`, `"NGRAM"`, `"FTS"` or `"INVERTED"`.

name : str, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.name "Permalink to this definition")

The index name. If not provided, it will be generated from the
column name.

replace : bool, default True [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.create_scalar_index.replace "Permalink to this definition")

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

LanceDataset.drop\_index(_[name](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.drop_index.name"):str_)

Drops an index from the dataset

Note: Indices are dropped by “index name”. This is not the same as the field
name. If you did not specify a name when you created the index then a name was
generated for you. You can use the list\_indices method to get the names of
the indices.

LanceDataset.scanner(_[columns](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.columns "lance.dataset.LanceDataset.scanner.columns — List of column names to be fetched. Or a dictionary of column names to SQL expressions. All columns are fetched if None or unspecified."):list\[str\]\|dict\[str,str\]\|None= `None`_, _[filter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.filter "lance.dataset.LanceDataset.scanner.filter — Duplicate explicit target name: \"lance filter pushdown\"."):[Expression](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html#pyarrow.dataset.Expression "(in Apache Arrow v20.0.0)") \|str\|None= `None`_, _[limit](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.limit "lance.dataset.LanceDataset.scanner.limit — Fetch up to this many rows."):int\|None= `None`_, _[offset](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.offset "lance.dataset.LanceDataset.scanner.offset — Fetch starting with this row."):int\|None= `None`_, _[nearest](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.nearest "lance.dataset.LanceDataset.scanner.nearest — Get the rows corresponding to the K most similar vectors."):dict\|None= `None`_, _[batch\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_size "lance.dataset.LanceDataset.scanner.batch_size — The target size of batches returned."):int\|None= `None`_, _[batch\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_readahead "lance.dataset.LanceDataset.scanner.batch_readahead — The number of batches to read ahead."):int\|None= `None`_, _[fragment\_readahead](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragment_readahead "lance.dataset.LanceDataset.scanner.fragment_readahead — The number of fragments to read ahead."):int\|None= `None`_, _[scan\_in\_order](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_in_order "lance.dataset.LanceDataset.scanner.scan_in_order — Whether to read the fragments and batches in order."):bool\|None= `None`_, _[fragments](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragments "lance.dataset.LanceDataset.scanner.fragments — If specified, only scan these fragments."):Iterable\[ [LanceFragment](https://lancedb.github.io/lance/api/py_modules.html#lance.fragment.LanceFragment "lance.fragment.LanceFragment — Count rows matching the scanner filter.")\]\|None= `None`_, _[full\_text\_query](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.full_text_query "lance.dataset.LanceDataset.scanner.full_text_query — query string to search for, the results will be ranked by BM25. e.g."):str\|dict\|FullTextQuery\|None= `None`_, _\*_, _[prefilter](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.prefilter "lance.dataset.LanceDataset.scanner.prefilter — If True then the filter will be applied before the vector query is run. This will generate more correct results but it may be a more costly query."):bool\|None= `None`_, _[with\_row\_id](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.scanner.with_row_id"):bool\|None= `None`_, _[with\_row\_address](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.scanner.with_row_address"):bool\|None= `None`_, _[use\_stats](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.scanner.use_stats"):bool\|None= `None`_, _[fast\_search](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fast_search "lance.dataset.LanceDataset.scanner.fast_search — If True, then the search will only be performed on the indexed data, which yields faster search time."):bool\|None= `None`_, _[io\_buffer\_size](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.io_buffer_size "lance.dataset.LanceDataset.scanner.io_buffer_size — The size of the IO buffer."):int\|None= `None`_, _[late\_materialization](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.late_materialization "lance.dataset.LanceDataset.scanner.late_materialization — Allows custom control over late materialization."):bool\|list\[str\]\|None= `None`_, _[use\_scalar\_index](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.use_scalar_index "lance.dataset.LanceDataset.scanner.use_scalar_index — Lance will automatically use scalar indices to optimize a query."):bool\|None= `None`_, _[include\_deleted\_rows](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.include_deleted_rows "lance.dataset.LanceDataset.scanner.include_deleted_rows — If True, then rows that have been deleted, but are still present in the fragment, will be returned."):bool\|None= `None`_, _[scan\_stats\_callback](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_stats_callback "lance.dataset.LanceDataset.scanner.scan_stats_callback — A callback function that will be called with the scan statistics after the scan is complete."):Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/py_modules.html#lance.ScanStatistics "_lib.ScanStatistics")\],None\]\|None= `None`_, _[strict\_batch\_size](https://lancedb.github.io/lance/api/python.html# "lance.dataset.LanceDataset.scanner.strict_batch_size"):bool\|None= `None`_)→[LanceScanner](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceScanner "lance.dataset.LanceScanner — Execute the plan for this scanner and display with runtime metrics.")

Return a Scanner that can support various pushdowns.

Parameters:columns : list of str, or dict of str to str default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.columns "Permalink to this definition")

List of column names to be fetched.
Or a dictionary of column names to SQL expressions.
All columns are fetched if None or unspecified.

filter : pa.compute.Expression or str [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.filter "Permalink to this definition")

Expression or str that is a valid SQL where clause. See
[Lance filter pushdown](https://lancedb.github.io/lance/introduction/read_and_write.html#filter-push-down)
for valid SQL expressions.

limit : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.limit "Permalink to this definition")

Fetch up to this many rows. All rows if None or unspecified.

offset : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.offset "Permalink to this definition")

Fetch starting with this row. 0 if None or unspecified.

nearest : dict, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.nearest "Permalink to this definition")

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

batch\_size : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_size "Permalink to this definition")

The target size of batches returned. In some cases batches can be up to
twice this size (but never larger than this). In some cases batches can
be smaller than this size.

io\_buffer\_size : int, default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.io_buffer_size "Permalink to this definition")

The size of the IO buffer. See `ScannerBuilder.io_buffer_size`
for more information.

batch\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.batch_readahead "Permalink to this definition")

The number of batches to read ahead.

fragment\_readahead : int, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragment_readahead "Permalink to this definition")

The number of fragments to read ahead.

scan\_in\_order : bool, default True [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_in_order "Permalink to this definition")

Whether to read the fragments and batches in order. If false,
throughput may be higher, but batches will be returned out of order
and memory use might increase.

fragments : iterable of [LanceFragment](https://lancedb.github.io/lance/api/python/LanceFragment.html "lance.LanceFragment — Initialize self.  See help(type(self)) for accurate signature."), default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fragments "Permalink to this definition")

If specified, only scan these fragments. If scan\_in\_order is True, then
the fragments will be scanned in the order given.

prefilter : bool, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.prefilter "Permalink to this definition")

If True then the filter will be applied before the vector query is run.
This will generate more correct results but it may be a more costly
query. It’s generally good when the filter is highly selective.

If False then the filter will be applied after the vector query is run.
This will perform well but the results may have fewer than the requested
number of rows (or be empty) if the rows closest to the query do not
match the filter. It’s generally good when the filter is not very
selective.

use\_scalar\_index : bool, default True [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.use_scalar_index "Permalink to this definition")

Lance will automatically use scalar indices to optimize a query. In some
corner cases this can make query performance worse and this parameter can
be used to disable scalar indices in these cases.

late\_materialization : bool or List\[str\], default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.late_materialization "Permalink to this definition")

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

full\_text\_query : str or dict, optional [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.full_text_query "Permalink to this definition")

query string to search for, the results will be ranked by BM25.
e.g. “hello world”, would match documents containing “hello” or “world”.
or a dictionary with the following keys:

- columns: list\[str\]

The columns to search,
currently only supports a single column in the columns list.

- query: str

The query string to search for.


fast\_search : bool, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.fast_search "Permalink to this definition")

If True, then the search will only be performed on the indexed data, which
yields faster search time.

scan\_stats\_callback : Callable\[\[ [ScanStatistics](https://lancedb.github.io/lance/api/python/ScanStatistics.html "lance.ScanStatistics — Statistics about the scan.")\], None\], default None [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.scan_stats_callback "Permalink to this definition")

A callback function that will be called with the scan statistics after the
scan is complete. Errors raised by the callback will be logged but not
re-raised.

include\_deleted\_rows : bool, default False [¶](https://lancedb.github.io/lance/api/python.html#lance.dataset.LanceDataset.scanner.include_deleted_rows "Permalink to this definition")

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

## API Reference [¶](https://lancedb.github.io/lance/api/python.html\#api-reference "Link to this heading")

More information can be found in the [API reference](https://lancedb.github.io/lance/api/py_modules.html).