#!/usr/bin/env python

import itertools

def removezeroes(d):
    for k, v in d.iteritems():
        if v == 0:
            del d[k]
    
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

class Datum(object):
    def __init__(self, value, **exps):
        self.value = value
        self.units = {}
        # Copy units and exponents, discarding zero
        for unit, exp in exps.iteritems():
            if exp != 0:
                self.units[unit] = exp

    def subunits(self):
        """Yield all units (compound and simple) that exist here

        For example, from m^2/s this would return m, m^2, m^2/s, m/s and 1/s.

        """
        ls = []
        for unit, exp in self.units.iteritems():
            while exp > 0:
                ls.append((unit, 1))
                exp -= 1
            while exp < 0:
                ls.append((unit, -1))
                exp += 1
        combos = set(powerset(ls))
        for combo in combos:
            if combo == ():
                continue
            ret = Unit()
            for unit in combo:
                ret *= Unit(**{unit[0]: unit[1]})
            yield ret
        
    def __pow__(self, other, modulo=None):
        exps = self.units.copy()
        for unit in exps:
            exps[unit] *= other
        return Datum(self.value ** other, **exps)

    def __mul__(self, other):
        exps = self.units.copy()
        for unit, exp in other.units.iteritems():
            if unit in exps:
                exps[unit] += exp
            else:
                exps[unit] = exp
        return Datum(self.value * other.value, **exps)

    def __div__(self, other):
        exps = other.units.copy()
        for unit, exp in exps.iteritems():
            exps[unit] = -1 * exp
        return self * Datum(float(self.value) / other.value, **exps)

    def __str__(self):
        ret = "{0} ".format(self.value)

        positives = filter(lambda x: x[1] > 0, self.units.items())
        negatives = filter(lambda x: x[1] < 0, self.units.items())
        
        numerator = ''
        denominator = ''

        def chain(units):
            ret = ''
            for unit, exp in units:
                exp = abs(exp)
                if exp == 1:
                    ret += unit + ' '
                else:
                    ret += '{0}^{1} '.format(unit, exp)
            if len(units) > 1:
                ret = '(' + ret.strip() + ')'
            return ret.strip()

        if len(positives) == 0:
            numerator = '1'
        else:
            numerator = chain(positives)
        if len(negatives) > 0:
            denominator = ' / ' + chain(negatives)
        ret += '(' + numerator + denominator + ')'

        return ret

    def __repr__(self):
        ret = "Datum({0}".format(self.value)
        for unit, exp in self.units.items():
            ret += ", {0}={1}".format(unit, exp)
        ret += ")"
        return ret

    def __eq__(self, other):
        """Equality test for a Datum.

        Two Datum instances are considered equal when:
        - The values are the same
        - The units dictionaries contain only the same units
        - The exponents for those units match
        Conveniently these last two can be checked for with dictionary 
        equality.
        """
        if self.value == other.value and self.units == other.units:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.value == other.value

class Unit(Datum):
    def __init__(self, **exps):
        super(Unit, self).__init__(1, **exps)

if __name__=="__main__":
#    speed = Datum(4, m=1, s=-1)
#    time = Datum(2, s=1)
#    print(speed)
    print Datum(5, K=-1, s=-1)
#    unit = Datum(1, m=2, s=-1)
#    for sub in unit.subunits():
#        print sub
