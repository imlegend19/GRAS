from components.query_engine.entity.api_static import APIStatic, RepositoryStatic
from components.query_engine.entity.models import LanguageModel
from components.query_engine.gh_query import GitHubQuery
from local_settings import AUTH_KEY


class LanguageStruct(GitHubQuery, LanguageModel):
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

    def __init__(self, github_token, name, owner):
        super().__init__(
            github_token=github_token,
            query=LanguageStruct.LANGUAGE_QUERY,
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

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY][
                RepositoryStatic.LANGUAGES
            ][APIStatic.PAGE_INFO][APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = '"' + endCursor + '"'

            resp = response[APIStatic.DATA][APIStatic.REPOSITORY][
                RepositoryStatic.LANGUAGES
            ][APIStatic.EDGES]

            if resp is not None:
                if None not in resp:
                    yield response[APIStatic.DATA][APIStatic.REPOSITORY][
                        RepositoryStatic.LANGUAGES
                    ][APIStatic.EDGES]
                else:
                    yield list(
                        filter(
                            None.__ne__,
                            response[APIStatic.DATA][APIStatic.REPOSITORY][
                                RepositoryStatic.LANGUAGES
                            ][APIStatic.EDGES],
                        )
                    )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY][
                RepositoryStatic.LANGUAGES
            ][APIStatic.PAGE_INFO][APIStatic.HAS_NEXT_PAGE]


if __name__ == "__main__":
    lang = LanguageStruct(github_token=AUTH_KEY, owner="sympy", name="sympy")

    for lst in lang.iterator():
        for lan in lst:
            print(lang.object_decoder(lan).language)
