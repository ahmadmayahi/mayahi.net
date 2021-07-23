# Test Doubles in PHP- Part 1: Dummies
#php
Test doubles are one of the essential pillars of testing.

In this post and the next upcoming ones, I will guide you through all the five test doubles and explain each one in detail, so let's get started with the easiest one, the `Dummy` test double.

> Please bear in mind that you need to have [PHPUnit](https://phpunit.de) up and running on your machine.  

## What is test double?
According to [Martin Fowler](https://martinfowler.com/bliki/TestDouble.html) the test double is:

> a generic term for any case where you **replace a production object for testing purposes**.  

For example, let's say that your application uses an external API to do some currency conversion:
```php
namespace App\Services;

use GuzzleHttp\Client;

class CurrencyConversion
{
    public function __construct(private Client $client)
    {
    }

    public function convert(string $from, array $to)
    {
        return $this->client
            ->request('GET', 'https://api.exchangeratesapi.io/latest?base=' . $from . '&symbols=' . implode(',', $to))
            ->getBody()
            ->getContents();
    }
}

```

Now, let's pretend that the `CurrencyConversion` class was used in the the `InvoiceGenerator` as follows:
```php
namespace App\Services;

use App\Models\Product;
use App\Models\Client;
use CurrencyConvertor;

class InvoiceGenerator
{
    public function __construct(private CurrencyConvertor $currencyConvertor)
    {
    
    }
    
    public function generate(Product $product, Client $client)
    {
        // Convert the product's price into the client's local currency

        
        $clientCurrencyRate = $this->currencyConvertor->convert(
            $product->currency->code,
            $client->currency->code,
        )['rates'][$client->currency->code];
        
        $convertedPrice = ($product->price_without_vat * $clientCurrencyRate);
        
        // Generate the invoice ...
    }
}
```

The obvious question that comes to mind is how do we test the `CurrencyConversion` class?

Short answer: **we don't**.

**We don't test code that we have no control over**, and the external API is one of them.

But what if the API fails? How do we know that?

Well, That's a different thing, you should add some error handling to check whether the API returns the expected data, but you must avoid calling external APIs within your test cases.

For example, you can rewrite the `convert` method to handle the possible errors:
```php
namespace App\Services;

use GuzzleHttp\Client;

class CurrencyConversion
{
    public function convert(string $from, array $to): array
    {
        $request = $this
            ->client
            ->request('GET', 'https://api.exchangeratesapi.io/latest?base='.$from.'&symbols='.implode(',', $to);
            
        if ($request->getStatusCode() !== 200) {
            throw new Exception('Could not convert the currency!');
        }
        
        $rates = json_decode($request->getBody()->getContents());
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception('Malformed data returned');
        }
        
        return $rates;
    }
}
```

Normally, the external APIs comes with versioning, and they should work as expected.

Take the Stripe API as an example:
```text
https://api.stripe.com/v1/charge
```

The versioning is a great way to prevent breaking changes, so if Stripe adds some breaking changes, they will definitely add that in the next major version, which is version 2 in this case.

Fair enough, you shouldn't test code that we don't own, but how about the `InvoiceGenerator` class? Shouldn't we test it? If so, how do we do that without calling the external API?

Yes, you must test the `InvoiceGenerator` but without calling the external API, but how? What??? 😕

**Welcome to test doubles** 🚀.

Basically, the `CurrencyConvertor` needs to be mocked, so we can test the rest of the code.

The mocking means that we replace a production object (`CurrencyConvertor`) with a testing object, that's it.

## Dummies
The dummy is nothing but a dump object that mimics the production behaviour.

In other words, it’s sole responsibility is to get your code to work, without any expectations.

Prior PHP 5.3, programmers tend to create dummy objects to test their classes, but things have changed with the advent of type-hinting.

Nowadays, programmers use either `stubs` or `mocks,` and `dummy` is rarely used.

Anyway, let me demystify it by an example:
```php
class CountryDecorator
{
    private $country;
    
    private $capital;

    public function __constructor($data)
    {
        $this->country = $data->country;
        $this->capital = $data->capital;
    }
    
    public function decorate()
    {
        return 'The capital of '.$this->country.' is '.$this->capital;
    }
}
```

As you've noticed, the `$data` parameter is not type-hinted; therefore we can easily inject a dump object and get it tested:
```php
/** @test */
public function it_decorates_the_country()
{
    $data = new stdClass();
    $data->country = 'Denmark';
    $data->capital = 'Copenhagen';
    
    $countryDecorator = new CountryDecorator($data);
    
    $this->assertEquals('The capital of Denmark is Copenhagen', $countryDecorator->decorate());
}
```

As I mentioned earlier, dummies are rarely used.

But what if the `$data` was a type-hinted object?

In the next post, I will discuss the stubs.
