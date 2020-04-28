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
        watchers = []

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                APIStatic.WATCHERS
            ][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params["after"] = '"' + endCursor + '"'

            watchers.extend(
                response[APIStatic.DATA][APIStatic.REPOSITORY][APIStatic.WATCHERS][
                    APIStatic.NODES
                ]
            )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                APIStatic.WATCHERS
            ][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

        return watchers

    def object_decoder(self, dic) -> WatcherModel:
        obj = WatcherModel(
            login=dic[APIStatic.LOGIN], created_at=dic[APIStatic.CREATED_AT]
        )
        return obj


if __name__ == "__main__":
    watcher = WatcherStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    watcher_list = list(filter(None.__ne__, watcher.iterator()))
    # watcher_list = watcher.iterator()

    for i in range(len(watcher_list)):
        watcher_list[i] = watcher.object_decoder(watcher_list[i])

    for p in watcher_list:
        # print(p)
        print(p.login)

    pprint(len(watcher_list))
