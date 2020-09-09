# Programming structures

## Conditional structures

## Switch
```
a = {
    True: 1,
    False: -1,
    None: 0
}
print(a.get(False, default=0))
```
## Conditional assignment

Assign variables conditionally
```
path = sys.argv[1] if len(sys.argv) > 1 else '.'
```

Assign functions conditionally
```
print((function1 if b else function2)(arg1, arg21))
```

## Iteration

Objects that support the __iter__ and __next__ "dunder" methods automatically work with for-in loops.
