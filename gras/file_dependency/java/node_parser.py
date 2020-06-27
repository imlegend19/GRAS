from typing import Any

from antlr4 import CommonTokenStream, InputStream

from gras.file_dependency.java.grammar_v7.JavaParserVisitor import JavaParserVisitor
from gras.file_dependency.java.grammar_v7.JavaLexer import JavaLexer
from gras.file_dependency.java.grammar_v7.JavaParser import JavaParser
from gras.file_dependency.java.models import (
    AnnotationTypeModel, BodyModel, CallModel, ClassModel, EnumModel, ImportModel, InterfaceModel, MemberModel,
    MethodModel, TypeParameterModel
)

EXT_CLASSES = set()


class NodeParser(JavaParserVisitor):
    def __init__(self, node, subtype=None):
        self.node = node
        self.subtype = subtype

        self.base_type = node.__class__.__name__
        self.value: Any = None

        if node:
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
        annotate = NodeParser(node=ctx.annotation()) if ctx.annotation() else None

        self.value(
            TypeParameterModel(
                annotations=annotate,
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
        if ctx.formalParameterList():
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
                if not temp:
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

        if call:
            call = call.split(".")
            if len(call) == 1:
                ref, target = "this", call[0]
            else:
                ref, target = call[0], call[1]

            self.value.append(CallModel(reference=ref, target=target, lineno=ctx.start.line))

        if new:
            self.value.append(CallModel(reference=new, target=None, lineno=ctx.start.line))

    def visitParExpression(self, ctx: JavaParser.ParExpressionContext):
        self.value = NodeParser(node=ctx.expression()).value

    def visitArrayInitializer(self, ctx: JavaParser.ArrayInitializerContext):
        calls = []

        for cld in ctx.children[1: -1]:
            if isinstance(cld, JavaParser.VariableInitializerContext):
                calls.extend(NodeParser(node=cld).value)

    def visitVariableInitializer(self, ctx: JavaParser.VariableInitializerContext):
        self.value = NodeParser(node=ctx.children[0]).value

    def visitVariableDeclarator(self, ctx: JavaParser.VariableDeclaratorContext):
        val = NodeParser(node=ctx.variableInitializer()).value
        if val:
            self.value = val
        else:
            self.value = []

    def visitVariableDeclarators(self, ctx: JavaParser.VariableDeclaratorsContext):
        calls = []

        for cld in ctx.children[::2]:
            calls.extend(NodeParser(node=cld).value)

        self.value = calls

    def visitLocalVariableDeclaration(self, ctx: JavaParser.LocalVariableDeclarationContext):
        # Only parsing calls
        self.value = NodeParser(node=ctx.variableDeclarators()).value

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

    def visitCatchClause(self, ctx: JavaParser.CatchClauseContext):
        self.value = NodeParser(node=ctx.block()).value

    def visitFinallyBlock(self, ctx: JavaParser.FinallyBlockContext):
        self.value = NodeParser(node=ctx.block()).value

    def visitResource(self, ctx: JavaParser.ResourceContext):
        self.value = NodeParser(node=ctx.expression()).value

    def visitResources(self, ctx: JavaParser.ResourcesContext):
        calls = []

        for cld in ctx.children[::2]:
            calls.extend(NodeParser(node=cld).value)

    def visitResourceSpecification(self, ctx: JavaParser.ResourceSpecificationContext):
        self.value = NodeParser(node=ctx.resources()).value

    def visitStatement(self, ctx: JavaParser.StatementContext):
        calls = []

        for cld in ctx.children:
            if isinstance(cld, (
                    JavaParser.BlockContext,
                    JavaParser.SwitchBlockStatementGroupContext,
                    JavaParser.FinallyBlockContext,
                    JavaParser.CatchClauseContext,
                    JavaParser.ForControlContext,
                    JavaParser.ExpressionContext,
                    JavaParser.StatementContext,
                    JavaParser.ParExpressionContext,
                    JavaParser.ResourceSpecificationContext
            )):
                calls.extend(NodeParser(node=cld).value)

        self.value = calls

    def visitBlockStatement(self, ctx: JavaParser.BlockStatementContext):
        calls = []

        # Not parsing localTypeDeclaration (Class or Interface)
        if ctx.localVariableDeclaration():
            calls.extend(NodeParser(node=ctx.localVariableDeclaration()).value)
        elif ctx.statement():
            calls.extend(NodeParser(node=ctx.statement()).value)

        self.value = calls

    def visitBlock(self, ctx: JavaParser.BlockContext):
        if ctx.getChildCount() == 2:
            self.value = []
        else:
            calls = []
            for cld in ctx.children[1: -1:2]:
                calls.append(NodeParser(node=cld).value)

            self.value = calls

    def visitMethodBody(self, ctx: JavaParser.MethodBodyContext):
        self.value = NodeParser(node=ctx.block()).value

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        return_type = NodeParser(node=ctx.typeTypeOrVoid()).value
        name = NodeParser(node=ctx.IDENTIFIER()).value
        total_args = NodeParser(node=ctx.formalParameters()).value
        throws = NodeParser(node=ctx.qualifiedNameList()).value if ctx.THROWS() else None
        calls = NodeParser(node=ctx.methodBody()).value

        self.value = MethodModel(
            name=name,
            return_type=return_type,
            total_args=total_args,
            throws=throws,
            calls=calls,
            lineno=ctx.start.line
        )

    def visitGenericMethodDeclaration(self, ctx: JavaParser.GenericMethodDeclarationContext):
        self.value = NodeParser(node=ctx.methodDeclaration()).value

    def visitFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        self.value = NodeParser(node=ctx.variableDeclarators()).value

    def visitConstructorDeclaration(self, ctx: JavaParser.ConstructorDeclarationContext):
        self.value = NodeParser(node=ctx.constructorBody).value

    def visitGenericConstructorDeclaration(self, ctx: JavaParser.GenericConstructorDeclarationContext):
        self.value = NodeParser(node=ctx.constructorDeclaration()).value

    def visitMemberDeclaration(self, ctx: JavaParser.MemberDeclarationContext):
        val = ctx.children[0]

        if isinstance(val, JavaParser.MethodDeclarationContext):
            self.value = MemberModel(
                subtype="Method",
                value=NodeParser(node=val).value
            )
        elif isinstance(val, JavaParser.GenericMethodDeclarationContext):
            self.value = MemberModel(
                subtype="Method",
                value=NodeParser(node=val).value
            )
        elif isinstance(val, JavaParser.FieldDeclarationContext):
            self.value = MemberModel(
                subtype="Call",
                value=NodeParser(node=val).value
            )
        elif isinstance(val, JavaParser.ConstructorDeclarationContext):
            self.value = MemberModel(
                subtype="Call",
                value=NodeParser(node=val).value
            )

    def visitConstantDeclarator(self, ctx: JavaParser.ConstantDeclaratorContext):
        self.value = NodeParser(node=ctx.variableInitializer()).value

    def visitConstDeclaration(self, ctx: JavaParser.ConstDeclarationContext):
        calls = []

        for cld in ctx.children:
            if isinstance(cld, JavaParser.ConstantDeclaratorContext):
                calls.extend(NodeParser(node=cld).value)

        self.value = calls

    def visitInterfaceMethodDeclaration(self, ctx: JavaParser.InterfaceMethodDeclarationContext):
        modifiers, calls = [], []

        return_type, throws = None, None
        total_args = 0
        name = NodeParser(node=ctx.IDENTIFIER()).value

        for cld in ctx.children:
            if isinstance(cld, JavaParser.InterfaceMethodModifierContext):
                modifiers.append(NodeParser(node=cld).value)
            elif isinstance(cld, JavaParser.TypeTypeOrVoidContext):
                return_type = NodeParser(node=cld).value
            elif isinstance(cld, JavaParser.QualifiedNameListContext):
                throws = NodeParser(node=cld).value
            elif isinstance(cld, JavaParser.MethodBodyContext):
                calls = NodeParser(node=cld).value
            elif isinstance(cld, JavaParser.FormalParametersContext):
                total_args = NodeParser(node=cld).value

        self.value = MethodModel(
            name=name,
            modifiers=modifiers,
            return_type=return_type,
            total_args=total_args,
            throws=throws,
            calls=calls,
            lineno=ctx.start.line
        )

    def visitGenericInterfaceMethodDeclaration(self, ctx: JavaParser.GenericInterfaceMethodDeclarationContext):
        self.value = NodeParser(node=ctx.interfaceMethodDeclaration()).value

    def visitInterfaceMemberDeclaration(self, ctx: JavaParser.InterfaceMemberDeclarationContext):
        val = ctx.children[0]

        if isinstance(val, JavaParser.ConstDeclarationContext):
            self.value = MemberModel(
                subtype="Call",
                value=NodeParser(node=val).value
            )
        elif isinstance(val, JavaParser.InterfaceMethodDeclarationContext):
            self.value = MemberModel(
                subtype="Method",
                value=NodeParser(node=val).value
            )
        elif isinstance(val, JavaParser.GenericMethodDeclarationContext):
            self.value = MemberModel(
                subtype="Method",
                value=NodeParser(node=val).value
            )

    def visitClassBodyDeclaration(self, ctx: JavaParser.ClassBodyDeclarationContext):
        if not ctx.STATIC():
            modifiers = []
            for cld in ctx.children:
                if isinstance(cld, JavaParser.ModifierContext):
                    modifiers.append(NodeParser(node=cld).value)

            method, calls = None, []

            # noinspection PyTypeChecker
            member = NodeParser(node=ctx.memberDeclaration()).value

            if member:
                member: MemberModel
                if member.subtype == "Method":
                    tmp: MethodModel = member.value
                    if tmp.modifiers:
                        tmp.modifiers.extend(modifiers)
                    else:
                        tmp.modifiers = modifiers

                    method = tmp
                elif member.subtype == "Call":
                    calls.extend(member.value)

            self.value = BodyModel(
                method=method,
                calls=calls
            )
        else:
            calls = NodeParser(node=ctx.block()).value

            self.value = BodyModel(
                method=None,
                calls=calls
            )

    def visitInterfaceBodyDeclaration(self, ctx: JavaParser.InterfaceBodyDeclarationContext):
        modifiers = []
        for cld in ctx.children:
            if isinstance(cld, JavaParser.ModifierContext):
                modifiers.append(NodeParser(node=cld).value)

        method, calls = None, []

        # noinspection PyTypeChecker
        member = NodeParser(node=ctx.interfaceMemberDeclaration()).value

        if member:
            member: MemberModel
            if member.subtype == "Method":
                tmp: MethodModel = member.value
                tmp.modifiers = modifiers
                method = tmp
            elif member.subtype == "Call":
                calls.extend(member.value)

        self.value = BodyModel(
            method=method,
            calls=calls
        )

    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        # TODO: Name may be type<annotation>
        name = NodeParser(node=ctx.IDENTIFIER()).value
        EXT_CLASSES.add(name)  # Used in case of recursion

        extends, implements = None, None

        if ctx.EXTENDS():
            extends = NodeParser(node=ctx.typeType()).value
        elif ctx.IMPLEMENTS():
            implements = NodeParser(node=ctx.typeList()).value

        methods, calls = [], []

        body = ctx.classBody()
        for cld in body.children[1: -1]:
            # noinspection PyTypeChecker
            val = NodeParser(node=cld).value
            if val:
                val: BodyModel
                if val.method:
                    methods.append(val.method)
                elif val.calls:
                    calls.extend(val.calls)

        self.value = ClassModel(
            name=name,
            extends=extends,
            implements=implements,
            methods=methods,
            calls=calls,
            lineno=ctx.start.line
        )

    def visitEnumDeclaration(self, ctx: JavaParser.EnumDeclarationContext):
        name = NodeParser(node=ctx.IDENTIFIER()).value
        EXT_CLASSES.add(name)

        implements = None
        if ctx.IMPLEMENTS():
            implements = NodeParser(node=ctx.typeList()).value

        methods, calls = [], []

        body = ctx.enumBodyDeclarations()
        if body:
            for cld in body.children[1:]:
                # noinspection PyTypeChecker
                val = NodeParser(node=cld).value
                if val:
                    val: BodyModel
                    if val.method:
                        methods.append(val.method)
                    elif val.calls:
                        calls.extend(val.calls)

        self.value = EnumModel(
            name=name,
            implements=implements,
            methods=methods,
            calls=calls,
            lineno=ctx.start.line
        )

    def visitInterfaceDeclaration(self, ctx: JavaParser.InterfaceDeclarationContext):
        name = NodeParser(node=ctx.IDENTIFIER()).value
        EXT_CLASSES.add(name)

        extends = None

        if ctx.EXTENDS():
            extends = NodeParser(node=ctx.typeList())

        methods, calls = [], []

        body = ctx.interfaceBody()
        for cld in body.children[1:-1]:
            # noinspection PyTypeChecker
            val = NodeParser(node=cld).value
            if val:
                val: BodyModel
                if val.method:
                    methods.append(val.method)
                elif val.calls:
                    calls.extend(val.calls)

        self.value = InterfaceModel(
            name=name,
            extends=extends,
            methods=methods,
            calls=calls,
            lineno=ctx.start.line
        )

    def visitAnnotationConstantRest(self, ctx: JavaParser.AnnotationConstantRestContext):
        calls = NodeParser(node=ctx.variableDeclarators()).value

        self.value = BodyModel(
            method=None,
            calls=calls
        )

    def visitAnnotationMethodOrConstantRest(self, ctx: JavaParser.AnnotationMethodOrConstantRestContext):
        if ctx.annotationConstantRest():
            self.value = NodeParser(node=ctx.annotationConstantRest()).value

    def visitAnnotationTypeElementRest(self, ctx: JavaParser.AnnotationTypeElementRestContext):
        if ctx.annotationMethodOrConstantRest():
            self.value = NodeParser(node=ctx.annotationMethodOrConstantRest()).value

    def visitAnnotationTypeElementDeclaration(self, ctx: JavaParser.AnnotationTypeElementDeclarationContext):
        if ctx.annotationTypeElementRest():
            self.value = NodeParser(node=ctx.annotationTypeElementRest()).value

    def visitAnnotationTypeDeclaration(self, ctx: JavaParser.AnnotationTypeDeclarationContext):
        name = NodeParser(node=ctx.IDENTIFIER()).value

        calls = []

        body = ctx.annotationTypeBody()
        for cld in body.children[1:-1]:
            # noinspection PyTypeChecker
            val = NodeParser(node=cld).value
            if val:
                val: BodyModel
                if val.calls:
                    calls.extend(val.calls)

        self.value = AnnotationTypeModel(
            name=name,
            calls=calls,
            lineno=ctx.start.line
        )

    def visitTypeDeclaration(self, ctx: JavaParser.TypeDeclarationContext):
        modifiers = []
        node = None

        for cld in ctx.children:
            if isinstance(cld, JavaParser.ClassOrInterfaceModifierContext):
                modifiers.append(NodeParser(node=cld).value)
            elif isinstance(cld, JavaParser.ClassDeclarationContext):
                node = NodeParser(node=cld).value
                node.modifiers = modifiers
            elif isinstance(cld, JavaParser.EnumDeclarationContext):
                node = NodeParser(node=cld).value
                node.modifiers = modifiers
            elif isinstance(cld, JavaParser.InterfaceDeclarationContext):
                node = NodeParser(node=cld).value
                node.modifiers = modifiers
            elif isinstance(cld, JavaParser.AnnotationTypeDeclarationContext):
                node = NodeParser(node=cld).value
                node.modifiers = modifiers

        self.value = node


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

    if tree.packageDeclaration():
        pkg = NodeParser(node=tree.children.pop(0)).value

    imports, classes, interfaces, annotations, enums = [], [], [], [], []
    for child in tree.children:
        model = NodeParser(node=child).value
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

    print(imports)
