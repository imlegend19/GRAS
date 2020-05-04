from components.query_engine.entity.api_static import APIStaticV4, UserStatic
from components.query_engine.entity.models import UserModel
from components.query_engine.github import GithubInterface
from local_settings import AUTH_KEY


class AssignableUserStruct(GithubInterface, UserModel):
    QUERY = """
        {{
            repository(owner: "{owner}", name: "{name}") {{
                assignableUsers(first: 100, after: {after}) {{
                    nodes {{
                        login
                        name
                        email
                        createdAt
                        email
                        followers {{
                            totalCount
                        }}
                        location
                        updatedAt
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, github_token, owner, name, after="null"):
        super().__init__()
        
        self.github_token = github_token
        self.query = AssignableUserStruct.QUERY
        self.query_params = dict(name=name, owner=owner, after=after)
    
    def iterator(self):
        generator = self.generator()
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
    
    def __init__(self, github_token, login):
        super().__init__()
        
        self.github_token = github_token
        self.query = UserStruct.QUERY
        self.query_params = dict(login=login)
    
    def iterator(self):
        generator = self.generator()
        return next(generator)[APIStaticV4.DATA][UserStatic.USER]


# if __name__ == '__main__':
#     ass_user = AssignableUserStruct(
#         github_token=AUTH_KEY,
#         owner="sympy",
#         name="sympy"
#     )
#
#     for lst in ass_user.iterator():
#         for o in lst:
#             print(ass_user.object_decoder(o).login)

if __name__ == '__main__':
    user = UserStruct(
        github_token=AUTH_KEY,
        login="imlegend19"
    )
    
    print(user.object_decoder(user.iterator()).login)
