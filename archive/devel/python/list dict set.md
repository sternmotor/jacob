# Python complex data handling

## Dictionaries

Merge two directories

```
x = {'a': 1, 'b': 2}
y = {'b': 3, 'c': 4}
x.update(y)
```
```
{'c': 4, 'a': 1, 'b': 3}
```

Merge two directories (3.5+)
```
x = {'a': 1, 'b': 2}
y = {'b': 3, 'c': 4}
z = {**x, **y}
z
```
```
{'c': 4, 'a': 1, 'b': 3}
```

Get dictionary key by it's value:

```
Key = MyDict.keys()[MyDict.values().index(GivenValue)]
```

Sort dictionary by values
```
d = {'a':1, 'b':3, 'c':2}
sorted(d, key=d.get)
```

Combine tow dictionaries (no merge)
```
>>> from collections import ChainMap
>>> dict1 = {'one': 1, 'two': 2}
>>> dict2 = {'three': 3, 'four': 4}
>>> chain = ChainMap(dict1, dict2)
>>> chain['three']
3
>>> chain['one']
1
```

## Lists

Slizing: "[start:stop:step]" pattern
```
>>> lst = [1, 2, 3, 4, 5]
>>> lst
[1, 2, 3, 4, 5]
# lst[start:end:step]
>>> lst[1:3:1]
[2, 3]
```

Create a sublist that includes every other element of the original
```
lst[::2]
```

Get a copy of the original list, but in the reverse order:
```
>>> numbers[::-1]  # better: mylist.reverse()
[5, 4, 3, 2, 1]
```

Remove all elementes from list:

```
mylist.clear()
```


Validate list object

```
isinstance( Requests, (list, tuple))
```


Copy list - cut references
```
NewList = list(SomeList)
```

Copy list recursively

```
NestedList = [[1,3], [2,4]]
import copy
copy.deepcopy(NestedList)
```
```
[[1, 3], [2, 4]]
```


## Sets

Set operations
```
a = set(['a', 'b', 'c', 'd'])
b = {'c', 'd', 'e', 'f'}
c = {'a', 'c'}
>>> a.union(b)      # b may be set or list
{'b', 'e', 'f', 'c', 'a', 'd'}
>>> a.intersection(b)
{'c', 'd'}
>>> a.difference(b)
{'b', 'a'}
>>> a.symmetric_difference(b)
{'b', 'e', 'f', 'a'}
>>> a.issuperset(c)
True
>>> c.issuperset(a)
False
>>> c.issubset(a)
True
>>> c.issubset(b)
False
a.isdisjoint(["y", 'z']) #have no common elements
```



```
vowels = {'a', 'e', 'i', 'o', 'u'}
squares = {x * x for x in range(10)}
```

## Collections
Advanced datatypes: https://docs.python.org/3.5/library/collections.html

```
import collections
Person = collections.namedtuple('Person', 'name age gender')
bob = Person(name='Bob', age=30, gender='male')
print('{person.name} is a {person.age} old {person.gender}'.format(person=bob))
```



## Memory objects

Size of object in memory (e.g. big excel table)

```
sheet_size = sys.getsizeof(sheet) / 1024.0 / 1024
log.debug( "Loaded excel worksheet, size is %.3f MB" % sheet_size )
```
