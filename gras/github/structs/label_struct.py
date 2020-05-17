from gras.github.entity.api_static import APIStaticV4, LabelStatic
from gras.github.entity.github_models import LabelModel
from gras.github.github import GithubInterface


class LabelStruct(GithubInterface, LabelModel):
    LABEL_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                labels(first: 100, orderBy: {{ field:  NAME, direction: ASC }}, after: {after}) {{
                    edges {{
                        node {{
                            color
                            name
                            createdAt
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
        """
        The object models the query to fetch the list of labels associated with a repository and generates an
        object using :class:`~gras.github.entity.github_models.LabelModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `label connection documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _label connection documentation:
            https://developer.github.com/v4/object/labelconnection

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str
        """
        super().__init__(
            query=self.LABEL_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.label_struct.LabelStruct`. For more information see
            :class:`~gras.github.github.GithubInterface`.
            
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.PAGE_INFO][
                APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.EDGES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.PAGE_INFO][
                APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        Generates a :class:`~gras.github.entity.github_models.LabelModel` object representing the fetched data.
        
        :return: A :class:`~gras.github.entity.github_models.LabelModel` object
        :rtype: object
        """

        for lst in self.iterator():
            for label in lst:
                yield self.object_decoder(label)
