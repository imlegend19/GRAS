from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import ForkModel
from gras.github.github import GithubInterface


class ForkStruct(GithubInterface, ForkModel):
    """
    The object models the query to fetch the list of directly forked repositories and
    generates an object using
    :class:`gras.github.entity.github_models.ForkModel` containing the fetched data.

    Please see GitHub's `repository documentation`_, `fork connection documentation`_ for more information.

    .. _repository documentation:
        https://developer.github.com/v4/object/repository/

    .. _fork connection documentation:
        https://developer.github.com/v4/object/repositoryconnection/

    :param name: name of the repository
    :type name: str

    :param owner: owner of the repository
    :type owner: str
    """

    FORK_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                forks(first: 100, orderBy: {{field: CREATED_AT, direction: ASC}}, after: {after}) {{
                    nodes {{
                        createdAt
                        nameWithOwner
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
        """Constructor Method"""
        super().__init__(
            query=self.FORK_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        """
        Iterator function for :class:`gras.github.structs.fork_struct.ForkStruct`. For more information see
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.FORKS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.FORKS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.FORKS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        Generates a :class:`gras.github.entity.github_models.ForkModel` object representing the fetched data.
        
        :return: A :class:`gras.github.entity.github_models.ForkModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for fork in lst:
                yield self.object_decoder(fork)
