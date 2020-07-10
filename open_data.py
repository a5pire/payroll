import json


class Open:

    def __init__(self, json_file):  # initialise class with the json input file
        self.json_file = json_file

    def open_json_file(self):
        with open(self.json_file) as f: # context manager to open the supplied json file
            return json.load(f)
