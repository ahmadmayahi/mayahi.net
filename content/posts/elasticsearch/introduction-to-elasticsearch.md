I used to work in a company where almost everything seemed to be difficult for our boss.

The boss was one of those old-school guys who stuck with their computer science degree and don’t want to move ahead.

You may ask, why am I talking about my ex-boss in an Elasticsearch post?

The application that we were building was using PostgresSQL to do some full-text searching, but guess what, the searching could take at least 30 seconds to complete, imagine, thirty seconds waiting to get a few results, that is insane.

The database was not normalized, and you’d join multiple tables to narrow down the results, even if you’d perform a simple search, much less full-text searching.

## What is Elasticsearch?
Elasticsearch is a highly-scalable open-source full-text search engine that is based on Apache Lucene.

Elasticsearch provides full-text search with an HTTP web interface and schema-free JSON, this means that you’d communicate with Elasticsearch servers by sending HTTP requests and parsing the HTTP responses (which are in JSON as well).

Elasticsearch has a numerous features:

- Highly optimized for searching; it uses some techniques that make searching blazing, such as analyzers, stemmers, etc…
- Built on top of Apache Lucene, an ultra-fast search library, this means that it uses the same indexing as Lucene.
- Uses Rest API: send json requests and get json responses, that’s it.
- Very fast.
- Easy to work with.

