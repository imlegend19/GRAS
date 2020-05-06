from components.query_engine.entity.api_static import APIStaticV3, APIStaticV4, CommitStatic
from components.query_engine.entity.github_models import CodeChangeModel, CommitModelV3, CommitModelV4, to_iso_format
from components.query_engine.github import GithubInterface
from local_settings import AUTH_KEY


class CodeChangeStruct(GithubInterface, CodeChangeModel):
    def __init__(self, github_token, name, owner, commit_id):
        super().__init__(
            github_token=github_token,
            query=None,
            url=f"https://api.github.com/repos/{owner}/{name}/commits/{commit_id}",
            query_params=None
        )
    
    def iterator(self):
        generator = self.generator()
        return next(generator).json()[CommitStatic.FILES]


class CommitStructV3(GithubInterface, CommitModelV3):
    def __init__(self, github_token, name, owner, start_date, end_date, merge):
        super().__init__(
            github_token=github_token,
            query=None,
            url=f"https://api.github.com/search/commits?q=repo:{owner}/{name}+merge:{merge}+"
                f"committer-date:{start_date}..{end_date}+sort:committer-date-asc&per_page=100&page=1",
            query_params=None,
            additional_headers=dict(Accept="application/vnd.github.cloak-preview+json")
        )
    
    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        
        while hasNextPage:
            response = next(generator)  # Response object (not json)
            
            try:
                next_url = response.links["next"]["url"]
            except KeyError:
                break
            
            self.url = next_url
            
            response = response.json()
            yield response[APIStaticV3.ITEMS]
            
            hasNextPage = True if next_url is not None else False


class CommitStructV4(GithubInterface, CommitModelV4):
    COMMIT_QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                object(expression: "{branch}") {{
                    ... on Commit {{
                        history(since: "{start_date}", until: "{end_date}", first: 100, after: {after}) {{
                            totalCount
                            pageInfo {{
                                hasNextPage
                                endCursor
                            }}
                            nodes {{
                                oid
                                additions
                                deletions
                                author {{
                                    email
                                    name
                                    user {{
                                        login
                                    }}
                                }}
                                authoredDate
                                committer {{
                                    email
                                    name
                                    user {{
                                        login
                                    }}
                                }}
                                committedDate
                                message
                                status {{
                                    state
                                }}
                                changedFiles
                                parents {{
                                    totalCount
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, github_token, name, owner, start_date, end_date, branch, after="null"):
        super().__init__(
            github_token=github_token,
            query=CommitStructV4.COMMIT_QUERY,
            query_params=dict(name=name, owner=owner, start_date=start_date, end_date=end_date, after=after,
                              branch=branch)
        )
    
    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        
        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break
            
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][CommitStatic.HISTORY][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
            
            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"
            
            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][CommitStatic.HISTORY][
                APIStaticV4.NODES]
            
            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][CommitStatic.HISTORY][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]


# if __name__ == '__main__':
#     commit = CommitStructV3(
#         github_token=AUTH_KEY,
#         name="sympy",
#         owner="sympy",
#         merge="false",
#         start_date="2009-01-01",
#         end_date="2015-01-01"
#     )
#
#     it = 1
#     for lst in commit.iterator():
#         for c in lst:
#             com = commit.object_decoder(c, False)
#             print(it, ":", com.committed_date)
#             it += 1

if __name__ == '__main__':
    commit = CommitStructV4(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy",
        start_date=to_iso_format("2009-01-01"),
        end_date=to_iso_format("2015-01-01"),
        branch="master"
    )
    
    it = 1
    for lst in commit.iterator():
        for c in lst:
            com = commit.object_decoder(c)
            print(it, ":", com.committed_date)
            it += 1

# if __name__ == '__main__':
#     cc = CodeChangeStruct(
#         github_token=AUTH_KEY,
#         name="sympy",
#         owner="sympy",
#         commit_id="386f8ece1725063e8af7642d12cd882966b5f851"
#     )
#
#     lst = cc.iterator()
#
#     for c in lst:
#         print(cc.object_decoder(c).filename)
