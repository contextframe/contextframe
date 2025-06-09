---
url: "https://lancedb.github.io/lance/integrations/spark.html"
title: "Lance ❤️ Spark - Lance  documentation"
---

[Skip to content](https://lancedb.github.io/lance/integrations/spark.html#build-from-source-code)

# Lance ❤️ Spark [¶](https://lancedb.github.io/lance/integrations/spark.html\#lance-spark "Link to this heading")

Lance can be used as a third party datasource of [https://spark.apache.org/docs/latest/sql-data-sources.html](https://spark.apache.org/docs/latest/sql-data-sources.html)

Warning

This feature is experimental and the APIs may change in the future.

## Build from source code [¶](https://lancedb.github.io/lance/integrations/spark.html\#build-from-source-code "Link to this heading")

```
git clone https://github.com/lancedb/lance.git
cd lance/java
mvn clean package -DskipTests -Drust.release.build=true

```

After building the code, the spark related jars are under path `lance/java/spark/target/jars/`

```
arrow-c-data-15.0.0.jar
arrow-dataset-15.0.0.jar
jar-jni-1.1.1.jar
lance-core-0.25.0-SNAPSHOT.jar
lance-spark-0.25.0-SNAPSHOT.jar

```

## Download the pre-build jars [¶](https://lancedb.github.io/lance/integrations/spark.html\#download-the-pre-build-jars "Link to this heading")

If you did not want to get jars from source, you can download these five jars from maven repo.

```
wget https://repo1.maven.org/maven2/com/lancedb/lance-core/0.23.0/lance-core-0.23.0.jar
wget https://repo1.maven.org/maven2/com/lancedb/lance-spark/0.23.0/lance-spark-0.23.0.jar
wget https://repo1.maven.org/maven2/org/questdb/jar-jni/1.1.1/jar-jni-1.1.1.jar
wget https://repo1.maven.org/maven2/org/apache/arrow/arrow-c-data/12.0.1/arrow-c-data-12.0.1.jar
wget https://repo1.maven.org/maven2/org/apache/arrow/arrow-dataset/12.0.1/arrow-dataset-12.0.1.jar

```

## Configurations for Lance Spark Connector [¶](https://lancedb.github.io/lance/integrations/spark.html\#configurations-for-lance-spark-connector "Link to this heading")

There are some configurations you have to set in `spark-defaults.conf` to enable lance datasource.

```
spark.sql.catalog.lance com.lancedb.lance.spark.LanceCatalog

```

This config define the LanceCatalog and then the spark will treat lance as a datasource.

If dealing with lance dataset stored in object store, these configurations should be set:

```
spark.sql.catalog.lance.access_key_id {your object store ak}
spark.sql.catalog.lance.secret_access_key {your object store sk}
spark.sql.catalog.lance.aws_region {your object store region(optional)}
spark.sql.catalog.lance.aws_endpoint {your object store aws_endpoint which should be in virtual host style}
spark.sql.catalog.lance.virtual_hosted_style_request true

```

## Startup the Spark Shell [¶](https://lancedb.github.io/lance/integrations/spark.html\#startup-the-spark-shell "Link to this heading")

```
bin/spark-shell --master "local[56]"  --jars "/path_of_code/lance/java/spark/target/jars/*.jar"

```

Use `--jars` to involve the related jars we build or downloaded.

Note

Spark shell console use `scala` language not `python`

## Using Spark Shell to manipulate lance dataset [¶](https://lancedb.github.io/lance/integrations/spark.html\#using-spark-shell-to-manipulate-lance-dataset "Link to this heading")

- Write a new dataset named `test.lance`


```
val df = Seq(
  ("Alice", 1),
  ("Bob", 2)
).toDF("name", "id")
df.write.format("lance").option("path","./test.lance").save()

```

- Overwrite the `test.lance` dataset


```
val df = Seq(
  ("Alice", 3),
  ("Bob", 4)
).toDF("name", "id")
df.write.format("lance").option("path","./test.lance").mode("overwrite").save()

```

- Append Data into the `test.lance` dataset


```
val df = Seq(
  ("Chris", 5),
  ("Derek", 6)
).toDF("name", "id")
df.write.format("lance").option("path","./test.lance").mode("append").save()

```

- Use spark data frame to read the `test.lance` dataset


```
val data = spark.read.format("lance").option("path", "./test.lance").load();
data.show()

```

- Register data frame as table and use sql to query `test.lance` dataset


```
data.createOrReplaceTempView("lance_table")
spark.sql("select id, count(*) from lance_table group by id order by id").show()

```