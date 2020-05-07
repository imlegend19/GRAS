from string import Template

from components.query_engine.entity.api_static import APIStaticV4
from components.query_engine.entity.github_models import RepositoryModel
from components.query_engine.github import GithubInterface
from local_settings import AUTH_KEY


class RepositoryStruct(GithubInterface, RepositoryModel):
    REPO_QUERY_TEMPLATE = Template(
        """
            {{
                repository(name: "{name}", owner: "{owner}") {{
                    name
                    createdAt
                    updatedAt
                    description
                    diskUsage
                    forkCount
                    homepageUrl
                    isArchived
                    isFork
                    url
                    parent {{
                        url
                    }}
                    primaryLanguage {{
                        name
                    }}
                    stargazers {{
                        totalCount
                    }}
                    watchers {{
                        totalCount
                    }}
                }}
            }}
        """
    )
    
    def __init__(self, github_token, name, owner):
        REPO_QUERY = RepositoryStruct.REPO_QUERY_TEMPLATE.substitute(name=name, owner=owner)
        super().__init__(github_token, query=REPO_QUERY)
    
    def iterator(self):
        generator = self.generator()
        return dict(next(generator)[APIStaticV4.DATA][APIStaticV4.RESOURCE])


if __name__ == '__main__':
    repo = RepositoryStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy"
    )
    
    # repo_obj = object_decoder(dict(next(repo.generator())[APIStatic.DATA][APIStatic.RESOURCE]))
    repo_obj = repo.object_decoder(repo.iterator())
    print(repo_obj.name)
