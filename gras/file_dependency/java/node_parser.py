from antlr4 import CommonTokenStream, InputStream

from gras.file_dependency.java.grammar_v8.Java8ParserVisitor import Java8ParserVisitor
from gras.file_dependency.java.grammar_v8.Java8Lexer import Java8Lexer
from gras.file_dependency.java.grammar_v8.Java8Parser import Java8Parser


class NodeParser(Java8ParserVisitor):
    def __init__(self, node, subtype=None):
        self.node = node
        self.subtype = subtype

        self.base_type = node.__class__.__name__
        self.value = None

    def visitTypeDeclaration(self, ctx: Java8Parser.TypeDeclarationContext):
        pass


if __name__ == '__main__':
    with open("/home/mahen/PycharmProjects/GRAS/tests/data/java/sample.java") as f:
        content = f.read()

    # TODO: Use antlr.FileStream
    lexer = Java8Lexer(InputStream(content))
    stream = CommonTokenStream(lexer)
    parser = Java8Parser(stream)
    tree = parser.compilationUnit()

    for child in tree.children:
        np = NodeParser(node=child)
