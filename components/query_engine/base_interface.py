from abc import ABCMeta, abstractmethod


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
