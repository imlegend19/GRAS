from components.query_engine.entity.api_static import APIStaticV4
from components.query_engine.entity.models import IssueModel
from components.query_engine.github import GithubInterface
from components.utils import time_period_chunks
from local_settings import AUTH_KEY


class IssueStruct(GithubInterface, IssueModel):
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
    
    def __init__(self, github_token, name, owner, start_date, end_date, chunk_size=200):
        super().__init__(
            github_token=github_token,
            query=IssueStruct.ISSUE_QUERY,
            query_params=dict(owner=owner, name=name, after="null",
                              start_date="*" if start_date is None else start_date,
                              end_date="*" if end_date is None else end_date)
        )
        
        self.chunk_size = chunk_size
    
    def _iterate(self):
        pass
    
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


if __name__ == '__main__':
    issue = IssueStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy",
        start_date="2009-01-01",
        end_date="2017-01-31"
    )
    
    it = 0
    for lst in issue.iterator():
        for iss in lst:
            dec = issue.object_decoder(iss)
            print(it, ":", dec.number, dec.created_at)
            it += 1
