---
url: "https://lancedb.github.io/lance/notebooks/quickstart.html"
title: "Quickstart - Lance  documentation"
---

[Skip to content](https://lancedb.github.io/lance/notebooks/quickstart.html#creating-datasets)

# Quickstart [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#quickstart "Link to this heading")

```
import shutil

import lance
import numpy as np
import pandas as pd
import pyarrow as pa

```

## Creating datasets [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#creating-datasets "Link to this heading")

Via pyarrow it’s really easy to create lance datasets

Create a dataframe

```
df = pd.DataFrame({"a": [5]})
df

```

|  | a |
| --- | --- |
| 0 | 5 |

Write it to lance

```
shutil.rmtree("/tmp/test.lance", ignore_errors=True)

dataset = lance.write_dataset(df, "/tmp/test.lance")
dataset.to_table().to_pandas()

```

|  | a |
| --- | --- |
| 0 | 5 |

### Converting from parquet [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#converting-from-parquet "Link to this heading")

```
shutil.rmtree("/tmp/test.parquet", ignore_errors=True)
shutil.rmtree("/tmp/test.lance", ignore_errors=True)

tbl = pa.Table.from_pandas(df)
pa.dataset.write_dataset(tbl, "/tmp/test.parquet", format='parquet')

parquet = pa.dataset.dataset("/tmp/test.parquet")
parquet.to_table().to_pandas()

```

|  | a |
| --- | --- |
| 0 | 5 |

Write to lance in 1 line

```
dataset = lance.write_dataset(parquet, "/tmp/test.lance")

```

```
# make sure it's the same
dataset.to_table().to_pandas()

```

|  | a |
| --- | --- |
| 0 | 5 |

## Versioning [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#versioning "Link to this heading")

We can append rows

```
df = pd.DataFrame({"a": [10]})
tbl = pa.Table.from_pandas(df)
dataset = lance.write_dataset(tbl, "/tmp/test.lance", mode="append")

dataset.to_table().to_pandas()

```

|  | a |
| --- | --- |
| 0 | 5 |
| 1 | 10 |

We can overwrite the data and create a new version

```
df = pd.DataFrame({"a": [50, 100]})
tbl = pa.Table.from_pandas(df)
dataset = lance.write_dataset(tbl, "/tmp/test.lance", mode="overwrite")

```

```
dataset.to_table().to_pandas()

```

|  | a |
| --- | --- |
| 0 | 50 |
| 1 | 100 |

The old version is still there

```
dataset.versions()

```

```
[{'version': 1,\
  'timestamp': datetime.datetime(2024, 8, 15, 21, 22, 31, 453453),\
  'metadata': {}},\
 {'version': 2,\
  'timestamp': datetime.datetime(2024, 8, 15, 21, 22, 35, 475152),\
  'metadata': {}},\
 {'version': 3,\
  'timestamp': datetime.datetime(2024, 8, 15, 21, 22, 45, 32922),\
  'metadata': {}}]

```

```
lance.dataset('/tmp/test.lance', version=1).to_table().to_pandas()

```

|  | a |
| --- | --- |
| 0 | 5 |

```
lance.dataset('/tmp/test.lance', version=2).to_table().to_pandas()

```

|  | a |
| --- | --- |
| 0 | 5 |
| 1 | 10 |

We can create tags

```
dataset.tags.create("stable", 2)
dataset.tags.create("nightly", 3)
dataset.tags.list()

```

```
{'nightly': {'version': 3, 'manifest_size': 628},
 'stable': {'version': 2, 'manifest_size': 684}}

```

which can be checked out

```
lance.dataset('/tmp/test.lance', version="stable").to_table().to_pandas()

```

|  | a |
| --- | --- |
| 0 | 5 |
| 1 | 10 |

## Vectors [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#vectors "Link to this heading")

### Data preparation [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#data-preparation "Link to this heading")

For this tutorial let’s use the Sift 1M dataset:

- Download `ANN_SIFT1M` from: [http://corpus-texmex.irisa.fr/](http://corpus-texmex.irisa.fr/)

- Direct link should be
`ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz`

- Download and then unzip the tarball


```
!rm -rf sift* vec_data.lance
!wget ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz
!tar -xzf sift.tar.gz

```

```
--2023-02-13 16:54:50--  ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz
           => ‘sift.tar.gz’
Resolving ftp.irisa.fr (ftp.irisa.fr)... 131.254.254.45
Connecting to ftp.irisa.fr (ftp.irisa.fr)|131.254.254.45|:21... connected.
Logging in as anonymous ... Logged in!
==> SYST ... done.    ==> PWD ... done.
==> TYPE I ... done.  ==> CWD (1) /local/texmex/corpus ... done.
==> SIZE sift.tar.gz ... 168280445
==> PASV ... done.    ==> RETR sift.tar.gz ... done.
Length: 168280445 (160M) (unauthoritative)

sift.tar.gz         100%[===================>] 160.48M  6.85MB/s    in 36s

2023-02-13 16:55:29 (4.43 MB/s) - ‘sift.tar.gz’ saved [168280445]

```

Convert it to Lance

```
from lance.vector import vec_to_table
import struct

uri = "vec_data.lance"

with open("sift/sift_base.fvecs", mode="rb") as fobj:
    buf = fobj.read()
    data = np.array(struct.unpack("<128000000f", buf[4 : 4 + 4 * 1000000 * 128])).reshape((1000000, 128))
    dd = dict(zip(range(1000000), data))

table = vec_to_table(dd)
lance.write_dataset(table, uri, max_rows_per_group=8192, max_rows_per_file=1024*1024)

```

```
<lance.dataset.LanceDataset at 0x13859fe20>

```

```
uri = "vec_data.lance"
sift1m = lance.dataset(uri)

```

### KNN (no index) [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#knn-no-index "Link to this heading")

Sample 100 vectors as query vectors

```
import duckdb
# if this segfaults make sure duckdb v0.7+ is installed
samples = duckdb.query("SELECT vector FROM sift1m USING SAMPLE 100").to_df().vector
samples

```

```
0     [29.0, 10.0, 1.0, 50.0, 7.0, 89.0, 95.0, 51.0,...\
1     [7.0, 5.0, 39.0, 49.0, 17.0, 12.0, 83.0, 117.0...\
2     [0.0, 0.0, 0.0, 10.0, 12.0, 31.0, 6.0, 0.0, 0....\
3     [0.0, 2.0, 9.0, 1.793662034335766e-43, 30.0, 1...\
4     [54.0, 112.0, 16.0, 0.0, 0.0, 7.0, 112.0, 44.0...\
                            ...\
95    [1.793662034335766e-43, 33.0, 47.0, 28.0, 0.0,...\
96    [1.0, 4.0, 2.0, 32.0, 3.0, 7.0, 119.0, 116.0, ...\
97    [17.0, 46.0, 12.0, 0.0, 0.0, 3.0, 23.0, 58.0, ...\
98    [0.0, 11.0, 30.0, 14.0, 34.0, 7.0, 0.0, 0.0, 1...\
99    [20.0, 8.0, 121.0, 98.0, 37.0, 77.0, 9.0, 18.0...\
Name: vector, Length: 100, dtype: object\
\
```\
\
Call nearest neighbors (no ANN index here)\
\
```\
import time\
\
start = time.time()\
tbl = sift1m.to_table(columns=["id"], nearest={"column": "vector", "q": samples[0], "k": 10})\
end = time.time()\
\
print(f"Time(sec): {end-start}")\
print(tbl.to_pandas())\
\
```\
\
```\
Time(sec): 0.10735273361206055\
       id                                             vector    score\
0  144678  [29.0, 10.0, 1.0, 50.0, 7.0, 89.0, 95.0, 51.0,...      0.0\
1  575538  [2.0, 0.0, 1.0, 42.0, 3.0, 38.0, 152.0, 27.0, ...  76908.0\
2  241428  [11.0, 0.0, 2.0, 118.0, 11.0, 108.0, 116.0, 21...  92877.0\
3  220788  [0.0, 0.0, 0.0, 95.0, 0.0, 8.0, 133.0, 67.0, 1...  93305.0\
4  833796  [1.0, 1.0, 0.0, 23.0, 11.0, 26.0, 140.0, 115.0...  95721.0\
5  919065  [1.0, 1.0, 1.0, 42.0, 96.0, 42.0, 126.0, 83.0,...  96632.0\
6  741948  [36.0, 9.0, 15.0, 108.0, 17.0, 23.0, 25.0, 55....  96927.0\
7  225303  [0.0, 0.0, 3.0, 41.0, 0.0, 2.0, 36.0, 84.0, 68...  97055.0\
8  787098  [4.0, 5.0, 7.0, 29.0, 7.0, 1.0, 9.0, 91.0, 33....  97950.0\
9  113073  [0.0, 0.0, 0.0, 64.0, 65.0, 30.0, 12.0, 33.0, ...  99572.0\
\
```\
\
Without the index this is scanning through the whole dataset to compute\
the distance.\
\
For real-time serving we can do much better with an ANN index\
\
### Build index [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#build-index "Link to this heading")\
\
Now let’s build an index. Lance now supports IVF\_PQ, IVF\_HNSW\_PQ and\
IVF\_HNSW\_SQ indexes\
\
**NOTE** If you’d rather not wait for index build, you can download a\
version with the index pre-built from\
[here](https://eto-public.s3.us-west-2.amazonaws.com/datasets/sift/sift_ivf256_pq16.tar.gz)\
and skip the next cell\
\
```\
%%time\
\
sift1m.create_index(\
    "vector",\
    index_type="IVF_PQ", # IVF_PQ, IVF_HNSW_PQ and IVF_HNSW_SQ are supported\
    num_partitions=256,  # IVF\
    num_sub_vectors=16,  # PQ\
)\
\
```\
\
```\
Building vector index: IVF256,PQ16\
CPU times: user 2min 23s, sys: 2.77 s, total: 2min 26s\
Wall time: 22.7 s\
Sample 65536 out of 1000000 to train kmeans of 128 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
Sample 65536 out of 1000000 to train kmeans of 8 dim, 256 clusters\
\
```\
\
**NOTE** If you’re trying this on your own data, make sure your vector\
(dimensions / num\_sub\_vectors) % 8 == 0, or else index creation will\
take much longer than expected due to SIMD misalignment\
\
### Try nearest neighbors again with ANN index [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#try-nearest-neighbors-again-with-ann-index "Link to this heading")\
\
Let’s look for nearest neighbors again\
\
```\
sift1m = lance.dataset(uri)\
\
```\
\
```\
import time\
\
tot = 0\
for q in samples:\
    start = time.time()\
    tbl = sift1m.to_table(nearest={"column": "vector", "q": q, "k": 10})\
    end = time.time()\
    tot += (end - start)\
\
print(f"Avg(sec): {tot / len(samples)}")\
print(tbl.to_pandas())\
\
```\
\
```\
Avg(sec): 0.0009334301948547364\
       id                                             vector         score\
0  378825  [20.0, 8.0, 121.0, 98.0, 37.0, 77.0, 9.0, 18.0...  16560.197266\
1  143787  [11.0, 24.0, 122.0, 122.0, 53.0, 4.0, 0.0, 3.0...  61714.941406\
2  356895  [0.0, 14.0, 67.0, 122.0, 83.0, 23.0, 1.0, 0.0,...  64147.218750\
3  535431  [9.0, 22.0, 118.0, 118.0, 4.0, 5.0, 4.0, 4.0, ...  69092.593750\
4  308778  [1.0, 7.0, 48.0, 123.0, 73.0, 36.0, 8.0, 4.0, ...  69131.812500\
5  222477  [14.0, 73.0, 39.0, 4.0, 16.0, 94.0, 19.0, 8.0,...  69244.195312\
6  672558  [2.0, 1.0, 0.0, 11.0, 36.0, 23.0, 7.0, 10.0, 0...  70264.828125\
7  365538  [54.0, 43.0, 97.0, 59.0, 34.0, 17.0, 10.0, 15....  70273.710938\
8  659787  [10.0, 9.0, 23.0, 121.0, 38.0, 26.0, 38.0, 9.0...  70374.703125\
9  603930  [32.0, 32.0, 122.0, 122.0, 70.0, 4.0, 15.0, 12...  70583.375000\
\
```\
\
**NOTE** on performance, your actual numbers will vary by your storage.\
These numbers are run on local disk on an M2 Macbook Air. If you’re\
querying S3 directly, HDD, or network drives, performance will be\
slower.\
\
The latency vs recall is tunable via: - nprobes: how many IVF partitions\
to search - refine\_factor: determines how many vectors are retrieved\
during re-ranking\
\
```\
%%time\
\
sift1m.to_table(\
    nearest={\
        "column": "vector",\
        "q": samples[0],\
        "k": 10,\
        "nprobes": 10,\
        "refine_factor": 5,\
    }\
).to_pandas()\
\
```\
\
```\
CPU times: user 2.53 ms, sys: 3.31 ms, total: 5.84 ms\
Wall time: 4.18 ms\
\
```\
\
|  | id | vector | score |\
| --- | --- | --- | --- |\
| 0 | 144678 | \[29.0, 10.0, 1.0, 50.0, 7.0, 89.0, 95.0, 51.0,... | 0.0 |\
| 1 | 575538 | \[2.0, 0.0, 1.0, 42.0, 3.0, 38.0, 152.0, 27.0, ... | 76908.0 |\
| 2 | 241428 | \[11.0, 0.0, 2.0, 118.0, 11.0, 108.0, 116.0, 21... | 92877.0 |\
| 3 | 220788 | \[0.0, 0.0, 0.0, 95.0, 0.0, 8.0, 133.0, 67.0, 1... | 93305.0 |\
| 4 | 833796 | \[1.0, 1.0, 0.0, 23.0, 11.0, 26.0, 140.0, 115.0... | 95721.0 |\
| 5 | 919065 | \[1.0, 1.0, 1.0, 42.0, 96.0, 42.0, 126.0, 83.0,... | 96632.0 |\
| 6 | 741948 | \[36.0, 9.0, 15.0, 108.0, 17.0, 23.0, 25.0, 55.... | 96927.0 |\
| 7 | 225303 | \[0.0, 0.0, 3.0, 41.0, 0.0, 2.0, 36.0, 84.0, 68... | 97055.0 |\
| 8 | 787098 | \[4.0, 5.0, 7.0, 29.0, 7.0, 1.0, 9.0, 91.0, 33.... | 97950.0 |\
| 9 | 113073 | \[0.0, 0.0, 0.0, 64.0, 65.0, 30.0, 12.0, 33.0, ... | 99572.0 |\
\
q => sample vector\
\
k => how many neighbors to return\
\
nprobes => how many partitions (in the coarse quantizer) to probe\
\
refine\_factor => controls “re-ranking”. If k=10 and refine\_factor=5 then\
retrieve 50 nearest neighbors by ANN and re-sort using actual distances\
then return top 10. This improves recall without sacrificing performance\
too much\
\
**NOTE** the latencies above include file io as lance currently doesn’t\
hold anything in memory. Along with index building speed, creating a\
purely in memory version of the dataset would make the biggest impact on\
performance.\
\
### Features and vector can be retrieved together [¶](https://lancedb.github.io/lance/notebooks/quickstart.html\#features-and-vector-can-be-retrieved-together "Link to this heading")\
\
Usually we have other feature or metadata columns that need to be stored\
and fetched together. If you’re managing data and the index separately,\
you have to do a bunch of annoying plumbing to put stuff together. With\
Lance it’s a single call\
\
```\
tbl = sift1m.to_table()\
tbl = tbl.append_column("item_id", pa.array(range(len(tbl))))\
tbl = tbl.append_column("revenue", pa.array((np.random.randn(len(tbl))+5)*1000))\
tbl.to_pandas()\
\
```\
\
|  | id | vector | item\_id | revenue |\
| --- | --- | --- | --- | --- |\
| 0 | 0 | \[0.0, 16.0, 35.0, 5.0, 32.0, 31.0, 14.0, 10.0,... | 0 | 5950.436925 |\
| 1 | 1 | \[1.8e-43, 14.0, 35.0, 19.0, 20.0, 3.0, 1.0, 13... | 1 | 4680.298627 |\
| 2 | 2 | \[33.0, 1.8e-43, 0.0, 1.0, 5.0, 3.0, 44.0, 40.0... | 2 | 5342.593212 |\
| 3 | 3 | \[23.0, 10.0, 1.8e-43, 12.0, 47.0, 14.0, 25.0, ... | 3 | 5080.994002 |\
| 4 | 4 | \[27.0, 29.0, 21.0, 1.8e-43, 1.0, 1.0, 0.0, 0.0... | 4 | 4977.299308 |\
| ... | ... | ... | ... | ... |\
| 999995 | 999995 | \[8.0, 9.0, 5.0, 0.0, 10.0, 39.0, 72.0, 68.0, 3... | 999995 | 4928.768010 |\
| 999996 | 999996 | \[3.0, 28.0, 55.0, 29.0, 35.0, 12.0, 1.0, 2.0, ... | 999996 | 5056.264199 |\
| 999997 | 999997 | \[0.0, 13.0, 41.0, 72.0, 40.0, 9.0, 0.0, 0.0, 0... | 999997 | 5930.547635 |\
| 999998 | 999998 | \[41.0, 121.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 24... | 999998 | 5985.139759 |\
| 999999 | 999999 | \[2.0, 4.0, 8.0, 8.0, 26.0, 72.0, 63.0, 0.0, 0.... | 999999 | 5008.962686 |\
\
1000000 rows × 4 columns\
\
```\
sift1m = lance.write_dataset(tbl, uri, mode="overwrite")\
\
```\
\
```\
sift1m.to_table(columns=["revenue"], nearest={"column": "vector", "q": samples[0], "k": 10}).to_pandas()\
\
```\
\
|  | revenue | vector | score |\
| --- | --- | --- | --- |\
| 0 | 2994.968781 | \[29.0, 10.0, 1.0, 50.0, 7.0, 89.0, 95.0, 51.0,... | 0.0 |\
| 1 | 4231.026305 | \[2.0, 0.0, 1.0, 42.0, 3.0, 38.0, 152.0, 27.0, ... | 76908.0 |\
| 2 | 3340.900287 | \[11.0, 0.0, 2.0, 118.0, 11.0, 108.0, 116.0, 21... | 92877.0 |\
| 3 | 4339.588996 | \[0.0, 0.0, 0.0, 95.0, 0.0, 8.0, 133.0, 67.0, 1... | 93305.0 |\
| 4 | 5141.730799 | \[1.0, 1.0, 0.0, 23.0, 11.0, 26.0, 140.0, 115.0... | 95721.0 |\
| 5 | 4518.194820 | \[1.0, 1.0, 1.0, 42.0, 96.0, 42.0, 126.0, 83.0,... | 96632.0 |\
| 6 | 3383.586889 | \[36.0, 9.0, 15.0, 108.0, 17.0, 23.0, 25.0, 55.... | 96927.0 |\
| 7 | 5496.905675 | \[0.0, 0.0, 3.0, 41.0, 0.0, 2.0, 36.0, 84.0, 68... | 97055.0 |\
| 8 | 5298.669719 | \[4.0, 5.0, 7.0, 29.0, 7.0, 1.0, 9.0, 91.0, 33.... | 97950.0 |\
| 9 | 6742.810395 | \[0.0, 0.0, 0.0, 64.0, 65.0, 30.0, 12.0, 33.0, ... | 99572.0 |