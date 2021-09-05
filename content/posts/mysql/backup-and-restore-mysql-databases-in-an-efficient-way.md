`mysqldump` allows us to create logical backups of our databases, as well as restoring them.

A logical backup uses SQL statements to create the contents of the database, such as tables, views, triggers and inserts the data using the INSERT statement.

For example:

```sql
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email_verified_at` timestamp NULL DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `two_factor_secret` text COLLATE utf8mb4_unicode_ci,
  `two_factor_recovery_codes` text COLLATE utf8mb4_unicode_ci,
  `remember_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `current_team_id` bigint unsigned DEFAULT NULL,
  `profile_photo_path` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_email_unique` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `users` (`id`, `name`, `email`, `email_verified_at`, `password`, `two_factor_secret`, `two_factor_recovery_codes`, `remember_token`, `current_team_id`, `profile_photo_path`, `is_admin`, `created_at`, `updated_at`) VALUES
(1, 'Prof. Norwood Moen', 'moen@example.com', '2021-08-28 20:39:31', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', NULL, NULL, 'Ji0Eqw70n1', NULL, NULL, 1, '2021-08-28 20:39:31', '2021-08-28 20:39:31');
```

In this post, I will show you how to backup MySQL using `mysqldump` in an efficient way.

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