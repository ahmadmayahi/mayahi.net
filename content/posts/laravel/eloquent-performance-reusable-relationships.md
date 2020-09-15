Sometimes, the relationship was already loaded somewhere, but we often load it repeatedly, causing some N+1 problems. 

Let me clarify this by an example.

Let's say that you have a method named `isAuthor()` in the `App\Models\Comment`, this method determines whether the author of the comment is the same author of the post:
```php
public function isAuthor(): bool
{
    return $this->post->user_id === $this->user_id;
}
```

```php
// App\Controllers\PostsController

$post = Post::where('id', $id)
    ->with('comments.user')
    ->first();

return view('posts.show', compact('post'));
```

In the template we show a badge if the comment's author is the same as the post's author:
```blade
@foreach ($post->comments as $comment)
<div class="card">
    <div class="card-body">
        <h6 class="card-title">Published at {{ $comment->created_at->toFormattedDateString() }}
            by {{ $comment->user->name }}
            @if ($comment->isAuthor())
                <span class="badge badge-warning">Author</span>
            @endif
        </h6>
        <p class="card-text">{{ $comment->comment }}</p>
    </div>
</div>
<div class="m-4"></div>
@endforeach
```

As you see in the template, the `isAuthor()` method was called inside the `foreach` (N+1 problem).

Since the `App\Models\Post` was already loaded in the controller, can't we reuse it? So we prevent the `isAuthor` method from calling the database again to fetch the same model.

Yes, we can that by using the `setRelation` method on the `Illuminate\Database\Eloquent\Collection`:
```php
// App\Controllers\PostsController

$post = Post::where('id', $id)->with('comments.user')->first();

// This is our fix
$post->comments->each->setRelation('post', $post);

return view('posts.show', compact('post'));
```

The fix is too easy; We tell Laravel to apply the `setRelation` method on each `App\Models\Comment`, so it doesn't need to fetch again from the database, that's it.

In the next post, I will discuss counting records in a single query.
