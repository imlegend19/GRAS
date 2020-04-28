from abc import ABCMeta
from abc import abstractmethod

from requests import exceptions, request

from api_static import APIStatic


class GitHubQuery(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(
            self,
            github_token=None,
            query_params=None,
            query=None
    ):
        self.github_token = github_token
        self.query = query
        self.query_params = query_params

    @property
    @abstractmethod
    def headers(self):
        default_headers = dict(
            Authorization=f"token {self.github_token}",
        )

        return {
            **default_headers,
        }

    @abstractmethod
    def generator(self):
        while True:
            try:
                if self.query_params is None:
                    yield request(
                        'post',
                        APIStatic.BASE_URL,
                        headers=self.headers,
                        json=dict(query=self.query)
                    ).json()
                else:
                    yield request(
                        'post',
                        APIStatic.BASE_URL,
                        headers=self.headers,
                        json=dict(query=self.query.format_map(self.query_params))
                    ).json()
            except exceptions.HTTPError as http_err:
                raise http_err
            except Exception as err:
                raise err

    @abstractmethod
    def iterator(self):
        pass
