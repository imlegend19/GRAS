from abc import ABC


class BaseType(ABC):
    __slots__ = ("type_", "subtype")

    def __init__(self, subtype):
        self.type_ = type(self)
        self.subtype = subtype


class Class:
    __name__ = "Class"


class Function:
    __name__ = "Function"


class Method:
    __name__ = "Method"


class GlobalVariable:
    __name__ = "GlobalVariable"


class Arg:
    __name__ = "Arg"


class Kwarg:
    __name__ = "Kwarg"


class Base:
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
