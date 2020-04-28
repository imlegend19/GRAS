from api_static import APIStatic, IssueStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY


class Issue:
    def __init__(self, created_at, title, body, author_login, assignees, number, milestone_number, labels, state,
                 reaction_count):
        self.reaction_count = reaction_count
        self.state = state
        self.labels = labels
        self.milestone_number = milestone_number
        self.number = number
        self.assignees = assignees
        self.author_login = author_login
        self.body = body
        self.title = title
        self.created_at = created_at


def object_decoder(dic) -> Issue:
    obj = Issue(
        created_at=dic[APIStatic.CREATED_AT],
        title=dic[IssueStatic.TITLE],
        body=dic[IssueStatic.BODY_TEXT],
        author_login=dic[IssueStatic.AUTHOR][APIStatic.LOGIN],
        assignees=list(node[APIStatic.LOGIN] for node in dic[IssueStatic.ASSIGNEES][APIStatic.NODES]),
        number=dic[IssueStatic.NUMBER],
        milestone_number=dic[IssueStatic.MILESTONE],
        labels=list(node[APIStatic.NAME] for node in dic[IssueStatic.LABELS][APIStatic.NODES]),
        reaction_count=dic[IssueStatic.REACTIONS][APIStatic.TOTAL_COUNT],
        state=dic[IssueStatic.STATE]
    )

    return obj


class IssueStruct(GitHubQuery):
    ISSUE_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                issues(first: 100, orderBy: {{field: CREATED_AT, direction: ASC}}, after: {after}) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        createdAt
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
                        labels(first: 25, orderBy: {{field: CREATED_AT, direction: ASC}}) {{
                            nodes {{
                               name 
                            }}
                        }}
                        state
                        reactions {{
                            totalCount
                        }}
                    }}
                }}
            }}
        }}
    """

    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=IssueStruct.ISSUE_QUERY,
            query_params=dict(name=name, owner=owner, after="null")
        )

    def iterator(self, limit=None):
        generator = self.generator()
        hasNextPage = True
        issues = []

        if limit is None:
            while hasNextPage:
                response = next(generator)

                endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                    [IssueStatic.ISSUES][APIStatic.PAGE_INFO] \
                    [APIStatic.END_CURSOR]

                self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\""

                issues.extend(response[APIStatic.DATA]
                              [APIStatic.REPOSITORY]
                              [IssueStatic.ISSUES]
                              [APIStatic.NODES])

                hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                    [IssueStatic.ISSUES][APIStatic.PAGE_INFO] \
                    [APIStatic.HAS_NEXT_PAGE]
        else:
            while hasNextPage and limit > 0:
                response = next(generator)

                endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                    [IssueStatic.ISSUES][APIStatic.PAGE_INFO] \
                    [APIStatic.END_CURSOR]

                self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\""

                issues.extend(response[APIStatic.DATA]
                              [APIStatic.REPOSITORY]
                              [IssueStatic.ISSUES]
                              [APIStatic.NODES])

                hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                    [IssueStatic.ISSUES][APIStatic.PAGE_INFO] \
                    [APIStatic.HAS_NEXT_PAGE]

                limit -= 100

        return issues


if __name__ == '__main__':
    issue = IssueStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy"
    )

    issue_list = issue.iterator(limit=100)
    for i in range(len(issue_list)):
        issue_list[i] = object_decoder(issue_list[i])

    for _ in issue_list:
        print(_.number, ":", _.title)
