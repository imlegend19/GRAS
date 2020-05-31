from gras.github.entity.api_static import APIStaticV4
from gras.github.entity.github_models import RepositoryModel
from gras.github.github import GithubInterface


class RepositoryStruct(GithubInterface, RepositoryModel):
    """
        The object models the query to fetch the basic data of a repository and generates an object using
        :class:`gras.github.entity.github_models.RepositoryModel` containing the fetched data.

        Please see GitHub's `repository documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
    """

    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                name
                createdAt
                updatedAt
                description
                diskUsage
                forkCount
                homepageUrl
                isArchived
                isFork
                url
                parent {{
                    url
                }}
                primaryLanguage {{
                    name
                }}
                stargazers {{
                    totalCount
                }}
                watchers {{
                    totalCount
                }}
            }}
        }}
    """

    def __init__(self, name, owner):
        """Constructor method
        """
        super().__init__(
            query=self.QUERY,
            query_params=dict(name=name, owner=owner)
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.repository_struct.RepositoryStruct`. For more
            information see
            :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.REPOSITORY]

    def process(self):
        return self.object_decoder(self.iterator())
