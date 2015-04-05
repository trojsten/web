# -*- coding: utf-8 -*-

import random


class A(object):

    NAME = "Agátová"

    MORE = 1
    LESS = -1

    @staticmethod
    def get_initial_state():
        return [1, 1000]

    @staticmethod
    def response(number, state, previous):
        mini, maxi = state

        if number < mini:
            return A.MORE, state, False

        if number > maxi:
            return A.LESS, state, False

        if maxi == mini:
            if len(previous) < 10:
                return 3, state, True
            if len(previous) < 20:
                return 2, state, True
            return 1, state, True

        if number - mini > maxi - number:
            return A.LESS, (mini, number-1), False
        else:
            return A.MORE, (number+1, maxi), False

    @staticmethod
    def format(response):
        if response == A.MORE:
            return 'Prefíkaný kocúr býva vyššie'
        else:
            return 'Prefíkaný kocúr býva nižšie'


class B(object):

    NAME = "Biela"

    @staticmethod
    def get_initial_state():
        return (2, 0, 999, 1)

    @staticmethod
    def response(number, state, previous):

        if number == 1 or number == 1000:
            return 0, state, False

        mini, midi, maxi, base = state

        if number < mini:
            border = mini
            for visit in previous:
                if number <= visit.number and visit.number < border:
                    border = visit.number
                    result = visit.response - visit.number + number
            return result, state, False

        if number > maxi:
            border = maxi
            for visit in previous:
                if number >= visit.number and visit.number > maxi:
                    border = visit.number
                    result = visit.response + visit.number - number
            return result, state, False

        if maxi == mini:
            if len(previous) < 20:
                return 3, state, True
            if len(previous) < 40:
                return 2, state, True
            return 1, state, True

        if midi == 0:
            base += max((number-mini), (maxi-number))
            return B._check(base, mini, number, maxi, base)

        if number == midi:
            return base, state, False
        elif number < midi:
            if (midi - mini) > (maxi - midi):
                result = base + (midi - number)
                return B._check(result, mini, number, midi-1, result)
            else:
                result = base - (midi - number)
                return B._check(result, number+1, midi, maxi, base)
        else:
            if (maxi - midi) > (midi - mini):
                result = base + (number - midi)
                return B._check(result, midi+1, number, maxi, result)
            else:
                result = base - (number - midi)
                return B._check(result, mini, midi, number-1, base)

    @staticmethod
    def format(response):
        return 'Prefíkanosť nášho kocúra je %00.3f %%' % (response / 1000.0)

    @staticmethod
    def _check(result, mini, midi, maxi, base):
        if mini == midi:
            return result, (mini+1, 0, maxi, base+1), False
        if maxi == midi:
            return result, (mini, 0, maxi-1, base+1), False
        return result, (mini, midi, maxi, base), False


class C(object):

    NAME = "Cesnaková"

    @staticmethod
    def get_initial_state():
        border = (random.randint(21, 79) + 100*random.randint(0, 1))*1000
        return [border]

    @staticmethod
    def response(number, state, previous):
        return 0, [], True

    @staticmethod
    def format(response):
        return 'Prefíkanosť nášho kocúra je %.3f %%' % (response / 1000.0)

ALL = {'A': A, 'B': B, 'C': C}
