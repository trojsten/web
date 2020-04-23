# -*- coding: utf-8 -*-

import codecs
import os
import re

"""Prask zwarte doos forked from ./plugin_ksp_32_2_1 created by Sysel"""

__author__ = "SamoM"


class Level1(object):

    TARGET = "35473936"

    @classmethod
    def run(cls, x, try_count):
        return str(x ** 2)


class Level2(object):

    TABLE = [
        "-",
        "H",
        "He",
        "Li",
        "Be",
        "B",
        "C",
        "N",
        "O",
        "F",
        "Ne",
        "Na",
        "Mg",
        "Al",
        "Si",
        "P",
        "S",
        "Cl",
        "Ar",
        "K",
        "Ca",
        "Sc",
        "Ti",
        "V",
        "Cr",
        "Mn",
        "Fe",
        "Co",
        "Ni",
        "Cu",
        "Zn",
        "Ga",
        "Ge",
        "As",
        "Se",
        "Br",
        "Kr",
        "Rb",
        "Sr",
        "Y",
        "Zr",
        "Nb",
        "Mo",
        "Tc",
        "Ru",
        "Rh",
        "Pd",
        "Ag",
        "Cd",
        "In",
        "Sn",
        "Sb",
        "Te",
        "I",
        "Xe",
        "Cs",
        "Ba",
        "La",
        "Ce",
        "Pr",
        "Nd",
        "Pm",
        "Sm",
        "Eu",
        "Gd",
        "Tb",
        "Dy",
        "Ho",
        "Er",
        "Tm",
        "Yb",
        "Lu",
        "Hf",
        "Ta",
        "W",
        "Re",
        "Os",
        "Ir",
        "Pt",
        "Au",
        "Hg",
        "Tl",
        "Pb",
        "Bi",
        "Po",
        "At",
        "Rn",
        "Fr",
        "Ra",
        "Ac",
        "Th",
        "Pa",
        "U",
        "Np",
        "Pu",
        "Am",
        "Cm",
        "Bk",
        "Cf",
        "Es",
    ]
    TARGET = "Al,I,Ca"

    @classmethod
    def run(cls, x, try_count):
        str_x = str(x)
        elements = []
        start = 0
        if len(str_x) % 2 == 1:
            elements.append(cls.TABLE[int(str_x[0])])
            start = 1
        for i in range(start, len(str_x), 2):
            elements.append(cls.TABLE[int(str_x[i : i + 2])])
        return ",".join(elements)


class Level3(object):

    TARGET = "7907"
    PRIMES = []

    @classmethod
    def generate_primes(cls):
        LIMIT = 10 ** 6
        erat = [True] * LIMIT
        for i in range(2, LIMIT):
            if not erat[i]:
                continue
            cls.PRIMES.append(i)
            for j in range(i, LIMIT, i):
                erat[j] = False

    @classmethod
    def run(cls, x, try_count):
        if not cls.PRIMES:
            cls.generate_primes()
        if x >= len(cls.PRIMES):
            return "PRILIS VELKE"
        return str(cls.PRIMES[x])


class Level4(object):

    TARGET = "Oto"
    DATA = []
    FILE = os.path.join(os.path.dirname(__file__), "mena.txt")

    @classmethod
    def init_data(cls):
        if not cls.DATA:
            with codecs.open(cls.FILE, "r", "utf8") as f:
                cls.DATA = list([name.strip() for name in f])

    @classmethod
    def run(cls, x, try_count):
        cls.init_data()
        return cls.DATA[x % 365]


# class Level5(object):
#
#     TARGET = "5268"
#
#     @classmethod
#     def run(cls, x, try_count):
#         return str(abs(x - try_count))


class Level5(object):
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
    def run(cls, x, try_count):
        str_x = str(x)
        match_array = []
        neg_array = []

        for i in cls.TABLE_MATCH:
            match_array.append('green' if re.match(str_x, i) is not None else 'red')
        for j in cls.TABLE_NEGATIVE:
            neg_array.append('blue' if re.match(str_x, j) is None else 'yellow')
        # TODO 'good' ide ako ma, dokonca aj web ukazuje dobre
        #   ale match_array, neg_array nefunguje
        good = 'red' not in match_array     # and 'yellow' not in neg_array

        return good, match_array, neg_array
        # return good, [1,1,1,1,1], [-1, -1, -1, -1]


class Level6(object):

    TARGET = "3684591"

    @classmethod
    def run(cls, x, try_count):
        ans = ""
        for (i, c) in enumerate(str(x)):
            ans += str((((int(c) - i) % 10) + 10) % 10)
        return ans


class Level7(object):

    TARGET = "24032"
    PRIMES = [
        2,
        3,
        5,
        7,
        11,
        13,
        17,
        19,
        23,
        29,
        31,
        37,
        41,
        43,
        47,
        53,
        59,
        61,
        67,
        71,
        73,
        79,
        83,
        89,
        97,
        101,
        103,
        107,
        109,
        113,
    ]
    BAD_NUM = "BLBE_CISLO"

    @classmethod
    def run(cls, x, try_count):
        prime_count = [0] * len(cls.PRIMES)
        for i in range(len(cls.PRIMES)):
            while x % cls.PRIMES[i] == 0:
                prime_count[i] += 1
                if prime_count[i] >= 10:
                    return cls.BAD_NUM
                x /= cls.PRIMES[i]

        return cls.BAD_NUM if x != 1 else "".join([str(c) for c in prime_count]).rstrip("0")


class Level8(object):

    TARGET = "214365"

    @classmethod
    def run(cls, x, try_count):
        digits = list(map(int, str(x)))
        last = digits[0]
        num = 1
        res = ""
        for i in digits[1:] + [None]:
            if last == i:
                num += 1
            else:
                res += "%d%d" % (last, num)
                last = i
                num = 1
        return res


class Level9(object):

    TARGET = "31L17D"

    @classmethod
    def run(cls, x, try_count):
        n = int(x ** 0.5) // 2
        x -= 4 * n * n
        if x < 2 * n + 1:
            pos = (-n, n - x)
        elif x < 4 * n + 2:
            pos = (-n + 1 + (x - 2 * n - 1), -n)
        elif x < 6 * n + 3:
            pos = (n + 1, -n + 1 + (x - 4 * n - 2))
        else:
            pos = (n - (x - 6 * n - 3), n + 1)

        ypos = "" if pos[1] == 0 else str(abs(pos[1])) + ("H" if pos[1] > 0 else "D")
        xpos = "" if pos[0] == 0 else str(abs(pos[0])) + ("P" if pos[0] > 0 else "L")
        return "DALEKO" if len(xpos + ypos) > 30 else xpos + ypos


class Level10(object):

    TARGET = "8"

    @classmethod
    def run(cls, x, try_count):
        return str(bin(x).count("1"))


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
