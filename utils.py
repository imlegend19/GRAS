from abc import abstractmethod

from api_static import IssueStatic, APIStatic


class Utils:
    @staticmethod
    @abstractmethod
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
                count += obj[IssueStatic.USERS][APIStatic.TOTAL_COUNT]

        return count
