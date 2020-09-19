If you take a look at the `posts` table, you'll see that there is a `status` column which indicates the status of the post:

- published
- draft

And let's say that we want to calculate both the total `published` and `draft` posts.

Normally we'd do it as follows:
```php
$published = Post::where('status', 'published')->count();
$draft = Post::where('status', 'draft')->count();
```

What if I tell you that you can do it in one single query? 😄
```php
Post::toBase()->
    ->selectRaw('count(IF(status = 'published', 1, null)) as published')
    ->selectRaw('count(IF(status = 'draft', 1, null)) as draft')
    ->get();
```

In the [next post](../eloquent-performance-faster-LIKE-searching/), I will discuss the LIKE operator, and how it could impact the performance.