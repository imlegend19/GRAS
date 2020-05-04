from components.query_engine.entity.api_static import APIStaticV4, RepositoryStatic
from components.query_engine.entity.models import TopicModel
from components.query_engine.github import GithubInterface
from local_settings import AUTH_KEY


class TopicStruct(GithubInterface, TopicModel):
    TOPIC_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                repositoryTopics(first: 100, after: {after}) {{
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
    
    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=TopicStruct.TOPIC_QUERY,
            query_params=dict(name=name, owner=owner, after="null"),
        )
    
    def iterator(self):
        generator = self.generator()
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


if __name__ == "__main__":
    topic = TopicStruct(
        github_token=AUTH_KEY,
        name="sympy",
        owner="sympy"
    )
    
    for lst in topic.iterator():
        for t in lst:
            print(topic.object_decoder(t).topic_name)
