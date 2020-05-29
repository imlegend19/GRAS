import ast
from ast import Attribute, Call, ClassDef, Expr, FunctionDef, Import, ImportFrom, Name, Pass
from collections import namedtuple

from gras.file_dependency.python.models import DecoratorModel, DefModel, ImportModel
from gras.file_dependency.python.node_types import AttributeTree, CallTree, Class, Function

Template = namedtuple('Template', 'type name decorators docstring')


class FileAnalyzer(ast.NodeVisitor):
    """
    `NodeVisitor` class that visits specifics Nodes in an abstract syntax tree and generates a dictionary.
    For more information,see `ast.NodeVisitor`_

    .. _ast.NodeVisitor :
        https://docs.python.org/3/library/ast.html#ast.NodeVisitor
    """
    
    def __init__(self):
        """Constructor Method"""
        
        self.functions = []
        self.classes = []
        self.imports = []
        self.global_variables = []
    
    def visit_ClassDef(self, node, return_=False):
        name = node.name
        line = node.lineno
        decorators = self.__parse_decorators(node.decorator_list)
        docstring = ast.get_docstring(node)
        
        arguments = []
        for base in node.bases:
            if isinstance(base, Name):
                arguments.append(node.name)
            else:
                # TODO: Implement Call and Attribute types
                raise NotImplementedError
        
        functions, classes, imports = [], [], []
        
        for obj in node.body:
            if isinstance(obj, Expr):
                ...
            elif isinstance(obj, Import):
                imports.extend(self.visit_Import(node=obj, return_=True))
            elif isinstance(obj, ImportFrom):
                imports.extend(self.visit_ImportFrom(node=obj, return_=True))
            elif isinstance(obj, FunctionDef):
                functions.append(self.visit_FunctionDef(node=obj, return_=True))
            elif isinstance(obj, ClassDef):
                classes.append(self.visit_ClassDef(node=obj, return_=True))
            elif isinstance(obj, Pass):
                pass
            else:
                # TODO: Implement various types
                print(type(obj), "Not Implemented")
        
        class_obj = DefModel(
            subtype=Class,
            name=name,
            decorators=decorators,
            arguments=arguments,
            functions=functions,
            classes=classes,
            imports=imports,
            docstring=docstring,
            line=line
        )
        
        if return_:
            return class_obj
        else:
            self.classes.append(class_obj)
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node, return_=False):
        if node.name != "__init__":
            name = node.name
            line = node.lineno
            decorators = self.__parse_decorators(node.decorator_list)
            docstring = ast.get_docstring(node)
            
            arguments = []
            # TODO: More info present -> defaults, kw_defaults, kwarg, kwonlyargs, vararg.
            # TODO: Add a special type of Model -> `ArgumentModel` should be made for arguments.
            for arg in node.args.args:
                arguments.append(arg.arg)
            
            functions, classes, imports = [], [], []
            
            for obj in node.body:
                if isinstance(obj, Expr):
                    ...
                elif isinstance(obj, Import):
                    imports.extend(self.visit_Import(node=obj, return_=True))
                elif isinstance(obj, ImportFrom):
                    imports.extend(self.visit_ImportFrom(node=obj, return_=True))
                elif isinstance(obj, FunctionDef):
                    func = self.visit_FunctionDef(node=obj, return_=True)
                    if func:
                        functions.append(func)
                elif isinstance(obj, ClassDef):
                    classes.append(self.visit_ClassDef(node=obj, return_=True))
                elif isinstance(obj, Pass):
                    pass
                else:
                    # TODO: Implement various types
                    print(type(obj), "Not Implemented")
            
            function_obj = DefModel(
                subtype=Function,
                name=name,
                decorators=decorators,
                arguments=arguments,
                functions=functions,
                classes=classes,
                imports=imports,
                docstring=docstring,
                line=line
            )
            
            if return_:
                return function_obj
            else:
                self.functions.append(function_obj)
        else:
            if return_:
                return None
        
        self.generic_visit(node)
    
    def visit_Import(self, node, return_=False):
        objs = []
        for alias in node.names:
            objs.append(
                ImportModel(
                    name=alias.name,
                    as_name=alias.asname,
                    line=node.lineno
                )
            )
        if return_:
            return objs
        else:
            self.imports.extend(objs)
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node, return_=False):
        objs = []
        for alias in node.names:
            objs.append(
                ImportModel(
                    module=node.module,
                    name=alias.name,
                    as_name=alias.asname,
                    line=node.lineno
                )
            )
        
        if return_:
            return objs
        else:
            self.imports.extend(objs)
        
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        for alias in node.targets:
            if isinstance(alias, ast.Tuple):
                for name in alias.elts:
                    if name.id not in self.global_variables:
                        self.global_variables.append(name.id)
            elif alias.id not in self.global_variables:
                self.global_variables.append(alias.id)
    
    def process(self):
        return {
            "functions": self.functions,
            "classes"  : self.classes,
            "variables": self.global_variables,
            "imports"  : self.imports
        }
    
    @staticmethod
    def __parse_decorators(lst):
        objects = []
        
        for decorator in lst:
            if isinstance(decorator, Name):
                objects.append(
                    DecoratorModel(
                        subtype=Name,
                        name=decorator.id,
                        value=None,
                        line=decorator.lineno
                    )
                )
            elif isinstance(decorator, Call):
                # @deco()-> Call
                # @a.deco() -> CallTree
                if isinstance(decorator.func, Attribute):
                    objects.append(
                        DecoratorModel(
                            subtype=CallTree,
                            name=decorator.func.attr,
                            value=CallTree(node=decorator),
                            line=decorator.lineno
                        )
                    )
                else:
                    objects.append(
                        DecoratorModel(
                            subtype=Call,
                            name=decorator.func.id,
                            line=decorator.lineno,
                            value=None,
                            total_args=decorator.args.__len__(),
                            total_kwargs=decorator.keywords.__len__()
                        )
                    )
            elif isinstance(decorator, Attribute):
                objects.append(
                    DecoratorModel(
                        subtype=Attribute,
                        name=decorator.attr,
                        value=AttributeTree(node=decorator),
                        line=decorator.lineno,
                    )
                )
            else:
                raise NotImplementedError
        
        return objects
