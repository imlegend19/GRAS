from typing import Any

from antlr4 import CommonTokenStream, InputStream

from gras.file_dependency.java.grammar.Java8ParserVisitor import Java8ParserVisitor
from gras.file_dependency.java.grammar.Java8Lexer import Java8Lexer
from gras.file_dependency.java.grammar.Java8Parser import Java8Parser


class NodeParser(Java8ParserVisitor):
    def __init__(self, node, subtype=None):
        self.node = node
        self.subtype = subtype

        self.base_type = node.__class__.__name__
        self.value: Any = None

        self.visit(node)

    def visitTerminal(self, node):
        self.value = node.getText()

    def visitTypeDeclaration(self, ctx: Java8Parser.TypeDeclarationContext):
        pass


if __name__ == '__main__':
    with open("/home/mahen/PycharmProjects/GRAS/.cache/com/fasterxml/jackson/dataformat/smile/SmileParser.java") as f:
        content = f.read()

    # TODO: Use antlr.FileStream
    lexer = Java8Lexer(InputStream(content))
    stream = CommonTokenStream(lexer)
    parser = Java8Parser(stream)

    print("Compiling...")
    tree = parser.packageDeclaration()
    print("Done!")

    imports = []
    for child in tree.children:
        np = NodeParser(node=child).value
        imports.extend(np)

    print(imports)
