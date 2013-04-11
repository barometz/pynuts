#!/usr/bin/env python

import collections
import operator
import time

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

def get_convs(convs, frm=None, to=None):
    ret = []
    for conv in convs:
        if (frm is None or frm == conv.frm) and (to is None or to == conv.to):
            ret.append(conv)
    return ret

def load_convs(filename):
    """Read conversion factors from the given file.
    
    The file format is line-based:
       from [whitespace] to [whitespace] factor
    Anything past the third element is ignored.  Lines starting with # are 
    ignored.

    """
    convs = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.split()
            if line.startswith('#') or len(parts) < 3:
                continue
            convs.extend(factor_conv(
                    tokens.parse_infix(parts[0]),
                    tokens.parse_infix(parts[1]),
                    parts[2]))
    return convs

def find_conversion_path(convs, frm, to=None, original=None, seen=[]):
    """Find a conversion path, either to a target unit or to a simpler one.

    When `to` is provided this recursively searches for a suitable path among
    the conversion functions.  
    When `to` is None, recursively search for a less complex but equivalent
    unit.

    Gets the subunits of `frm` and applies whatever suitable conversion hasn't
    been tried yet.  Rinse, recurse.  Returns a tuple containing a list of
    conversion functions and the unit they lead to.

    """
    def complexity(u):
        'Complexity metric'
        return sum(abs(x) for x in u.units.values())

    if to is not None:
        # Exit conditions for targeted conversion
        if frm.units == to.units:
            # Reached the target, noop.
            return ([], to)
        direct = get_convs(convs, frm, to)
        if len(direct) != 0:
            # Found a single step to get to the target
            return ([direct[0]], to)

    if original is None:
        original = frm
        seen = [frm]

    for subunit in frm.subunits():
        for conv in get_convs(convs, subunit):
            newfrm = frm / conv.frm * conv.to
            if not newfrm in seen:
                seen.append(newfrm)
                path, _to = find_conversion_path(convs, newfrm, to, original, seen)
                if (_to is not None 
                    # Some path was found
                    and ((to is not None and to.units == _to.units)
                         or complexity(_to) < complexity(newfrm))):
                    # and it's either the target or shorter than what we have
                    return ([conv] + path, _to)
                elif (to is None and complexity(newfrm) < complexity(original)):
                    # Otherwise, see if what we've got is shorter than the original.
                    return ([conv], newfrm)
    # And if all else fails...
    return ([], None)

def convert(convs, frm, to):
    path, _to = find_conversion_path(convs, frm, to)
    value = frm.value
    for conv in path:
        value = conv.func(value)
    ret = _to.copy()
    ret.value = value
    return ret

def simplify(convs, frm):
    return convert(convs, frm, None)

if __name__ == '__main__':
    print 'pynuts conversion demo'
    convs = load_convs('data.txt')
    
#    print convert(convs, tokens.parse_infix('2 W h'), tokens.parse_infix('J'))

    print 'Simplify 2 mol/L * N_A:'

    jph = tokens.parse_infix('2 mol/L * N_A')
    target = simplify(convs, jph)
    print convert(convs, jph, target)

    print 'Convert 3 ha to km^2'
    print convert(convs, tokens.parse_infix('3 ha'), tokens.parse_infix('km^2'))

    print 'Convert 5 furlongs per fortnight to meter per hour'
    print convert(convs, tokens.parse_infix('5 fur/ftn'), tokens.parse_infix('m/h'))
