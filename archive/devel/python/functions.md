# Python functions and parameters

Functions may be return value of other functions (nested) or item in a dictionary - in python, every variable is a reference.

## Lambda functions
My most frequent use case for lambdas is writing
short and concise key funcs for sorting iterables by an alternate key:
```python
>>> tuples = [(1, 'd'), (2, 'b'), (4, 'a'), (3, 'c')]
>>> sorted(tuples, key=lambda x: x[1])
[(4, 'a'), (2, 'b'), (3, 'c'), (1, 'd')]

>>> sorted(range(-5, 6), key=lambda x: abs(x))
[0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5]

	nested functions
>>> def make_adder(n):
... return lambda x: x + n
>>> plus_3 = make_adder(3)
>>> plus_5 = make_adder(5)
```



## Decorators
```python
def trace(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        print(f, args, kwargs)
        result = f(*args, **kwargs)
        print(result)
    return decorated_function

@trace
def greet(greeting, name):
    return '{}, {}!'.format(greeting, name)
```

Test    
```python
>>> greet('Hello', 'Bob')
<function greet at 0x1031c9158> ('Hello', 'Bob') {}
'Hello, Bob!'
```
## Variable argument lists and dicts

* The *args will give you all function parameters as a tuple respectively take a tuple as function paramters
* The **kwargs will give you all keyword arguments except for those corresponding to a formal parameter as a dictionary.
* Check [this](https://www.learnpython.org/en/Multiple_Function_Arguments)

Pass through parameters

```python
def test_args_kwargs(arg1, *args, **kwargs):
    test_args_kwargs_subfunction(*args, **kwargs)
Call function with predefined parameter array


Predefine arguments

```python
def product(a, b):
    return a * b
>>> argument_tuple = (1, 1)
>>> argument_dict = {'a': 1, 'b': 1}
>>> product(*argument_tuple)
>>> product(**argument_dict)
```

## Retrieving results

Placeholder variable

```python
a, *b, c = range(10)
print(a, b, c)
```

```
0 [1, 2, 3, 4, 5, 6, 7, 8] 9
```

## Comments for functions
Sphinx-style reST for doc strings: see [requests lib](https://github.com/requests/requests/blob/master/requests/api.py)
so code can easyly be adapted in readthedocs.io

```python
def get(url, qsargs=None, timeout=5.0):
    """Send an HTTP GET request.

    :param url: URL for the new request.
    :type url: str
    :param qsargs: Converted to query string arguments.
    :type qsargs: dict
    :param timeout: In seconds.
    :rtype: mymodule.Response

    Usage::
      >>> import requests
      >>> req = requests.request('GET', 'http://httpbin.org/get')
      <Response [200]>

    """
    return request('get', url, qsargs=qsargs, timeout=timeout)
```
