from components.query_engine.entity.api_static import APIStaticV4, RepositoryStatic
from components.query_engine.entity.github_models import BranchModel
from components.query_engine.github import GithubInterface
from local_settings import AUTH_KEY


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
    
    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=BranchStruct.BRANCH_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )
        
        self.name = name
        self.owner = owner
    
    def iterator(self):
        generator = self.generator()
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
    
    def get_branches_list(self):
        branches = []
        for lst in self.iterator():
            for br in lst:
                branches.append(self.object_decoder(br))
        
        return branches
