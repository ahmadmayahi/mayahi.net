## Dummy Objects
A dummy is an object that replaces all the original methods with a dummy implementation that returns `null` (**without calling the original method**).

We can easily create a dummy object using the `createMock` method in [PHPUnit](https://phpunit.readthedocs.io/en/9.5/test-doubles.html):
```php
use GuzzleHttp\Client;

$client = $this->createMock(Client::class);
```

Let's inspect the dummy object using the `dd($client);` helper:
```php
Mock_Client_8cd31d5b {#129
  -config: null
  -__phpunit_originalObject: null
  -__phpunit_returnValueGeneration: true
  -__phpunit_invocationMocker: null
}
```

As you might have noticed, the `createMock` creates a random class; In our case it was named `Mock_Client_8cd31d5b`.  The `Mock_Client_8cd31d5b` extends `GuzzleHttp\Client` class:
```php
dd(
    class_parents($this->createMock(Client::class)),
);
```

Output:
```php
array:1 [
  "GuzzleHttp\Client" => "GuzzleHttp\Client"
]
```

Additionally, it overrides all the original methods, so they return `null`:
```php
$client = $this->createMock(Client::class);

// This line returns null
dd(
    $client->get('https://example.com')->getBody()
);
```

Please notice that the `createMock` replaces all the objects recursively, this means that the `get` method will return a new dummy implementation of the `Psr\Http\Message\ResponseInterface`.  

So, now we know what dummies are, but how would we use them?

Let's make some changes into the `CurrencyConvertor` class as follows:
```php
<?php

namespace App;

use Exception;
use GuzzleHttp\Client;

class CurrencyConversion
{
    public function __construct(private Client $client)
    {
    }

    public function convert(string $from, string $to, int|float $amount): float
    {
        $query = http_build_query([
            'from' => $from,
            'to' => $to,
            'amount' => $amount,
        ]);

        $req = $this
            ->client
            ->request('GET', 'https://api.exchangerate.host/convert?'.$query);

        if ($req->getStatusCode() !== 200) {
            throw new Exception('Could not convert!');
        }

        $res = json_decode($req->getBody()->getContents());

        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception('Invalid response!');
        }

        return $this->formatNumber($res->result);
    }

    public function formatNumber(float $amount, int $decimals = 2): float
    {
        return (float) number_format($amount, $decimals);
    }
}
```

As you might have noticed, I moved out the `number_format` in its own method.

Let's see how do we test the `formatNumber` method:
```php
    public function test_format_number()
    {
        $client = $this->createMock(Client::class);
        $currencyConvertor = new CurrencyConversion($client);

        $this->assertEqualsWithDelta(
            10.99,
            $currencyConvertor->formatNumber(10.999)
        , 0.1);
    }
```

The `CurrencyConvertor::__construct` requires an instance of `GuzzleHttp\Client` but it doesn't use it unless we call the `convert` method.

## Stubs
The practice of replacing an object with a test double that (optionally) returns configured return values is referred to as stubbing. [PHPUnit](https://phpunit.readthedocs.io/en/9.5/test-doubles.html).

In the previous post, we mocked different objects, for example the response object:
```php
$response = $this->createMock(ResponseInterface::class);

$response
    ->method('getStatusCode')
    ->willReturn(200);
```

This is called stubbing because we're configuring an object that returns a predefined value when it gets called.

## Conclusion
The difference between Dummies and Stubs lies in the return value; Dummy always returns `null`, whereas Stub returns a predefined value.

PHPUnit supports a bunch of stubbing methods such as `willReturnArgument`, `willReturnSelf`, `willThrowException`, consider instructing the documentation if you want to know more about them.

