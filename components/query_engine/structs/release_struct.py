from components.query_engine.entity.api_static import APIStatic, ReleaseStatic
from components.query_engine.entity.models import ReleaseModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class ReleaseStruct(GitHubQuery, ReleaseModel):
    RELEASE_QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                releases(first: 100, after:{after}) {{
                    nodes {{
                        author {{
                            login
                        }}
                        description
                        createdAt
                        isPrerelease
                        name
                        releaseAssets(first: 100) {{
                            nodes {{
                                downloadCount
                                name
                                size
                                updatedAt
                                contentType
                                createdAt
                            }}
                        }}
                        tagName
                        updatedAt
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
            github_token,
            query=ReleaseStruct.RELEASE_QUERY,
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

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][ReleaseStatic.RELEASES] \
                [APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = '\"' + endCursor + '\"'

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][ReleaseStatic.RELEASES][APIStatic.NODES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY] \
                        [ReleaseStatic.RELEASES][APIStatic.NODES]

                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStatic.DATA][APIStatic.REPOSITORY][ReleaseStatic.RELEASES][APIStatic.NODES],
                        )
                    )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][ReleaseStatic.RELEASES] \
                [APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]


if __name__ == "__main__":
    release = ReleaseStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in release.iterator():
        for rel in lst:
            print(release.object_decoder(rel).name)
