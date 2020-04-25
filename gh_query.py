from requests import exceptions, request
from api_static import APIStatic


class GitHubQuery:

    def __init__(
            self,
            github_token=None,
            query=None,
    ):
        self.github_token = github_token
        self.query = query

    @property
    def headers(self):
        default_headers = dict(
            Authorization=f"token {self.github_token}",
        )
        return {
            **default_headers,
        }

    def generator(self):
        while True:
            try:
                yield request(
                    'post',
                    APIStatic.BASE_URL,
                    headers=self.headers,
                    json=dict(query=self.query)
                ).json()
            except exceptions.HTTPError as http_err:
                raise http_err
            except Exception as err:
                raise err

    def iterator(self):
        pass
