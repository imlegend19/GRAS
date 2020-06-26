from typing import Any

from antlr4 import CommonTokenStream, InputStream
from antlr4.tree.Tree import TerminalNodeImpl

from gras.file_dependency.java.grammar_v7.JavaParserVisitor import JavaParserVisitor
from gras.file_dependency.java.grammar_v7.JavaLexer import JavaLexer
from gras.file_dependency.java.grammar_v7.JavaParser import JavaParser
from gras.file_dependency.java.models import CallModel, ImportModel, TypeParameterModel

EXT_CLASSES = set()


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

        EXT_CLASSES.add(name)

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

    def visitVariableModifier(self, ctx: JavaParser.VariableModifierContext):
        # Only check if variable is `final`
        if ctx.FINAL():
            self.value = True
        else:
            self.value = False

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        # Currently not parsing n-hop `SUPER` calls and inter-class methods calls (`THIS`)
        # Not parsing `expressionList` => IDENTIFIER '(' expressionList? ')'
        if ctx.IDENTIFIER():
            self.value = NodeParser(node=ctx.IDENTIFIER()).value
            if self.value not in EXT_CLASSES:  # Considers calls for external classes only
                self.value = None

    def visitPrimary(self, ctx: JavaParser.PrimaryContext):
        # Only parsing `SUPER` & `IDENTIFIER`
        if ctx.SUPER():
            self.value = "super"
        elif ctx.IDENTIFIER():
            self.value = NodeParser(node=ctx.IDENTIFIER()).value
            if self.value not in EXT_CLASSES:
                self.value = None

    def visitCreatedName(self, ctx: JavaParser.CreatedNameContext):
        if ctx.IDENTIFIER():
            self.value = NodeParser(node=ctx.IDENTIFIER()).value

    def visitCreator(self, ctx: JavaParser.CreatorContext):
        self.value = NodeParser(node=ctx.createdName()).value

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        # Parsing only `primary` & `methodCall`
        self.value = []
        call = None
        new = None

        if ctx.bop:
            val = []
            for cld in ctx.children[::2]:
                temp = NodeParser(node=cld).value
                if temp is None and len(val) == 0:
                    val = None
                    break
                else:
                    val.append(temp)

            if val:
                # noinspection PyTypeChecker
                call = ".".join(val)
        else:
            if isinstance(ctx.children[0], JavaParser.MethodCallContext):
                call = NodeParser(node=ctx.children[0]).value
            elif ctx.NEW():
                new = NodeParser(node=ctx.creator()).value
                if new not in EXT_CLASSES:
                    new = None

        if not call:
            call = call.split(".")
            if len(call) == 1:
                ref, target = "this", call[0]
            else:
                ref, target = call[0], call[1]

            self.value.append(CallModel(reference=ref, target=target))

        if new:
            self.value.append(CallModel(reference=new, target=None))

    def visitParExpression(self, ctx: JavaParser.ParExpressionContext):
        self.value = NodeParser(node=ctx.expression()).value

    def visitVariableInitializer(self, ctx: JavaParser.VariableInitializerContext):
        if ctx.expression():
            self.value = NodeParser(node=ctx.expression()).value

    def visitVariableDeclarator(self, ctx: JavaParser.VariableDeclaratorContext):
        val = NodeParser(node=ctx.variableInitializer()).value
        if val:
            self.value = val
        else:
            self.value = []

    def visitLocalVariableDeclaration(self, ctx: JavaParser.LocalVariableDeclarationContext):
        # Only parsing calls
        calls = []

        for cld in ctx.variableDeclarators().children[::2]:
            calls.extend(NodeParser(node=cld).value)

    def visitEnhancedForControl(self, ctx: JavaParser.EnhancedForControlContext):
        self.value = NodeParser(node=ctx.expression()).value

    def visitExpressionList(self, ctx: JavaParser.ExpressionListContext):
        self.value = []

        for cld in ctx.children[::2]:
            self.value.extend(NodeParser(node=cld).value)

    def visitForInit(self, ctx: JavaParser.ForInitContext):
        self.value = NodeParser(node=ctx.children[0]).value

    def visitForControl(self, ctx: JavaParser.ForControlContext):
        val = []

        for cld in ctx.children:
            if isinstance(cld, JavaParser.EnhancedForControlContext):
                val.extend(NodeParser(node=cld).value)
            elif isinstance(cld, JavaParser.ForInitContext):
                val.extend(NodeParser(node=cld).value)
            elif isinstance(cld, JavaParser.ExpressionContext):
                val.extend(NodeParser(node=cld).value)
            elif isinstance(cld, JavaParser.ExpressionListContext):
                val.extend(NodeParser(node=cld).value)

        self.value = val

    def visitStatement(self, ctx: JavaParser.StatementContext):
        calls = []

        if ctx.IF():  # `if` statement
            calls.extend(NodeParser(node=ctx.parExpression()).value)
            calls.extend(NodeParser(node=ctx.getChild(2)).value)
            if ctx.ELSE():
                calls.extend(NodeParser(node=ctx.getChild(4)).value)
        elif ctx.FOR():
            calls.extend(NodeParser(node=ctx.forControl()).value)
            calls.extend(NodeParser(node=ctx.statement()).value)
        elif ctx.DO():
            calls.extend(NodeParser(node=ctx.statement()).value)
            calls.extend(NodeParser(node=ctx.parExpression()).value)
        elif ctx.WHILE():
            calls.extend(NodeParser(node=ctx.parExpression()).value)
            calls.extend(NodeParser(node=ctx.statement()).value)
        elif ctx.THROW() or ctx.RETURN():
            if ctx.expression():
                calls.extend(NodeParser(node=ctx.expression()).value)
        elif ctx.ASSERT():
            for cld in ctx.children[1: -1: 2]:
                calls.extend(NodeParser(node=cld).value)
        elif ctx.TRY():
            ...

        self.value = calls

    def visitBlockStatement(self, ctx: JavaParser.BlockStatementContext):
        calls = []

        if ctx.localVariableDeclaration():
            calls.extend(NodeParser(node=ctx.localVariableDeclaration()).value)
        elif ctx.statement():
            calls.extend(NodeParser(node=ctx.statement()).value)
        else:
            # localTypeDeclaration
            ...

    def visitBlock(self, ctx: JavaParser.BlockContext):
        if ctx.getChildCount() == 2:
            self.value = []
        else:
            stmt = []
            for cld in ctx.children[1: -1, :2]:
                stmt.append(NodeParser(node=cld).value)

    def visitMethodBody(self, ctx: JavaParser.MethodBodyContext):
        self.value = NodeParser(node=ctx.block()).value

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        return_type = NodeParser(node=ctx.typeTypeOrVoid()).value
        name = NodeParser(node=ctx.IDENTIFIER()).value
        total_param = NodeParser(node=ctx.formalParameters()).value
        throws = NodeParser(node=ctx.qualifiedNameList()).value if ctx.THROWS() else None
        calls = NodeParser(node=ctx.methodBody()).value

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
