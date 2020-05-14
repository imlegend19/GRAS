from requests import exceptions

from gras.github.entity.api_static import APIStaticV3, APIStaticV4, UserStatic
from gras.github.entity.github_models import AnonContributorModel, UserModel
from gras.github.github import GithubInterface


class AssignableUserStruct(GithubInterface, UserModel):
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
        super().__init__()
    
        self.query = self.QUERY
        self.query_params = dict(name=name, owner=owner, after=after)
    
    def iterator(self):
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
        for node_list in self.iterator():
            for node in node_list:
                yield node[UserStatic.LOGIN]


class UserNodesStruct(GithubInterface, UserModel):
    QUERY = """
        {{
            nodes(ids: [{node_ids}]) {{
                ... on User {{
                    login
                    name
                    email
                    location
                    createdAt
                    updatedAt
                    followers {{
                        totalCount
                    }}
                }}
            }}
        }}
    """

    def __init__(self, node_ids):
        super().__init__(
            query=self.QUERY,
            query_params=dict(node_ids=node_ids)
        )
    
    def iterator(self):
        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.NODES]
    
    def process(self):
        for node in self.iterator():
            yield self.object_decoder(node)


class ContributorList(GithubInterface, AnonContributorModel):
    def __init__(self, name, owner, anon=1):
        super().__init__(
            query=None,
            url=f"https://api.github.com/repos/{owner}/{name}/contributors?per_page=100&page=1&anon={anon}",
            query_params=None
        )
    
    def iterator(self):
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
        for lst in self.iterator():
            for obj in lst:
                try:
                    yield obj[APIStaticV3.NODE_ID]
                except KeyError:
                    yield self.object_decoder(obj)


class UserStructV3(GithubInterface, UserModel):
    def __init__(self, login):
        super().__init__(
            query=None,
            url=f"https://api.github.com/users/{login}",
            query_params=None
        )
    
    def iterator(self):
        generator = self._generator()
        return next(generator).json()
    
    def process(self):
        return self.object_decoder(self.iterator())


class UserStruct(GithubInterface, UserModel):
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
        super().__init__()
    
        self.query = self.QUERY
        self.query_params = dict(login=login)
    
    def iterator(self):
        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][UserStatic.USER]
    
    def process(self):
        try:
            return self.object_decoder(self.iterator())
        except exceptions.RequestException:
            return None
