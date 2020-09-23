If you take a look at the `posts` table, you'll see that there is a `status` column which indicates the status of the post:

- draft
- moderation
- published

And let's say that we want to count all the statues.

Normally we'd do it as follows:
```php
$draft = Post::where('status', 'draft')->count();
$moderation = Post::where('status', 'moderation')->count();
$published = Post::where('status', 'published')->count();
```

What if I tell you that you can do it in one single query? 😄
```php
Post::toBase()->
    ->selectRaw('count(IF(status = 'draft', 1, null)) as draft')
    ->selectRaw('count(IF(status = 'moderation', 1, null)) as moderation')
    ->selectRaw('count(IF(status = 'published', 1, null)) as published')
    ->get();
```

In the [next post](../eloquent-performance-faster-LIKE-searching/), I will discuss the LIKE operator, and how it could impact the performance.