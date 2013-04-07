#!/usr/bin/env python

import parsley
import collections
import pyunits
import sys

# 
# There are 5 kinds of tokens:
# NUM:    For numbers, both integral and float.
# UNIT:   For simple units. "m" is a unit.
# MUL:    For operators * and /
# POW:    For exponentation (^2)
# SUBEXP: For subexpressions, such as (a b) in c/(a b)
# The subexpressions are a little odd to have as a token, but it was easy to
# implement in parsley and makes the recursive processing later on a bit easier.
#
Token = collections.namedtuple('Token', ['name', 'value'])

# Holds parsers (as produced by parsley.makeGrammar) for different notations
_parsers = {}

def cobble(tokens):
    power = 1
    temp = pyunits.Unit()
    prevtoken = Token('NUM', 1)
    current = pyunits.Unit()
    nextop = '*'

    unitlist = [pyunits.Unit()]

    for token in tokens:
        # Extract a Datum or Unit, if any.
        if token.name == 'NUM':
            temp = pyunits.Datum(token.value)
        elif token.name == 'UNIT':
            temp = pyunits.Unit(**{token.value: 1})
        elif token.name == 'SUBEXP':
            temp = cobble(token.value)

        # Process the token
        if token.name in ['NUM', 'UNIT', 'SUBEXP']:
            unitlist.append(pyunits.Unit())
            if nextop == '/':
                unitlist[-1] /= temp
                nextop = '*'
            elif nextop == '*':
                unitlist[-1] *= temp
        elif token.name == 'POW':
            unitlist[-1] = unitlist[-1] ** token.value
        elif token.name == 'MUL':
            nextop = token.value

    ret = pyunits.Unit()
    for unit in unitlist:
        ret *= unit

    return ret

def parse_infix(text):
    if not 'infix' in _parsers:
        grammar = """
subexp  = '(' (token | subexp)+:ts ')' ws -> Token('SUBEXP', ts)
token   = fnumber | number | pow | op | unit
tokens  = token+:ts -> ts
expr = (subexp | token)+

number  = <digit+>:ds ws -> Token('NUM', int(ds))
fnumber = <digit+>:whole '.' <digit+>:dec ws -> Token('NUM', float(whole + '.' + dec))
unit    = <letter+>:sym ws -> Token('UNIT', sym)
op      = ('*' | '/'):sym ws -> Token('MUL', sym)
pow     = '^' number:exp ws -> Token('POW', exp.value)

"""
        _parsers['infix'] = parsley.makeGrammar(grammar, {'Token': Token})
    tokenized = _parsers['infix'](text).expr()
    return cobble(tokenized)

def testrun():
    """Several testcases for the tokenizer and parser.

    Implemented like this rather than with proper unittests as currently this
    is all that needs testing.
    
    """
    tests = [
        ('a', 1, {'a': 1}),
        ('a * b', 1, {'a': 1, 'b': 1}),
        ('a* b', 1, {'a': 1, 'b': 1}),
        ('a*b', 1, {'a': 1, 'b': 1}),
        ('(a)*b', 1, {'a': 1, 'b': 1}),
        ('(a) * b', 1, {'a': 1, 'b': 1}),
        ('a b^2', 1, {'a': 1, 'b': 2}),
        ('a*b^2', 1, {'a': 1, 'b': 2}),
        ('a/b^2', 1, {'a': 1, 'b': -2}),
        ('a/(b a)', 1, {'b': -1}),
        ('a/a a', 1, {'a': 1}),
        ('a/(a^2)', 1, {'a': -1}),
        ('a b/c c^2/b', 1, {'a': 1, 'c': 1}),
        ('a^2/(3b)', 1.0/3, {'a': 2, 'b': -1}),
        ]
    for test in tests:
        result = parse_infix(test[0])
        if result.value != test[1] or result.units != test[2]:
            print 'MISMATCH'
            print 'Source: ' + test[0]
            print 'Target: {0} {1}'.format(test[1], test[2])
            print 'Result: {0} {1}'.format(result.value, result.units)


if __name__ == '__main__':
    if len(sys.argv) != 1:
        text = ' '.join(sys.argv[1:])
        print parseunits(text)
    else:
        testrun()
