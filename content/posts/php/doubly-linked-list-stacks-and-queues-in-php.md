A data structure is a way of sorting and organizing data inside the memory, so it can be used efficiently.

PHP supports a bunch of data structures such as ad Doubly-Linked list, Stacks, Queues, etc...

In this post, I will shed light on the Doubly-Linked list data structure.

In the next upcoming post, I will discuss more data structures.

## Doubly Linked List

Doubly Linked List is a data structure that consists of sequentially linked records called nodes, each node (also called an element) knows about its neighbors (preceding and following elements).

![Doubly-Linked-List in PHP](/static/img/php/doubly-linked-list.png)

As you see here, the element 99 knows about both 12 and 37 elements.

Doubly Linked List uses some terms to deal with the list:

* `push`: pushes an element at the end of the list.
* `unshift`: prepends the list with an element.
* `shift`: shifts (remove) a node from the beginning of the list.
* `pop`: pops (remove) a node from the end of the list.

PHP supports the Doubly Linked List through the `SplDoublyLinkedList` class.

Let's put this into practice:

```php
$list = new SplDoublyLinkedList();

$list->push('C++');
$list->push('PHP');
$list->push('Python');
$list->push('Go');
$list->push('C');

$list->pop(); // Removes "C"
$list->shift(); // Removes "C++"

foreach ($list as $item) {
    echo $item.PHP_EOL;
}
```

```text
PHP
Python
Go
```

You may use the array notation instead of the push method:

```php
$list[] = 'Swift';
```

Use the `add` method to add/insert a new value at the specified index:

```php
$list->add(2, 'Java');
```

By default, `SplDoublyLinkedList` works on basis of FIFO (first in, first out), which means that every element you push, it becomes the first one when iterating over the list.

This behavior can be changed to LIFO (last in, first out) which is the opposite of FIFO.

```php
$list->setIteratorMode(SplDoublyLinkedList::IT_MODE_LIFO);
```

```text
Swift
C
Go
Java
Python
PHP
```

You may also use the `IT_MODE_FIFO` for the FIFO mode (which is the default one).

Sometimes you might need to remove the iterated elements, this can be achieved by setting the iterator mode to `IT_MODE_DELETE`:

```php
$list = new SplDoublyLinkedList();
$list->setIteratorMode(SplDoublyLinkedList::IT_MODE_DELETE);

$list->push('PHP');
$list->push('Python');
$list->push('Go');

foreach ($list as $item) {
    echo $item . PHP_EOL;
}

// rewind has no effect
$list->rewind();

// This foreach won't show anything
foreach ($list as $item) {
    echo $item . PHP_EOL;
}
```

Internally, the `rewind` method won't be invoked when using the `IT_MODE_DELETE`, that's it.

You may also want to use `top` / `bottom` methods to get the first and last elements in the list:

```php
$list = new SplDoublyLinkedList();
$list->push('C++');
$list->push('PHP');
$list->push('Python');

echo $list->top(); // Python
echo $list->bottom(); // C++
```

The `SplDoublyLinkedList` class extends the `ArrayAccess` iterator, which means that you can use the `ArrayAccess` methods such as `offsetExists`, `offsetGet`, `offsetUnset` on the Doubly-Linked list.

Now, we know what Doubly-Linked list works and how can we use it in PHP, but is there any real-world scenarios that use Doubly-Linked list?

## Stacks
A stack works on the principle of LIFO (last in, first out). The first item is at the bottom of the stack, the most recent is at the top:

```php
$list = new SplStack();
$list->push('Go');
$list->push('PHP');
$list->push('Python');

foreach ($list as $item) {
    echo $item.PHP_EOL;
}
```

```text
Python
PHP
Go
```

## Queues
A queue works on the principle of FIFO (first in, first out) just like the Doubly-Linked List.

> Both `SplStack` and `SplQueue` extend the `DoublyLinkedList` class.

Thq queue uses its own terminology, so, instead of `push` and `offsetUnset` we use the `enqueue` and `dequeue` methods:

```php
$list = new SplQueue();

$list->enqueue('C++');
$list->enqueue('PHP');
$list->enqueue('Python');

foreach ($list as $item) {
    echo $item."\n";
}
``` 


