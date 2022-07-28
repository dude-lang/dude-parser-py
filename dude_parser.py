import traceback

from iterator import Iterator
from shared import *
from dude_ast import *


dbg = False


def debug(func):
    def wrapper(*args, **kwargs):
        if dbg:
         print(func.__name__, '\n-', '\n- '.join(map(lambda x: x.__repr__(), args)), '\n\n')
        return func(*args, **kwargs)
    return wrapper


# class Peek:
#     def __init__(self, it: Iterator):
#         self._it = it
#         self._pos = it.pos()
#
#     def __enter__(self):
#         pass
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if exc_type == InvalidToken:
#             self._it.seek(self._pos)


# def peek(func):
#     def wrapper(it: Iterator, ast: Program, ctx: Context):
#         pos = it.pos()
#         try:
#             func(it, ast, ctx)
#         except Reset:
#             it.seek(pos)
#
#     return wrapper


class InvalidToken(BaseException):
    def __init__(self, it: Iterator, expected):
        pos = sum(map(len, it.front()))
        sym = it.get()
        hint = ' '.join(it.front()[-5:] + [it.get()])
        hint_pos = len(hint)
        hint = '' if not hint else '\n\n  {}\n  {}^\n'.format(hint, ' ' * (hint_pos - len(it.get())))
        super().__init__(f'Invalid Symbol at Position {pos}: \'{sym}\' expected \'{expected}\' {hint}')


class Reset(BaseException):
    def __init__(self):
        pass


class SYM:
    SYM = None

    def __contains__(self, item):
        return item in self.SYM


class KW(SYM):
    SYM = END, FUN, IF, ELIF, ELSE, NOP, RET = \
        'end', 'fun', 'if', 'elif', 'else', 'nop', 'ret'


class OP(SYM):
    SYM = EQ, PLUS, MINUS, MUL, DIV, LT, GT, NOT, AND, OR, XOR, COM = \
        '=', '+', '-', '*', '/', '<', '>', '!', '&', '|', '^', '~'


class CT(SYM):
    SYM = COL, PAR_OP, PAR_CL, SQB_OP, SQB_CL = ',', '(', ')', '[', ']'


KWs = KW()
OPs = OP()
CTs = CT()


@debug
def parse_expression(it: Iterator, ast: Program, ctx: Context):
    tk = it.get()

    if is_identifier(tk):
        return Identifier(tk)
    elif is_number(tk):
        return Constant(tk)
    elif tk in CTs:
        return Identifier('')
        pass  # parse_control
    elif tk in OPs:
        return Identifier('')
        pass  # parse_operator
    else:
        raise InvalidToken(it, '...')


@debug
def parse_return_statement(it: Iterator, ast: Program, ctx: Context):
    tk = it.get()

    if tk != KW.RET:
        raise InvalidToken(it, KW.RET)

    if it.peek() in KWs:
        return ReturnStatement()

    it.next()

    return ReturnStatement(parse_expression(it, ast, ctx))


@debug
def parse_function_statement(it: Iterator, ast: Program, ctx: Context):
    tk = it.get()

    if tk != KW.FUN:
        raise InvalidToken(it, KW.FUN)

    tk = it.next()

    # Optional function name
    name = Identifier('')
    if is_identifier(tk):
        name = Identifier(tk)

    tk = it.next()

    if tk != CT.PAR_OP:
        raise InvalidToken(it, CT.PAR_OP)

    tk = it.next()

    # Optional function parameters
    params = []
    while tk != CT.PAR_CL:
        if is_identifier(tk):
            params.append(Identifier(tk))
        elif tk == CT.COL:
            pass
        else:
            raise InvalidToken(it, (CT.COL, 'id'))

        tk = it.next()

    if tk != CT.PAR_CL:
        raise InvalidToken(it, CT.PAR_CL)

    tk = it.next()

    # Optional function body
    body = []
    while tk != KW.END:
        body.append(parse_statement(it, ast, ctx))
        tk = it.next()

    if tk != KW.END:
        raise InvalidToken(it, KW.END)

    return FunctionStatement(name, params, body)


@debug
def parse_conditional_statement(it: Iterator, ast: Program, ctx: Context):
    tk = it.get()

    if tk != KW.IF:
        raise InvalidToken(it, KW.IF)

    it.next()

    # if condition
    if_condition = parse_expression(it, ast, ctx)

    tk = it.next()

    # if body
    if_body = []
    while tk not in (KW.ELIF, KW.ELSE, KW.END):
        if_body.append(parse_statement(it, ast, ctx))

        tk = it.next()

    # elif condition
    elif_condition = None
    elif_body = []
    if tk == KW.ELIF:

        it.next()

        elif_condition = parse_expression(it, ast, ctx)

        tk = it.next()

        # elif body
        while tk not in (KW.ELSE, KW.END):
            elif_body.append(parse_statement(it, ast, ctx))

            tk = it.next()

    # else condition
    else_body = []
    if tk == KW.ELSE:

        tk = it.next()

        # elif body
        while tk != KW.END:
            else_body.append(parse_statement(it, ast, ctx))

            tk = it.next()

    if tk != KW.END:
        raise InvalidToken(it, KW.END)

    return ConditionalStatement(if_condition, if_body, elif_condition, elif_body, else_body)


@debug
def parse_assignment_statement(it: Iterator, ast: Program, ctx: Context):
    tk = it.get()

    if not is_identifier(tk):
        raise InvalidToken(it, 'id')
    var = Identifier(tk)

    tk = it.next()

    if tk != OP.EQ:
        raise InvalidToken(it, OP.EQ)

    it.next()

    return AssignmentStatement(var, parse_expression(it, ast, ctx))


@debug
def parse_statement(it: Iterator, ast: Program, ctx: Context):
    tk = it.get()

    if tk == KW.NOP:
        return EmptyStatement()
    elif tk == KW.RET:
        return parse_return_statement(it, ast, ctx)
    elif tk == KW.FUN:
        return parse_function_statement(it, ast, ctx)
    elif tk == KW.IF:
        return parse_conditional_statement(it, ast, ctx)
    elif is_identifier(tk):
        return parse_assignment_statement(it, ast, ctx)
    else:
        raise InvalidToken(it, '...')


@debug
def parse(program: str) -> Program:
    ast = Program()
    ctx = Context()

    try:
        it = Iterator(program.split(' '))

        while it:
            st = parse_statement(it, ast, ctx)
            ast += st
            it.next()

    except StopIteration as e:
        print(traceback.format_exc())
    except InvalidToken as e:
        print(e)
    except Exception as e:
        print('EX: ', e)
        print(traceback.format_exc())

    return ast
