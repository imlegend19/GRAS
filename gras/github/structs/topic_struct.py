from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import TopicModel
from gras.github.github import GithubInterface


class TopicStruct(GithubInterface, TopicModel):
    """
        The object models the query to fetch the list of applied repository-topic associations for a repository and
        generates an object using
        :class:`gras.github.entity.github_models.TopicModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `repository-topic connection documentation`_ for more
        information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _repository-topic connection documentation:
            https://developer.github.com/v4/object/repositorytopicconnection/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
    """

    TOPIC_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                repositoryTopics(first: 50, after: {after}) {{
                    nodes {{
                        url
                        topic {{
                            name
                            stargazers {{
                                totalCount
                            }}
                        }}
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
        super().__init__(
            query=self.TOPIC_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.topic_struct.TopicStruct`. For more information see
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.TOPICS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.TOPICS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.TOPICS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        generates a :class:`gras.github.entity.github_models.TopicModel` object representing the fetched data.
        :return: A :class:`gras.github.entity.github_models.TopicModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for topic in lst:
                yield self.object_decoder(topic)
