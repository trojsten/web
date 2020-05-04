# -*- coding: utf-8 -*-

import codecs
import os
import re

"""Prask zwarte doos forked from ./plugin_ksp_32_2_1 created by Sysel"""

__author__ = "SamoM"


def run_regex_check(cls, regex, try_count):
    regex = str(regex)
    match_array = []
    neg_array = []

    for i in cls.TABLE_MATCH:
        match_array.append('green' if re.match(regex, i) is not None else 'red')
    for j in cls.TABLE_NEGATIVE:
        neg_array.append('green' if re.match(regex, j) is None else 'red')
    good = 'red' not in match_array and 'red' not in neg_array

    return good, match_array, neg_array


class Level1(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two"
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level2(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level3(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level4(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level5(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level6(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level7(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
        "respite"
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level8(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
        "respite"
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level9(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
        "respite"
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


class Level10(object):

    TABLE_MATCH = [
        "pit",
        "spot",
        "spate",
        "slap two",
        "respite"
    ]

    TABLE_NEGATIVE = [
        "pt",
        "Pot",
        "peat",
        "part"
    ]

    TARGET = True

    @classmethod
    def run(cls, regex, try_count):
        return run_regex_check(cls, regex, try_count)


LEVELS = {
    1: Level1,
    2: Level2,
    3: Level3,
    4: Level4,
    5: Level5,
    6: Level6,
    7: Level7,
    8: Level8,
    9: Level9,
    10: Level10,
}
