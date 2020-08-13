Strings are one of the most important data types in any programming language, no application can be done without dealing with strings.

Python provides a bunch of string methods for different usages, in this post I’m going to describe the most important string methods in Python, but before I do this, let’s see the basic of strings in Python.

## Strings in Python
Python 3 stores strings as a sequence of Unicode code point, this means that we can represent any Unicode characters, like Arabic, Hebrew, Danish and even emojis.

Strings are immutable, so once you create a string you can’t change it at a later point.

String in Python could be created either by enclosing it with a double/single quotes or by using the `str`object, both ways produce a `str`object, because everything in Python is an object:

```python
# Double quotes
hello = "Hello World I'm using Python!"

# Single quotes
hello = 'Hello World I\'m using Python!'

# str object
hello = str("Hello World I'm using Python!")

print(type(hello)) # This should always return "<class 'str'>"
``` 

Sometimes we need to create a raw string, a string that should be treated as it is, without handling the escaping characters like (`\n`, `\r`, `\t` etc...) for this purpose we can use the r operator as follows:

```python
print(r"Hello World\nI'm using Python!\t\t\t Amazing")
```

The triple quotes `"""` can be used for multi line string:

```python
python = """
Python is an interpreted, high-level, general-purpose programming language. Created by Guido van Rossum and first released in 1991, Python has a design philosophy that emphasizes code readability, notably using significant whitespace. It provides constructs that enable clear programming on both small and large scales.[26] Van Rossum led the language community until stepping down as leader in July 2018
"""

print(python)
```

> Please note that the triple quotes are also used in multi-line code comments in Python.

What if we need to concatenate a string? this can be achieved the plus (+) sign:

```python
hello = "Hello" + " " + "World"
```

As I mentioned earlier, Python treats the string as a set of sequences, which means each character gets its own index, as if it were a `list()` or `dict()` let’s demystify this by an example:

```python
hello = "Hello World! I'm using Python!"
h = hello[0]
print(h) # Output: H

for char in hello:
    print(char, " ") #Output: H\ne\nl etc...
```

We can cut off a string by using the slice operator:

```python
hello = "Hello World"
print( hello[:5] ) # Output: Hello
print( hello[6:] ) # Output: World
print( hello[-1:-5] ) # Output: World
```

Use the multiplication operator to print the string twice:

```python
print("Hi" * 2) # Output: HiHi
```

Since Python3 deals with Unicode code points, this means we can print out emojis as simple as strings:

```python
# All these statements produce the same output

print("I love Python ♥️")
print("I love Python \U0001F600") # Emoji using the Unicode code number
print("I love Python \N{grinning face}") #Emojis using the CLDR
```

