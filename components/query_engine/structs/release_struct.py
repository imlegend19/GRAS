from components.query_engine.entity.api_static import APIStaticV4, ReleaseStatic
from components.query_engine.entity.github_models import ReleaseModel
from components.query_engine.github import GithubInterface


class ReleaseStruct(GithubInterface, ReleaseModel):
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
            github_token=github_token,
            query=self.RELEASE_QUERY,
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][ReleaseStatic.RELEASES][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][ReleaseStatic.RELEASES][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][ReleaseStatic.RELEASES][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for release in lst:
                yield self.object_decoder(release)
