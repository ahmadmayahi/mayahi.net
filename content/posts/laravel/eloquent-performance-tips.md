Unoptimized Eloquent queries make your project slower and expensive to run.

As a Laravel developer, you should always measure your Eloquent queries and make them fast and efficient.

Unfortunately, many Laravel developers use Eloquent without paying attention to some critcial parts and they end up writing slow and inefficient queries.

I will publish a few Eloquent optimization posts in the upcoming days where I show you some great solutions, so keep an eye on my blog 😄

In this post, I will introduce you to the Laravel debugger as well as explaining the N+1 problem.

## Database Diagram
During this post, I will be referring to the following diagram whenever I mention a model or a table:
 
![Database Diagram](./static/img/laravel/eloquent-performance/002.png)

You don't need to create all these tables, since the tips can be applied in any kind of project.  

## What is N+1 issue?
The N+1 issue is a common problem in [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping) systems such as [Eloquent](https://en.wikipedia.org/wiki/Object-relational_mapping).

Let's say that you want to iterate over a bunch of users and list all the posts for each individual one:
```text
John
    Post 1
    Post 2
    Post 3
    ...
Ahmad
    Post 1
    Post 2
    ...
Dania
    ...
```

Laravel implementation:
```php
// Controllers\UsersController

public function posts(User $user)
{
    return view('user.posts', ['users' => User::paginate()]);
}
```

```blade
<!-- users/posts.blade.php -->

@foreach ($users as $user)
    <h3>{{ $user->name }}</h3>
    <ul>
        @foreach ($user->posts as $post)
            <li>{{ $post->title }}</li>
        @endforeach
    </ul>
@endforeach
```

The above code introduced a **N+1 problem**, which means that we've issued one `SELECT` statement:
```sql
SELECT * FROM users;
```

And **N** (total number of posts) additional `SELECT` statements:
```sql
SELECT * FROM posts where user_id = 1;
SELECT * FROM posts where user_id = 2;
SELECT * FROM posts where user_id = 3;
# ...
```

In the upcoming posts I will show you some great tips to avoid N+1 problem as well as making your queries fast and efficient.

> Remember, your focus should be on reducing the time that the sql queries take to run, that's it.

## Tip 1: Laravel Debugger
[Laravel Debugger](https://github.com/barryvdh/laravel-debugbar) is a great tool for measuring your database performance as well as debugging some other application layers.

> If you are already familiar with Laravel Debugger, then we may want to skip this part.

In case you haven't installed it yet:
```bash
composer require barryvdh/laravel-debugbar --dev
```

Head up to your application and you'll see a very nice debug bar. 

![Laravel Debugger](./static/img/laravel/eloquent-performance/001.png)

Since we're dealing with database, you must pay attention to the **Queries** and **Models** tabs:

* **Queries**: Executed queries on the current route.
* **Models**: Loaded models on the current route.

You should also pay attention to the execution time:

* **Queries Execution Time**: How long did it take to execute all the queries?
* **Page Load Time**: How long did it take to load the entire page?


Let's get our hands dirty by running the following query within a controller:
```php
// App\Http\Controllers\UsersController

User::take(10)->get();
``` 

If you inspect the **Queries** tab you'll see one single query:
```sql
select * from `users` limit 10
```

And if you inspect the **Models** tab, you'll see ten models; this means that we've got ten Eloquent models loaded on the current route.

In the upcoming post I will discuss the eager-loading.