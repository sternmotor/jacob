# Python Time, date units handling

Links
* [Good introduction](http://effbot.org/librarybook/datetime.htm)

Timestamp for files

```python
import time
time.strftime("%d.%m.%Y")
time.strftime("%Y%m%d_%H%M%S")
time.strftime("%y-%m-%d_%H:%M:%S_cw%W")
```

Convert time strings

```python
import time
a = 'Sun Jan  4 14:12:45 2009'
datetime.datetime(*time.strptime( a )[0:6])
```

* Output
```
2009-01-04 14:12:00
```

Now() in seconds

```python
from datetime import datetime as dt
now_seconds = int(dt.now().strftime('%s'))
```


Time object to seconds

```python
time_iso.strftime( DateTimeObject )
```

* Output
```
1231074720
```

Date string to seconds

```python
datetime.datetime.strptime(date, '%Y-%m-%d').strftime( "%s" )
```


Seconds to time object

```python
import datetime
print datetime.datetime.fromtimestamp(1231074720)
```

* Output
    ```
    2009-01-04 14:12:00
    ```

* Human readable numbers: see devel/python/data
