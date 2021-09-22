A database transaction (DB transaction) is **a unit of work that is either completed as a unit or undone as a unit** [[Source](https://docs.progress.com/bundle/openedge-webspeed-117/page/What-is-a-database-transaction.html)].

Laravel allows us to start database transactions using either the `DB::transaction()` or `DB::beginTransaction()` methods.

The `DB::transaction()` accepts a closure, and can optionally return a value:
```php
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;
use App\Models\Post;
use App\Models\Log;

// The transactio won't be comitted if an exception ocurr
$postId = 1;
$post = DB::transaction(function() use ($postId) {
		$post = Post::findOrFail($postId);

		$post = $post->update([
			'title' => $request->input('title'),
			'content' => $request->input('content'),
		]);

		Log::create([
			'post_id' => $post->id,
			'user_id' => Auth::id(),
			'action' => 'created',
		]);	

		return $post;
));

echo "You created a post with id ".$post->id;
```

In other hand, the `DB::beginTransaction()` provides more flexibility, because we should explicitly start, commit and rollback the transaction:

```php
try {
		DB::beginTransaction();

		// Find and update the post


		// Log it

		DB::commit();
} catch (Throwable $exception) {
		DB::rollBack();

		throw $exception;
}
```

That was all about transactions.

## What if…?
What if somebody else deletes the post while saving the log entry? Then what happens to the logging? As you might have guessed, it fails.

In an extensive system with thousands of writing queries, there is always a possibility where such a thing could occur.

> I remember we had a similar issue with a project that I was working on a few years ago.  
```php
$post = DB::transaction(function() {
		// We get the post by id	
		$post = Post::findOrFail($postId);

		// Update post

		// Somebody else deletes the post before logging it
		Log::create([]);	

		return $post;
));
```

As I mentioned earlier, the transaction will fail and the log entry won’t be saved.

## Use Pessimistic Locking
The Pessimistic Locking prevents the selected rows from being modified until the transaction gets committed.

In our case, nobody else can modify the post until we’re done with our transaction.

>  [Read](https://stackoverflow.com/questions/129329/optimistic-vs-pessimistic-locking)  more about the differences between  [Optimistic Locking](http://en.wikipedia.org/wiki/Optimistic_locking)  and ~[Pessimistic Locking](http://en.wikipedia.org/wiki/Lock_(database))~  

We can easily achieve such a thing using the `sharedLock` method in Laravel as follows:
```php
$post = DB::transaction(function() use ($postId) {
		$post = Post::sharedLock()->findOrFail($postId);

		// ...
});
```

The `sharedLock` method tells the database to lock the rows until we’re done with our transaction.

You may also use the `lockForUpdate` which prevents the selected records from being modified or from being **selected** with another shared lock.

> Read more about   [Pessimistic Locking in Laravel](https://laravel.com/docs/queries#pessimistic-locking).  
