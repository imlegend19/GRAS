import ast
from ast import Attribute, Call, Name

from gras.file_dependency.python.node_types import AttributeTree, CallTree, Class, Decorator, Function


class FileAnalyzer(ast.NodeVisitor):
    """
    `NodeVisitor` class that visits specifics Nodes in an abstract syntax tree and generates a dictionary.
    For more information,see `ast.NodeVisitor`_

    .. _ast.NodeVisitor :
        https://docs.python.org/3/library/ast.html#ast.NodeVisitor
    """
    
    def __init__(self):
        """Constructor Method"""
        self.stats = {
            "classes"              : [],
            "class_count"          : 0,
            "imports"              : [],
            "import_count"         : 0,
            "functions"            : [],
            "function_count"       : 0,
            "global_variable_count": 0,
            "global_variables"     : []
        }
    
    def visit_ClassDef(self, node):
        if node.name not in self.stats["classes"]:
            self.stats["classes"].append({
                "type"      : Class,
                "name"      : node.name,
                "docstring" : ast.get_docstring(node),
                "methods"   : [],
                "decorators": self.__parse_decorators(node.decorator_list)
            })
            
            for body in node.body:
                if isinstance(body, ast.FunctionDef) and body.name != "__init__":
                    self.stats["classes"][self.stats["class_count"]]["methods"].append({
                        "type"      : Function,
                        "name"      : body.name,
                        "docstring" : ast.get_docstring(body),
                        "decorators": list(decorator.id for decorator in body.decorator_list)
                    })
            
            self.stats["class_count"] += 1
            self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        if node.name != "__init__" and node.name not in self.stats["functions"]:
            self.stats["functions"].append({
                "name"      : node.name,
                "decorators": self.__parse_decorators(node.decorator_list),
                "docstring" : ast.get_docstring(node)
            })

            self.stats["function_count"] += 1
    
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name not in self.stats["imports"]:
                self.stats["import_count"] += 1
                self.stats["imports"].append({
                    "name"         : alias.name,
                    "imported_from": None
                })
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name not in self.stats["imports"]:
                self.stats["import_count"] += 1
                self.stats["imports"].append({
                    "name"         : alias.name,
                    "imported_from": node.module
                })
        
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        for alias in node.targets:
            if isinstance(alias, ast.Tuple):
                for name in alias.elts:
                    if name.id not in self.stats["global_variables"]:
                        self.stats["global_variables"].append(name.id)
            elif alias.id not in self.stats["global_variables"]:
                self.stats["global_variables"].append(alias.id)
                self.stats["global_variable_count"] += 1

    def gen(self):
        return self.stats

    @staticmethod
    def __parse_decorators(lst):
        objects = []
    
        for decorator in lst:
            if isinstance(decorator, Name):
                dic = {
                    "type": Decorator(subtype=Name),
                    "name": decorator.id,
                    "line": decorator.lineno
                }
            elif isinstance(decorator, Call):
                # @deco()-> Call
                # @a.deco() -> CallTree
                if isinstance(decorator.func, Attribute):
                    dic = {
                        "type" : Decorator(subtype=CallTree),
                        "value": CallTree(node=decorator),
                        "line" : decorator.lineno
                    }
                else:
                    dic = {
                        "type"        : Decorator(subtype=Call),
                        "name"        : decorator.func.id,
                        "line"        : decorator.lineno,
                        "total_args"  : decorator.args.__len__(),
                        "total_kwargs": decorator.keywords.__len__()
                    }
            elif isinstance(decorator, Attribute):
                dic = {
                    "type" : Decorator(subtype=AttributeTree),
                    "value": AttributeTree(node=decorator),
                    "line" : decorator.lineno
                }
            else:
                raise NotImplementedError
        
            objects.append(dic)
    
        return objects

# if __name__ == '__main__':
#     # dic = parse_file("/home/mahen/PycharmProjects/GRAS/gras/github/", "github_miner.py")
#     dic = parse_file("/home/mahen/.config/JetBrains/PyCharm2020.1/scratches/", "scratch_8.py")
#
#     import json
#
#     print(json.dumps(dic, indent=4))
