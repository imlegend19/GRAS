import logging

from requests import exceptions

from gras.errors import ObjectDoesNotExistError
from gras.github.entity.api_static import APIStaticV3, APIStaticV4, CommitStatic, UserStatic
from gras.github.entity.github_models import AnonContributorModel, CommitUserModel, UserModel
from gras.github.github import GithubInterface

logger = logging.getLogger("main")


class AssignableUserStruct(GithubInterface, UserModel):
    """
        The object models the query to fetch a list of users that can be assigned to issues in a repository and
        generates an object using :class:`gras.github.entity.github_models.UserModel` containing the
        fetched data.

        Please see GitHub's `repository documentation`_ , `user connection documentation`_ for more
        information.

        .. _repository documentation:
            https://developer.github.com/v4/object/repository/

        .. _user connection documentation:
            https://developer.github.com/v4/object/userconnection

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
        :param after: return the elements in the list that come after the specified cursor `after`
        :type after: str
    """
    
    QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                assignableUsers(first: 100, after: {after}) {{
                    nodes {{
                        login
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, owner, name, after="null"):
        """Constructor Method"""
        super().__init__()

        self.query = self.QUERY
        self.query_params = dict(name=name, owner=owner, after=after)
    
    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.contributor_struct.AssignableUserStruct`. For more
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][UserStatic.ASSIGNABLE_USERS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][UserStatic.ASSIGNABLE_USERS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][UserStatic.ASSIGNABLE_USERS][
                APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]
    
    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.UserModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.UserModel` object
            :rtype: class
        """

        for node_list in self.iterator():
            for node in node_list:
                yield node[UserStatic.LOGIN]


class UserNodesStruct(GithubInterface, UserModel):
    """
        The object models the query to fetch users, organizations and bots associated with a repository generates an
        object
        using  :class:`gras.github.entity.github_models.UserModel` containing the fetched data.

        Please see GitHub's `Query documentation`_ , `node documentation`_ , `organization documentation`_ ,
        `user documentation`_ , `bot documentation`_ for more
        information.

        .. _Query documentation:
            https://developer.github.com/v4/query/

        .. _node documentation:
            https://developer.github.com/v4/interface/node/

        .. _organization documentation:
            https://developer.github.com/v4/object/organization/

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        .. _bot documentation:
            https://developer.github.com/v4/object/bot/

        :param node_ids: list of ids of nodes to fetch
        :type node_ids: list
    """

    QUERY = """
        {{
            nodes(ids: [{node_ids}]) {{
                type: __typename
                ... on Organization {{
                    createdAt
                    updatedAt
                    email
                    login
                    name
                    location
                }}
                ... on User {{
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
                ... on Bot {{
                    login
                    updatedAt
                    createdAt
                }}
            }}
        }}
    """

    def __init__(self, node_ids):
        """Constructor Method"""
        super().__init__(
            query=self.QUERY,
            query_params=dict(node_ids=node_ids)
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.contributor_struct.UserNodesStruct`. For more
            information see
            :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.NODES]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.UserModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.UserModel` object
            :rtype: class
        """

        for node in self.iterator():
            yield self.object_decoder(node)


class ContributorList(GithubInterface, AnonContributorModel):
    """
        The object models the query to fetch the list of contributors to a repository and generates an object using
        :class:`gras.github.entity.github_models.AnonContributorModel` containing the fetched data.

        Please see GitHub's `list contributors documentation`_ for more information.

        .. _list contributors documentation:
            https://developer.github.com/v3/repos/#list-contributors

        :param name: name of the repository
        :type name: str
        :param owner: owner of the repository
        :type owner: str
        :param anon: Set to `1` or `true` to include anonymous contributors in results
        :type anon: str
    """

    def __init__(self, name, owner, anon=1):
        """Constructor Method"""
        super().__init__(
            query=None,
            url=f"https://api.github.com/repos/{owner}/{name}/contributors?per_page=100&page=1&anon={anon}",
            query_params=None
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.contributor_struct.ContributorList`. For more
            information see :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
        hasNextPage = True

        while hasNextPage:
            response = next(generator)  # Response object (not json)

            try:
                next_url = response.links["next"]["url"]
            except KeyError:
                break

            self.url = next_url

            yield response.json()

            hasNextPage = True if next_url is not None else False

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.AnonContributorModel` object representing the
            fetched data.
            :return: A :class:`gras.github.entity.github_models.AnonContributorModel` object
            :rtype: class
        """

        for lst in self.iterator():
            for obj in lst:
                try:
                    yield obj[APIStaticV3.NODE_ID]
                except KeyError:
                    yield self.object_decoder(obj)


class UserStructV3(GithubInterface, UserModel):
    """
        The object models the query to fetch a list of users by their username and generates an object using
        :class:`gras.github.entity.github_models.UserModel` containing the fetched data.

        Please see GitHub's `users documentation`_ for more information.

        .. _users documentation:
            https://developer.github.com/v3/users/

        :param login: username
        :type login: str
    """

    def __init__(self, login):
        """Constructor Method"""
        super().__init__(
            query=None,
            url=f"https://api.github.com/users/{login}",
            query_params=None
        )

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.contributor_struct.UserStructV3`. For more information see
            :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()

        try:
            return next(generator).json()
        except ObjectDoesNotExistError:
            logger.error("User does not exist!")
            return None
        except Exception as e:
            logger.error(e)
            return None

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.UserModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.UserModel` object
            :rtype: class
        """

        user = self.iterator()
        if not user:
            return None

        return self.object_decoder(user)


class UserStruct(GithubInterface, UserModel):
    """
        The object models the query to fetch a list of users by their username and generates an object using
        :class:`gras.github.entity.github_models.UserModel` containing the fetched data.

        Please see GitHub's `user documentation`_ for more information.

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        :param login: username
        :type login: str
    """

    QUERY = """
        {{
            user(login: "{login}") {{
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
    """

    def __init__(self, login):
        """Constructor Method"""
        super().__init__()

        self.query = self.QUERY
        self.query_params = dict(login=login)

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.contributor_struct.UserStruct`. For more information see
            :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][UserStatic.USER]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.UserModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.UserModel` object
            :rtype: class
        """

        try:
            return self.object_decoder(self.iterator())
        except exceptions.RequestException:
            return None


class CommitUserStruct(GithubInterface, CommitUserModel):
    """
        The object models the query to fetch a single user object for a particular commit and generates an object using
        :class:`gras.github.entity.github_models.CommitUserModel` containing the fetched data.

        Please see GitHub's `user documentation`_ for more information.

        .. _user documentation:
            https://developer.github.com/v4/object/user/

        :param name: name
        :type name: str
        
        :param email: email
        :type email: str
        
        :param repo_name: name of the repository
        :type repo_name: str
        
        :param repo_owner: owner of the repository
        :type repo_owner: str
        
        :param oid: SHA-12 (oid) of the commit
        :type oid: str
    """
    
    QUERY = """
        {{
            repository(name:"{name}", owner:"{owner}") {{
                object(oid:"{oid}") {{
                    ... on Commit {{
                        author {{
                            user {{
                                login
                                createdAt
                                updatedAt
                                location
                                followers {{
                                    totalCount
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, name, email, repo_name, repo_owner, oid):
        super().__init__(
            query=self.QUERY,
            query_params=dict(name=repo_name, owner=repo_owner, oid=oid),
        )

        self.oid = oid
        self.name = name
        self.email = email

    async def async_iterator(self):
        """
            Async iterator function for :class:`gras.github.structs.contributor_struct.CommitUserStruct`. For more
            information see :class:`gras.github.github.githubInterface`.
            
            :return: a single API response or a list of responses
            :rtype: dict
        """
    
        gen = await self.async_request()
        return gen[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][CommitStatic.AUTHOR][
            UserStatic.USER]

    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.contributor_struct.CommitUserStruct`. For more
            information see :class:`gras.github.github.githubInterface`.
            
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """
    
        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.REPOSITORY][CommitStatic.OBJECT][CommitStatic.AUTHOR][
            UserStatic.USER]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.CommitUserModel` object representing the fetched data.
            
            :return: A :class:`gras.github.entity.github_models.CommitUserModel` object
            :rtype: CommitUserModel
        """
    
        try:
            user = self.object_decoder(dic=self.iterator(), name=self.name, email=self.email)
            if not user:
                return None
            else:
                return user
        except exceptions.RequestException:
            return None

    async def async_process(self):
        """
            generates a :class:`gras.github.entity.github_models.CommitUserModel` object representing the fetched data.
            
            :return: A :class:`gras.github.entity.github_models.CommitUserModel` object
            :rtype: CommitUserModel
        """
    
        try:
            result = await self.async_iterator()
            user = self.object_decoder(dic=result, name=self.name, email=self.email)
            if not user:
                return None
            else:
                return self.oid, user
        except exceptions.RequestException:
            return None
