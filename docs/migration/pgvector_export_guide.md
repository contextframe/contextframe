# pgvector Export and Migration Guide

## Overview

pgvector is an open-source PostgreSQL extension that enables efficient storage and similarity search for vector embeddings. This guide covers pgvector's capabilities, export methods, and best practices for working with vector data in PostgreSQL.

## Table of Contents

1. [pgvector Installation and Setup](#installation)
2. [Vector Data Types and Operations](#data-types)
3. [Index Types and Performance](#indexes)
4. [Export Methods](#export-methods)
5. [Python Integration](#python-integration)
6. [Performance Best Practices](#performance)

## Installation and Setup {#installation}

### Installing pgvector

#### Ubuntu/Debian
```bash
# Install from PostgreSQL APT repository
sudo apt install postgresql-16-pgvector

# Or compile from source
cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

#### macOS (Homebrew)
```bash
brew install pgvector
```

#### Docker
```bash
docker run -d \
  --name pgvector-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

### Enable Extension
```sql
CREATE EXTENSION vector;
```

## Vector Data Types and Operations {#data-types}

### Supported Vector Types

pgvector supports multiple vector types:
- **vector**: Single-precision vectors (default)
- **halfvec**: Half-precision vectors (16-bit floats)
- **sparsevec**: Sparse vectors
- **bit**: Binary vectors

### Creating Tables with Vectors

```sql
-- Create table with 1536-dimensional vectors (e.g., OpenAI embeddings)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table with half-precision vectors for memory efficiency
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    image_url TEXT,
    embedding halfvec(512)
);
```

### Distance Functions

pgvector supports six distance operators:

| Operator | Description | Best For |
|----------|-------------|----------|
| `<->` | L2 (Euclidean) distance | General similarity, clustering |
| `<#>` | Negative inner product | Normalized vectors (e.g., OpenAI) |
| `<=>` | Cosine distance | Document similarity, NLP |
| `<+>` | L1 (Manhattan) distance | Sparse data |
| `<~>` | Hamming distance | Binary vectors |
| `<%>` | Jaccard distance | Set similarity |

### Query Examples

```sql
-- Find 10 most similar documents using cosine distance
SELECT id, content, embedding <=> '[0.1, 0.2, ...]'::vector AS distance
FROM documents
ORDER BY distance
LIMIT 10;

-- Filter by metadata and similarity
SELECT id, content, embedding <-> query_vector AS distance
FROM documents
WHERE metadata->>'category' = 'technical'
ORDER BY distance
LIMIT 5;
```

## Index Types and Performance {#indexes}

### IVFFlat Index

IVFFlat (Inverted File with Flat compression) divides vectors into clusters:

```sql
-- Create IVFFlat index
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);

-- Set search parameters
SET ivfflat.probes = 50;  -- Number of clusters to search
```

**Guidelines:**
- Lists: `rows/1000` for <1M rows, `sqrt(rows)` for >1M rows
- Probes: Start with `sqrt(lists)`, increase for better recall

### HNSW Index

HNSW (Hierarchical Navigable Small Worlds) creates a multi-layer graph:

```sql
-- Create HNSW index
CREATE INDEX ON documents USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 200);

-- Set search parameters
SET hnsw.ef_search = 100;  -- Higher = better recall, slower search
```

**Guidelines:**
- m: 16-64 (higher = better recall, more memory)
- ef_construction: 200+ (higher = better quality, slower build)
- ef_search: 50-500 (tune based on recall needs)

### Index Comparison

| Aspect | IVFFlat | HNSW |
|--------|---------|------|
| Build Speed | Fast | Slower |
| Memory Usage | Lower | Higher |
| Query Speed | Moderate | Fast |
| Recall | Good | Excellent |
| Best For | Large datasets, frequent updates | Static datasets, high accuracy |

## Export Methods {#export-methods}

### 1. Using pg_dump

For complete database backup including vector data:

```bash
# Backup database with pgvector data
pg_dump -h localhost -U postgres -d mydb > backup.sql

# Backup specific tables
pg_dump -h localhost -U postgres -d mydb -t documents -t images > vectors_backup.sql

# Compress large backups
pg_dump -h localhost -U postgres -d mydb | gzip > backup.sql.gz
```

**Important for restore:**
```sql
-- Create extension before restore
CREATE EXTENSION vector;
```

### 2. COPY Command (Fastest for Bulk Export)

```sql
-- Export to CSV
COPY (
    SELECT id, content, embedding::text, metadata
    FROM documents
    WHERE created_at > '2024-01-01'
) TO '/tmp/vectors.csv' WITH CSV HEADER;

-- Export with custom delimiter
COPY documents TO '/tmp/vectors.tsv' 
WITH (FORMAT csv, DELIMITER E'\t', HEADER true);

-- Export to stdout (for piping)
COPY documents TO STDOUT WITH (FORMAT csv);
```

### 3. Binary COPY (Most Efficient)

```sql
-- Export in binary format (smaller, faster)
COPY documents TO '/tmp/vectors.bin' WITH (FORMAT binary);

-- Import binary data
COPY documents FROM '/tmp/vectors.bin' WITH (FORMAT binary);
```

### 4. Paginated Export for Large Datasets

```sql
-- Export in chunks using OFFSET/LIMIT
DO $$
DECLARE
    batch_size INT := 10000;
    offset_val INT := 0;
    total_rows INT;
BEGIN
    SELECT COUNT(*) INTO total_rows FROM documents;
    
    WHILE offset_val < total_rows LOOP
        EXECUTE format(
            'COPY (SELECT * FROM documents ORDER BY id LIMIT %s OFFSET %s) 
             TO ''/tmp/batch_%s.csv'' WITH CSV HEADER',
            batch_size, offset_val, offset_val / batch_size
        );
        offset_val := offset_val + batch_size;
    END LOOP;
END $$;
```

### 5. Streaming Export with CURSOR

```sql
BEGIN;
DECLARE vector_cursor CURSOR FOR 
    SELECT * FROM documents ORDER BY id;

-- Fetch in batches
FETCH 1000 FROM vector_cursor;
```

## Python Integration {#python-integration}

### Using psycopg3

```python
import psycopg
import numpy as np
from psycopg.adapt import register_vector

# Register vector type
psycopg.adapters.register_vector(psycopg.adapters.types)

# Connect to database
conn = psycopg.connect(
    "postgresql://user:password@localhost/dbname",
    row_factory=psycopg.rows.dict_row
)

# Export vectors with pagination
def export_vectors_paginated(conn, batch_size=10000):
    with conn.cursor() as cur:
        offset = 0
        while True:
            cur.execute("""
                SELECT id, content, embedding, metadata
                FROM documents
                ORDER BY id
                LIMIT %s OFFSET %s
            """, (batch_size, offset))
            
            rows = cur.fetchall()
            if not rows:
                break
                
            yield rows
            offset += batch_size

# Efficient bulk export using COPY
def export_to_file(conn, filename):
    with conn.cursor() as cur:
        with open(filename, 'w') as f:
            cur.copy_expert(
                "COPY documents TO STDOUT WITH CSV HEADER",
                f
            )

# Export with binary format for efficiency
def export_binary(conn, filename):
    with conn.cursor() as cur:
        with open(filename, 'wb') as f:
            cur.copy_expert(
                "COPY documents TO STDOUT WITH (FORMAT BINARY)",
                f
            )
```

### Using asyncpg (Async)

```python
import asyncpg
import asyncio

async def export_vectors_async():
    conn = await asyncpg.connect(
        'postgresql://user:password@localhost/dbname'
    )
    
    # Use server-side cursor for memory efficiency
    async with conn.transaction():
        async for record in conn.cursor(
            'SELECT * FROM documents ORDER BY id'
        ):
            # Process each record
            yield record
    
    await conn.close()

# Parallel export using multiple connections
async def parallel_export(num_workers=4):
    async def export_partition(conn, partition_id, num_partitions):
        query = """
            SELECT * FROM documents 
            WHERE id % $1 = $2
            ORDER BY id
        """
        return await conn.fetch(query, num_partitions, partition_id)
    
    # Create connection pool
    pool = await asyncpg.create_pool(
        'postgresql://user:password@localhost/dbname',
        min_size=num_workers,
        max_size=num_workers
    )
    
    tasks = []
    for i in range(num_workers):
        conn = await pool.acquire()
        task = export_partition(conn, i, num_workers)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    await pool.close()
    
    return results
```

### Using pgvector-python

```python
from pgvector.psycopg import register_vector
import psycopg

# Register vector type
conn = psycopg.connect("postgresql://localhost/mydb")
register_vector(conn)

# Query with vector operations
cur = conn.cursor()
cur.execute("""
    SELECT id, embedding <-> %s AS distance
    FROM documents
    ORDER BY distance
    LIMIT 10
""", ([0.1, 0.2, 0.3],))

results = cur.fetchall()
```

## Performance Best Practices {#performance}

### 1. Bulk Loading Optimization

```sql
-- Disable indexes during bulk load
ALTER TABLE documents DROP INDEX documents_embedding_idx;

-- Use UNLOGGED table for initial load
ALTER TABLE documents SET UNLOGGED;

-- Load data
COPY documents FROM '/tmp/data.csv' WITH CSV;

-- Convert back to logged and rebuild index
ALTER TABLE documents SET LOGGED;
CREATE INDEX documents_embedding_idx ON documents 
USING hnsw (embedding vector_cosine_ops);
```

### 2. Parallel Loading

```bash
# Split large file
split -l 100000 data.csv chunk_

# Load in parallel
for file in chunk_*; do
    psql -d mydb -c "\COPY documents FROM '$file' WITH CSV" &
done
wait
```

### 3. Memory and Configuration Tuning

```sql
-- Increase work memory for index creation
SET maintenance_work_mem = '4GB';

-- Optimize for bulk operations
SET synchronous_commit = OFF;
SET checkpoint_segments = 100;
SET checkpoint_completion_target = 0.9;

-- For COPY operations
SET wal_level = minimal;
SET max_wal_senders = 0;
```

### 4. Export Performance Tips

1. **Use COPY instead of SELECT**: 10-100x faster for bulk exports
2. **Binary format**: Reduces size by ~50% and speeds up I/O
3. **Compression**: Use gzip for network transfers
4. **Parallel export**: Split by ID ranges or hash partitioning
5. **Avoid ORDER BY**: Unless necessary, as it requires sorting
6. **Use UNLOGGED tables**: For temporary export staging

### 5. Monitoring Export Progress

```sql
-- Monitor long-running exports
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query
FROM pg_stat_activity
WHERE query LIKE '%COPY%'
AND state = 'active';

-- Check export size
SELECT 
    pg_size_pretty(pg_relation_size('documents')) AS table_size,
    count(*) AS row_count
FROM documents;
```

## Common Issues and Solutions

### Issue: pg_dump restore fails
**Solution**: Ensure `CREATE EXTENSION vector;` is run before restore

### Issue: Out of memory during export
**Solution**: Use cursor-based pagination or COPY with smaller batches

### Issue: Slow vector similarity queries
**Solution**: Create appropriate indexes and tune parameters

### Issue: Large export files
**Solution**: Use binary format and compression

## Summary

pgvector provides powerful vector similarity search capabilities within PostgreSQL. Key takeaways:

1. **Choose the right index**: IVFFlat for frequently updated data, HNSW for best query performance
2. **Use COPY for bulk operations**: Significantly faster than INSERT/SELECT
3. **Optimize for your use case**: Binary format for efficiency, CSV for compatibility
4. **Monitor and tune**: Adjust PostgreSQL settings and pgvector parameters based on workload
5. **Plan for scale**: Use pagination and parallel processing for large datasets

For production deployments, always test export and import procedures with representative data volumes to ensure acceptable performance.