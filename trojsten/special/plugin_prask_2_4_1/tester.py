# coding: utf-8
from __future__ import unicode_literals

import random
from collections import defaultdict
from first import first

POCET_PRVKOV = 16


def dfs(reach, edges, u):
    if u in reach:
        return
    reach[u] = set()
    for v in edges[u]:
        dfs(reach, edges, v)
        reach[u].add(v)
        reach[u] |= reach[v]


def get_reach(queries):
    edges = defaultdict(set)
    for a, b in queries:
        edges[b].add(a)

    reach = dict()
    for i in range(1, POCET_PRVKOV + 1):
        dfs(reach, edges, i)
    return reach


def adversary(reach, a, b):
    if b in reach[a]:
        return b
    if a in reach[b]:
        return a
    arank = min(2, len(reach[a]))
    brank = min(2, len(reach[b]))
    if arank == 0 and brank == 0:
        for k, v in reach.items():
            if len(v) == 1 and a in v:
                arank -= 1
            if len(v) == 1 and b in v:
                brank -= 1
        if arank < brank:
            return a
        if arank > brank:
            return b
    return random.choice((a, b))


def verify(reach, x, numqueries):
    roots = set()
    semiroots = set()
    for k, v in reach.items():
        if len(v) == 0:
            roots.add(k)
        if len(v) == 1:
            semiroots.add(k)

    # Overime, ci x moze byt druhy najvacsi
    if (x not in roots and x not in semiroots) or (len(roots) == 1 and x in roots):
        return 0, "Zle! %d určite nie je druhá najľahšia." % (x,)
    # Overime, ci aj iny moze byt druhy najvacsi
    otherroot = None
    if len(roots) > 1:
        otherroot = first(roots, key=lambda k: k != x)
    if len(semiroots) > 1:
        otherroot = first(semiroots, key=lambda k: k != x)
    if otherroot is not None:
        return 0, "Len tipuješ! Podľa tvojich otázok by druhá najľahšia mohla byť aj %d." % (
            otherroot,
        )
    # OK, nasli ho
    max_points = False
    if numqueries <= 15 + 3:
        points = 10
        max_points = True
    elif numqueries <= 15 + 6:
        points = 8
    elif numqueries <= 15 + 14:
        points = 6
    else:
        points = 4
    message = "Správne! Máš to za %d otázok, takže dostávaš %d %s." % (
        numqueries, points, "body" if points == 4 else "bodov"
    )
    if not max_points:
        message = message + " Podarí sa ti vymyslieť lepšie riešenie?"
    return points, message


def process_question(queries, a, b):
    reach = get_reach(queries)
    greater = adversary(reach, a, b)
    smaller = b if greater == a else a
    queries.append((greater, smaller))


def process_answer(queries, selection):
    reach = get_reach(queries)
    return verify(reach, selection, len(queries))
