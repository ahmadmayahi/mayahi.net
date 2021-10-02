A friend of mine shared a private repository with me and asked me to review his code.

While reviewing, I came across the following piece of code:
```php
class Import
{
    public function __construct(private IndexDocument $indexDocument)
    {
    }

    public function import()
    {
        $data = $this->indexDocument->prepareData(
            [
                'first_name' => 'Ahmad',
                'last_name' => 'Mayahi',
            ]
        );

        $this->indexDocument->index($data);

        // ...
    }
}
```

The `import` method needs to call the `prepareData` before calling the `index` method in order to prepare the given data for Elasticsearch.

If you don't prepare the data, your data may be invalid and not ready to be indexed.

This is considered a bad design because it introduces something called "**Temporal Coupling**".

Temporal coupling is a kind of coupling where code is dependent on time in some way. It is particularly insidious because it is hard to detect unless you know what you are looking for. ([source](https://www.pluralsight.com/tech-blog/forms-of-temporal-coupling/)).

In order to fix it, the `prepareData` has to be moved in the `index` method, so the `index` method prepares and index the data at the same time:
```php
class Import
{
    public function __construct(private IndexDocument $indexDocument)
    {
    }

    public function import()
    {
        $data = [
            'first_name' => 'Ahmad',
            'last_name' => 'Mayahi',
        ];
        
        // Prepares and indexes the given data
        $this->indexDocument->index($data);

        // ...
    }
}
```

Additionally, the `prepareData` should be a `private` method in the `IndexDocument` since it'll only be used within the `IndexDocument` class.

Whenever you see such a code in your project, consider refactoring it, otherwise you may end up saving/handling invalid data.
