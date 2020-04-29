from components.query_engine.entity.api_static import APIStatic, RepositoryStatic
from components.query_engine.entity.models import BranchModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class BranchStruct(GitHubQuery, BranchModel):
    BRANCH_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                refs(refPrefix: "refs/heads/", first: 100, orderBy: {{ field: TAG_COMMIT_DATE, direction: ASC }}, 
                     after: {after}) {{
                    nodes {{
                        name
                        target {{
                            oid
                        }}
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }}
            }}
        }}
    """

    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=BranchStruct.BRANCH_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True

        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [RepositoryStatic.REFS][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else None

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][RepositoryStatic.REFS] \
                [APIStatic.NODES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY] \
                        [RepositoryStatic.REFS][APIStatic.NODES]
            else:
                yield list(
                    (
                        filter(
                            None.__ne__,
                            response[APIStatic.DATA][APIStatic.REPOSITORY]
                            [RepositoryStatic.REFS][APIStatic.NODES],
                        )
                    )
                )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [RepositoryStatic.REFS][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]


if __name__ == "__main__":
    branch = BranchStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in branch.iterator():
        for br in lst:
            print(branch.object_decoder(br).name)
