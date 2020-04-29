import logging
import time
from abc import ABCMeta
from abc import abstractmethod
from datetime import datetime

from requests import exceptions, request

from components.query_engine.entity.api_static import APIStatic


class GitHubQuery(metaclass=ABCMeta):
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
    def headers(self):
        default_headers = dict(
            Authorization=f"token {self.github_token}",
        )

        return {
            **default_headers,
        }

    def __send_request(self, param):
        tries = 1
        while tries <= 3:
            logging.debug("Sending request to base url. (Try: %s)" % tries)

            try:
                req = request(
                    'post',
                    APIStatic.BASE_URL,
                    headers=self.headers,
                    json=param
                )
            except exceptions.ConnectionError:
                time.sleep(2)
                try:
                    req = request(
                        'post',
                        APIStatic.BASE_URL,
                        headers=self.headers,
                        json=param
                    )
                except exceptions.ConnectionError:
                    logging.error("Connection Error while fetching data from base url.")
                    break

            if req.status_code == 200:
                if 'X-RateLimit-Remaining' in req.headers and int(req.headers['X-RateLimit-Remaining']) <= 2:
                    reset_time = datetime.fromtimestamp(float(req.headers['X-RateLimit-Reset']))
                    wait_time = (reset_time - datetime.now()).total_seconds() + 5

                    logging.info("Github API maximum rate limit reached. Waiting for %0.5f sec..." % wait_time)
                    time.sleep(wait_time)

                    req = request(
                        'post',
                        APIStatic.BASE_URL,
                        headers=self.headers,
                        json=param
                    )

                return req.json()
            else:
                logging.error("Problem with getting data via base url. Error: %s" % req.text)
                tries += 1
                time.sleep(2)

        raise exceptions.RequestException("Problem with getting data via base url.")

    def generator(self):
        while True:
            try:
                if self.query_params is None:
                    yield self.__send_request(
                        param=dict(query=self.query)
                    )
                else:
                    yield self.__send_request(
                        param=dict(query=self.query.format_map(self.query_params))
                    )
            except exceptions.HTTPError as http_err:
                raise http_err
            except Exception as err:
                raise err

    @abstractmethod
    def iterator(self):
        pass
