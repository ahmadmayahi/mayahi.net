Typing `mysql -u user -p` asks us to provide the password, but the shell sometimes needs to be non-interactive.

Imagine a case where you need to take a complete backup of your database every night, and transfer it to S3; then how would you provide the MySQL password?

You can do something like this:
```bash
mysqldump -u user -p password my_database > mydatabase.dump
```

Typing the password as an argument is insecure because it leads to exposing the password in the `.bash_history`:
```bash
less /root/.bash_history
mysqldump -u user -p password my_database > mydatabase.dump
```

We can fix this issue by creating a local file named `.my.cnf` in the current user’s directory.

To be safe, I usually create a backup user `bkp` and protect the `.my.cnf` so only the `bkp`  can read/write to it:
```php
cd /home/bkp
touch .my.cnf
chmod u=rw,go-rwx .my.cnf
```

Lastly, open up the `.my.cnf` file and type the password as follows:
```bash
[client]
user=mysql_user
password="password"
default-character-set=utf8mb4
```

Now you can access `mysql` and `mysqldump` without password:
```bash
bkp@myserver:~# mysql
mysql> show databases;
...
```

That’s it. 🥳