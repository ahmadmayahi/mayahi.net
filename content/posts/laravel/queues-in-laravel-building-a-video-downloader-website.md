Imagine you are building a website that can download videos from several video providers such as Youtube, Vimeo, etc. it’s all start by asking the guest to enter a valid video link. Then the website will download that particular video file and sends it back to the web browser. Easy peasy.

![Queues in Laravel](./static/img/laravel/queues-in-laravel-building-a-video-downloader-website/001.png)

Without a queueing system, we’re going to have a big problem, to be honest, it’s impossible to create such a website without queuing.

But why queueing is important?

It’s because the heavy processing requests need to be run asynchronously, so the user won’t be waiting for a very long time until the web browser sends back the requested file.

In addition to that, If the user requests a large file, then he might get an error indicating that the request cannot be accomplished due to 504 Gateway Time-out.

![Queues in Laravel](./static/img/laravel/queues-in-laravel-building-a-video-downloader-website/002.png)


So, how could we improve our websites by letting the time-consuming processes to be run in the background?

## Sync. vs Async.

Before we dive into Laravel queues, let’s discover two important terms.

Synchronous (abbr. sync): when you execute something synchronously, you wait for it to finish before moving on to another task.

The signing up process is a good example; when the user signs up, she waits until her data will be saved into the database and then she’ll be notified immediately. 

Asynchronous (abbr. async): When you execute something asynchronously, you can move on to another task before it finishes.

An example is uploading a video file on youtube, it’ll take some time until youtube finishes processing the video file.

In this post, I’ll show you how could you build a youtube download by using queues, so, let’s get started.


## Let’s build a video downloader

Let’s put the queues into practice and get our hands dirty by creating a real project.

In this project, I will be using youtube-dl to download the videos; youtube-dl supports a variety of websites, such as Youtube, Vimeo, Facebook, etc, so, I suppose that you have youtube-dl installed on your computer.

So, let’s get started by creating a new Laravel project:

```bash
laravel new video-downloader
cd video-downloader
```

> Refer to the documentation to install the Laravel installer.

We need at least two controllers, one for viewing the home page and the other one to take care of the video requests:

```bash
php artisan make:controller HomeController
php artisan make:controller DownloaderContoller
```

We need to store the downloaded videos somewhere into our project, so, go ahead and create a new folder named downloads inside the storage/app/public folder:

```bash
mkdir storage/app/public/downloads
php artisan storage:link
```

We do need a few routes for c

Replace the routes/web.php file with the following contents:

```php
Route::get('/', 'HomeController')->name('home');
Route::post('prepare', 'DownloaderController@prepare')->name('prepare');
Route::get('status/{video}', 'DownloaderController@status')->name('status');
Route::get('download/{video}', 'DownloaderController@download')->name('download');
```

Create a new view named base.blade.php with the following contents:


```php
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Video downloader</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
          integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
</head>
<body>

<main role="main">
    <div class="container">
        <div class="row">
            <div class="col-6 text-center" style="margin: 0 auto;">
                <h1 class="mt-5">@yield('title')</h1>
                @yield('content')
            </div>
        </div>
    </div>
</main>

</body>
</html>
```

Create a new view named home.blade.php with the following contents:

```php
@extends('base')
@section('title', 'Video Downloader')

@section('content')
    <form method="post" action="{{ route('prepare') }}">
        @csrf

        @if(Session::has('error'))
            <div class="alert alert-danger">{{ Session::get('error') }}</div>
        @endif

        <div class="form-group">
            <input name="url" type="text" required class="form-control @error('url')  is-invalid @enderror" id="url"
                   aria-describedby="url" value="{{ old('url') }}"
                   autocomplete="off" autofocus>

            @error('url')
                <div class="invalid-feedback">{{ $message }}</div>
            @enderror
        </div>

        <div class="text-center">
            <button class="btn btn-lg btn-primary">Download</button>
        </div>
    </form>
@endsection
```

Open the DownloaderController and replace it with the following contents:

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;

