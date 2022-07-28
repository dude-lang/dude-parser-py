import os
import sys
from argparse import ArgumentParser, FileType
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pickle

sys.path.append(str(os.path.dirname(__file__) + '\\..'))

from dude_parser import parse


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('--file', '-f', type=FileType('r', encoding='utf-8'), required=True)
    parser.add_argument('--export', '-e', action='store_true')
    parser.add_argument('--print', '-p', action='store_true')
    parser.add_argument('--time', '-t', action='store_true')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    t1 = datetime.now()
    ast = parse(args.file.read())
    t2 = datetime.now()

    if args.time:
        d = relativedelta(t2, t1).normalized()
        print(f'Parsing took {d.seconds}s {d.microseconds // 1000}ms')

    if args.print:
        def p(el, indent: str = ''):
            print(indent, el)
            for e in dir(el):
                if '_' not in e:
                    child = getattr(el, e)
                    if not isinstance(child, (str, int, float)):
                        if isinstance(child, (list, tuple)):
                            print(indent, len(child), 'children:')
                            for s in child:
                                p(s, indent + '  ')
                        else:
                            p(child, indent + '  ')

        p(ast)

    if args.export:
        pickle.dump(ast, open(args.file.name + '.ast', 'wb+'))


if __name__ == '__main__':
    main()
