from pprint import pprint

from api_static import APIStatic, RepositoryStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY


class StargazerStruct(GitHubQuery):
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
            query_params=dict(name=name, owner=owner, after="null")
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        stargazers = []

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params["after"] = "\"" + endCursor + "\""

            stargazers.extend(response[APIStatic.DATA]
                              [APIStatic.REPOSITORY]
                              [RepositoryStatic.STARGAZERS]
                              [APIStatic.EDGES]
                              )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

        return stargazers


if __name__ == '__main__':
    stargazer = StargazerStruct(github_token=AUTH_KEY,
                                name="sympy",
                                owner="sympy")

    stargazer_list = stargazer.iterator()

    pprint(stargazer_list)
    pprint(len(stargazer_list))
