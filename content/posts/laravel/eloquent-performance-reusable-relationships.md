Sometimes we end up causing N+1 problems by reloading the same relationships that we already loaded.

Let's say that you have a method named `isAuthor()` in the `App\Models\Comment`.
 
The method determines whether the author of the comment is the same author of the post:
```php
// App\Models\Comment

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

Since the `App\Models\Post` was already loaded in the controller, can't we reuse it instead of calling the database again to fetch the same model (`App\Models\Post`)?

Yes, we can do that by using the `setRelation()` method on the `Illuminate\Database\Eloquent\Collection`:
```php
// App\Controllers\PostsController

$post = Post::where('id', $id)->with('comments.user')->first();

// This is our fix
$post->comments->each->setRelation('post', $post);

return view('posts.show', compact('post'));
```

No N+1 problem, that's amazing.

In the next post, I will discuss counting records in a single query.
