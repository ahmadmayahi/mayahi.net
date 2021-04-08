A few weeks ago, I wanted to use JSON Web Token into one of my Laravel projects.

After a bit of research, I found some composer packages, but I was thinking why do I need a package for such a simple thing?

To be honest, I’m not a big fan of using composer packages for every single problem I encounter.

Jwt provides an official PHP support via the `firebase/php-jwt` composer library which does all the heavy lifting (encoding/decoding).

> If you like/want to use composer packages then this post is not for you, since I don’t use any other packages rather than the `firebase/php-jwt`.

I will be using Laravel 8 as well as SQLite database, so, you may need to create a new Laravel project:

```bash
laravel new jwt
cd jwt
composer require laravel/ui "^2.0"
php artisan ui bootstrap --auth && npm install && npm run dev
```

> You are free to use the appropriate database driver that suits your needs, but I’ll stick with SQLite.

## Setting up the database
Let’s create our SQLite database:

```bash
cd jwt/database
sqlite3 database.sqlite "create table t(id int); drop table t;"
```

SQLite doesn’t allow us to create empty databases, therefore I created a new table and dropped it at the same time to have an empty database.

Update your `.env` and set the `DATABASE_CONNECTION` to sqlite.

We do need some users for testing, so, open up the `database/seeds/DatabaseSeeder.php` and add the following line:

```php
factory(App\User::class, 10)->create();
```

Run the migrations and the seeders:

```php
php artisan migrate:fresh --seed
```

## Authentication Guards in Laravel
Laravel guard acts like a real guard sitting in front of the entrance door, searching people for a valid ID.

Since we are creating a new authentication mechanism, we need to create a new guard that can be used to check the incoming request, inspect it and validate the Jwt token.

Laravel provides two ways of creating guards, the easiest one is by using closures, so let’s see try it out.

Open up your `AuthServiceProvider` and add the following code inside the boot method:

```php
 \Auth::viaRequest('email', function ($request) {
    return App\User::where('email', $request->email)->first();
 });
```

The guard has to return a `User` model, if the user couldn’t be found, then a value of null has to be returned.

Open up the `config/auth.php` file and add the newly added guard into the guards section:

```php
'guards' => 
    'email' => [
            'driver' => 'email',
            'provider' => 'users'
    ]
]
```

Let’s see how do we use it.

Open up your `routes/web.php` file and add the following code:

```php
Route::get('/dashboard', function() {
    return response('Hello '.\Auth::user()->name);
})->middleware('auth:email');
```

By using the `middleware('auth:email')` we are telling Laravel to use the `email` guard, easy peasy.

Let’s try it out by running Laravel’s internal server:

```php
php artisan serve
```

Try to access the dashboard route, and you’ll see that you’ve being redirected to the login page, that is because you didn’t provide a valid email address.

Let’s try it again, but this time we'll provide a valid email address.

Get an email address from the database:

```bash
sqlite3 database/database.sqlite "select email from users limit 1"
```

Copy the returned email address, and then try to access the dashboard route with an email address:

```text
http://127.0.0.1:8000/test?email=cmarquardt@example.org
```

You should be able to see the content, which is `Hello {user.name}`.

The other way of adding a new guard is by using the Auth::extend method; by using this method, we should return an object that implements the `Illuminate\Contracts\Guard interface`.

You may take a look at the guard interface to see what kind of methods has to be implemented.

## What is JSON Web Token?
In its simplest terms, `JSON Web Token` (`Jwt`) is a base64-encoded JSON that is encrypted by one of the supported algorithms such as `HS256`, `RS256`, etc... This means that nobody can tamper with the data without having the decryption key.

While Jwt can be used for anything, it is mostly used as an authentication/authorization mechanism.

Once the user is logged in by her username and password, a new JSON Web Token will be sent back to her, and then she may use this token to perform other protected actions, such as updating her profile, inserting new data, and so on.

The token could have an expiration date.

You may ask how Laravel knows that the received token belongs to a specific user?

Before I answer this question, let’s inspect the Jwt.

Jwt consists of three main parts:

- **Header**: specifies the encrypted algorithm such as HS256, RS256, etc…
- **Payload**: the actual data that we need to exchange, such as the user id, password, etc…
- **Signature**: is created by combining the header, payload and the secret key.

Sounds confusing? so, Let’s break it down.

Header: is the easiest part, which specifies the algorithm such as `HS256` as well as the type (which is always JWT):
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Payload: contains the claims. The `claims` describes the entity (typically, the user), claims could be divided into three parts, only two parts of them are needed:

- **Registered Claims**: a set of predefined claims which are not mandatory but recommended, such as the expiration time (`exp`) and some other claims.
- **Private claims**: these are custom claims created to share information, such as the user id, user type, etc...

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "admin": true
}
```

**Signature**: is the signature created by taking the encoded header, the encoded payload, and sign them by the algorithm specified in the header (as well as the secret key).

```text
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

