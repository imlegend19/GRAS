from components.query_engine.entity.api_static import APIStaticV4
from components.query_engine.entity.github_models import WatcherModel
from components.query_engine.github import GithubInterface
from local_settings import AUTH_KEY


class WatcherStruct(GithubInterface, WatcherModel):
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
            
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.PAGE_INFO][
                APIStaticV4.END_CURSOR]
            
            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"
            
            resp = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.NODES]
            
            if resp is not None:
                if None not in resp:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.NODES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.NODES],
                        )
                    )
            
            hasNextPage = \
                response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.PAGE_INFO][
                    APIStaticV4.HAS_NEXT_PAGE]


if __name__ == "__main__":
    watcher = WatcherStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy"
    )
    
    for lst in watcher.iterator():
        for w in lst:
            print(watcher.object_decoder(w).login)
