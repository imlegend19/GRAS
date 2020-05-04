import logging
import time
from abc import ABCMeta, abstractmethod
from datetime import datetime

from requests import exceptions, request

from components.query_engine.entity.api_static import APIStaticV4
from local_settings import AUTH_KEY


class BaseInterface(metaclass=ABCMeta):
    @property
    @abstractmethod
    def tag(self):
        """
        Tag of the backend

        .. WARNING:: Must be unique among all the interfaces.
        """
        return
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def generator(self):
        pass
    
    @abstractmethod
    def iterator(self):
        pass


class GithubInterface(BaseInterface):
    def tag(self):
        return 'github'
    
    def __init__(self, github_token=None, query_params=None, url=APIStaticV4.BASE_URL, query=None,
                 additional_headers=None):
        super().__init__()
        
        self.github_token = github_token
        self.query = query
        self.url = url
        self.query_params = query_params
        self.additional_headers = additional_headers or dict()
    
    @property
    def headers(self):
        default_headers = dict(
            Authorization=f"token {self.github_token}"
        )
        
        return {
            **default_headers,
            **self.additional_headers
        }
    
    def _send_request(self, param=None, only_json=True, method="post"):
        tries = 1
        while tries <= 3:
            logging.debug(f"Sending request to url {self.url}. (Try: {tries})")
            
            try:
                req = request(
                    method,
                    self.url,
                    headers=self.headers,
                    json=param
                )
            except exceptions.ConnectionError:
                time.sleep(2)
                try:
                    req = request(
                        method,
                        self.url,
                        headers=self.headers,
                        json=param
                    )
                except exceptions.ConnectionError:
                    logging.error(f"Connection Error while fetching data from url {self.url}.")
                    break
            
            if req.status_code == 200:
                if 'X-RateLimit-Remaining' in req.headers and int(req.headers['X-RateLimit-Remaining']) <= 2:
                    reset_time = datetime.fromtimestamp(float(req.headers['X-RateLimit-Reset']))
                    wait_time = (reset_time - datetime.now()).total_seconds() + 5
                    
                    logging.info(f"Github API maximum rate limit reached. Waiting for {wait_time} sec...")
                    time.sleep(wait_time)
                    
                    req = request(
                        method,
                        self.url,
                        headers=self.headers,
                        json=param
                    )
                
                if only_json:
                    return req.json()
                else:
                    return req
            else:
                logging.error(f"Problem with getting data via url {self.url}. Error: {req.text}")
                tries += 1
                time.sleep(2)
        
        raise exceptions.RequestException(f"Problem with getting data via url {self.url}.")
    
    def generator(self):
        if self.url is None:
            self.url = APIStaticV4.BASE_URL
        
        while True:
            try:
                if self.query is not None:
                    if self.query_params is None:
                        yield self._send_request(
                            param=dict(query=self.query)
                        )
                    else:
                        yield self._send_request(
                            param=dict(query=self.query.format_map(self.query_params))
                        )
                else:
                    yield self._send_request(only_json=False, method="get")
            
            except exceptions.HTTPError as http_err:
                raise http_err
            except Exception as err:
                raise err
    
    def iterator(self):
        generator = self.generator()
        return next(generator)


if __name__ == '__main__':
    from components.utils import to_iso_format
    
    owner, name = "sympy", "sympy"
    start_date = to_iso_format("2012-01-01")
    end_date = to_iso_format("2012-01-02")
    
    github = GithubInterface(
        github_token=AUTH_KEY,
        url=f"https://api.github.com/search/commits?q=repo:{owner}/{name}+merge:false+"
            f"committer-date:{start_date}..{end_date}+sort:committer-date-asc&per_page=1&page=1"
    )
    
    response = github.iterator()
    print(response.status_code)
