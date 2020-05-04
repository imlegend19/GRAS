import configparser
import os
import unittest
import unittest.mock as mock

from requests import exceptions

from components.query_engine.github import GithubInterface
from components.utils import to_iso_format
from local_settings import AUTH_KEY


class TestGithubInterface(unittest.TestCase):
    def setUp(self):
        parser = configparser.ConfigParser()
        parser.read_file(open(os.path.dirname(os.path.abspath(__file__)) + "/data/test_config.ini"))
        
        self.github_token = parser.get("GITHUB", "github_token")
        self.name = parser.get("GITHUB", "name")
        self.owner = parser.get("GITHUB", "owner")
        self.start_date = to_iso_format(parser.get("GITHUB", "start_date"))
        self.end_date = to_iso_format(parser.get("GITHUB", "end_date"))
        
        self.url = f"https://api.github.com/search/commits?q=repo:{self.owner}/" \
                   f"{self.name}+merge:false+committer-date:{self.start_date}.." \
                   f"{self.end_date}+sort:committer-date-asc&per_page=1&page=1"
    
    @mock.patch('components.query_engine.github.GithubInterface')
    def test_send_request_via_url_if_accept_header(self, mock_request):
        mock_request.return_value.status_code = 200
        
        github = GithubInterface(
            github_token=self.github_token or AUTH_KEY,
            url=f"https://api.github.com/search/commits?q=repo:{self.owner}/{self.name}+merge:false+"
                f"committer-date:{self.start_date}..{self.end_date}+sort:committer-date-asc&per_page=1&page=1",
            additional_headers=dict(Accept="application/vnd.github.cloak-preview+json")
        )
        
        response = github.iterator()
        self.assertTrue(response.status_code)
    
    @mock.patch('components.query_engine.github.GithubInterface')
    def test_send_request_via_url_if_no_accept_header(self, mock_request):
        mock_request.return_value.side_effect = f"Problem with getting data via url {self.url}."
        
        github = GithubInterface(
            github_token=self.github_token or AUTH_KEY,
            url=self.url
        )
        
        try:
            github.iterator()
        except exceptions.RequestException as e:
            self.assertTrue(e)
