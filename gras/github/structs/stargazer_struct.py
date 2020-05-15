from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import StargazerModel
from gras.github.github import GithubInterface


class StargazerStruct(GithubInterface, StargazerModel):
    STARGAZER_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                stargazers(first: 100, orderBy: {{ field: STARRED_AT, direction:ASC }}, after: {after}) {{
                    edges {{
                        starredAt
                        node {{
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
            query=self.STARGAZER_QUERY,
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
    
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
    
            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"
    
            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.STARGAZERS][
                APIStaticV4.EDGES]
    
            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for stag in lst:
                yield self.object_decoder(stag)