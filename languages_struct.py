from string import Template

from api_static import APIStatic, LanguageStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY  # Not changing this


class Languages:
    def __init__(self, Id, languages, created_at, total_size):
        self.Id = Id
        self.languages = languages
        self.created_at = created_at
        self.total_size = total_size


def object_decoder(dic) -> Languages:
    obj = Languages(

    )
    return obj


class LanguagesStruct(GitHubQuery):
    LANGUAGES_QUERY_TEMPLATE = Template(
        """
            {
                repository(name: $name, owner: $owner) {
                    id
                    createdAt
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
        LANGUAGES_QUERY = LanguagesStruct.LANGUAGES_QUERY_TEMPLATE.substitute(
            name=name, owner=owner)
        super().__init__(github_token, query=LANGUAGES_QUERY)


if __name__ == "__main__":
    languages = LanguagesStruct(
        github_token=AUTH_KEY, owner="sympy", name="sympy")

    languages_obj = object_decoder(
        dict(next(languages.generator())[APIStatic.DATA][APIStatic.RESOURCE]))
