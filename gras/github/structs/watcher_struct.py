from gras.github.entity.api_static import APIStaticV4
from gras.github.entity.github_models import WatcherModel
from gras.github.github import GithubInterface


class WatcherStruct(GithubInterface, WatcherModel):
    WATCHER_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                watchers(first: 100, after: {after}) {{
                    nodes {{
                        createdAt
                        email
                        login
                        name
                        location
                        updatedAt
                        followers {{
                            totalCount
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
    
    def __init__(self, name, owner):
        super().__init__(
            query=self.WATCHER_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )
    
    def iterator(self):
        generator = self._generator()
        hasNextPage = True
        
        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break
    
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.PAGE_INFO][
                APIStaticV4.END_CURSOR]
    
            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"
    
            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.NODES]
    
            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for watcher in lst:
                yield self.object_decoder(watcher)
