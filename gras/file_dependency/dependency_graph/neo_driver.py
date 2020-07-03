import json

from neo4j import GraphDatabase

from gras.file_dependency.python.file_miner import PythonMiner


class DependencyGraph(object):
    def __init__(self, uri, user, password, model):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.model = model
        self.session = self._driver.session()

    def _create_import_node(self, import_node, parent_node):
        run = f"""
            CREATE ({import_node.name}: Import {{
                name: "{import_node.name}",
                module: "{import_node.module}",
                as_name: "{import_node.as_name}",
                line: "{import_node.lineno}"
            }})
            WITH {import_node.name}
            MATCH (p: {parent_node.label}{{name: "
{parent_node.name[:-3] if parent_node.label == 'File' else parent_node.name}"}})                    
            CREATE ({import_node.name})<-[:IMPORTS]-(p)
        """
        print('import', run)

        self.session.run(
            run
        )

    def _create_var_node(self, var_node, parent_node):
        run = f"""
            CREATE ({var_node.name}: Variable {{
                name: "{var_node.name}",
                scope: "{var_node.scope}"
            }})
            WITH {var_node.name}
            MATCH (p: {parent_node.label}{{name: "{parent_node.name[:-3] if parent_node.label == 'File' else parent_node.name}"}})                    
            CREATE ({var_node.name})-[:IS_VARIABLE_OF]->(p)
            """
        print(run)

        self.session.run(
            run
        )

    def _create_decorator_node(self, decorator_node, parent_node):
        run = f"""
            CREATE ({decorator_node.name}: Decorator {{
                name: "{decorator_node.name}",
                value: "{decorator_node.value}",
                line: "{decorator_node.lineno}"
            }})
            WITH {decorator_node.name}
            MATCH (p: {parent_node.label}{{name: "{parent_node.name}"}})                    
            CREATE ({decorator_node.name})-[:IS_DECORATOR_OF]->(p)
        """
        print('dec', run)

        self.session.run(
            run
        )

    def _create_func_node(self, func_node, parent_node):
        # removed -> decorators: {func_node.decorator_list},
        run = f"""
            CREATE ({func_node.name}: Function {{
                name: "{func_node.name}",
                line: {func_node.lineno},
                docstring: {f'"{func_node.docstring}"' if func_node.docstring is not None else "null"},
                bases: {json.dumps(func_node.argument_list)}
            }})
            WITH {func_node.name}
            MATCH (p: {parent_node.label}{{name: "{parent_node.name[:-3] if parent_node.label == 'File' else parent_node.name}"}})                   
            CREATE ({func_node.name})-[:IS_FUNCTION_OF]->(p)
        """
        print('func', run)
        self.session.run(
            run
        )

        if func_node.decorators:
            for dec_node in func_node.decorators:
                self._create_decorator_node(decorator_node=dec_node, parent_node=func_node)

        if func_node.imports:
            for import_node in func_node.imports:
                self._create_import_node(import_node=import_node, parent_node=func_node)

        if func_node.variables:
            for var_node in func_node.variables:
                self._create_var_node(var_node=var_node, parent_node=func_node)

        if func_node.classes:
            for class_node in func_node.classes:
                self._create_class_node(class_node=class_node, parent_node=func_node)

        if func_node.functions:
            for func_node_ in func_node.functions:
                self._create_func_node(func_node=func_node_, parent_node=func_node)

    def _create_class_node(self, class_node, parent_node):
        run = f"""
            CREATE ({class_node.name}: Class {{
                name: "{class_node.name}",
                line: {class_node.lineno},
                docstring: {f'"{class_node.docstring}"' if class_node.docstring is not None else "null"},
                bases: {class_node.argument_list}
            }})
            WITH {class_node.name}
            MATCH (p: {parent_node.label}{{name: "{parent_node.name[:-3] if parent_node.label == 'File' else parent_node.name}"}})                    
            CREATE ({class_node.name})-[:IS_CLASS_OF]->(p)
        """
        print('class', run)
        self.session.run(
            run
        )

        if class_node.decorators:
            for dec_node in class_node.decorators:
                self._create_decorator_node(decorator_node=dec_node, parent_node=class_node)

        if class_node.variables:
            for var_node in class_node.variables:
                self._create_var_node(var_node=var_node, parent_node=class_node)

        if class_node.imports:
            for import_node in class_node.imports:
                self._create_import_node(import_node=import_node, parent_node=class_node)

        if class_node.functions:
            for func_node in class_node.functions:
                self._create_func_node(func_node=func_node, parent_node=class_node)

        if class_node.classes:
            for class_node_ in class_node.classes:
                self._create_class_node(class_node=class_node_, parent_node=class_node)

    def _create_file_node(self, file, parent_node=None):
        if parent_node is None:
            run = f"""
                CREATE ({file.name[-3]}:File{{
                    name: "{file.name[:-3]}",
                    loc: {file.loc},
                    imports: {file.import_list if file.import_list else "null"},
                    total_classes: {file.total_classes},
                    total_functions: {file.total_functions},
                    total_variables: {file.total_variables},
                    total_imports: {file.total_imports}
                    }})
            """
        else:
            run = (f"""
                CREATE ({file.name[:-3]}:File{{
                    name: "{file.name[:-3]}",
                    loc: {file.loc},
                    imports: {file.import_list if file.import_list else "null"},
                    total_classes: {file.total_classes},
                    total_functions: {file.total_functions},
                    total_variables: {file.total_variables},
                    total_imports: {file.total_imports}
                    }})
                WITH {file.name[:-3]}
                MATCH (p: {parent_node.label}{{name: "{parent_node.name}"}})                    
                CREATE ({file.name[:-3]})-[:IS_FILE_OF]->(p)
                """
                   )

        self.session.run(run)

        if file.imports:
            for import_node in file.imports:
                self._create_import_node(import_node=import_node, parent_node=file)

        if file.variables:
            for var_node in file.variables:
                try:
                    self._create_var_node(var_node=var_node)
                except Exception:
                    print(var_node.name, var_node.scope)

        if file.functions:
            for func_node in file.functions:
                self._create_func_node(func_node=func_node, parent_node=file)

        if file.classes:
            for class_node in file.classes:
                self._create_class_node(class_node=class_node, parent_node=file)

    def _create_directory_node(self, dir_node, parent_node=None):
        if parent_node is None:
            run = f"""
                     CREATE ({dir_node.name}:Directory{{
                            name: "{dir_node.name}"
                        }})        
                    """
        else:
            run = f"""
                CREATE ({dir_node.name}:Directory{{
                    name: "{dir_node.name}"
                    }})
                WITH {dir_node.name}
                MATCH (p: {parent_node.label}{{name: "{parent_node.name}"}})                    
                CREATE ({dir_node.name})-[:IS_DIRECTORY_OF]->(p)
            """
        self.session.run(
            run
        )

        if dir_node.files:
            for file_node in dir_node.files:
                self._create_file_node(file=file_node, parent_node=dir_node)

        if dir_node.directories:
            for dir_node_ in dir_node.directories:
                self._create_directory_node(dir_node=dir_node_, parent_node=dir_node)

    def process(self):
        self._create_directory_node(dir_node=self.model)

    def __del__(self):
        self.session.close()
        self._driver.close()


if __name__ == '__main__':
    # fl = PythonMiner(args=None, project_dir="/home/viper/dev/GRAS/tests/deptest",
    #                  file_path=None).process()
    fl = PythonMiner(args=None, project_dir="/home/viper/dev/GRAS/gras/file_dependency/dependency_graph",
                     file_path=None).process()

    Driver = DependencyGraph(uri="bolt://localhost:7687", user="neo4j", password="gras", model=fl)
    Driver.process()
    Driver.__del__()
