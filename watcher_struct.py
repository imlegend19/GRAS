from abc import ABC
from pprint import pprint

from api_static import APIStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY
from models import WatcherModel


class WatcherStruct(GitHubQuery, ABC):
    WATCHER_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                watchers(first: 100, after: {after}) {{
                    nodes {{
                        login
                        createdAt
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
            query=WatcherStruct.WATCHER_QUERY,
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
                APIStatic.WATCHERS
            ][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params["after"] = '"' + endCursor + '"'

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][APIStatic.WATCHERS][
                APIStatic.NODES
            ]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY][
                        APIStatic.WATCHERS
                    ][APIStatic.NODES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStatic.DATA][APIStatic.REPOSITORY][
                                APIStatic.WATCHERS
                            ][APIStatic.NODES],
                        )
                    )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                APIStatic.WATCHERS
            ][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

    def object_decoder(self, dic) -> WatcherModel:
        obj = WatcherModel(
            login=dic[APIStatic.LOGIN], created_at=dic[APIStatic.CREATED_AT]
        )

        return obj


if __name__ == "__main__":
    watcher = WatcherStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in watcher.iterator():
        for w in lst:
            print(watcher.object_decoder(w).login)
