from gras.github.entity.api_static import APIStaticV4
from gras.github.github import GithubInterface


class CustomQueryStruct(GithubInterface):
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

    def __init__(self, name, owner):
        super().__init__(
            query=CustomQueryStruct.QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
            additional_headers=dict(Accept="application/vnd.github.hawkgirl-preview+json")
        )

    def iterator(self):
        generator = self._generator()
        hasNextPage = True

        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY]["dependencyGraphManifests"][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            resp = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY]["dependencyGraphManifests"][APIStaticV4.NODES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY]["dependencyGraphManifests"][
                        APIStaticV4.NODES]
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

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY]["dependencyGraphManifests"][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]


if __name__ == '__main__':
    cq = CustomQueryStruct(name="sympy", owner="sympy")

    for lst in cq.iterator():
        for c in lst:
            print(c)
