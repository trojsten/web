import json
from argparse import Action
from functools import lru_cache
from math import floor, sqrt

STEPS = 0
MAX_STEPS = 10_000_000
DEBUG = False

CALL_STACK = set()

FUNCTIONS = dict()

ALLOWED = set()


def cache(user_function):
    'Simple lightweight unbounded cache.  Sometimes called "memoize".'
    return lru_cache(maxsize=None)(user_function)


class BooleanOptionalAction(Action):
    def __init__(self, option_strings, dest, default=None, required=False, help=None):
        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith("--"):
                option_string = "--no-" + option_string[2:]
                _option_strings.append(option_string)

        type = None
        choices = None
        metavar = None

        super().__init__(
            option_strings=_option_strings,
            dest=dest,
            nargs=0,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(namespace, self.dest, not option_string.startswith("--no-"))

    def format_usage(self):
        return " | ".join(self.option_strings)


def step(func):
    what = func.__name__

    def wrapper(*args: int):
        global STEPS
        STEPS += 1

        if STEPS > MAX_STEPS:
            raise RuntimeError(f"Maximum number of steps reached ({MAX_STEPS})")

        ret = func(*args)

        if DEBUG:
            print(f"{what}({args}) -> {ret}")

        return ret

    return wrapper


@step
def start(func):
    global STEPS, CALL_STACK
    STEPS = 0
    CALL_STACK.clear()

    def _start_inner(*args):
        if next((x for x in args if x < 0), False):
            raise Exception("Input must not include negative numbers")

        return func(*args)

    return _start_inner


def _zero_inner():
    return 0


@step
def zero():
    return _zero_inner


def _incrementor_inner(x):
    return x + 1


@step
def incrementor():
    return _incrementor_inner


@step
def selector(which):
    def _selector_inner(*args):
        if which > len(args):
            raise Exception(
                f"You tried to select input #{which}, but you have given only {len(args)} inputs"
            )
        return args[which - 1]

    return _selector_inner


@step
def compositor(g, *f):
    @cache
    def _compositor_inner(*args):
        return g(*[x(*args) for x in f])

    return _compositor_inner


@step
def repeater(f, g):
    @cache
    def _repeater_inner(x, *y):
        tmp = f(*y)
        for i in range(x):
            tmp = g(i, *y, tmp)

        return tmp

    return _repeater_inner


@step
def constant(c):
    if "constant" not in ALLOWED:
        raise Exception("Operácia 'constant' nie je povolená!")

    def _constant_inner(*x):
        return c

    return _constant_inner


@step
def math(operation):
    if operation not in ALLOWED:
        raise Exception(f"Operácia '{operation}' nie je povolená!")

    def _math_inner(*x):
        if operation in ("√", "!", "sign", "--"):
            if len(x) != 1:
                raise Exception(
                    f"{operation} vyžaduje práve 1 vstup, ale dostala {len(x)}"
                )

            a = x[0]
            if operation == "√":
                return floor(sqrt(a))
            elif operation == "!":
                return 1 if a == 0 else 0
            elif operation == "sign":
                return min(a, 1)
            elif operation == "--":
                return max(a - 1, 0)

        if len(x) != 2:
            raise Exception(
                f"{operation} vyžaduje práve 2 vstupy, ale dostala {len(x)}"
            )

        a, b = x[0], x[1]

        if operation == "+":
            return a + b
        elif operation == "-":
            return max(a - b, 0)
        elif operation == "*":
            return a * b
        elif operation == "/":
            return a // b
        elif operation == "%":
            return a % b
        elif operation == "^":
            return a**b
        elif operation == ">":
            return 1 if a > b else 0
        elif operation == "≥":
            return 1 if a >= b else 0
        elif operation == "<":
            return 1 if a < b else 0
        elif operation == "≤":
            return 1 if a <= b else 0
        elif operation == "min":
            return min(a, b)
        elif operation == "max":
            return max(a, b)
        else:
            raise Exception(f"Neznáma operácia {operation}")

    return _math_inner


@step
def custom_definition(name, args, f):
    def _custom_definition_inner(*y):
        if len(y) != args:
            raise Exception(
                f"Funkcia {name} vyžaduje {args} vstupov, ale dostala {len(y)}"
            )

        return f(*y)

    return _custom_definition_inner


@step
def custom_usage(fun):
    @cache
    def _custom_usage_inner(*args):
        if fun in CALL_STACK:
            raise Exception(f"Custom block {fun} calls itself!")

        function = FUNCTIONS.get(fun)

        if not function:
            raise Exception(f"Custom block {fun} not defined!")

        CALL_STACK.add(fun)
        ret = function(*args)
        CALL_STACK.remove(fun)

        return ret

    return _custom_usage_inner


def parser_helper(block):
    if block["type"] == "start":
        return parser_helper(block["inputs"]["x"]["block"])
    elif block["type"] == "zero":
        return zero()
    elif block["type"] == "incrementor":
        return incrementor()
    elif block["type"] == "selector":
        return selector(block["fields"]["index"])
    elif block["type"] == "repeater":
        return repeater(
            parser_helper(block["inputs"]["init"]["block"]),
            parser_helper(block["inputs"]["step"]["block"]),
        )
    elif block["type"] == "compositor":
        childs = []
        for i in range(1, block["extraState"]["itemCount"]):
            childs.append(parser_helper(block["inputs"]["f" + str(i)]["block"]))
        return compositor(parser_helper(block["inputs"]["final"]["block"]), *childs)
    elif block["type"] == "constant":
        return constant(block["fields"]["value"])
    elif block["type"] == "math":
        return math(block["fields"]["operation"])
    elif block["type"] == "custom_usage":
        return custom_usage(block["extraState"]["parentId"])
    else:
        raise Exception(f"Unknown block type: {block['type']}")


def parser(blocks):
    startBlock = None
    for block in blocks:
        if block["type"] == "start":
            startBlock = block
        elif block["type"] == "custom_definition":
            FUNCTIONS[block["id"]] = custom_definition(
                block["fields"]["name"],
                block["fields"]["num_arguments"],
                parser_helper(block["inputs"]["start"]["block"]),
            )

    if not startBlock:
        raise Exception("Start block not found!")

    return start(parser_helper(startBlock["inputs"]["x"]["block"]))


def run_program(program, allowed, max_steps, input):
    global ALLOWED, MAX_STEPS
    MAX_STEPS = max_steps
    ALLOWED = allowed
    block = parser(program["blocks"]["blocks"])
    return block(*input)


if __name__ == "__main__":
    import argparse

    cmdparser = argparse.ArgumentParser(
        description="""
Interpreter pre interaktívku z blokov

Ako to funguje:

Vstup zoberie z prvého riadoku stdin ako čísla oddelené medzerami.
Výstup ako číslo na stdout.

Ak program spadne, tak spadne aj interpreter a vypíše hlášku.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Authors: Andrej Lackovič (Aiq0) & Stanislav Bezák (Stanko)",
    )

    cmdparser.add_argument("path", type=str, help="cesta k JSON súboru s programom")
    cmdparser.add_argument("-p", "--profile", action=BooleanOptionalAction)
    cmdparser.add_argument(
        "-a", "--allow", action="append", help="rozšírenia, ktoré sú povolené"
    )
    cmdparser.add_argument("-s", "--max-steps", type=int, help="maximálny počet krokov")

    args = cmdparser.parse_args()

    if args.max_steps:
        MAX_STEPS = args.max_steps

    ALLOWED = set(args.allow if args.allow is not None else [])

    with open(args.path) as f:
        inp = [int(x) for x in input().split()]

        if args.profile:
            import cProfile
            import io
            import pstats

            pr = cProfile.Profile()
            pr.enable()

        block = parser(json.loads(f.read())["blocks"]["blocks"])

        print(block(*inp))

        if args.profile:
            pr.disable()
            s = io.StringIO()
            pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats()
            print(s.getvalue())
