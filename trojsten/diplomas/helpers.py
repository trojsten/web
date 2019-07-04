import io
import json

try:
    from backports import csv
except ImportError:
    import csv


def parse_csv(data):
    f = io.StringIO(data)
    reader = csv.DictReader(f, dialect='excel-tab', strict=True)
    result = [dict(row) for row in reader]
    for row in result:
        for k in row.keys():
            if not k.isalnum():  # Otherwise the reader would parse just about anything...
                raise csv.Error
    return result


def parse_json(data):
    return json.loads(data)
