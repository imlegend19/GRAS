import datetime
import inspect
import logging
import multiprocessing as mp
import sys
import time
import warnings
from collections import OrderedDict
from functools import partial, wraps
from timeit import default_timer as timer

from dateutil import parser

from gras.errors import BadGatewayError, GrasError
from gras.github.entity.api_static import APIStaticV4, IssueStatic, UserStatic

DEFAULT_START_DATE = datetime.datetime.strptime('1990-01-01', '%Y-%m-%d').isoformat()
DEFAULT_END_DATE = datetime.datetime.strptime('2100-01-01', '%Y-%m-%d').isoformat()
ELAPSED_TIME_ON_FUNCTIONS = OrderedDict()
STAGE_WISE_TIME = OrderedDict()

logger = logging.getLogger("main")

lock = mp.Lock()


class CircularQueue:
    def __init__(self, n):
        self.__nodes: list = [None for _ in range(n)]
        self.__n: int = n
        self.__pointer = 0
    
    def enqueue(self, node):
        if self.__nodes[self.__pointer] is None:
            self.__nodes[self.__pointer] = node
            self.__pointer = (self.__pointer + 1) % self.__n
        else:
            raise OverflowError

    def next(self):
        value = self.__nodes[self.__pointer]
        self.__pointer = (self.__pointer + 1) % self.__n
        return value


TOKEN_QUEUE: CircularQueue = CircularQueue(n=0)


def reaction_count(dic, decider) -> int:
    """
    Github supports various reactions. The function classifies them into either positive or negative reaction.
    The ambiguous 👀`eyes` and (the slightly less ambiguous) `rocket` have been considered as ambiguous reactions.

    | Positive  |  Negative |  Ambiguous |
    |-----------------------|------------|
    |    +1	    |    -1     |    eyes    |
    |   smile	| confused  |   rocket   |
    |   tada    |           |            |
    |   heart	|           |            |

    :param dic: the `reactionGroup` dict to parse
    :type dic: dict
    :param decider: 1, 0 or -1 which denotes positive_reaction_count, ambiguous_reaction_count or
                    negative_reaction_count
    :type decider: int
    
    :return: corresponding reaction count
    :rtype int
    """
    
    reaction_decider = {
        'THUMBS_UP'  : 1,
        'LAUGH'      : 1,
        'HOORAY'     : 1,
        'HEART'      : 1,
        'THUMBS_DOWN': -1,
        'CONFUSED'   : -1,
        'ROCKET'     : 0,
        'EYES'       : 0
    }
    
    count = 0
    
    for obj in dic:
        if reaction_decider[obj[IssueStatic.CONTENT]] == decider:
            count += obj[UserStatic.USERS][APIStaticV4.TOTAL_COUNT]
    
    return count


def time_period_chunks(start_date, end_date, chunk_size=400):
    dt_start = parser.parse(start_date)
    dt_end = parser.parse(end_date)
    
    assert dt_start < dt_end
    
    while True:
        end = dt_start + datetime.timedelta(days=chunk_size)
        
        if end > dt_end:
            yield dt_start.isoformat(), dt_end.isoformat()
            break
        else:
            yield dt_start.isoformat(), end.isoformat()
        
        dt_start = end - datetime.timedelta(days=1)


def to_iso_format(date):
    if not date:
        return None
    else:
        return parser.parse(date).isoformat()


def waiting_animation(n, msg):
    n = n % 3 + 1
    dots = n * '.' + (3 - n) * ' '
    sys.stdout.write(f'\r {msg} ' + dots)
    sys.stdout.flush()
    time.sleep(0.5)
    
    return n


def to_datetime(date):
    """
    Converts non-null string to date in ISO-8601 format.
    
    :param date: str
    :return: Returns a :class:`datetime.datetime` object
    """
    if not date:
        return None
    else:
        return parser.parse(date)


def get_value(str_):
    """
    Helper function to store formatted string. Will replace '\x00' characters in string with ''.
    
    :param str_: <str> to be formatted
    :return:
    """
    if not str_:
        return None
    else:
        return str_.strip().replace('\x00', '').replace("'", "\\'")


class DeprecatedWarning(UserWarning):
    pass


def deprecated(instructions):
    """
    Flags a method as deprecated.
    
    :param instructions: A human-friendly string of instructions, such
            as: 'Please migrate to function() ASAP.'
    """
    
    def decorator(func):
        """
        This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emitted
        when the function is used.
        """
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = 'Call to deprecated function {}. {}'.format(
                func.__name__,
                instructions)
            
            frame = inspect.currentframe().f_back
            
            warnings.warn_explicit(message,
                                   category=DeprecatedWarning,
                                   filename=inspect.getfile(frame.f_code),
                                   lineno=frame.f_lineno)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def locked(func):
    """
    A decorator to wrap the function with :class:`~multiprocessing.Lock`. This ensure that
    only 1 Process can execute the function at a time.
    
    :param func: Function
    
    Examples:
    
        >>>
        >>> @locked
        >>> def function_to_be_locked(*args, **kwargs):
        >>>     ...
        >>>
    """
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        lock.acquire()
        result = func(*args, **kwargs)
        lock.release()
        
        return result
    
    return wrapper