> The sub `claim` normally used to store the user id.

## Jwt Configurations

The very first thing you should be doing is installing the `firebase/php-jwt` package:

```bash
composer require firebase/php-jwt
```

We do need private and public keys, these keys will be used to encrypt/decrypt the payload.

I usually put these keys into the storagedirectory, but it’s up to you to choose the appropriate directory path:

```bash
cd ~my-jwt-project/storage
ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key
openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub
```

Create a new config file in config/jwt.php:

```php
<?php

return [
    'private_key' => storage_path('jwtRS256.key'),

    'public_key' => storage_path('jwtRS256.key.pub'),

    'ttl' => 86400, // in seconds

    'leeway' => 60, // in seconds

    'encrypt_algo' => 'RS256',

    'allowed_algo' => ['RS256']
];
```

> As you can see, I use the `RS256` algorithm, if you want to use a different one, then consider looking at the supported algorithms.

> If you want to know more about the leeway option, then consider reading the nbf claim. I think one minute is sufficient for clock skew.

To make it simple and straightforward, I will start by creating three classes:

- `JwtBuilder`: this class will be responsible for creating the token by using some convenient methods.
- `JwtParser`: reads the given token, and decrypts it.
- `JwtGuard`: this is the Laravel guard which is used to authenticate the user via the token.
- `JwtAuth`: authenticates the user.

## JwtBuilder

`JwtBuilder` is a wrapper around the claims, it provides some convenient methods, for example, calling relatedTo is more readable than aud.

I also added the `claims` descriptions for each method.

Create a new class `app/Services/Jwt/JwtBuilder.php`:

```php
<?php

namespace App\Services\Auth;

use Carbon\CarbonInterface;
use Firebase\JWT\JWT;

class JwtBuilder
{
    protected $claims;

    /**
     *  The "iss" (issuer) claim identifies the principal that issued the
     *  JWT.  The processing of this claim is generally application specific.
     *  The "iss" value is a case-sensitive string containing a StringOrURI
     *  value.  Use of this claim is OPTIONAL.
     *
     * @param $val
     * @return $this
     */
    public function issuedBy($val): self
    {
        return $this->registerClaim('iss', $val);
    }

    /**
     * The iat (issued at) claim identifies the time at which the JWT was issued.
     * This claim can be used to determine the age of the JWT.
     * Its value MUST be a number containing a NumericDate value. Use of this claim is OPTIONAL.
     *
     * @param $val
     * @return $this
     */
    public function issuedAt($val)
    {
        return $this->registerClaim('iat', $val);
    }

    /**
     *  The "sub" (subject) claim identifies the principal that is the
     *  subject of the JWT.  The claims in a JWT are normally statements
     *  about the subject.  The subject value MUST either be scoped to be
     *  locally unique in the context of the issuer or be globally unique.
     *  The processing of this claim is generally application specific.  The
     *  "*sub" value is a case-sensitive string containing a StringOrURI
     *  value.  Use of this claim is OPTIONAL.
     *
     * @param $val
     * @return $this
     */
    public function relatedTo($val)
    {
        return $this->registerClaim('sub', $val);
    }

    /**
     * The aud (audience) claim identifies the recipients that the JWT is intended for.
     * Each principal intended to process the JWT MUST identify itself with a value in the audience claim.
     * If the principal processing the claim does not identify itself with a value in the aud claim when this
     * claim is present, then the JWT MUST be rejected. In the general case, the aud value is an array
     * of case-sensitive strings, each containing a StringOrURI value.
     * In the special case when the JWT has one audience, the aud value MAY be a single case-sensitive string
     * containing a StringOrURI value. The interpretation of audience values is generally application specific.
     * Use of this claim is OPTIONAL.
     *
     * @param $name
     * @return $this
     */
    public function audience($name)
    {
        return $this->registerClaim('aud', $name);
    }

    /**
     * The exp (expiration time) claim identifies the expiration time on or after which the JWT MUST NOT be accepted
     * for processing.
     * The processing of the exp claim requires that the current date/time MUST be before the expiration date/time
     * listed in the exp claim. Implementers MAY provide for some small leeway, usually no more than a few minutes,
     * to account for clock skew. Its value MUST be a number containing a NumericDate value. Use of this claim is OPTIONAL.
     *
     * @param CarbonInterface $dateTime
     * @return $this
     */
    public function expiresAt(CarbonInterface $dateTime)
    {
        return $this->registerClaim('exp', $dateTime->timestamp);
    }

    /**
     * The jti (JWT ID) claim provides a unique identifier for the JWT.
     * The identifier value MUST be assigned in a manner that ensures that there is a negligible probability that the
     * same value will be accidentally assigned to a different data object; if the application uses multiple issuers,
     * collisions MUST be prevented among values produced by different issuers as well. The jti claim can be used to
     * prevent the JWT from being replayed. The jti value is a case-sensitive string. Use of this claim is OPTIONAL.
     *
     * @param $val
     * @return $this
     */
    public function identifiedBy($val)
    {
        return $this->registerClaim('jti', $val);
    }

    /**
     * The nbf (not before) claim identifies the time before which the JWT MUST NOT be accepted for processing.
     * The processing of the nbf claim requires that the current date/time MUST be after or equal to the not-before
     * date/time listed in the nbf claim. Implementers MAY provide for some small leeway, usually no more than a
     * few minutes, to account for clock skew. Its value MUST be a number containing a NumericDate value.
     * Use of this claim is OPTIONAL.
     *
     * @param CarbonInterface $carbon
     * @return $this
     */
    public function canOnlyBeUsedAfter(CarbonInterface $carbon)
    {
        return $this->registerClaim('nbf', $carbon->timestamp);
    }

    public function withClaim($name, $value)
    {
        return $this->registerClaim($name, $value);
    }

    public function withClaims(array $claims): self
    {
        foreach ($claims as $name => $value) {
            $this->withClaim($name, $value);
        }
        return $this;
    }

    public function getToken()
    {
        return JWT::encode($this->claims, $this->getPrivateKey(), $this->getAlgo());
    }

    protected function getPrivateKey(): string
    {
        return file_get_contents(config('jwt.private_key'));
    }

    protected function getAlgo()
    {
        return config('jwt.encrypt_algo');
    }

    protected function registerClaim(string $name, string $val): self
    {
        $this->claims[$name] = $val;
        return $this;
    }
}
```

