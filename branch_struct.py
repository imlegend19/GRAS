from abc import ABC

from api_static import APIStatic, BranchStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY
from models import BranchModel


class BranchStruct(GitHubQuery, ABC):
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
                                [BranchStatic.REFS][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = '\"' + endCursor + '\"'

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][BranchStatic.REFS] \
                           [APIStatic.NODES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY]
                                  [BranchStatic.REFS][APIStatic.NODES]
                else:
                    yield list(
                        (
                            filter(
                                None.__ne__,
                                response[APIStatic.DATA][APIStatic.REPOSITORY] \
                                [BranchStatic.REFS][APIStatic.NODES],
                            )
                        )
                    )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                                  [BranchStatic.REFS][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

    def object_decoder(self, dic) -> BranchModel:
        obj = BranchModel(
            name=dic[APIStatic.NAME],
            commit_id=dic[BranchStatic.TARGET][BranchStatic.OID],
        )

        return obj


if __name__ == "__main__":
    branch = BranchStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in branch.iterator():
        for br in lst:
            print(branch.object_decoder(br).name)
