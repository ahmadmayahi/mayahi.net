In the [previous post](../eloquent-performance-subqueries) I discussed the subqueries, an efficient way to fetch a subset of data from another table.

In this post, I will extend upon the subquery and introduce you to the fake queries.

> Fake query is the name that I use to refer to a particular solution, other people may use different names.

Let me show you what I mean.

In the previous post, we've seen how to fetch the `latest_login_date` from the `App\Models\Login` in a fast way.

What if you want to get the latest `App\Models\Login` as an Eloquent model instance and not just a Carbon instance?

But isn't that easy to achieve? I mean we can add a method to fetch the last login in the `App\Models\User` as follows:
```php
// App\Models\User

public function latestLogin()
{
    return App\Models\Login::where('user_id', $this->id)->latest()->first();
}
``` 

Bummm! we introduced N+1 problem 😄, since the `App\Models\Login` will be loaded for each user individually.

Let me show you how to solve such an issue by using the fake relationship.

## Fake relationships
We can create a fake relationship and delude Laravel to treat it as if it was a real relationship, sounds confusing? No problem, let me demystify it.

Let's add a new fake relationship in the `App\Models\User`:
```php
public function lastLogin()
{
    return $this->belongsTo(App\Models\Login::class);
}
```

As I said, this is a fake relationship, because there's no `last_login_id` in the `App\Models\User` which is required for the `belongsTo` relationship to work properly.

The solution is to combine the subquery with the eager-loading to make the `lastLogin` relationship works:
```php
public function scopeWithLastLogin($query)
{
    $query->addSelect(['last_login_id' => Login::select('id')
        ->whereColumn('user_id', 'users.id')
        ->latest()
        ->take(1)
    ])->with('lastLogin');;
}
```

```php
// App\Http\Controllers\UsersController

// ...

User::withLastLogin()->paginate();

// ...
```

If you take a look at the debugger you'll see that all the latest logins were eager-loaded:
![Eager-loading with fake realtionships](./static/img/laravel/eloquent-performance/003.png)

Remember that the `lastLogin` method cannot be used without calling the `withLastLogin` scope on the `App\Models\User`.

In the [next post](../eloquent-performance-reusable-relationships/), I will discuss the reusable relationships.