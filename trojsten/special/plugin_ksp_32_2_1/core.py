# -*- coding: utf-8 -*-

"""KSP 32.2.1 Specification"""

__author__ = "Sysel"

import codecs
import os
from collections import Counter


class Level1:

    TARGET = "47"

    @classmethod
    def run(cls, x):
        return str(2*x+3)


class Level2:

    TARGET = "11628"

    @classmethod
    def run(cls, x):
        return str((x*(x+1))//2)


class Level3:

    TARGET = "529200"

    @classmethod
    def run(cls, x):
        res = 1
        for i in map(int, str(x)):
            res = res * i
        return str(res)


class Level4:

    TARGET = str((37,73))

    @classmethod
    def run(cls, x):
        n = int(x**0.5)//2
        x = x - 4*n*n
        if x < 2*n+1:
            res = (-n,n-x)
        elif x < 4*n+2:
            res = (-n+1+(x-2*n-1),-n)
        elif x < 6*n+3:
            res = (n+1,-n+1+(x-4*n-2))
        else:
            res = (n-(x-6*n-3),n+1)
        return str(res)

class Level5:

    TARGET = u'drúže'
    DATA = []
    FILE = os.path.join(os.path.dirname(__file__),"dom.txt")

    @classmethod
    def init_data(cls):
        if not cls.DATA:
            with codecs.open(cls.FILE,"r","utf8") as f:
                cls.DATA = list(f)

    @classmethod
    def run(cls, x):
        cls.init_data()
        try:
            return Level5.DATA[x][:-1]
        except KeyError:
            return ""


class Level6:

    SECRET = 7182818
    TARGET = "1.000000000000000"

    @classmethod
    def run(cls, x):
        if x <= cls.SECRET:
            res = 1.0/(cls.SECRET - x + 1)
        else:
            res = 1.0/(x - cls.SECRET + 1)
        return "%1.15f" % res


class Level7:

    COUNTS = [6, 2, 5, 5, 4, 5, 6, 3, 7, 6]
    TARGET = "42"

    @classmethod
    def run(cls, x):
        return str(sum(map(cls.COUNTS.__getitem__, map(int, str(x)))))


class Level8:

    TARGET = str(13*7*2*2*2)

    @classmethod
    def divs(cls, x):
        yield 2
        i = 3
        while True:
            yield i
            i+=2

    @classmethod
    def run(cls, x):
        if x == 0: return u'NEKONEČNO'
        res = 1
        for i in cls.divs(x):
            if x == 1:
                return str(res)
            num = 1
            while x % i == 0:
                num += 1
                x //= i
            res *= num


class Level9:

    TARGET = str(1234*1024 + 256)

    @classmethod
    def run(cls, x):
        return str(x * (x&(-x)))


class Level10:

    TARGET = u'7 SPRÁVNE, 0 NA ZLEJ POZÍCII'
    SECRET = "2637033"

    @classmethod
    def run(cls, x):
        x = str(int(x))
        if len(x) < 7:
            return u'KRÁTKE'
        if len(x) > 7:
            return u'DLHÉ'
        spravne = 0
        for i in range(7):
            if cls.SECRET[i] == x[i]:
                spravne+=1
        pozicia = len(list((Counter(cls.SECRET)&Counter(x)).elements()))
        return u'%d SPRÁVNE, %d NA ZLEJ POZÍCII' % (spravne, pozicia-spravne)


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

def test(l, maxi = 20):
    print("Level %d" % l)
    print("Target %s" % str(LEVELS[l].TARGET))
    for x in range(maxi - 20, maxi):
        print("%d -> %s" % (x, str(LEVELS[l].run(x))))