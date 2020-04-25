from pprint import pprint
from string import Template

from gh_query import GitHubQuery
from local_settings import AUTH_KEY


class Milestone:
    def __init__(self, closed_at, created_at, creator_login, description, due_on, state, title, updated_at, url):
        self.closed_at = closed_at
# super().__init__(closed_at, created_at, creator_login, description, due_on, state, title, updated_at, url)




def object_decoder(param):
    pass


class MilestoneStruct(GitHubQuery):
    MILESTONE_QUERY_TEMPLATE = Template(
        """
            {
                repository(name: "$name", owner: "$owner") {
                    id
                    createdAt
                    milestones(orderBy: {field: NUMBER, direction: ASC}, first: 100) {
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                        nodes {
                            creator {
                                login
                                url
                            }
                            description
                            dueOn
                            url
                            title
                            closedAt
                            createdAt
                            number
                            state
                            updatedAt
                        }
                    }
                }
            }
        """
    )

    def __init__(self, github_token, name, owner):
        MILESTONE_QUERY = MilestoneStruct.MILESTONE_QUERY_TEMPLATE.substitute(name=name, owner=owner)
        super().__init__(github_token, query=MILESTONE_QUERY)


if __name__ == '__main__':
    ms = MilestoneStruct(github_token=AUTH_KEY,
                         name="sympy",
                         owner="sympy")

    ms_obj = dict(next(ms.generator()))

    pprint(ms_obj)
