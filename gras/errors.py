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
    """Database connection exception"""

    message = "%(msg)s"


class InvalidTokenError(GrasError):
    """Exception to be raised if the user enters invalid token"""

    message = "%(msg)s"


class ObjectDoesNotExistError(GrasError):
    """Exception to be raised if HTTPError is throws, i.e when object to be fetched has been deleted."""

    message = "%(msg)s"


class QueryObjectError(GrasError):
    """Exception to be raised by :class:`~gras.github.query_builder.QueryObject`"""

    message = "%(msg)s"


class BadGatewayError(GrasError):
    """Exception to be raised by :class:`~gras.github.github.GithubInterface` on ``502 Bad Gateway`` response."""

    pass


class DownloaderError(GrasError):
    """Exception to be thrown by :class:`~gras.pipermail.downloader.Downloader`"""

    message = "%(msg)s"


class YandexKeyError(GrasError):
    """
    Exception to be thrown by :class:`~gras.identity_merging.IdentityMiner` on
    :class:`yandex.Translater.TranslaterError`
    """

    message = "Invalid Yandex Key: %(msg)s"


class YandexError(GrasError):
    """Exception to be thrown by :class:`~gras.identity_merging.IdentityMiner`"""

    message = "Yandex Error! %(msg)s"
