from abc import ABCMeta, abstractmethod


class BaseModel(metaclass=ABCMeta):
    def __init__(self):
        self.type_ = type(self)

    @abstractmethod
    def object_decoder(self, **kwargs):
        pass
