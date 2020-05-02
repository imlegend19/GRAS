from components.query_engine.entity.api_static import APIStaticV4, RepositoryStatic
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = '"' + endCursor + '"'

            resp = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStaticV4.EDGES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.STARGAZERS][APIStaticV4.EDGES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.STARGAZERS][
                                APIStaticV4.EDGES],
                        )
                    )

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]


if __name__ == "__main__":
    stargazer = StargazerStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in stargazer.iterator:
        for stag in lst:
            print(stargazer.object_decoder(stag).login)