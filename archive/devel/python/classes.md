# Methods and classes

## Class and instance variables

Class variables are for data shared by all instances of a class

Access class variables through `self.__class__`:
```
class CountedObject:
	num_instances = 0
	def __init__(self):
		self.__class__.num_instances += 1  # !not: self.num_instances += 1
```

## Namespaces

Have a dictionary accessible like a class (dot notation) - use a class

```
class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
args = Namespace(a=1, b='c')
args.a
```

or better a collection
```
import collections
Person = collections.namedtuple('Person', 'name age gender')
bob = Person(name='Bob', age=30, gender='male')
print('{person.name} is a {person.age} old {person.gender}'.format(person=bob))
```
