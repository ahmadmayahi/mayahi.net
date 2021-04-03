By default, Laravel doesn’t observe the pivot tables. To make this clear, let’s have a look at the following tables:

```text
posts
	- id
	- title
	- content
	- ...
tags
	- id
	- name
	- ...
post_tag
	- id
	- post_id
	- tag_id
```

As you might have noticed, the `post_tag` is a pivot table, and therefore we don’t need a model for it.

Let’s have a look at the following relationship:
```php
public function tags(): BelongsToMany
{
    return $this->belongsToMany(Tag::class);
}
```

To determine the relationship's intermediate table's name, Eloquent will join the two related model names in alphabetical order; in our case, it's `post_tag` since `P` comes before `T` in the English alphabet.

> [Read](https://laravel.com/docs/eloquent-relationships#many-to-many-model-structure) more about Eloquent relationships  

Let’s create an observer for the `post_tag` table, so we get informed whenever the user attaches a tag to the `post` table.

First of all, we need to create a model for the `post_tag` because it’s a pivot table and doesn’t have an actual model:
```bash
php artisan make:model PostTag
``` 

The model should look like this:
```php
namespace App\Models;

use Illuminate\Database\Eloquent\Relations\Pivot;

class PostTag extends Pivot
{
    protected $table = 'post_tag';

    public $timestamps = null;
}
```

Remember, the `PostTag` must extend the `Illuminate\Database\Eloquent\Relations\Pivot` class and not the `Illuminate\Database\Eloquent\Model` since it’s a pivot table, otherwise, you’ll get an error similar to the following one:
```text
BadMethodCallException
Call to undefined method App\Models\PostTag::fromRawAttributes() 
```

The second step is to create an observer for the `PostTag` model:
```bash
php artisan make:observer PostTagObserver --model=PostTag
```

Add the observer into `boot` method in the `AppServiceProvider` as follows:
```php
PostTag::observe(PostTagObserver::class);
```

Open up the `PostTagObserver` and add the following code to log the `PostTag` model in the `created` event:
```php
namespace App\Observers;

use App\Models\PostTag;

class PostTagObserver
{
    public function created(PostTag $postTag)
    {
        logger($postTag);
    }
}
```

Let’s try it out:
```php
# Filename: routes/web.php

Route::get('/observer', function() {
    $post = \App\Models\Post::find(1);
    $tag = \App\Models\Tag::inRandomOrder()->first();
    $post->tags()->attach($tag->id);
});
```

Go ahead and open up the `storage/logs/laravel.log` file; Ops! nothing there.

The problem is that Laravel doesn’t know anything about the `PostTag` model that we created for the pivot table `post_tag` because Laravel relies on the table’s name and not the model name.

This shouldn’t be a problem because the pivot table is just an intermediate table. Therefore it doesn’t need a model unless you want to customize it.

Fortunately, the solution is straightforward. All we need to do is to tell Eloquent about the `PostTag` model:

```php
# Filename: app/Models/Post.php

public function tags(): BelongsToMany
{
    return $this->belongsToMany(Tag::class)->using(PostTag::class);
}
```

The `using` method is used to specify the custom pivot model to use for the relationship.

Try to hit the same route again, and you’ll see a new logged entry.
```text
[2021-04-03 12:59:46] local.DEBUG: {"tag_id":59,"post_id":1}
```

I hope you enjoyed this short article.
