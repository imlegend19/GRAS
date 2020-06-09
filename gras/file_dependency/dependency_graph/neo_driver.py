from neo4j import GraphDatabase
from gras.file_dependency.python.file_miner import PythonMiner


# driver = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "gras"), encrypted=False)


class DependencyGraph(object):
    def __init__(self, uri, user, password, model):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.model = model

    def close(self):
        self._driver.close()

    def create(self):
        with self._driver.session() as graphDB_Session:
            graphDB_Session.run(
                f"""
                CREATE ({self.model.name}: File {{
                     name: "{self.model.name}",
                     loc: {self.model.loc},
                     imports: {self.model.import_list},
                     total_classes: {self.model.total_classes},
                     total_functions: {self.model.total_functions},
                     total_variables: {self.model.total_variables},
                     total_imports: {self.model.total_imports}
                     }})
                """
                )
            for class_ in self.model.classes:
                graphDB_Session.run(
                    f"""
                    CREATE ({class_.name}: Class {{
                        name: "{class_.name}",
                        line: {class_.line},
                        docstring: "{class_.docstring}",
                        bases: {class_.argument_list},
                        decorators: {class_.decorator_list},
                        total_decorators: {class_.total_decorators},
                        total_classes: {class_.total_classes},
                        total_functions: {class_.total_functions},
                        total_variables: {class_.total_variables},
                        total_imports: {class_.total_imports}
                    }})
                    """
                    )
                if class_.total_imports > 0:
                    for import_ in class_.imports:
                        graphDB_Session.run(
                            f"""
                            CREATE ({import_.name}: Import {{
                                name: "{import_.name}",
                                line: {import_.line},
                                module: {import_.module},
                                as_name: {import_.as_name}
                            }})
                            """
                            )


fl = PythonMiner(args=None, project_dir="/home/viper/dev/GRAS/gras/file_dependency", file_path=None).process()
Driver = DependencyGraph(uri="bolt://localhost:7687", user="neo4j", password="gras", model=fl)
Driver.create()
Driver.close()
