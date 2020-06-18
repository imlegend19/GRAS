import os
import logging
import xml.etree.ElementTree as Et

from gras.base_miner import BaseMiner
from gras.db.neo_helper import create_node, create_relationship
from gras.errors import GrasError

NAME = "name"
CLASSIFICATION = "classification"
VISIBILITY = "visibility"
IS_ABSTRACT = "isAbstract"
IS_FINAL = "isFinal"

logger = logging.getLogger("main")


class Cda2Neo4j(BaseMiner):
    def __init__(self, args):
        super().__init__(args=args)

        try:
            tree = Et.parse(args.path)
        except Et.ParseError:
            raise GrasError(msg="Cannot parse the XML file!")

        self.root = tree.getroot()

        self.context = self.root.find('context')
        self.context_name = self.context.attrib[NAME]

        self.class_id = {}
        self.package_class = {}
        self.package_id = {}

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    def process(self):
        self.parse_context()

    def build_dependencies(self, container):
        print("Building Dependencies...")
        for package in container:
            print(f"Ongoing Package: {package.attrib[NAME]}")
            cls: Et.Element
            for cls in package:
                class_id, class_type = self.class_id[cls.attrib[NAME]]
                dependencies = cls.find("dependencies")

                print(f"\tOngoing Class: {cls.attrib[NAME]}")
                print(f"\tTotal Dependencies: {dependencies.attrib['count']}")

                for dep in dependencies:
                    name = dep.attrib[NAME]
                    relation = dep.attrib[CLASSIFICATION]

                    try:
                        dep_id, dep_type = self.class_id[name]
                    except KeyError:
                        out = self._conn.run(create_node(node_type="Builtin", name=name))
                        dep_id = out.single()[0]
                        dep_type = "Builtin"
                        self.class_id[name] = dep_id, dep_type

                    self._conn.run(create_relationship(id1=class_id, id2=dep_id, label1=class_type,
                                                       label2=dep_type, relation=relation))

    def parse_package(self, package: Et.Element, container_id):
        name = package.attrib[NAME]
        classes = len(package)

        print(f"Ongoing package: {name}, Total Classes: {classes}")
        out = self._conn.run(create_node(node_type="Package", name=name, classes=classes))
        package_id = out.single()[0]

        self.package_id[name] = package_id

        print("Creating Package Relationship...")
        self._conn.run(create_relationship(id1=package_id, id2=container_id, label1="Package", label2="Container",
                                           relation="is_package_of"))

        pkg_classes = []

        cls: Et.Element
        for cls in package:
            name = cls.attrib[NAME]
            type_ = cls.attrib[CLASSIFICATION]
            visibility = cls.attrib[VISIBILITY]
            is_abstract = True if IS_ABSTRACT in cls.attrib else False
            is_final = True if IS_FINAL in cls.attrib else False

            print(f"\tDumping Class: {name}...")
            out = self._conn.run(create_node(node_type=type_.title(), name=name, type=type_, visibility=visibility,
                                             is_abstract=is_abstract, is_final=is_final))
            class_id = out.single()[0]
            self.class_id[name] = class_id, type_.title()

            pkg_classes.append(name)

            self._conn.run(create_relationship(id1=class_id, id2=package_id, label1=type_.title(),
                                               label2="Package", relation=f"is_{type_}_of"))

        self.package_class[package_id] = pkg_classes

    def parse_container(self, container: Et.Element):
        name = os.path.basename(container.attrib[NAME])
        path = container.attrib[NAME]
        packages = len(container)
        ext = container.attrib[CLASSIFICATION]

        print(f"Ongoing container: {name}")
        out = self._conn.run(create_node(node_type="Container", name=name, path=path, packages=packages, ext=ext))
        container_id = out.single()[0]

        for package in container:
            self.parse_package(package=package, container_id=container_id)

        print("Packages:", self.package_id)
        print("Classes:", self.class_id)

        self.build_dependencies(container)

    def parse_context(self):
        for container in self.context:
            self.parse_container(container)
