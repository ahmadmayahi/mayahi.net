Laravel provides the `Illuminate\Foundation\Testing\RefreshDatabase ` trait to reset the database after each test so that data from a previous test does not interfere with subsequent tests.

The `RefreshDatabase` trait uses the artisan command `migrate:fresh` to drop all the tables from the database and then execute the `migrate` command; this is useful when you create or modify migrations.

In large applications with hundreds of migrations, the `migrate:fresh` could potentially slow down your tests.

This post will show you an easy solution to make your tests run faster by only executing the `migrate:fresh` when necessary.

## RefreshTestDatabase Trait
The `refreshTestDatabase` method in `RefreshDatabase` trait is responsible for migrating the database using the artisan command `migrate:fresh`, which drops all the tables and migrate:
```php
protected function refreshTestDatabase()
{
    if (! RefreshDatabaseState::$migrated) {
        $this->artisan('migrate:fresh');
        
        $this->app[Kernel::class]->setArtisan(null);
        
        RefreshDatabaseState::$migrated = true;
        }
    
    $this->beginDatabaseTransaction();
}
```

> [Read more](https://laravel.com/docs/migrations#drop-all-tables-migrate) about `migrate:fresh`   

The code is pretty straightforward, first of all, it checks for the migrations state, then it runs the `migrate:fresh` if necessary. Checking the state avoids running the `migrate:fresh` on each test, which is an expensive operation.

## The issue with migrate:fresh command
Let me raise a flag here; the `migrate:fresh` will be executed whenever we run `phpunit`:
```bash
# drop and migrate the database #1
./vendor/bin/phpunit

# drop and migrate the database #2
./vendor/bin/phpunit --filter="my_test"

# drop and migrate the database #3
./vendor/bin/phpunit --filter="my_test2"
```

Dropping/migrating the database makes sense if you make some changes by creating or modifying migrations, but what if you don’t do that?

Let’s have a look at the following example.

You create a new `languages` migration:
```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('languages', function (Blueprint $table) {
            $table->id();
            $table->string('code', 2)->unique();
            $table->string('name')->unique();
            $table->string('native_name')->unique();
            $table->timestamps();
        });
    }
};
```

Then you write some tests:
```php
use Tests\TestCase;

class LanguageTest extends TestCase
{
    /** @test **/
    public function it_creates_langage()
    {
        // ...
    }

    /** @test **/
    public function it_updates_langage()
    {
        // ...
    }   
    
    /** @test **/
    public function it_deletes_langage()
    {
        // ...
    }   
}
```

And you run the test:
```php
# running the test for the 1st time

./vendor/bin/phpunit --filter="it_creates_a_new_langage"
```

You might need to run the test several times, because you’re working on some improvements:

```php
# running the test for the 2nd time
./vendor/bin/phpunit --filter="it_creates_a_new_langage"
```

That is the problem! Laravel should not drop and migrate the database unless we make some changes to the `migrations`.

For example, renaming the `code` column to `iso_639_1` should force Laravel to drop and migrate the database:

```php
$table->string('iso_639_1', 2)->unique();
```

In short, we don’t need the `migrate:fresh` to be executed whenever we run `phpunit`, that’s it.

## Make it faster
We can easily avoid the  `migrate:fresh` command on each  `phpunit`  execution unless we make some changes in the migrations.

Let’s see how it works.

1. First of all, we need to calculate and save the checksum of the entire `migrations` folder; we can use [Symfony Finder](https://symfony.com/doc/current/components/finder.html) by iterating over the `database/migrations` folder and calculate the checksum for each migration file using the `md5_file` function.
2. Then we compare the checksum on the next test run; if the current checksum is different than the saved one, then we run the `migrate:fresh` otherwise, we skip it.

That’s it, let’s get started.

## Implementation
Create a new `trait` named `RefreshTestDatabase` in `/tests` folder.

```php
namespace Tests;

use Illuminate\Contracts\Console\Kernel;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Foundation\Testing\RefreshDatabaseState;
use Symfony\Component\Finder\Finder;

trait RefreshTestDatabase
{
    use DatabaseTransactions;

    protected function refreshTestDatabase(): void
    {
        if (! RefreshDatabaseState::$migrated) {
            $this->runMigrationsIfNecessary();

            $this->app[Kernel::class]->setArtisan(null);

            RefreshDatabaseState::$migrated = true;
        }

        $this->beginDatabaseTransaction();
    }

    protected function runMigrationsIfNecessary(): void
    {
        if (! $this->identicalChecksum() ||  ! $this->checksumExists()) {
            $this->createChecksum();
            $this->artisan('migrate:fresh');
        }
    }

    protected function calculateChecksum(): string
    {
        $files = Finder::create()
            ->files()
            ->exclude([
                'factories',
                'seeders',
            ])
            ->in(database_path())
            ->ignoreDotFiles(true)
            ->ignoreVCS(true)
            ->getIterator();

        $files = array_keys(iterator_to_array($files));

        $checksum = collect($files)->map(fn($file) => md5_file($file))->implode('');

        return md5($checksum);
    }

    protected function checksumFilePath(): string
    {
        return base_path('.phpunit.database.checkum');
    }

    protected function createChecksum(): void
    {
        file_put_contents($this->checksumFilePath(), $this->calculateChecksum());
    }

    protected function checksumFileContents(): bool|string
    {
        return file_get_contents($this->checksumFilePath());
    }

    protected function checksumExists(): bool
    {
        return file_exists($this->checksumFilePath());
    }

    protected function identicalChecksum(): bool
    {
        return ($this->checksumFileContents() === $this->calculateChecksum());
    }
}
```

From now and then, you should use the `RefreshTestDatabase` trait instead of the `RefreshDatabase` one.

The next step is to call the `refreshTestDatabase` method whenever you use the trait in your test files, this is done through the  `setUpTraits` method in the `Tests\TestCase` file:

```php
namespace Tests;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

abstract class TestCase extends BaseTestCase
{
    use CreatesApplication;
    use RefreshDatabase;

    protected function setUpTraits()
    {
        $uses = parent::setUpTraits();

        if (isset($uses[RefreshTestDatabase::class])) {
            $this->refreshTestDatabase();
        }

        return $uses;
    }
}
```

The last step is to add the `.phpunit.database.checkum` entry into the `.gitignore` file.

Try to run some tests and depends on the amount of your tests, you might notice a huge difference.

Here is the benchmark for one of my projects, which concist of more than 300 migrations:

* Without checksum: **9.229** s
* With checksum: **222.2** ms

That’s all.

I hope you enjoyed reading the post.