## JwtParser
The `JwtParser` takes a token, decodes it and saves it into the `$claims` property, then we can access these claims by some readable methods such as `getRelatedTo`.

Create a new class `app/Services/Jwt/JwtParser.php`:

```php
<?php

namespace App\Services\Auth;

use Firebase\JWT\JWT;

class JwtParser
{
    /**
     * @var array|object
     */
    protected $claims;

    public function __construct(string $token)
    {
        JWT::$leeway = $this->getLeeway();
        $this->claims = JWT::decode($token, $this->getPublicKey(), $this->supportedAlgos());
    }

    public static function loadFromToken(string $token)
    {
        return new self($token);
    }

    public function getIssuedBy()
    {
        return $this->getClaim('iss');
    }

    public function getIssuedAt()
    {
        return $this->getClaim('iat');
    }

    public function getRelatedTo()
    {
        return $this->getClaim('sub');
    }

    public function getAudience()
    {
        return $this->getClaim('aud');
    }

    public function getExpiresAt()
    {
        return $this->getClaim('exp');
    }

    public function getIdentifiedBy()
    {
        return $this->getClaim('jti');
    }

    public function getCanOnlyBeUsedAfter()
    {
        return $this->getClaim('nbf');
    }

    protected function getClaim(string $name)
    {
        return $this->claims->{$name} ?? null;
    }

    protected function getPublicKey(): string
    {
        return file_get_contents(config('jwt.public_key'));
    }

    protected function getAlgo()
    {
        return config('jwt.encrypt_algo');
    }

    protected function getLeeway()
    {
        return config('jwt.leeway');
    }

    protected function supportedAlgos()
    {
        return config('jwt.supported_algos');
    }
}
```

## JwtGuard
The guard contains the actual Jwt authentication process, what it does simply is reading the bear-token, decodes it, and loads the appropriate user by inspecting the sub claim.

The sub `claim` contains the user id, if you take a look at the `JwtAuth` you’ll see that the user id will be stored in the sub (releatedTo method).

Since the token is encrypted by `RSA256`, only we have the ability to decode it by the private key, so, we’re 100% sure that we can rely on the sub value.

