from gras.file_dependency.utils import lines_of_code_counter
from gras.file_dependency.py_files.py_dependency_models import ProjectStatsModel, FileStatsModel
import ast
import os

#TODO: have one big analyzer module, first implementation is very sloppy
class ProjectAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.import_count = 0
        self.var_count = 0
        self.class_count = 0
        self.stats = {
            "imports"    : [], "import_count": self.import_count
            , "var_count": self.var_count, "vars": [], "class_count": self.class_count, "classes": []
            }

    def visit_ClassDef(self, node):
        if node.name not in self.stats["classes"]:
            self.stats["class_count"] += 1
            self.stats["classes"].append(node.name)

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

    def gen(self):
        return self.stats
    # TODO: var_count seems unnecessary for stats


class ProjectStats(ProjectStatsModel, ProjectAnalyzer):
    """
    The object models the project statistics data and generates a :class:`ProjectStatsModel`

    :param path: path of the project root directory
    :type path: str
    """

    def __init__(self, root):
        """Constructor Method"""
        self.dic = {}
        self.root = root

    def __parse__(self):
        ret = lines_of_code_counter(self.root)
        self.dic["file_count"] = len(ret[0])
        self.dic["total_loc"] = ret[1][0]
        self.dic["class_count"] = 0
        self.dic["dependency_count"] = 0
        for root, _, files in os.walk(self.root):
            for f in files:
                if f.endswith(".py"):
                    with open(os.path.join(root, f), "r") as file:
                        tree = ast.parse(file.read())
                        a = ProjectAnalyzer()
                        a.visit(tree)
                        self.dic["class_count"] += a.gen()["class_count"]
                        self.dic["dependency_count"] += a.gen()["import_count"]
                    file.close()

    def generate(self):
        self.__parse__()
        return self.object_decoder(self.dic)

a = ProjectStats('/home/viper/dev/GRAS/').generate()
print("total lines of code: ", a.total_loc, "file count: ", a.file_count, "class count: ", a.class_count)