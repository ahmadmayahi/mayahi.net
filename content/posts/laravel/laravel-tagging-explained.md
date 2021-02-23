According to Laravel’s documentation, tagging used to resolve a particular **category of binding**.

For example, you could group `CpuReport`, `MemoryReport`, and `DiskReport` under a tag named `reports`.

But that’s still vague for many developers.

In this post, I will explain the tagging by looking discovering a real-world example, so let’s get started.

## Scanning a file using different OCRs
In one of my side projects, I used the following OCR systems to scan the uploaded document:
- Google Vision.
- Amazon Textract.
- Tesseract.

Using multiple OCRs increases the scanning accuracy; therefore, it gives the user the best possible results.

After a bit of thinking, I realized that the OCRs list is subject to change; for example, I might need to remove `Tesseract` and replace it with something else, such as `Abbyy`. Maybe I need to add both `Abbyy` and `MicrosoftComputerVision`.

If I explicitly type-hint the dependencies, then my `Recognizer` class would look like this:
```php
class Recognizer
{
    public function __construct(
        private GoogleVision $googleVision,
        private AmazonTextract $amazonTextract,
        private Tesseract $tesseract
    )
    {
    }
}
```

And let’s say that I need to add two more OCRs, `Abbyy` and `MicrosoftComputerVision`, then I have no choice but modifying the `__constructor` :
```php
class Recognizer
{
    public function __construct(
        private GoogleVision $googleVision,
        private AmazonTextract $amazonTextract,
        private Tesseract $tesseract,
        
        // New OCRs
        private MicrosoftVision $microsoftVision,
        private Abbyy $abbyy,
    )
    {
    }

    public function recognize(File $file)
    {
        // recognize
    }
}
```

What if I need to get rid of `Tesseract`? Again, I have to open the `Recognizer` class and remove it from the `__constructor`.

Fortunately,  the OCR classes implement the `App\Contracts\OCR` interface:
```php
interface OCR
{
    public function recognize(File $file): RecognizedFile;
}
```

This means that the `recognize` method is available for all the OCR classes:
```php
class Recognizer
{
    public function __construct(
        private GoogleVision $googleVision,
        private AmazonTextract $amazonTextract,
        private Tesseract $tesseract,
        private MicrosoftVision $microsoftVision,
        private Abbyy $abbyy,
    )
    {
    }

    public function recognize(File $file)
    {
        $this->googleVision->recognize($file);
        $this->amazonTextract->recognize($file);
        $this->tesseract->recognize($file);
        $this->microsoftVision->recognize($file);
        $this->abbyy->recognize($file);
    }
}
```

## Tagging the OCR classes
Instead of using dependency injection by type-hinting the OCR classes and then calling the `recognize method on each one of them, I can easily create a group that contains the supported OCR as follows:
```php
class AppServiceProvider
{
    public function register()
    {
        $this->app->tag([
            GoogleVision::class, 
            AmazonTextract::class, 
            Tesseract::class
        ], 'ocrs');
    }
}
```

This grouping is called [tagging](https://laravel.com/docs/container#tagging).

Then I will inject the tagged classes into  `App\Support\Recognizer` as follows:
```php
// AppServiceProvider
// register() method
$this->app->bind(Recognizer::class, function() {
    return new Recognizer(...$this->app->tagged('ocrs'));
});
```

Since the `$this->app->tagged` returns an `Iterator`. I can use the array spread operator `…` to inject all the tagged dependencies.

The `...` operator spreads the array elements and pass them individually to the `Recognizer` object.

Let’s modify the `Recoginzer` class to have the new changes:
```php
class Recognizer
{
    public function __construct(App\Contracts\OCR ...$ocrs)
    {
    }

    public function recognize(File $file)
    {
        foreach ($this->ocrs as $ocr) {
            $ocr->recognize($file);
        }
    }
}
```

As you can see, the class became more maintainable than the previous implementation, if we got a new OCR then all we need to do is to add into the `ocrs` tag, that’s it.

I hope you enjoyed reading this post; keep an eye on the upcoming posts.