```php
<?php

namespace App\Services\Auth;

use Illuminate\Auth\GuardHelpers;
use Illuminate\Contracts\Auth\{Guard, UserProvider};
use Illuminate\Http\Request;

class JwtGuard implements Guard
{
    use GuardHelpers;

    /**
     * @var Request
     */
    private $request;

    private $lastAttempted;

    public function __construct(UserProvider $provider, Request $request)
    {
        $this->provider = $provider;
        $this->request = $request;
    }

    public function user()
    {
        if (! is_null($this->user)) {
            return $this->user;
        }

        return $this->user = $this->authenticateByToken();
    }

    public function validate(array $credentials = [])
    {
        if (! $credentials) {
            return false;
        }

        if ($this->provider->retrieveByCredentials($credentials)) {
            return true;
        }

        return false;
    }

    protected function authenticateByToken()
    {
        if (! empty($this->user)) {
            return $this->user;
        }

        $token = $this->getBearerToken();

        if (empty($token)) {
            return null;
        }

        try {
            $decoded = $this->authenticatedAccessToken($token);

            if (! $decoded) {
                $user = null;
            } else {
                $user = $this->provider->retrieveById($decoded->getRelatedTo());
            }

        } catch (\Exception $exception) {
            logger($exception);
            $user = null;
        }

        return $user;
    }

    protected function getBearerToken()
    {
        return $this->request->bearerToken();
    }

    public function attempt(array $credentials = [], $login = true)
    {
        $this->lastAttempted = $user = $this->provider->retrieveByCredentials($credentials);

        if ($this->hasValidCredentials($user, $credentials)) {
            $this->user = $user;
            return true;
        }

        return false;
    }

    protected function hasValidCredentials($user, $credentials)
    {
        return $user !== null && $this->provider->validateCredentials($user, $credentials);
    }

    public function authenticatedAccessToken($token)
    {
        return JwtParser::loadFromToken($token);
    }
}
```

## JwtAuth
This class is used to generate the Jwt upon the successful authentication, this means that the `authenticateAndReturnJwtToken` method has to be called within a controller

Create a new class `app/Services/Jwt/JwtAuth.php`:

```php
<?php

namespace App\Services\Jwt;

use App\Services\Auth\JwtBuilder;
use App\User;
use Carbon\CarbonInterface;
use Illuminate\Support\Facades\Auth;

class JwtAuth
{
    public function authenticateAndReturnJwtToken(string $email, string $password): ?string
    {
        if (! Auth::attempt(['email' => $email, 'password' => $password])) {
            return false;
        }

        try {
            /** @var User $user */
            return $this->createJwtToken(Auth::user());

        } catch (\Throwable $exception) {
            logger($exception->getMessage());
            return false;
        }
    }

    protected function createJwtToken(User $user, CarbonInterface $ttl = null): string
    {
        return (new JwtBuilder())
            ->issuedBy(config('app.url'))
            ->audience(config('app.name'))
            ->issuedAt(now())
            ->canOnlyBeUsedAfter(now()->addMinute())
            ->expiresAt($ttl ?? now()->addSeconds(config('jwt.ttl')))
            ->relatedTo($user->id)
            ->getToken();
    }
}
```

## Putting all together
Let’s it put all together and start by creating the `AuthController`.

The `AuthController` is responsible for authenticating the user by using the default guard (`web`), if it succeeds, then a new token will be sent back to the user.

So, let’s get started:

```bash
php artisan make:controller AuthController
```

```php
<?php

namespace App\Http\Controllers;

use App\Services\Jwt\JwtAuth;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class AuthController extends Controller
{
    public function __invoke(Request $request, JwtAuth $jwtAuth)
    {
        $valid = Validator::make($request->all(), [
            'email'     => 'required|email|exists:users,email',
            'password'  => 'required|string|min:8',
        ]);

        if ($errors = $valid->errors()->all()) {
            return response()->json(['errors' => $errors], 400);
        }

        if ($token = $jwtAuth->authenticateAndReturnJwtToken($request->email, $request->password)) {
            return response()->json(['token' => $token]);
        }

        return response()->json(['errors' => 'Cannot authenticated!'], 400);
    }
}
```

Add the authentication route in routes/api.php file:

```php
Route::post('auth', 'AuthController')->name('jwt.auth');
```

Let’s try it out:

```php
curl --location --request POST 'http://127.0.0.1:8000/api/auth' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data-raw '{
    "email" : "myemail@example.com",
    "password" : "password"
}'
```

If the authentication process succesed, then you’d see see the token:

```json
{
    "token": "{jwt token goes here}"
}
```

Now we’ve got the token, let’s see how could we use this token to authenticate.

Open you the routes/api.php and add the following route:

```php
Route::get('/user', function() {
    return \Auth::user();
})->middleware('auth:jwt');
```

Now, try to authenticate via the generate token:

```bash
curl --location --request GET 'http://127.0.0.1:8000/api/user' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer {generate token goes here}'
```

If the authentication succeed, then you’ll see the authenticated user information:

```json
{
    "id": 1,
    "name": "Elissa Dickens",
    "email": "janice.harber@example.net",
    "email_verified_at": "2020-03-17T11:00:06.000000Z",
    "created_at": "2020-03-17T11:00:06.000000Z",
    "updated_at": "2020-03-17T11:00:06.000000Z"
}
```

## Conclusion

JSON Web Token is a powerful yet simple authentication mechanism, you can also use it to exchange some data rather than the authentication.

If you have a SPA/mobile app then you might need to look at the Sanctum package.

Sanctum is a first party Laravel package created by the Taylor Otwell, it’s aim is to provide a simple API authentication for SPA/mobile etc
