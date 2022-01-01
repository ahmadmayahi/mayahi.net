Google Vision provides elegant image analysis services based on AI.

Although, it provides a PHP support through their official [google-cloud-php-vision](https://github.com/googleapis/google-cloud-php-vision) package, I was not satisfied with the amount of code that I need to write in order to analyze an image.

For example, if I want to use the web detection feature, then I should write something like this:
```php
$imageAnnotator = new ImageAnnotatorClient();

# Annotate the image
$image = file_get_contents($path);
$response = $imageAnnotator->webDetection($image);
$web = $response->getWebDetection();

// Print best guess labels
printf('%d best guess labels found' . PHP_EOL,
    count($web->getBestGuessLabels()));
foreach ($web->getBestGuessLabels() as $label) {
    printf('Best guess label: %s' . PHP_EOL, $label->getLabel());
}
print(PHP_EOL);

// Print pages with matching images
printf('%d pages with matching images found' . PHP_EOL,
    count($web->getPagesWithMatchingImages()));
foreach ($web->getPagesWithMatchingImages() as $page) {
    printf('URL: %s' . PHP_EOL, $page->getUrl());
}
print(PHP_EOL);

// Print full matching images
printf('%d full matching images found' . PHP_EOL,
    count($web->getFullMatchingImages()));
foreach ($web->getFullMatchingImages() as $fullMatchingImage) {
    printf('URL: %s' . PHP_EOL, $fullMatchingImage->getUrl());
}
print(PHP_EOL);

// Print partial matching images
printf('%d partial matching images found' . PHP_EOL,
    count($web->getPartialMatchingImages()));
foreach ($web->getPartialMatchingImages() as $partialMatchingImage) {
    printf('URL: %s' . PHP_EOL, $partialMatchingImage->getUrl());
}
print(PHP_EOL);

// Print visually similar images
printf('%d visually similar images found' . PHP_EOL,
    count($web->getVisuallySimilarImages()));
foreach ($web->getVisuallySimilarImages() as $visuallySimilarImage) {
    printf('URL: %s' . PHP_EOL, $visuallySimilarImage->getUrl());
}
print(PHP_EOL);

// Print web entities
printf('%d web entities found' . PHP_EOL,
    count($web->getWebEntities()));
foreach ($web->getWebEntities() as $entity) {
    printf('Description: %s, Score %s' . PHP_EOL,
        $entity->getDescription(),
        $entity->getScore());
}
```

> This example was taken from [php-docs-sample](https://github.com/GoogleCloudPlatform/php-docs-samples/blob/master/vision/src/detect_web.php).

Additionally, I also needed to test my code by mocking many objects, which is an insane job.

Therefore, I decided to create a wrapper around google vision API, so I don't need to write a lot of lines to achieve a simple thing.

Welcome to [PHP Google Vision](https://github.com/ahmadmayahi/php-google-vision), an elegant wrapper around Google Vision API.

The purpose of creating this package it to make Google Vision easy and fun to work with.

For example, let's see how to use the web detection feature:
```php
use AhmadMayahi\Vision\Vision;
use AhmadMayahi\Vision\Enums\Color;
use AhmadMayahi\Vision\Enums\Font;
use AhmadMayahi\Vision\Support\Image;
use AhmadMayahi\Vision\Data\LocalizedObject;

$response = Vision::init($config)
    ->file('/path/to/input/image.jpg')
    ->webDetection()
    ->detect(); 

$response->fullMatchingImages;

$response->partialMatchingImages;

$response->bestGuessLabels;;

$response->pagesWithMatchingImages;

$response->visuallySimilarImages;

$response->webEntities;
```

Easy and neat.

You may install the package via composer:

```bash
composer require ahmadmayahi/php-google-vision
```

You also need to create a service account through your Google Cloud account.

If you're not familiar with service accounts, then you migh need to visit [Google cloud documentation](https://cloud.google.com/iam/docs/creating-managing-service-accounts).

That's it.

For more information about the package, please [visit Github](https://github.com/ahmadmayahi/php-google-vision).
