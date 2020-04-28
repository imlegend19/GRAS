from abc import ABC
from pprint import pprint

from api_static import APIStatic, StargazerStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY

from models import StargazerModel


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
        stargazers = []

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                StargazerStatic.STARGAZERS
            ][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params["after"] = '"' + endCursor + '"'

            stargazers.extend(
                response[APIStatic.DATA][APIStatic.REPOSITORY][
                    StargazerStatic.STARGAZERS
                ][APIStatic.EDGES]
            )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                StargazerStatic.STARGAZERS
            ][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

        return stargazers

    def object_decoder(self, dic) -> StargazerModel:
        obj = StargazerModel(
            starred_at=dic[StargazerStatic.STARRED_AT],
            login=dic[APIStatic.NODE][APIStatic.LOGIN],
        )

        return obj


if __name__ == "__main__":

    stargazer = StargazerStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    stargazer_list = list(filter(None.__ne__, stargazer.iterator()))

    for i in range(len(stargazer_list)):
        stargazer_list[i] = stargazer.object_decoder(stargazer_list[i])

    for _ in stargazer_list:
        print(_.login)
