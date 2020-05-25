from gras.github.entity.api_static import APIStaticV4, CommitStatic
from gras.github.entity.github_models import CommitCommentModel
from gras.github.github import GithubInterface


class CommitCommentStruct(GithubInterface, CommitCommentModel):
    """
        The object models the query to fetch a list of commit comments associated with a repository and generates an
        object using :class:`gras.github.entity.github_models.CommitCommentModel` containing the
        fetched data.

        Please see GitHub's `repository documentation`_ , `commit-comment connection documentation`_ for more
        information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _commit-comment connection documentation:
            https://developer.github.com/v4/object/commitcommentconnection/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
    """

    QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                commitComments(after: {after}, first: 100) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        author {{
                            login
                        }}
                        bodyText
                        commit {{
                            oid
                        }}
                        createdAt
                        path
                        position
                        reactionGroups {{
                            content
                            users {{
                                totalCount
                            }}
                        }}
                        updatedAt
                    }}
                }}
            }}
        }}
    """

    def __init__(self, name, owner):
        """Constructor Method"""
        super().__init__()

        self.query = CommitCommentStruct.QUERY
        self.query_params = dict(name=name, owner=owner, after="null")

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.commit_comment_struct.CommitCommentStruct`. For more
            information see
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.COMMIT_COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.COMMIT_COMMENTS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.COMMIT_COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        generates a :class:`gras.github.entity.github_models.CommitCommentModel` object representing the fetched data.
        :return: A :class:`gras.github.entity.github_models.CommitCommentModel` object
        :rtype: class
        """

        for cc in self.iterator():
            for node in cc:
                obj = self.object_decoder(node)
                if obj:
                    yield obj
