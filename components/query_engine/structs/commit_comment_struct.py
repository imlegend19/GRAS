from components.query_engine.entity.api_static import APIStaticV4, CommitStatic
from components.query_engine.entity.github_models import CommitCommentModel
from components.query_engine.github import GithubInterface
from local_settings import AUTH_KEY


class CommitCommentStruct(GithubInterface, CommitCommentModel):
    QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                commitComments(after: {after}, first: 100) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        author {{
                            login
                        }}
                        bodyText
                        commit {{
                            oid
                        }}
                        createdAt
                        path
                        position
                        reactionGroups {{
                            content
                            users {{
                                totalCount
                            }}
                        }}
                        updatedAt
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, github_token, name, owner, after="null"):
        super().__init__()
        
        self.github_token = github_token
        self.query = CommitCommentStruct.QUERY
        self.query_params = dict(name=name, owner=owner, after=after)
        
    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        
        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break
                
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.COMMIT_COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.COMMIT_COMMENTS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.COMMIT_COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]
            

if __name__ == '__main__':
    com = CommitCommentStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy"
    )
    
    for lst in com.iterator():
        for c in lst:
            try:
                print(com.object_decoder(c).created_at)
            except AttributeError:
                pass
