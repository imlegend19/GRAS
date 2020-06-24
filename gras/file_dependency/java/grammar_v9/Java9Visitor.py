# Generated from Java9.g4 by ANTLR 4.7.1
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .Java9Parser import Java9Parser
else:
    from Java9Parser import Java9Parser


# This class defines a complete generic visitor for a parse tree produced by Java9Parser.

class Java9Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by Java9Parser#literal.
    def visitLiteral(self, ctx: Java9Parser.LiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primitiveType.
    def visitPrimitiveType(self, ctx: Java9Parser.PrimitiveTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#numericType.
    def visitNumericType(self, ctx: Java9Parser.NumericTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#integralType.
    def visitIntegralType(self, ctx: Java9Parser.IntegralTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#floatingPointType.
    def visitFloatingPointType(self, ctx: Java9Parser.FloatingPointTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#referenceType.
    def visitReferenceType(self, ctx: Java9Parser.ReferenceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classOrInterfaceType.
    def visitClassOrInterfaceType(self, ctx: Java9Parser.ClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classType.
    def visitClassType(self, ctx: Java9Parser.ClassTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classType_lf_classOrInterfaceType.
    def visitClassType_lf_classOrInterfaceType(self, ctx: Java9Parser.ClassType_lf_classOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classType_lfno_classOrInterfaceType.
    def visitClassType_lfno_classOrInterfaceType(self, ctx: Java9Parser.ClassType_lfno_classOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceType.
    def visitInterfaceType(self, ctx: Java9Parser.InterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceType_lf_classOrInterfaceType.
    def visitInterfaceType_lf_classOrInterfaceType(self, ctx: Java9Parser.InterfaceType_lf_classOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceType_lfno_classOrInterfaceType.
    def visitInterfaceType_lfno_classOrInterfaceType(self,
                                                     ctx: Java9Parser.InterfaceType_lfno_classOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeVariable.
    def visitTypeVariable(self, ctx: Java9Parser.TypeVariableContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#arrayType.
    def visitArrayType(self, ctx: Java9Parser.ArrayTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#dims.
    def visitDims(self, ctx: Java9Parser.DimsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeParameter.
    def visitTypeParameter(self, ctx: Java9Parser.TypeParameterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeParameterModifier.
    def visitTypeParameterModifier(self, ctx: Java9Parser.TypeParameterModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeBound.
    def visitTypeBound(self, ctx: Java9Parser.TypeBoundContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#additionalBound.
    def visitAdditionalBound(self, ctx: Java9Parser.AdditionalBoundContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeArguments.
    def visitTypeArguments(self, ctx: Java9Parser.TypeArgumentsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeArgumentList.
    def visitTypeArgumentList(self, ctx: Java9Parser.TypeArgumentListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeArgument.
    def visitTypeArgument(self, ctx: Java9Parser.TypeArgumentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#wildcard.
    def visitWildcard(self, ctx: Java9Parser.WildcardContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#wildcardBounds.
    def visitWildcardBounds(self, ctx: Java9Parser.WildcardBoundsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#moduleName.
    def visitModuleName(self, ctx: Java9Parser.ModuleNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#packageName.
    def visitPackageName(self, ctx: Java9Parser.PackageNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeName.
    def visitTypeName(self, ctx: Java9Parser.TypeNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#packageOrTypeName.
    def visitPackageOrTypeName(self, ctx: Java9Parser.PackageOrTypeNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#expressionName.
    def visitExpressionName(self, ctx: Java9Parser.ExpressionNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodName.
    def visitMethodName(self, ctx: Java9Parser.MethodNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#ambiguousName.
    def visitAmbiguousName(self, ctx: Java9Parser.AmbiguousNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#compilationUnit.
    def visitCompilationUnit(self, ctx: Java9Parser.CompilationUnitContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#ordinaryCompilation.
    def visitOrdinaryCompilation(self, ctx: Java9Parser.OrdinaryCompilationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#modularCompilation.
    def visitModularCompilation(self, ctx: Java9Parser.ModularCompilationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#packageDeclaration.
    def visitPackageDeclaration(self, ctx: Java9Parser.PackageDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#packageModifier.
    def visitPackageModifier(self, ctx: Java9Parser.PackageModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#importDeclaration.
    def visitImportDeclaration(self, ctx: Java9Parser.ImportDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#singleTypeImportDeclaration.
    def visitSingleTypeImportDeclaration(self, ctx: Java9Parser.SingleTypeImportDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeImportOnDemandDeclaration.
    def visitTypeImportOnDemandDeclaration(self, ctx: Java9Parser.TypeImportOnDemandDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#singleStaticImportDeclaration.
    def visitSingleStaticImportDeclaration(self, ctx: Java9Parser.SingleStaticImportDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#staticImportOnDemandDeclaration.
    def visitStaticImportOnDemandDeclaration(self, ctx: Java9Parser.StaticImportOnDemandDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeDeclaration.
    def visitTypeDeclaration(self, ctx: Java9Parser.TypeDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#moduleDeclaration.
    def visitModuleDeclaration(self, ctx: Java9Parser.ModuleDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#moduleDirective.
    def visitModuleDirective(self, ctx: Java9Parser.ModuleDirectiveContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#requiresModifier.
    def visitRequiresModifier(self, ctx: Java9Parser.RequiresModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classDeclaration.
    def visitClassDeclaration(self, ctx: Java9Parser.ClassDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#normalClassDeclaration.
    def visitNormalClassDeclaration(self, ctx: Java9Parser.NormalClassDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classModifier.
    def visitClassModifier(self, ctx: Java9Parser.ClassModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeParameters.
    def visitTypeParameters(self, ctx: Java9Parser.TypeParametersContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeParameterList.
    def visitTypeParameterList(self, ctx: Java9Parser.TypeParameterListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#superclass.
    def visitSuperclass(self, ctx: Java9Parser.SuperclassContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#superinterfaces.
    def visitSuperinterfaces(self, ctx: Java9Parser.SuperinterfacesContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceTypeList.
    def visitInterfaceTypeList(self, ctx: Java9Parser.InterfaceTypeListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classBody.
    def visitClassBody(self, ctx: Java9Parser.ClassBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classBodyDeclaration.
    def visitClassBodyDeclaration(self, ctx: Java9Parser.ClassBodyDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classMemberDeclaration.
    def visitClassMemberDeclaration(self, ctx: Java9Parser.ClassMemberDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#fieldDeclaration.
    def visitFieldDeclaration(self, ctx: Java9Parser.FieldDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#fieldModifier.
    def visitFieldModifier(self, ctx: Java9Parser.FieldModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#variableDeclaratorList.
    def visitVariableDeclaratorList(self, ctx: Java9Parser.VariableDeclaratorListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#variableDeclarator.
    def visitVariableDeclarator(self, ctx: Java9Parser.VariableDeclaratorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#variableDeclaratorId.
    def visitVariableDeclaratorId(self, ctx: Java9Parser.VariableDeclaratorIdContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#variableInitializer.
    def visitVariableInitializer(self, ctx: Java9Parser.VariableInitializerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannType.
    def visitUnannType(self, ctx: Java9Parser.UnannTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannPrimitiveType.
    def visitUnannPrimitiveType(self, ctx: Java9Parser.UnannPrimitiveTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannReferenceType.
    def visitUnannReferenceType(self, ctx: Java9Parser.UnannReferenceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannClassOrInterfaceType.
    def visitUnannClassOrInterfaceType(self, ctx: Java9Parser.UnannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannClassType.
    def visitUnannClassType(self, ctx: Java9Parser.UnannClassTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannClassType_lf_unannClassOrInterfaceType.
    def visitUnannClassType_lf_unannClassOrInterfaceType(self,
                                                         ctx:
                                                         Java9Parser.UnannClassType_lf_unannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannClassType_lfno_unannClassOrInterfaceType.
    def visitUnannClassType_lfno_unannClassOrInterfaceType(self,
                                                           ctx:
                                                           Java9Parser.UnannClassType_lfno_unannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannInterfaceType.
    def visitUnannInterfaceType(self, ctx: Java9Parser.UnannInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannInterfaceType_lf_unannClassOrInterfaceType.
    def visitUnannInterfaceType_lf_unannClassOrInterfaceType(self,
                                                             ctx:
                                                             Java9Parser.UnannInterfaceType_lf_unannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannInterfaceType_lfno_unannClassOrInterfaceType.
    def visitUnannInterfaceType_lfno_unannClassOrInterfaceType(self,
                                                               ctx:
                                                               Java9Parser.UnannInterfaceType_lfno_unannClassOrInterfaceTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannTypeVariable.
    def visitUnannTypeVariable(self, ctx: Java9Parser.UnannTypeVariableContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unannArrayType.
    def visitUnannArrayType(self, ctx: Java9Parser.UnannArrayTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodDeclaration.
    def visitMethodDeclaration(self, ctx: Java9Parser.MethodDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodModifier.
    def visitMethodModifier(self, ctx: Java9Parser.MethodModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodHeader.
    def visitMethodHeader(self, ctx: Java9Parser.MethodHeaderContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#result.
    def visitResult(self, ctx: Java9Parser.ResultContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodDeclarator.
    def visitMethodDeclarator(self, ctx: Java9Parser.MethodDeclaratorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#formalParameterList.
    def visitFormalParameterList(self, ctx: Java9Parser.FormalParameterListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#formalParameters.
    def visitFormalParameters(self, ctx: Java9Parser.FormalParametersContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#formalParameter.
    def visitFormalParameter(self, ctx: Java9Parser.FormalParameterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#variableModifier.
    def visitVariableModifier(self, ctx: Java9Parser.VariableModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#lastFormalParameter.
    def visitLastFormalParameter(self, ctx: Java9Parser.LastFormalParameterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#receiverParameter.
    def visitReceiverParameter(self, ctx: Java9Parser.ReceiverParameterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#throws_.
    def visitThrows_(self, ctx: Java9Parser.Throws_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#exceptionTypeList.
    def visitExceptionTypeList(self, ctx: Java9Parser.ExceptionTypeListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#exceptionType.
    def visitExceptionType(self, ctx: Java9Parser.ExceptionTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodBody.
    def visitMethodBody(self, ctx: Java9Parser.MethodBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#instanceInitializer.
    def visitInstanceInitializer(self, ctx: Java9Parser.InstanceInitializerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#staticInitializer.
    def visitStaticInitializer(self, ctx: Java9Parser.StaticInitializerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#constructorDeclaration.
    def visitConstructorDeclaration(self, ctx: Java9Parser.ConstructorDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#constructorModifier.
    def visitConstructorModifier(self, ctx: Java9Parser.ConstructorModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#constructorDeclarator.
    def visitConstructorDeclarator(self, ctx: Java9Parser.ConstructorDeclaratorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#simpleTypeName.
    def visitSimpleTypeName(self, ctx: Java9Parser.SimpleTypeNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#constructorBody.
    def visitConstructorBody(self, ctx: Java9Parser.ConstructorBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#explicitConstructorInvocation.
    def visitExplicitConstructorInvocation(self, ctx: Java9Parser.ExplicitConstructorInvocationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enumDeclaration.
    def visitEnumDeclaration(self, ctx: Java9Parser.EnumDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enumBody.
    def visitEnumBody(self, ctx: Java9Parser.EnumBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enumConstantList.
    def visitEnumConstantList(self, ctx: Java9Parser.EnumConstantListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enumConstant.
    def visitEnumConstant(self, ctx: Java9Parser.EnumConstantContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enumConstantModifier.
    def visitEnumConstantModifier(self, ctx: Java9Parser.EnumConstantModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enumBodyDeclarations.
    def visitEnumBodyDeclarations(self, ctx: Java9Parser.EnumBodyDeclarationsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceDeclaration.
    def visitInterfaceDeclaration(self, ctx: Java9Parser.InterfaceDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#normalInterfaceDeclaration.
    def visitNormalInterfaceDeclaration(self, ctx: Java9Parser.NormalInterfaceDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceModifier.
    def visitInterfaceModifier(self, ctx: Java9Parser.InterfaceModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#extendsInterfaces.
    def visitExtendsInterfaces(self, ctx: Java9Parser.ExtendsInterfacesContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceBody.
    def visitInterfaceBody(self, ctx: Java9Parser.InterfaceBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceMemberDeclaration.
    def visitInterfaceMemberDeclaration(self, ctx: Java9Parser.InterfaceMemberDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#constantDeclaration.
    def visitConstantDeclaration(self, ctx: Java9Parser.ConstantDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#constantModifier.
    def visitConstantModifier(self, ctx: Java9Parser.ConstantModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceMethodDeclaration.
    def visitInterfaceMethodDeclaration(self, ctx: Java9Parser.InterfaceMethodDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#interfaceMethodModifier.
    def visitInterfaceMethodModifier(self, ctx: Java9Parser.InterfaceMethodModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#annotationTypeDeclaration.
    def visitAnnotationTypeDeclaration(self, ctx: Java9Parser.AnnotationTypeDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#annotationTypeBody.
    def visitAnnotationTypeBody(self, ctx: Java9Parser.AnnotationTypeBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#annotationTypeMemberDeclaration.
    def visitAnnotationTypeMemberDeclaration(self, ctx: Java9Parser.AnnotationTypeMemberDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#annotationTypeElementDeclaration.
    def visitAnnotationTypeElementDeclaration(self, ctx: Java9Parser.AnnotationTypeElementDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#annotationTypeElementModifier.
    def visitAnnotationTypeElementModifier(self, ctx: Java9Parser.AnnotationTypeElementModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#defaultValue.
    def visitDefaultValue(self, ctx: Java9Parser.DefaultValueContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#annotation.
    def visitAnnotation(self, ctx: Java9Parser.AnnotationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#normalAnnotation.
    def visitNormalAnnotation(self, ctx: Java9Parser.NormalAnnotationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#elementValuePairList.
    def visitElementValuePairList(self, ctx: Java9Parser.ElementValuePairListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#elementValuePair.
    def visitElementValuePair(self, ctx: Java9Parser.ElementValuePairContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#elementValue.
    def visitElementValue(self, ctx: Java9Parser.ElementValueContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#elementValueArrayInitializer.
    def visitElementValueArrayInitializer(self, ctx: Java9Parser.ElementValueArrayInitializerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#elementValueList.
    def visitElementValueList(self, ctx: Java9Parser.ElementValueListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#markerAnnotation.
    def visitMarkerAnnotation(self, ctx: Java9Parser.MarkerAnnotationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#singleElementAnnotation.
    def visitSingleElementAnnotation(self, ctx: Java9Parser.SingleElementAnnotationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#arrayInitializer.
    def visitArrayInitializer(self, ctx: Java9Parser.ArrayInitializerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#variableInitializerList.
    def visitVariableInitializerList(self, ctx: Java9Parser.VariableInitializerListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#block.
    def visitBlock(self, ctx: Java9Parser.BlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#blockStatements.
    def visitBlockStatements(self, ctx: Java9Parser.BlockStatementsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#blockStatement.
    def visitBlockStatement(self, ctx: Java9Parser.BlockStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#localVariableDeclarationStatement.
    def visitLocalVariableDeclarationStatement(self, ctx: Java9Parser.LocalVariableDeclarationStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#localVariableDeclaration.
    def visitLocalVariableDeclaration(self, ctx: Java9Parser.LocalVariableDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#statement.
    def visitStatement(self, ctx: Java9Parser.StatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#statementNoShortIf.
    def visitStatementNoShortIf(self, ctx: Java9Parser.StatementNoShortIfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#statementWithoutTrailingSubstatement.
    def visitStatementWithoutTrailingSubstatement(self, ctx: Java9Parser.StatementWithoutTrailingSubstatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#emptyStatement.
    def visitEmptyStatement(self, ctx: Java9Parser.EmptyStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#labeledStatement.
    def visitLabeledStatement(self, ctx: Java9Parser.LabeledStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#labeledStatementNoShortIf.
    def visitLabeledStatementNoShortIf(self, ctx: Java9Parser.LabeledStatementNoShortIfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#expressionStatement.
    def visitExpressionStatement(self, ctx: Java9Parser.ExpressionStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#statementExpression.
    def visitStatementExpression(self, ctx: Java9Parser.StatementExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#ifThenStatement.
    def visitIfThenStatement(self, ctx: Java9Parser.IfThenStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#ifThenElseStatement.
    def visitIfThenElseStatement(self, ctx: Java9Parser.IfThenElseStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#ifThenElseStatementNoShortIf.
    def visitIfThenElseStatementNoShortIf(self, ctx: Java9Parser.IfThenElseStatementNoShortIfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#assertStatement.
    def visitAssertStatement(self, ctx: Java9Parser.AssertStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#switchStatement.
    def visitSwitchStatement(self, ctx: Java9Parser.SwitchStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#switchBlock.
    def visitSwitchBlock(self, ctx: Java9Parser.SwitchBlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#switchBlockStatementGroup.
    def visitSwitchBlockStatementGroup(self, ctx: Java9Parser.SwitchBlockStatementGroupContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#switchLabels.
    def visitSwitchLabels(self, ctx: Java9Parser.SwitchLabelsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#switchLabel.
    def visitSwitchLabel(self, ctx: Java9Parser.SwitchLabelContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enumConstantName.
    def visitEnumConstantName(self, ctx: Java9Parser.EnumConstantNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#whileStatement.
    def visitWhileStatement(self, ctx: Java9Parser.WhileStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#whileStatementNoShortIf.
    def visitWhileStatementNoShortIf(self, ctx: Java9Parser.WhileStatementNoShortIfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#doStatement.
    def visitDoStatement(self, ctx: Java9Parser.DoStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#forStatement.
    def visitForStatement(self, ctx: Java9Parser.ForStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#forStatementNoShortIf.
    def visitForStatementNoShortIf(self, ctx: Java9Parser.ForStatementNoShortIfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#basicForStatement.
    def visitBasicForStatement(self, ctx: Java9Parser.BasicForStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#basicForStatementNoShortIf.
    def visitBasicForStatementNoShortIf(self, ctx: Java9Parser.BasicForStatementNoShortIfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#forInit.
    def visitForInit(self, ctx: Java9Parser.ForInitContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#forUpdate.
    def visitForUpdate(self, ctx: Java9Parser.ForUpdateContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#statementExpressionList.
    def visitStatementExpressionList(self, ctx: Java9Parser.StatementExpressionListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enhancedForStatement.
    def visitEnhancedForStatement(self, ctx: Java9Parser.EnhancedForStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#enhancedForStatementNoShortIf.
    def visitEnhancedForStatementNoShortIf(self, ctx: Java9Parser.EnhancedForStatementNoShortIfContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#breakStatement.
    def visitBreakStatement(self, ctx: Java9Parser.BreakStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#continueStatement.
    def visitContinueStatement(self, ctx: Java9Parser.ContinueStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#returnStatement.
    def visitReturnStatement(self, ctx: Java9Parser.ReturnStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#throwStatement.
    def visitThrowStatement(self, ctx: Java9Parser.ThrowStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#synchronizedStatement.
    def visitSynchronizedStatement(self, ctx: Java9Parser.SynchronizedStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#tryStatement.
    def visitTryStatement(self, ctx: Java9Parser.TryStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#catches.
    def visitCatches(self, ctx: Java9Parser.CatchesContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#catchClause.
    def visitCatchClause(self, ctx: Java9Parser.CatchClauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#catchFormalParameter.
    def visitCatchFormalParameter(self, ctx: Java9Parser.CatchFormalParameterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#catchType.
    def visitCatchType(self, ctx: Java9Parser.CatchTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#finally_.
    def visitFinally_(self, ctx: Java9Parser.Finally_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#tryWithResourcesStatement.
    def visitTryWithResourcesStatement(self, ctx: Java9Parser.TryWithResourcesStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#resourceSpecification.
    def visitResourceSpecification(self, ctx: Java9Parser.ResourceSpecificationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#resourceList.
    def visitResourceList(self, ctx: Java9Parser.ResourceListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#resource.
    def visitResource(self, ctx: Java9Parser.ResourceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#variableAccess.
    def visitVariableAccess(self, ctx: Java9Parser.VariableAccessContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primary.
    def visitPrimary(self, ctx: Java9Parser.PrimaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray.
    def visitPrimaryNoNewArray(self, ctx: Java9Parser.PrimaryNoNewArrayContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray_lf_arrayAccess.
    def visitPrimaryNoNewArray_lf_arrayAccess(self, ctx: Java9Parser.PrimaryNoNewArray_lf_arrayAccessContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray_lfno_arrayAccess.
    def visitPrimaryNoNewArray_lfno_arrayAccess(self, ctx: Java9Parser.PrimaryNoNewArray_lfno_arrayAccessContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray_lf_primary.
    def visitPrimaryNoNewArray_lf_primary(self, ctx: Java9Parser.PrimaryNoNewArray_lf_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray_lf_primary_lf_arrayAccess_lf_primary.
    def visitPrimaryNoNewArray_lf_primary_lf_arrayAccess_lf_primary(self,
                                                                    ctx:
                                                                    Java9Parser.PrimaryNoNewArray_lf_primary_lf_arrayAccess_lf_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray_lf_primary_lfno_arrayAccess_lf_primary.
    def visitPrimaryNoNewArray_lf_primary_lfno_arrayAccess_lf_primary(self,
                                                                      ctx:
                                                                      Java9Parser.PrimaryNoNewArray_lf_primary_lfno_arrayAccess_lf_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray_lfno_primary.
    def visitPrimaryNoNewArray_lfno_primary(self, ctx: Java9Parser.PrimaryNoNewArray_lfno_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray_lfno_primary_lf_arrayAccess_lfno_primary.
    def visitPrimaryNoNewArray_lfno_primary_lf_arrayAccess_lfno_primary(self,
                                                                        ctx:
                                                                        Java9Parser.PrimaryNoNewArray_lfno_primary_lf_arrayAccess_lfno_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#primaryNoNewArray_lfno_primary_lfno_arrayAccess_lfno_primary.
    def visitPrimaryNoNewArray_lfno_primary_lfno_arrayAccess_lfno_primary(self,
                                                                          ctx:
                                                                          Java9Parser.PrimaryNoNewArray_lfno_primary_lfno_arrayAccess_lfno_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classLiteral.
    def visitClassLiteral(self, ctx: Java9Parser.ClassLiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classInstanceCreationExpression.
    def visitClassInstanceCreationExpression(self, ctx: Java9Parser.ClassInstanceCreationExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classInstanceCreationExpression_lf_primary.
    def visitClassInstanceCreationExpression_lf_primary(self,
                                                        ctx:
                                                        Java9Parser.ClassInstanceCreationExpression_lf_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#classInstanceCreationExpression_lfno_primary.
    def visitClassInstanceCreationExpression_lfno_primary(self,
                                                          ctx:
                                                          Java9Parser.ClassInstanceCreationExpression_lfno_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#typeArgumentsOrDiamond.
    def visitTypeArgumentsOrDiamond(self, ctx: Java9Parser.TypeArgumentsOrDiamondContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#fieldAccess.
    def visitFieldAccess(self, ctx: Java9Parser.FieldAccessContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#fieldAccess_lf_primary.
    def visitFieldAccess_lf_primary(self, ctx: Java9Parser.FieldAccess_lf_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#fieldAccess_lfno_primary.
    def visitFieldAccess_lfno_primary(self, ctx: Java9Parser.FieldAccess_lfno_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#arrayAccess.
    def visitArrayAccess(self, ctx: Java9Parser.ArrayAccessContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#arrayAccess_lf_primary.
    def visitArrayAccess_lf_primary(self, ctx: Java9Parser.ArrayAccess_lf_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#arrayAccess_lfno_primary.
    def visitArrayAccess_lfno_primary(self, ctx: Java9Parser.ArrayAccess_lfno_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodInvocation.
    def visitMethodInvocation(self, ctx: Java9Parser.MethodInvocationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodInvocation_lf_primary.
    def visitMethodInvocation_lf_primary(self, ctx: Java9Parser.MethodInvocation_lf_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodInvocation_lfno_primary.
    def visitMethodInvocation_lfno_primary(self, ctx: Java9Parser.MethodInvocation_lfno_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#argumentList.
    def visitArgumentList(self, ctx: Java9Parser.ArgumentListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodReference.
    def visitMethodReference(self, ctx: Java9Parser.MethodReferenceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodReference_lf_primary.
    def visitMethodReference_lf_primary(self, ctx: Java9Parser.MethodReference_lf_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#methodReference_lfno_primary.
    def visitMethodReference_lfno_primary(self, ctx: Java9Parser.MethodReference_lfno_primaryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#arrayCreationExpression.
    def visitArrayCreationExpression(self, ctx: Java9Parser.ArrayCreationExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#dimExprs.
    def visitDimExprs(self, ctx: Java9Parser.DimExprsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#dimExpr.
    def visitDimExpr(self, ctx: Java9Parser.DimExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#constantExpression.
    def visitConstantExpression(self, ctx: Java9Parser.ConstantExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#expression.
    def visitExpression(self, ctx: Java9Parser.ExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#lambdaExpression.
    def visitLambdaExpression(self, ctx: Java9Parser.LambdaExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#lambdaParameters.
    def visitLambdaParameters(self, ctx: Java9Parser.LambdaParametersContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#inferredFormalParameterList.
    def visitInferredFormalParameterList(self, ctx: Java9Parser.InferredFormalParameterListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#lambdaBody.
    def visitLambdaBody(self, ctx: Java9Parser.LambdaBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#assignmentExpression.
    def visitAssignmentExpression(self, ctx: Java9Parser.AssignmentExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#assignment.
    def visitAssignment(self, ctx: Java9Parser.AssignmentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#leftHandSide.
    def visitLeftHandSide(self, ctx: Java9Parser.LeftHandSideContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#assignmentOperator.
    def visitAssignmentOperator(self, ctx: Java9Parser.AssignmentOperatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#conditionalExpression.
    def visitConditionalExpression(self, ctx: Java9Parser.ConditionalExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#conditionalOrExpression.
    def visitConditionalOrExpression(self, ctx: Java9Parser.ConditionalOrExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#conditionalAndExpression.
    def visitConditionalAndExpression(self, ctx: Java9Parser.ConditionalAndExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#inclusiveOrExpression.
    def visitInclusiveOrExpression(self, ctx: Java9Parser.InclusiveOrExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#exclusiveOrExpression.
    def visitExclusiveOrExpression(self, ctx: Java9Parser.ExclusiveOrExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#andExpression.
    def visitAndExpression(self, ctx: Java9Parser.AndExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#equalityExpression.
    def visitEqualityExpression(self, ctx: Java9Parser.EqualityExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#relationalExpression.
    def visitRelationalExpression(self, ctx: Java9Parser.RelationalExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#shiftExpression.
    def visitShiftExpression(self, ctx: Java9Parser.ShiftExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#additiveExpression.
    def visitAdditiveExpression(self, ctx: Java9Parser.AdditiveExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx: Java9Parser.MultiplicativeExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unaryExpression.
    def visitUnaryExpression(self, ctx: Java9Parser.UnaryExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#preIncrementExpression.
    def visitPreIncrementExpression(self, ctx: Java9Parser.PreIncrementExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#preDecrementExpression.
    def visitPreDecrementExpression(self, ctx: Java9Parser.PreDecrementExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#unaryExpressionNotPlusMinus.
    def visitUnaryExpressionNotPlusMinus(self, ctx: Java9Parser.UnaryExpressionNotPlusMinusContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#postfixExpression.
    def visitPostfixExpression(self, ctx: Java9Parser.PostfixExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#postIncrementExpression.
    def visitPostIncrementExpression(self, ctx: Java9Parser.PostIncrementExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#postIncrementExpression_lf_postfixExpression.
    def visitPostIncrementExpression_lf_postfixExpression(self,
                                                          ctx:
                                                          Java9Parser.PostIncrementExpression_lf_postfixExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#postDecrementExpression.
    def visitPostDecrementExpression(self, ctx: Java9Parser.PostDecrementExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#postDecrementExpression_lf_postfixExpression.
    def visitPostDecrementExpression_lf_postfixExpression(self,
                                                          ctx: Java9Parser.PostDecrementExpression_lf_postfixExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#castExpression.
    def visitCastExpression(self, ctx: Java9Parser.CastExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Java9Parser#identifier.
    def visitIdentifier(self, ctx: Java9Parser.IdentifierContext):
        return self.visitChildren(ctx)


del Java9Parser
