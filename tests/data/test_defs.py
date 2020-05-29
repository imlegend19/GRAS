import functools


# noinspection PyUnresolvedReferences
async def af():
    return [i async for i in var]


# noinspection PyUnresolvedReferences
def f(a: annotation = 2, b=1, c=2, *d, e, f=3, **g) -> annotation:
    """doc for f()"""
    var = 1
    
    class A(base1, base2, metaclass=meta):
        global lol
        
        LOL = var + a + b + c + e + f;
        semi = 1
        
        def __init__(self, a: int):
            self.a = a + self.LOL
        
        def f1(self):
            return self.a
    
    class B(A):
        def __init__(self):
            super().__init__(1)
        
        def f1(self):
            return self.a + 1
    
    def g():
        b = B()
        return b.f1()
    
    return g()


class A(object):
    """Docstring for A"""
    
    def __init__(self, a):
        self.a = a
    
    def __str__(self):
        return "A"
    
    def f(self):
        return self.a


def decorator(function):
    """A general decorator function"""
    
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        return result
    
    return wrapper


class C(object):
    @decorator
    def method(self, x, y):
        print(x, y)


class B(object):
    """General decorator class"""
    
    def __init__(self, *args, **kwargs):
        """Decorator arguments"""
        pass
    
    def __call__(self, function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            return result
        
        return wrapper


def x():
    def u(_):
        pass
    
    return u(None)


# noinspection PyUnresolvedReferences
def synchronized(wrapped):
    """
    Function taken for testing from
    https://github.com/GrahamDumpleton/wrapt/blob/develop/src/wrapt/decorators.py#L423
    """
    if hasattr(wrapped, 'acquire') and hasattr(wrapped, 'release'):
        lock = wrapped
        
        @decorator
        def _synchronized(wrapped, instance, args, kwargs):
            with lock:
                return wrapped(*args, **kwargs)
        
        class _PartialDecorator(CallableObjectProxy):
            def __enter__(self):
                lock.acquire()
                return lock
            
            def __exit__(self, *args):
                lock.release()
        
        return _PartialDecorator(wrapped=_synchronized)
    
    # noinspection PyUnresolvedReferences
    def _synchronized_lock(context):
        lock = vars(context).get('_synchronized_lock', None)
        
        if lock is None:
            with synchronized._synchronized_meta_lock:
                lock = vars(context).get('_synchronized_lock', None)
                
                if lock is None:
                    lock = RLock()
                    setattr(context, '_synchronized_lock', lock)
        
        return lock
    
    def _synchronized_wrapper(wrapped, instance, args, kwargs):
        with _synchronized_lock(instance if instance is not None else wrapped):
            return wrapped(*args, **kwargs)
    
    class _FinalDecorator(FunctionWrapper):
        
        def __enter__(self):
            self._self_lock = _synchronized_lock(self.__wrapped__)
            self._self_lock.acquire()
            return self._self_lock
        
        def __exit__(self, *args):
            self._self_lock.release()
    
    return _FinalDecorator(wrapped=wrapped, wrapper=_synchronized_wrapper)
