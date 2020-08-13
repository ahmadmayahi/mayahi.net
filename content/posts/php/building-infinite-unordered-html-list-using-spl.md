Iterating over a nested menu isn't that easy, especially when we got a big menu with many nested levels.

The problem that I want to solve here is to build an unordered HTML list that is based on a multi-level nested menu for our products:

```php
$products = [
  'Camera & Photo' => [
    'Video Projectors' => [],
    'Digital Cameras' => [
        'Digital SLRs' => [
            'Canon' => [
                'Canon EOS 4000D', 'Canon EOS 2000D DSLR'
            ],
            'Nikon' => [
                'Nikon D7500',
                'Nikon D5600'
            ],
            'Fujifilm' => [
                'Fujifilm X-A5 Mirrorless'
            ]
        ],
        'Mirrorless Cameras' => [
            'Sony' => [
                'Sony α6400 E-mount compact'
            ],
            'Panasonic' => [
                'Panasonic LUMIX DC-GH5LEB-K'
            ]
        ],
        'Lenses' => [
            'Camera Lenses' => [],
            'Camcorder Lenses' => [],
        ]
    ],
      'Mobile Phones' => [
          'Smart Phones' => [
              'Apple' => [
                  'iPhone 11',
                  'iPhone 11 Pro',
                  'iPhone Xs Max'
              ],
              'Samsung' => [],
              'Huawei' => [],
              'Google' => [],
          ]
      ]
  ]
];
```

I will be using the SPL library to solve this problem.
 
SPL provides a bunch of iterators, In this post I will be using  `RecursiveArrayIterator` as well as `RecursiveIteratorIterator`.

As its name implies, the `RecursiveArrayIterator` iterates over a given array, but it doesn't support nested arrays, therefore we also need to use the `RecursiveIteratorIterator`.  

Let's get started:

```php
$products = new RecursiveArrayIterator($products);
```

The `RecursiveIteratorIterator` class has four methods that will react when a particular event occurs, these methods are:
`beginIteration`, `endIteration`, `beginChildren` and `endChildren`.

Let's create a class tha uses these four methods:

```php
class NestedList extends RecursiveIteratorIterator
{
    public function beginIteration()
    {
        echo "<ul>".PHP_EOL;
    }

    public function endIteration()
    {
        echo "</ul>".PHP_EOL;
    }

    public function beginChildren()
    {
        echo "<ul>".PHP_EOL;
    }

    public function endChildren()
    {
        echo "</ul></li>".PHP_EOL;
    }
}
```

Let's use the class:

```php
$products = new NestedList($products, RecursiveIteratorIterator::SELF_FIRST);

foreach ($products as $category => $item) {
    if ($products->hasChildren()) {
        echo "<li>$category";
    } else {
        echo "<li>$item</li>\n";
    }
}
```

> The `RecursiveIteratorIterator::SELF_FIRST` flag is used to show the parent and its children, if you try to remove this flag, then it’ll fall back to the `LEAVES_ONLY` (default) which means that only the children will be shown.

Here is final result:

![Unordered list](/static/img/php/building-infinite-unordered-html-list-using-spl-img.png)
