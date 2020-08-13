The Standard PHP Library (SPL) is a collection of interfaces and classes that are meant to solve common problems.

SPL had been introduced in 2005 with PHP 5.0.0.

SPL doesn’t require any additional libraries; it comes by default when you install PHP.

In this post, I’ll be showing you some iterators that are used to deal with the filesystem.

## File Handling
SPL library provides three classes for file handling:

- `SplFileInfo`: file information, such as size, pathname, real path, etc.
- `SplFileObject`: an object-oriented interface for a file.
- `SplTempFileObject`: an object-oriented interface for a temporary file.

Let’s dive into these three classes.

As I mentioned, `SplFileObject` provides an object-oriented interface for a file, so, instead of using `fopen()`, `fgets()`, `eof()` functions you’d use the `SplFileObject`:

```php
// Writing to a file
$file = new SplFileObject('myfile', 'w+');
$file->fwrite('Hello World');
```

Let me show you another example.

Create a new text file with the following contents:

```text
Hello World
I love PHP
PHP is amazing
SPL is great


PHP is the most used server-side programming language.
```

Save it as `php.txt`.

The `SplFileObject` class extends the `SplFileInfo` as well as the `Iterator` interface:

Get the file size:

```php
echo $file->getSize();
```

Read the file line by line:

```php
$file = new SplFileObject('php.txt');
foreach ($file as $line) {
    echo $line;
}
```

You may want to know a few information about the given file, so use `SplFileInfo` for this purpose:

```php
$info = new SplFileInfo('php.txt');
if ($info->isFile()) {
    echo $info->getRealPath();
}
```

The `SplFileInfo` offers an interface that provides many useful methods such as `getMime()`, `getPath()`, `getSize()` etc...

> Refer to the PHP’s documentation for the full list of `SplFileInfo` methods.

You may want to use the `SplTempFileObject` to create a memory-based temporary file:

```php
$temp = new SplTempFileObject();
$temp->fwrite('Hello World');

var_dump($temp->getPathName()); // php://temp
```

As you see here, the temporary file is stored in the memory and not in the file disk, but that’s not always the case, as I will discuss it later.

You may wondering why the file is saved into memory and not in the file system?

The memory is much faster than the file system.

Imagine that you’re parsing a CSV file and sending it back to the end user so she can download it:

```php
$file = new SplTempFileObject();
// csv processing here
$file->rewind();
header('Content-Type: text/csv');
header('Content-Disposition: attachmenet; filename=mycsvfile.csv');
$file->fpassthru();
```

> [Read more about parsing the csv files in PHP](/php/parsing-csv-in-php-the-easiest-way/).

Please notice that if the file size exceeds the `max_memory` value (which is 2 MB by default), then it will be saved as a disk file in the system’s temp directory unless you specify the maximum memory size in the `__costructor` as follows:

```php
$temp = new SplTempFileObject(10); // 10 bytes is the max memory size
$temp->fwrite("This is the first line\n");
$temp->fwrite("And this is the second.\n");
```

> Even if the file will be saved on disk, there’s no way to get its full system path, it’ll always refer to the `php://temp` as a file path, it’s wired, isn’t it?

You may use the `tmpfile()` function to create a disk-based temp file and then retrieve its path by using the `stream_get_meta_data`:

```php
$file = tmpfile();
$path = stream_get_meta_data($file)['uri']; // eg: /tmp/phpFx0513a
```

## DirectoryIterator

As its name implies, `DirectoryIterator` traverses the given directory:

```php
$files = new DirectoryIterator('/Users/ahmad');
echo '<ul>';
foreach ($files as $file) {
    echo '<li>'.$file.'</br>';
}
echo '</ul>';
```

By default, `DirectoryIterator` includes the `.` and `..` when listing the files, you may use the `isDot()` method to skip the dots while traversing:

```php
/** @var DirectoryIterator $item */
foreach ($dir as $key => $item) {
    if ($item->isDot()) { continue; }
    echo '<li>'.$item.'</br>';
}
```

You can view the available methods for the `DirectoryIterator` by either calling the `get_class_methods()` or inspecting the PHP’s documentation:

```php
print_r(get_class_methods(DirectoryIterator::class));
```

Sometimes, you need to filter the files by storing them into a new array:

```php
$files = [];
foreach ($dir as $key => $item) {
    $files[] = $item;
}
echo $files[0]->getFilename();
```

Due to the nature of the iterators, the last line won’t return anything, to fix it, you do need to clone the `$item`:

