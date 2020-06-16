from typing import Any

from antlr4 import CommonTokenStream, InputStream
from antlr4.tree.Tree import TerminalNodeImpl

from gras.file_dependency.javascript.grammar.JavaScriptLexer import JavaScriptLexer
from gras.file_dependency.javascript.grammar.JavaScriptParser import JavaScriptParser
from gras.file_dependency.javascript.grammar.JavaScriptParserVisitor import JavaScriptParserVisitor
from gras.file_dependency.javascript.models import ImportModel
from gras.file_dependency.javascript.node_types import Namespace


class NodeParser(JavaScriptParserVisitor):
    def __init__(self, node, subtype=None):
        self.node = node
        self.subtype = subtype

        self.base_type = node.__class__.__name__
        self.value: Any = None

        self.visit(node)

    def visitTerminal(self, node: TerminalNodeImpl):
        self.value = node.getText()

    def visitImportNamespace(self, ctx: JavaScriptParser.ImportNamespaceContext):
        name = NodeParser(node=ctx.children[0]).value

        if len(ctx.children) > 1:
            asname = NodeParser(node=ctx.children[-1]).value
        else:
            asname = None

        self.value = Namespace(
            name=name,
            asname=asname
        )

    def visitIdentifier(self, ctx: JavaScriptParser.IdentifierContext):
        self.value = NodeParser(node=ctx.children[0]).value

    def visitIdentifierName(self, ctx: JavaScriptParser.IdentifierNameContext):
        self.value = NodeParser(node=ctx.children[0]).value

    def visitImportFrom(self, ctx: JavaScriptParser.ImportFromContext):
        self.value = NodeParser(node=ctx.StringLiteral()).value

    def visitKeyword(self, ctx: JavaScriptParser.KeywordContext):
        self.value = NodeParser(node=ctx.children[0]).value

    def visitReservedWord(self, ctx: JavaScriptParser.ReservedWordContext):
        self.value = NodeParser(node=ctx.children[0]).value

    def visitAliasName(self, ctx: JavaScriptParser.AliasNameContext):
        name = NodeParser(node=ctx.children[0]).value

        if len(ctx.children) > 1:
            asname = NodeParser(node=ctx.children[-1]).value
        else:
            asname = None

        self.value = Namespace(
            name=name,
            asname=asname
        )

    def visitModuleItems(self, ctx: JavaScriptParser.ModuleItemsContext):
        self.value = []

        for alias in ctx.children[1: -1: 2]:
            self.value.append(NodeParser(node=alias).value)

    def visitImportDefault(self, ctx: JavaScriptParser.ImportDefaultContext):
        self.value = []

        for sub_node in ctx.children[::2]:
            self.value.append(NodeParser(node=sub_node).value)

    def visitImportFromBlock(self, ctx: JavaScriptParser.ImportFromBlockContext):
        self.value = []

        default = ctx.importDefault()
        module_items = ctx.moduleItems()
        namespace = ctx.importNamespace()

        module = NodeParser(node=ctx.importFrom()).value

        if default:
            val = NodeParser(node=default).value

            for item in val:
                self.value.append(
                    ImportModel(
                        name=item.name,
                        asname=item.asname,
                        module=module,
                        line=ctx.start.line
                    )
                )

        if namespace:
            val: Any = NodeParser(node=namespace).value

            self.value.append(
                ImportModel(
                    name=val.name,
                    asname=val.asname,
                    module=module,
                    line=ctx.start.line
                )
            )
        elif module_items:
            val = NodeParser(node=module_items).value

            for item in val:
                self.value.append(
                    ImportModel(
                        name=item.name,
                        asname=item.asname,
                        module=module,
                        line=ctx.start.line
                    )
                )

    def visitImportStatement(self, ctx: JavaScriptParser.ImportStatementContext):
        self.value = NodeParser(node=ctx.importFromBlock()).value


if __name__ == '__main__':
    with open("/home/mahen/PycharmProjects/GRAS/tests/data/imports.js") as f:
        content = f.read()

    lexer = JavaScriptLexer(InputStream(content))
    stream = CommonTokenStream(lexer)
    parser = JavaScriptParser(stream)
    tree: JavaScriptParser.SourceElementsContext = parser.program().children[0]
    children = [parent.children[0] for parent in tree.children]

    imports = []

    for child in children:
        np = NodeParser(node=child).value
        imports.extend(np)

    print(imports)
