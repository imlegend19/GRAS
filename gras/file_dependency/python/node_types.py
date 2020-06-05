from abc import ABC
from ast import Attribute, Call, Name


class BaseType(ABC):
    __slots__ = ("type_", "subtype")

    def __init__(self, subtype):
        self.type_ = type(self)
        self.subtype = subtype


class Class(BaseType):
    __name__ = "Class"


class Function(BaseType):
    __name__ = "Function"


class Method(BaseType):
    __name__ = "Method"


class GlobalVariable(BaseType):
    __name__ = "Global Variable"


class CallTree:
    def __init__(self, node):
        self.__set_values(node)

        if isinstance(node.func, Attribute):
            self.parent = AttributeTree(node=node.func)
        else:
            self.parent = None

    def __set_values(self, node):
        if isinstance(node, Attribute):
            self.name = node.attr
            self.type = Attribute
        elif isinstance(node, Name):
            self.name = node.id
            self.type = Name
        elif isinstance(node, Call):
            if isinstance(node.func, Name):
                self.name = node.func.id
            else:
                self.name = node.func.attr
            self.type = Call
            self.args = node.args.__len__()
            self.kwargs = node.keywords.__len__()
        else:
            raise NotImplementedError


class AttributeTree:
    def __init__(self, node):
        self.__set_values(node)

        if isinstance(node.value, Attribute):
            self.parent = AttributeTree(node=node.value)
        else:
            self.parent = None

    def __set_values(self, node):
        if isinstance(node, Attribute):
            self.name = node.attr
            self.type = Attribute
        elif isinstance(node, Name):
            self.name = node.id
            self.type = Name
        elif isinstance(node, Call):
            self.name = node.func.id
            self.type = Call
            self.args = node.args.__len__()
            self.kwargs = node.keywords.__len__()
        else:
            raise NotImplementedError
