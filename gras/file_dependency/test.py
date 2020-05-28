def x():
    # noinspection PyUnresolvedReferences
    class A:
        GLOBAL = 1

        def __init__(self, a, b=1):
            self.a = a
            self.b = b

            temp = None

        @deco
        def y(self, att):
            pass

    # noinspection PyUnresolvedReferences
    class B(A):
        def __init__(self, c):
            super().__init__(a=None)

            self.c = c

        @a.b.deco()
        def z(self):
            pass

    def local():
        b = B(c=2)
        b.z()

    return local()
