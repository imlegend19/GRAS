from components.query_engine.entity.api_static import APIStatic
from components.query_engine.entity.models import PullRequestModel, time_period_chunks
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class PullRequestStruct(GitHubQuery, PullRequestModel):
    PR_QUERY = """
        {{
            search(query: "repo:{owner}/{name} is:pr created:{start_date}..{end_date} sort:created-asc", 
                   type: ISSUE, first: 100) {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    ... on PullRequest {{
                        title
                        author {{
                          login
                        }}
                        assignees(first: 30) {{
                          nodes {{
                            login
                          }}
                        }}
                        bodyText
                        changedFiles
                        closed
                        closedAt
                        createdAt
                        updatedAt
                        additions
                        deletions
                        headRefName
                        headRefOid
                        labels(first: 50, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                            nodes {{
                                name
                            }}
                        }}
                        merged
                        mergedAt
                        mergedBy {{
                            login
                        }}
                        milestone {{
                            number
                        }}
                        number
                        reactionGroups {{
                            content
                            users {{
                                totalCount
                            }}
                        }}
                        state
                    }}
                }}
            }}
        }}
    """

    def __init__(self, github_token, name, owner, start_date, end_date, chunk_size=200):
        super().__init__(
            github_token=github_token,
            query=PullRequestStruct.PR_QUERY,
            query_params=dict(owner=owner, name=name, after="null",
                              start_date="*" if start_date is None else start_date,
                              end_date="*" if end_date is None else end_date)
        )

        self.chunk_size = chunk_size

    def iterator(self):
        assert self.query_params["start_date"] is not None
        assert self.query_params["end_date"] is not None

        for start, end in time_period_chunks(self.query_params["start_date"],
                                             self.query_params["end_date"], chunk_size=self.chunk_size):
            self.query_params["start_date"] = start
            self.query_params["end_date"] = end

            generator = self.generator()
            hasNextPage = True

            while hasNextPage:
                response = next(generator)

                endCursor = response[APIStatic.DATA][APIStatic.SEARCH] \
                    [APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

                self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

                yield response[APIStatic.DATA] \
                    [APIStatic.SEARCH] \
                    [APIStatic.NODES]

                hasNextPage = response[APIStatic.DATA][APIStatic.SEARCH] \
                    [APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]


if __name__ == '__main__':
    pr = PullRequestStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy",
        start_date="2009-01-01",
        end_date="2015-01-31"
    )

    for lst in pr.iterator():
        for p in lst:
            o = pr.object_decoder(p)
            print(o.number, o.created_at)
