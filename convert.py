#!/usr/bin/env python

import pyunits
import collections
import tokens

Conv = collections.namedtuple('Conversion', ['frm', 'to', 'func'])

convs = []

def factor_conv(frm, to, factor):
    factor = float(factor)
    return [
        Conv(frm, to, lambda x: x * factor),
        Conv(to, frm, lambda x: x / factor),
        Conv(pyunits.Unit() / frm, pyunits.Unit() / to, lambda x: x / factor),
        Conv(pyunits.Unit() / to, pyunits.Unit() / frm, lambda x: x * factor)
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
    if frm == to:
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

convs = load_convs('data.txt')

#path = find_convpath(convs, meter/second, kilometer/hour)
#path = find_convpath(convs, meter, kilometer)
path = find_convpath(convs, tokens.parse_infix('W h'), tokens.parse_infix('J'))

val = 1

for conv in path:
    print val
    print conv
    val = conv.func(val)

print val
