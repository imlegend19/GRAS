from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import ForkModel
from gras.github.github import GithubInterface


class ForkStruct(GithubInterface, ForkModel):
    FORK_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                forks(first: 100, orderBy: {{field: CREATED_AT, direction: ASC}}, after: {after}) {{
                    nodes {{
                        createdAt
                        nameWithOwner
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
        }}
    """

    def __init__(self, name, owner):
        super().__init__(
            query=self.FORK_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )

    def iterator(self):
        generator = self._generator()
        hasNextPage = True

        while hasNextPage:
            try:
                response = next(generator)
            except StopIteration:
                break

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.FORKS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.FORKS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.FORKS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for fork in lst:
                yield self.object_decoder(fork)