class GrasException(Exception):
    """Base GRAS Exception."""
    
    message = "GRAS Exception"
    
    def __init__(self, **kwargs):
        super().__init__()
        self.msg = self.message % kwargs
    
    def __str__(self):
        return self.msg


class GrasArgumentParserError(GrasException):
    """Exception to be raised by :class:`~main.GrasArgumentParser` in case the user has entered invalid arguments."""
    
    message = "Invalid Arguments: %(msg)"


class GrasConfigError(GrasException):
    """Exception to be raise if the config file does not contain all the required details"""
    
    message = "Config File error: %(msg)"
