## Introduction to `LIKE` operator
The `LIKE` operator checks whether a string contains a specified pattern or not.

Usually, it is used with the percentage (`%`) wildcard to match any string of zero or more characters:
```sql
SELECT * FROM `companies` WHERE `name` LIKE '%clur%';
```

This example will match any company name that contains `clur` string:

- Mc<mark>Clur</mark>e Ltd
- Mc<mark>Clur</mark>e, Jaskolski and Nitzsche
- Sawayn-Mc<mark>Clur</mark>e
- Emmerich-Mc<mark>Clur</mark>e
- ...

> Read more about `LIKE` operator [here](https://www.mysqltutorial.org/mysql-like/).

Let's try it with one percentage at the end of the string:
```sql
SELECT * FROM companies WHERE `name` LIKE 'mc%';
```

This example will match any company name that starts with `mc` string:

- <mark>Mc</mark>Clure and Sons
- <mark>Mc</mark>Clure Inc
- <mark>Mc</mark>Clure-Koss
- ...

Another example:
```sql
SELECT * FROM companies WHERE `name` LIKE '%sons';
```

This example matches any company name that ends with `sons`:

- Schiller and <mark>Sons</mark>
- Feest and <mark>Sons</mark>
- Ankunding and <mark>Sons</mark>
- ...

## Indices with LIKE operator
Adding an index to the `name` field will make our search runs faster:
```sql
CREATE INDEX `users_name_index` ON `users` (`name`);
CREATE INDEX `companies_name_index` ON `companies` (`name`); 
```

In Laravel, we could achieve the same thing by creating a new migration:
```bash
php artisan make:migration add_name_index
```

```php
// migration

public function up()
{
    Schema::table('users', function (Blueprint $table) {
        $table->index('name');
    });

    Schema::table('companies', function (Blueprint $table) {
        $table->index('name');
    });
}
```

> Do not use one migration for two different tables; I just did that because I want to keep things simple.

There are two caveats when it comes to using the `LIKE` operator against a field **that** has an index:

1. The percentage wildcard at the beginning of the string wouldn't use any indices; therefore, the `users_name_index` will not be used, which means a slower query.
2. Using `whereHas` and `whereIn` will ignore the `users_name_index` as well (I'll discuss this later).

In this post, I will show you some tips that make your `LIKE` searching runs faster.

Please bear in mind that using the percentage wildcard at the beginning of the search term will not use the searched field index (if any), in our case, the `users_name_index`.

Maybe it doesn't make that difference if you have a small dataset, but in case of thousands of records, this will significantly impact the performance.

> Please note that my database contains 10.000 companies and 100.000 users.

## Laravel Implementation
Let's take the following Laravel code in the `App\Models\Company`:
```php
use Illuminate\Database\Eloquent\Builder;

public function scopeSearch(Builder $query, string $term = null)
{
    $query->where('name', 'like', '%'.$term.'%');
}
```

```php
// App\Http\Controllers\CompanyController

public function index(Request $request)
{
    $users = Company::query()
        ->search($request->input('q'))
        ->paginate;

    return view('company.index', compact($users));
}
```

Looking at the debug bar, I can see that it takes **90 ms** to execute the query.

Now, let's try to modify the scope as follows:
```php
$query->where('name', 'like', $term.'%');
```

Now it takes only **20 ms** on my machine! And that happened by just removing the percentage from the beginning of the string.

This means that MySQL is able to use the `name_index` on the `companies` table.

> Be careful when using the percentage at the beginning of the string; it has a significant impact on the performance.

## Searching in multiple fields within multiple tables
Sometimes you need to use the `LIKE` operator in two different fields within two separate tables.

For example, you would like to search for either the `users_name_index` or `user.company.name`:

```php
// App\Models\User
use Illuminate\Database\Eloquent\Builder;

public function scopeSearch(Builder $query, string $term = null)
{
    $term = $term.'%';
    $query->where('name', 'like', $term)
        ->orWhereHas('company', function($query) use ($term) {
            $query->where('name', 'like', $term);
        });
}
```

Because of the `whereHas` statement, MySQL won't be able to use the `user.name` index, which means a slower query.

How about joining? Can't we solve it by using the `$query->join` as follows:
```php
$query->join('companies', 'companies.id', '=', 'users.company_id');
```

The `join` has introduced two problems.

First of all, MySQL still not able to use the `users_name_index`

Since both `companies` and `users` have a `name` column, Laravel will end up overrding the `$user->name` with the `$company->name`.
 
Let's try it now by using the `whereIn` clause:
```php
$query->where('name', 'like', $term)
    ->orWhereIn('company_id', function($query) use ($term) {
        $query->select('id')->from('companies')->where('name', 'like', $term);
    });
```

Looking at the debug bar, I see that the `whereIn` clause is much faster than `whereHas` and `join`.

Here is my benchmark (**in ms**):

- `whereHas`: 600 ms
- `join` : 500 ms
- `whereIn` : <span class="text-green-800 font-black">130 ms</span>

But we still have the same problem.
 
MySQL still can't use the `users_name_index`, even though we use the `whereIn` clause.

## Combine two LIKE queries
Sometimes, it's faster to run multiple queries than one query.

For example, Let's see how long will it take to run the following query:
```sql
SELECT * FROM `users` WHERE `name` LIKE 'ahmad%';
```

On my computer, it took only **2 ms**, because MySQL has used the `users_name_index`.

Now, let's try the following query:
```sql
SELECT * FROM `companies` WHERE `name` LIKE 'ahmad%';
```

It took **2 ms** as well, so by combining these two queries, we achieve to main things:

1. Much faster execution time.
2. Both `users_name_index` and `companies_name_index` will be used.

Let's see how do we run these two queries in Laravel:
```php
// App\Models\User

use Illuminate\Database\Eloquent\Builder;

public function scopeSearch(Builder $query, string $term = null)
{
    $term = $term.'%';
    $query->where('name', 'like', $term)
        ->orWhereIn('company_id', Company::query()
            ->select('id')
            ->where('name', 'like', $term)
            ->get()
            ->pluck('id')
        );
}
```

We've just issued two queries.

The first query (`Company::query()...`) fetches all the `companies.id` that matches the given pattern:
```sql
# Took 24 ms on my machine
SELECT `id` FROM `companies` WHERE `name` LIKE 'ahmad%';
```

The second query fetches all the `users.name` that matches the given query as well, but it'll also use the company ids from the above query:
```sql
# Took 5 ms on my machine
SELECT * from `users` where (`name` LIKE 'mc%' OR `company_id` in (267, 4563, ...)
```

By doing so, we ensure that both `users_name_index` and `companies_name_index` are used, which results in faster querying.

I hope you enjoy this post, keep an eye for next upcoming post.