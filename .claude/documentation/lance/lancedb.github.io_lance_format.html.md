---
url: "https://lancedb.github.io/lance/format.html"
title: "Lance Formats - Lance  documentation"
---

[Skip to content](https://lancedb.github.io/lance/format.html#dataset-directory)

# Lance Formats [¶](https://lancedb.github.io/lance/format.html\#lance-formats "Link to this heading")

The Lance format is both a table format and a file format. Lance typically refers
to tables as “datasets”. A Lance dataset is designed to efficiently handle secondary indices,
fast ingestion and modification of data, and a rich set of schema evolution features.

## Dataset Directory [¶](https://lancedb.github.io/lance/format.html\#dataset-directory "Link to this heading")

A Lance Dataset is organized in a directory.

```
/path/to/dataset:
    data/*.lance  -- Data directory
    _versions/*.manifest -- Manifest file for each dataset version.
    _indices/{UUID-*}/index.idx -- Secondary index, each index per directory.
    _deletions/*.{arrow,bin} -- Deletion files, which contain ids of rows
      that have been deleted.

```

A `Manifest` file includes the metadata to describe a version of the dataset.

|     |     |
| --- | --- |
| ```<br>  1<br>  2<br>  3<br>  4<br>  5<br>  6<br>  7<br>  8<br>  9<br> 10<br> 11<br> 12<br> 13<br> 14<br> 15<br> 16<br> 17<br> 18<br> 19<br> 20<br> 21<br> 22<br> 23<br> 24<br> 25<br> 26<br> 27<br> 28<br> 29<br> 30<br> 31<br> 32<br> 33<br> 34<br> 35<br> 36<br> 37<br> 38<br> 39<br> 40<br> 41<br> 42<br> 43<br> 44<br> 45<br> 46<br> 47<br> 48<br> 49<br> 50<br> 51<br> 52<br> 53<br> 54<br> 55<br> 56<br> 57<br> 58<br> 59<br> 60<br> 61<br> 62<br> 63<br> 64<br> 65<br> 66<br> 67<br> 68<br> 69<br> 70<br> 71<br> 72<br> 73<br> 74<br> 75<br> 76<br> 77<br> 78<br> 79<br> 80<br> 81<br> 82<br> 83<br> 84<br> 85<br> 86<br> 87<br> 88<br> 89<br> 90<br> 91<br> 92<br> 93<br> 94<br> 95<br> 96<br> 97<br> 98<br> 99<br>100<br>101<br>102<br>103<br>104<br>105<br>106<br>107<br>108<br>109<br>110<br>111<br>112<br>113<br>114<br>115<br>116<br>117<br>118<br>119<br>120<br>121<br>122<br>123<br>124<br>``` | ```<br>// Manifest is a global section shared between all the files.<br>message Manifest {<br>  // All fields of the dataset, including the nested fields.<br>  repeated lance.file.Field fields = 1;<br>  // Fragments of the dataset.<br>  repeated DataFragment fragments = 2;<br>  // Snapshot version number.<br>  uint64 version = 3;<br>  // The file position of the version auxiliary data.<br>  //  * It is not inheritable between versions.<br>  //  * It is not loaded by default during query.<br>  uint64 version_aux_data = 4;<br>  // Schema metadata.<br>  map<string, bytes> metadata = 5;<br>  message WriterVersion {<br>    // The name of the library that created this file.<br>    string library = 1;<br>    // The version of the library that created this file. Because we cannot assume<br>    // that the library is semantically versioned, this is a string. However, if it<br>    // is semantically versioned, it should be a valid semver string without any 'v'<br>    // prefix. For example: `2.0.0`, `2.0.0-rc.1`.<br>    string version = 2;<br>  }<br>  // The version of the writer that created this file.<br>  //<br>  // This information may be used to detect whether the file may have known bugs<br>  // associated with that writer.<br>  WriterVersion writer_version = 13;<br>  // If presented, the file position of the index metadata.<br>  optional uint64 index_section = 6;<br>  // Version creation Timestamp, UTC timezone<br>  google.protobuf.Timestamp timestamp = 7;<br>  // Optional version tag<br>  string tag = 8;<br>  // Feature flags for readers.<br>  //<br>  // A bitmap of flags that indicate which features are required to be able to<br>  // read the table. If a reader does not recognize a flag that is set, it<br>  // should not attempt to read the dataset.<br>  //<br>  // Known flags:<br>  // * 1: deletion files are present<br>  // * 2: move_stable_row_ids: row IDs are tracked and stable after move operations<br>  //       (such as compaction), but not updates.<br>  // * 4: use v2 format (deprecated)<br>  // * 8: table config is present<br>  uint64 reader_feature_flags = 9;<br>  // Feature flags for writers.<br>  //<br>  // A bitmap of flags that indicate which features are required to be able to<br>  // write to the dataset. if a writer does not recognize a flag that is set, it<br>  // should not attempt to write to the dataset.<br>  //<br>  // The flags are the same as for reader_feature_flags, although they will not<br>  // always apply to both.<br>  uint64 writer_feature_flags = 10;<br>  // The highest fragment ID that has been used so far.<br>  //<br>  // This ID is not guaranteed to be present in the current version, but it may<br>  // have been used in previous versions.<br>  // <br>  // For a single file, will be zero.<br>  uint32 max_fragment_id = 11;<br>  // Path to the transaction file, relative to `{root}/_transactions`<br>  //<br>  // This contains a serialized Transaction message representing the transaction<br>  // that created this version.<br>  //<br>  // May be empty if no transaction file was written.<br>  //<br>  // The path format is "{read_version}-{uuid}.txn" where {read_version} is the<br>  // version of the table the transaction read from, and {uuid} is a <br>  // hyphen-separated UUID.<br>  string transaction_file = 12;<br>  // The next unused row id. If zero, then the table does not have any rows.<br>  //<br>  // This is only used if the "move_stable_row_ids" feature flag is set.<br>  uint64 next_row_id = 14;<br>  message DataStorageFormat {<br>    // The format of the data files (e.g. "lance")<br>    string file_format = 1;<br>    // The max format version of the data files.<br>    //<br>    // This is the maximum version of the file format that the dataset will create.<br>    // This may be lower than the maximum version that can be written in order to allow<br>    // older readers to read the dataset.<br>    string version = 2;<br>  }<br>  // The data storage format<br>  //<br>  // This specifies what format is used to store the data files.<br>  DataStorageFormat data_format = 15;<br>  <br>  // Table config.<br>  //<br>  // Keys with the prefix "lance." are reserved for the Lance library. Other<br>  // libraries may wish to similarly prefix their configuration keys<br>  // appropriately.<br>  map<string, string> config = 16;<br>  // The version of the blob dataset associated with this table.  Changes to<br>  // blob fields will modify the blob dataset and update this version in the parent<br>  // table.<br>  //<br>  // If this value is 0 then there are no blob fields.<br>  uint64 blob_dataset_version = 17;<br>} // Manifest<br>``` |

### Fragments [¶](https://lancedb.github.io/lance/format.html\#fragments "Link to this heading")

`DataFragment` represents a chunk of data in the dataset. Itself includes one or more `DataFile`,
where each `DataFile` can contain several columns in the chunk of data. It also may include a
`DeletionFile`, which is explained in a later section.

|     |     |
| --- | --- |
| ```<br>  1<br>  2<br>  3<br>  4<br>  5<br>  6<br>  7<br>  8<br>  9<br> 10<br> 11<br> 12<br> 13<br> 14<br> 15<br> 16<br> 17<br> 18<br> 19<br> 20<br> 21<br> 22<br> 23<br> 24<br> 25<br> 26<br> 27<br> 28<br> 29<br> 30<br> 31<br> 32<br> 33<br> 34<br> 35<br> 36<br> 37<br> 38<br> 39<br> 40<br> 41<br> 42<br> 43<br> 44<br> 45<br> 46<br> 47<br> 48<br> 49<br> 50<br> 51<br> 52<br> 53<br> 54<br> 55<br> 56<br> 57<br> 58<br> 59<br> 60<br> 61<br> 62<br> 63<br> 64<br> 65<br> 66<br> 67<br> 68<br> 69<br> 70<br> 71<br> 72<br> 73<br> 74<br> 75<br> 76<br> 77<br> 78<br> 79<br> 80<br> 81<br> 82<br> 83<br> 84<br> 85<br> 86<br> 87<br> 88<br> 89<br> 90<br> 91<br> 92<br> 93<br> 94<br> 95<br> 96<br> 97<br> 98<br> 99<br>100<br>101<br>102<br>103<br>104<br>105<br>106<br>107<br>108<br>109<br>110<br>111<br>112<br>113<br>114<br>115<br>``` | ```<br>// Data fragment. A fragment is a set of files which represent the<br>// different columns of the same rows.<br>// If column exists in the schema, but the related file does not exist,<br>// treat this column as nulls.<br>message DataFragment {<br>  // Unique ID of each DataFragment<br>  uint64 id = 1;<br>  repeated DataFile files = 2;<br>  // File that indicates which rows, if any, should be considered deleted.<br>  DeletionFile deletion_file = 3;<br>  // TODO: What's the simplest way we can allow an inline tombstone bitmap?<br>  // A serialized RowIdSequence message (see rowids.proto).<br>  //<br>  // These are the row ids for the fragment, in order of the rows as they appear.<br>  // That is, if a fragment has 3 rows, and the row ids are [1, 42, 3], then the<br>  // first row is row 1, the second row is row 42, and the third row is row 3.<br>  oneof row_id_sequence {<br>    // If small (< 200KB), the row ids are stored inline.<br>    bytes inline_row_ids = 5;<br>    // Otherwise, stored as part of a file.<br>    ExternalFile external_row_ids = 6;<br>  } // row_id_sequence<br>  // Number of original rows in the fragment, this includes rows that are <br>  // now marked with deletion tombstones. To compute the current number of rows, <br>  // subtract `deletion_file.num_deleted_rows` from this value.<br>  uint64 physical_rows = 4;<br>}<br>// Lance Data File<br>message DataFile {<br>  // Relative path to the root.<br>  string path = 1;<br>  // The ids of the fields/columns in this file.<br>  //<br>  // -1 is used for "unassigned" while in memory. It is not meant to be written<br>  // to disk. -2 is used for "tombstoned", meaningful a field that is no longer<br>  // in use. This is often because the original field id was reassigned to a<br>  // different data file.<br>  //<br>  // In Lance v1 IDs are assigned based on position in the file, offset by the max<br>  // existing field id in the table (if any already). So when a fragment is first<br>  // created with one file of N columns, the field ids will be 1, 2, ..., N. If a<br>  // second, fragment is created with M columns, the field ids will be N+1, N+2,<br>  // ..., N+M.<br>  //<br>  // In Lance v1 there is one field for each field in the input schema, this includes<br>  // nested fields (both struct and list).  Fixed size list fields have only a single<br>  // field id (these are not considered nested fields in Lance v1).<br>  //<br>  // This allows column indices to be calculated from field IDs and the input schema.<br>  //<br>  // In Lance v2 the field IDs generally follow the same pattern but there is no<br>  // way to calculate the column index from the field ID.  This is because a given<br>  // field could be encoded in many different ways, some of which occupy a different<br>  // number of columns.  For example, a struct field could be encoded into N + 1 columns<br>  // or it could be encoded into a single packed column.  To determine column indices<br>  // the column_indices property should be used instead.<br>  //<br>  // In Lance v1 these ids must be sorted but might not always be contiguous.<br>  repeated int32 fields = 2;<br>  // The top-level column indices for each field in the file.<br>  //<br>  // If the data file is version 1 then this property will be empty<br>  //<br>  // Otherwise there must be one entry for each field in `fields`.<br>  //<br>  // Some fields may not correspond to a top-level column in the file.  In these cases<br>  // the index will -1.<br>  //<br>  // For example, consider the schema:<br>  //<br>  // - dimension: packed-struct (0):<br>  //   - x: u32 (1)<br>  //   - y: u32 (2)<br>  // - path: list<u32> (3)<br>  // - embedding: fsl<768> (4)<br>  //   - fp64<br>  // - borders: fsl<4> (5)<br>  //   - simple-struct (6)<br>  //     - margin: fp64 (7)<br>  //     - padding: fp64 (8)<br>  //<br>  // One possible column indices array could be:<br>  // [0, -1, -1, 1, 3, 4, 5, 6, 7]<br>  //<br>  // This reflects quite a few phenomenon:<br>  // - The packed struct is encoded into a single column and there is no top-level column<br>  //   for the x or y fields<br>  // - The variable sized list is encoded into two columns<br>  // - The embedding is encoded into a single column (common for FSL of primitive) and there<br>  //   is not "FSL column"<br>  // - The borders field actually does have an "FSL column"<br>  //<br>  // The column indices table may not have duplicates (other than -1)<br>  repeated int32 column_indices = 3;<br>  // The major file version used to create the file<br>  uint32 file_major_version = 4;<br>  // The minor file version used to create the file<br>  //<br>  // If both `file_major_version` and `file_minor_version` are set to 0,<br>  // then this is a version 0.1 or version 0.2 file.<br>  uint32 file_minor_version = 5;<br>  // The known size of the file on disk in bytes.<br>  //<br>  // This is used to quickly find the footer of the file.<br>  //<br>  // When this is zero, it should be interpreted as "unknown".<br>  uint64 file_size_bytes = 6;<br>} // DataFile<br>``` |

The overall structure of a fragment is shown below. One or more data files store
the columns of a fragment. New columns can be added to a fragment by adding new
data files. The deletion file (if present), stores the rows that have been
deleted from the fragment.

![_images/fragment_structure.png](https://lancedb.github.io/lance/_images/fragment_structure.png)

Every row has a unique id, which is an u64 that is composed of two u32s: the
fragment id and the local row id. The local row id is just the index of the
row in the data files.

## File Structure [¶](https://lancedb.github.io/lance/format.html\#file-structure "Link to this heading")

Each `.lance` file is the container for the actual data.

![_images/format_overview.png](https://lancedb.github.io/lance/_images/format_overview.png)

At the tail of the file, ColumnMetadata protobuf blocks are used to describe the encoding of the columns
in the file.

|     |     |
| --- | --- |
| ```<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>``` | ```<br>// ## Metadata<br>// Each column has a metadata block that is placed at the end of the file.<br>// These may be read individually to allow for column projection.<br>message ColumnMetadata {<br>  // This describes a page of column data.<br>  message Page {<br>    // The file offsets for each of the page buffers<br>    //<br>    // The number of buffers is variable and depends on the encoding.  There<br>    // may be zero buffers (e.g. constant encoded data) in which case this<br>    // could be empty.<br>    repeated uint64 buffer_offsets = 1;<br>    // The size (in bytes) of each of the page buffers<br>    //<br>    // This field will have the same length as `buffer_offsets` and<br>    // may be empty.<br>    repeated uint64 buffer_sizes = 2;<br>    // Logical length (e.g. # rows) of the page<br>    uint64 length = 3;<br>    // The encoding used to encode the page<br>    Encoding encoding = 4;<br>    // The priority of the page<br>    //<br>    // For tabular data this will be the top-level row number of the first row<br>    // in the page (and top-level rows should not split across pages).<br>    uint64 priority = 5;<br>  }<br>  // Encoding information about the column itself.  This typically describes<br>  // how to interpret the column metadata buffers.  For example, it could<br>  // describe how statistics or dictionaries are stored in the column metadata.<br>  Encoding encoding = 1;<br>  // The pages in the column<br>  repeated Page pages = 2;   <br>  // The file offsets of each of the column metadata buffers<br>  //<br>  // There may be zero buffers.<br>  repeated uint64 buffer_offsets = 3;<br>  // The size (in bytes) of each of the column metadata buffers<br>  //<br>  // This field will have the same length as `buffer_offsets` and<br>  // may be empty.<br>  repeated uint64 buffer_sizes = 4;<br>} // Metadata-End<br>``` |

A `Footer` describes the overall layout of the file. The entire file layout is described here:

|     |     |
| --- | --- |
| ```<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>``` | ```<br>// ## File Layout<br>//<br>// Note: the number of buffers (BN) is independent of the number of columns (CN)<br>//       and pages.<br>//<br>//       Buffers often need to be aligned.  64-byte alignment is common when<br>//       working with SIMD operations.  4096-byte alignment is common when<br>//       working with direct I/O.  In order to ensure these buffers are aligned<br>//       writers may need to insert padding before the buffers.<br>//       <br>//       If direct I/O is required then most (but not all) fields described<br>//       below must be sector aligned.  We have marked these fields with an<br>//       asterisk for clarity.  Readers should assume there will be optional<br>//       padding inserted before these fields.<br>//<br>//       All footer fields are unsigned integers written with  little endian<br>//       byte order.<br>//<br>// ├──────────────────────────────────┤<br>// | Data Pages                       |<br>// |   Data Buffer 0*                 |<br>// |   ...                            |<br>// |   Data Buffer BN*                |<br>// ├──────────────────────────────────┤<br>// | Column Metadatas                 |<br>// | |A| Column 0 Metadata*           |<br>// |     Column 1 Metadata*           |<br>// |     ...                          |<br>// |     Column CN Metadata*          |<br>// ├──────────────────────────────────┤<br>// | Column Metadata Offset Table     |<br>// | |B| Column 0 Metadata Position*  |<br>// |     Column 0 Metadata Size       |<br>// |     ...                          |<br>// |     Column CN Metadata Position  |<br>// |     Column CN Metadata Size      |<br>// ├──────────────────────────────────┤<br>// | Global Buffers Offset Table      |<br>// | |C| Global Buffer 0 Position*    |<br>// |     Global Buffer 0 Size         |<br>// |     ...                          |<br>// |     Global Buffer GN Position    |<br>// |     Global Buffer GN Size        |<br>// ├──────────────────────────────────┤<br>// | Footer                           |<br>// | A u64: Offset to column meta 0   |<br>// | B u64: Offset to CMO table       |<br>// | C u64: Offset to GBO table       |<br>// |   u32: Number of global bufs     |<br>// |   u32: Number of columns         |<br>// |   u16: Major version             |<br>// |   u16: Minor version             |<br>// |   "LANC"                         |<br>// ├──────────────────────────────────┤<br>//<br>// File Layout-End<br>``` |

## File Version [¶](https://lancedb.github.io/lance/format.html\#file-version "Link to this heading")

The Lance file format has gone through a number of changes including a breaking change
from version 1 to version 2. There are a number of APIs that allow the file version to
be specified. Using a newer version of the file format will lead to better compression
and/or performance. However, older software versions may not be able to read newer files.

In addition, the latest version of the file format (next) is unstable and should not be
used for production use cases. Breaking changes could be made to unstable encodings and
that would mean that files written with these encodings are no longer readable by any
newer versions of Lance. The `next` version should only be used for experimentation
and benchmarking upcoming features.

The following values are supported:

| Version | Minimal Lance Version | Maximum Lance Version | Description |
| --- | --- | --- | --- |
| 0.1 | Any | Any | This is the initial Lance format. |
| 2.0 | 0.16.0 | Any | Rework of the Lance file format that removed row groups and introduced null<br>support for lists, fixed size lists, and primitives |
| 2.1 (unstable) | None | Any | Enhances integer and string compression, adds support for nulls in struct fields,<br>and improves random access performance with nested fields. |
| legacy | N/A | N/A | Alias for 0.1 |
| stable | N/A | N/A | Alias for the latest stable version (currently 2.0) |
| next | N/A | N/A | Alias for the latest unstable version (currently 2.1) |

File Versions [¶](https://lancedb.github.io/lance/format.html#id3 "Link to this table")

## File Encodings [¶](https://lancedb.github.io/lance/format.html\#file-encodings "Link to this heading")

Lance supports a variety of encodings for different data types. The encodings
are chosen to give both random access and scan performance. Encodings are added
over time and may be extended in the future. The manifest records a max format
version which controls which encodings will be used. This allows for a gradual
migration to a new data format so that old readers can still read new data while
a migration is in progress.

Encodings are divided into “field encodings” and “array encodings”. Field encodings
are consistent across an entire field of data, while array encodings are used for
individual pages of data within a field. Array encodings can nest other array
encodings (e.g. a dictionary encoding can bitpack the indices) however array encodings
cannot nest field encodings. For this reason data types such as
`Dictionary<UInt8, List<String>>` are not yet supported (since there is no dictionary
field encoding)

| Encoding Name | Encoding Type | What it does | Supported Versions | When it is applied |
| --- | --- | --- | --- | --- |
| Basic struct | Field encoding | Encodes non-nullable struct data | >= 2.0 | Default encoding for structs |
| List | Field encoding | Encodes lists (nullable or non-nullable) | >= 2.0 | Default encoding for lists |
| Basic Primitive | Field encoding | Encodes primitive data types using separate validity array | >= 2.0 | Default encoding for primitive data types |
| Value | Array encoding | Encodes a single vector of fixed-width values | >= 2.0 | Fallback encoding for fixed-width types |
| Binary | Array encoding | Encodes a single vector of variable-width data | >= 2.0 | Fallback encoding for variable-width types |
| Dictionary | Array encoding | Encodes data using a dictionary array and an indices array which is useful for large data types with few unique values | >= 2.0 | Used on string pages with fewer than 100 unique elements |
| Packed struct | Array encoding | Encodes a struct with fixed-width fields in a row-major format making random access more efficient | >= 2.0 | Only used on struct types if the field metadata attribute `"packed"` is set to `"true"` |
| Fsst | Array encoding | Compresses binary data by identifying common substrings (of 8 bytes or less) and encoding them as symbols | >= 2.1 | Used on string pages that are not dictionary encoded |
| Bitpacking | Array encoding | Encodes a single vector of fixed-width values using bitpacking which is useful for integral types that do not span the full range of values | >= 2.1 | Used on integral types |

Encodings Available [¶](https://lancedb.github.io/lance/format.html#id4 "Link to this table")

## Feature Flags [¶](https://lancedb.github.io/lance/format.html\#feature-flags "Link to this heading")

As the file format and dataset evolve, new feature flags are added to the
format. There are two separate fields for checking for feature flags, depending
on whether you are trying to read or write the table. Readers should check the
`reader_feature_flags` to see if there are any flag it is not aware of. Writers
should check `writer_feature_flags`. If either sees a flag they don’t know, they
should return an “unsupported” error on any read or write operation.

## Fields [¶](https://lancedb.github.io/lance/format.html\#fields "Link to this heading")

Fields represent the metadata for a column. This includes the name, data type,
id, nullability, and encoding.

Fields are listed in depth first order, and can be one of (1) parent (struct),
(2) repeated (list/array), or (3) leaf (primitive). For example, the schema:

```
a: i32
b: struct {
    c: list<i32>
    d: i32
}

```

Would be represented as the following field list:

| name | id | type | parent\_id | logical\_type |
| --- | --- | --- | --- | --- |
| `a` | 1 | LEAF | 0 | `"int32"` |
| `b` | 2 | PARENT | 0 | `"struct"` |
| `b.c` | 3 | REPEATED | 2 | `"list"` |
| `b.c` | 4 | LEAF | 3 | `"int32"` |
| `b.d` | 5 | LEAF | 2 | `"int32"` |

- Field Encoding Specification


Column-level encoding configurations are specified through PyArrow field metadata:

```
import pyarrow as pa

schema = pa.schema([\
    pa.field(\
        "compressible_strings",\
        pa.string(),\
        metadata={\
            "lance-encoding:compression": "zstd",\
            "lance-encoding:compression-level": "3",\
            "lance-encoding:structural-encoding": "miniblock",\
            "lance-encoding:packed": "true"\
        }\
    )\
])

```

| Metadata Key | Type | Description | Example Values | Example Usage (Python) |
| --- | --- | --- | --- | --- |
| `lance-encoding:compression` | Compression | Specifies compression algorithm | zstd | `metadata={"lance-encoding:compression": "zstd"}` |
| `lance-encoding:compression-level` | Compression | Zstd compression level (1-22) | 3 | `metadata={"lance-encoding:compression-level": "3"}` |
| `lance-encoding:blob` | Storage | Marks binary data (>4MB) for chunked storage | true/false | `metadata={"lance-encoding:blob": "true"}` |
| `lance-encoding:packed` | Optimization | Struct memory layout optimization | true/false | `metadata={"lance-encoding:packed": "true"}` |
| `lance-encoding:structural-encoding` | Nested Data | Encoding strategy for nested structures | miniblock/fullzip | `metadata={"lance-encoding:structural-encoding": "miniblock"}` |

## Dataset Update and Schema Evolution [¶](https://lancedb.github.io/lance/format.html\#dataset-update-and-schema-evolution "Link to this heading")

`Lance` supports fast dataset update and schema evolution via manipulating the `Manifest` metadata.

`Appending` is done by appending new `Fragment` to the dataset.
While adding columns is done by adding new `DataFile` of the new columns to each `Fragment`.
Finally, `Overwrite` a dataset can be done by resetting the `Fragment` list of the `Manifest`.

![_images/schema_evolution.png](https://lancedb.github.io/lance/_images/schema_evolution.png)

## Deletion [¶](https://lancedb.github.io/lance/format.html\#deletion "Link to this heading")

Rows can be marked deleted by adding a deletion file next to the data in the
`_deletions` folder. These files contain the indices of rows that have between
deleted for some fragment. For a given version of the dataset, each fragment can
have up to one deletion file. Fragments that have no deleted rows have no deletion
file.

Readers should filter out row ids contained in these deletion files during a
scan or ANN search.

Deletion files come in two flavors:

1. Arrow files: which store a column with a flat vector of indices

2. Roaring bitmaps: which store the indices as compressed bitmaps.


[Roaring Bitmaps](https://roaringbitmap.org/) are used for larger deletion sets, while Arrow files are used for
small ones. This is because Roaring Bitmaps are known to be inefficient for small
sets.

The filenames of deletion files are structured like:

```
_deletions/{fragment_id}-{read_version}-{random_id}.{arrow|bin}

```

Where `fragment_id` is the fragment the file corresponds to, `read_version` is
the version of the dataset that it was created off of (usually one less than the
version it was committed to), and `random_id` is a random i64 used to avoid
collisions. The suffix is determined by the file type ( `.arrow` for Arrow file,
`.bin` for roaring bitmap).

|     |     |
| --- | --- |
| ```<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>``` | ```<br>// Deletion File<br>//<br>// The path of the deletion file is constructed as:<br>//   {root}/_deletions/{fragment_id}-{read_version}-{id}.{extension}<br>// where {extension} is `.arrow` or `.bin` depending on the type of deletion.<br>message DeletionFile {<br>  // Type of deletion file, which varies depending on what is the most efficient<br>  // way to store the deleted row offsets. If none, then will be unspecified. If there are<br>  // sparsely deleted rows, then ARROW_ARRAY is the most efficient. If there are<br>  // densely deleted rows, then BIT_MAP is the most efficient.<br>  enum DeletionFileType {<br>    // Deletion file is a single Int32Array of deleted row offsets. This is stored as<br>    // an Arrow IPC file with one batch and one column. Has a .arrow extension.<br>    ARROW_ARRAY = 0;<br>    // Deletion file is a Roaring Bitmap of deleted row offsets. Has a .bin extension.<br>    BITMAP = 1;<br>  }<br>  // Type of deletion file. If it is unspecified, then the remaining fields will be missing.<br>  DeletionFileType file_type = 1;<br>  // The version of the dataset this deletion file was built from.<br>  uint64 read_version = 2;<br>  // An opaque id used to differentiate this file from others written by concurrent<br>  // writers.<br>  uint64 id = 3;<br>  // The number of rows that are marked as deleted.<br>  uint64 num_deleted_rows = 4;<br>} // DeletionFile<br>``` |

Deletes can be materialized by re-writing data files with the deleted rows
removed. However, this invalidates row indices and thus the ANN indices, which
can be expensive to recompute.

## Committing Datasets [¶](https://lancedb.github.io/lance/format.html\#committing-datasets "Link to this heading")

A new version of a dataset is committed by writing a new manifest file to the
`_versions` directory.

To prevent concurrent writers from overwriting each other, the commit process
must be atomic and consistent for all writers. If two writers try to commit
using different mechanisms, they may overwrite each other’s changes. For any
storage system that natively supports atomic rename-if-not-exists or
put-if-not-exists, these operations should be used. This is true of local file
systems and most cloud object stores including Amazon S3, Google Cloud Storage,
Microsoft Azure Blob Storage. For ones that lack this functionality,
an external locking mechanism can be configured by the user.

### Manifest Naming Schemes [¶](https://lancedb.github.io/lance/format.html\#manifest-naming-schemes "Link to this heading")

Manifest files must use a consistent naming scheme. The names correspond to the
versions. That way we can open the right version of the dataset without having
to read all the manifests. It also makes it clear which file path is the next
one to be written.

There are two naming schemes that can be used:

1. V1: `_versions/{version}.manifest`. This is the legacy naming scheme.

2. V2: `_versions/{u64::MAX - version:020}.manifest`. This is the new naming
scheme. The version is zero-padded (to 20 digits) and subtracted from
`u64::MAX`. This allows the versions to be sorted in descending order,
making it possible to find the latest manifest on object storage using a
single list call.


It is an error for there to be a mixture of these two naming schemes.

### Conflict resolution [¶](https://lancedb.github.io/lance/format.html\#conflict-resolution "Link to this heading")

If two writers try to commit at the same time, one will succeed and the other
will fail. The failed writer should attempt to retry the commit, but only if
its changes are compatible with the changes made by the successful writer.

The changes for a given commit are recorded as a transaction file, under the
`_transactions` prefix in the dataset directory. The transaction file is a
serialized `Transaction` protobuf message. See the `transaction.proto` file
for its definition.

![_images/conflict_resolution_flow.png](https://lancedb.github.io/lance/_images/conflict_resolution_flow.png)

The commit process is as follows:

> 1. The writer finishes writing all data files.
>
> 2. The writer creates a transaction file in the `_transactions` directory.
> This file describes the operations that were performed, which is used for two
> purposes: (1) to detect conflicts, and (2) to re-build the manifest during
> retries.
>
> 3. Look for any new commits since the writer started writing. If there are any,
> read their transaction files and check for conflicts. If there are any
> conflicts, abort the commit. Otherwise, continue.
>
> 4. Build a manifest and attempt to commit it to the next version. If the commit
> fails because another writer has already committed, go back to step 3.

When checking whether two transactions conflict, be conservative. If the
transaction file is missing, assume it conflicts. If the transaction file
has an unknown operation, assume it conflicts.

### External Manifest Store [¶](https://lancedb.github.io/lance/format.html\#external-manifest-store "Link to this heading")

If the backing object store does not support \*-if-not-exists operations, an
external manifest store can be used to allow concurrent writers. An external
manifest store is a KV store that supports put-if-not-exists operation. The
external manifest store supplements but does not replace the manifests in
object storage. A reader unaware of the external manifest store could read a
table that uses it, but it might be up to one version behind the true latest
version of the table.

![_images/external_store_commit.gif](https://lancedb.github.io/lance/_images/external_store_commit.gif)

The commit process is as follows:

1. `PUT_OBJECT_STORE mydataset.lance/_versions/{version}.manifest-{uuid}` stage a new manifest in object store under a unique path determined by new uuid

2. `PUT_EXTERNAL_STORE base_uri, version, mydataset.lance/_versions/{version}.manifest-{uuid}` commit the path of the staged manifest to the external store.

3. `COPY_OBJECT_STORE mydataset.lance/_versions/{version}.manifest-{uuid} mydataset.lance/_versions/{version}.manifest` copy the staged manifest to the final path

4. `PUT_EXTERNAL_STORE base_uri, version, mydataset.lance/_versions/{version}.manifest` update the external store to point to the final manifest


Note that the commit is effectively complete after step 2. If the writer fails
after step 2, a reader will be able to detect the external store and object store
are out-of-sync, and will try to synchronize the two stores. If the reattempt at
synchronization fails, the reader will refuse to load. This is to ensure that
the dataset is always portable by copying the dataset directory without special
tool.

![_images/external_store_reader.gif](https://lancedb.github.io/lance/_images/external_store_reader.gif)

The reader load process is as follows:

1. `GET_EXTERNAL_STORE base_uri, version, path` then, if path does not end in a UUID return the path

2. `COPY_OBJECT_STORE mydataset.lance/_versions/{version}.manifest-{uuid} mydataset.lance/_versions/{version}.manifest` reattempt synchronization

3. `PUT_EXTERNAL_STORE base_uri, version, mydataset.lance/_versions/{version}.manifest` update the external store to point to the final manifest

4. `RETURN mydataset.lance/_versions/{version}.manifest` always return the finalized path, return error if synchronization fails


## Statistics [¶](https://lancedb.github.io/lance/format.html\#statistics "Link to this heading")

Statistics are stored within Lance files. The statistics can be used to determine
which pages can be skipped within a query. The null count, lower bound (min),
and upper bound (max) are stored.

Statistics themselves are stored in Lance’s columnar format, which allows for
selectively reading only relevant stats columns.

### Statistic values [¶](https://lancedb.github.io/lance/format.html\#statistic-values "Link to this heading")

Three types of statistics are stored per column: null count, min value, max value.
The min and max values are stored as their native data types in arrays.

There are special behaviors for different data types to account for nulls:

For integer-based data types (including signed and unsigned integers, dates,
and timestamps), if the min and max are unknown (all values are null), then the
minimum/maximum representable values should be used instead.

For float data types, if the min and max are unknown, then use `-Inf` and `+Inf`,
respectively. ( `-Inf` and `+Inf` may also be used for min and max if those values
are present in the arrays.) `NaN` values should be ignored for the purpose of min and max
statistics. If the max value is zero (negative or positive), the max value
should be recorded as `+0.0`. Likewise, if the min value is zero (positive
or negative), it should be recorded as `-0.0`.

For binary data types, if the min or max are unknown or unrepresentable, then use
null value. Binary data type bounds can also be truncated. For example, an array
containing just the value `"abcd"` could have a truncated min of
`"abc"` and max of `"abd"`. If there is no truncated value greater than the
maximum value, then instead use null for the maximum.

Warning

The `min` and `max` values are not guaranteed to be within the array;
they are simply upper and lower bounds. Two common cases where they are not
contained in the array is if the min or max original value was deleted and
when binary data is truncated. Therefore, statistic should not be used to
compute queries such as `SELECT max(col) FROM table`.

### Page-level statistics format [¶](https://lancedb.github.io/lance/format.html\#page-level-statistics-format "Link to this heading")

Page-level statistics are stored as arrays within the Lance file. Each array
contains one page long and is `num_pages` long. The page offsets are stored in
an array just like the data page table. The offset to the statistics page
table is stored in the metadata.

The schema for the statistics is:

```
<field_id_1>: struct
    null_count: i64
    min_value: <field_1_data_type>
    max_value: <field_1_data_type>
...
<field_id_N>: struct
    null_count: i64
    min_value: <field_N_data_type>
    max_value: <field_N_data_type>

```

Any number of fields may be missing, as statistics for some fields or of some
kind may be skipped. In addition, readers should expect there may be extra
fields that are not in this schema. These should be ignored. Future changes to
the format may add additional fields, but these changes will be backwards
compatible.

However, writers should not write extra fields that aren’t described in this
document. Until they are defined in the specification, there is no guarantee that
readers will be able to safely interpret new forms of statistics.

## Feature: Move-Stable Row IDs [¶](https://lancedb.github.io/lance/format.html\#feature-move-stable-row-ids "Link to this heading")

The row ids features assigns a unique u64 id to each row in the table. This id is
stable after being moved (such as during compaction), but is not necessarily
stable after a row is updated. (A future feature may make them stable after
updates.) To make access fast, a secondary index is created that maps row ids to
their locations in the table. The respective parts of these indices are stored
in the respective fragment’s metadata.

row id

A unique auto-incrementing u64 id assigned to each row in the table.

row address

The current location of a row in the table. This is a u64 that can be thought
of as a pair of two u32 values: the fragment id and the local row offset. For
example, if the row address is (42, 9), then the row is in the 42rd fragment
and is the 10th row in that fragment.

row id sequence

The sequence of row ids in a fragment.

row id index

A secondary index that maps row ids to row addresses. This index is constructed
by reading all the row id sequences.

### Assigning row ids [¶](https://lancedb.github.io/lance/format.html\#assigning-row-ids "Link to this heading")

Row ids are assigned in a monotonically increasing sequence. The next row id is
stored in the manifest as the field `next_row_id`. This starts at zero. When
making a commit, the writer uses that field to assign row ids to new fragments.
If the commit fails, the writer will re-read the new `next_row_id`, update
the new row ids, and then try again. This is similar to how the `max_fragment_id`
is used to assign new fragment ids.

When a row id updated, it is typically assigned a new row id rather than
reusing the old one. This is because this feature doesn’t have a mechanism to
update secondary indices that may reference the old values for the row id. By
deleting the old row id and creating a new one, the secondary indices will avoid
referencing stale data.

### Row ID sequences [¶](https://lancedb.github.io/lance/format.html\#row-id-sequences "Link to this heading")

The row id values for a fragment are stored in a `RowIdSequence` protobuf
message. This is described in the [protos/rowids.proto](https://github.com/lancedb/lance/blob/main/protos/rowids.proto) file. Row id sequences
are just arrays of u64 values, which have representations optimized for the
common case where they are sorted and possibly contiguous. For example, a new
fragment will have a row id sequence that is just a simple range, so it is
stored as a `start` and `end` value.

These sequence messages are either stored inline in the fragment metadata, or
are written to a separate file and referenced from the fragment metadata. This
choice is typically made based on the size of the sequence. If the sequence is
small, it is stored inline. If it is large, it is written to a separate file. By
keeping the small sequences inline, we can avoid the overhead of additional IO
operations.

[protos/table.proto](https://github.com/lancedb/lance/blob/main/protos/table.proto) [¶](https://lancedb.github.io/lance/format.html#id5 "Permalink to this code")

```
  oneof row_id_sequence {
    // If small (< 200KB), the row ids are stored inline.
    bytes inline_row_ids = 5;
    // Otherwise, stored as part of a file.
    ExternalFile external_row_ids = 6;
  } // row_id_sequence

```

### Row ID index [¶](https://lancedb.github.io/lance/format.html\#row-id-index "Link to this heading")

To ensure fast access to rows by their row id, a secondary index is created that
maps row ids to their locations in the table. This index is built when a table is
loaded, based on the row id sequences in the fragments. For example, if fragment
42 has a row id sequence of `[0, 63, 10]`, then the index will have entries for
`0 -> (42, 0)`, `63 -> (42, 1)`, `10 -> (42, 2)`. The exact form of this
index is left up to the implementation, but it should be optimized for fast lookups.