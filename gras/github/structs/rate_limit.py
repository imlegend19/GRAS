from gras.github.entity.api_static import APIStaticV4
from gras.github.entity.github_models import RateLimitModel
from gras.github.github import GithubInterface


class RateLimitStruct(GithubInterface, RateLimitModel):
    QUERY = """
        {
            rateLimit {
                remaining
                limit
                resetAt
            }
        }
    """
    
    def __init__(self, github_token):
        super().__init__(
            query=self.QUERY,
            query_params=None,
            github_token=github_token
        )
    
    def iterator(self):
        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.RATE_LIMIT]
    
    def process(self):
        return self.object_decoder(self.iterator())
