---
url: "https://lancedb.github.io/lance/introduction/read_and_write.html"
title: "Read and Write Data - Lance  documentation"
---

[Skip to content](https://lancedb.github.io/lance/introduction/read_and_write.html#writing-lance-dataset)

# Read and Write Data [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#read-and-write-data "Link to this heading")

## Writing Lance Dataset [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#writing-lance-dataset "Link to this heading")

If you’re familiar with [Apache PyArrow](https://arrow.apache.org/docs/python/getstarted.html),
you’ll find that creating a Lance dataset is straightforward.
Begin by writing a [`pyarrow.Table`](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)") using the [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") function.

```
>>> import lance
>>> import pyarrow as pa

>>> table = pa.Table.from_pylist([{"name": "Alice", "age": 20},\
...                               {"name": "Bob", "age": 30}])
>>> ds = lance.write_dataset(table, "./alice_and_bob.lance")

```

If the dataset is too large to fully load into memory, you can stream data using [`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri")
also supports `Iterator` of [`pyarrow.RecordBatch`](https://arrow.apache.org/docs/python/generated/pyarrow.RecordBatch.html#pyarrow.RecordBatch "(in Apache Arrow v20.0.0)") es.
You will need to provide a [`pyarrow.Schema`](https://arrow.apache.org/docs/python/generated/pyarrow.Schema.html#pyarrow.Schema "(in Apache Arrow v20.0.0)") for the dataset in this case.

```
>>> def producer() -> Iterator[pa.RecordBatch]:
...     """An iterator of RecordBatches."""
...     yield pa.RecordBatch.from_pylist([{"name": "Alice", "age": 20}])
...     yield pa.RecordBatch.from_pylist([{"name": "Bob", "age": 30}])

>>> schema = pa.schema([\
...     ("name", pa.string()),\
...     ("age", pa.int32()),\
... ])

>>> ds = lance.write_dataset(producer(),
...                          "./alice_and_bob.lance",
...                          schema=schema, mode="overwrite")
>>> ds.count_rows()
2

```

[`lance.write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") supports writing [`pyarrow.Table`](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html#pyarrow.Table "(in Apache Arrow v20.0.0)"), [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html#pandas.DataFrame "(in pandas v2.3.0)"),
[`pyarrow.dataset.Dataset`](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Dataset.html#pyarrow.dataset.Dataset "(in Apache Arrow v20.0.0)"), and `Iterator[pyarrow.RecordBatch]`.

## Adding Rows [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#adding-rows "Link to this heading")

To insert data into your dataset, you can use either [`LanceDataset.insert`](https://lancedb.github.io/lance/api/python/LanceDataset.insert.html "lance.LanceDataset.insert — Insert data into the dataset.")
or [`write_dataset()`](https://lancedb.github.io/lance/api/python/write_dataset.html "lance.write_dataset — Write a given data_obj to the given uri") with `mode=append`.

```
>>> import lance
>>> import pyarrow as pa

>>> table = pa.Table.from_pylist([{"name": "Alice", "age": 20},\
...                               {"name": "Bob", "age": 30}])
>>> ds = lance.write_dataset(table, "./insert_example.lance")

>>> new_table = pa.Table.from_pylist([{"name": "Carla", "age": 37}])
>>> ds.insert(new_table)
>>> ds.to_table().to_pandas()
    name  age
0  Alice   20
1    Bob   30
2  Carla   37

>>> new_table2 = pa.Table.from_pylist([{"name": "David", "age": 42}])
>>> ds = lance.write_dataset(new_table2, ds, mode="append")
>>> ds.to_table().to_pandas()
    name  age
0  Alice   20
1    Bob   30
2  Carla   37
3  David   42

```

## Deleting rows [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#deleting-rows "Link to this heading")

Lance supports deleting rows from a dataset using a SQL filter, as described in filter-push-down.
For example, to delete Bob’s row from the dataset above, one could use:

```
>>> import lance

>>> dataset = lance.dataset("./alice_and_bob.lance")
>>> dataset.delete("name = 'Bob'")
>>> dataset2 = lance.dataset("./alice_and_bob.lance")
>>> dataset2.to_table().to_pandas()
    name  age
0  Alice   20

```

Note

[Lance Format is immutable](https://lancedb.github.io/lance/format.html). Each write operation creates a new version of the dataset,
so users must reopen the dataset to see the changes. Likewise, rows are removed by marking
them as deleted in a separate deletion index, rather than rewriting the files. This approach
is faster and avoids invalidating any indices that reference the files, ensuring that subsequent
queries do not return the deleted rows.

## Updating rows [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#updating-rows "Link to this heading")

Lance supports updating rows based on SQL expressions with the
[`lance.LanceDataset.update()`](https://lancedb.github.io/lance/api/python/LanceDataset.update.html "lance.LanceDataset.update — Update column values for rows matching where.") method. For example, if we notice
that Bob’s name in our dataset has been sometimes written as `Blob`, we can fix
that with:

```
import lance

dataset = lance.dataset("./alice_and_bob.lance")
dataset.update({"name": "'Bob'"}, where="name = 'Blob'")

```

The update values are SQL expressions, which is why `'Bob'` is wrapped in single
quotes. This means we can use complex expressions that reference existing columns if
we wish. For example, if two years have passed and we wish to update the ages
of Alice and Bob in the same example, we could write:

```
import lance

dataset = lance.dataset("./alice_and_bob.lance")
dataset.update({"age": "age + 2"})

```

If you are trying to update a set of individual rows with new values then it is often
more efficient to use the merge insert operation described below.

```
import lance

# Change the ages of both Alice and Bob
new_table = pa.Table.from_pylist([{"name": "Alice", "age": 30},\
                                  {"name": "Bob", "age": 20}])

# This works, but is inefficient, see below for a better approach
dataset = lance.dataset("./alice_and_bob.lance")
for idx in range(new_table.num_rows):
  name = new_table[0][idx].as_py()
  new_age = new_table[1][idx].as_py()
  dataset.update({"age": new_age}, where=f"name='{name}'")

```

## Merge Insert [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#merge-insert "Link to this heading")

Lance supports a merge insert operation. This can be used to add new data in bulk
while also (potentially) matching against existing data. This operation can be used
for a number of different use cases.

### Bulk Update [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#bulk-update "Link to this heading")

The [`lance.LanceDataset.update()`](https://lancedb.github.io/lance/api/python/LanceDataset.update.html "lance.LanceDataset.update — Update column values for rows matching where.") method is useful for updating rows based on
a filter. However, if we want to replace existing rows with new rows then a [`lance.LanceDataset.merge_insert()`](https://lancedb.github.io/lance/api/python/LanceDataset.merge_insert.html "lance.LanceDataset.merge_insert — Returns a builder that can be used to create a \"merge insert\" operation")
operation would be more efficient:

```
>>> import lance

>>> dataset = lance.dataset("./alice_and_bob.lance")
>>> dataset.to_table().to_pandas()
    name  age
0  Alice   20
1    Bob   30
>>> # Change the ages of both Alice and Bob
>>> new_table = pa.Table.from_pylist([{"name": "Alice", "age": 2},\
...                                   {"name": "Bob", "age": 3}])
>>> # This will use `name` as the key for matching rows.  Merge insert
>>> # uses a JOIN internally and so you typically want this column to
>>> # be a unique key or id of some kind.
>>> rst = dataset.merge_insert("name") \
...        .when_matched_update_all() \
...        .execute(new_table)
>>> dataset.to_table().to_pandas()
    name  age
0  Alice    2
1    Bob    3

```

Note that, similar to the update operation, rows that are modified will
be removed and inserted back into the table, changing their position to
the end. Also, the relative order of these rows could change because we
are using a hash-join operation internally.

### Insert if not Exists [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#insert-if-not-exists "Link to this heading")

Sometimes we only want to insert data if we haven’t already inserted it
before. This can happen, for example, when we have a batch of data but
we don’t know which rows we’ve added previously and we don’t want to
create duplicate rows. We can use the merge insert operation to achieve
this:

```
>>> # Bob is already in the table, but Carla is new
>>> new_table = pa.Table.from_pylist([{"name": "Bob", "age": 30},\
...                                   {"name": "Carla", "age": 37}])
>>>
>>> dataset = lance.dataset("./alice_and_bob.lance")
>>>
>>> # This will insert Carla but leave Bob unchanged
>>> _ = dataset.merge_insert("name") \
...        .when_not_matched_insert_all() \
...        .execute(new_table)
>>> # Verify that Carla was added but Bob remains unchanged
>>> dataset.to_table().to_pandas()
    name  age
0  Alice   20
1    Bob   30
2  Carla   37

```

### Update or Insert (Upsert) [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#update-or-insert-upsert "Link to this heading")

Sometimes we want to combine both of the above behaviors. If a row
already exists we want to update it. If the row does not exist we want
to add it. This operation is sometimes called “upsert”. We can use
the merge insert operation to do this as well:

```
>>> import lance
>>> import pyarrow as pa
>>>
>>> # Change Carla's age and insert David
>>> new_table = pa.Table.from_pylist([{"name": "Carla", "age": 27},\
...                                   {"name": "David", "age": 42}])
>>>
>>> dataset = lance.dataset("./alice_and_bob.lance")
>>>
>>> # This will update Carla and insert David
>>> _ = dataset.merge_insert("name") \
...        .when_matched_update_all() \
...        .when_not_matched_insert_all() \
...        .execute(new_table)
>>> # Verify the results
>>> dataset.to_table().to_pandas()
    name  age
0  Alice   20
1    Bob   30
2  Carla   27
3  David   42

```

### Replace a Portion of Data [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#replace-a-portion-of-data "Link to this heading")

A less common, but still useful, behavior can be to replace some region
of existing rows (defined by a filter) with new data. This is similar
to performing both a delete and an insert in a single transaction. For
example:

```
>>> import lance
>>> import pyarrow as pa
>>>
>>> new_table = pa.Table.from_pylist([{"name": "Edgar", "age": 46},\
...                                   {"name": "Francene", "age": 44}])
>>>
>>> dataset = lance.dataset("./alice_and_bob.lance")
>>> dataset.to_table().to_pandas()
      name  age
0    Alice   20
1      Bob   30
2  Charlie   45
3    Donna   50
>>>
>>> # This will remove anyone above 40 and insert our new data
>>> _ = dataset.merge_insert("name") \
...        .when_not_matched_insert_all() \
...        .when_not_matched_by_source_delete("age >= 40") \
...        .execute(new_table)
>>> # Verify the results - people over 40 replaced with new data
>>> dataset.to_table().to_pandas()
       name  age
0     Alice   20
1       Bob   30
2     Edgar   46
3  Francene   44

```

## Reading Lance Dataset [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#reading-lance-dataset "Link to this heading")

To open a Lance dataset, use the [`lance.dataset()`](https://lancedb.github.io/lance/api/python/dataset.html "lance.dataset — Opens the Lance dataset from the address specified.") function:

```
import lance
ds = lance.dataset("s3://bucket/path/imagenet.lance")
# Or local path
ds = lance.dataset("./imagenet.lance")

```

Note

Lance supports local file system, AWS `s3` and Google Cloud Storage( `gs`) as storage backends
at the moment. Read more in [\`Object Store Configuration\`\_](https://lancedb.github.io/lance/introduction/read_and_write.html#id1).

The most straightforward approach for reading a Lance dataset is to utilize the [`lance.LanceDataset.to_table()`](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html "lance.LanceDataset.to_table — Read the data into memory as a pyarrow.Table")
method in order to load the entire dataset into memory.

```
table = ds.to_table()

```

Due to Lance being a high-performance columnar format, it enables efficient reading of subsets of the dataset by utilizing
**Column (projection)** push-down and **filter (predicates)** push-downs.

```
table = ds.to_table(
    columns=["image", "label"],
    filter="label = 2 AND text IS NOT NULL",
    limit=1000,
    offset=3000)

```

Lance understands the cost of reading heavy columns such as `image`.
Consequently, it employs an optimized query plan to execute the operation efficiently.

If the dataset is too large to fit in memory, you can read it in batches
using the [`lance.LanceDataset.to_batches()`](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches — Read the dataset as materialized record batches.") method:

```
for batch in ds.to_batches(columns=["image"], filter="label = 10"):
    # do something with batch
    compute_on_batch(batch)

```

Unsurprisingly, [`to_batches()`](https://lancedb.github.io/lance/api/python/LanceDataset.to_batches.html "lance.LanceDataset.to_batches — Read the dataset as materialized record batches.") takes the same parameters
as [`to_table()`](https://lancedb.github.io/lance/api/python/LanceDataset.to_table.html "lance.LanceDataset.to_table — Read the data into memory as a pyarrow.Table") function.

Lance embraces the utilization of standard SQL expressions as predicates for dataset filtering.
By pushing down the SQL predicates directly to the storage system,
the overall I/O load during a scan is significantly reduced.

Currently, Lance supports a growing list of expressions.

- `>`, `>=`, `<`, `<=`, `=`

- `AND`, `OR`, `NOT`

- `IS NULL`, `IS NOT NULL`

- `IS TRUE`, `IS NOT TRUE`, `IS FALSE`, `IS NOT FALSE`

- `IN`

- `LIKE`, `NOT LIKE`

- `regexp_match(column, pattern)`

- `CAST`


For example, the following filter string is acceptable:

```
((label IN [10, 20]) AND (note['email'] IS NOT NULL))
    OR NOT note['created']

```

Nested fields can be accessed using the subscripts. Struct fields can be
subscripted using field names, while list fields can be subscripted using
indices.

If your column name contains special characters or is a [SQL Keyword](https://docs.rs/sqlparser/latest/sqlparser/keywords/index.html),
you can use backtick ( `` ` ``) to escape it. For nested fields, each segment of the
path must be wrapped in backticks.

```
`CUBE` = 10 AND `column name with space` IS NOT NULL
  AND `nested with space`.`inner with space` < 2

```

Warning

Field names containing periods ( `.`) are not supported.

Literals for dates, timestamps, and decimals can be written by writing the string
value after the type name. For example

```
date_col = date '2021-01-01'
and timestamp_col = timestamp '2021-01-01 00:00:00'
and decimal_col = decimal(8,3) '1.000'

```

For timestamp columns, the precision can be specified as a number in the type
parameter. Microsecond precision (6) is the default.

| SQL | Time unit |
| --- | --- |
| `timestamp(0)` | Seconds |
| `timestamp(3)` | Milliseconds |
| `timestamp(6)` | Microseconds |
| `timestamp(9)` | Nanoseconds |

Lance internally stores data in Arrow format. The mapping from SQL types to Arrow
is:

| SQL type | Arrow type |
| --- | --- |
| `boolean` | `Boolean` |
| `tinyint` / `tinyint unsigned` | `Int8` / `UInt8` |
| `smallint` / `smallint unsigned` | `Int16` / `UInt16` |
| `int` or `integer` / `int unsigned` or `integer unsigned` | `Int32` / `UInt32` |
| `bigint` / `bigint unsigned` | `Int64` / `UInt64` |
| `float` | `Float32` |
| `double` | `Float64` |
| `decimal(precision, scale)` | `Decimal128` |
| `date` | `Date32` |
| `timestamp` | `Timestamp` (1) |
| `string` | `Utf8` |
| `binary` | `Binary` |

1. See precision mapping in previous table.


One district feature of Lance, as columnar format, is that it allows you to read random samples quickly.

```
# Access the 2nd, 101th and 501th rows
data = ds.take([1, 100, 500], columns=["image", "label"])

```

The ability to achieve fast random access to individual rows plays a crucial role in facilitating various workflows
such as random sampling and shuffling in ML training.
Additionally, it empowers users to construct secondary indices,
enabling swift execution of queries for enhanced performance.

## Table Maintenance [¶](https://lancedb.github.io/lance/introduction/read_and_write.html\#table-maintenance "Link to this heading")

Some operations over time will cause a Lance dataset to have a poor layout. For
example, many small appends will lead to a large number of small fragments. Or
deleting many rows will lead to slower queries due to the need to filter out
deleted rows.

To address this, Lance provides methods for optimizing dataset layout.

Data files can be rewritten so there are fewer files. When passing a
`target_rows_per_fragment` to [`lance.dataset.DatasetOptimizer.compact_files()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.DatasetOptimizer.compact_files "lance.dataset.DatasetOptimizer.compact_files — Compacts small files in the dataset, reducing total number of files."),
Lance will skip any fragments that are already above that row count, and rewrite
others. Fragments will be merged according to their fragment ids, so the inherent
ordering of the data will be preserved.

Note

Compaction creates a new version of the table. It does not delete the old
version of the table and the files referenced by it.

```
import lance

dataset = lance.dataset("./alice_and_bob.lance")
dataset.optimize.compact_files(target_rows_per_fragment=1024 * 1024)

```

During compaction, Lance can also remove deleted rows. Rewritten fragments will
not have deletion files. This can improve scan performance since the soft deleted
rows don’t have to be skipped during the scan.

When files are rewritten, the original row addresses are invalidated. This means the
affected files are no longer part of any ANN index if they were before. Because
of this, it’s recommended to rewrite files before re-building indices.