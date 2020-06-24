import os
import subprocess
import shutil

from gras.base_miner import BaseMiner

ROOT = "/home/mahen/PycharmProjects/GRAS"
CACHE = os.path.join(ROOT, ".cache")


# noinspection PyMissingConstructor
class JavaMiner(BaseMiner):
    def __init__(self, args, path):
        # super().__init__(args)

        # TODO: Take from args
        self.path = path

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    def process(self):
        if os.path.exists(CACHE):
            shutil.rmtree(CACHE)
            os.makedirs(CACHE)
        else:
            os.makedirs(CACHE)

        if os.path.isfile(self.path) and ".jar" in os.path.basename(self.path):
            os.chdir(CACHE)
            subprocess.run(["jar", "xf", self.path])

            # TODO: Parse jar file
        elif os.path.isdir(self.path):
            jars = []
            for dir_name, _, filenames in os.walk(self.path):
                for f in filenames:
                    if os.path.splitext(f)[1] == ".jar":
                        jars.append(os.path.abspath(os.path.join(dir_name, f)))

            for jar in jars:
                print(f"Ongoing jar: {jar}")

                shutil.rmtree(CACHE)
                os.makedirs(CACHE)
                os.chdir(CACHE)

                print("Extracting...")
                subprocess.run(["jar", "xf", jar])
                print("Extracted Successfully!")

                break
        else:
            raise NotImplementedError


if __name__ == '__main__':
    JavaMiner(None, path="/home/mahen/elasticsearch-7.8.0/lib").process()
