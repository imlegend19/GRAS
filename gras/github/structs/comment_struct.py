from gras.github.entity.api_static import APIStaticV4, IssueStatic
from gras.github.entity.github_models import CommentModel
from gras.github.github import GithubInterface


class CommentStruct(GithubInterface, CommentModel):
    COMMENT_QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                {type_filter}(number: {number}) {{
                    comments(first: 100, after: {after}) {{
                        pageInfo {{
                            hasNextPage
                            endCursor
                        }}
                        nodes {{
                            author {{
                                login
                            }}
                            bodyText
                            createdAt
                            isMinimized
                            minimizedReason
                            updatedAt
                            reactionGroups {{
                                content
                                users {{
                                    totalCount
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, name, owner, number, type_filter):
        super().__init__(
            query=self.COMMENT_QUERY,
            query_params=dict(owner=owner, name=name, number=number, type_filter=type_filter, after="null")
        )
    
        self.type_filter = type_filter
    
    def iterator(self):
        generator = self._generator()
        hasNextPage = True
        
        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][IssueStatic.COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][IssueStatic.COMMENTS][
                APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][IssueStatic.COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for comment in lst:
                yield self.object_decoder(comment)