class DownloaderController extends Controller
{
    public function prepare(Request $request)
    {
        $this->validate($request, [
           'url' => 'required'
        ]);

        try {
            $process = new Process([
                'youtube-dl',
                $request->url,
                '-o',
                storage_path('app/public/downloads/%(title)s.%(ext)s')
                , '--print-json'
            ]);

            $process->mustRun();

            $output = json_decode($process->getOutput(), true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new \Exception("Could not download the file!");
            }

            return response()->download($output['_filename']);

        }  catch (\Throwable $exception) {
            $request->session()->flash('error', 'Could not download the given link!');
            logger()->critical($exception->getMessage());
            return back();
        }
    }
}
```

> –print-json instructs youtube-dl to output the video information in JSON format while the video is still being downloaded; I’ll save this piece of information into the database for any future usages such as getting the video title, thumbnail, etc..

Let’s run our project by issuing php artisan serve.

Try to enter some valid video links (could be from Youtube, Vimeo, Facebook, etc…).

Depending on your internet connection (as well as the video size); it might take a few seconds to download the video and then send it back to the user.

In addition to that, a few users might be using the website at the same time, so, it’s impossible to handle all these connections synchronously without crashing the webserver.

Let’s see how could we improve this piece of code by running it asynchronously.


## Setting up the queues

Unlike some other PHP frameworks, working with queues in Laravel is a cinch.

The whole idea behind queues is that you tell Laravel to run a specific job in the background instead of running it synchronously, Laravel will run the job and let you know whether it succeeded or not.

Laravel supports a variety of queue drivers, and these drivers can be easily configured in the app/queue.php file, Laravel supports Redis, database, Amazon SQS, Beanstalkd out of the box.

The queue driver can be set by modifying the QUEUE_CONNECTION in .env file to the appropriate driver; By default the QUEUE_CONNECTION is set to sync which means no queuing.

You’re free to use whatever driver that suits you, for this post, I’ll stick with the database driver, so, open up your .env file and change QUEUE_CONNECTION to database.

In order to use the database driver, you need a table that holds the jobs, this table can be easily created by running php artisan queue:table followed by php artisan migrate.

## Dispatching Jobs

While it is not always the case, the dispatching term refers to running a piece of code async. That’s it.

You can use the dispatch helper to run any piece code asynchronously, this means that the queue will pick up your code and run it later.

> “later” is not always the case, if the value of QUEUE_CONNECTION in .env file is set to sync then no jobs will be queued, and all the dispatched jobs will be run immediately, this is helpful while testing, take a look at the phpunit.xml and you’ll see that the queue is set to sync.

Let’s try the dispatch helper, open up your routes/web.php and add the following route:

```php
# routes/web.php
Route::get('/queue', function() {
    dispatch(function() {
        logger('Running our first job!');
    });
});
```
Try to hit this route, yes, nothing happens, this is because we don’t have any worker running yet, but before I show you how to fix that, let’s see what other functions does the dispatch function provide.

|Option|Description|
|---|---|
|`delay`|Use this function if you’d like to run the job on a specific date/time.|
|`onQueue`|You might have different queues for different purposes, such as emails, videos, etc…<br>The queue is just a name that can be used for categorizing your jobs, if you don’t specify any value, then the default value will be used.|

In the database case, Laravel stores all the jobs in the jobs table, so let’s inspect this table and see what does it contain.

![Queues in Laravel](./static/img/laravel/queues-in-laravel-building-a-video-downloader-website/003.png)


As you see here, we have one none-executed job, since we don’t have any running workers yet, this job will never be executed.

> You can also use Job::dispatch() which is doing the exact same thing as the dispatch helper.

> I highly encourage you to use the job classes instead of closures, I’ll show you how to do that later.

## Workers
The worker is just a daemon running in the background.

The sole responsibility of the worker is to pick up the next available job and execute it either immediately or after a specific date/time (if delay has been applied).

Let’s run the worker:

```bash
php artisan queue:work
```

If the job was executed successfully, then you have to see a new log entry in the storage/logs/laravel.log:

```text
[2020-02-28 12:05:02] local.DEBUG: Just for testing. 2020-02-28 12:05:02  
```

You may specify the queue name while running the worker; this is useful when you have multiple queues:

```bash
# Only emails queue
php artisan queue:work --queue="emails"

