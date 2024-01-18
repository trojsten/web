# -*- coding: utf-8 -*-

import codecs
import os
from datetime import datetime
from math import sqrt
from string import ascii_uppercase

"""Prask zwarte doos forked from ./plugin_prask_5_1_1"""

__author__ = "Siegrift"


class Level1(object):
    TARGET = "G"

    @classmethod
    def run(cls, x, try_count):
        return str(ascii_uppercase[x % len(ascii_uppercase)])


class Level2(object):
    GEPARD_MOVEMENT_SPEED = 110
    TARGET = "531.54 Geparda"

    @classmethod
    def run(cls, x, try_count):
        return "%.2f Geparda" % (x / cls.GEPARD_MOVEMENT_SPEED)


class Level3(object):
    DIGITS_FIRST_LETTERS = "NJDTŠPŠSOD"
    TARGET = "JNJNDŠ"

    @classmethod
    def run(cls, x, try_count):
        return "".join([cls.DIGITS_FIRST_LETTERS[ord(d) - ord("0")] for d in str(x)])


class Level4(object):
    TARGET = "20"

    @classmethod
    def run(cls, x, try_count):
        divs = 0
        for i in range(1, 1 + int(sqrt(x))):
            if x % i == 0:
                divs += 1 if x == i ** 2 else 2
        return str(divs)


class Level5(object):
    TARGET = "Rozpaprčená"
    DATA = []
    FILE = os.path.join(os.path.dirname(__file__), "tapakovci.txt")

    @classmethod
    def init_data(cls):
        if not cls.DATA:
            with codecs.open(cls.FILE, "r", "utf8") as f:
                cls.DATA = list(f)

    @classmethod
    def run(cls, x, try_count):
        cls.init_data()
        try:
            return Level5.DATA[x][:-1]
        except IndexError:
            return ""


class Level6(object):
    TARGET = "Merkúr 8913.28"
    PLANETS = [
        ("Merkúr", 0.38),
        ("Venuša", 0.9),
        ("Zem", 1),
        ("Mars", 0.38),
        ("Jupiter", 2.36),
        ("Saturn", 0.92),
        ("Urán", 0.89),
        ("Neptún", 1.13),
        ("Pluto", 0.07),
    ]

    @classmethod
    def run(cls, x, try_count):
        if x == 0:
            return "NIČ"
        if x < 10:
            return cls.PLANETS[x - 1][0]

        x = str(x)
        first_digit, weight = int(x[0]), int(x[1:])
        return "{} {:.2f}".format(
            cls.PLANETS[first_digit - 1][0],
            cls.PLANETS[first_digit - 1][1] * weight,
        )


class Level7(object):
    TARGET = "2018-12-28T05:10:15"

    @classmethod
    def run(cls, x, try_count):
        return datetime.utcfromtimestamp(x).isoformat()


class Level8(object):
    TARGET = "Lothar Collatz 111"

    @classmethod
    def run(cls, x, try_count):
        if x == 0:
            return 0

        ans = 0
        while x != 1:
            ans += 1
            if x % 2 == 0:
                x //= 2
            else:
                x = x * 3 + 1
        return "Lothar Collatz %d" % ans


class Level9(object):
    TARGET = "432"
    MAX = 10 ** 10
    PRIMES = []

    @classmethod
    def init_primes(cls):
        mx = int(sqrt(cls.MAX) + 1)
        sieve = [True] * mx
        for p in range(2, mx):
            if sieve[p]:
                cls.PRIMES.append(p)
                for x in range(p, mx, p):
                    sieve[x] = False

    @classmethod
    def run(cls, x, try_count):
        if len(cls.PRIMES) == 0:
            cls.init_primes()

        if x <= 1:
            return x
        else:
            phi = 1
            for p in cls.PRIMES:
                if x % p != 0:
                    continue

                c = 0
                while x % p == 0:
                    c += 1
                    x //= p
                phi *= (p ** (c - 1)) * (p - 1)

            return str(phi if x == 1 else phi * (x - 1))


class Level10(object):
    TARGET = "TABULKA"

    @classmethod
    def run(cls, x, try_count):
        if x == 0:
            return "A"

        ans = ""
        while x != 0:
            ans += chr((x % len(ascii_uppercase)) + ord("A"))
            x //= len(ascii_uppercase)
        return ans[::-1]


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
