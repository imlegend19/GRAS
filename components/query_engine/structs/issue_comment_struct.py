from components.query_engine.entity.api_static import APIStaticV4, IssueStatic
from components.query_engine.entity.models import IssueCommentModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class IssueCommentStruct(GitHubQuery, IssueCommentModel):
    ISSUE_COMMENT_QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                issue(number: {number}) {{
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
    
    def __init__(self, github_token, name, owner, number):
        super().__init__(
            github_token=github_token,
            query=IssueCommentStruct.ISSUE_COMMENT_QUERY,
            query_params=dict(owner=owner, name=name, number=number, after="null")
        )
    
    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        
        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break
            
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.ISSUE][IssueStatic.COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
            
            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"
            
            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.ISSUE][IssueStatic.COMMENTS][
                APIStaticV4.NODES]
            
            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.ISSUE][IssueStatic.COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]


if __name__ == '__main__':
    issue_comment = IssueCommentStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy",
        number=2681
    )
    
    for lst in issue_comment.iterator():
        for iss in lst:
            print(issue_comment.object_decoder(iss).positive_reaction_count,
                  issue_comment.object_decoder(iss).negative_reaction_count)
