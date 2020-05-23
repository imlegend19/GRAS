import ast
import os

from gras.base_miner import BaseMiner
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
            
            dic = self.parse_file(content=content, path=path)
            
            from pprint import pprint
            
            pprint(dic, width=300)
    
    def _load_from_file(self, file):
        pass
    
    def dump_to_file(self, path):
        pass
    
    @staticmethod
    def parse_file(content, path):
        analyzer = FileAnalyzer()
        file_dict = {
            "name"         : f"{os.path.basename(path)}",
            "effective_loc": lines_of_code_counter(content.split("\n"))
        }
        
        tree = ast.parse(content)
        analyzer.visit(tree)
        file_dict["file_data"] = analyzer.gen()
        del analyzer
        
        return file_dict
    
    def parse_dir(self):
        """
        Function to parse the project directory to generate a file dependency dictionary.

        :return: dictionary of file dependency data
        :rtype: dict
        """
        dependency_dict = {}
        for root, dirname, files in os.walk(self.project_dir):
            if os.path.basename(root) != "__pycache__":
                files_in_dir = []
                for file in files:
                    if is_python_file(os.path.join(root, file)) and file != "__init__.py":
                        with open(os.path.join(root, file), "r") as fp:
                            content = fp.read()
                        
                        file_dict = self.parse_file(content=content, path=fp.name)
                        files_in_dir.append(file_dict)
                
                dependency_dict[f"DIR {os.path.basename(root)}"] = files_in_dir
        
        return dependency_dict
    
    def process(self):
        pass
