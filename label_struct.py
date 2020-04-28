from abc import ABC

from api_static import APIStatic, LabelStatic
from gh_query import GitHubQuery
from local_settings import AUTH_KEY
from models import LabelModel


class LabelStruct(GitHubQuery, ABC):
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
        labels = []

        while hasNextPage:
            response = next(generator)

            endCursor = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [LabelStatic.LABELS][APIStatic.PAGE_INFO] \
                [APIStatic.END_CURSOR]

            self.query_params["after"] = '\"' + endCursor + '\"'

            labels.extend(
                response[APIStatic.DATA][APIStatic.REPOSITORY]
                [LabelStatic.LABELS][APIStatic.EDGES]
            )

            hasNextPage = response[APIStatic.DATA][APIStatic.REPOSITORY] \
                [LabelStatic.LABELS][APIStatic.PAGE_INFO] \
                [APIStatic.HAS_NEXT_PAGE]

        return labels

    def object_decoder(self, dic) -> LabelModel:
        obj = LabelModel(
            color=dic[APIStatic.NODE][LabelStatic.COLOR],
            name=dic[APIStatic.NODE][APIStatic.NAME],
            created_at=dic[APIStatic.NODE][APIStatic.CREATED_AT],
        )

        return obj


if __name__ == "__main__":
    label = LabelStruct(github_token=AUTH_KEY, name="sympy", owner="sympy")

    label_list = label.iterator()

    for i in range(len(label_list)):
        label_list[i] = label.object_decoder(label_list[i])

    for _ in label_list:
        print(_.name)
