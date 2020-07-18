from collections import namedtuple

from gras.base_miner import BaseMiner
from gras.db.neo_helper import create_node, create_relationship
from gras.file_dependency.java.java_miner import JavaMiner
from gras.file_dependency.java.models import (
    AnnotationTypeModel, ClassModel, EnumModel, FileModel, InterfaceModel,
    JarModel
)

FILE = namedtuple("Node", ["name", "pkg"])
NODE = namedtuple("Node", ["type", "name", "file_id"])


class JavaNeoExecutor(BaseMiner):
    def __init__(self, args):
        super().__init__(args=args)
        # args.path -> path where java files are to be parsed
        self.jars = JavaMiner(path=args.path).process()

        self._initialise_db()
        self.session = self._conn.session()

        self.packages = {}
        self.files = {}
        self.nodes = {}

    def load_from_file(self, **kwargs):
        ...

    def dump_to_file(self, **kwargs):
        ...

    def __check_for_pkg(self, pkg):
        for p in self.packages:
            if p == pkg:
                return self.packages[p]

    def _parse_file(self, file: FileModel):
        print(f"\tOngoing file: {file.name}...")

        pkg_id = self.__check_for_pkg(file.pkg)
        if not pkg_id:
            out = self.session.run(create_node(node_type="Package", name=file.pkg))
            pkg_id = out.single()[0]
            self.packages[file.pkg] = pkg_id

        out = self.session.run(create_node(node_type="File", name=file.name, loc=file.loc))
        file_id = out.single()[0]
        self.files[FILE(name=file.name, pkg=file.pkg)] = file_id

        create_relationship(id1=file_id, id2=pkg_id, label1="File", label2="Package", relation="is_file_of")

        cls: ClassModel
        for cls in file.classes:
            out = self.session.run(create_node(node_type="Class", name=cls.name, modifiers=cls.modifiers, loc=cls.loc))
            cls_id = out.single()[0]
            self.nodes[NODE(type="Class", name=cls.name, file_id=file_id)] = cls_id

        itf: InterfaceModel
        for itf in file.interfaces:
            out = self.session.run(create_node(node_type="Interface", name=itf.name, modifiers=itf.modifiers,
                                               loc=itf.loc))
            itf_id = out.single()[0]
            self.nodes[NODE(type="Interface", name=itf.name, file_id=file_id)] = itf_id

        enum: EnumModel
        for enum in file.enums:
            out = self.session.run(create_node(node_type="Enum", name=enum.name, modifiers=enum.modifiers,
                                               loc=enum.loc))
            enum_id = out.single()[0]
            self.nodes[NODE(type="Enum", name=enum.name, file_id=file_id)] = enum_id

        anon: AnnotationTypeModel
        for anon in file.annotations:
            out = self.session.run(create_node(node_type="AnnotationType", name=anon.name, modifiers=anon.modifiers,
                                               loc=anon.loc))
            anon_id = out.single()[0]
            self.nodes[NODE(type="AnnotationType", name=anon.name, file_id=file_id)] = anon_id

    def parse_jar(self, jar: JarModel):
        print(f"Ongoing jar: {jar.name}...")
        for file in jar.files:
            self._parse_file(file)

    def _link_file(self, file: FileModel):
        print(f"\tLinking file: {file.name}...")

        for imp in file.imports:
            ...

    def link_jar(self, jar: JarModel):
        print(f"Linking jar: {jar.name}...")
        for file in jar.files:
            self._link_file(file)

    def process(self):
        if isinstance(self.jars, list):
            for jar in self.jars:
                self.parse_jar(jar)

            for jar in self.jars:
                self.link_jar(jar)
        else:
            self.parse_jar(self.jars)
            self.link_jar(self.jars)
