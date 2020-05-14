from gras.github.entity.api_static import (
    APIStaticV4, CommitStatic, LabelStatic, MilestoneStatic, ReleaseStatic, RepositoryStatic
)
from gras.github.github import GithubInterface
from gras.github.structs.branch_struct import BranchStruct


class RepoStatistics:
    def __init__(self, token, owner, name, start_date, end_date):
        self.token = token
        self.owner = owner
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
    
    def _total_contributors(self, anon):
        u = GithubInterface(
            url=f"https://api.github.com/repos/{self.owner}/{self.name}/contributors?per_page=100&anon={anon}"
        )
        
        total = 0
        generator = u._generator()
        hasNextPage = True
        
        while hasNextPage:
            response = next(generator)  # Response object (not json)
            total += len(response.json())
            
            try:
                next_url = response.links["next"]["url"]
                u.url = next_url
            except KeyError:
                break
        
        return total
    
    def _total_issues_and_pr(self):
        QUERY = """
            {{
                issue: search(query: "repo:{owner}/{name} is:issue created:{start_date}..{end_date}", type: ISSUE) {{
                    issueCount
                }}
                pr: search(query: "repo:{owner}/{name} is:pr created:{start_date}..{end_date}", type: ISSUE) {{
                    issueCount
                }}
            }}
        """
        
        gi = GithubInterface(
            query=QUERY,
            query_params=dict(name=self.name, owner=self.owner, start_date=self.start_date, end_date=self.end_date)
        )
        
        response = gi.iterator()[APIStaticV4.DATA]
        
        return {
            "total_issues"       : response["issue"]["issueCount"],
            "total_pull_requests": response["pr"]["issueCount"]
        }
    
    def _other_repo_stats(self):
        QUERY = """
            {{
                repository(name: "{name}", owner: "{owner}") {{
                    labels {{
                        totalCount
                    }}
                    forks {{
                        totalCount
                    }}
                    languages {{
                        totalCount
                    }}
                    releases {{
                        totalCount
                    }}
                    stargazers {{
                        totalCount
                    }}
                    watchers {{
                        totalCount
                    }}
                    tags: refs(refPrefix: "refs/tags/") {{
                        totalCount
                    }}
                    milestones {{
                        totalCount
                    }}
                    assignees: assignableUsers {{
                        totalCount
                    }}
                }}
            }}
        """
        
        gi = GithubInterface(
            query=QUERY,
            query_params=dict(name=self.name, owner=self.owner)
        )
        
        response = gi.iterator()[APIStaticV4.DATA][APIStaticV4.REPOSITORY]
        
        return {
            "total_labels"    : response[LabelStatic.LABELS][APIStaticV4.TOTAL_COUNT],
            "total_forks"     : response[RepositoryStatic.FORKS][APIStaticV4.TOTAL_COUNT],
            "total_languages" : response[RepositoryStatic.LANGUAGES][APIStaticV4.TOTAL_COUNT],
            "total_releases"  : response[ReleaseStatic.RELEASES][APIStaticV4.TOTAL_COUNT],
            "total_stargazers": response[RepositoryStatic.STARGAZERS][APIStaticV4.TOTAL_COUNT],
            "total_watchers"  : response[RepositoryStatic.WATCHERS][APIStaticV4.TOTAL_COUNT],
            "total_tags"      : response[RepositoryStatic.TAGS][APIStaticV4.TOTAL_COUNT],
            "total_milestones": response[MilestoneStatic.MILESTONES][APIStaticV4.TOTAL_COUNT],
            "total_assignees" : response[RepositoryStatic.ASSIGNEES][APIStaticV4.TOTAL_COUNT]
        }
    
    def repo_stats(self):
        total_contributors = self._total_contributors(anon=0)
        total_anon_contributors = self._total_contributors(anon=1) - total_contributors

        branch_list = []
        for br in BranchStruct(name=self.name, owner=self.owner).process():
            branch_list.append(br.name)

        branches = {}

        QUERY = """
            {{
                repository(name: "{name}", owner: "{owner}") {{
                    object(expression: "{branch}") {{
                        ... on Commit {{
                            history(since: "{start_date}", until: "{end_date}") {{
                                totalCount
                            }}
                        }}
                    }}
                    commitComments {{
                        totalCount
                    }}
                }}
            }}
        """
        
        for branch in branch_list:
            branches[branch] = {}
            
            gi = GithubInterface(
                query=QUERY,
                query_params=dict(name=self.name, owner=self.owner, start_date=self.start_date,
                                  end_date=self.end_date,
                                  branch=branch)
            )
            
            resp = gi.iterator()
            response = resp[APIStaticV4.DATA][APIStaticV4.REPOSITORY]
            branches[branch]["total_commits"] = response[CommitStatic.OBJECT][CommitStatic.HISTORY][
                APIStaticV4.TOTAL_COUNT]
            branches[branch]["total_commit_comments"] = response[CommitStatic.COMMIT_COMMENTS][APIStaticV4.TOTAL_COUNT]
        
        return {
            "total_contributors"     : total_contributors,
            "total_anon_contributors": total_anon_contributors,
            **self._total_issues_and_pr(),
            "branches"               : branches,
            **self._other_repo_stats()
        }
