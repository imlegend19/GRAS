from argparse import Namespace
from datetime import datetime
from os import listdir
from os.path import isfile, join

from gras.base_miner import BaseMiner
from gras.pipermail.downloader import Downloader

BUGS_URL = "bugs.python.org"


class CPythonMiner(BaseMiner):
    def __init__(self, args, url, path):
        try:
            super().__init__(args=args)
        except AttributeError:
            pass
        
        self.url = url
        self.path = path
        
        self.files = [f for f in listdir(self.path) if isfile(join(self.path, f))]
        self.files.sort(key=lambda x: datetime.strptime(x.split('.')[0], "%Y-%B"))
        
        self.process()
    
    def load_from_file(self, file):
        pass
    
    def dump_to_file(self, path):
        pass
    
    def download_files(self):
        downloader = Downloader(url=self.url, path=self.path)
        downloader.process()
    
    @staticmethod
    def _parse(path):
        issues = {}
        
        with open(path, "r") as fp:
            obj = {}
            toggle = False
            message = []
            
            for line in fp.readlines():
                if not toggle:
                    if BUGS_URL in line and "http://" not in line:
                        continue
                    elif "http://" + BUGS_URL in line:
                        value = line[line.find("<") + 1:line.find(">")]
                        obj["number"] = int(value.split("issue")[-1])
                        issues[value.strip()] = obj.copy()
                        
                        obj.clear()
                        message.clear()
                    elif "New submission from" in line:
                        value = line.split("New submission from")[1]
                        if '<' in line:
                            obj["author_email"] = value[value.find("<") + 1:value.find(">")].strip()
                        else:
                            obj["author_email"] = None
                        
                        toggle = True
                    elif ":" in line:
                        temp = line.split(":", maxsplit=1)
                        key, value = temp[0].strip().lower(), temp[1].strip()
                        
                        if key == "from":
                            key = "author"
                            value = value[value.find("(") + 1:value.find(")")].strip()
                        elif key == "date":
                            try:
                                value = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %z")
                            except ValueError:
                                value = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S")
                        elif key == "subject":
                            value = value.split("[New-bugs-announce]")[1].strip()
                        elif key in ["nosy", "files", "components", "versions", "keywords"]:
                            value = value.split(",")
                        elif key in ["severity", "priority", "status", "title", "type", "assignee", "message-id"]:
                            value = value.strip()
                        else:
                            print(key)
                            continue
                        
                        obj[key] = value
                    else:
                        continue
                else:
                    if "----------" in line:
                        obj["message"] = "\n".join(message)
                        toggle = False
                    else:
                        message.append(line.strip())
        
        return issues
    
    def process(self):
        from pprint import pprint
        
        for f in self.files:
            issues = self._parse(join(self.path, f))
            for iss in issues:
                pprint(issues[iss])
            
            break


if __name__ == '__main__':
    CPythonMiner(args=Namespace(), url=None, path="/home/mahen/PycharmProjects/GRAS/custom_miners/cpython/data")
