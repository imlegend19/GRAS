import ast
import os

from gras.base_miner import BaseMiner
from gras.file_dependency.python.models import FileModel, DirectoryModel
from gras.file_dependency.python.node_parser import FileAnalyzer
from gras.file_dependency.utils import lines_of_code_counter


class PythonMiner(BaseMiner):
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
            obj = self.project_walker(self.project_dir)
            print(obj)

    def load_from_file(self, file):
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

    @staticmethod
    def parse_directory(path):
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        directories = [os.path.join(path, d) for d in os.listdir(path)
                       if os.path.isdir(os.path.join(path, d)) and d != '__pycache__']

        return files, directories

    def project_walker(self, path):
        """
        Function to parse the project directory to generate a file dependency dictionary.

        :return: dictionary of file dependency data
        :rtype: dict
        """
        files, directories = self.parse_directory(path)

        model = DirectoryModel(
            name=os.path.basename(path),
            files=[
                _ for _ in files  # TODO: Added FileModel object
            ],
            directories=[
                self.project_walker(dir_path) for dir_path in directories
            ],
            total_loc=None,
            total_files=None,
            total_classes=None,
            total_functions=None,
            total_global_variables=0,
        )

        # TODO: Refer the previous implementation to init the values for other parameters

        return model

        # for root, dirname, files in os.walk(self.project_dir):
        #     if os.path.basename(root) != "__pycache__":
        #         files_in_dir = []
        #         for file in files:
        #             if is_python_file(os.path.join(root, file)) and file != "__init__.py":
        #                 with open(os.path.join(root, file), "r") as fp:
        #                     content = fp.read()
        #
        #                 file_object = self.parse_file(content=content, path=fp.name)
        #                 files_in_dir.append(file_object)
        #
        #         project = ProjectModel(
        #             name=os.path.basename(root),
        #             total_loc=sum([x.loc for x in files_in_dir]),
        #             total_files=len(files_in_dir),
        #             total_classes=sum([x.total_classes for x in files_in_dir]),
        #             total_functions=sum([x.total_functions for x in files_in_dir]),
        #             total_global_variables=0,
        #             files=files_in_dir
        #         )

    def process(self):
        pass


if __name__ == '__main__':
    PythonMiner(args=None, project_dir="/home/mahen/PycharmProjects/GRAS/gras/file_dependency", file_path=None)
