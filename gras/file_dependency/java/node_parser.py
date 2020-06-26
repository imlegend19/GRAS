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
        val = []
        for cld in ctx.children:
            val.append(NodeParser(node=cld).value)

        self.value = "".join(val)

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
        self.value = []
        for cld in ctx.children:
            self.value.append(NodeParser(node=cld).value)

    def visitClassOrInterfaceType(self, ctx: JavaParser.ClassOrInterfaceTypeContext):
        # TODO: Only considering first identifier

        children = [cld for cld in ctx.children if not isinstance(cld, JavaParser.TypeArgumentsContext)]
        self.value = NodeParser(node=children[0]).value

    def visitPrimitiveType(self, ctx: JavaParser.PrimitiveTypeContext):
        self.value = NodeParser(node=ctx.children[0]).value

    def visitTypeType(self, ctx: JavaParser.TypeTypeContext):
        if ctx.classOrInterfaceType():
            self.value = NodeParser(node=ctx.classOrInterfaceType()).value
        elif ctx.primitiveType():
            self.value = NodeParser(node=ctx.primitiveType()).value

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

    def visitTypeList(self, ctx: JavaParser.TypeListContext):
        self.value = []

        for cld in ctx.children[::2]:
            self.value.extend(NodeParser(node=cld).value)

    def visitTypeTypeOrVoid(self, ctx: JavaParser.TypeTypeOrVoidContext):
        if ctx.VOID():
            self.value = NodeParser(node=ctx.VOID()).value
        else:
            self.value = NodeParser(node=ctx.typeType()).value

    def visitFormalParameters(self, ctx: JavaParser.FormalParametersContext):
        # Only considers the total number of parameters for a method
        self.value = len(ctx.formalParameterList().children)

    def visitQualifiedNameList(self, ctx: JavaParser.QualifiedNameListContext):
        self.value = []

        for cld in ctx.children[::2]:
            self.value.append(NodeParser(node=cld).value)

    def visitBlockStatement(self, ctx: JavaParser.BlockStatementContext):
        if ctx.localVariableDeclaration():
            ...
        elif ctx.statement():
            ...
        else:
            # localTypeDeclaration
            ...

    def visitBlock(self, ctx: JavaParser.BlockContext):
        if ctx.getChildCount() == 2:
            pass
        else:
            stmt = []
            for cld in ctx.children[1: -1, :2]:
                stmt.append(NodeParser(node=cld).value)

    def visitMethodBody(self, ctx: JavaParser.MethodBodyContext):
        if ctx.block():
            self.value = NodeParser(node=ctx.block()).value

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        return_type = NodeParser(node=ctx.typeTypeOrVoid()).value
        name = NodeParser(node=ctx.IDENTIFIER()).value
        total_param = NodeParser(node=ctx.formalParameters()).value
        throws = NodeParser(node=ctx.qualifiedNameList()).value if ctx.THROWS() else None
        body = NodeParser(node=ctx.methodBody()).value

    def visitMemberDeclaration(self, ctx: JavaParser.MemberDeclarationContext):
        self.value = NodeParser(node=ctx.children.pop()).value

    def visitClassBodyDeclaration(self, ctx: JavaParser.ClassBodyDeclarationContext):
        modifiers = []

        if ctx.STATIC():
            modifiers.append(NodeParser(node=ctx.STATIC()).value)

        member = NodeParser(node=ctx.memberDeclaration()).value

        for cld in ctx.children:
            if isinstance(cld, JavaParser.ModifierContext):
                modifiers.append(NodeParser(node=cld).value)

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
