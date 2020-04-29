from components.query_engine.entity.api_static import APIStatic, MilestoneStatic
from components.query_engine.entity.models import MilestoneModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class MilestoneStruct(GitHubQuery, MilestoneModel):
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
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True

        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                MilestoneStatic.MILESTONES
            ][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = '"' + endCursor + '"'

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][
                MilestoneStatic.MILESTONES
            ][APIStatic.NODES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY][
                        MilestoneStatic.MILESTONES
                    ][APIStatic.NODES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStatic.DATA][APIStatic.REPOSITORY][
                                MilestoneStatic.MILESTONES
                            ][APIStatic.NODES],
                        )
                    )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                MilestoneStatic.MILESTONES
            ][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]


if __name__ == "__main__":
    milestone = MilestoneStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in milestone.iterator():
        for ms in lst:
            print(milestone.object_decoder(ms).title)
