from gras.github.entity.api_static import APIStaticV4
from gras.github.entity.github_models import RateLimitModel
from gras.github.github import GithubInterface


class RateLimitStruct(GithubInterface, RateLimitModel):
    """
        The object models the query to fetch the rate limit information of a client and generates an object using
        :class:`gras.github.entity.github_models.RateLimitModel` containing the fetched data.

        Please see GitHub's `ratelimit documentation`_ for more information.

        .. _ratelimit documentation:
            https://developer.github.com/v4/object/ratelimit/

    """
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
        """Constructor Method"""
        super().__init__(
            query=self.QUERY,
            github_token=github_token
        )
        
    def iterator(self):
        """
            Iterator function for :class:`gras.github.structs.rate_limit.RateLimitStruct`. For more information see
            :class:`gras.github.github.githubInterface`.
            :return: a single API response or a list of responses
            :rtype: generator<dict>
        """

        generator = self._generator()
        return next(generator)[APIStaticV4.DATA][APIStaticV4.RATE_LIMIT]

    def process(self):
        """
            generates a :class:`gras.github.entity.github_models.RateLimitModel` object representing the fetched data.
            :return: A :class:`gras.github.entity.github_models.RateLimitModel` object
            :rtype: class
        """
    
        return self.object_decoder(self.iterator())
