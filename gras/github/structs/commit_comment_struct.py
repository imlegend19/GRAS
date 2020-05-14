from gras.github.entity.api_static import APIStaticV4, CommitStatic
from gras.github.entity.github_models import CommitCommentModel
from gras.github.github import GithubInterface


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

    def __init__(self, name, owner):
        super().__init__()
    
        self.query = CommitCommentStruct.QUERY
        self.query_params = dict(name=name, owner=owner, after="null")

    def iterator(self):
        generator = self._generator()
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

    def process(self):
        for cc in self.iterator():
            for node in cc:
                obj = self.object_decoder(node)
                if obj:
                    yield obj
