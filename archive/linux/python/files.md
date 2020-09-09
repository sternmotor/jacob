# File handling

## Read and write files

Read complete file and close it - raises `FileNotFoundError`
```python
with open('Path/to/file', 'r') as import_file:
    content = import_file.read()
```

Write text to file and close it
```python
with open('Path/to/file', 'w') as export_file:
    file.write(Data)
```

Json - write sorted (without indent, file would be 40% smaller)
```python
with open(ExportPath, 'w') as JsonFile:
    json.dump(ExportData, JsonFile, indent=4, sort_keys=True, ensure_ascii=False)
```

Json - read from file
```python
with open(ImportPath, 'r') as JsonFile:
    ImportData = json.load(JsonFile)
```

## Compression and Encryption

Gzip exisiting file
```python
import gzip
import shutil
import os

with open(EXPORT_PATH, 'rb') as f_in, gzip.open('%s.gz' % EXPORT_PATH, 'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)

os.remove(EXPORT_PATH)
```

## Piping

Read 256 bytes at once, handle input

```python
import sys

while True:
    data = sys.stdin.read(256)

    # process input
    if data != '':
        data = '#'  + data
        # end of data processing command group
        sys.stdout.write(data)
    # stop, no more input
    else:
        sys.stdout.flush()
        break
```
