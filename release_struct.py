from abc import ABC

from api_static import APIStatic, ReleaseStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY
from models import ReleaseModel, AssetModel


class ReleaseStruct(GitHubQuery, ABC):
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

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                ReleaseStatic.RELEASES
            ][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params["after"] = '"' + endCursor + '"'

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][
                ReleaseStatic.RELEASES
            ][APIStatic.NODES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY][
                        ReleaseStatic.RELEASES
                    ][APIStatic.NODES]

                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStatic.DATA][APIStatic.REPOSITORY][
                                ReleaseStatic.RELEASES
                            ][APIStatic.NODES],
                        )
                    )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                ReleaseStatic.RELEASES
            ][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]

    def asset_decoder(self, dic) -> AssetModel:
        assetlist = dic[APIStatic.NODES]
        returnlist = []
        for p in assetlist:
            obj = AssetModel(
                download_count=p[ReleaseStatic.DOWNLOAD_COUNT],
                name=p[APIStatic.NAME],
                size=p[ReleaseStatic.SIZE],
                updated_at=p[APIStatic.UPDATED_AT],
                content_type=p[ReleaseStatic.CONTENT_TYPE],
                created_at=p[APIStatic.CREATED_AT],
            )
            returnlist.append(obj)
        return returnlist

    def object_decoder(self, dic) -> ReleaseModel:
        obj = ReleaseModel(
            author_login=None
            if dic[ReleaseStatic.AUTHOR] is None
            else dic[ReleaseStatic.AUTHOR][APIStatic.LOGIN],
            description=dic[APIStatic.DESCRIPTION],
            created_at=dic[APIStatic.CREATED_AT],
            isPrerelease=dic[ReleaseStatic.ISPRERELEASE],
            name=dic[APIStatic.NAME],
            release_assets=None
            if dic[ReleaseStatic.RELEASE_ASSETS] is None
            else self.asset_decoder(dic[ReleaseStatic.RELEASE_ASSETS]),
            tag_name=dic[ReleaseStatic.TAG_NAME],
            updated_at=dic[APIStatic.UPDATED_AT],
        )
        return obj


if __name__ == "__main__":
    release = ReleaseStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    for lst in release.iterator():
        for rel in lst:
            print(release.object_decoder(rel).name)
