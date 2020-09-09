# Python development style guide


## General
http://docs.python-guide.org/en/latest/


* all function parameters should be serializable (as json) -  use  simple standard objects like dict, float etc.
* prefer modules and functions over classes
    * reuse code on module level, not classes
    * see [here](https://www.youtube.com/watch?v=o9pEzgHorH0)
* flat is better than nested : prefer modules over classes, condense nested loops!

* use generator and iterator massivly, see https://www.youtube.com/watch?v=5-qadlG7tWo and https://www.youtube.com/watch?v=z4P6hSa6K9g
    * from itertools import groupby, chain
* YAGNI: "Always implement things when you actually need them, never when you just foresee that you need them."
* Python supports "metaprogramming" via a number of features, including decorators, context managers, descriptors, import hooks, metaclasses and AST transformations - understand and use it but have an eye on involved complexity


+ Read further:

https://github.com/rasbt/python_reference
