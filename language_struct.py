from string import Template

from api_static import APIStatic, LanguageStatic, RepositoryStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY


class Language:
    def __init__(self, language, size):
        self.language = language
        self.size = size


def object_decoder(dic) -> Language:
    obj = Language(
        language=dic[APIStatic.NODE][APIStatic.NAME],
        size=dic[LanguageStatic.SIZE]/1024
    )

    return obj


class LanguageStruct(GitHubQuery):
    LANGUAGE_QUERY_TEMPLATE = Template(
        """
            {
                repository(name: "$name", owner: "$owner") {
                    languages(first: 100, orderBy: {field: SIZE, direction: ASC}) {
                        edges {
                            size
                            node {
                                name
                                id
                            }
                        }
                    }
                }
            }   
        """
    )

    def __init__(self, github_token, name, owner):
        LANGUAGE_QUERY = LanguageStruct.LANGUAGE_QUERY_TEMPLATE.substitute(name=name, owner=owner)
        super().__init__(github_token, query=LANGUAGE_QUERY)


if __name__ == "__main__":
    lang = LanguageStruct(github_token=AUTH_KEY,
                          owner="sympy",
                          name="sympy")

    lang_list = []
    result = dict(next(lang.generator())
                  [APIStatic.DATA]
                  [RepositoryStatic.REPOSITORY]
                  [LanguageStatic.LANGUAGES])
    for item in result[APIStatic.EDGES]:
        lang_list.append(object_decoder(item))

    for i in lang_list:
        print(i.language, i.size)
