from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import BranchModel
from gras.github.github import GithubInterface


class BranchStruct(GithubInterface, BranchModel):
    BRANCH_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                refs(refPrefix: "refs/heads/", first: 100, orderBy: {{ field: TAG_COMMIT_DATE, direction: ASC }}, 
                     after: {after}) {{
                    nodes {{
                        name
                        target {{
                            oid
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
            query=self.BRANCH_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )
    
        self.name = name
        self.owner = owner
    
    def iterator(self):
        generator = self._generator()
        hasNextPage = True
        
        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break
            
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.REFS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
            
            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"
            
            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.REFS][APIStaticV4.NODES]
            
            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.REFS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for br in lst:
                yield self.object_decoder(br)
