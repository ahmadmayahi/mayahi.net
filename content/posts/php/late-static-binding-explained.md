PHP 5.3 came out with a fantastic OO feature called Late Static Binding, a fancy term for a simple concept.

If you take a look at some of the modern PHP frameworks/libraries you’ll see that static method is used a lot in their classes.

In this post, I’ll be showing you the differences between `self` and `static` and when should we use them.

## String Class

Imagine that you’re creating a composer library that provides some string helpers, one of the helpers is a string decorator:

```php
namespace Mayahi\MyStringPackage;

class Str
{
    public function decorate(string $str): string
    {
        $lines = self::getLines();
        
        return $lines . PHP_EOL . $str . PHP_EOL . $lines;
    }
        
    public function getLines()
    {
        return str_repeat('-', 10);
    }

        // other helpers ...
}
```

Let’s try it out:

```php
$str = new Mayahi\MyStringPackage\Str();
echo $str->decorate('Hello World');
```

Output:

```
----------
Hello World
----------
```

What if I want to change the `getLines()` method and makes it generate twenty stars per line (*) instead of ten dashes (-)?

Since `Str` class rely on the `getLines()` method, the only way to accomplish that is to create a subclass that extends the `Str` class and then overriding the `getLines()` method:

```php
class MyStr extends Str
{
    public function getLines()
    {
        return str_repeat('*', 20);
    }
}
```

Let’s try it out:

```php
$str = new MyStr();
echo $str->decorate('Hello World');
```

Output:

```text
----------
Hello World
----------
```

It still returns the same result as before, but why? It's because of the `self` pseudo-variable.

The `self` pseudo-variable refers to the same class, this means that the `getLines()` method must be in the same class.

To solve this issue, all you need to do is to change the `self` pseudo-variable in the `decorate()` method to `static`:

```php
public function decorate(string $str): string
{
    $lines = static::getLines();
    return $lines.PHP_EOL.$str.PHP_EOL.$lines;
}
```

Try to run your code again:

```text
********************
Hello World
********************
```

Yes, the result is correct now.

By using the **Late Static Binding** (`static`) we are telling PHP to lookup for the `getLines()` method in the subclass (if any), if PHP doesn’t find it there, then it’ll fall back to the current class, that’s it.

## A Real-World Example

Let’s have a look at a real world example by inspecting the Laravel’s Str class.

As you may see, Late Static Binding is used in many different methods, such as the containsAll() which uses the Late Static Binding to call the contains method:

```php
if (! static::contains($haystack, $needle)) {
     return false;
}
```

By doing so, Laravel allows us to extend the Str class and having our own implementation for some of the methods.

## When to use it?

If you’re creating an extendable class, or you’re relying on the subclass to provide a particular method, then go for static.

> Remember that self refers to the current class and not the object, you must use $this to refer to the current object, such as none-static properties.

Let me show you another example.

## Real-World Example: Singleton Design Pattern

You may have heard of the Singleton Design Pattern, in case you don’t, here is a brief introduction.

Imagine that you have a DatabaseConnection class that establishes a MySQL connection using PDO:


```php
class DatabaseConnection
{
    private $dbh;
    
    public function __construct(string $dsn, string $user, string $password)
    {
        // Connect
    }
    
    public function fetch(string $sql, array $bindings): ?array
    {
        // Fetch some data
    }
    
    // Rest implemention...
    
}
```

You may need to call the database connection in different places, this ends up establishing several database connections:

```php
$db1 = new DatabaseConnection('mysql:dbname=testdb;host=127.0.0.1', 'user', 'password');
echo 'Object Id: '.spl_object_id($db1).PHP_EOL;

$db2 = new DatabaseConnection('mysql:dbname=testdb;host=127.0.0.1', 'user', 'password');
echo 'Object Id: '.spl_object_id($db2).PHP_EOL;
```

```text
Object Id: 1
Object Id: 2
```

The spl_object_id returns the unique identifier for the given object during the runtime,

Since we are instantiating the DatabaseConnection twice, the spl_object_id returns two different values, which means that we’re establishing two database connections.

The Singleton Design Patterns ensures that the object is only instantiated once during the runtime, by doing so, we’re limiting the database connections to one:

```php
class Singleton
{
    private static ?object $instance = null;
    
    protected function __construct() { }

    protected function __clone() { }

    public function __wakeup() { }

    public static function getInstance()
    {
        $subclass = static::class;
        if (is_null(self::$instance)) {
            self::$instance = new static;
        }

        return self::$instance;
    }
}
```

Let’s try it out:

```php
class DatabaseConnection extends Singleton
{
    private $dbh;
    
    protected function __construct()
    {
        // Connect to the database
    }
    
    public function fetch(string $sql, array $bindings = []): ?array
    {
        // Fetch some data
    }
    
    // Rest implemention...

}

$db1 = DatabaseConnection::getInstance();
echo 'Object Id: '.spl_object_id($db1).PHP_EOL;

$db2 = DatabaseConnection::getInstance();
echo 'Object Id: '.spl_object_id($db2).PHP_EOL;
```

```text
Object Id: 1
Object Id: 1
```

Try to instantiate the DatabaseConnection class as many times as you want and you’ll get the exact same object id.