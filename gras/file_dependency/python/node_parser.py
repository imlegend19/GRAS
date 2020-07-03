import ast
import logging
import os
from ast import (
    Attribute, Call, ClassDef, FunctionDef, Global, Import, ImportFrom, Name, Nonlocal, arguments,
)

from gras.file_dependency.python.models import (
    ArgModel, AttributeModel, CallModel, DecoratorModel, DefModel, FileModel, ImportModel, VariableModel,
)
from gras.file_dependency.python.node_types import Arg, Base, Class, Function, Kwarg
from gras.file_dependency.utils import lines_of_code_counter

logger = logging.getLogger("main")


class NodeParser(ast.NodeVisitor):
    def __init__(self, node, subtype=None):
        self.node = node
        self.subtype = subtype

        self.base_type = node.__class__.__name__
        self.value = None

        self.visit(node)

    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__

        try:
            visitor = getattr(self, method)
            return visitor(node)
        except AttributeError:
            logger.error(f"Not Implemented: visit_{self.base_type}")

    def __parse_decorators(self, lst):
        objects = []

        for decorator in lst:
            value = NodeParser(decorator).value

            if isinstance(value, str):
                name = value
                value = None
            elif isinstance(decorator, Call):
                if isinstance(decorator.func, Attribute):
                    name = decorator.func.attr
                else:
                    name = decorator.func.id
            elif isinstance(decorator, Attribute):
                name = decorator.attr
            else:
                raise NotImplementedError

            objects.append(
                DecoratorModel(
                    lineno=decorator.lineno,
                    name=name,
                    value=value
                )
            )

        return objects

    def visit_arg(self, node):
        self.value = ArgModel(
            subtype=self.subtype,
            name=node.arg,
            value=None,
            lineno=node.lineno,
            annotation=node.annotation.id if node.annotation else None
        )

    def visit_arguments(self, node: arguments):
        self.value = []

        if node.args:
            for arg in node.args:
                self.value.append(NodeParser(arg, subtype=Arg).value)

        if node.kwonlyargs:
            for arg in node.kwonlyargs:
                self.value.append(NodeParser(arg, subtype=Kwarg).value)

        if node.kwarg:
            self.value.append(NodeParser(node.kwarg, subtype=Kwarg).value)

        if node.vararg:
            self.value.append(NodeParser(node.vararg, subtype=Arg).value)

    def visit_keyword(self, node):
        self.value = ArgModel(
            subtype=Class,
            name=node.arg,
            value=NodeParser(node.value).value,
            annotation=None,
            lineno=node.value.lineno
        )

    def visit_Import(self, node: Import):
        self.value = [
            ImportModel(
                name=alias.name,
                as_name=alias.asname,
                lineno=node.lineno
            ) for alias in node.names
        ]

    def visit_ImportFrom(self, node: ImportFrom):
        self.value = [
            ImportModel(
                module=node.module,
                name=alias.name,
                as_name=alias.asname,
                lineno=node.lineno
            ) for alias in node.names
        ]

    def visit_Global(self, node: Global):
        self.value = [
            VariableModel(
                subtype=Global,
                name=nm
            ) for nm in node.names
        ]

    def visit_Nonlocal(self, node: Nonlocal):
        self.value = [
            VariableModel(
                subtype=Nonlocal,
                name=nm
            ) for nm in node.names
        ]

    def visit_Name(self, node: Name):
        self.value = node.id

    def visit_Call(self, node: Call):
        self.value = CallModel(
            lineno=node.lineno,
            func=NodeParser(node.func).value
        )

    def visit_Attribute(self, node: Attribute):
        self.value = AttributeModel(
            name=node.attr,
            lineno=node.lineno,
            value=NodeParser(node.value).value
        )

    def visit_ClassDef(self, node: ClassDef):
        classes, functions, imports, variables = [], [], [], []

        args = []
        for base in node.bases:
            if isinstance(base, Name):
                name = node.name
                base = None
            elif isinstance(base, Attribute):
                name = base.attr
            elif isinstance(base, Call):
                name = base.func.attr
            else:
                raise NotImplementedError

            args.append(
                ArgModel(
                    subtype=Base,
                    name=name,
                    value=NodeParser(base).value if base else None,
                    lineno=node.lineno,
                    annotation=None
                )
            )

        for obj in node.body:
            value = NodeParser(obj).value

            if not value:
                continue

            if isinstance(value, list):
                if isinstance(value[0], ImportModel):
                    imports.extend(value)
                elif isinstance(value[0], VariableModel):
                    variables.extend(value)
            elif isinstance(value, DefModel) and value.subtype.__name__ == 'Function':
                functions.append(value)
            elif isinstance(value, DefModel) and value.subtype.__name__ == 'Class':
                classes.append(value)
            elif isinstance(value, VariableModel):
                variables.append(value)
            else:
                logger.error(f"{type(obj)}: Not Implemented")

        self.value = DefModel(
            subtype=Class,
            name=node.name,
            lineno=node.lineno,
            decorators=self.__parse_decorators(node.decorator_list),
            docstring=ast.get_docstring(node),
            arguments=args,
            classes=classes,
            functions=functions,
            imports=imports,
            variables=variables
        )

    def visit_FunctionDef(self, node: FunctionDef):
        classes, functions, imports, variables = [], [], [], []

        for obj in node.body:
            value = NodeParser(obj).value

            if not value:
                continue

            if isinstance(value, list):
                if isinstance(value[0], ImportModel):
                    imports.extend(value)
                elif isinstance(value[0], VariableModel):
                    variables.extend(value)
            elif isinstance(value, DefModel) and value.subtype.__name__ == 'Function':
                functions.append(value)
            elif isinstance(value, DefModel) and value.subtype.__name__ == 'Class':
                classes.append(value)
            elif isinstance(value, VariableModel):
                variables.append(value)
            else:
                logger.error(f"{type(obj)}: Not Implemented")

        self.value = DefModel(
            subtype=self.subtype if self.subtype else Function,
            name=node.name,
            lineno=node.lineno,
            decorators=self.__parse_decorators(node.decorator_list),
            docstring=ast.get_docstring(node),
            arguments=NodeParser(node.args).value,
            classes=classes,
            functions=functions,
            imports=imports,
            variables=variables
        )


