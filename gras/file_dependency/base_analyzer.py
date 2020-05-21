from abc import ABCMeta, abstractmethod

class BaseAnalyzer(metaclass=ABCMeta):
    """
    BaseAnalyzer class to analyze source code to create file-dependency graphs
    """
    def __init__(self):
        pass