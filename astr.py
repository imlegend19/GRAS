import ast
from pprint import pprint

with open("local_settings.py", "r") as source:
    tree = ast.parse(source.read())

# def read_initial_comment(tree):
#     tree = ast.dump(tree)
#     comment = Module()

v = ast.dump(tree)


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.import_count = 0
        self.var_count = 0
        self.class_count = 0
        self.stats = {
            "imports"    : [], "import_count": self.import_count
            , "var_count": self.var_count, "vars": [], "class_count": self.class_count, "classes": []
            }


    # def visit_Assign(self, node):
    #     for alias in node.targets:
    #         if isinstance(alias, ast.Name):
    #             self.stats["vars"].append(alias.id)
    #             if alias.id not in self.stats["vars"]:
    #                 self.stats["var_count"] += 1
    #         elif isinstance(alias, ast.Attribute):
    #             if alias.value.id != 'self':
    #                 self.stats["vars"].append(alias.value.id)
    #                 if alias.value.id not in self.stats["vars"]:
    #                     self.stats["var_count"] += 1
    #         elif isinstance(alias, ast.Subscript):
    #             if isinstance(alias.value, ast.Attribute):
    #                 if alias.value.value.id != 'self':
    #                     self.stats["vars"].append(alias.value.value.id)
    #             else:
    #                 self.stats["vars"].append(alias.value.id)
    #     self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.stats["class_count"] += 1
        self.stats["classes"].append(node.name)

    def visit_Import(self, node):
        for alias in node.names:
            self.stats["import_count"] += 1
            self.stats["imports"].append({"name": alias.name, "imported_from": None})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["import_count"] += 1
            self.stats["imports"].append({"name": alias.name, "imported_from": node.module})
        self.generic_visit(node)

    def report(self):
        pprint(self.stats)


# i = 0
# for node in tree.body:
#     if i == 10:
#         pprint(type(node))
#         pprint(dir(node))
#         # for n in node.names:
#         #     pprint(n.name)
#         # pprint(node.value.s)
#     i += 1

analyzer = Analyzer()
analyzer.visit(tree)
analyzer.report()
