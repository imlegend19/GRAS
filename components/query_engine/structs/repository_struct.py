from components.query_engine.entity.api_static import APIStaticV4
from components.query_engine.entity.github_models import RepositoryModel
from components.query_engine.github import GithubInterface


class RepositoryStruct(GithubInterface, RepositoryModel):
    QUERY = """
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
    
    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=self.QUERY,
            query_params=dict(name=name, owner=owner)
        )
    
    def iterator(self):
        generator = self.generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.REPOSITORY]
    
    def process(self):
        return self.object_decoder(self.iterator())
