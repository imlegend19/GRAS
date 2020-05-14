from gras.github.entity.api_static import APIStaticV3, APIStaticV4, CommitStatic
from gras.github.entity.github_models import CodeChangeModel, CommitModelV3, CommitModelV4
from gras.github.github import GithubInterface


class CodeChangeStruct(GithubInterface, CodeChangeModel):
    def __init__(self, name, owner, commit_id):
        super().__init__(
            query=None,
            url=f"https://api.github.com/repos/{owner}/{name}/commits/{commit_id}",
            query_params=None
        )

    def iterator(self):
        generator = self._generator()
        return next(generator).json()[CommitStatic.FILES]

    def process(self):
        for cc in self.iterator():
            obj = self.object_decoder(cc)
            if obj:
                yield obj


class CommitStructV3(GithubInterface, CommitModelV3):
    def __init__(self, name, owner, start_date, end_date, merge):
        super().__init__(
            query=None,
            url=f"https://api.github.com/search/commits?q=repo:{owner}/{name}+merge:{merge}+"
                f"committer-date:{start_date}..{end_date}+sort:committer-date-asc&per_page=100&page=1",
            query_params=None,
            additional_headers=dict(Accept="application/vnd.github.cloak-preview+json")
        )
    
    def iterator(self):
        generator = self._generator()
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

    SINGLE_COMMIT_QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                object(oid: "{oid}") {{
                    ... on Commit {{
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
    """

    def __init__(self, name, owner, start_date=None, end_date=None, branch=None, after="null", oid=None):
        super().__init__(
            query=self.SINGLE_COMMIT_QUERY if oid else self.COMMIT_QUERY,
            query_params=dict(name=name, owner=owner, oid=oid) if oid else dict(name=name, owner=owner, after=after,
                                                                                start_date=start_date,
                                                                                end_date=end_date, branch=branch)
        )
    
        self.oid = oid

    def iterator(self):
        generator = self._generator()
        hasNextPage = True

        if not self.oid:
            while hasNextPage:
                try:
                    response = next(generator)
                except StopIteration:
                    break

                try:
                    endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][
                        CommitStatic.HISTORY][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
                except KeyError:
                    endCursor = None

                self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

                try:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][CommitStatic.HISTORY][
                        APIStaticV4.NODES]
                except KeyError:
                    yield None

                try:
                    hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][
                        CommitStatic.HISTORY][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]
                except KeyError:
                    hasNextPage = False
        else:
            response = next(generator)
            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT]

    def process(self):
        if not self.oid:
            for lst in self.iterator():
                for commit in lst:
                    yield self.object_decoder(commit)
        else:
            for dic in self.iterator():
                yield self.object_decoder(dic)
