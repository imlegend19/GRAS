from components.query_engine.entity.api_static import APIStaticV4, LabelStatic
from components.query_engine.entity.models import LabelModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class LabelStruct(GitHubQuery, LabelModel):
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
            query=LabelStruct.LABEL_QUERY,
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
            
            resp = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.EDGES]
            
            if resp is not None:
                if None not in resp:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.EDGES]
            else:
                yield list(
                    filter(
                        None.__ne__,
                        response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.EDGES],
                    )
                )
            
            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][LabelStatic.LABELS][APIStaticV4.PAGE_INFO][
                APIStaticV4.HAS_NEXT_PAGE]


if __name__ == "__main__":
    label = LabelStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")
    
    for lst in label.iterator():
        for lab in lst:
            print(label.object_decoder(lab).name)
