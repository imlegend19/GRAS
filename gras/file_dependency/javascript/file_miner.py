import json
import subprocess

from gras.base_miner import BaseMiner
from gras.file_dependency.javascript.models import FunctionModel, VariableModel


class JavascriptMiner(BaseMiner):
    # noinspection PyMissingConstructor
    def __init__(self, args, project_dir, file_path):
        # super().__init__(args=args)

        self.project_dir = project_dir
        self.file_path = file_path

        self._init_npm()

        if self.file_path:
            self.parse_file(path=file_path)

    @staticmethod
    def _init_npm():
        # TODO: Check whether npm is present or not
        subprocess.run(['npm', 'install'])

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path, content):
        with open(path, 'w') as fp:
            fp.write(json.dumps(content, indent=4))

    @staticmethod
    def parse_file(path):
        out = subprocess.run(['node', 'esprima-parser.js', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ast = json.loads(out.stdout.decode('utf-8'))

        variables = []
        functions = []

        for i in ast['body']:
            if i['type'] == 'FunctionDeclaration':
                name = i['id']['name']
                temp = []
                for p in i['params']:
                    temp.append(p['name'])
                functions.append(FunctionModel(name=name, params=temp))

            if i['type'] == 'VariableDeclaration' and i['declarations'][0]['init']['type'] != 'ArrowFunctionExpression':
                name = i['declarations'][0]['id']['name']
                kind = i['declarations'][0]['init']['type']
                variables.append(VariableModel(name=name, kind=kind))
            elif i['type'] == 'VariableDeclaration' and \
                    i['declarations'][0]['init']['type'] == "ArrowFunctionExpression":
                name = i['declarations'][0]['id']['name']
                temp = []
                for p in i['declarations'][0]['init']['params']:
                    temp.append(p['name'])
                functions.append(FunctionModel(name=name, params=temp))

        print('=== Printing Variables ===')
        for i in variables:
            print(i.name)
            print(i.kind)

        print('=== Printing Functions ===')
        for i in functions:
            print(i.name)
            for p in i.params:
                print(p)

    def process(self):
        pass


if __name__ == '__main__':
    JavascriptMiner(args=None, project_dir=None, file_path="/home/mahen/PycharmProjects/GRAS/tests/data/test.js")
