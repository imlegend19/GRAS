import ast
import os

from gras.base_miner import BaseMiner
from gras.file_dependency.python.models import DirectoryModel, FileModel
from gras.file_dependency.python.node_parser import FileAnalyzer
from gras.file_dependency.utils import is_python_file, lines_of_code_counter


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

            self.obj = self.parse_file(content=content, path=path)

        if self.project_dir:
            self.obj = self.project_walker(self.project_dir)
            # self._print(obj=self.obj)

    def _print(self, obj):
        print("\n")
        print("dir: ", obj.name)
        if obj.files:
            for file in obj.files:
                print(file.name)
        if bool(obj.directories):
            for d in obj.directories:
                self._print(d)

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    @staticmethod
    def parse_file(content, path):
        name = os.path.basename(path)
        loc = lines_of_code_counter(content.split("\n"))

        analyzer = FileAnalyzer(file_name=path)
        tree = ast.parse(content)
        analyzer.visit(tree)

        file_stats = analyzer.process()
        del analyzer

        file = FileModel(
            name=name,
            loc=loc,
            classes=file_stats["classes"],
            functions=file_stats["functions"],
            variables=file_stats["all_variables"],
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
        file_models = []
        for file_path in files:
            if os.path.basename(file_path) != '__pycache__' and is_python_file(file_path):
                with open(file_path, "r") as fp:
                    content = fp.read()
                    file_obj = self.parse_file(content=content, path=fp.name)
                    file_models.append(file_obj)
                    fp.close()

        model = DirectoryModel(
            name=os.path.basename(path),
            files=file_models,
            directories=[
                self.project_walker(dir_path) for dir_path in directories
            ],
            total_loc=[sum(file_.loc for file_ in file_models)],
            total_files=len(file_models),
            total_classes=0,
            total_functions=0,
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
        return self.obj


if __name__ == '__main__':
    obj = PythonMiner(args=None, project_dir=None,
                      file_path="/home/mahen/PycharmProjects/GRAS/gras/file_dependency/python/node_parser.py").process()
