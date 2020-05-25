from gras.github.entity.api_static import APIStaticV4, IssueStatic
from gras.github.entity.github_models import CommentModel
from gras.github.github import GithubInterface


class CommentStruct(GithubInterface, CommentModel):
    """
        The object models the query to fetch the comments of a `type_filter`(for example: "pullRequest") of a
        repository and generates an object using :class:`gras.github.entity.github_models.CommentModel` containing the
        fetched data.

        Please see GitHub's `repository documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
        :param number: `type_filter` number
        :type number: int
        :param type_filter: type of comment(pullRequest/issue)
        :type type_filter: str
    """

    COMMENT_QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                {type_filter}(number: {number}) {{
                    comments(first: 100, after: {after}) {{
                        pageInfo {{
                            hasNextPage
                            endCursor
                        }}
                        nodes {{
                            author {{
                                login
                            }}
                            bodyText
                            createdAt
                            isMinimized
                            minimizedReason
                            updatedAt
                            reactionGroups {{
                                content
                                users {{
                                    totalCount
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, name, owner, number, type_filter):
        """Constructor Method"""
        super().__init__(
            query=self.COMMENT_QUERY,
            query_params=dict(owner=owner, name=name, number=number, type_filter=type_filter, after="null")
        )

        self.type_filter = type_filter
    
    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.comment_struct.CommentStruct`. For more information see
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][IssueStatic.COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][IssueStatic.COMMENTS][
                APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][self.type_filter][IssueStatic.COMMENTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
        generates a :class:`gras.github.entity.github_models.CommentModel` object representing the fetched data.
        :return: A :class:`gras.github.entity.github_models.CommentModel` object
        :rtype: class
        """

        for lst in self.iterator():
            for comment in lst:
                yield self.object_decoder(comment)
