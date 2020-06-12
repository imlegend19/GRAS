from abc import ABC


class BaseType(ABC):
    __slots__ = ("type_", "subtype")

    def __init__(self, subtype):
        self.type_ = type(self)
        self.subtype = subtype


class Class(BaseType):
    __name__ = "Class"


class Function(BaseType):
    __name__ = "Function"


class Method(BaseType):
    __name__ = "Method"


class GlobalVariable(BaseType):
    __name__ = "GlobalVariable"


class Arg(BaseType):
    __name__ = "Arg"


class Kwarg(BaseType):
    __name__ = "Kwarg"


class Base(BaseType):
    __name__ = "Base"


if __name__ == '__main__':
    import astpretty
    import ast

    s = """ 
async def run():
    conn = await asyncpg.connect(user='user', password='password',
                                 database='database', host='127.0.0.1')
    values = await conn.fetch('''SELECT * FROM mytable''')
    await conn.close()
    """

    print(astpretty.pprint(ast.parse(s).body[0]))
