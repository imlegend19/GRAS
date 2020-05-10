from gras.github.entity.api_static import APIStaticV4, LabelStatic
from gras.github.entity.github_models import LabelModel
from gras.github.github import GithubInterface


class LabelStruct(GithubInterface, LabelModel):
    LABEL_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                labels(first: 100, orderBy: {{ field:  NAME, direction: ASC }}, after: {after}) {{
                    edges {{
                        node {{
                            color
                            name
                            createdAt
                        }}
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }}
            }}
        }}
    """
    
    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token,
            query=self.LABEL_QUERY,
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

            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.PAGE_INFO][
                APIStaticV4.END_CURSOR]

            self.query_params[APIStaticV4.AFTER] = "\"" + endCursor + "\"" if endCursor is not None else "null"

            yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.EDGES]

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.PAGE_INFO][
                APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for label in lst:
                yield self.object_decoder(label)
