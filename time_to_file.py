import json


def save_time_to_file(filename, data):
    with open(filename, 'w') as f:
        obj = json.dumps(data)
        f.write(obj)
