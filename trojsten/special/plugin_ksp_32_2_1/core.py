# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import itertools

"""KSP 32.2.1 Specification"""

__author__ = "Sysel"

import codecs
import os
from collections import Counter


class Level1(object):

    TARGET = "47"

    @classmethod
    def run(cls, x):
        return str(2*x+3)


class Level2(object):

    TARGET = "11628"

    @classmethod
    def run(cls, x):
        return str((x*(x+1))//2)


class Level3(object):

    TARGET = "529200"

    @classmethod
    def run(cls, x):
        res = 1
        for i in map(int, str(x)):
            res *= i
        return str(res)


class Level4(object):

    TARGET = str((37, 73))

    @classmethod
    def run(cls, x):
        n = int(x**0.5)//2
        x -= 4*n*n
        if x < 2*n+1:
            res = (-n, n-x)
        elif x < 4*n+2:
            res = (-n+1+(x-2*n-1), -n)
        elif x < 6*n+3:
            res = (n+1, -n+1+(x-4*n-2))
        else:
            res = (n-(x-6*n-3), n+1)
        return str(res)


class Level5(object):

    TARGET = 'drúže'
    DATA = []
    FILE = os.path.join(os.path.dirname(__file__), "dom.txt")

    @classmethod
    def init_data(cls):
        if not cls.DATA:
            with codecs.open(cls.FILE, "r", "utf8") as f:
                cls.DATA = [""]+list(f)

    @classmethod
    def run(cls, x):
        cls.init_data()
        try:
            return Level5.DATA[x][:-1]
        except IndexError:
            return ""


class Level6(object):

    SECRET = 7182818
    TARGET = "1.000000000000000"

    @classmethod
    def run(cls, x):
        res = 1.0 / (abs(x - cls.SECRET) + 1)
        return "%1.15f" % res


class Level7(object):

    COUNTS = [6, 2, 5, 5, 4, 5, 6, 3, 7, 6]
    TARGET = "42"

    @classmethod
    def run(cls, x):
        return str(sum(map(cls.COUNTS.__getitem__, map(int, str(x)))))


class Level8(object):

    TARGET = str(13*7*2*2*2)

    @classmethod
    def divs(cls):
        yield 2
        for i in itertools.count(start=3, step=2):
            yield i

    @classmethod
    def run(cls, x):
        if x == 0:
            return 'NEKONEČNO'
        res = 1
        for i in cls.divs():
            if x == 1:
                return str(res)
            num = 1
            while x % i == 0:
                num += 1
                x //= i
            res *= num


class Level9(object):

    TARGET = str(1234*1024 + 256)

    @classmethod
    def run(cls, x):
        return str(x * (x & (-x)))


class Level10(object):

    TARGET = '7 SPRÁVNE, 0 NA ZLEJ POZÍCII'
    SECRET = "2637033"

    @classmethod
    def run(cls, x):
        x = str(int(x))
        if len(x) < 7:
            return 'KRÁTKE'
        if len(x) > 7:
            return 'DLHÉ'
        spravne = 0
        for i in range(7):
            if cls.SECRET[i] == x[i]:
                spravne += 1
        pozicia = len(list((Counter(cls.SECRET) & Counter(x)).elements()))
        return '%d SPRÁVNE, %d NA ZLEJ POZÍCII' % (spravne, pozicia-spravne)


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
