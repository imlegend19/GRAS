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


if __name__ == '__main__':
    t = [
        "b62c6b609bb8065399d4f09a85d6bad15894f345",
        "b647ad8aaa1482bd6b090ab8f290b3579ca5b7dc",
        "5b4174a5138e19e56492ed9ed156b0536ae6fc28",
        "e07f3d6b8761a25c05790e999e6b9b3fe5dee242",
        "611d49d3ea9b270e7533b1ed001f42dbdac3a145",
        "055caf4d79af024f16c903b4886bcb0c608a465a",
        "c19a9abcc15793107c88ced3d5115358894b1c69",
        "223163d584710a1f4efbb3e04698b19385fd503b"
    ]
    
    for token in t:
        r = RateLimitStruct(
            github_token=token
        ).process()
        
        print(r)
