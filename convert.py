#!/usr/bin/env python

import pyunits
import collections

meter = pyunits.Unit(m=1)
yard = pyunits.Unit(yd=1)
inch = pyunits.Unit(**{'in': 1})
centimeter = pyunits.Unit(cm=1)
second = pyunits.Unit(s=1)
hour = pyunits.Unit(h=1)
kilometer = pyunits.Unit(km=1)
watt = pyunits.Unit(W=1)
joule = pyunits.Unit(J=1)

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

convs.extend(factor_conv(meter, centimeter, 100))
convs.extend(factor_conv(inch, centimeter, 2.54))
convs.extend(factor_conv(yard, inch, 36))
convs.extend(factor_conv(hour, second, 3600))
convs.extend(factor_conv(kilometer, meter, 1000))
convs.extend(equiv_conv(watt, joule/second))

cmconv = get_convs(convs, centimeter)

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

#path = find_convpath(convs, meter/second, kilometer/hour)
#path = find_convpath(convs, meter, kilometer)
path = find_convpath(convs, watt * hour, joule)

val = 1

for conv in path:
    print val
    print conv
    val = conv.func(val)

print val
