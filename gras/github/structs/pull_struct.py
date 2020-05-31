from gras.github.entity.api_static import APIStaticV4, IssueStatic
from gras.github.entity.github_models import PullRequestCommitModel, PullRequestModel, time_period_chunks
from gras.github.github import GithubInterface


class PullRequestDetailStruct(GithubInterface, PullRequestModel):
    """
        The object models the query to fetch details of a pull request in a repository and generates an object using
        :class:`gras.github.entity.github_models.PullRequestModel` containing the fetched data.

        Please see GitHub's `repository documentation`_ , `pull-request documentation`_ , `user documentation`_ for more
        information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _pull-request documentation:
            https://developer.github.com/v4/object/pullrequest/

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str

        :param number: pull request number
        :type number: int
    """

    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                pullRequest(number: {number}) {{
                    title
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
                    assignees(first: 30) {{
                        nodes {{
                            login
                        }}
                    }}
                    bodyText
                    changedFiles
                    closed
                    closedAt
                    createdAt
                    updatedAt
                    additions
                    deletions
                    baseRefName
                    baseRefOid
                    headRefName
                    headRefOid
                    commits(first: 100) {{
                        nodes {{
                            commit {{
                                oid
                            }}
                        }}
                    }}
                    labels(first: 50, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                        nodes {{
                            name
                        }}
                    }}
                    merged
                    mergedAt
                    mergedBy {{
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
                    milestone {{
                        number
                    }}
                    number
                    reactionGroups {{
                        content
                        users {{
                           totalCount
                        }}
                    }}
                    state
                    reviewDecision
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
            Iterator function for :class:`gras.github.structs.pull_struct.PullRequestDetailStruct`. For more
            information see :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.PULL_REQUEST]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.PullRequestModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.PullRequestModel` object
            :rtype: class
        """

        return self.object_decoder(self.iterator())


class PullRequestSearchStruct(GithubInterface, PullRequestModel):
    """
        The object models the query to fetch pull requests in a repository and generates an object using
        :class:`gras.github.entity.github_models.PullRequestModel` containing the fetched data.

        Please see GitHub's `repository documentation`_ , `pull-request documentation`_ , `user documentation`_ for more
        information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _pull-request documentation:
            https://developer.github.com/v4/object/pullrequest/

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str

        :param start_date: fetch data after this date
        :type start_date: :class:`datetime.datetime` object

        :param end_date: fetch data till this date
        :type end_date: :class:`datetime.datetime` object
        
        :param limit: Number of results to be fetched in 1 request, default=100
        :type limit: int

        :param chunk_size: required to divide search space into `chunk_size` days
        :type chunk_size: int
    """

    PR_QUERY = """
        {{
            search(query: "repo:{owner}/{name} is:pr created:{start_date}..{end_date} sort:created-asc", 
                   type: ISSUE, first: {limit}, after: {after}) {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    ... on PullRequest {{
                        title
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
                        assignees(first: 30) {{
                            nodes {{
                                login
                            }}
                        }}
                        bodyText
                        changedFiles
                        closed
                        closedAt
                        createdAt
                        updatedAt
                        additions
                        deletions
                        baseRefName
                        baseRefOid
                        headRefName
                        headRefOid
                        labels(first: 50, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                            nodes {{
                                name
                            }}
                        }}
                        merged
                        mergedAt
                        mergedBy {{
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
                        milestone {{
                            number
                        }}
                        number
                        reactionGroups {{
                            content
                            users {{
                                totalCount
                            }}
                        }}
                        state
                        reviewDecision
                    }}
                }}
            }}
        }}
    """

    def __init__(self, name, owner, start_date, end_date, limit=100, chunk_size=200):
        """Constructor Method"""
        super().__init__(
            query=self.PR_QUERY,
            query_params=dict(owner=owner, name=name, after="null", limit=limit,
                              start_date="*" if start_date is None else start_date,
                              end_date="*" if end_date is None else end_date)
        )

        self.chunk_size = chunk_size

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.pull_struct.PullRequestSearchStruct`. For more
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
            generates a :class:`gras.github.entity.github_models.PullRequestModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.PullRequestModel` object
            :rtype: class
        """

        for lst in self.iterator():
            for pr in lst:
                yield self.object_decoder(pr)


class PullRequestStruct(GithubInterface, PullRequestModel):
    """
        The object models the query to fetch pull requests in a repository and generates an object using
        :class:`gras.github.entity.github_models.PullRequestModel` containing the fetched data.

        Please see GitHub's `repository documentation`_ , `pull-request documentation`_ , `user documentation`_ for more
        information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _pull-request documentation:
            https://developer.github.com/v4/object/pullrequest/

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        :param name: name of the repository
        :type name: str

        :param owner: owner of the repository
        :type owner: str
        
        :param limit: Number of results to be fetched in 1 request, default=100
        :type limit: int
    """

    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                pullRequests(first: {limit}, orderBy: {{ field: CREATED_AT, direction: ASC }}, after: {after}) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        title
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
                        assignees(first: 30) {{
                            nodes {{
                                login
                            }}
                        }}
                        bodyText
                        changedFiles
                        closed
                        closedAt
                        createdAt
                        updatedAt
                        additions
                        deletions
                        baseRefName
                        baseRefOid
                        headRefName
                        headRefOid
                        labels(first: 50, orderBy: {{ field: CREATED_AT, direction: ASC }}) {{
                            nodes {{
                                name
                            }}
                        }}
                        merged
                        mergedAt
                        mergedBy {{
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
                        milestone {{
                            number
                        }}
                        number
                        reactionGroups {{
                            content
                            users {{
                                totalCount
                            }}
                        }}
                        state
                        reviewDecision
                    }}
                }}
            }}
        }}
    """

    def __init__(self, name, owner, limit=100):
        """Constructor Method"""
        super().__init__(
            query=self.QUERY,
            query_params=dict(owner=owner, name=name, limit=limit, after="null")
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.pull_struct.PullRequestStruct`. For more
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.PULL_REQUESTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.PULL_REQUESTS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.PULL_REQUESTS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.PullRequestModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.PullRequestModel` object
            :rtype: class
        """

        for lst in self.iterator():
            for issue in lst:
                yield self.object_decoder(issue)


class PullRequestCommitsStruct(GithubInterface, PullRequestCommitModel):
    QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                pullRequest(number: {number}) {{
                    number
                    commits(first: 100, after: {after}) {{
                        pageInfo {{
                            hasNextPage
                            endCursor
                        }}
                        nodes {{
                            commit {{
                                oid
                            }}
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
            query_params=dict(owner=owner, name=name, number=number, after="null")
        )

        self.number = number

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.pull_struct.PullRequestCommitsStruct`. For more
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.PULL_REQUEST][
                IssueStatic.COMMITS][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.PULL_REQUEST][IssueStatic.COMMITS][
                APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][IssueStatic.PULL_REQUEST][
                IssueStatic.COMMITS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.PullRequestCommitModel` object representing the
            fetched data.
            :return: A :class:`gras.github.entity.github_models.PullRequestCommitModel` object
            :rtype: class
        """

        for lst in self.iterator():
            for pr in lst:
                yield self.object_decoder(num=self.number, dic=pr)