def timing(func=None, *, name=None, is_stage=None):
    """
    Decorator to measure the time taken by the function to execute
    
    :param func: Function
    :param name: Display Name of the function for which the time is being calculated
    :param is_stage: Identifier for mining stage
    
    Examples:
        
        >>>
        >>> @timing(name="foo")
        >>> def func():
        >>>     ...
        >>>
        >>> @timing
        >>> def func():
        >>>     ...
        >>>
    """
    
    if func is None:
        return partial(timing, name=name, is_stage=is_stage)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        end = timer()

        total_time = end - start

        logger.info(f"Time taken to execute `{name}`: {total_time} sec")

        if not is_stage:
            ELAPSED_TIME_ON_FUNCTIONS[name] = total_time
        else:
            STAGE_WISE_TIME[name] = total_time

        return result

    return wrapper


def exception_handler(func=None, *, retries=3, exceptions_to_catch=Exception, exception_to_raise=Exception, msg=None):
    """
    A decorator to handle exception and recall the function `retries` number of times.

    :param func: Function
    :type func: function
    :param retries: Number of times the function should be recalled
    :type retries: int
    :param exceptions_to_catch: The exception to catch, ex. `BadGatewayError`
    :type exceptions_to_catch: Exception or GrasError
    :param exception_to_raise: The exception to raise
    :type exception_to_raise: Exception or GrasError or type
    :param msg: Message for exception_to_raise
    :type msg: str
    
    Examples:
    
        >>>
        >>> @exception_handler(retries=3, exceptions_to_catch=BadGatewayError, exception_to_raise=GrasError)
        >>> def func():
        >>>     ...
        >>>
    """
    
    if func is None:
        return partial(exception_handler)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(retries):
            try:
                return func(*args, **kwargs)
            except exceptions_to_catch:
                pass
        
        if msg is None or not issubclass(exception_to_raise, GrasError):
            raise exception_to_raise
        else:
            raise exception_to_raise(msg=msg)
    
    return wrapper


def set_up_token_queue(tokens):
    """
    Sets a token :class:`~gras.utils.CircularQueue`
    
    :param tokens: list of tokens
    """
    global TOKEN_QUEUE
    
    TOKEN_QUEUE = CircularQueue(n=len(tokens))
    
    for token in tokens:
        TOKEN_QUEUE.enqueue(token)


def get_next_token():
    """
    Retrieves the next token in the queue
    
    :return: token <str>
    """
    assert TOKEN_QUEUE is not None
    return TOKEN_QUEUE.next()


ARROW_ANIMATOR = ['⬍', '⬈', '➞', '⬊', '⬍', '⬋', '⬅', '⬉']
ECLIPSE_ANIMATOR = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
DOTS_1_ANIMATOR = ['.', '..', '...']
DOTS_2_ANIMATOR = ['.', '..', '...', '..']
BIRDS_ANIMATOR = ['︷', '︵', '︹', '︺', '︶', '︸', '︶', '︺', '︹', '︵']
DASH_ANIMATOR = ['-', '—', '--', '——', '---', '———', '---', '——', '--', '—']
CYCLE_ANIMATOR = ['bo', 'do', 'ob', 'od', 'oq', 'op', 'qo', 'po']
ROD_ANIMATOR = ["/", "—", "\\", "|"]
LOADING_BAR_ANIMATOR = ["□□□□□□□□□□", "■□□□□□□□□□", "■■□□□□□□□□", "■■■□□□□□□□", "■■■■□□□□□□", "■■■■■□□□□□",
                        "■■■■■■□□□□", "■■■■■■■□□□", "■■■■■■■■□□", "■■■■■■■■■□", "■■■■■■■■■■"]
BALLOON_ANIMATOR = ['.', 'o', 'O', '@', '*']

ANIMATORS = {
    "arrow"  : ARROW_ANIMATOR,
    "eclipse": ECLIPSE_ANIMATOR,
    "dots_1" : DOTS_1_ANIMATOR,
    "dots_2" : DOTS_2_ANIMATOR,
    "birds"  : BIRDS_ANIMATOR,
    "dash"   : DASH_ANIMATOR,
    "cycle"  : CYCLE_ANIMATOR,
    "rod"    : ROD_ANIMATOR,
    "bar"    : LOADING_BAR_ANIMATOR,
    "balloon": BALLOON_ANIMATOR
}
