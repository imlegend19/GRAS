from abc import ABC
from string import Template

from api_static import APIStatic, RepositoryStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY

from models import RepositoryModel


class RepositoryStruct(GitHubQuery, ABC):
    REPO_QUERY_TEMPLATE = Template(
        """
             {
                resource(url: "$url") {
                    ... on Repository {
                       id
                       name
                       createdAt
                       description
                       diskUsage
                       forkCount
                       homepageUrl
                       isArchived
                       isFork
                       url
                       updatedAt
                       owner {
                         login
                         id
                       }
                       primaryLanguage {
                         name
                       }
                       stargazers {
                         totalCount
                       }
                       watchers {
                         totalCount
                       }
                    }
                }
             }
        """
    )

    def __init__(self, github_token, url):
        REPO_QUERY = RepositoryStruct.REPO_QUERY_TEMPLATE.substitute(url=url)
        super().__init__(github_token, query=REPO_QUERY)

    def iterator(self):
        generator = self.generator()
        return dict(next(generator)[APIStatic.DATA][APIStatic.RESOURCE])

    def object_decoder(self, dic) -> RepositoryModel:
        obj = RepositoryModel(
            name=dic[APIStatic.NAME],
            url=dic[APIStatic.URL],
            created_at=dic[APIStatic.CREATED_AT],
            updated_at=dic[APIStatic.UPDATED_AT],
            description=dic[APIStatic.DESCRIPTION],
            disk_usage=dic[RepositoryStatic.DISK_USAGE],
            fork_count=dic[RepositoryStatic.FORK_COUNT],
            homepage_url=dic[RepositoryStatic.HOMEPAGE_URL],
            is_archived=dic[RepositoryStatic.IS_ARCHIVED],
            is_fork=dic[RepositoryStatic.IS_FORK],
            owner_login=dic[RepositoryStatic.OWNER][APIStatic.LOGIN],
            primary_language=dic[RepositoryStatic.PRIMARY_LANGUAGE][APIStatic.NAME],
            stargazer_count=dic[RepositoryStatic.STARGAZERS][APIStatic.TOTAL_COUNT],
            watcher_count=dic[RepositoryStatic.WATCHERS][APIStatic.TOTAL_COUNT],
        )

        return obj


if __name__ == '__main__':
    repo = RepositoryStruct(github_token=AUTH_KEY,
                            url="https://github.com/sympy/sympy")

    # repo_obj = object_decoder(dict(next(repo.generator())[APIStatic.DATA][APIStatic.RESOURCE]))
    repo_obj = repo.object_decoder(repo.iterator())
    print(repo_obj.name)
