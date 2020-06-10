import json

from neo4j import GraphDatabase

from gras.file_dependency.python.file_miner import PythonMiner


class DependencyGraph(object):
    def __init__(self, uri, user, password, model):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.model = model
        self.session = self._driver.session()

    def _create_import_node(self, import_node):
        run = f"""
            CREATE ({import_node.name}: Import {{
                name: "{import_node.name}",
                module: "{import_node.module}",
                as_name: "{import_node.as_name}",
                line: "{import_node.line}"
            }})
        """
        print('import', run)

        self.session.run(
            run
        )

    def _create_var_node(self, var_node):
        run = f"""
            CREATE ({var_node.name}: Variable {{
                name: "{var_node.name}",
                scope: "{var_node.scope}"
            }})
            """
        print(run)

        self.session.run(
            run
        )

    def _create_decorator_node(self, decorator_node):
        run = f"""
            CREATE ({decorator_node.name}: Decorator {{
                name: "{decorator_node.name}",
                subtype: "{decorator_node.subtype}"
                value: "{decorator_node.value}",
                line: "{decorator_node.line}"
            }})
        """
        print('dec', run)

        self.session.run(
            run
        )

    def _create_func_node(self, func_node):
        # removed -> decorators: {func_node.decorator_list},
        run = f"""
            CREATE ({func_node.name}: Function {{
                name: "{func_node.name}",
                line: {func_node.line},
                docstring: {f'"{func_node.docstring}"' if func_node.docstring is not None else "null"},
                bases: {json.dumps(func_node.argument_list)},
                total_decorators: {func_node.total_decorators},
                total_classes: {func_node.total_classes},
                total_functions: {func_node.total_functions},
                total_variables: {func_node.total_variables},
                total_imports: {func_node.total_imports}
            }})
        """
        print('func', run)
        self.session.run(
            run
        )

        if func_node.decorators:
            for dec_node in func_node.decorators:
                self._create_decorator_node(decorator_node=dec_node)

        if func_node.variables:
            for var_node in func_node.variables:
                self._create_var_node(var_node=var_node)

        if func_node.classes:
            for class_node in func_node.classes:
                self._create_class_node(class_node=class_node)

        if func_node.functions:
            for func_node in func_node.functions:
                self._create_func_node(func_node=func_node)

        if func_node.imports:
            for import_node in func_node.imports:
                self._create_import_node(import_node=import_node)

    def _create_class_node(self, class_node):
        run = f"""
            CREATE ({class_node.name}: Class {{
                name: "{class_node.name}",
                line: {class_node.line},
                docstring: "{class_node.docstring}",
                bases: {class_node.argument_list},
                decorators: {class_node.decorator_list},
                total_decorators: {class_node.total_decorators},
                total_classes: {class_node.total_classes},
                total_functions: {class_node.total_functions},
                total_variables: {class_node.total_variables},
                total_imports: {class_node.total_imports}
            }})
        """
        print('class', run)
        self.session.run(
            run
        )

        if class_node.decorators:
            for dec_node in class_node.decorators:
                self._create_decorator_node(decorator_node=dec_node)

        if class_node.functions:
            for func_node in class_node.functions:
                self._create_func_node(func_node=func_node)

        if class_node.variables:
            for var_node in class_node.variables:
                self._create_var_node(var_node=var_node)

        if class_node.imports:
            for import_node in class_node.imports:
                self._create_import_node(import_node=import_node)

        if class_node.classes:
            for class_node in class_node.classes:
                self._create_class_node(class_node=class_node)

    def _create_file_node(self, file):
        run = f"""
            CREATE ({file.name[:-3]}: File {{
                name: "{file.name}",
                loc: {file.loc},
                imports: {file.import_list},
                total_classes: {file.total_classes},
                total_functions: {file.total_functions},
                total_variables: {file.total_variables},
                total_imports: {file.total_imports}
            }})
        """
        print('file', run)

        self.session.run(
            run
        )

        if file.classes:
            for class_node in file.classes:
                self._create_class_node(class_node=class_node)

        if file.imports:
            for import_node in file.imports:
                self._create_import_node(import_node=import_node)

        if file.variables:
            for var_node in file.variables:
                try:
                    self._create_var_node(var_node=var_node)
                except Exception:
                    print(var_node.name, var_node.scope)

        if file.functions:
            for func_node in file.functions:
                self._create_func_node(func_node=func_node)

    def _create_directory_node(self, dir_node):
        self.session.run(
            f"""
            CREATE ({dir_node.name}: Directory {{
                name: "{dir_node.name}"
            }})
            """
        )

        if dir_node.files:
            for file_node in dir_node.files:
                self._create_file_node(file=file_node)

        if dir_node.directories:
            for dir_node in dir_node.directories:
                self._create_directory_node(dir_node=dir_node)

    def process(self):
        self._create_directory_node(dir_node=self.model)

    def __del__(self):
        self.session.close()
        self._driver.close()


if __name__ == '__main__':
    fl = PythonMiner(args=None, project_dir="/home/mahen/PycharmProjects/GRAS/gras/file_dependency/python",
                     file_path=None).process()

    Driver = DependencyGraph(uri="bolt://localhost:7687", user="neo4j", password="gras", model=fl)
    Driver.process()
