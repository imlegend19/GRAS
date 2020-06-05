from gras.github.entity.api_static import APIStaticV4, ReleaseStatic
from gras.github.entity.github_models import ReleaseModel
from gras.github.github import GithubInterface


class ReleaseStruct(GithubInterface, ReleaseModel):
    """
        The object models the query to fetch the list of releases of a repository and generates an object using
        :class:`gras.github.entity.github_models.ReleaseModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `release connection documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _release connection documentation:
            https://developer.github.com/v4/object/releaseconnection/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
    """

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

    def __init__(self, name, owner):
        """Constructor method
        """

        super().__init__(
            query=self.RELEASE_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.release_struct.ReleaseStruct`. For more information see
            :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
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
        """
        generates a :class:`gras.github.entity.github_models.ReleaseModel` object representing the fetched data.
        :return: A :class:`gras.github.entity.github_models.ReleaseModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for release in lst:
                yield self.object_decoder(release)
