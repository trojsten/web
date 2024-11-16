import json
import os
import traceback

from .interpreter import run_program


def load_levels():
    levels = []

    with open(os.path.dirname(__file__) + "/static/levels2.json") as f:
        data = json.load(f)
        for level in data:
            levels.append(level)

    return levels


levels = load_levels()


def test_program(program, level):
    level_id = level["zadanie"].split(".")[0]
    path = os.path.dirname(__file__) + "/inputs/" + level_id
    vstupy = read_file(path + "/in")
    ocakavane_vystupy = read_file(path + "/out")
    for i in range(len(vstupy)):
        allowed = set()
        if "allowed" in level:
            allowed = set(level["allowed"])
        try:
            output = run_program(
                program, allowed, level["timelimit"], map(int, vstupy[i].split())
            )
            if output != int(ocakavane_vystupy[i]):
                print("ksp_plugin_41: WA", output, "!=", ocakavane_vystupy[i])
                return "WA"

        except Exception:
            print("ksp_plugin_41:", traceback.format_exc())
            return "TLE"

    return "OK"


def read_file(path):
    lines = []
    with open(path) as f:
        for line in f:
            lines.append(line)
    return lines
