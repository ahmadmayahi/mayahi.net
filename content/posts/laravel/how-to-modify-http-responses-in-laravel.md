Laravel middleware provides a convenient mechanism for inspecting and filtering HTTP requests entering our application.

> [Learn more about Laravel middleware](https://laravel.com/docs/middleware)

Additionally, the middleware may also be used to modify the HTTP response.

Let’s see how to do it.

Create a new middleware:
```bash
php artisan make:middleware MyMiddleware
```

Open up `app/Http/Kernel.php` file and add the newly created middleware in the `$middleware` key:

```php
class Kernel 
{
    protected $middleware = [
        // ...
        App\Http\Middleware\MyMiddleware::class,
    ];
}
```

Go back to `MyMiddleware` file, here you can easily modify the response:
```php
public function handle(Request $request, Closure $next)
{
    /** @var \Illuminate\Http\Response $response */
    $response = $next($request);
    
    // Modify the response ...
    
    return $response;
}
```

For example, you may add a new Http header as follows:
```php
$response->addHeader($response->header('X-ADMIN', Auth::user()->isAdmin);
```

You can also change the status code based on a certain criteria:
```php
if (false) {
	$response->setStatusCode(400);
}
```

> Inspect the [Illuminate\Http\Response | Laravel API](https://laravel.com/api/master/Illuminate/Http/Response.html) for more methods.

That’s it.

I hoped you enjoyed reading this post :-)
