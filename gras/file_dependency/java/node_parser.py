from typing import Any

from antlr4 import CommonTokenStream, InputStream
from antlr4.tree.Tree import TerminalNodeImpl

from gras.file_dependency.java.grammar_v7.JavaParserVisitor import JavaParserVisitor
from gras.file_dependency.java.grammar_v7.JavaLexer import JavaLexer
from gras.file_dependency.java.grammar_v7.JavaParser import JavaParser
from gras.file_dependency.java.models import ImportModel, TypeParameterModel


class NodeParser(JavaParserVisitor):
    def __init__(self, node, subtype=None):
        self.node = node
        self.subtype = subtype

        self.base_type = node.__class__.__name__
        self.value: Any = None

        self.visit(node)

    def visitTerminal(self, node):
        self.value = node.getText()

    def visitQualifiedName(self, ctx: JavaParser.QualifiedNameContext):
        pkg = ""
        for cld in ctx.children:
            pkg += NodeParser(node=cld).value

        self.value = pkg

    def visitPackageDeclaration(self, ctx: JavaParser.PackageDeclarationContext):
        self.value = NodeParser(node=ctx.qualifiedName()).value

    # noinspection PyUnresolvedReferences
    def visitImportDeclaration(self, ctx: JavaParser.ImportDeclarationContext):
        val = NodeParser(node=ctx.qualifiedName()).value.split('.')
        pkg, name = ".".join(val[:-1]), val[-1]

        self.value = ImportModel(
            pkg=pkg,
            name=name,
            lineno=ctx.start.line
        )

    def visitClassOrInterfaceModifier(self, ctx: JavaParser.ClassOrInterfaceModifierContext):
        # TODO: Parse annotation

        self.value = []
        for cld in ctx.children:
            self.value.append(NodeParser(node=cld).value)

    def visitTypeType(self, ctx: JavaParser.TypeTypeContext):
        self.value = NodeParser(node=ctx.classOrInterfaceType()).value

    def visitTypeBound(self, ctx: JavaParser.TypeBoundContext):
        self.value = []
        for cld in ctx.children[::2]:
            val = NodeParser(node=cld).value
            if val:
                self.value.append(val)

    def visitTypeParameter(self, ctx: JavaParser.TypeParameterContext):
        name = NodeParser(node=ctx.IDENTIFIER()).value
        extends = None if not ctx.EXTENDS() else NodeParser(node=ctx.typeBound()).value
        annotations = NodeParser(node=ctx.annotation()) if ctx.annotation() else None

        self.value(
            TypeParameterModel(
                annotations=annotations,
                name=name,
                extends=None if not extends else extends,
                lineno=ctx.start.line
            )
        )

    def visitTypeParameters(self, ctx: JavaParser.TypeParametersContext):
        self.value = []

        for cld in ctx.children[1: -1: 2]:
            self.value.append(NodeParser(node=cld).value)

    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        # TODO: Name may be type<annotation>
        children = ctx.children

        type_ = NodeParser(node=children.pop(0)).value
        name = NodeParser(node=children.pop(0)).value
        body: JavaParser.ClassBodyContext = children.pop(-1)

        type_parameters, extends, implements = None, None, None

        if isinstance(children[0], JavaParser.TypeParametersContext):
            type_parameters = NodeParser(node=children.pop(0)).value

        if isinstance(children[0], TerminalNodeImpl):
            val = NodeParser(node=children.pop(0)).value
            if val == "extends":
                extends = NodeParser(node=children.pop(0)).value
            else:
                implements = NodeParser(node=children.pop(0)).value

        body = body.children[1: -1]
        # for cld in body:

    def visitTypeDeclaration(self, ctx: JavaParser.TypeDeclarationContext):
        children = ctx.children
        children.pop()

        modifier = NodeParser(node=children.pop(0)).value


if __name__ == '__main__':
    with open("/home/mahen/PycharmProjects/GRAS/tests/data/java/Sample.java") as f:
        content = f.read()

    # TODO: Use antlr.FileStream
    lexer = JavaLexer(InputStream(content))
    stream = CommonTokenStream(lexer)
    parser = JavaParser(stream)

    print("Compiling...")
    tree = parser.compilationUnit()
    print("Done!")

    loc = tree.stop.line - tree.start.line + 1

    imports = []
    for child in tree.children:
        np = NodeParser(node=child).value
        imports.extend(np)

    print(imports)
