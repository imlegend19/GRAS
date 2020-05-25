from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import StargazerModel
from gras.github.github import GithubInterface


class StargazerStruct(GithubInterface, StargazerModel):
    """
        The object models the query to fetch the list of stargazers in a repository and generates an object using
        :class:`gras.github.entity.github_models.StargazerModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `stargazer connection documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _stargazer connection documentation:
            https://developer.github.com/v4/object/stargazerconnection/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
    """

    STARGAZER_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                stargazers(first: 100, orderBy: {{ field: STARRED_AT, direction:ASC }}, after: {after}) {{
                    edges {{
                        starredAt
                        node {{
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
            query=self.STARGAZER_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.stargazer_struct.StargazerStruct`. For more information
            see
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.STARGAZERS][
                APIStaticV4.EDGES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.STARGAZERS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        generates a :class:`gras.github.entity.github_models.StargazerModel` object representing the fetched data.
        :return: A :class:`gras.github.entity.github_models.StargazerModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for stag in lst:
                yield self.object_decoder(stag)
