# pyhon text file handling


## Excel, Ods, CSV files

Load excel 
```
import openpyxl # sudo pip3 install openpyxl

book = openpyxl.load_workbook(filename='some_file.xlsx')
sheet = book.active

header = [cell.value for cell in sheet[1]]
for row in sheet:
    values = {}
    for k, cell in zip(header, row):
        values[k] = cell.value
    print(values)
```

Openoffice calc table, skip first two rows
```
import pyexcel_ods

data = pyexcel_ods.get_data('some_file.ods')
header = data['hosts'][0]
for row in data['hosts'][2:]: # start reading third line
    values = {}
    for key, val in zip(header, row):
        values[key] = val
    print(values)
```
