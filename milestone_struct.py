from pprint import pprint

from api_static import APIStatic, MilestoneStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY


class Milestone:
    def __init__(self, closed_at, created_at, creator_login, description, due_on, state, title, updated_at, url):
        super().__init__(closed_at, created_at, creator_login, description, due_on, state, title, updated_at, url)

        self.url = url
        self.updated_at = updated_at
        self.title = title
        self.state = state
        self.due_on = due_on
        self.description = description
        self.creator_login = creator_login
        self.created_at = created_at
        self.closed_at = closed_at


class MilestoneStruct(GitHubQuery):
    MILESTONE_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                milestones(first: 100, after: {after}) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        creator {{
                            login
                            url
                        }}
                        description
                        dueOn
                        url
                        title
                        closedAt
                        createdAt
                        state
                        updatedAt
                    }}
                }}
            }}
        }}
    """

    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token,
            query=MilestoneStruct.MILESTONE_QUERY,
            query_params=dict(name=name, owner=owner, after="null")
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        milestones = []

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [MilestoneStatic.MILESTONES][APIStatic.PAGE_INFO] \
                [APIStatic.END_CURSOR]

            self.query_params["after"] = "\"" + endCursor + "\""

            milestones.extend(response[APIStatic.DATA]
                              [APIStatic.REPOSITORY]
                              [MilestoneStatic.MILESTONES]
                              [APIStatic.NODES])

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [MilestoneStatic.MILESTONES][APIStatic.PAGE_INFO] \
                [APIStatic.HAS_NEXT_PAGE]

        return milestones


if __name__ == '__main__':
    ms = MilestoneStruct(github_token=AUTH_KEY,
                         name="sympy",
                         owner="sympy")

    ms_list = ms.iterator()

    pprint(len(ms_list))
