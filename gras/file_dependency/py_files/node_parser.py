import ast
import os
from gras.file_dependency.utils import lines_of_code_counter
from pprint import pprint


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
            "classes"  : [], "class_count": 0, "imports": [], "import_count": 0,
            "functions": [], "function_count": 0, "global_variable_count": 0, "global_variables": []
            }

    def visit_ClassDef(self, node):
        if node.name not in self.stats["classes"]:
            self.stats["classes"].append({
                "name"      : node.name,
                "docstring" : ast.get_docstring(node),
                # "bases"     : list(base.id for base in node.bases),
                "methods"   : [],
                "decorators": list(decorator.id for decorator in node.decorator_list)
                })
            for body in node.body:
                if isinstance(body, ast.FunctionDef) and body.name != "__init__":
                    self.stats["classes"][self.stats["class_count"]]["methods"].append({
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
                "decorators": list(decorator.id for decorator in node.decorator_list),
                "docstring" : ast.get_docstring(node)
                })
            self.stats["function_count"] += 1

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name not in self.stats["imports"]:
                self.stats["import_count"] += 1
                self.stats["imports"].append({"name": alias.name, "imported_from": None})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name not in self.stats["imports"]:
                self.stats["import_count"] += 1
                self.stats["imports"].append({"name": alias.name, "imported_from": node.module})
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


def parse_dir(project_dir):
    """
    Function to parse the project directory to generate a file dependency dictionary.

    :param project_dir: directory of the project to be parsed
    :type project_dir: str
    :return: dictionary of file dependency data
    :rtype: dict
    """
    dependency_dict = {}
    for root, dirname, files in os.walk(project_dir):
        if os.path.basename(root) != "__pycache__":
            files_in_dir = []
            for f in files:
                if f.endswith(".py") and f != "__init__.py":
                    with open(os.path.join(root, f), "r") as file:
                        analyzer = FileAnalyzer()
                        file_dict = {
                            "name"         : f"{os.path.basename(f)}",
                            "effective_loc": lines_of_code_counter(os.path.join(root, f))
                            }
                        tree = ast.parse(file.read())
                        analyzer.visit(tree)
                        file_dict["file_data"] = analyzer.gen()
                        del analyzer
                        file.close()
                        files_in_dir.append(file_dict)
            dependency_dict[f"DIR {os.path.basename(root)}"] = files_in_dir
    return dependency_dict

