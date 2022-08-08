import traceback

from iterator import Iterator
from shared import *
from dude_ast import *

dbg = True


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
#     def wrapper(it: Iterator, ctx: Context):
#         pos = it.pos()
#         try:
#             func(it, ctx)
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


class LT(SYM):
    SYM = QM, APS = \
        '"', '\''


class KW(SYM):
    SYM = END, FUN, IF, ELIF, ELSE, NOP, RET, FOR, IN, WHILE, DAT, TRUE, FALSE, NULL = \
        'end', 'fun', 'if', 'elif', 'else', 'nop', 'ret', 'for', 'in', 'while', 'dat', 'true', 'false', 'null'


class OP(SYM):
    SYM = EQ, PLUS, MINUS, MUL, DIV, LT, GT, NOT, AND, OR, XOR, COM = \
        '=', '+', '-', '*', '/', '<', '>', '!', '&', '|', '^', '~'


class CT(SYM):
    SYM = COL, COM, PAR_OP, PAR_CL, SQB_OP, SQB_CL = ':', ',', '(', ')', '[', ']'


LTs = LT()
KWs = KW()
OPs = OP()
CTs = CT()


@debug
def parse_expression(it: Iterator, ctx: Context):
    tk = it.get()

    if is_number(tk):
        expression = Number(tk)
    elif tk in [KW.TRUE, KW.FALSE]:
        expression = Boolean(tk)
    elif tk == KW.NULL:
        expression = Null()
    elif tk in LTs:
        expression = parse_literal(it, ctx)
    elif tk in CTs:
        # Nested expression
        if tk == CT.PAR_OP:
            it.next()
            expression = NestedExpression(parse_expression(it, ctx))

            if it.next() != CT.PAR_CL:
                raise InvalidToken(it, CT.PAR_CL)

        # Sequence expression
        elif tk == CT.SQB_OP:
            it.next()

            start = parse_expression(it, ctx)

            tk = it.next()

            # List
            if tk == CT.COM:
                tk = it.next()

                elements = [start]
                while tk != CT.SQB_CL:
                    if tk == CT.COM:
                        pass
                    else:
                        elements.append(parse_expression(it, ctx))
                    tk = it.next()

                return List(elements)

            # Slice
            elif tk == CT.COL:
                it.next()

                stop = parse_expression(it, ctx)

                tk = it.next()

                if tk == CT.SQB_CL:
                    return Sequence(start, stop, EmptyExpression())
                elif tk != CT.COL:
                    raise InvalidToken(it, CT.COL)

                it.next()

                step = parse_expression(it, ctx)

                expression = Sequence(start, stop, step)

                if it.next() != CT.SQB_CL:
                    raise InvalidToken(it, CT.SQB_CL)

                return expression

            else:
                raise InvalidToken(it, (CT.COM, CT.COL))

        else:
            raise InvalidToken(it, CT.PAR_CL)
    elif is_identifier(tk):
        expression = Identifier(tk)
    else:
        raise InvalidToken(it, '...')

    pk = it.peek()
    if pk in OPs:
        op = Operator(it.next())

        it.next()

        expression = Condition(expression, op, parse_expression(it, ctx))

    elif tk in KWs:
        return expression

    return expression


@debug
def parse_literal(it: Iterator, ctx: Context):
    tk = it.get()

    if tk not in LTs:
        raise InvalidToken(it, LTs)

    # String
    if tk == LT.QM:
        tk = it.next()

        string = ''
        while tk != LT.QM:
            string += tk
            tk = it.next()

        return String(string)

    # Character
    elif tk == LT.APS:
        char = it.next()

        if it.next() != LT.APS:
            raise InvalidToken(it, '\'')

        return Character(char)

    else:
        raise InvalidToken(it, '...')


@debug
def parse_return_statement(it: Iterator, ctx: Context):
    tk = it.get()

    if tk != KW.RET:
        raise InvalidToken(it, KW.RET)

    # No value is returned
    if it.peek() in KWs:
        return ReturnStatement()

    it.next()

    expression = parse_expression(it, ctx)

    return ReturnStatement(expression)


@debug
def parse_function_statement(it: Iterator, ctx: Context):
    tk = it.get()

    if tk != KW.FUN:
        raise InvalidToken(it, KW.FUN)

    tk = it.next()

    # Optional function name
    name = Identifier('')
    if is_identifier(tk):
        name = Identifier(tk)

    if it.next() != CT.PAR_OP:
        raise InvalidToken(it, CT.PAR_OP)

    tk = it.next()

    # Optional function parameters
    params = []
    while tk != CT.PAR_CL:
        if is_identifier(tk):
            params.append(Identifier(tk))
        elif tk == CT.COM:
            pass
        else:
            raise InvalidToken(it, (CT.COM, 'id'))

        tk = it.next()

    if tk != CT.PAR_CL:
        raise InvalidToken(it, CT.PAR_CL)

    tk = it.next()

    # Optional function body
    body = []
    while tk != KW.END:
        body.append(parse_statement(it, ctx))
        tk = it.next()

    if tk != KW.END:
        raise InvalidToken(it, KW.END)

    return FunctionStatement(name, params, body)


