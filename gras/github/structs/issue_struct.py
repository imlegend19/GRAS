import logging

from gras.github.entity.api_static import APIStaticV4, IssueStatic
from gras.github.entity.github_models import IssueModel
from gras.github.github import GithubInterface
from gras.utils import time_period_chunks

logger = logging.getLogger("main")


class IssueDetailStruct(GithubInterface, IssueModel):
    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                issue(number: {number}) {{
                    createdAt
                    updatedAt
                    closedAt
                    title
                    bodyText
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
                    assignees(first: 10) {{
                        nodes {{
                            login
                        }}
                    }}
                    number
                    milestone {{
                        number
                    }}
                    state
                    labels(first: 30, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                        nodes {{
                            name
                        }}
                    }}
                    reactionGroups {{
                        content
                        users {{
                            totalCount
                        }}
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, name, owner, number):
        super().__init__(
            query=self.QUERY,
            query_params=dict(owner=owner, name=name, number=number)
        )
    
    def iterator(self):
        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.ISSUE]
    
    def process(self):
        return self.object_decoder(self.iterator())


class IssueStruct(GithubInterface, IssueModel):
    ISSUE_QUERY = """
        {{
            search(query: "repo:{owner}/{name} is:issue created:{start_date}..{end_date} sort:created-asc",
                   type: ISSUE, first: 100, after: {after}) {{
                issueCount
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
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, name, owner, start_date, end_date, chunk_size=25):
        super().__init__(
            query=self.ISSUE_QUERY,
            query_params=dict(owner=owner, name=name, after="null",
                              start_date=start_date.split('T')[0],
                              end_date=end_date.split('T')[0])
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
                    logger.debug(
                        f"Issue Count: {response[APIStaticV4.DATA][APIStaticV4.SEARCH]['issueCount']} btn {start}.."
                        f"{end}"
                    )
                except StopIteration:
                    break

                endCursor = response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.PAGE_INFO][
                    APIStaticV4.END_CURSOR]

                self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

                print(len(response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.NODES]))
                yield response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.NODES]

                hasNextPage = response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.PAGE_INFO][
                    APIStaticV4.HAS_NEXT_PAGE]
    
    def process(self):
        for lst in self.iterator():
            for issue in lst:
                yield self.object_decoder(issue)
