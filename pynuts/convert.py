#!/usr/bin/env python

import collections

from pynuts import units
from pynuts import tokens

Conv = collections.namedtuple('Conversion', ['frm', 'to', 'func'])

convs = []

def factor_conv(frm, to, factor):
    factor = float(factor)
    return [
        Conv(frm, to, lambda x: x * factor),
        Conv(to, frm, lambda x: x / factor),
        Conv(units.Unit() / frm, units.Unit() / to, lambda x: x / factor),
        Conv(units.Unit() / to, units.Unit() / frm, lambda x: x * factor)
        ]

def equiv_conv(frm, to):
    return factor_conv(frm, to, 1)

def get_convs(convs, frm=None, to=None):
    ret = []
    for conv in convs:
        if (frm is None or frm == conv.frm) and (to is None or to == conv.to):
            ret.append(conv)
    return ret

def load_convs(filename):
    convs = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.split()
            convs.extend(factor_conv(
                    tokens.parse_infix(parts[0]),
                    tokens.parse_infix(parts[1]),
                    parts[2]))
    return convs

def find_convpath(convs, frm, to, seen=[]):
    if frm.units == to.units:
        # already there, noop.
        return []
    
    direct = get_convs(convs, frm, to)
    if len(direct) != 0:
        # Found a single step to get directly to the target
        return [direct[0]]

    if len(convs) == 0:
        return None

    branches = frm.subunits()
    for branch in branches:
        potentials = get_convs(convs, branch)
        for conv in potentials:
            newfrm = frm / conv.frm * conv.to
            if not newfrm in seen:
                foo = find_convpath(convs, newfrm, to, seen + [newfrm])
                if foo != None:
                    return [conv] + foo

def simplify(convs, frm, original=None, seen=[]):
    if original is None:
        original = frm
        seen = [frm]
    branches = frm.subunits()
#    if len(list(branches)) == 0:
#        return frm
    for branch in branches:
        potentials = get_convs(convs, branch)
        for conv in potentials:
            newfrm = frm / conv.frm * conv.to
            if not newfrm in seen:
                foo = simplify(convs, newfrm, original, seen + [newfrm])
                if foo is not None and len(foo.units) < len(original.units):
                    return foo
                elif len(newfrm.units) < len(original.units):
                    return newfrm

convs = load_convs('data.txt')

def apply_convpath(val, path):
    for conv in path: 
        val = conv.func(val)
    return val

def convert(convs, frm, to):
    path = find_convpath(convs, frm, to)
    value = apply_convpath(frm.value, path)
    ret = units.Unit() * to
    ret.value = value
    return ret

#path = find_convpath(convs, meter/second, kilometer/hour)
#path = find_convpath(convs, meter, kilometer)
#path = find_convpath(convs, tokens.parse_infix('W h'), tokens.parse_infix('J'))
#print apply_convpath(tokens.parse_infix('2 W h'), path)

print convert(convs, tokens.parse_infix('W h'), tokens.parse_infix('J'))

print "Simplify J/h:"

jph = tokens.parse_infix('J/h')

target = simplify(convs, jph)
print convert(convs, jph, target)
#path = find_convpath(convs, tokens.parse_infix('J/h'), target)
#print path
#print apply_convpath(tokens.parse_infix('J/h'), path)