class FileAnalyzer:
    """
    `NodeVisitor` class that visits specifics Nodes in an abstract syntax tree and generates a dictionary.
    For more information,see `ast.NodeVisitor`_

    .. _ast.NodeVisitor :
        https://docs.python.org/3/library/ast.html#ast.NodeVisitor
    """

    def __init__(self, file_path):
        """Constructor Method"""

        self.file_path = file_path

        with open(file_path, "r") as fp:
            self.content = fp.read()

        self.loc = lines_of_code_counter(self.content.split("\n"))

    def process(self):
        classes, functions, variables, imports = [], [], [], []

        tree = ast.parse(self.content)
        for child in tree.body:
            value = NodeParser(child).value

            if isinstance(value, DefModel):
                if value.subtype.__name__ == 'Class':
                    classes.append(value)
                else:
                    functions.append(value)
            elif isinstance(value, list):
                if isinstance(value[0], VariableModel):
                    variables.extend(value)
                elif isinstance(value[0], ImportModel):
                    imports.extend(value)
            elif isinstance(value, VariableModel):
                variables.append(value)
            elif isinstance(value, ImportModel):
                imports.append(value)

        return FileModel(
            name=os.path.basename(self.file_path),
            path=self.file_path,
            loc=self.loc,
            classes=classes,
            functions=functions,
            variables=variables,
            imports=imports,
        )


if __name__ == '__main__':
    f = FileAnalyzer(file_path="/home/viper/dev/GRAS/gras/file_dependency/dependency_graph/neo_driver.py").process()
    print(f)
