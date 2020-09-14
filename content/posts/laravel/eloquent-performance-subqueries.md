In the [previous post](../eloquent-performance-eager-loading/), I asked a the following question:

> **How can you get the latest login date from `App\Models\User` in an efficient way?**

The short answer is by using the subqueries.

Subquery is a query within another query, and it's supported by most RDBMS such as [MySQL](https://www.mysqltutorial.org/mysql-subquery/), [Postgres](https://www.postgresqltutorial.com/postgresql-subquery/) etc.

Let's demystify this by an example:
```sql
SELECT
    `users`.*,
    (
        SELECT
            COUNT(id)
        FROM
            `posts`
        WHERE
            `user_id` = `users`.`id`
        LIMIT 1) AS `total_posts`
FROM
    `users`
ORDER BY
    `total_posts` DESC
LIMIT 15 OFFSET 0
```

The above query will count the total number of posts for each user, so we don't need to have another `SELECT COUNT()...` statement.

Laravel supports subqueries through the `addSelect` method:
```php
$users = User::query()
    ->addSelect([
        'total_posts' => Post::selectRaw('COUNT(*)')
            ->whereColumn('user_id', '=', 'users.id')
            ->take(1)
    ])
    ->orderBy('total_posts', 'desc')
    ->paginate();
```

> Remember to join the tables correctly when using subqueries.

We've got a new column `total_posts` in the `App\Models\User`, that's amazing, isn't it?

Let me show you one more thing before I end this section.

It's better to move your subqueries into scopes, so you will have great control over them:
```php
// App\Models\Post

public function scopeWithTotalPosts()
{
    $users = User::query()
        ->addSelect([
            'total_posts' => Post::selectRaw('COUNT(*)')
                ->whereColumn('user_id', '=', 'users.id')
                ->take(1)
        ])
        ->orderBy('total_posts', 'desc')
        ->paginate();
}
```

You can easily call the scope as follows:
```php
User::withTotalPosts()->paginate();
```

## Getting the latest login date using subquery
Now you know how to use subqueries in Laravel, this means that you can apply the same thing to get the latest login date.

Let's see how it's done:
```php
// App\Models\User

public function scopeWithLatestLoginDate($query)
{
    $query->addSelect(['latest_login_date' => Login::select('created_at')
            ->whereColumn('user_id', 'users.id')
            ->latest()
            ->take(1)
        ])
        ->withCasts(['last_login_at' => 'datetime']);
}
```

```php
// App\Http\Controllers\UsersController

$users = User::query()
    ->withLatestLoginDate()
    ->paginate(10);
```

Now, you can access the `latest_login_date` directly from the `App\Models\User`:
```blade
@foreach ($users as $user) {
    {{ $user->last_login_at->diffForHumans() }}
}
```

> The `latest_login_date` is an instance of `Illuminate\Support\Carbon` and that's because it was casted using the `withCasts` method.
 
In the next [upcoming post](../eloquent-performance-fake-relationships/), I will discuss the fake relationships using subqueries.