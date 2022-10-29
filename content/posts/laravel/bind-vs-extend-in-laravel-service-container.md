According to [Laravel’s documentation](https://laravel.com/docs/container#extending-bindings), the `extend` method allows the modification of resolved services.

But what is the benefit of extending a class? And what is the difference between `bind` and `extend`?

Let’s dive into that.

## Binding
The `bind` method used to register a class into the service container.

Let’s see a real example from one of my projects:
```php
use Google\Cloud\Translate\V2\TranslateClient;

class AppServiceProvider
{
    public function register()
    {
        $this->app->singleton(TranslateClient::class, function() {
            return new TranslateClient([
                'keyFilePath' => storage_path('security/google-vision-credentials.json'),
            ]);
        });
    }
}
```

The `TranslateClient` is ready to be injected without any additional configuration, since the config key `keyFilePath` was already set:
```php
class Translate
{
    public function __construct(private TranslateClient $translateClient)
    {
    }
	
    // ...
}
```

That’s the power of dependency injection.

But what if I want to add a new method into the `TranslateClient`? Something like `isTranslatable` which detects whether or not the given string is translatable.

I can easily do that by extending the `TranslateClient` and start adding the `isTranslatable` method as follows:
```php
use Google\Cloud\Translate\V2\TranslateClient;

class MyTranslateClient extends TranslateClient
{
    public function isTranslatable(string $string): bool
    {
        // ...
    }
}
```

```php
$this->app->singleton(TranslateClient::class, function() {
    return new MyTranslateClient([
        'keyFilePath' => storage_path('security/google-vision-credentials.json'),
    ]);
});
```

That worked perfectly.

Let’s try to add `isAdmin` method in the `Illuminate\Auth\AuthManager`. This method checks the `is_admin` column on the `users` table; if it sets to `1`, the user is an admin; otherwise, she’s not.

As its name implies, the `AuthManager` has access to all the authentication features, such as `login`, `logout`, `loginUsingId`, `user`, etc…

You can access the `AuthManager` in different ways:
```php
// auth() helper
auth()->user();

// Illuminate\Support\Facades\Auth facade
// Auth::user();

// Dependency injection
public function __construct(private AuthManager $authManager)
{
    // ...
}
```

Ok. Let’s add the `isAdmin` method:
```php
namespace App\Support;

use Illuminate\Auth\AuthManager;
use Illuminate\Foundation\Application;

class MyAuthManager extends AuthManager
{
    public function __construct(private AuthManager $auth, Application $app)
    {
        parent::__construct($app);
    }

    public function isAdmin(): bool
    {
        return $this->auth->check() && $this->auth->user()->is_admin === 1;
    }
}
```

Let’s bind `MyAuthManager` into the service container:
```php
// AppServiceProvider
use Illuminate\Auth\AuthManager;
use Illuminate\Foundation\Application;

public function register()
{
    $this->app->bind(AuthManager::class, function(AuthManager $auth, Application $app) {
        return new MyAuthManager($auth, $app);
    });
}
```

```php
// BadMethodCallException
// Method Illuminate\Auth\SessionGuard::isAdmin does not exist. 

Auth::isAdmin();
```

That didn’t work, because the `bind` method can’t override/modify the builtin/3rd party services.

## Extending
Use the `extend` method whenever you want to modify a built-in/3rd party service, for example the `Illuminate\Auth\AuthManager`:
```php
// AppServiceProvider
use Illuminate\Auth\AuthManager;
use Illuminate\Foundation\Application;
public function register()
{
    $this->app->extend(AuthManager::class, function(AuthManager $auth, Application $app) {
        return new MyAuthManager($auth, $app);
    });
}
```

It should be working now:
```php
Auth::isAdmin();
```

I hope you enjoyed reading this post; keep an eye on the next upcoming ones.
