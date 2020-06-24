import os
import subprocess
import shutil

from gras.base_miner import BaseMiner
from gras.errors import GrasError

ROOT = "/home/mahen/PycharmProjects/GRAS"
CACHE = os.path.join(ROOT, ".cache")
DECOMPILER = os.path.join(ROOT, "gras/file_dependency/java/decompiler/cfr.jar")


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

    def parse_file(self, file):
        file_name = os.path.basename(os.path.relpath(file, CACHE))
        package = os.path.dirname(os.path.relpath(file, CACHE))

        with open(file) as fp:
            content = fp.read()

    def parse_jar(self, jar):
        shutil.rmtree(CACHE)
        os.makedirs(CACHE)

        print("Extracting...")

        # extensions = ('.class', '.java')
        # with zipfile.ZipFile(jar, "r") as zip_ref:
        #     for f in zip_ref.namelist():
        #         if f.endswith(extensions):
        #             zip_ref.extract(f, CACHE)

        subprocess.run(["java", "-jar", DECOMPILER, jar, "--outputdir", CACHE])

        print("Extracted Successfully!")

        class_files = []
        for dir_path, dirs, filenames in os.walk(CACHE, topdown=True):
            for d in dirs:
                if d.startswith('.') or d == "META-INF":
                    dirs.remove(d)

            for f in filenames:
                file = os.path.join(dir_path, f)
                if os.path.splitext(file)[1] == ".class":
                    class_files.append(file)

        print(f"TOTAL FILES: {len(class_files)}")

        for file in class_files:
            self.parse_file(file)

    def process(self):
        if os.path.exists(CACHE):
            shutil.rmtree(CACHE)
            os.makedirs(CACHE)
        else:
            os.makedirs(CACHE)

        if os.path.isfile(self.path) and os.path.splitext(self.path)[1] == ".jar":
            self.parse_jar(self.path)
        elif os.path.isdir(self.path):
            jars = []
            for dir_name, _, filenames in os.walk(self.path):
                for f in filenames:
                    if os.path.splitext(f)[1] == ".jar":
                        jars.append(os.path.abspath(os.path.join(dir_name, f)))

            for jar in jars:
                print(f"Ongoing jar: {jar}")
                self.parse_jar(jar)
                break
        else:
            raise GrasError(msg="Not a valid path!")


if __name__ == '__main__':
    JavaMiner(None, path="/home/mahen/elasticsearch-7.8.0/lib/").process()
