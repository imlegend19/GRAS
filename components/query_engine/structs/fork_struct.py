from components.query_engine.entity.api_static import APIStaticV4, ForkStatic
from components.query_engine.entity.models import ForkModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class ForkStruct(GitHubQuery, ForkModel):
    FORK_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                forks(first: 100, orderBy: {{field: CREATED_AT, direction: ASC}}, after: {after}) {{
                    nodes {{
                        owner {{
                            login
                        }}
                    createdAt
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
        }}
    """

    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=ForkStruct.FORK_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    @property
    def iterator(self):
        generator = self.generator()
        hasNextPage = True

        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                ForkStatic.FORKS
            ][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = (
                '"' + endCursor + '"' if endCursor is not None else "null"
            )

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][ForkStatic.FORKS][
                APIStaticV4.NODES
            ]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                ForkStatic.FORKS
            ][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]


if __name__ == "__main__":
    fork = ForkStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in fork.iterator:
        for f in lst:
            print(fork.object_decoder(f).created_at)
