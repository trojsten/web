# import json
# from typing import Callable, Literal

# STEPS = 0
# MAX_STEPS = 1_000_000
# DEBUG = True


# def step(what, ret, *args):
#     global STEPS
#     STEPS += 1

#     if STEPS > MAX_STEPS:
#         raise Exception(f"Maximum number of steps reached ({MAX_STEPS})")

#     if DEBUG:
#         print(f"{what}({args}) -> {ret}")


# def zero():
#     def new() -> Literal[0]:
#         step("zero", 0)
#         return 0

#     return new


# def incrementor():
#     def new(x: int):
#         step("incrementor", x + 1, x)
#         return x + 1

#     return new


# def selector(which: int) -> Callable:
#     which -= 1

#     def new(*args: int):
#         if which >= len(args):
#             raise Exception(
#                 f"You tried to select input #{which}, but you have given only {len(args)} inputs"
#             )
#         step("selector", args[which], *args)
#         return args[which]

#     return new


# def compositor(g: Callable, *f: Callable) -> Callable:
#     def new(*args):
#         ret = g(*[x(*args) for x in f])
#         step("compositor", ret, *args)
#         return ret

#     return new


# def repeater(f: Callable, g: Callable):
#     def new(*args: int):
#         x = args[-1]

#         y = args[:-1]

#         tmp = f(*y)
#         for i in range(x):
#             tmp = g(i, *y, tmp)

#         step("repeater", tmp, *[x, *y])
#         return tmp

#     return new


# # def unpack(data: dict):
# #     match data["type"]:
# #         case "zero":
# #             return zero()
# #         case "incrementor":
# #             return incrementor()
# #         case "selector":
# #             return selector(*data["args"])
# #         case "repeater":
# #             return repeater(unpack(data["args"][0]), unpack(data["args"][1]))
# #         case "compositor":
# #             return compositor(
# #                 unpack(data["args"][0]), *[unpack(x) for x in data["args"][1:]]
# #             )
# #         case _:
# #             raise Exception(f"Unknown type: {data['type']}")


# def unpack_blockly(block: dict):
#     match block["type"]:
#         case "start":
#             return unpack_blockly(block["inputs"]["x"]["block"])
#         case "zero":
#             return zero()
#         case "incrementor":
#             return incrementor()
#         case "selector":
#             return selector(block["fields"]["index"])
#         case "repeater":
#             return repeater(
#                 unpack_blockly(block["inputs"]["init"]["block"]),
#                 unpack_blockly(block["inputs"]["step"]["block"]),
#             )
#         case "compositor":
#             childs = []
#             for i in range(1, block["extraState"]["itemCount"]):
#                 childs.append(unpack_blockly(block["inputs"]["f" + str(i)]["block"]))
#             return compositor(
#                 unpack_blockly(block["inputs"]["final"]["block"]), *childs
#             )
#         case _:
#             raise Exception(f"Unknown type: {block['type']}")


# # print(
# #     unpack(
# #         json.loads(
# #             '{"type":"repeater","args":[{"type":"selector","args":[1]},{"type":"compositor","args":[{"type":"incrementor"},{"type":"selector","args":[3]}]}]}'
# #         )
# #     )(3, 5)
# # )

# if __name__ == "__main__":
#     print(
#         unpack_blockly(
#             json.loads(
#                 '{"type":"start","id":"Ia~J%RIOSJInZp`--Z}_","x":10,"y":10,"deletable":false,"movable":false,"inputs":{"x":{"block":{"type":"repeater","id":"LuaU]bpmAEc0JPPrb,|K","inputs":{"init":{"block":{"type":"selector","id":"_2_i@F+VdzQ,6{UiH7s6","fields":{"index":1}}},"step":{"block":{"type":"compositor","id":"QVr9ESD50nuX8I4{;WLU","extraState":{"itemCount":2},"inputs":{"final":{"block":{"type":"incrementor","id":"rvO#lH.|pTekJwd`^vR5"}},"f1":{"block":{"type":"selector","id":"o0f?:r{quzNhkR)?b=`R","fields":{"index":3}}}}}}}}}}}'
#             )
#         )(3, 5)
#     )

#     print(selector(1)(5))
#     print()
#     print(compositor(incrementor(), zero())())
#     print()
#     print(compositor(incrementor(), compositor(incrementor(), incrementor()))(10))
#     print()
#     print(repeater(selector(1), compositor(incrementor(), selector(3)))(3, 5))
#     print()
#     print(repeater(zero(), selector(2))(1))
