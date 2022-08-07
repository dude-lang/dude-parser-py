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
        indent = 3

        def dump(el, level: int = 0):
            print('{}{:{len}s}'.format(level * (' ' * indent), el.__repr__(), len=80 - level * indent), end='')

            # No children
            if not list(filter(lambda x: x[0] != '_', dir(el))):
                print()
                return

            first_child = True
            for child in dir(el):
                if '_' == child[0]:
                    continue

                child_el = getattr(el, child)

                if isinstance(child_el, (str, int, float)) or child_el is None:
                    print('{:20s}{}'.format(child, child_el))

                elif isinstance(child_el, (list, tuple)):
                    if first_child:
                        print()
                    for sub in child_el:
                        dump(sub, level + 1)

                else:
                    if first_child:
                        print()
                    dump(child_el, level + 1)

                first_child = False

        try:
            dump(ast)
        except Exception as e:
            print(e)

    if args.export:
        pickle.dump(ast, open(args.file.name + '.ast', 'wb+'))


if __name__ == '__main__':
    main()
