from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import LanguageModel
from gras.github.github import GithubInterface


class LanguageStruct(GithubInterface, LanguageModel):
    """
        The object models the query to fetch the language composition of a repository and generates an object using
        :class:`gras.github.entity.github_models.LanguageModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `language connection documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _language connection documentation:
            https://developer.github.com/v4/object/languageconnection

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
    """

    LANGUAGE_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                languages(first: 100, orderBy: {{ field: SIZE, direction: ASC }}, after: {after}) {{
                    edges {{
                        size
                        node {{
                            name
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
            query=self.LANGUAGE_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )
    
    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.language_struct.LanguageStruct`. For more information see
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
                RepositoryStatic.LANGUAGES][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
            
            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"
            
            resp = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.LANGUAGES][APIStaticV4.EDGES]
            
            if resp is not None:
                if None not in resp:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                        RepositoryStatic.LANGUAGES][APIStaticV4.EDGES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                                RepositoryStatic.LANGUAGES][APIStaticV4.EDGES],
                        )
                    )

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.LANGUAGES][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        generates a :class:`gras.github.entity.github_models.LanguageModel` object representing the fetched data.
        :return: A :class:`gras.github.entity.github_models.LanguageModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for lang in lst:
                yield self.object_decoder(lang)
