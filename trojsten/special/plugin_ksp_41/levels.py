import json
import os

def load_levels():
    levels = []

    with open(os.path.dirname(__file__) + "/static/levels.json") as f:
        data = json.load(f)
        for level in data:
            levels.append(level)

    return levels

levels = load_levels()
