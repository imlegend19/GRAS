from abc import ABCMeta, abstractmethod


class BaseInterface(metaclass=ABCMeta):
    MAX_RETRIES = 5
    
    @property
    @abstractmethod
    def tag(self):
        """
        Tag of the backend

        .. WARNING:: Must be unique among all the interfaces.
        """
        return
    
    @abstractmethod
    def __init__(self, max_retries=MAX_RETRIES):
        self.max_retries = max_retries

    @abstractmethod
    def _generator(self):
        pass

    @abstractmethod
    def iterator(self):
        pass

    @abstractmethod
    def process(self):
        pass
