from abc import ABC

from api_static import APIStatic, IssueStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY
from models import IssueCommentModel
from utils import Utils


class IssueCommentStruct(GitHubQuery, ABC, Utils):
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
                            authorAssociation
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
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [IssueStatic.ISSUE][IssueStatic.COMMENTS] \
                [APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\""

            yield response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [IssueStatic.ISSUE][IssueStatic.COMMENTS][APIStatic.NODES]

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [IssueStatic.ISSUE][IssueStatic.COMMENTS][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

    def object_decoder(self, dic) -> IssueCommentModel:
        obj = IssueCommentModel(
            created_at=dic[APIStatic.CREATED_AT],
            updated_at=dic[APIStatic.UPDATED_AT],
            body=dic[IssueStatic.BODY_TEXT],
            author_login=None if dic[IssueStatic.AUTHOR] is None else dic[IssueStatic.AUTHOR][APIStatic.LOGIN],
            author_association=dic[IssueStatic.AUTHOR_ASSOCIATION],
            positive_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], -1),
            ambiguous_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            is_minimized=dic[IssueStatic.IS_MINIMIZED],
            minimized_reason=dic[IssueStatic.MINIMIZED_REASON]
        )

        return obj


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
