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
Token = collections.namedtuple('Token', ['name', 'value'])

# Holds parsers (as produced by parsley.makeGrammar) for different notations
_parsers = {}

def cobble(tokens):
    """Takes a bunch of tokens and turns them into a Datum.

    Keeps a stack of Datum objects in a way that's slightly messy and could
    do with a rewrite.

    """
    # lastvalue is the most recent NUM/UNIT/SUBEXP token
    lastvalue = pyunits.Unit()
    # current accumulates the current value (a plus ^2 makes a^2, etc)
    current = pyunits.Unit()
    # ret accumulates the entire return value
    ret = pyunits.Unit()
    nextop = '*'

    for token in tokens:
        # Extract a Datum or Unit, if any.
        if token.name == 'NUM':
            lastvalue = pyunits.Datum(token.value)
        elif token.name == 'UNIT':
            lastvalue = pyunits.Unit(**{token.value: 1})
        elif token.name == 'SUBEXP':
            lastvalue = cobble(token.value)

        # Process the token
        if token.name in ['NUM', 'UNIT', 'SUBEXP']:
            # push the accumulated value to the return accumulator
            ret *= current
            if nextop == '/':
                # the previous token indicated division, so take the inverse
                current = pyunits.Unit() / lastvalue
                nextop = '*'
            elif nextop == '*':
                current = lastvalue
        elif token.name == 'POW':
            # Raise the last NUM/UNIT/SUBEXP token to the indicated power
            current = lastvalue ** token.value
        elif token.name == 'MUL':
            nextop = token.value

    ret *= current
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
        ('a',       1, {'a': 1}),
        ('a * b',   1, {'a': 1, 'b': 1}),
        ('a* b',    1, {'a': 1, 'b': 1}),
        ('a*b',     1, {'a': 1, 'b': 1}),
        ('(a)*b',   1, {'a': 1, 'b': 1}),
        ('(a) * b', 1, {'a': 1, 'b': 1}),
        ('a b^2',   1, {'a': 1, 'b': 2}),
        ('a*b^2',   1, {'a': 1, 'b': 2}),
        ('a/b^2',   1, {'a': 1, 'b': -2}),
        ('a/(b a)', 1, {'b': -1}),
        ('a/a a',   1, {'a': 1}),
        ('a/(a^2)', 1, {'a': -1}),
        ('a b/c c^2/b', 1, {'a': 1, 'c': 1}),
        ('a^2/(3b)', 1.0/3, {'a': 2, 'b': -1}),
        ]
    for test in tests:
        result = parse_infix(test[0])
        target = pyunits.Datum(test[1], **test[2])
        if result != target:
            print 'MISMATCH'
            print 'Source: ' + test[0]
            print 'Target: ' + repr(target)
            print 'Result: ' + repr(result)


if __name__ == '__main__':
    if len(sys.argv) != 1:
        text = ' '.join(sys.argv[1:])
        print parse_infix(text)
    else:
        testrun()
