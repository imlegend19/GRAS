from components.query_engine.entity.api_static import APIStatic, RepositoryStatic
from components.query_engine.entity.models import StargazerModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class StargazerStruct(GitHubQuery, StargazerModel):
    STARGAZER_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                stargazers(first: 100, orderBy: {{ field: STARRED_AT, direction:ASC }}, after: {after}) {{
                    edges {{
                        starredAt
                        node {{
                            login
                            id
                        }}
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }} 
            }}
        }}
    """

    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token,
            query=StargazerStruct.STARGAZER_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    @property
    def iterator(self):
        generator = self.generator()
        hasNextPage = True

        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                RepositoryStatic.STARGAZERS
            ][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params["after"] = '"' + endCursor + '"'

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][
                RepositoryStatic.STARGAZERS
            ][APIStatic.EDGES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY][
                        RepositoryStatic.STARGAZERS
                    ][APIStatic.EDGES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStatic.DATA][APIStatic.REPOSITORY][
                                RepositoryStatic.STARGAZERS
                            ][APIStatic.EDGES],
                        )
                    )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                RepositoryStatic.STARGAZERS
            ][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]


if __name__ == "__main__":
    stargazer = StargazerStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in stargazer.iterator:
        for stag in lst:
            print(stargazer.object_decoder(stag).login)
