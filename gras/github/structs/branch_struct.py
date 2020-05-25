from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import BranchModel
from gras.github.github import GithubInterface


class BranchStruct(GithubInterface, BranchModel):
    """
        The object models the query to fetch the branches of a repository and generates an object using
        :class:`gras.github.entity.github_models.BranchModel` containing the fetched data.

        Please see GitHub's `repository documentation`_, `ref connection documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _ref connection documentation:
            https://developer.github.com/v4/object/refconnection

        :param name: name of the repository
        :type name: str
        
        :param owner: owner of the repository
        :type owner: str
    """

    BRANCH_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                refs(refPrefix: "refs/heads/", first: 100, orderBy: {{ field: TAG_COMMIT_DATE, direction: ASC }}, 
                     after: {after}) {{
                    nodes {{
                        name
                        target {{
                            oid
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
        """Constructor Method"""
        super().__init__(
            query=self.BRANCH_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )
    
        self.name = name
        self.owner = owner

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.branch_struct.BranchStruct`. For more information see
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.REFS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.REFS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.REFS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        Generates a :class:`gras.github.entity.github_models.BranchModel` object representing the fetched data.
        
        :return: A :class:`gras.github.entity.github_models.BranchModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for br in lst:
                yield self.object_decoder(br)
