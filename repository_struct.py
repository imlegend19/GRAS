from string import Template

from api_static import APIStatic, RepositoryStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY


class Repository:
    def __init__(self, created_at, updated_at, disk_usage, url, owner_login, name, description, fork_count,
                 homepage_url, is_archived, is_fork, primary_language, stargazer_count, watcher_count):

        self.name = name
        self.description = description
        self.fork_count = fork_count
        self.owner_login = owner_login
        self.url = url
        self.watcher_count = watcher_count
        self.stargazer_count = stargazer_count
        self.primary_language = primary_language
        self.is_fork = is_fork
        self.is_archived = is_archived
        self.homepage_url = homepage_url
        self.disk_usage = disk_usage
        self.updated_at = updated_at
        self.created_at = created_at


def object_decoder(dic) -> Repository:
    obj = Repository(
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


class RepositoryStruct(GitHubQuery):
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


if __name__ == '__main__':
    repo = RepositoryStruct(github_token=AUTH_KEY,
                            url="https://github.com/sympy/sympy")

    repo_obj = object_decoder(dict(next(repo.generator())[APIStatic.DATA][APIStatic.RESOURCE]))

    print(repo_obj.name)
