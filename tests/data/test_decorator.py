# noinspection PyUnresolvedReferences
@deco1
@deco2()
@deco3(1, 'a', x={})
def f():
    """Decorated FunctionDef"""
    pass


# noinspection PyUnresolvedReferences
@deco1
@deco2()
@deco3(1)
async def f():
    """Decorated AsyncFunctionDef"""
    pass


# noinspection PyUnresolvedReferences
@deco1
@deco2()
@deco3(1)
class C:
    """Decorated ClassDef"""
    pass


# noinspection PyUnresolvedReferences
@deco(a for a in b)
def f():
    """Decorator with generator argument"""
    pass


# noinspection PyUnresolvedReferences,PyUnboundLocalVariable
@a.b.c
def f():
    """Decorator with attribute"""
    pass


# noinspection PyUnresolvedReferences
@a.b.deco(1)
def f():
    """Decorator with attribute and function call"""
    pass