# Run emails jobs first and then pickup the videos jobs
php artisan queue:work --queue="emails,videos"
```
You may instruct the worker to only run the next available job by using --once, this command is useful when the worker is not running.


## Job classes
In addition to the closure, dispatch can also take an object that implements the `Illuminate\Contracts\Queue\ShouldQueue` interface, you may either create your own class which implements the ShouldQueue interface or use the `php artisan make:job` to let Laravel do that for.

So, let’s put our video downloading code into a dedicated job:

```bash
php artisan make:job DownloadVideo
```

Laravel stores all the jobs in the app/Jobs folder.

The handle method is responsible for executing the job, so, all your job’s code has to be inside this method, otherwise, the job won’t be executed.

The handle will be resolved by the container, this means that you can use dependency injection to resolve any other classes:

```php
public function handle(FileSystem $fileSystem)
{
    // Use filesystem here.
}
```
The job class uses the Dispatchable trait, this means that you can dispatch the job directly from the job itself, without passing it to the dispatch() or Job::dispatch functions:

```php
DownloadVideo::dispatch();
```

If you don’t want to dispatch your jobs like that, so, consider removing the Dispatchable trait; I like to dispatch the job directly from the class, anyway, it’s a preference rather than best practice.


## The video model
Since the video will be downloaded asynchronously, we do need a way of keeping track of it.

When the user enters a video link and hits Download then we should save the video link into the database and then push it to the queue.

The queue will pick up the job, run it, and based on the information given by youtube-dl it’ll set the video’s status to one of these values: in_progress, completed and failed as well as storing the video’s information (such as thumbnail, title, description, etc).

So, let’s start creating the Video model:
```bash
php artisan make:migration create_videos_table
```

```php
public function up()
{
    Schema::create('videos', function (Blueprint $table) {
        $table->uuid('id')->unique();
        $table->string('url');
        $table->enum('status', ['in_progress', 'failed', 'completed'])->default('in_progress');
        $table->json('info')->nullable();
        $table->timestamps();
    });
}
```

``bash
php artisan make:model Video
``

```php
<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Video extends Model
{
    protected $keyType = 'uuid';

    public $incrementing = false;

    protected $guarded = [];

    public function getInfoAttribute($value)
    {
        return json_decode($value, false, JSON_THROW_ON_ERROR);
    }
}
```

## Downloader Job
The downloader job is responsible for downloading the given video by call the youtube-dl command.

If the downloading command succeed, then we update the video’s status as well as inserting the video’s information

```bash
php artisan make:job DownloadVideo
```

```php
<?php

namespace App\Jobs;

use App\Video;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Symfony\Component\Process\Process;
use Throwable;

class DownloadVideo implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * @var Video
     */
    private $video;

    /**
     * Create a new job instance.
     *
     * @param Video $video
     */
    public function __construct(Video $video)
    {
        $this->video = $video;
    }

    /**
     * Execute the job.
     *
     * @return void
     * @throws \Exception
     */
    public function handle()
    {
        $process = new Process([
            'youtube-dl',
            $this->video->url,
            '-o',
            storage_path('app/public/videos/%(title)s.%(ext)s')
            , '--print-json'
        ]);

        try {
            $process->mustRun();

            $output = json_decode($process->getOutput(), true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                $this->video->status = 'failed';
            } else {
                $this->video->status = 'completed';
                $this->video->info = $output;

                $this->video->save();
            }
        } catch (Throwable $exception) {
            $this->video->status = 'failed';
            $this->video->save();
            logger(sprintf('Could not download video id %d with url %s', $this->video->id, $this->video->url));

            throw new $exception;
        }
    }
}
```

## Dispatching the job through the DownloaderController

Open up the DownloaderController and replace its contents with the following:


```php
<?php

namespace App\Http\Controllers;

use App\Jobs\DownloadVideo;
use App\Video;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class DownloaderController extends Controller
{
    public function prepare(Request $request)
    {
        $this->validate($request, [
           'url' => 'required|url'
        ]);

        $video = Video::create([
            'url' => $request->input('url')
        ]);

        DownloadVideo::dispatch($video);

        return redirect()->route('status', ['video' => $video]);
    }

    public function status(Video $video)
    {
        return view('status', ['video' => $video]);
    }

    public function download(Video $video)
    {
        abort_if($video->status !== 'completed', 404);

        return response()->download($video->info->_filename);
    }
}
```

Let’s explain the actions:

- prepare: stores the requested video into the database and passes it to the DownloadVideo job.
- status: shows the video’s status, so, if the video was downloaded, then the download link will be presented.
- download: downloads the requested video by reading the _filename property from the stored JSON object that was returned by youtube-dl.
We do miss the status view, so, create a new file named status.blade.php and replace its contents with the following:

```blade
@extends('base')

@section('content')

    @if ($video->status == 'completed')
        <h3>{{ $video->info->title }}</h3>
        <img src="{{ $video->info->thumbnail }}">
        <h3>Click <a href="{{ route('download', ['download' => $video]) }}">here</a> to download it</h3>
    @endif

    @if($video->status == 'in_progress')
        <h3>Download in progress..</h3>
        <p>Please <a href="javascript:;" onclick="window.reload()">refresh</a> this page in a few seconds.</p>
    @endif

    @if ($video->status == 'failed')
        <h3>Download failed!</h3>
        <p>Please try again, if the problem persist, then please contact us.</p>
    @endif