## Installing Elasticsearch
I’m not going to cover the installation process since it’s already described [here](https://www.elastic.co/downloads/elasticsearch).

Anyway, If you’re running Docker – as I do – then you may spin up an Elasticsearch container as follows:

```bash
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:7.8.0
```

Elasticsearch uses port 9200 for the REST API, so, let’s ensure that it’s up and running:

```bash
curl http://localhost:9200
```

```json
{
  "name" : "d1da3c443ba0",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "OqUjXWjgRDOln-_RXfNARA",
  "version" : {
    "number" : "7.8.0",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "757314695644ea9a1dc2fecd26d1a43856725e65",
    "build_date" : "2020-06-14T19:35:50.234439Z",
    "build_snapshot" : false,
    "lucene_version" : "8.5.1",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```

## Elasticsearch vs RDBMS
Now we have an Elasticsearch container up and running on our machine, but you may ask what the difference between Elasticsearch and other RDBMS such as MySQL?

Elasticsearch is a No-SQL database, this means that it doesn’t have relations, joins, and transactions as the RDBMS does.

> Elasticsearch does have sort of simple joining, I’ll cover that in the upcoming posts.

Elasticsearch is suitable for many different use cases:

- Highly optimized for searching.
- Scalable by default.
- Full-text searching in a big amount of data, where the relevance matters.
- Creating an autocomplete feature.
- Implementing the did-you-mean feature when entering misspelled words.
- Searching in external files, such as PDF, XLS, PPT, etc…
- Much more...

Elasticsearch uses text analysis to provide the best searching experience (I will describe how it does that later in this post).

Let’s say that you want to search for the word father but you also want to match dad, daddy, papa, parent, etc.. Elasticsearch can do that for you.

That was Elasticsearch, so, how about RDBMS?

If you want some of the RDBMS features such as transactions, then you definitely need to go for an RDBMS.

In most cases, you need a fast search engine as well as joins and transactions, that’s completely fine, you can have Elasticsearch running beside your RDBMS, but remember you do need to sync your data between Elasticsearch and your database.

Later in this post, I will show you how to use Laravel observers to achieve syncing.

## Elasticsearch Concepts
Let’s get familiar with the basic terms of Elasticsearch.

- Index: similar to the database’s table; An index can contain a collection of documents.
- Document: similar to the database’s record; A document is any structured JSON data.
- Field: same as the database’s field; Fields must-have types, such as long, date, byte, short, integer, etc…
- Multi-Fields: in contrast with databases, in Elasticsearch a field could have multiple fields with different data types (I will explain this later).
- Mapping: each field has to be mapped to a data type, the process of setting the appropriate data types is called mappings.
- Analyzer: breaks the text down into small searchable chunks.
- Shard: an index can be split into small chunks named “shards”; Shards can also be placed into different nodes (machines).

Let’s discuss these terms thorughly.

## Index
An index is nothing but a collection of documents.

The term index can also refer to storing data into Elasticsearch, so, I will use indexing data instead of storing data.

In Elasticsearch each index contains one or more shards (I will cover that soon).

Let’s see where does Elasticsearch store the indices by inspecting the folder structure:

```bash
docker exec -it elasticsearch sh
cd /usr/share/elasticsearch/data/nodes/0/indices
```

Elasticsearch stores all the indices in a folder named indices inside the nodes folder, but why nodes?

Remember I said that Elasticsearch is scalable by default, this means that you can easily scale it by adding more nodes into the cluster.

> Elasticsearch can only index text-based documents, if you want to index your PDF, PPT, XLS files, then consider using the Elasticsearch-Mapper-Attachments plugin (which is based on Apache Tika).

## Sharding
Since we’re learning Elasticsearch, it’s very important to know what the sharding is.

Imagine that you want to index 1 TB of data and you only have a single node with 500 GB of space, how could that fit then?

If you add an additional node with sufficient capacity, Elasticsearch can store data in both nodes, meaning that the cluster now has enough storage capacity.

Sharding is a way of dividing indices into smaller pieces, so each piece is referred to as a shard.

For example, an index of size 1 TB could be divided into four shards of sizes 250 GB and then spreading over four nodes.

> Sharding is done at the index level and not at the cluster or the node level.

Think of a shard as if it was a an independent index.

## Creating our first index
Elasticsearch provides an elegant REST API, you can use any HTTP client such as curl, postman, Insomnia, etc… in this post I will stick with cURL.

Let’s start by creating an index named “employees”:

```bash
curl -XPUT  'http://127.0.0.1:9200/employees?pretty'
```

> Appending pretty leads to returning a formatted JSON.

```json
{
    "acknowledged": true,
    "shards_acknowledged": true,
    "index": "employees"
}
```

You may need to get some information about an existing index:

```bash
curl -XGET  'http://127.0.0.1:9200/employees?pretty'
```

```json
{
    "employees": {
        "aliases": {},
        "mappings": {},
        "settings": {
            "index": {
                "creation_date": "1590765061412",
                "number_of_shards": "1",
                "number_of_replicas": "1",
                "uuid": "RVbipfdBSRG0SSLhLl0Ogg",
                "version": {
                    "created": "7070099"
                },
                "provided_name": "employees"
            }
        }
    }
}
```

Our index is ready now, let’s create some documents.

## Creating documents
Creating a document is as easy as creating an index.

All you need to do is to send some json data:

```bash
curl --location --request POST 'http://localhost:9200/employees/_doc' \
--header 'Content-Type: application/json' \
--data-raw '{
    "first_name": "Ahmad",
    "last_name": "Iraq",
    "birth_date": "1986-06-11"
}'
```

```json
{
    "_index": "employees",
    "_type": "_doc",
    "_id": "u_t_ZXIB2DKxG4ehFP57",
    "_version": 1,
    "result": "created",
    "_shards": {
        "total": 2,
        "successful": 1,
        "failed": 0
    },
    "_seq_no": 1,
    "_primary_term": 1
}
```

The document must have a unique id; therefore, Elasticsearch assigns an arbitrary id for the newly created document.

```bash
http://127.0.0.1:9200/employees/_doc/1
```

What if you want to get all the indexed documents?

```bash
curl --location --request GET 'http://localhost:9200/employees/_search'
```
```json
{
    "took": 1,
    "timed_out": false,
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 1.0,
        "hits": [
            {
                "_index": "employees",
                "_type": "_doc",
                "_id": "Q_uEZXIB2DKxG4ehof_Y",
                "_score": 1.0,
                "_source": {
                    "first_name": "Ahmad",
                    "last_name": "Iraq",
                    "birth_date": "1986-06-11"
                }
            }
        ]
    }
}
```

Don’t worry about this big document, I’ll get back to it soon.

Take a look at the `_source` key which contains the entire document that you indexed.

Repeat the same step to add more employees.


