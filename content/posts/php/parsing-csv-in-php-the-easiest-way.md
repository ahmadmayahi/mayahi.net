I discourage using composer libraries for very simple problems that can be solved with pure PHP.

For example, a few days ago I came across these lines of code:

```php
$csv = Reader::createFromPath(storage_path('dummy.csv'), 'r');
$csv->setHeaderOffset(0);

$records = $csv->getRecords();

foreach ($records as $record) {
    echo $record['first_name'];
}
```

As you may see here, this code extracts the `first_name` from the given CSV file.

To make this code work, you do need the `league/csv` composer package.

The `league/csv` is one of the best CSV packages for PHP, it provides some convenient methods to work with CSV, but it’s not solving a big problem here, actually, it adds more complexity into our project.

If somebody got a simple problem, something like iterating over a CSV file, why don’t she use the PHP’s built-in CSV functions?

Let’s see how can we convert the previous code to pure PHP code:

```php
$csv = new SplFileObject(storage_path('dummy.csv'));
$csv->setFlags(SplFileObject::READ_CSV);
foreach ($csv as $item) {
    echo $item['first_name'];
}
```

It’s simpler, cleaner and without any extra packages.

You may use the `setCsvControl` method to specify more things such as the delimiter.