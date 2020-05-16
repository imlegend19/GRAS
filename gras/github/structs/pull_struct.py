from gras.github.entity.api_static import APIStaticV4, IssueStatic
from gras.github.entity.github_models import PullRequestModel, time_period_chunks
from gras.github.github import GithubInterface
from local_settings import AUTH_KEY


class PullRequestDetailStruct(GithubInterface, PullRequestModel):
    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                pullRequest(number: {number}) {{
                    title
                    author {{
                        ... on User {{
                            type: __typename
                            email
                            createdAt
                            login
                            name
                            location
                            updatedAt
                            followers {{
                                totalCount
                            }}
                        }}
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
                    baseRefName
                    baseRefOid
                    headRefName
                    headRefOid
                    commits(first: 100) {{
                        nodes {{
                            commit {{
                                oid
                            }}
                        }}
                    }}
                    labels(first: 50, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                        nodes {{
                            name
                        }}
                    }}
                    merged
                    mergedAt
                    mergedBy {{
                        ... on User {{
                            type: __typename
                            email
                            createdAt
                            login
                            name
                            location
                            updatedAt
                            followers {{
                                totalCount
                            }}
                        }}
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
                    reviewDecision
                }}
            }}
        }}
    """
    
    def __init__(self, name, owner, number):
        super().__init__(
            query=self.QUERY,
            query_params=dict(owner=owner, name=name, number=number),
            github_token=AUTH_KEY
        )
    
    def iterator(self):
        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.PULL_REQUEST]
    
    def process(self):
        return self.object_decoder(self.iterator())


class PullRequestStruct(GithubInterface, PullRequestModel):
    PR_QUERY = """
        {{
            search(query: "repo:{owner}/{name} is:pr created:{start_date}..{end_date} sort:created-asc", 
                   type: ISSUE, first: 100, after: {after}) {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    ... on PullRequest {{
                        title
                        author {{
                            ... on User {{
                                type: __typename
                                email
                                createdAt
                                login
                                name
                                location
                                updatedAt
                                followers {{
                                    totalCount
                                }}
                            }}
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
                        baseRefName
                        baseRefOid
                        headRefName
                        headRefOid
                        commits(first: 100) {{
                            nodes {{
                                commit {{
                                    oid
                                }}
                            }}
                        }}
                        labels(first: 50, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                            nodes {{
                                name
                            }}
                        }}
                        merged
                        mergedAt
                        mergedBy {{
                            ... on User {{
                                type: __typename
                                email
                                createdAt
                                login
                                name
                                location
                                updatedAt
                                followers {{
                                    totalCount
                                }}
                            }}
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
                        reviewDecision
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, name, owner, start_date, end_date, chunk_size=200):
        super().__init__(
            query=self.PR_QUERY,
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
            self.query_params["after"] = "null"
            
            generator = self._generator()
            hasNextPage = True
            
            while hasNextPage:
                try:
                    response = next(generator)
                except StopIteration:
                    break

                endCursor = response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.PAGE_INFO][
                    APIStaticV4.END_CURSOR]

                self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

                yield response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.NODES]

                hasNextPage = response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.PAGE_INFO][
                    APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for pr in lst:
                yield self.object_decoder(pr)
