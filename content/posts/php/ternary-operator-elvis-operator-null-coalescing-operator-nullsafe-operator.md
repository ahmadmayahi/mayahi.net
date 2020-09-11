## Ternary Operator
[Ternary Operator](https://en.wikipedia.org/wiki/%3F:) (`?:`) it's an inline `if-else` statement. 

Let's take a look at the following example:

```php
$status = true;
$statusText = null;

if ($status === true) {
    $statusText = 'OK';   
} else {
    $statusText = 'Fail';
}
```

By using the ternary operator, we could get rid of the entire `if-else` statement and replace it with something concise and more readable:

```php
$status = true;
$statusText = $status === true ? 'OK' : 'Fail';
```

## Elvis Operator
[Elvis operator](https://en.wikipedia.org/wiki/Elvis_operator) (`?:`) returns its first operand if that operand evaluates to a `true` value.

Let's see how it works by looking at the following example:

```php
$statusText = 'OK';

if ($statusText === "OK") {
	echo "OK";
} else {
	echo "Fail";
}
```

As you see, we repeat the value of the `$statusText` twice, so instead of doing that, we could use the Elvis-operator as follows:

```php
$statusText = 'OK';
echo $statusText ?: "Fail";
``` 

More concise and readable, but what if the `$statusCode` isn't defined?

```php
echo $statusText ?: "Fail";
```

We get a notice:

```text
PHP Notice:  Undefined variable: statusText in operators.php on line 2
```

The variable needs to be defined before we use the elvis-operator:

```php
if (isset($statusCode)) {
    echo $statusText ?: "Fail";
}
```

## Null coalescing operator
This operator was introduced in PHP 7.0.

[Null coalescing operator](https://www.php.net/manual/en/migration70.new-features.php) (`??`) works the exact same way as the elvis-operator, except it doesn't trigger a notice if the variable isn't defined or has a `null` value, hence it was named `null coalescing`:

```php
echo $statusText ?? "Fail";
```

Empty values, `false` and `0` are considered to be **not** `null`, therefore they will be returned:

```php
var_dump('' ?? "Second Value"); // string(0) ""
var_dump(false ?? "Second Value"); // bool(false)
var_dump(0 ?? "Second Value"); // int(0)
```

Let's try to use it on an undefined class property:

```php
class Person { }

$person = new Person();
echo $person->name ?? 'No name'; // No name
```

It works well, but how about the undefined class methods?

```php
class Person { }

$person = new Person();
echo $person->getName() ?? 'No name';
```

```text
PHP Fatal error:  Uncaught Error: Call to undefined method Person::getName()
```

You could solve this by using the `method_exists()` function:

```php
class Person { }

$person = new Person();

if (method_exists($person, 'getName')) {
	echo $person->getName() ?? 'No name';
}
```

## Null safe operator
This operator was introduced in PHP 8.0.

Null safe operator (`?->`) doesn't throw an error if the method 

```php
echo $person?->getName();
```