```php
$files = [];
foreach ($dir as $key => $item) {
    $files[] = clone $item;
}
echo $files[0]->getFilename();
```

## FilesystemIterator

The `FilesystemIterator` is an enhanced version of the `DirectoryIterator`.

In fact, `FilesystemIterator` extends the `DirectoryIterator` and adds a few more features:

- `flags`: configurable options.
- Returns `SplFileInfo` as a file object instead of the `DirectoryIterator`.
- Uses the file path as a key/value pair.

Let’s see a few examples:

```php
// Skipping the dots by using the SKIO_DOTS flag
$files = new FilesystemIterator('/Users/ahmad', FilesystemIterator::SKIP_DOTS);
foreach ($files as $key => $item) {
    var_dump($key); // $key is used a full path name
}
```

You may want to use the filename instead of the full path as the key:

```php
// Use | to add more flags
$files = new FilesystemIterator($dirName, FilesystemIterator::SKIP_DOTS | FilesystemIterator::KEY_AS_FILENAME);
```

If you dump the `$item` you can see that it’s of type `SplFileInfo` and not `DirectoryIterator`:

```php
foreach ($files as $item) {
    var_dump($item); // SplFileInfo
}
```

```php
// Listing the full SplFileInfo methods
print_r(get_class_methods(SplFileInfo::class));
```

Unlike `DirectoryIterator` you don’t need to clone the `$item` while storing it into an array:

```php
$files = [];
foreach ($dir as $key => $file) {
    $files[] = $file;
}
var_dump($files[0]->getSize());
```

> I highly encourage you to use the FilesystemIterator instead of DirectoryIterator.

## RecursiveDirectoryIterator

You may use the `RecursiveDirectoryIterator` to get all the files/directories recursively.

The `RecursiveDirectoryIterator` extends the `FilesystemIterator `as well as implementing the `RecursiveIterator` interface:

```php
$files = new RecursiveDirectoryIterator('/Users/ahmad');
foreach ($files as $item) {
    echo $item.'<br>';
}
```

As you can see here, nothing happens but returning the exact same result as if we were using the `FilesystemIterator`.

To make it return all the files/directories recursively, you have to give the `RecursiveDirectoryIterator` as a parameter to the `RecursiveIteratorIterator` it’s kinda weird, but it makes sense, because `RecursiveIteratorIterator` traverses all the children recursively, so, let’s see how it works:

```php
$files = new RecursiveDirectoryIterator('/Users/ahmad');
$files = new RecursiveIteratorIterator($files);
foreach ($files as $file) {
    echo $file.PHP_EOL;
}
```

You may use the `setMaxDepth()` method to specify the traversing depth, the default value is zero which means traversing all the files/directories.

## LimitIterator

The `LimitIterator` allows iteration over a limited subset of items in an Iterator:

```php
$files = new RecursiveDirectoryIterator('/Users/ahmad');
$files = new RecursiveIteratorIterator($files);

// Get the first 10 results
$files = new LimitIterator($files, 0, 10);
foreach ($files as $file) {
    echo $file.PHP_EOL;
}
```

## GlobIterator

As its name implies, the `GlobIterator` uses the glob patterns.

Please notice that the `GlobIterator` extends the `FilesystemIterator` which means that it returns an iterator of `SplFileInfo` when returning its results.

Let’s see how can we get all the pdf files that reside in a particular directory:

```php
$files = new GlobIterator('/Users/ahmad/Library/*.pdf');
/** @var SplFileInfo $file */
foreach ($files as $file) {
    echo $file->getFilename();
}
```

> `GlobalIterator` only accepts an absolute path

## RegexIterator

As its name implies, `RegexIterator` is used to apply regular expressions on the file system:

```php
// Get all "pdf" and "epub" files
$files = new FilesystemIterator('/Users/ahmad/Library');
$files = new RegexIterator($files, '/\.(?:pdf|epub)$/i');
foreach ($files as $file) {
    echo $file.PHP_EOL;
}
```

You may want to apply the `RegexIterator` to search for the given pattern recursively:

```php
$files = new RecursiveDirectoryIterator('/Users/ahmad/Library');
$files = new RecursiveIteratorIterator($files);
$files = new RegexIterator($files, '/\.(?:pdf|epub)$/i');

foreach ($files as $item) {
    echo $item.PHP_EOL;
}
```

## Conclusion
SPL is a rich library, it provides solutions for some common problems.

I highly encourage you to use SPL instead of some composer libraries unless the composer library provides something difficult to implement such as [SymfonyFinder](https://symfony.com/doc/current/components/finder.html).