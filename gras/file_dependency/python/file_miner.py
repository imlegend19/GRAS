import ast
import os

from gras.base_miner import BaseMiner
from gras.file_dependency.python.models import FileModel, ProjectModel
from gras.file_dependency.python.node_parser import FileAnalyzer
from gras.file_dependency.utils import is_python_file, lines_of_code_counter


class FileMiner(BaseMiner):
    # noinspection PyMissingConstructor
    def __init__(self, args, project_dir, file_path):
        # super().__init__(args=args)
        
        # TODO: Add the following arguments in ArgumentParser
        
        self.project_dir = project_dir
        self.file_path = file_path

        if self.file_path:
            with open(file_path, "r") as fp:
                content = fp.read()
                path = fp.name

            obj = self.parse_file(content=content, path=path)
            print(obj.variables)

        if self.project_dir:
            obj = self.parse_dir()
            print(obj)
    
    def _load_from_file(self, file):
        pass
    
    def dump_to_file(self, path):
        pass

    @staticmethod
    def parse_file(content, path):
        name = os.path.basename(path)
        loc = lines_of_code_counter(content.split("\n"))
    
        analyzer = FileAnalyzer()
        tree = ast.parse(content)
        analyzer.visit(tree)
    
        file_stats = analyzer.process()
        del analyzer
    
        file = FileModel(
            name=name,
            loc=loc,
            classes=file_stats["classes"],
            functions=file_stats["functions"],
            variables=file_stats["variables"],
            imports=file_stats["imports"]
        )
    
        return file
    
    def parse_dir(self):
        """
        Function to parse the project directory to generate a file dependency dictionary.

        :return: dictionary of file dependency data
        :rtype: dict
        """
        project = None
        for root, dirname, files in os.walk(self.project_dir):
            if os.path.basename(root) != "__pycache__":
                files_in_dir = []
                for file in files:
                    if is_python_file(os.path.join(root, file)) and file != "__init__.py":
                        with open(os.path.join(root, file), "r") as fp:
                            content = fp.read()
                
                        file_object = self.parse_file(content=content, path=fp.name)
                        files_in_dir.append(file_object)
        
                project = ProjectModel(
                    name=os.path.basename(root),
                    total_loc=sum([x.loc for x in files_in_dir]),
                    total_files=len(files_in_dir),
                    total_classes=sum([x.total_classes for x in files_in_dir]),
                    total_functions=sum([x.total_functions for x in files_in_dir]),
                    total_global_variables=0,
                    files=files_in_dir
                )

        return project

    def process(self):
        pass


if __name__ == '__main__':
    FileMiner(args=None, project_dir=None, file_path="/home/mahen/PycharmProjects/GRAS/tests/data/test_defs.py")
