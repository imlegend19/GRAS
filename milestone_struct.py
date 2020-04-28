from abc import ABC

from api_static import APIStatic, MilestoneStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY
from models import MilestoneModel


class MilestoneStruct(GitHubQuery, ABC):
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
                        }}
                        number
                        description
                        dueOn
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
            github_token=github_token,
            query=MilestoneStruct.MILESTONE_QUERY,
            query_params=dict(name=name, owner=owner, after="null")
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        milestones = []

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                MilestoneStatic.MILESTONES][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\""

            milestones.extend(response[APIStatic.DATA]
                              [APIStatic.REPOSITORY]
                              [MilestoneStatic.MILESTONES]
                              [APIStatic.NODES])

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                MilestoneStatic.MILESTONES][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

        return milestones

    def object_decoder(self, dic) -> MilestoneModel:
        obj = MilestoneModel(
            number=dic[MilestoneStatic.NUMBER],
            title=dic[MilestoneStatic.TITLE],
            state=dic[MilestoneStatic.STATE],
            due_on=dic[MilestoneStatic.DUE_ON],
            description=dic[APIStatic.DESCRIPTION],
            creator_login=dic[MilestoneStatic.CREATOR][APIStatic.LOGIN],
            created_at=dic[APIStatic.CREATED_AT],
            updated_at=dic[APIStatic.UPDATED_AT],
            closed_at=dic[MilestoneStatic.CLOSED_AT]
        )

        return obj


if __name__ == '__main__':
    ms = MilestoneStruct(github_token=AUTH_KEY,
                         name="sympy",
                         owner="sympy"
                         )

    ms_list = ms.iterator()
    for i in range(len(ms_list)):
        ms_list[i] = ms.object_decoder(ms_list[i])

    for _ in ms_list:
        print(_.number, ":", _.title)
