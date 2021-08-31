`mysqldump` allows us to backup and easily restore our databases.

In this post, I will show you how to backup MySQL in an efficient way.

## Basic of mysqldump
You can easily backup your database using the following command:
```bash
mysqldump your_database > database.sql
```

To make the backup file smaller, we may compress it using `gzip` :
```bash
mysqldump mysql | gzip > database.sql.gz
```

`gzip` is a great tool, but it doesn't work properly on a multi-core system.

## pigz
An alternative tool to `gzip` is `pigz` which stands for **p**arallel **I**mplementation of **gz**ip.

`pigz` exploits multiple processors and multiple cores to the hilt when compressing data [[Source](https://zlib.net/pigz/)]:

```bash
sudo apt-get install -y pigz

mysqldump mysql | pigz > database.sql.gz
```

## Data Inconsistency 
Let's say that your database has `users` and `posts` tables, then what happens if the `users` table is dumped out, a new user is created before the `posts` table is dumped?

As you can probably tell, `mysqldump` will export inconsistent data, it will have a post related to a user that doesn't exist.

We can easily get around this issue by running the export operation within a transaction, which keeps our data inconsistent:
```bash
mysqldump -u your_user -p --single-transaction \
    --default-character-set=utf8mb4 \
    your_database | pigz > database.sql.gz
```

## Restore database
Let's see how to restore the database:
```bash
gunzip < database_file.sql.gz | mysql -u your_user -p your_database
```

That's it 🥳