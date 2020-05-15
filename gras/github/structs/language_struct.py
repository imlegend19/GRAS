from gras.github.entity.api_static import APIStaticV4, RepositoryStatic
from gras.github.entity.github_models import LanguageModel
from gras.github.github import GithubInterface


class LanguageStruct(GithubInterface, LanguageModel):
    LANGUAGE_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                languages(first: 100, orderBy: {{ field: SIZE, direction: ASC }}, after: {after}) {{
                    edges {{
                        size
                        node {{
                            name
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
    
    def __init__(self, name, owner):
        super().__init__(
            query=self.LANGUAGE_QUERY,
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
            
            endCursor = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.LANGUAGES][APIStaticV4.PAGE_INFO][APIStaticV4.END_CURSOR]
            
            self.query_params[APIStaticV4.AFTER] = '\"' + endCursor + '\"' if endCursor is not None else "null"
            
            resp = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.LANGUAGES][APIStaticV4.EDGES]
            
            if resp is not None:
                if None not in resp:
                    yield response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                        RepositoryStatic.LANGUAGES][APIStaticV4.EDGES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                                RepositoryStatic.LANGUAGES][APIStaticV4.EDGES],
                        )
                    )

            hasNextPage = response[APIStaticV4.DATA][APIStaticV4.REPOSITORY][
                RepositoryStatic.LANGUAGES][APIStaticV4.PAGE_INFO][APIStaticV4.HAS_NEXT_PAGE]

    def process(self):
        for lst in self.iterator():
            for lang in lst:
                yield self.object_decoder(lang)