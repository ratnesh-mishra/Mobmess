import json


def json_file_to_dict(file):
    config = None

    with open(file) as config_file:
        config = json.load(config_file)

    return config

get_dest_from_key = lambda key: tuple(key.split(":")[1])


