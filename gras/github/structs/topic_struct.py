from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import TopicModel
from gras.github.github import GithubInterface


class TopicStruct(GithubInterface, TopicModel):
    TOPIC_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                repositoryTopics(first: 50, after: {after}) {{
                    nodes {{
                        url
                        topic {{
                            name
                            stargazers {{
                                totalCount
                            }}
                        }}
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
            query=self.TOPIC_QUERY,
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.TOPICS][
                APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][RepositoryStatic.TOPICS][APIStaticV4.NODES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.TOPICS][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for topic in lst:
                yield self.object_decoder(topic)
