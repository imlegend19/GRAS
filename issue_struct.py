from abc import ABC

from api_static import APIStatic, IssueStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY
from models import IssueModel
from utils import Utils


class IssueStruct(GitHubQuery, ABC, Utils):
    ISSUE_QUERY = """
        {{
            search(query: "repo:{owner}/{name} is:issue created:{start_date}..{end_date} sort:created-asc", 
                   type: ISSUE, first: 100, after: {after}) {{
                pageInfo {{
                    endCursor
                    hasNextPage
                }}
                nodes {{
                    ... on Issue {{
                        createdAt
                        updatedAt
                        closedAt
                        title
                        bodyText
                        author {{
                            login
                        }}
                        assignees(first: 10) {{
                            nodes {{
                                login
                            }}
                        }}
                        number
                        milestone {{
                            number
                        }}
                        labels(first: 30, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                            nodes {{
                                name
                            }}
                        }}
                        state
                        reactionGroups {{
                            content
                            users {{
                                totalCount
                            }}
                        }}
                        number
                        repository {{
                            name
                        }}
                    }}
                }}
            }}
        }}
    """

    def __init__(self, github_token, name, owner, start_date, end_date):
        super().__init__(
            github_token=github_token,
            query=IssueStruct.ISSUE_QUERY,
            query_params=dict(owner=owner, name=name, after="null",
                              start_date="*" if start_date is None else start_date,
                              end_date="*" if end_date is None else end_date)
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.SEARCH] \
                [APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\""

            yield response[APIStatic.DATA] \
                [APIStatic.SEARCH] \
                [APIStatic.NODES]

            hasNextPage = response[APIStatic.DATA][APIStatic.SEARCH] \
                [APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

    def object_decoder(self, dic) -> IssueModel:
        obj = IssueModel(
            created_at=dic[APIStatic.CREATED_AT],
            updated_at=dic[APIStatic.UPDATED_AT],
            closed_at=dic[IssueStatic.CLOSED_AT],
            title=dic[IssueStatic.TITLE],
            body=dic[IssueStatic.BODY_TEXT],
            author_login=None if dic[IssueStatic.AUTHOR] is None else dic[IssueStatic.AUTHOR][APIStatic.LOGIN],
            assignees=list(node[APIStatic.LOGIN] for node in dic[IssueStatic.ASSIGNEES][APIStatic.NODES]),
            number=dic[IssueStatic.NUMBER],
            milestone_number=dic[IssueStatic.MILESTONE],
            labels=list(node[APIStatic.NAME] for node in dic[IssueStatic.LABELS][APIStatic.NODES]),
            positive_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 1),
            negative_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], -1),
            ambiguous_reaction_count=self.reaction_count(dic[IssueStatic.REACTION_GROUPS], 0),
            state=dic[IssueStatic.STATE]
        )

        return obj


if __name__ == '__main__':
    issue = IssueStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy",
        start_date="2009-01-01",
        end_date="2009-01-31"
    )

    for lst in issue.iterator():
        for iss in lst:
            print(issue.object_decoder(iss).positive_reaction_count, issue.object_decoder(iss).negative_reaction_count)