@endsection
```

Go ahead and download some videos.

![Queues in Laravel](./static/img/laravel/queues-in-laravel-building-a-video-downloader-website/006.gif)

Instruct the worker to pickup only the first available job:

```bash
php artisan queue:work --once
```

Wait until the job finishes:

![Queues in Laravel](./static/img/laravel/queues-in-laravel-building-a-video-downloader-website/004.png)

Go back to the web browser and refresh the page:
![Queues in Laravel](./static/img/laravel/queues-in-laravel-building-a-video-downloader-website/005.png)

Click Download and enjoy.

## Error Handling
What if youtube-dl couldn't download the requested video? what is going to happen in such a case?

If you take a look at the DownloadVideo job, you can see that the process is set to me mustRun, so, if it fails an exception of type ProcessFailedException will be thrown.

> If an exception is thrown while the job is being processed, the job will automatically be released back onto the queue so it may be attempted again.

You can instruct Laravel to retry the failed job for certain times, this can be done either by instructing the worker or by using the $tries property into our job:

```bash
php artisan queue:work --retry=3
```

```php
class DownloadVideo implements ShouldQueue
{
     public $tries = 3;
}
```

Laravel stores the failed jobs into the failed_jobs table, so, consider inspecting this table to know more information about your failed job.

## Testing

By default the QUEUE_CONNECTION option is set to sync in phpunit.xml file, this means that the jobs will be run immediately (no queuing):

```xml
<server name="QUEUE_CONNECTION" value="sync"/>
```

Since the video will be downloaded from the internet, we need a way to mock it, well, we don’t really need to do that, since Laravel already provide job faking capability out of the box.

Let’s see how it works by writing a simple unit test that tests the prepare action:

```bash
php artisan make:test DownloadVideoTest
```

Replace the tests/Feature/DownloadVideoTest with the following contents:

```php
<?php

namespace Tests\Feature;

use App\Jobs\DownloadVideo;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Illuminate\Support\Facades\Bus;
use Illuminate\Support\Facades\DB;
use ReflectionClass;
use Tests\TestCase;

class DownloadVideoJobTest extends TestCase
{
    use RefreshDatabase, WithFaker;

    /** @test */
    public function ensure_the_video_download_job_is_dispatched()
    {
        Bus::fake();

        $url        = $this->faker->url;
        $response   = $this->post(route('prepare'), compact('url'));
        $video      = DB::table('videos')->where('url', $url)->first();

        $response->assertRedirect(route('status', ['video' => $video->id]));
        $response->assertSessionHasNoErrors();

        Bus::assertDispatched(DownloadVideo::class, function($job) use ($video) {
            return $this->getPrivateProperty($job, 'video')->id === $video->id;
        });
    }

    protected function getPrivateProperty(object $obj, string $property)
    {
        $reflection = new ReflectionClass($obj);
        $privateProperty = $reflection->getProperty($property);
        $privateProperty->setAccessible(true);

        return $privateProperty->getValue($obj);
    }
}
```
Run the test:
```bash
./vendor/bin/phpunit
```

Let’s see what does this code do.

First of all, we started our test case by instructing Laravel to prevent the job from being dispatched by using the Bus::fake().

By using the Bus::assertDispatched method, we assert that the DownloadVideo job is dispatched.

Bus::assertDispatched is a closure that provides the actual job as its first parameter, so, we can compare the dispatched video with the one that we’ve created.

So far so good, but what about the crazy $this->getPrivateProperty(...); line?

```php
return $this->getPrivateProperty($job, 'video')->id === $video->id;
```

Since the $video property is private, I needed a way to make it publicly accessible, so, I can read its value, therefore I’ve used the reflection class.

## Deploying
Nowadays, Docker is so popular, and many people use supervisor to manage multiple processes, if that’s your case, then consider putting the Laravel worker into the supervisor, this approach is thoroughly explained in Laravel documentation.

If you don’t use Docker, then you might need to run the worker with the systemd, this is also explained thoroughly in this post.

> I highly encourage you to use Laravel Horizon, if you use Redis as a queuing driver.

## Conclusion
Congratulations, you’ve well-equipped with the essential knowledge of the queues.






