import json
import subprocess

from gras.base_miner import BaseMiner


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
        
        # TODO: Parse ast
    
    def process(self):
        pass
