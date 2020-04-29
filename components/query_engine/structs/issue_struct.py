from components.query_engine.entity.api_static import APIStatic
from components.query_engine.entity.models import IssueModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class IssueStruct(GitHubQuery, IssueModel):
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

            self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else None

            yield response[APIStatic.DATA] \
                [APIStatic.SEARCH] \
                [APIStatic.NODES]

            hasNextPage = response[APIStatic.DATA][APIStatic.SEARCH] \
                [APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]


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
