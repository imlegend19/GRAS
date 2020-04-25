from pprint import pprint
from string import Template

from gh_query import GitHubQuery


class Repository:
    def __init__(self, url, owner_id, name, description, ):
        pass


class RepositoryStruct(GitHubQuery):
    REPO_QUERY_TEMPLATE = Template(
        """
             {
                resource(url: $url) {
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
        super().__init__(github_token,
                         query=REPO_QUERY)


if __name__ == '__main__':
    repo = RepositoryStruct(github_token="93b717120efc9123208279a6d87b4d50dfe7168d",
                            url="\"https://github.com/sympy/sympy\"")
    pprint(dict(next(repo.generator())))
