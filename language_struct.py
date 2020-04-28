from abc import ABC

from api_static import APIStatic, LanguageStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY


class Language:
    def __init__(self, language, size):
        self.language = language
        self.size = size


def object_decoder(dic) -> Language:
    obj = Language(
        language=dic[APIStatic.NODE][APIStatic.NAME],
        size=dic[LanguageStatic.SIZE] / 1024
    )

    return obj


class LanguageStruct(GitHubQuery, ABC):
    LANGUAGE_QUERY = """
        {{
            repository(name: "{name}", owner: "{owner}") {{
                languages(first: 100, orderBy: {{field: SIZE, direction: ASC}}, after: {after}) {{
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
            query_params=dict(name=name, owner=owner, after="null")
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        languages = []

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [LanguageStatic.LANGUAGES][APIStatic.PAGE_INFO] \
                [APIStatic.END_CURSOR]

            self.query_params[APIStatic.AFTER] = "\"" + endCursor + "\""

            languages.extend(response[APIStatic.DATA]
                             [APIStatic.REPOSITORY]
                             [LanguageStatic.LANGUAGES]
                             [APIStatic.EDGES])

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [LanguageStatic.LANGUAGES][APIStatic.PAGE_INFO] \
                [APIStatic.HAS_NEXT_PAGE]

        return languages


if __name__ == "__main__":
    lang = LanguageStruct(github_token=AUTH_KEY,
                          owner="sympy",
                          name="sympy")

    lang_list = lang.iterator()
    for i in range(len(lang_list)):
        lang_list[i] = object_decoder(lang_list[i])

    for _ in lang_list:
        print(_.language)
