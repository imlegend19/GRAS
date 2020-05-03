import datetime

import dateutil

from components.query_engine.entity.api_static import APIStaticV4, IssueStatic


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
            count += obj[IssueStatic.USERS][APIStaticV4.TOTAL_COUNT]
    
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
    d = dateutil.parser.parse(date)
    return d.isoformat()
