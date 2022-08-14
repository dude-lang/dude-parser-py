class Context:
    def __init__(self):
        self.level = 0


class Statement:
    pass


class Operator:
    def __init__(self, operator: str):
        self.operator = operator


class Control:
    def __init__(self, control: str):
        self.control = control


class Expression(Statement):
    def __bool__(self):
        for child in dir(self):
            if child[0] != '_':
                if getattr(self, child):
                    return False
        return True


class EmptyExpression(Expression):
    pass


class NestedExpression(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression


class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name


class Null(Expression):
    def __init__(self):
        self.null = 'null'


class Number(Expression):
    def __init__(self, number: float):
        self.number = number


class Boolean(Expression):
    def __init__(self, boolean: bool):
        self.boolean = boolean


class String(Expression):
    def __init__(self, string: str):
        self.string = string


class Character(Expression):
    def __init__(self, char: str):
        self.char = char


class List(Expression):
    def __init__(self, elements: [Expression]):
        self.elements = elements


class Sequence(Expression):
    def __init__(self, start: Expression, stop: Expression, step: Expression):
        self.start = start
        self.stop = stop
        self.step = step


class Condition(Expression):
    def __init__(self, left: Expression, operator: Operator, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right


class EmptyStatement(Statement):
    def __init__(self):
        super().__init__()


class ReturnStatement(Statement):
    def __init__(self, expression: Expression = None):
        super().__init__()

        self.expression = expression


class AssignmentStatement(Statement):
    def __init__(self, var: Identifier, expression: Expression):
        super().__init__()
        self.var = var
        self.expression = expression


class StructureStatement(Statement):
    def __init__(self, name: Identifier, members: [Identifier]):
        super().__init__()
        self.name = name
        self.members = members


class FunctionStatement(Statement):
    def __init__(self, name: Identifier, arguments: [Identifier], body: [Statement]):
        super().__init__()
        self.name = name
        self.arguments = arguments
        self.body = body


class WhileLoopStatement(Statement):
    def __init__(self, condition: Condition, body: [Statement]):
        super().__init__()
        self.condition = condition
        self.body = body


class ForLoopStatement(Statement):
    def __init__(self, index: Identifier, sequence: Expression, body: [Statement]):
        super().__init__()
        self.index = index
        self.sequence = sequence
        self.body = body


class ConditionalStatement(Statement):
    def __init__(self, if_condition: Expression, if_body: [Statement],
                 elif_condition: Expression = None, elif_body: [Statement] = None,
                 else_body: [Statement] = None):
        super().__init__()
        self.if_condition = if_condition
        self.elif_condition = elif_condition
        self.if_body = if_body
        self.elif_body = elif_body
        self.else_body = else_body


class Program:
    def __init__(self, statements: [Statement] = None):
        self.statements = []

        if statements:
            self.statements = statements

    def __iadd__(self, other: Statement):
        self.statements.append(other)
        return self
