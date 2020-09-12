As I [discussed earlier](/laravel/eloquent-performance-tips/) N+1 is a common problem in ORM systems such as Eloquent.

Fortunately, Laravel provides a smart way to overcome the N+1 issues, but let's discover the problem first before I show the solution.

Let's say that we'd like to list all the users along with their company names:
```php
// App\Http\Controllers\UserController

public function index()
{
    $users = User::take(20)->get();
    return view('users.index', compact('users'));
}
```

```blade
<-- resources/views/users/index.blade.php -->

@foreach ($users as $user)
    <p>Name: {{ $user->name }}</p>
    <p>Company: {{ $user->company->name }}</p>
@endforeach
```

If you inspect the **Queries** tab, you'll see several `companies` queries due to the `company` calling within the foreach (`$user->company->name`):
```sql
select * from `companies` where `companies`.`id` = 5843 limit 1;
select * from `companies` where `companies`.`id` = 2116 limit 1;
select * from `companies` where `companies`.`id` = 1345 limit 1;
# ...
```

As you guessed, we introduced an N+1 problem.

> Laravel uses the term lazy-loading in contrast to eager-loading.

We can easily mitigate such problems by the use of [eager loading](https://laravel.com/docs/eloquent-relationships#eager-loading).

But what does this fancy term mean?

The eager-loading uses one single `SELECT` statement instead of **N** `SELECT`s, thanks to the SQL `IN` operator: 
```sql
select * from `companies` where `companies`.`id` in (5843, 2116, 1345);
``` 

Now, let's see how do we mitigate it:
```php
$users = App\Models\User::with('company')
    ->take(20)
    ->get();
```

By using the `with` method we're telling Eloquent to eager-load the `company` relationship.

You can also tell Eloquent to eager-load the relationships directly from the model, although it's not recommended, and I don't use it at all:

```php
# App\Models\User

// The `Company` will be automatically loaded 
// whenever we access the `User` model.

protected $with = ['company'];
```

You may also eager-load multiple relationships:
```php
$users = User::with(['company', 'posts'])->paginate();
```

Nested eager loading is supported as well using the do notation.

Let's say that you want to eager-load the `App\Models\Country` in the `App\Models\Company` from the `App\Models\User`:
```php
$users = User::with('company.country')->paginate();
``` 

Now, you can safely access the `App\Models\Country` in the `App\Models\Company` without worrying about N+1 problems:
```blade
@foreach ($users as $user)
    <p>Company: {{ $user->company->name }}, Country {{ $user->company->country->name }}</p>
@endforeach
```

That was all about eager-loading, now you may ask, will eager-loading solve all my N+1 problems? And when do I use it?

Well, eager-loading will not solve all your N+1 problems; it might solve some of them, but not all of them.

Let me ask you a question: **How can you get the latest login date from `App\Models\User` in an efficient way?**

> By efficient way, I mean a single SQL query. 

I'm not going to show you the solution now 😁 but just think about it for a while.

In the meanwhile, let me show you piece of code that I found in one of the projects:
```php
// App\Models\User
public function logins()
{
    return $this->hasMany(Login::class);
}

public function latestLogin()
{
    return $this->logins->latest();
}
```

You might have seen such a code as well, or you may use such as code in your project, can you see the problem?

It fetches all the login records for the current user, and then it uses only the last one.

While it's not a big problem if we have a few login entries, it could be a serious problem if there are too many records (1000+ records for each user).

I will show you a great solution in the next upcoming post.