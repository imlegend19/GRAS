from components.query_engine.entity.api_static import APIStaticV4
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class CustomQueryStruct(GitHubQuery):
    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                dependencyGraphManifests(first: 100, after: {after}) {{
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                    nodes {{
                        blobPath
                        dependenciesCount
                        exceedsMaxSize
                        filename
                        parseable
                    }}
                }}
            }}
        }}
    """

    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=CustomQueryStruct.QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
            additional_headers=dict(Accept="application/vnd.github.hawkgirl-preview+json")
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True

        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            print(response)

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY]["dependencyGraphManifests"][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else None

            resp = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY]["dependencyGraphManifests"] \
                [APIStaticV4.NODES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY] \
                        ["dependencyGraphManifests"][APIStaticV4.NODES]
            else:
                yield list(
                    (
                        filter(
                            None.__ne__,
                            response[APIStaticV4.DATA][APIStaticV4.REPOSITORY]
                            ["dependencyGraphManifests"][APIStaticV4.NODES],
                        )
                    )
                )

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY] \
                ["dependencyGraphManifests"][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]


if __name__ == '__main__':
    cq = CustomQueryStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in cq.iterator():
        for c in lst:
            print(c)
