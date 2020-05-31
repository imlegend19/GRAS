import logging

from gras.github.entity.api_static import APIStaticV4, IssueStatic
from gras.github.entity.github_models import IssueModel
from gras.github.github import GithubInterface
from gras.utils import time_period_chunks

logger = logging.getLogger("main")


class IssueDetailStruct(GithubInterface, IssueModel):
    """
        The object models the query to fetch details of an issue in a repository and
        generates an object using :class:`gras.github.entity.github_models.IssueModel` containing the
        fetched data.

        Please see GitHub's `repository documentation`_ , `issue documentation`_ , `user documentation`_ for more
        information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _issue documentation:
            https://developer.github.com/v4/object/issue/

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str

        :param number: issue number
        :type number: int
    """

    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                issue(number: {number}) {{
                    createdAt
                    updatedAt
                    closedAt
                    title
                    bodyText
                    author {{
                        ... on User {{
                            type: __typename
                            email
                            createdAt
                            login
                            name
                            location
                            updatedAt
                            followers {{
                                totalCount
                            }}
                        }}
                    }}
                    assignees(first: 10) {{
                        nodes {{
                            login
                        }}
                    }}
                    number
                    milestone {{
                        number
                    }}
                    state
                    labels(first: 30, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                        nodes {{
                            name
                        }}
                    }}
                    reactionGroups {{
                        content
                        users {{
                            totalCount
                        }}
                    }}
                }}
            }}
        }}
    """

    def __init__(self, name, owner, number):
        """Constructor Method"""
        super().__init__(
            query=self.QUERY,
            query_params=dict(owner=owner, name=name, number=number)
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.issue_struct.IssueDetailStruct`. For more
            information see :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.ISSUE]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.IssueModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.IssueModel` object
            :rtype: class
        """

        return self.object_decoder(self.iterator())


class IssueSearchStruct(GithubInterface, IssueModel):
    """
        The object models the query to fetch issues created in a specific time frame in a repository and
        generates an object using :class:`gras.github.entity.github_models.IssueModel` containing the
        fetched data.

        Please see GitHub's `repository documentation`_ , `issue documentation`_ , `user documentation`_ ,
         `node documentation`_ for more
        information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _issue documentation:
            https://developer.github.com/v4/object/issue/

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        .. _node documentation:
            https://developer.github.com/v4/interface/node/

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str

        :param start_date: fetch data after this date
        :type start_date: :class:`datetime.datetime` object

        :param end_date: fetch data till this date
        :type end_date: :class:`datetime.datetime` object

        :param chunk_size: required to divide search space into `chunk_size` days
        :type chunk_size: int
    """

    ISSUE_QUERY = """
        {{
            search(query: "repo:{owner}/{name} is:issue created:{start_date}..{end_date} sort:created-asc",
                   type: ISSUE, first: 100, after: {after}) {{
                issueCount
                pageInfo {{
                    endCursor
                    hasNextPage
                }}
                nodes {{
                    ... on Issue {{
                        createdAt
                        updatedAt
                        closedAt
                        title
                        bodyText
                        author {{
                            ... on User {{
                                type: __typename
                                email
                                createdAt
                                login
                                name
                                location
                                updatedAt
                                followers {{
                                    totalCount
                                }}
                            }}
                        }}
                        assignees(first: 10) {{
                            nodes {{
                                login
                            }}
                        }}
                        number
                        milestone {{
                            number
                        }}
                        labels(first: 30, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                            nodes {{
                                name
                            }}
                        }}
                        state
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
    """

    def __init__(self, name, owner, start_date, end_date, chunk_size=25):
        """Constructor Method"""
        super().__init__(
            query=self.ISSUE_QUERY,
            query_params=dict(owner=owner, name=name, after="null",
                              start_date=start_date.split('T')[0],
                              end_date=end_date.split('T')[0])
        )

        self.chunk_size = chunk_size

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.issue_struct.IssueSearchStruct`. For more
            information see :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        assert self.query_params["start_date"] is not None
        assert self.query_params["end_date"] is not None

        for start, end in time_period_chunks(self.query_params["start_date"],
                                             self.query_params["end_date"], chunk_size=self.chunk_size):
            self.query_params["start_date"] = start
            self.query_params["end_date"] = end
            self.query_params["after"] = "null"

            generator = self._generator()
            hasNextPage = True

            while hasNextPage:
                try:
                    response = next(generator)
                    logger.debug(
                        f"Issue Count: {response[APIStaticV4.DATA][APIStaticV4.SEARCH]['issueCount']} btn {start}.."
                        f"{end}"
                    )
                except StopIteration:
                    break

                endCursor = response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.PAGE_INFO][
                    APIStaticV4.END_CURSOR]

                self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

                yield response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.NODES]

                hasNextPage = response[APIStaticV4.DATA][APIStaticV4.SEARCH][APIStaticV4.PAGE_INFO][
                    APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.IssueModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.IssueModel` object
            :rtype: class
        """

        for lst in self.iterator():
            for issue in lst:
                yield self.object_decoder(issue)


class IssueStruct(GithubInterface, IssueModel):
    """
        The object models the query to fetch issues in a repository and generates an object using
        :class:`gras.github.entity.github_models.IssueModel` containing the
        fetched data.

        Please see GitHub's `repository documentation`_ , `issue documentation`_ , `user documentation`_ ,
        `node documentation`_ for more information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _issue documentation:
            https://developer.github.com/v4/object/issue/

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        .. _node documentation:
            https://developer.github.com/v4/interface/node/

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str

    """

    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                issues(first: 100, orderBy: {{ field: CREATED_AT, direction: ASC }}, after: {after}) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        createdAt
                        updatedAt
                        closedAt
                        title
                        bodyText
                        author {{
                            ... on User {{
                                type: __typename
                                email
                                createdAt
                                login
                                name
                                location
                                updatedAt
                                followers {{
                                    totalCount
                                }}
                            }}
                        }}
                        assignees(first: 10) {{
                            nodes {{
                                login
                            }}
                        }}
                        number
                        milestone {{
                            number
                        }}
                        labels(first: 30, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                            nodes {{
                                name
                            }}
                        }}
                        state
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
    """

    def __init__(self, name, owner):
        """Constructor Method"""
        super().__init__(
            query=self.QUERY,
            query_params=dict(owner=owner, name=name, after="null")
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.issue_struct.IssueStruct`. For more
            information see :class:`gras.github.github.githubInterface`.
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.ISSUES][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.ISSUES][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.ISSUES][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.IssueModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.IssueModel` object
            :rtype: class
        """

        for lst in self.iterator():
            for issue in lst:
                yield self.object_decoder(issue)
