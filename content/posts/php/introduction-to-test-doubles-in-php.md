[Test doubles](https://en.wikipedia.org/wiki/Test_double) are one of the essential pillars of unit testing.

In this post and the next upcoming ones, I will guide you through all the five test doubles and explain each one in detail:

* Dummies.
* Stubs.
* Mocks.
* Spies.
* Fakes.

But before I dig into that, let me show you why do we need test doubles.

> Please bear in mind that you need to have [PHPUnit](https://phpunit.de) up and running on your machine.

## What is test double?
According to [Martin Fowler](https://martinfowler.com/bliki/TestDouble.html) the test double is:

> A generic term for any case where you **replace a production object for testing purposes**.

For example, let's say that your application uses an external API to do some currency conversion:
```php
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

        return number_format($res->result, 2);
    }
}
```

The obvious question that comes to mind is how do we test the `CurrencyConversion` class? 

Would it be ok to write a unit test that interacts with an external API?

Let's see:
```php
use App\CurrencyConversion;
use GuzzleHttp\Client;
use PHPUnit\Framework\TestCase;

class CurrencyConversionTest extends TestCase
{
    /** @test */
    public function it_converts_currency()
    {
        $cn = new CurrencyConversion(new Client());

        $amount = $cn->convert('USD', 'DKK', 100);

        $this->assertSame(634.461551, $amount);
    }
}
```

Run the test:
```bash
phpunit --filter="it_converts_currency"
```

Result:
```text
Time: 00:00.086, Memory: 20.00 MB

OK (1 test, 1 assertion)
```

The test passes, but there are a few caveats:

* The test is **wrong**, yes, you read it correctly, it is wrong because the exchange rate is subject to change, and that happens constantly.
* We should never call external APIs within our unit tests.
* Unit test should be as fast as possible, but calling an external API slows down the testing process.
* We should only test our code - _code that’s written by ourselves_ - but the external API is not ours.

The second point requires a bit of clarification.

You must know that production data - _such as API tokens_ - should not be exposed to the testing environment because the testing environment - _as its name implies_ - tests the production’s behavior without affecting it by making some unwanted changes.

Furthermore, calling production APIs could be dangerous. For example, imagine an API that chargers money - _such as Stripe_ - or an OCR API - _such as Google Vision API_ - where you pay per page/image.

So, what would we do? 😕

Well, we basically, **mock** the production behaviour. 🚀

Mocking means that we replace a production object (`GuzzleHttp\Client`) with a testing object; that's it.

In our example, we need to know what response does the API return, then we mock it and send it to the `CurrencyConversion`.

Sounds confusing? 🤔

Let’s have a look at the API response:

```json
{
  "motd": {
    "msg": "If you or your company use this project or like what we doing, please consider backing us so we can continue maintaining and evolving this project.",
    "url": "https://exchangerate.host/#/donate"
  },
  "success": true,
  "query": {
    "from": "USD",
    "to": "DKK",
    "amount": 100
  },
  "info": {
    "rate": 6.343743
  },
  "historical": false,
  "date": "2021-08-23",
  "result": 634.374255
}
```

As you have noticed, the `CurrencyConvertor::convert` method relies on the `result` key - _which is the total converted amount_ - so all we need to do is sending a fake response and then assert the predefined value.

But why would we assert something that already know? I mean the `result` value is `634.374255`.

That's a good question.

If you look at the `CurrencyConvertor::convert` method, you'll see that it uses the `number_format` function, so the goal is to test the behavior of `number_format`.

## How do we write test doubles?
There are a few PHP libraries to deal with test doubles in PHP, or what so-called mocking frameworks:
* [PHPUnit](https://phpunit.readthedocs.io/en/9.5/test-doubles.html).
* [Mockery](https://github.com/mockery/mockery).
* [Prophecy](https://github.com/phpspec/prophecy).

> PHPUnit doesn’t support spies or fakes, but the other frameworks do.

Let’s start testing the `CurrencyConvertor` using PHPUnit.

```php

use App\CurrencyConversion;
use GuzzleHttp\Client;
use PHPUnit\Framework\TestCase;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\StreamInterface;

class CurrencyConversionTest extends TestCase
{
    public function test_it_converts_currency()
    {
        $client = $this->createMock(Client::class);

        $response = $this->createMock(ResponseInterface::class);

        $response
            ->method('getStatusCode')
            ->willReturn(200);

        $stream = $this->createMock(StreamInterface::class);

        $stream
            ->method('getContents')
            ->willReturn($this->getJson());

        $response
            ->method('getBody')
            ->willReturn($stream);

        $client
            ->method('request')
            ->with('GET', 'https://api.exchangerate.host/convert?from=USD&to=DKK&amount=100')
            ->willReturn($response);

        $currencyConvertor = new CurrencyConversion($client);

        $amount = $currencyConvertor->convert('USD', 'DKK', 100);

        $this->assertSame(634.37, $amount);
    }

    private function getJson(): string
    {
        return '{"motd":{"msg":"If you or your company use this project or like what we doing, please consider backing us so we can continue maintaining and evolving this project.","url":"https://exchangerate.host/#/donate"},"success":true,"query":{"from":"USD","to":"DKK","amount":100},"info":{"rate":6.343743},"historical":false,"date":"2021-08-23","result":634.374255}';
    }
}
```

Let’s run it:
```bash
$ phpunit --filter="it_converts_currency"
PHPUnit 9.5.8 by Sebastian Bergmann and contributors.

.                                                                   1 / 1 (100%)

Time: 00:00.009, Memory: 20.00 MB

OK (1 test, 1 assertion)
```

The test works as it should be. Now let’s demystify the test case.

## Demystify the test case
We’ve started mocking the `GuzzleHttp\Client` because it is used as a dependency in the `CurrencyConvertor::__construct`:
```php
$client = $this->createMock(Client::class);
```

By default, all methods in the `GuzzleHttp\Client`  will be replaced with a dummy implementation that returns `null` (_without calling the original method_).

We've got a test double of type `Dummy`, but we can't really use it, because all the methods return `null` now.

Back to the `CurrencyConvertor::convert` method, we see that  the `request` method returns an instance of `Psr\Http\Message\ResponseInterface` , so we should mock that as well:
```php
$response = $this->createMock(ResponseInterface::class);

$response
    ->method('getStatusCode')
    ->willReturn(200);
```

The response became a test double of type `Stub`.

The practice of replacing an object with a test double that (optionally) returns configured return values is referred to as stubbing [Stubs in PHPUnit](https://phpunit.readthedocs.io/en/9.5/test-doubles.html#stubs).

So, as you guessed, the difference between Dummies and Stubs is that the latter returns some configured data, whereas the first one will always return `null`.

> In the next post, I will explain Dummies in detail.

The last thing that we need to do is mocking the `getBody()` method which returns an instance of `Psr\Http\Message\StreamInterface`:

```php
$stream = $this->createMock(StreamInterface::class);

$stream
    ->method('getContents')
    ->willReturn($this->getJson());
```

Here we’re telling the mocked object to return json data whenever the `getConents()` gets called.

And then, we tell the response to return the mocked stream if the `getBody()` method gets called:
```php
$response
    ->method('getBody')
    ->willReturn($stream);
```

Lastly, we mock the `request` method and inject the mocked `$client` instance as follows:
```php
$client
    ->method('request')
    ->with('GET', 'https://api.exchangerate.host/convert?from=USD&to=DKK&amount=100')
    ->willReturn($response);

$currencyConvertor = new CurrencyConversion($client);
```

Now, we’re ready to test it:
```php
$amount = $currencyConvertor->convert('USD', 'DKK', 100);

$this->assertSame(634.37, $amount);
```

So, now you know what mocking is, I will explain all the test doubles in detail in the following posts.
