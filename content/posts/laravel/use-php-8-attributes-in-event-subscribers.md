In Laravel, each event has its corresponding listener. For example, the `OrderShipped` event might have a `SendShipmentNotification` listener, simple and straightforward.

Sometimes you need to handle several events within the same listener class. For example, you might need to handle both `userLogin` and `userLogout` events in the same listener class.

The event subscribers give you the ability to subscribe to multiple events from within the subscriber class itself.
 
> [Read more](https://laravel.com/docs/events#writing-event-subscribers) about event subscribers in Laravel.  

## Introduction to event subscribers
Event subscribers are too easy to deal with. All you need to do is to create a class with a `subscribe` method in which it instructs Laravel to look for the listeners:
```php
namespace App\Listeners;

class UserEventSubscriber
{
    public function handleUserLogin($event) { // ... }

    public function handleUserLogout($event) { // ... }

    public function subscribe($events)
    {
        $events->listen(
            'Illuminate\Auth\Events\Login',
            [UserEventSubscriber::class, 'handleUserLogin']
        );

        $events->listen(
            'Illuminate\Auth\Events\Logout',
            [UserEventSubscriber::class, 'handleUserLogout']
        );
    }
}
```

And then register the event subscriber in the `EventServiceProvider`:
```php
protected $subscribe = [
	UserEventSubscriber::class,
];
```

That’s it.

Each time you need to add a new event, you should open up the `UserEventSubscriber` and modify the `subscribe` method to have the new event.

## PHP 8 Attributes
PHP 8 came with a fantastic feature called [attributes](https://php.watch/articles/php-attributes).

The attributes are used to add some meta-data to our code, for example:
```php
class AboutPageController
{
    #[Route('/about')]
    public function show()
    {
        return view('pages.about');
    }
}
```

The `#[Route('/about')]` is an attribute. It tells PHP that the `show` method got a `Route` attribute. That’s it.

Using the [reflection API](https://www.php.net/manual/en/book.reflection.php), we can extract the attributes and act upon them.

For example, whenever we encounter the `Route` attribute, we should create a route for the given parameter `/about`, so wouldn’t it be nice to implement attributes in `UserEventSubscriber` ?
```php
namespace App\Listeners;

use Attributes\ListensTo;

class UserEventSubscriber
{
    #[ListensTo(Illuminate\Auth\Events\Login::class)]
    public function handleUserLogin($event) { // ... }
    
    #[ListensTo(Illuminate\Auth\Events\Logout::class))
    public function handleUserLogout($event) { // ... }
}
```

Let’s see how do we do it.

## PHP Attributes Subscribers
Create a class named `ListensTo` in `App\Attributes` as follows:
```php
namespace App\Attributes;

use Attribute;

#[Attribute]
class ListensTo
{
    public function __construct(public string $event)
    {
    }
}
```

This class shouldn’t do anything, it’s just an attribute class.

Create another class named `UserEventSubscriber` in `App\Subscribers`:
```php
namespace App\Subscribers;

use App\Attributes\ListensTo;
use Illuminate\Auth\Events\Login as LoginEvent;
use Illuminate\Auth\Events\Logout as LogoutEvent;

class UserEventSubscriber
{
    #[ListensTo(LoginEvent::class)]
    public function handleUserLogin(LoginEvent $event)
    {
        logger('Users logged in: '.$event->user->id);
    }

    #[ListensTo(LogoutEvent::class)]
    public function handleUserLogout(LogoutEvent $event)
    {
        logger('Users logged out: '.$event->user->id);
    }
}
```

Open up the `EventServiveProvider` and add a new property `$subscibers`:

```php
use App\Subscribers\UserEventSubscriber;

class EventServiceProvider extends ServiceProvider
{
    protected array $subscribers = [
        UserEventSubscriber::class,
    ];
    // ...
}
```

> Please don’t mix Laravel’s `$subscribe` property with `$subscribers`. We make the latter to hold all the attributed subscribers.  

In the `register` method, we need to iterate over the `$subscribers`, read the `ListensTo` attribute, and send it to the event dispatcher.

Create a new class named `ResolveListeners` in the `App\Support`:

```php
namespace App\Support;

use App\Attributes\ListensTo;
use ReflectionClass;

class ResolveListeners
{
    public function resolve(string $subscriberClass): array
    {
        $subscriberReflectionClass = new ReflectionClass($subscriberClass);

        $listeners = [];

        foreach ($subscriberReflectionClass->getMethods() as $listenerMethod) {

            // Only get the attribute "ListensTo"
            $listenerMethodAttributes = $listenerMethod->getAttributes(ListensTo::class);

            foreach ($listenerMethodAttributes as $listenerMethodAttribute) {
                // Instantiate the "ListensTo" class so we can get the event name

                /** @var ListensTo $listener */
                $listener = $listenerMethodAttribute->newInstance();

                $listeners[] = [
                    $listener->event,
                    [$subscriberClass, $listenerMethod->getName()]
                ];
            }
        }

        return $listeners;
    }
}
```

Let’s see how does this class work:

1. The `$subscriberReflectionClass->getMethods()` iterates over the listener's methods for the given subscriber class; In our case it gets `handleUserLogin` and `handleUserLogout` methods from the `UserEventSubscriber`.
2. The `$listenerMethodAttributes` gets the `ListensTo::class` attributes for the given listener.
3. By iterating over the `$listenerMethodAttributes` we can easily instantiate the `ListensTo` attribute class by using the `$listenerMethodAttribute->newInstance()`. This will return an instance of `App\Attributes\ListensTo` so we can read the event’s name.
4. Finally, we add the event’s name and its listener to the `$listener` and we return it.
```php
Array
(
    [0] => Array
        (
            [0] => Illuminate\Auth\Events\Login
            [1] => Array
                (
                    [0] => App\Subscribers\UserEventSubscriber
                    [1] => handleUserLogin
                )
        )

    [1] => Array
        (
            [0] => Illuminate\Auth\Events\Logout
            [1] => Array
                (
                    [0] => App\Subscribers\UserEventSubscriber
                    [1] => handleUserLogout
                )
        )
)
```

The `ResolveListeners` is ready now. Let’s go back to the `EventServiceProvider` and resolve the events as follows:
```php
namespace App\Providers;

use App\Subscribers\LoggerSubscriber;
use App\Subscribers\UserEventSubscriber;
use App\Support\ResolveListeners;
use Illuminate\Events\Dispatcher;
use Illuminate\Foundation\Support\Providers\EventServiceProvider as ServiceProvider;

class EventServiceProvider extends ServiceProvider
{
    protected array $subscribers = [
        UserEventSubscriber::class,
        LoggerSubscriber::class,
    ];

    public function register()
    {
        /** @var Dispatcher $eventDispatcher */
        $eventDispatcher = $this->app->make(Dispatcher::class);

        foreach ($this->subscribers as $subscriber) {
            foreach ($this->resolveListeners($subscriber) as [$event, $listener]) {
                $eventDispatcher->listen($event, $listener);
            }
       }
    }

    private function resolveListeners(string $subscribeClass): array
    {
        return $this->app->make(ResolveListeners::class)->resolve($subscribeClass);
    }
}
```

1. The `$subscribers` array holds all the subscribers. Please don’t mix it with Laravel’s `$subscribe` property used to register the subscribers.
2. The `$eventDispatcher` gets the event dispatcher from the container.
3. We’ll iterate over the `$subscibers` and resolve it one by one and then we send it to the event dispatcher using the `listen` method.

All done, let’s try it out:
```php
// routes/web.php

Route::get('/test_event', function() {
    \Illuminate\Support\Facades\Auth::login(\App\Models\User::find(1));
    \Illuminate\Support\Facades\Auth::logout();
});
```

Head up to the  `storage/logs/laravel.log` file, and you should see the following entries:

```text
[2021-02-21 14:03:02] local.DEBUG: User logged in: 1  
[2021-02-21 14:03:02] local.DEBUG: User logged out: 1  
```

That’s it.

I hope you enjoyed this post. Keep an eye on the upcoming posts.
