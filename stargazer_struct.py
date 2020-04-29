from abc import ABC

from api_static import APIStatic, StargazerStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY
from models import StargazerModel
from pprint import pprint


class StargazerStruct(GitHubQuery, ABC):
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

    def iterator(self):
        generator = self.generator()
        hasNextPage = True

        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                StargazerStatic.STARGAZERS
            ][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params["after"] = '"' + endCursor + '"'

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][
                StargazerStatic.STARGAZERS
            ][APIStatic.EDGES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY][
                        StargazerStatic.STARGAZERS
                    ][APIStatic.EDGES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStatic.DATA][APIStatic.REPOSITORY][
                                StargazerStatic.STARGAZERS
                            ][APIStatic.EDGES],
                        )
                    )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                StargazerStatic.STARGAZERS
            ][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

    def object_decoder(self, dic) -> StargazerModel:
        obj = StargazerModel(
            starred_at=dic[StargazerStatic.STARRED_AT],
            login=dic[APIStatic.NODE][APIStatic.LOGIN],
        )

        return obj


if __name__ == "__main__":
    stargazer = StargazerStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in stargazer.iterator():
        for stag in lst:
            print(stargazer.object_decoder(stag).login)
