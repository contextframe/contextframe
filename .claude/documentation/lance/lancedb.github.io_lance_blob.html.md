---
url: "https://lancedb.github.io/lance/blob.html"
title: "Blob As Files - Lance  documentation"
---

# Blob As Files [¶](https://lancedb.github.io/lance/blob.html\#blob-as-files "Link to this heading")

Unlike other data formats, large multimodal data is a first-class citizen in the Lance columnar format.
Lance provides a high-level API to store and retrieve large binary objects (blobs) in Lance datasets.

[![_images/blob.png](https://lancedb.github.io/lance/_images/blob.png)](https://lancedb.github.io/lance/_images/blob.png)

Lance serves large binary data using [`lance.BlobFile`](https://lancedb.github.io/lance/api/python/BlobFile.html "lance.BlobFile — Represents a blob in a Lance dataset as a file-like object."), which
is a file-like object that lazily reads large binary objects.

To create a Lance dataset with large blob data, you can mark a large binary column as a blob column by
adding the metadata `lance-encoding:blob` to `true`.

```
import pyarrow as pa

schema = pa.schema(
    [\
        pa.field("id", pa.int64()),\
        pa.field("video",\
            pa.large_binary(),\
            metadata={"lance-encoding:blob": "true"}\
        ),\
    ]
)

```

To fetch blobs from a Lance dataset, you can use [`lance.dataset.LanceDataset.take_blobs()`](https://lancedb.github.io/lance/api/py_modules.html#lance.dataset.LanceDataset.take_blobs "lance.dataset.LanceDataset.take_blobs — Select blobs by row IDs.").

For example, it’s easy to use BlobFile to extract frames from a video file without
loading the entire video into memory.

```
# pip install av pylance

import av
import lance

ds = lance.dataset("./youtube.lance")
start_time, end_time = 500, 1000
blobs = ds.take_blobs([5], "video")
with av.open(blobs[0]) as container:
    stream = container.streams.video[0]
    stream.codec_context.skip_frame = "NONKEY"

    start_time = start_time / stream.time_base
    start_time = start_time.as_integer_ratio()[0]
    end_time = end_time / stream.time_base
    container.seek(start_time, stream=stream)

    for frame in container.decode(stream):
        if frame.time > end_time:
            break
        display(frame.to_image())
        clear_output(wait=True)

```