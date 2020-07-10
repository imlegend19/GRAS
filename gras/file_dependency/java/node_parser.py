from antlr4.tree.Tree import TerminalNodeImpl

from gras.file_dependency.java.grammar_v7.JavaParser import JavaParser
from gras.file_dependency.java.grammar_v7.JavaParserVisitor import JavaParserVisitor
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

    @staticmethod
    def __get_list(item):
        if isinstance(item, str):
            return [item]
        elif isinstance(item, list):
            return item
        else:
            return list(item)

    def visit(self, node):
        if node:
            return node.accept(self)

    def process(self):
        if self.node:
            return self.visit(self.node)
        else:
            return None

    def visitTerminal(self, node):
        return node.getText()

    def visitQualifiedName(self, ctx: JavaParser.QualifiedNameContext):
        val = []
        for cld in ctx.children:
            val.append(self.visit(cld))

        return "".join(val)

    def visitPackageDeclaration(self, ctx: JavaParser.PackageDeclarationContext):
        return self.visit(ctx.qualifiedName())

    def visitImportDeclaration(self, ctx: JavaParser.ImportDeclarationContext):
        val = self.visit(ctx.qualifiedName()).split('.')
        package, name = ".".join(val[:-1]), val[-1]

        EXT_CLASSES.add(name)

        return ImportModel(
            pkg=package,
            name=name,
            lineno=ctx.start.line
        )

    def visitClassOrInterfaceModifier(self, ctx: JavaParser.ClassOrInterfaceModifierContext):
        val = []
        for cld in ctx.children:
            val.append(self.visit(cld))

        return val

    def visitClassOrInterfaceType(self, ctx: JavaParser.ClassOrInterfaceTypeContext):
        # TODO: Only considering first identifier
        children = [cld for cld in ctx.children if not isinstance(cld, JavaParser.TypeArgumentsContext)]
        return self.visit(children[0])

    def visitPrimitiveType(self, ctx: JavaParser.PrimitiveTypeContext):
        return self.visit(ctx.children[0])

    def visitTypeType(self, ctx: JavaParser.TypeTypeContext):
        if ctx.classOrInterfaceType():
            return self.visit(ctx.classOrInterfaceType())
        elif ctx.primitiveType():
            return self.visit(ctx.primitiveType())

    def visitTypeBound(self, ctx: JavaParser.TypeBoundContext):
        val = []
        for cld in ctx.children[::2]:
            tmp = self.visit(cld)
            if tmp:
                val.append(tmp)

        return val

    def visitTypeParameter(self, ctx: JavaParser.TypeParameterContext):
        name = self.visit(ctx.IDENTIFIER())
        extends = None if not ctx.EXTENDS() else self.visit(ctx.typeBound())
        annotate = self.visit(ctx.annotation()) if ctx.annotation() else None

        return TypeParameterModel(
            annotations=annotate,
            name=name,
            extends=None if not extends else extends,
            lineno=ctx.start.line
        )

    def visitTypeParameters(self, ctx: JavaParser.TypeParametersContext):
        val = []
        for cld in ctx.children[1: -1: 2]:
            val.append(self.visit(cld))

        return val

    def visitTypeList(self, ctx: JavaParser.TypeListContext):
        val = []
        for cld in ctx.children[::2]:
            val.extend(self.__get_list(self.visit(cld)))

        return val

    def visitTypeTypeOrVoid(self, ctx: JavaParser.TypeTypeOrVoidContext):
        if ctx.VOID():
            return self.visit(ctx.VOID())
        else:
            return self.visit(ctx.typeType())

    def visitFormalParameters(self, ctx: JavaParser.FormalParametersContext):
        # Only considers the total number of parameters for a method
        if ctx.formalParameterList():
            return len(ctx.formalParameterList().children)

    def visitQualifiedNameList(self, ctx: JavaParser.QualifiedNameListContext):
        val = []
        for cld in ctx.children[::2]:
            val.append(self.visit(cld))

        return val

    def visitVariableModifier(self, ctx: JavaParser.VariableModifierContext):
        # Only check if variable is `final`
        if ctx.FINAL():
            return True
        else:
            return False

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        # Currently not parsing n-hop `SUPER` calls and inter-class methods calls (`THIS`)
        # Not parsing `expressionList` => IDENTIFIER '(' expressionList? ')'
        if ctx.IDENTIFIER():
            return self.visit(ctx.IDENTIFIER())

    def visitPrimary(self, ctx: JavaParser.PrimaryContext):
        # Only parsing `SUPER` & `IDENTIFIER`
        if ctx.SUPER():
            return "super"
        elif ctx.IDENTIFIER():
            return self.visit(ctx.IDENTIFIER())

    def visitCreatedName(self, ctx: JavaParser.CreatedNameContext):
        identifiers = ctx.IDENTIFIER()
        if isinstance(identifiers, list):
            val = []
            for idt in identifiers:
                val.append(self.visit(idt))

            return ".".join(val)
        else:
            return self.visit(identifiers)

    def visitInnerCreator(self, ctx: JavaParser.InnerCreatorContext):
        return self.visit(ctx.IDENTIFIER())

    def visitCreator(self, ctx: JavaParser.CreatorContext):
        return self.visit(ctx.createdName())

    def visitExpression(self, ctx: JavaParser.ExpressionContext, return_model=True):
        val = []

        for cld in ctx.children:
            if isinstance(cld, (
                    JavaParser.InnerCreatorContext,
                    JavaParser.PrimaryContext,
                    JavaParser.MethodCallContext,
                    JavaParser.CreatorContext,
                    TerminalNodeImpl
            )):
                x = self.visit(cld)
                if x not in ('new', 'this'):
                    val.append(x)
            elif isinstance(cld, JavaParser.ExpressionContext):
                x = self.visitExpression(ctx=cld, return_model=False)
                if x:
                    val.extend(self.__get_list(x))

        if return_model:
            if "super" in val or len(set(val).intersection(EXT_CLASSES)) >= 1:
                target = ".".join(list(filter('.'.__ne__, val))[1:]) or None
                return [CallModel(reference=val[0], target=target, lineno=ctx.start.line)]
            else:
                return []
        else:
            return val

    def visitParExpression(self, ctx: JavaParser.ParExpressionContext):
        return self.visit(ctx.expression())

    def visitArrayInitializer(self, ctx: JavaParser.ArrayInitializerContext):
        calls = []
        for cld in ctx.children[1: -1]:
            if isinstance(cld, JavaParser.VariableInitializerContext):
                calls.extend(self.__get_list(self.visit(cld)))

        return calls

    def visitVariableInitializer(self, ctx: JavaParser.VariableInitializerContext):
        return self.visit(ctx.children[0])

    def visitVariableDeclarator(self, ctx: JavaParser.VariableDeclaratorContext):
        val = self.visit(ctx.variableInitializer())
        if val:
            return val
        else:
            return []

    def visitVariableDeclarators(self, ctx: JavaParser.VariableDeclaratorsContext):
        calls = []
        for cld in ctx.children[::2]:
            calls.extend(self.__get_list(self.visit(cld)))

        return calls

    def visitLocalVariableDeclaration(self, ctx: JavaParser.LocalVariableDeclarationContext):
        # Only parsing calls
        return self.visit(ctx.variableDeclarators())

    def visitEnhancedForControl(self, ctx: JavaParser.EnhancedForControlContext):
        return self.visit(ctx.expression())

    def visitExpressionList(self, ctx: JavaParser.ExpressionListContext):
        val = []
        for cld in ctx.children[::2]:
            val.extend(self.__get_list(self.visit(cld)))

        return val

    def visitForInit(self, ctx: JavaParser.ForInitContext):
        return self.visit(ctx.children[0])

    def visitForControl(self, ctx: JavaParser.ForControlContext):
        val = []

        for cld in ctx.children:
            if isinstance(cld, JavaParser.EnhancedForControlContext):
                val.extend(self.__get_list(self.visit(cld)))
            elif isinstance(cld, JavaParser.ForInitContext):
                val.extend(self.__get_list(self.visit(cld)))
            elif isinstance(cld, JavaParser.ExpressionContext):
                val.extend(self.__get_list(self.visit(cld)))
            elif isinstance(cld, JavaParser.ExpressionListContext):
                val.extend(self.__get_list(self.visit(cld)))

        return val

    def visitCatchClause(self, ctx: JavaParser.CatchClauseContext):
        return self.visit(ctx.block())

    def visitFinallyBlock(self, ctx: JavaParser.FinallyBlockContext):
        return self.visit(ctx.block())

    def visitResource(self, ctx: JavaParser.ResourceContext):
        return self.visit(ctx.expression())

    def visitResources(self, ctx: JavaParser.ResourcesContext):
        calls = []
        for cld in ctx.children[::2]:
            calls.extend(self.__get_list(self.visit(cld)))

        return calls

    def visitResourceSpecification(self, ctx: JavaParser.ResourceSpecificationContext):
        return self.visit(ctx.resources())

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
                calls.extend(self.__get_list(self.visit(cld)))

        return calls

    def visitBlockStatement(self, ctx: JavaParser.BlockStatementContext):
        calls = []

        # Not parsing localTypeDeclaration (Class or Interface)
        if ctx.localVariableDeclaration():
            calls.extend(self.__get_list(self.visit(ctx.localVariableDeclaration())))
        elif ctx.statement():
            calls.extend(self.__get_list(self.visit(ctx.statement())))

        return calls

    def visitBlock(self, ctx: JavaParser.BlockContext):
        if ctx.getChildCount() == 2:
            return []
        else:
            calls = []
            for cld in ctx.children[1:-1]:
                calls.extend(self.__get_list(self.visit(cld)))

            return calls

    def visitMethodBody(self, ctx: JavaParser.MethodBodyContext):
        return self.visit(ctx.block())

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        return_type = self.visit(ctx.typeTypeOrVoid())
        name = self.visit(ctx.IDENTIFIER())
        total_args = self.visit(ctx.formalParameters())
        throws = self.visit(ctx.qualifiedNameList()) if ctx.THROWS() else None
        calls = self.visit(ctx.methodBody())

        return MethodModel(
            name=name,
            return_type=return_type,
            total_args=total_args,
            throws=throws,
            calls=calls,
            loc=ctx.stop.line - ctx.start.line + 1
        )

    def visitGenericMethodDeclaration(self, ctx: JavaParser.GenericMethodDeclarationContext):
        return self.visit(ctx.methodDeclaration())

    def visitFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        return self.visit(ctx.variableDeclarators())

    def visitConstructorDeclaration(self, ctx: JavaParser.ConstructorDeclarationContext):
        return self.visit(ctx.constructorBody)

    def visitGenericConstructorDeclaration(self, ctx: JavaParser.GenericConstructorDeclarationContext):
        return self.visit(ctx.constructorDeclaration())

    def visitMemberDeclaration(self, ctx: JavaParser.MemberDeclarationContext):
        val = ctx.children[0]

        if isinstance(val, JavaParser.MethodDeclarationContext):
            return MemberModel(
                subtype="Method",
                value=self.visit(val)
            )
        elif isinstance(val, JavaParser.GenericMethodDeclarationContext):
            return MemberModel(
                subtype="Method",
                value=self.visit(val)
            )
        elif isinstance(val, JavaParser.FieldDeclarationContext):
            return MemberModel(
                subtype="Call",
                value=self.visit(val)
            )
        elif isinstance(val, JavaParser.ConstructorDeclarationContext):
            return MemberModel(
                subtype="Call",
                value=self.visit(val)
            )

    def visitConstantDeclarator(self, ctx: JavaParser.ConstantDeclaratorContext):
        return self.visit(ctx.variableInitializer())

    def visitConstDeclaration(self, ctx: JavaParser.ConstDeclarationContext):
        calls = []
        for cld in ctx.children:
            if isinstance(cld, JavaParser.ConstantDeclaratorContext):
                calls.extend(self.__get_list(self.visit(cld)))

        return calls

    def visitInterfaceMethodDeclaration(self, ctx: JavaParser.InterfaceMethodDeclarationContext):
        modifiers, calls = [], []

        return_type, throws = None, None
        total_args = 0
        name = self.visit(ctx.IDENTIFIER())

        for cld in ctx.children:
            if isinstance(cld, JavaParser.InterfaceMethodModifierContext):
                modifiers.extend(self.__get_list(self.visit(cld)))
            elif isinstance(cld, JavaParser.TypeTypeOrVoidContext):
                return_type = self.visit(cld)
            elif isinstance(cld, JavaParser.QualifiedNameListContext):
                throws = self.visit(cld)
            elif isinstance(cld, JavaParser.MethodBodyContext):
                calls = self.visit(cld)
            elif isinstance(cld, JavaParser.FormalParametersContext):
                total_args = self.visit(cld)

        return MethodModel(
            name=name,
            modifiers=modifiers,
            return_type=return_type,
            total_args=total_args,
            throws=throws,
            calls=calls,
            loc=ctx.stop.line - ctx.start.line + 1
        )

    def visitGenericInterfaceMethodDeclaration(self, ctx: JavaParser.GenericInterfaceMethodDeclarationContext):
        return self.visit(ctx.interfaceMethodDeclaration())

    def visitInterfaceMemberDeclaration(self, ctx: JavaParser.InterfaceMemberDeclarationContext):
        val = ctx.children[0]

        if isinstance(val, JavaParser.ConstDeclarationContext):
            return MemberModel(
                subtype="Call",
                value=self.visit(val)
            )
        elif isinstance(val, JavaParser.InterfaceMethodDeclarationContext):
            return MemberModel(
                subtype="Method",
                value=self.visit(val)
            )
        elif isinstance(val, JavaParser.GenericMethodDeclarationContext):
            return MemberModel(
                subtype="Method",
                value=self.visit(val)
            )

    def visitModifier(self, ctx: JavaParser.ModifierContext):
        return self.visit(ctx.children[0])

    def visitClassBodyDeclaration(self, ctx: JavaParser.ClassBodyDeclarationContext):
        if not ctx.STATIC():
            modifiers = []
            for cld in ctx.children:
                if isinstance(cld, JavaParser.ModifierContext):
                    modifiers.extend(self.__get_list(self.visit(cld)))

            method, calls = None, []
            member = self.visit(ctx.memberDeclaration())

            if member:
                member: MemberModel
                if member.subtype == "Method":
                    tmp = member.value
                    if tmp.modifiers:
                        tmp.modifiers.extend(self.__get_list(modifiers))
                    else:
                        tmp.modifiers = modifiers

                    method = tmp
                elif member.subtype == "Call":
                    calls.extend(self.__get_list(member.value))

            return BodyModel(
                method=method,
                calls=calls
            )
        else:
            calls = self.visit(ctx.block())

            return BodyModel(
                method=None,
                calls=calls
            )

    def visitInterfaceBodyDeclaration(self, ctx: JavaParser.InterfaceBodyDeclarationContext):
        modifiers = []
        for cld in ctx.children:
            if isinstance(cld, JavaParser.ModifierContext):
                modifiers.extend(self.__get_list(self.visit(cld)))

        method, calls = None, []
        member = self.visit(ctx.interfaceMemberDeclaration())

        if member:
            member: MemberModel
            if member.subtype == "Method":
                tmp: MethodModel = member.value
                tmp.modifiers = modifiers
                method = tmp
            elif member.subtype == "Call":
                calls.extend(self.__get_list(member.value))

        return BodyModel(
            method=method,
            calls=calls
        )

    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        # TODO: Name may be type<annotation>
        name = self.visit(ctx.IDENTIFIER())
        EXT_CLASSES.add(name)  # Used in case of recursion

        extends, implements = None, None

        if ctx.EXTENDS():
            extends = self.visit(ctx.typeType())

        if ctx.IMPLEMENTS():
            implements = self.visit(ctx.typeList())

        methods, calls = [], []

        body = ctx.classBody()
        for cld in body.children[1: -1]:
            val = self.visit(cld)
            if val:
                val: BodyModel
                if val.method:
                    methods.append(val.method)
                elif val.calls:
                    calls.extend(val.calls)

        return ClassModel(
            name=name,
            extends=extends,
            implements=implements,
            methods=methods,
            calls=calls,
            loc=ctx.stop.line - ctx.start.line + 1
        )

    def visitEnumDeclaration(self, ctx: JavaParser.EnumDeclarationContext):
        name = self.visit(ctx.IDENTIFIER())
        EXT_CLASSES.add(name)

        implements = None
        if ctx.IMPLEMENTS():
            implements = self.visit(ctx.typeList())

        methods, calls = [], []

        body = ctx.enumBodyDeclarations()
        if body:
            for cld in body.children[1:]:
                val = self.visit(cld)
                if val:
                    val: BodyModel
                    if val.method:
                        methods.append(val.method)
                    elif val.calls:
                        calls.extend(val.calls)

        return EnumModel(
            name=name,
            implements=implements,
            methods=methods,
            calls=calls,
            loc=ctx.stop.line - ctx.start.line + 1
        )

    def visitInterfaceDeclaration(self, ctx: JavaParser.InterfaceDeclarationContext):
        name = self.visit(ctx.IDENTIFIER())
        EXT_CLASSES.add(name)

        extends = None

        if ctx.EXTENDS():
            extends = self.visit(ctx.typeList())

        methods, calls = [], []

        body = ctx.interfaceBody()
        for cld in body.children[1:-1]:
            val = self.visit(cld)
            if val:
                val: BodyModel
                if val.method:
                    methods.append(val.method)
                elif val.calls:
                    calls.extend(val.calls)

        return InterfaceModel(
            name=name,
            extends=extends,
            methods=methods,
            calls=calls,
            loc=ctx.stop.line - ctx.start.line + 1
        )

    def visitAnnotationConstantRest(self, ctx: JavaParser.AnnotationConstantRestContext):
        calls = self.visit(ctx.variableDeclarators())

        return BodyModel(
            method=None,
            calls=calls
        )

    def visitAnnotationMethodOrConstantRest(self, ctx: JavaParser.AnnotationMethodOrConstantRestContext):
        if ctx.annotationConstantRest():
            return self.visit(ctx.annotationConstantRest())

    def visitAnnotationTypeElementRest(self, ctx: JavaParser.AnnotationTypeElementRestContext):
        if ctx.annotationMethodOrConstantRest():
            return self.visit(ctx.annotationMethodOrConstantRest())

    def visitAnnotationTypeElementDeclaration(self, ctx: JavaParser.AnnotationTypeElementDeclarationContext):
        if ctx.annotationTypeElementRest():
            return self.visit(ctx.annotationTypeElementRest())

    def visitAnnotationTypeDeclaration(self, ctx: JavaParser.AnnotationTypeDeclarationContext):
        name = self.visit(ctx.IDENTIFIER())

        calls = []

        body = ctx.annotationTypeBody()
        for cld in body.children[1:-1]:
            val = self.visit(cld)
            if val:
                val: BodyModel
                if val.calls:
                    calls.extend(self.__get_list(val.calls))

        return AnnotationTypeModel(
            name=name,
            calls=calls,
            loc=ctx.stop.line - ctx.start.line + 1
        )

    def visitTypeDeclaration(self, ctx: JavaParser.TypeDeclarationContext):
        modifiers = []
        node = None

        for cld in ctx.children:
            if isinstance(cld, JavaParser.ClassOrInterfaceModifierContext):
                modifiers.extend(self.__get_list(self.visit(cld)))
            elif isinstance(cld, JavaParser.ClassDeclarationContext):
                node = self.visit(cld)
                node.modifiers = modifiers
            elif isinstance(cld, JavaParser.EnumDeclarationContext):
                node = self.visit(cld)
                node.modifiers = modifiers
            elif isinstance(cld, JavaParser.InterfaceDeclarationContext):
                node = self.visit(cld)
                node.modifiers = modifiers
            elif isinstance(cld, JavaParser.AnnotationTypeDeclarationContext):
                node = self.visit(cld)
                node.modifiers = modifiers

        return node
