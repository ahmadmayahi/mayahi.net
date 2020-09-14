Consider the following code: 
```php
# Controllers/UsersController

public function index()
{
    return view('posts.index', ['posts' => Post::paginate()]);
}
```

```blade
# views/posts/index.blade.php

@foreach ($posts as $post)
    <h2>{{ $post->title }}</h2>
@endforeach
```

By default, Laravel selects all the columns when using Eloquent:
```sql
-- Took 32 ms to execute
select * from `posts` limit 0, 15;
``` 

In this query, we're selecting the entire columns set, but we only use of them which is the `title`.
 
If you take a look at the database diagram, you'll see that the `content` column is of type `longtext` which means it can hold up to 4GB of data.

We saw that it took 32 ms on my machine to execute the above query, so what if we just select the `title` column:
```sql
-- Took 2 ms to execute
select title from posts;
```

A big difference, **32 ms vs 2 ms**.

Here is the tip, only select the columns that you need as follows:
```php
Post::query()
    ->select('title')
    ->paginate();
```

You may also use the `with` method to select the needed columns from the relationships as follows:
```php
Post::query()
    ->select('title')
    ->with('user:id,name')
    ->paginate();
```

In ths [upcoming post](../eloquent-performance-eager-loading/), I will discuss the eager-loading.