import datetime
import sys
import time

from dateutil import parser

from components.query_engine.entity.api_static import APIStaticV4, IssueStatic, UserStatic

DEFAULT_START_DATE = datetime.datetime.strptime('1990-01-01', '%Y-%m-%d').isoformat()
DEFAULT_END_DATE = datetime.datetime.now().isoformat()


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
    :param decider: 1, 0 or -1 which denotes positive_reaction_count, ambiguous_reaction_count or
                    negative_reaction_count
    :return: corresponding reaction count
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


def time_period_chunks(start_date, end_date, chunk_size=100):
    dt_start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    dt_end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
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
    d = parser.parse(date)
    return d.isoformat()


def waiting_animation(n, msg):
    n = n % 3 + 1
    dots = n * '.' + (3 - n) * ' '
    sys.stdout.write(f'\r {msg} ' + dots)
    sys.stdout.flush()
    time.sleep(0.5)
    
    return n
