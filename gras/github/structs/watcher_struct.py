from gras.github.entity.api_static import APIStaticV4
from gras.github.entity.github_models import WatcherModel
from gras.github.github import GithubInterface


class WatcherStruct(GithubInterface, WatcherModel):
    """
        The object models the query to fetch the list of watchers in a repository and generates an object using
        :class:`gras.github.entity.github_models.WatcherModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `watchers connection documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _watchers connection documentation:
            https://developer.github.com/v4/object/userconnection/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
    """

    WATCHER_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                watchers(first: 100, after: {after}) {{
                    nodes {{
                        createdAt
                        email
                        login
                        name
                        location
                        updatedAt
                        followers {{
                            totalCount
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

    def __init__(self, name, owner):
        """Constructor method
        """
        super().__init__(
            query=self.WATCHER_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
            )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.watcher_struct.WatcherStruct`. For more information see
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.PAGE_INFO][
                APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][APIStaticV4.WATCHERS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        generates a :class:`gras.github.entity.github_models.WatcherModel` object representing the fetched data.
        :return: A :class:`gras.github.entity.github_models.WatcherModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for watcher in lst:
                yield self.object_decoder(watcher)
