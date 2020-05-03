from components.query_engine.entity.api_static import APIStaticV3, CommitStaticV3
from components.query_engine.entity.models import CommitModel, CodeChangeModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class CodeChangeStruct(GitHubQuery, CodeChangeModel):
    def __init__(self, github_token, name, owner, commit_id):
        super().__init__(
            github_token=github_token,
            query=None,
            url=f"https://api.github.com/repos/{owner}/{name}/commits/{commit_id}",
            query_params=None
        )

    def iterator(self):
        generator = self.generator()
        return next(generator).json()[CommitStaticV3.FILES]


class CommitStructV3(GitHubQuery, CommitModel):
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
    cc = CodeChangeStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy",
        commit_id="386f8ece1725063e8af7642d12cd882966b5f851"
    )

    lst = cc.iterator()

    for c in lst:
        print(cc.object_decoder(c).filename)
