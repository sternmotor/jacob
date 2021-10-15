Pyhon text, csv and excel file handling
=======================================

Yaml
----

Use fast C Yaml - load yaml from file 

    import yaml
    with open(file_name, 'r') as yamlfile:
        data = yaml.load(yamlfile, Loader=yaml.CLoader)


Dump to string variable

    import yaml
    print(yaml.dump(data, default_flow_style=False, Dumper=yaml.CDumper))


Dump to to file

    import yaml
    with open(file_name, 'wb') as stream:
        yaml.dump(
            data, stream, encoding='utf-8', 
            default_flow_style=False, Dumper=yaml.CDumper
        )


CSV
---

Read CSV from disk

    with open (path, 'r', newline ='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter = ';')
        for row in reader:
            values = {}
            for k,v in row.items():
                values[k] = data.check_value(v)

            yield values

Store CSV on disk

    with open('outfile', 'w') as csvfile
        csvwriter = csv.DictWriter(csvfile, csv_headers, restval='-', dialect='unix', )
        csvwriter.writeheader()
        for data_set in csv_data:
            csvwriter.writerow(data_set)


Store CSV in variable - virtual writer

    class CsvTextBuilder(object):
        def __init__(self):
            self.csv_string = []

        def write(self, row):
            self.csv_string.append(row)

    csvfile = CsvTextBuilder()
    csvwriter = csv.DictWriter(csvfile, csv_headers, restval='-', dialect='unix', )
    csvwriter.writeheader()
    for data_set in csv_data:
        csvwriter.writerow(data_set)
    print(''.join(csvfile.csv_string))


Excel and ODS files
-------------------

Load excel 

    import openpyxl # sudo pip3 install openpyxl

    book = openpyxl.load_workbook(filename='some_file.xlsx')
    sheet = book.active

    header = [cell.value for cell in sheet[1]]
    for row in sheet:
        values = {}
        for k, cell in zip(header, row):
            values[k] = cell.value
        print(values)

Load openoffice calc table, skip first two rows

    import pyexcel_ods

    data = pyexcel_ods.get_data('some_file.ods')
    header = data['hosts'][0]
    for row in data['hosts'][2:]: # start reading third line
        values = {}
        for key, val in zip(header, row):
            values[key] = val
        print(values)
