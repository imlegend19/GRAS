import logging
import time
from datetime import datetime

from requests import Session, adapters, exceptions

from gras.base_interface import BaseInterface
from gras.github.entity.api_static import APIStaticV4

logger = logging.getLogger("main")


class GithubInterface(BaseInterface):
    GET = "get"
    POST = "post"
    
    @property
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
            Authorization=f"token {self.github_token}",
            Connection="close",
        )
        
        return {
            **default_headers,
            **self.additional_headers
        }
    
    def _create_http_session(self):
        self.session = Session()
        
        if self.headers:
            self.session.headers.update(self.headers)
        
        self.session.mount('http://', adapters.HTTPAdapter(max_retries=self.max_retries))
        self.session.mount('https://', adapters.HTTPAdapter(max_retries=self.max_retries))
    
    def _fetch(self, url, headers, method, payload=None):
        if method == self.GET:
            response = self.session.get(url, params=payload, headers=headers)
        else:
            response = self.session.post(url, json=payload, headers=headers)
        
        try:
            response.raise_for_status()
        except Exception as e:
            raise e
        
        return response
    
    def _close_session(self):
        """Close the session"""
        
        if self.session:
            self.session.keep_alive = False
    
    def _send_request(self, param=None, only_json=True, method=POST):
        self._create_http_session()
        
        tries = 1
        while tries <= 3:
            logger.debug(f"Sending request to url {self.url}. (Try: {tries})")
            try:
                req = self._fetch(url=self.url, headers=self.headers, method=method, payload=param)
            except exceptions.ConnectionError:
                time.sleep(2)
                try:
                    req = self._fetch(url=self.url, headers=self.headers, method=method, payload=param)
                except exceptions.ConnectionError:
                    logging.error(f"Connection Error while fetching data from url {self.url}.")
                    break
            
            if req.status_code == 200:
                if 'X-RateLimit-Remaining' in req.headers and int(req.headers['X-RateLimit-Remaining']) <= 2:
                    reset_time = datetime.fromtimestamp(float(req.headers['X-RateLimit-Reset']))
                    wait_time = (reset_time - datetime.now()).total_seconds() + 5
    
                    logger.info(f"Github API maximum rate limit reached. Waiting for {wait_time} sec...")
                    time.sleep(wait_time)
    
                    req = self._fetch(url=self.url, headers=self.headers, method=method, payload=param)

                self._close_session()

                content = req.json()
                if "errors" in content:
                    raise exceptions.RequestException(f"Problem with getting data via url {self.url} + {self.query}.")

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
                    yield self._send_request(only_json=False, method=self.GET)
            
            except exceptions.HTTPError as http_err:
                raise http_err
            except Exception as err:
                raise err
    
    def iterator(self):
        generator = self.generator()
        return next(generator)
