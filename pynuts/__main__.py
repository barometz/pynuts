import argparse
import time

import tokens
import convert

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert or simplify units, values and expressions.  All \
expressions should be provided in quotes.')
    parser.add_argument('expr', help=
                        'The expression you want to simplify or convert')
    parser.add_argument('--to', '-t', help=
                        'The unit you want the result to be converted to')
    parser.add_argument('--debug', '-D', action='store_true', help=
                        'Print timing info for debugging purposes')
    args = parser.parse_args()
    start = time.clock()
    convs = convert.load_convs('data.txt')
    if args.debug:
        print 'Loaded conversions: ' + str(time.clock() - start)
    frm = tokens.parse_infix(args.expr)
    if args.debug:
        print 'Parsed source: ' + str(time.clock() - start)
    if args.to is None:
        target = convert.simplify(convs, frm)
        if args.debug:
            print 'Simplified source: ' + str(time.clock() - start)
        print convert.convert(convs, frm, target)
        if args.debug:
            print 'Converted: ' + str(time.clock() - start)
    else:
        to = tokens.parse_infix(args.to)
        if args.debug:
            print 'Parsed target: ' + str(time.clock() - start)
        print convert.convert(convs, frm, to)
        if args.debug:
            print 'Converted: ' + str(time.clock() - start)
