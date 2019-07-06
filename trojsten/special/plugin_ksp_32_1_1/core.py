"""KSP 32.1.1 Specification"""

import datetime
import time

__author__ = "Sysel"


class Level1:

    TARGET = 47

    @staticmethod
    def run(x):
        return int(x) + 1


class Level2:

    TARGET = "123"

    @staticmethod
    def run(x):
        return "".join(reversed(str(x)))


class Level3:

    TARGET = 42

    @staticmethod
    def run(x):
        return sum(map(int, str(x)))


class Level4:

    SECRET = 14159265

    TARGET = "OK"

    @staticmethod
    def run(x):
        if int(x) < Level4.SECRET:
            return "VIAC"
        if int(x) > Level4.SECRET:
            return "MENEJ"
        return "OK"


class Level5:

    TARGET = "25252525"

    @staticmethod
    def run(x):
        digits = list(map(int, str(x)))
        for i in range(len(digits)):
            digits[i] += i
            digits[i] %= 10
        return "".join(map(str, digits))


class Level6:

    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    SIZE = 26

    TARGET = "PAPAGAJ"

    @staticmethod
    def run(x):
        x = int(x)
        length = 0
        while Level6.SIZE ** length <= x:
            x -= Level6.SIZE ** length
            length += 1
        result = ""
        while length:
            result = Level6.UPPERCASE[x % Level6.SIZE] + result
            x //= Level6.SIZE
            length -= 1
        return result


class Level7:

    TARGET = "POKLAD"

    WAY = [
        101010,
        1149586,
        625298,
        887442,
        756370,
        821906,
        789138,
        805522,
        797330,
        801426,
        799378,
        800402,
        799890,
        800146,
        800018,
        800082,
        800050,
        800066,
        800058,
        800062,
        800060,
        800061,
        "POKLAD",
    ]

    @staticmethod
    def run(x):
        x = int(x)
        if x in Level7.WAY:
            return Level7.WAY[1 + Level7.WAY.index(x)]
        else:
            return Level7.WAY[0]


class Level8:

    TARGET = "123456"

    @staticmethod
    def run(x):
        x = int(x)
        digits = list(map(int, str(x)))
        last = digits[0]
        num = 1
        res = ""
        for i in digits[1:] + [None]:
            if last == i:
                num += 1
            else:
                res += "%d%d" % (num, last)
                last = i
                num = 1
        return res


class Level9:

    TARGET = "04:13"

    @staticmethod
    def run(x):
        x = int(x) % (24 * 60)
        d = datetime.datetime.fromtimestamp(time.time() + x * 47 * 60)
        return "%02d:%02d" % (d.hour, d.minute)


class Level10:

    TARGET = "Boris a Hanka z Ganoviec"

    BOYS = ("Adam Boris Cyril Dusan Emil Fero Gustav " "Hugo Ivan Jozo Kubo Laco Miso").split(" ")

    GIRLS = ("Anicka Betka Cecilia Danka Eva Filomena Gabika " "Hanka Iveta Janka Katka").split(" ")

    TOWNS = ("Aleksiniec Bernolakova Cerovej Danisoviec " "Egresa Filakova Ganoviec").split(" ")

    @staticmethod
    def run(x):
        x = int(x)
        return "%s a %s z %s" % (Level10.BOYS[x % 13], Level10.GIRLS[x % 11], Level10.TOWNS[x % 7])


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