> - Visit the full [emoji list page](https://unicode.org/emoji/charts/full-emoji-list.html) from the Unicode website to know all about emoji codes.
> - When it comes to emojis representation, I encourage you to either use the **CLDR** or the Unicode charachter, and don’t use the direct emojis like 😀 in your code.
> - You might also be interested in [emoji module](https://pypi.org/project/emoji/).

We’ve done with emojis, so now I’d like to show you something else, which is printing none-Latin characterless, like Arabic. Since Python3 uses Unicode by default, we might print out any Unicode strings such as Arabic:

```python
print("أنا سَعيدٌ جِدّاً بلقاءك!") # Arabic
print("Jeg er så glad for at møde dig!") # Danish
print("Jeg er s\u00e5 glad for at m\xf8ode dig!") # Danish with Unicode chars.
```

> From my experience, writing none-Latin strings directly into your code is a bad practice, instead use something like [GNU gettext](https://www.gnu.org/software/gettext/) for this purpose, see [Python Multilingual internationalization](https://docs.python.org/3/library/gettext.html#) Services.

## How about bytes?
`bytes` type is similar to str except it’s stored as a sequence of bytes, instead of a sequence of [Unicode code points](https://en.wikipedia.org/wiki/Code_point) (`str` case), `bytes` is used in binary data, and a fixed single-byte character encoding.

`bytes` can be either represented by the b operator or by the `bytes()` object:

```python
hello = bytes(source="Hello World", encoding="utf8")
print(hello) #Output: b'Hello World'
```

Different data types could be set to the source parameter:

- **String**: the given string will be converted to bytes (as we’ve seen earlier).
- **Integer**: creates an array of zero values within the provided size.
- **Object**.
- **Iterable**: creates a numeric array of the given size, each element must be between 0 and 255.

Let’s see how these types work with `bytes`:

```python
n = bytes(5)
print(n) # Output: b'\x00\x00\x00\x00\x00'
print(list(n)) # Output: [0, 0, 0, 0, 0]

items = [1, 2, 4, 8, 16, 32]
arr = bytes(items)
print(arr) # Output: b'\x01\x02\x04\x08\x10 '
print(list(arr)) # Output: [1, 2, 4, 8, 16, 32]
```

We can encode/decode a string/bytes by using the encode/decode methods as follows:

```python
my_string = ("Jeg er så glad for at møde dig!")
my_string_encode = my_string.encode()
my_string_decode = my_string_encode.decode('utf8')

print(my_string_encode) # Output: b'Jeg er s\xc3\xa5 glad for at m\xc3\xb8de dig!'
print(my_string_decode) # Output: Jeg er så glad for at møde dig!
```

## String operators
Python provides a set of string operators, so far we’ve dealt with the concatenation operator (`+`), string repetition operator (`*`), slice (`[]`), and range slice (`[from:to]`) operators, let’s checkout the full list:

|Operator|Description|
|---|---|
|`+`|String concatenation|
|`*`|String repetition|
|`[n]`|Slice a string by getting a specific char.|
|`[from:to]`|Range slice, gets a portion of a string|
|`in`|Returns true if the char. exists in the string|
|`not in`|Returns true if the char. doesn’t exist in the string|
|`%`|String formatting|

```python
string = "Hello World I love Python"
print("Python" in string) # True

string = "Hello World I love Python"
print("Python" not in string) # False
```

String formatting operator is one of the coolest string operators in Python, it adds the ability to add placeholders in a string, let’s demystify this by an example:

```python
string = "My name is %s and I love to use %s"
print(string % ("Ahmad", "Python")) # Output: My name is Ahmad and I love to use Python
```

As we see here, the `%s` replaced by Ahmad and Python respectively, but what does `%s` mean here? 

The `%s` represents a string placeholder. Python provides many placeholders such as `%c` for character, `%d` for decimal integer, `%f` for floating points and etc...

> Python has a more readable method `format()` it’s highly recommend to use the format method instead of the regular string formatting, we’re going to discuss it later in string methods section.

## String methods
Python provides a bunch of string methods, some of these methods require explanation but some of them are too easy to understand.

* Capitalize first letter of string:
```python
print( "hello".capitalize() ) # Output: Hello
```
* All words become uppercase (title-case):
```python
print( "hello world".title() ) # Output: Hello World
```
* Converts string to upper/lower case or swapcase:
```python
print( "hello world".upper() ) # Output: HELLO WORLD
print( "HELLO WORLD".lower() ) # Output: hello world
print( "Hello WORLD".swapcase() ) # Output: hELLO world
```
* Get the length of the string:
```python
print (len("Hello World")) # Output: 11
```

> `len` function doesn’t belong to the string object, it can also be used in other types such as lists, dictionaries and tuples.

* Add right and left padding to the string: this function adds char. padding to the right and left side the string:
```python
# Output: ----Hello World-----
print ( "Hello World".center(20, "-") )
```

In this example, dash symbol (-) has been repeated ten times, five on right and five on left.

* Count the occurrences of sub-string
This method returns the number of occurrences of sub-string:
```python
string = """
Python is an interpreted, high-level, general-purpose programming language. Created by Guido van Rossum and first released in 1991, Python has a design philosophy that emphasizes code readability, notably using significant whitespace. It provides constructs that enable clear programming on both small and large scales.[26] Van Rossum led the language community until stepping down as leader in July 2018
"""

print( string.count("i") ) # Output: 23

#Starting from 10->20 char
print( string.count("i", 10, 20)) #Output: 1
```

* Determines if string starts/ends with a substring:
As their names implies, they used to determine if the string starts/ends with a substring:

```python
string = "Python is one of the most popular programming languages"
print( string.startswith("Python") ) # Output: True
print( string.endswith("languages") ) # Output: True

#Start from 0 position to 6th position.
print( string.startswith("Python", 0, 6) ) # Output: True
```


## is methods
All the methods which start with is are boolean methods, and they are used to determine if the given string has a special meaning:

|Method|Description|
|---|---|	
|`isalnum()`|Checks if the string is an alpha-numeric string.
|`isalpha()`|Check if the string is an alphabetic string.
|`isascii()`|Checks if all characters in the string are ASCII.
|`isdecimal()`|Checks if the string is a decimal string.
|`isdigit()`|Checks if the string is a decimal string.
|`isidentifier()`|Checks if the string is a valid Python identifier.
|`islower()`|Checks if the string is a valid Python identifier.
|`isnumeric()`|Checks if the string is a valid Python identifier.
|`isprintable()`|Checks if if the string is printable.
|`isspace()`|Checks if the string is printable.
|`istitle()`|Checks if the string is a title-cased string.
|`isupper()`|Checks if the string is an uppercase string.

I know, some of these methods seem obvious, but some of them requires more explanation, so let’s dentistry one by one:

```python
#isalnum
print( "Copenhagen 2000".isalnum() ) # Output: False because of the space
print( "2000i".isalnum() ) # True

#isalpha()
print( "Iraq".isalpha() ) # Output: True
print( "ar_IQ".isalpha() ) # Output: False because of the underscore charachter

#isascii
print( "Hello World \xb6".isascii() ) # Output: false because \xb6 is a hex. character not an ascii
print( "Hello World".isascii() ) # Output: True

#islower
print( "hello world".islower() ) # Output: True

#isupper
print( "HELLO WORLD".isupper() ) # Output: True

#isspace
print( " ".isspace() ) # Output: True
print( "".isspace() ) # Output: False
print( "\t \n".isspace() ) # Output: True

#istitle
print( "hello world".istitle() ) # Output: False
print( "Hello World".istitle() ) # Output: True
```
Those methods were the easiest methods because they are self-explained, but methods like `isdigi`, `isnumeric`, `isdecimal` need more clarification.

As their names implies, all these methods deals with numbers, but what is the difference between them? in short answers the difference lies in Unicode classification, let’s see how this is done.

`isdecimal` checks if the given string is a decimal number, numbers from 0-9 are valid, otherwise they aren’t:

```python
print( "123".isdecimal() ) # Output: True
print( "-123".isdecimal() ) # Output: False
print( "¼".isdecimal() ) # Output: False
print( "١٢٣".isdecimal() ) # Output: False ١٢٣ is the 123 in Hindu numeric system
```

`isnumeric` checks if the given string is a number in any kind (Unicode) numeric system:
```python
#isnumeric
print( "123".isnumeric() ) # Output: True (Arabic numerals)
print( "١٢٣".isnumeric() ) # Output: True (Hindu numerals)
print( "۴۵۶".isnumeric() ) # Output: True (Farsi numerals)
print( "¼½".isnumeric() ) # Output: True
print( "四五六".isnumeric() ) # Output: True (Chinese numerals)
```

> If you are building a multilingual application where it deals with different numeric system, you must consider using the isnumeric system.

> [More about numeric value in Unicode.](https://www.unicode.org/versions/Unicode12.0.0/ch04.pdf#G124206)

`isdigit` checks if the number is decimal and it can also be in a typographic context:

```python
print( "①".isdigit() ) # Output: True
print( "⒈".isdigit() ) # Output: True
print( "¹".isdigit() ) # Output: True
```

> [More about numerals in Unicode.](https://en.wikipedia.org/wiki/Numerals_in_Unicode)

Now, it’s time to checkout the `isidentifier` method and see what does this method do for us.

Imagine you want to give a particular name to a variable and you aren’t sure if this name is valid or not in Python, so `isidentifier` checks if the given name is a value Python identifier.

```python
print( "hello".isidentifier() ) # Output: True
print( "123hello".isidentifier() ) # Output: False
print( "\t".isidentifier() ) # Output: False
print( "hello123".isidentifier() ) # Output: True
```

The last method in our list is `isprintable`, this method checks if the given string can be printed or not, in other words if the string contains any of the following classes:

* Letters from A-Z (Uppercase)
* Letters from a-z (Lowercase)
* Digits from 0-9
* [Punctuation characters](https://en.wikipedia.org/wiki/Punctuation) ( !”#$%&'()*+, -./:;?@[]^_`{ | }~ )
* Space.

```python
print( "Hello World".isprintable() ) # Output: True
print( "أنا أتحدّث العربيّة".isprintable() ) # Output: True
print( "123".isprintable() ) #Output: True
print("Hello\nWorld".isprintable() ) # Output: False
print("Hello\r\tWorld".isprintable() ) # Output: False
```

### Join a sequence of elements by a separator
Joins all the items in list, tuple, or dictionary using a separator:

```python
# All these statements produce A,B,C string
print( ",".join(["A", "B", "C"]) ) # Using lists
print( ",".join(("A", "B", "C")) ) # Using tuples
print( ",".join({"A", "B", "C"}) ) # Using dictionaries
```

### Create a list from a given string using a separator
If you have a string and you want to cut it off by a given separator and store it in a list, then consider using `split`:

```python
# Output: ['Baghdad', ' Basra', ' Anbar', ' Erbil']
print( "Baghdad, Basra, Anbar, Erbil".split(",") ) 
```

By default, `split` is cutting off the whole string, if you’d like to cut a bunch of items, then you might set the second argument to the number of elements you want:

```python
# ['Baghdad', ' Basra', ' Anbar, Erbil']
print( "Baghdad, Basra, Anbar, Erbil".split(",", 2) )
```

> Use `rsplit()` method if you want to start the splitting from the right hand side.

`splitlines` converts all the new lines into a list:

```python
# Output: ['Hello World', 'I love Python!']
print("Hello World\nI love Python!".splitlines())
```

### Formatting