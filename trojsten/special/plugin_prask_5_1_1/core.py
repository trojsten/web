# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import codecs
import os

"""Prask zwarte doos forked from ./plugin_ksp_32_2_1 created by Sysel"""

__author__ = "Siegrift"


class Level1(object):

    TARGET = "35473936"

    @classmethod
    def run(cls, x, try_count):
        return str(x**2)


class Level2(object):

    TARGET = "196418"

    @classmethod
    def run(cls, x, try_count):
        a, b = 0, 1
        for i in range(x):
            a, b = b, a + b
            if len(str(a)) > 30:
                return 'PRILIS VELKE'
        return str(a)


class Level3(object):

    TARGET = "3528"

    @classmethod
    def run(cls, x, try_count):
        new_x = x
        if x % 2 == 0:
            new_x *= 3
        if x % 3 == 0:
            new_x *= 2
        return str(new_x)


class Level4(object):

    TARGET = "3684591"

    @classmethod
    def run(cls, x, try_count):
        ans = ''
        for (i, c) in enumerate(str(x)):
            ans += str((((int(c) - i) % 10) + 10) % 10)
        return ans


class Level5(object):

    TARGET = '5268'

    @classmethod
    def run(cls, x, try_count):
        return str(abs(x - try_count))


class Level6(object):

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


class Level7(object):

    TARGET = "24032"
    PRIMES = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
        71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113
    ]
    BAD_NUM = 'BLBE_CISLO'

    @classmethod
    def run(cls, x, try_count):
        prime_count = [0] * len(cls.PRIMES)
        for i in range(len(cls.PRIMES)):
            while x % cls.PRIMES[i] == 0:
                prime_count[i] += 1
                if prime_count[i] >= 10:
                    return cls.BAD_NUM
                x /= cls.PRIMES[i]

        return cls.BAD_NUM if x != 1 else ''.join(
            [str(c) for c in prime_count]).rstrip('0')


class Level8(object):

    TARGET = "8"

    @classmethod
    def run(cls, x, try_count):
        return str(bin(x).count('1'))


class Level9(object):

    TARGET = "31L17D"

    @classmethod
    def run(cls, x, try_count):
        n = int(x**0.5) // 2
        x -= 4 * n * n
        if x < 2 * n + 1:
            pos = (-n, n - x)
        elif x < 4 * n + 2:
            pos = (-n + 1 + (x - 2 * n - 1), -n)
        elif x < 6 * n + 3:
            pos = (n + 1, -n + 1 + (x - 4 * n - 2))
        else:
            pos = (n - (x - 6 * n - 3), n + 1)

        ypos = '' if pos[1] == 0 else str(abs(pos[1])) + ('H' if pos[1] > 0
                                                          else 'D')
        xpos = '' if pos[0] == 0 else str(abs(pos[0])) + ('P' if pos[0] > 0
                                                          else 'L')
        return 'DALEKO' if len(xpos + ypos) > 30 else xpos + ypos


class Level10(object):

    TARGET = "8"

    @classmethod
    def roman_size(cls, num):
        res = 0
        size = [9, 5, 4, 1]
        count = [2, 1, 2, 1]
        for i in range(100, -1, -1):
            for j in range(0, 4):
                while num - 10 ** i * size[j] >= 0:
                    num -= 10 ** i * size[j]
                    res += count[j]
        return res

    @classmethod
    def run(cls, x, try_count):
        return str(cls.roman_size(x))


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
