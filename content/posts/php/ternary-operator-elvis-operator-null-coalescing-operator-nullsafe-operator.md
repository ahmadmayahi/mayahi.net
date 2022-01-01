## Ternary Operator
[Ternary Operator](https://en.wikipedia.org/wiki/%3F:) (`?:`) it's an inline `if-else` statement. 

Let's have a look at the following example:
```php
$status = true;
$statusText = null;

if ($status === true) {
    $statusText = 'OK';   
} else {
    $statusText = 'Fail';
}
```

By using the ternary operator, we will be able to get rid of the entire `if-else` statement and replace it with a concise syntax:
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

As you see, we've repeated the value of the `$statusText` twice, so instead of doing that, we could use the Elvis-operator as follows:
```php
$statusText = 'OK';
echo $statusText ?: "Fail";
``` 

The variable needs to be defined before we using the elvis-operator, so the following code throws an error:
```php
echo $statusText ?: "Fail";
```

```text
PHP Notice:  Undefined variable: statusText in operators.php on line 2
```

We can solve it as follows:
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

Empty values, `false` and `0` are considered to be **NOT** `null`, therefore they will be returned:
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

It works well, but how about class properties?

Let's have a look at the following example:

```php
interface Country { }

class Iraq implements Country 
{
    public string $name = 'Iraq';
}
	
class Person 
{
    public ?Country $country = null;
    
    public function __construct(?Country $country) {
        $this->country = $country;
    }
}
	
$person = new Person(nulll);

echo 'I am are from: ' . $person->country->name;
```

```text
PHP Warning:  Attempt to read property "name" on null in ...
```

As you might have noticed, the `country` property on the `Person` class cen accept either a `Country` interface or a `null` value, but always expect it to have a `Country` object.

Let's see how to fix it in PHP < 8.0:

```php
if ($country = $person->country) {
    echo 'I am from '. $country->name;
}
```

## Null safe operator
This operator was introduced in PHP 8.0.

The null safe operator (`?->`) doesn't throw an exception if we try to access the `name` property on `null`:

```php
echo $person->country?->name;
```

Basically, it's telling PHP to get the `name` propery if the object does exist, otherwise it should neglect it.