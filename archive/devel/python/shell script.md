# Shell interaction in python
Make scripts behave like a unix shell application.

## Command lie arguments

### Argparse
Sort command line arguments alphabetically

```
parser = argparse.ArgumentParser()

# parser.add_argument( ...

for ActionGroup in parser._action_groups[1:]:  # sort options
    ActionGroup._group_actions.sort(key=lambda x:x.option_strings[0])
```

### DocOpt
Pull arguments and options from module doc string
* Use [Docopt](https://github.com/docopt/docopt)

## Piping

* See `fileinput` lib



## Script verbosity

Short: set loglevel according to -v cli option count

```
parser.add_argument(
    '--verbose', '-v', action='count', default=0,
    help='script verbosity, -v: show progress, -vv: debug mode'
)
```
...
```
# script verbosity according to number of argparse "-v", 30 is logging.WARN ...
if args.verbose > 2:
    raise KnownError('Verbosity up to -vv supported, only')
logging.basicConfig(
    level={0:30, 1:20, 2:10, 3:10, 4:10}[args.verbose],
    format={
        0: 'Error: %(message)s',
        1: '* %(message)s',
        2: '%(name)s L%(lineno)3s, %(levelname)-8s: %(message)s',
    }[args.verbose]
)
```

## Keyboard Input

Read single character from standard input

```
def getchar():
   # poll a single character from standard input
   import tty, termios, sys
   fd = sys.stdin.fileno()
   old_settings = termios.tcgetattr(fd)
   try:
      tty.setraw(sys.stdin.fileno())
      ch = sys.stdin.read(1)
   finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
   return ch

while 1:
    ch = getchar()
    if ch.strip() == '':
        print('bye!')
        break
    else:
        print 'You pressed', ch
```



## GNU readline support
Draw fancy menues

* see [Python prompt toolkit](https://github.com/jonathanslenders/python-prompt-toolkit)
