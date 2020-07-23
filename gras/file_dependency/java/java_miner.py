import glob
import multiprocessing as mp
import os
import shutil
import subprocess
import zipfile

from antlr4 import CommonTokenStream, FileStream

from gras import ROOT
from gras.errors import GrasError
from gras.file_dependency.java.grammar_v7.JavaLexer import JavaLexer
from gras.file_dependency.java.grammar_v7.JavaParser import JavaParser
from gras.file_dependency.java.models import (
    AnnotationTypeModel, ClassModel, EnumModel, FileModel, ImportModel,
    InterfaceModel, JarModel
)
from gras.file_dependency.java.node_parser import NodeParser

CACHE = os.path.join(ROOT, ".cache")
DECOMPILER = os.path.join(ROOT, "gras/file_dependency/java/decompiler/cfr.jar")
THREADS = min(mp.cpu_count() + 4, 32)


class JavaMiner:
    def __init__(self, path):
        self.path = path

    @staticmethod
    def parse_file(file):
        print("Ongoing file:", os.path.relpath(file, CACHE))
        file_name = os.path.basename(os.path.relpath(file, CACHE))
        package = os.path.dirname(os.path.relpath(file, CACHE))

        lexer = JavaLexer(FileStream(file))
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)

        tree = parser.compilationUnit()

        loc = tree.stop.line - tree.start.line + 1

        if tree.packageDeclaration():
            package = NodeParser(node=tree.children.pop(0)).process()

        imports, classes, interfaces, annotations, enums = [], [], [], [], []
        for child in tree.children:
            model = NodeParser(node=child).process()
            if isinstance(model, ImportModel):
                imports.append(model)
            elif isinstance(model, ClassModel):
                classes.append(model)
            elif isinstance(model, EnumModel):
                enums.append(model)
            elif isinstance(model, InterfaceModel):
                interfaces.append(model)
            elif isinstance(model, AnnotationTypeModel):
                annotations.append(model)

        return FileModel(
            name=file_name,
            pkg=package,
            imports=imports,
            classes=classes,
            interfaces=interfaces,
            enums=enums,
            annotations=annotations,
            loc=loc
        )

    def parse_jar(self, jar):
        shutil.rmtree(CACHE)
        os.makedirs(CACHE)

        print("Extracting...")

        if "-sources" in jar:
            extensions = '.java'
            with zipfile.ZipFile(jar, "r") as zip_ref:
                for f in zip_ref.namelist():
                    if f.endswith(extensions):
                        zip_ref.extract(f, CACHE)
        else:
            # procyon
            # subprocess.run(["java", "-jar", DECOMPILER, "-jar", jar, "mv", "-ll", "3", "-o", CACHE])

            # cfr
            subprocess.run(["java", "-jar", DECOMPILER, jar, "--hidelangimports", "false", "--outputdir", CACHE])

        print("Extracted Successfully!")

        class_files = []
        for dir_path, dirs, filenames in os.walk(CACHE, topdown=True):
            for d in dirs:
                if d.startswith('.') or d == "META-INF":
                    dirs.remove(d)

            for f in filenames:
                file = os.path.join(dir_path, f)
                if os.path.splitext(file)[1] in ".java" and "package-info" not in file:
                    if "$" in file:
                        print(file)
                    class_files.append(file)

        print(f"TOTAL FILES: {len(class_files)}")

        file_models = []
        remaining = len(class_files)
        for file in class_files:
            print("REMAINING:", remaining)
            file_models.append(self.parse_file(file))
            remaining -= 1

        # for i in range(0, len(class_files), 1):
        #     with mp.Pool(processes=1) as pool:
        #         result = pool.map_async(self.parse_file, class_files[i:i + 1])
        #         for file_model in result.get():
        #             print("REMAINING:", remaining)
        #             file_models.append(file_model)
        #             remaining -= 1

        return JarModel(
            name=os.path.basename(jar),
            files=file_models
        )

    def parse_directory(self, path):
        dirs = []
        for d in os.listdir(path):
            if os.path.isdir(os.path.join(path, d)) and not \
                    (d.startswith(".") or d in ["build", "buildSrc", "gradle", "ci"]):
                dirs.append(os.path.join(path, d))

        jars = []
        for d in dirs:
            jars.extend(self.fetch_jars_from_dir(d))

        print(f"TOTAL JARS: {len(jars)}")

        jar_models = []
        for jar in jars:
            jar_models.append(self.parse_jar(jar))

        return jar_models

    def fetch_jars_from_dir(self, dir_path, ph="sources"):
        final_jars = []

        sub_dirs = os.listdir(dir_path)
        if "build" and "src" in sub_dirs:
            jars = glob.glob(os.path.join(dir_path, f"build/libs/*{ph}.jar"))
            final_jars.extend(jars)
        elif "build" in sub_dirs:
            pass
        else:
            for dir_ in sub_dirs:
                if os.path.isdir(os.path.join(dir_path, dir_)):
                    final_jars.extend(self.fetch_jars_from_dir(os.path.join(dir_path, dir_)))

        return final_jars

    def process(self):
        if os.path.exists(CACHE):
            shutil.rmtree(CACHE)
            os.makedirs(CACHE)
        else:
            os.makedirs(CACHE)

        if os.path.isfile(self.path) and os.path.splitext(self.path)[1] == ".jar":
            jars = self.parse_jar(self.path)
        elif os.path.isdir(self.path):
            jars = self.parse_directory(self.path)
        else:
            raise GrasError(msg="Not a valid path!")

        return jars


if __name__ == '__main__':
    fm = JavaMiner(path=None).parse_file(
        "/home/mahen/PycharmProjects/GRAS/.cache/edu/stanford/nlp/pipeline/StanfordCoreNLP.java")
    print(fm)
