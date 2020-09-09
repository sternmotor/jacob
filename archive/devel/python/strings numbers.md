# Python scalar data handling


## Comparison

"is" vs. "=="

* An `is` expression evaluates to True if two variables point to the
same (identical) object.
* An `==` expression evaluates to True if the objects referred to by
the variables are equal (have the same contents).


Chained comparison

```
a = 10
print(1 < a < 50)
print(10 == a < 20)
```

Comparing to fixed values - use `is`

```
if item is None
if item is True
if item is False
```

Swap data
```
a, b = b, a
```


## Numbers

Ranges
```
for i in range(5):
```


Convert bytes human readablye (1024 multipler)
```
def human_readable_bytes(num):

    for factor in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return '{0:3.1f} {1}B'.format(num, factor)
        num /= 1024.0
    return '{0:.1f} YiB'.format(num)
```

Convert bytes human readable (1000 multipler)
```
def human_readable_decimal(num, precision=1, unit=''):

    for factor in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1000.0:
            return '{0:3.{preci}f} {1}{2}'.format(num, factor, unit, preci=precision)
        num /= 1000.0
    return '{0:.1f} Y{1}'.format(num, unit)
```

Display numbers, use a variable for digit length
```
>>> '{0:3.{preci}f}'.format(123.45678, preci=3)
'123.457'
```



## Strings

Strip and justify ( = strip/ pad whitespace)

```
strip, lstrip, rstrip, center(width), ljust(with), rjust(with)
```

Split string maximum times
```
some_string.split(':', 2)
```

Multiline strings
* Python's compiler will automatically join multiple quoted strings together into a single string:

    ```
    print(
        'bla bla{0}'
        "blub"
        "bli".format('INSERTED EXPRESSION')
    )
    ```

### Format strings
See [format specs](https://docs.python.org/2/library/string.html#formatspec)

Variables in format strings
```
d = {'name': 'Jeff', 'age': 24, 'float':23.456, 'preci':2}
print("My name is {name} and I'm {age} years old. Float is {float:.{preci}f}".format(**d))
```
```
octets = [192, 168, 0, 1]
'{:02X}{:02X}{:02X}{:02X}'.format(*octets)
```

Classes/Collections in format strings
```
import collections
Person = collections.namedtuple('Person', 'name age gender')
bob = Person(name='Bob', age=30, gender='male')
print('{person.name} is a {person.age} old {person.gender}'.format(person=bob))
```

Old `%s` syntax
* Use only in  case there is no formatting to the output and the order of `%s` and matching `()` contents is fix


### String Encryption, Compression, Hashes

Generate a password with length "passlen" with no duplicate characters in the password

```
import bcrypt   
chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ-_+()!?"
passlen = 10
for i in range(0,75):
    password =  "".join(random.sample(chars,passlen))
    # gensalt's log_rounds parameter determines the complexity.
    # The work factor is 2**log_rounds, and the default is 12
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(10))
    print('{} {}'.format(password, hashed))
```

Compress string

```
import bz2
CompressedText = bz2.compress("sometext".encode())
print(bz2.decompress(CompressedText).decode())
```