@debug
def parse_while_loop_statement(it: Iterator, ctx: Context):
    tk = it.get()
    
    if tk != KW.WHILE:
        raise InvalidToken(it, KW.WHILE)

    it.next()
    
    condition = parse_expression(it, ctx)

    tk = it.next()

    body = []
    while tk != KW.END:
        body.append(parse_statement(it, ctx))
        tk = it.next()
    
    return WhileLoopStatement(condition, body)


@debug
def parse_for_loop_statement(it: Iterator, ctx: Context):
    tk = it.get()

    if tk != KW.FOR:
        raise InvalidToken(it, KW.FOR)

    tk = it.next()

    if not is_identifier(tk):
        raise InvalidToken(it, 'identifier')

    index = Identifier(tk)

    if it.next() != KW.IN:
        raise InvalidToken(it, KW.IN)

    it.next()

    sequence = parse_expression(it, ctx)

    tk = it.next()

    body = []
    while tk != KW.END:
        body.append(parse_statement(it, ctx))
        tk = it.next()

    return ForLoopStatement(index, sequence, body)
    

@debug
def parse_structure_statement(it: Iterator, ctx: Context):
    tk = it.get()

    if tk != KW.DAT:
        raise InvalidToken(it, KW.DAT)

    name = Identifier(it.next())

    tk = it.next()

    members = []
    while tk != KW.END:
        if tk != CT.COM:
            members.append(Identifier(tk))
        tk = it.next()

    return StructureStatement(name, members)


@debug
def parse_conditional_statement(it: Iterator, ctx: Context):
    tk = it.get()

    if tk != KW.IF:
        raise InvalidToken(it, KW.IF)

    it.next()

    # if condition
    if_condition = parse_expression(it, ctx)

    tk = it.next()

    # if body
    if_body = []
    while tk not in (KW.ELIF, KW.ELSE, KW.END):
        if_body.append(parse_statement(it, ctx))

        tk = it.next()

    # elif condition
    elif_condition = None
    elif_body = []
    if tk == KW.ELIF:

        it.next()

        elif_condition = parse_expression(it, ctx)

        tk = it.next()

        # elif body
        while tk not in (KW.ELSE, KW.END):
            elif_body.append(parse_statement(it, ctx))

            tk = it.next()

    # else condition
    else_body = []
    if tk == KW.ELSE:

        tk = it.next()

        # elif body
        while tk != KW.END:
            else_body.append(parse_statement(it, ctx))

            tk = it.next()

    if tk != KW.END:
        raise InvalidToken(it, KW.END)

    return ConditionalStatement(if_condition, if_body, elif_condition, elif_body, else_body)


@debug
def parse_assignment_statement(it: Iterator, ctx: Context):
    tk = it.get()

    if not is_identifier(tk):
        raise InvalidToken(it, 'id')
    var = Identifier(tk)

    if it.next() != OP.EQ:
        raise InvalidToken(it, OP.EQ)

    it.next()

    return AssignmentStatement(var, parse_expression(it, ctx))


@debug
def parse_statement(it: Iterator, ctx: Context):
    tk = it.get()

    if tk == KW.NOP:
        return EmptyStatement()
    elif tk == KW.RET:
        return parse_return_statement(it, ctx)
    elif tk == KW.FUN:
        return parse_function_statement(it, ctx)
    elif tk == KW.IF:
        return parse_conditional_statement(it, ctx)
    elif tk == KW.WHILE:
        return parse_while_loop_statement(it, ctx)
    elif tk == KW.FOR:
        return parse_for_loop_statement(it, ctx)
    elif tk == KW.DAT:
        return parse_structure_statement(it, ctx)
    elif is_identifier(tk):
        return parse_assignment_statement(it, ctx)
    else:
        raise InvalidToken(it, '...')


@debug
def parse(program: str) -> Program:
    ast = Program()
    ctx = Context()

    try:
        it = Iterator(program.split(' '))

        while it:
            try:
                st = parse_statement(it, ctx)
                ast += st
            except StopIteration as e:
                print(e, traceback.format_exc())
            it.next()

    except StopIteration:
        pass
    except InvalidToken as e:
        print(e)
        print(traceback.format_exc())
    except Exception as e:
        print('EX: ', e)
        print(traceback.format_exc())

    return ast
