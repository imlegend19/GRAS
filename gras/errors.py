class GrasError(Exception):
    """Base GRAS Error."""
    
    message = "GRAS Error"
    
    def __init__(self, **kwargs):
        super().__init__()
        self.msg = self.message % kwargs
    
    def __str__(self):
        return self.msg


class GithubMinerError(GrasError):
    """Exception to be raised by :class:`~gras.github.github_miner.GithubMiner`"""
    
    message = "%(cause)s"


class GrasArgumentParserError(GrasError):
    """Exception to be raised by :class:`~main.GrasArgumentParser` in case the user has entered invalid arguments."""
    
    message = "Invalid Arguments: %(msg)s"


class GrasConfigError(GrasError):
    """Exception to be raise if the config file does not contain all the required details"""
    
    message = "Config File error: %(msg)s"


class DatabaseError(GrasError):
    """Database connecton exception"""
    
    message = "%(msg)s"


class InvalidTokenError(GrasError):
    """Exception to be raised if the user enters invalid token"""
    
    message = "%(msg)s"
