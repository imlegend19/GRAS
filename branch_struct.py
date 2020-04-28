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
        branches = []

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [BranchStatic.REFS][APIStatic.PAGE_INFO] \
                [APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = '\"' + endCursor + '\"'

            branches.extend(
                response[APIStatic.DATA][APIStatic.REPOSITORY][BranchStatic.REFS]
                [APIStatic.NODES]
            )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [BranchStatic.REFS][APIStatic.PAGE_INFO] \
                [APIStatic.HAS_NEXT_PAGE]

        return branches

    def object_decoder(self, dic) -> BranchModel:
        obj = BranchModel(
            name=dic[APIStatic.NAME],
            commit_id=dic[BranchStatic.TARGET][BranchStatic.OID]
        )

        return obj


if __name__ == "__main__":
    branch = BranchStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    branch_list = branch.iterator()
    for i in range(len(branch_list)):
        branch_list[i] = branch.object_decoder(branch_list[i])

    for _ in branch_list:
        print(_.name)
