# Generated from JavaScriptParser.g4 by ANTLR 4.7.1
from antlr4 import *

from gras.file_dependency.javascript.grammar.JavaScriptParser import JavaScriptParser


# This class defines a complete generic visitor for a parse tree produced by JavaScriptParser.
class JavaScriptParserVisitor(ParseTreeVisitor):
    # Visit a parse tree produced by JavaScriptParser#program.
    def visitProgram(self, ctx: JavaScriptParser.ProgramContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#sourceElement.
    def visitSourceElement(self, ctx: JavaScriptParser.SourceElementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#statement.
    def visitStatement(self, ctx: JavaScriptParser.StatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#block.
    def visitBlock(self, ctx: JavaScriptParser.BlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#statementList.
    def visitStatementList(self, ctx: JavaScriptParser.StatementListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#importStatement.
    def visitImportStatement(self, ctx: JavaScriptParser.ImportStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#importFromBlock.
    def visitImportFromBlock(self, ctx: JavaScriptParser.ImportFromBlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#moduleItems.
    def visitModuleItems(self, ctx: JavaScriptParser.ModuleItemsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#importDefault.
    def visitImportDefault(self, ctx: JavaScriptParser.ImportDefaultContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#importNamespace.
    def visitImportNamespace(self, ctx: JavaScriptParser.ImportNamespaceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#importFrom.
    def visitImportFrom(self, ctx: JavaScriptParser.ImportFromContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#aliasName.
    def visitAliasName(self, ctx: JavaScriptParser.AliasNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ExportDeclaration.
    def visitExportDeclaration(self, ctx: JavaScriptParser.ExportDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ExportDefaultDeclaration.
    def visitExportDefaultDeclaration(self, ctx: JavaScriptParser.ExportDefaultDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#exportFromBlock.
    def visitExportFromBlock(self, ctx: JavaScriptParser.ExportFromBlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#declaration.
    def visitDeclaration(self, ctx: JavaScriptParser.DeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#variableStatement.
    def visitVariableStatement(self, ctx: JavaScriptParser.VariableStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#variableDeclarationList.
    def visitVariableDeclarationList(self, ctx: JavaScriptParser.VariableDeclarationListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#variableDeclaration.
    def visitVariableDeclaration(self, ctx: JavaScriptParser.VariableDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#emptyStatement.
    def visitEmptyStatement(self, ctx: JavaScriptParser.EmptyStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#expressionStatement.
    def visitExpressionStatement(self, ctx: JavaScriptParser.ExpressionStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ifStatement.
    def visitIfStatement(self, ctx: JavaScriptParser.IfStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#DoStatement.
    def visitDoStatement(self, ctx: JavaScriptParser.DoStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#WhileStatement.
    def visitWhileStatement(self, ctx: JavaScriptParser.WhileStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ForStatement.
    def visitForStatement(self, ctx: JavaScriptParser.ForStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ForInStatement.
    def visitForInStatement(self, ctx: JavaScriptParser.ForInStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ForOfStatement.
    def visitForOfStatement(self, ctx: JavaScriptParser.ForOfStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#varModifier.
    def visitVarModifier(self, ctx: JavaScriptParser.VarModifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#continueStatement.
    def visitContinueStatement(self, ctx: JavaScriptParser.ContinueStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#breakStatement.
    def visitBreakStatement(self, ctx: JavaScriptParser.BreakStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#returnStatement.
    def visitReturnStatement(self, ctx: JavaScriptParser.ReturnStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#yieldStatement.
    def visitYieldStatement(self, ctx: JavaScriptParser.YieldStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#withStatement.
    def visitWithStatement(self, ctx: JavaScriptParser.WithStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#switchStatement.
    def visitSwitchStatement(self, ctx: JavaScriptParser.SwitchStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#caseBlock.
    def visitCaseBlock(self, ctx: JavaScriptParser.CaseBlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#caseClauses.
    def visitCaseClauses(self, ctx: JavaScriptParser.CaseClausesContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#caseClause.
    def visitCaseClause(self, ctx: JavaScriptParser.CaseClauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#defaultClause.
    def visitDefaultClause(self, ctx: JavaScriptParser.DefaultClauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#labelledStatement.
    def visitLabelledStatement(self, ctx: JavaScriptParser.LabelledStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#throwStatement.
    def visitThrowStatement(self, ctx: JavaScriptParser.ThrowStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#tryStatement.
    def visitTryStatement(self, ctx: JavaScriptParser.TryStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#catchProduction.
    def visitCatchProduction(self, ctx: JavaScriptParser.CatchProductionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#finallyProduction.
    def visitFinallyProduction(self, ctx: JavaScriptParser.FinallyProductionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#debuggerStatement.
    def visitDebuggerStatement(self, ctx: JavaScriptParser.DebuggerStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#functionDeclaration.
    def visitFunctionDeclaration(self, ctx: JavaScriptParser.FunctionDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#classDeclaration.
    def visitClassDeclaration(self, ctx: JavaScriptParser.ClassDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#classTail.
    def visitClassTail(self, ctx: JavaScriptParser.ClassTailContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#classElement.
    def visitClassElement(self, ctx: JavaScriptParser.ClassElementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#methodDefinition.
    def visitMethodDefinition(self, ctx: JavaScriptParser.MethodDefinitionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#formalParameterList.
    def visitFormalParameterList(self, ctx: JavaScriptParser.FormalParameterListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#formalParameterArg.
    def visitFormalParameterArg(self, ctx: JavaScriptParser.FormalParameterArgContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#lastFormalParameterArg.
    def visitLastFormalParameterArg(self, ctx: JavaScriptParser.LastFormalParameterArgContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#functionBody.
    def visitFunctionBody(self, ctx: JavaScriptParser.FunctionBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#sourceElements.
    def visitSourceElements(self, ctx: JavaScriptParser.SourceElementsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#arrayLiteral.
    def visitArrayLiteral(self, ctx: JavaScriptParser.ArrayLiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#elementList.
    def visitElementList(self, ctx: JavaScriptParser.ElementListContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#arrayElement.
    def visitArrayElement(self, ctx: JavaScriptParser.ArrayElementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PropertyExpressionAssignment.
    def visitPropertyExpressionAssignment(self, ctx: JavaScriptParser.PropertyExpressionAssignmentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ComputedPropertyExpressionAssignment.
    def visitComputedPropertyExpressionAssignment(self,
                                                  ctx: JavaScriptParser.ComputedPropertyExpressionAssignmentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#FunctionProperty.
    def visitFunctionProperty(self, ctx: JavaScriptParser.FunctionPropertyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PropertyGetter.
    def visitPropertyGetter(self, ctx: JavaScriptParser.PropertyGetterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PropertySetter.
    def visitPropertySetter(self, ctx: JavaScriptParser.PropertySetterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PropertyShorthand.
    def visitPropertyShorthand(self, ctx: JavaScriptParser.PropertyShorthandContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#propertyName.
    def visitPropertyName(self, ctx: JavaScriptParser.PropertyNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#arguments.
    def visitArguments(self, ctx: JavaScriptParser.ArgumentsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#argument.
    def visitArgument(self, ctx: JavaScriptParser.ArgumentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#expressionSequence.
    def visitExpressionSequence(self, ctx: JavaScriptParser.ExpressionSequenceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#TemplateStringExpression.
    def visitTemplateStringExpression(self, ctx: JavaScriptParser.TemplateStringExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#TernaryExpression.
    def visitTernaryExpression(self, ctx: JavaScriptParser.TernaryExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#LogicalAndExpression.
    def visitLogicalAndExpression(self, ctx: JavaScriptParser.LogicalAndExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PowerExpression.
    def visitPowerExpression(self, ctx: JavaScriptParser.PowerExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PreIncrementExpression.
    def visitPreIncrementExpression(self, ctx: JavaScriptParser.PreIncrementExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ObjectLiteralExpression.
    def visitObjectLiteralExpression(self, ctx: JavaScriptParser.ObjectLiteralExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#MetaExpression.
    def visitMetaExpression(self, ctx: JavaScriptParser.MetaExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#InExpression.
    def visitInExpression(self, ctx: JavaScriptParser.InExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#LogicalOrExpression.
    def visitLogicalOrExpression(self, ctx: JavaScriptParser.LogicalOrExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#NotExpression.
    def visitNotExpression(self, ctx: JavaScriptParser.NotExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PreDecreaseExpression.
    def visitPreDecreaseExpression(self, ctx: JavaScriptParser.PreDecreaseExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ArgumentsExpression.
    def visitArgumentsExpression(self, ctx: JavaScriptParser.ArgumentsExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#AwaitExpression.
    def visitAwaitExpression(self, ctx: JavaScriptParser.AwaitExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ThisExpression.
    def visitThisExpression(self, ctx: JavaScriptParser.ThisExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#FunctionExpression.
    def visitFunctionExpression(self, ctx: JavaScriptParser.FunctionExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#UnaryMinusExpression.
    def visitUnaryMinusExpression(self, ctx: JavaScriptParser.UnaryMinusExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#AssignmentExpression.
    def visitAssignmentExpression(self, ctx: JavaScriptParser.AssignmentExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PostDecreaseExpression.
    def visitPostDecreaseExpression(self, ctx: JavaScriptParser.PostDecreaseExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#TypeofExpression.
    def visitTypeofExpression(self, ctx: JavaScriptParser.TypeofExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#InstanceofExpression.
    def visitInstanceofExpression(self, ctx: JavaScriptParser.InstanceofExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#UnaryPlusExpression.
    def visitUnaryPlusExpression(self, ctx: JavaScriptParser.UnaryPlusExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#DeleteExpression.
    def visitDeleteExpression(self, ctx: JavaScriptParser.DeleteExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ImportExpression.
    def visitImportExpression(self, ctx: JavaScriptParser.ImportExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#EqualityExpression.
    def visitEqualityExpression(self, ctx: JavaScriptParser.EqualityExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#BitXOrExpression.
    def visitBitXOrExpression(self, ctx: JavaScriptParser.BitXOrExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#SuperExpression.
    def visitSuperExpression(self, ctx: JavaScriptParser.SuperExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#MultiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx: JavaScriptParser.MultiplicativeExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#BitShiftExpression.
    def visitBitShiftExpression(self, ctx: JavaScriptParser.BitShiftExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ParenthesizedExpression.
    def visitParenthesizedExpression(self, ctx: JavaScriptParser.ParenthesizedExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#AdditiveExpression.
    def visitAdditiveExpression(self, ctx: JavaScriptParser.AdditiveExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#RelationalExpression.
    def visitRelationalExpression(self, ctx: JavaScriptParser.RelationalExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#PostIncrementExpression.
    def visitPostIncrementExpression(self, ctx: JavaScriptParser.PostIncrementExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#YieldExpression.
    def visitYieldExpression(self, ctx: JavaScriptParser.YieldExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#BitNotExpression.
    def visitBitNotExpression(self, ctx: JavaScriptParser.BitNotExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#NewExpression.
    def visitNewExpression(self, ctx: JavaScriptParser.NewExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#LiteralExpression.
    def visitLiteralExpression(self, ctx: JavaScriptParser.LiteralExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ArrayLiteralExpression.
    def visitArrayLiteralExpression(self, ctx: JavaScriptParser.ArrayLiteralExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#MemberDotExpression.
    def visitMemberDotExpression(self, ctx: JavaScriptParser.MemberDotExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ClassExpression.
    def visitClassExpression(self, ctx: JavaScriptParser.ClassExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#MemberIndexExpression.
    def visitMemberIndexExpression(self, ctx: JavaScriptParser.MemberIndexExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#IdentifierExpression.
    def visitIdentifierExpression(self, ctx: JavaScriptParser.IdentifierExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#BitAndExpression.
    def visitBitAndExpression(self, ctx: JavaScriptParser.BitAndExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#BitOrExpression.
    def visitBitOrExpression(self, ctx: JavaScriptParser.BitOrExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#AssignmentOperatorExpression.
    def visitAssignmentOperatorExpression(self, ctx: JavaScriptParser.AssignmentOperatorExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#VoidExpression.
    def visitVoidExpression(self, ctx: JavaScriptParser.VoidExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#CoalesceExpression.
    def visitCoalesceExpression(self, ctx: JavaScriptParser.CoalesceExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#assignable.
    def visitAssignable(self, ctx: JavaScriptParser.AssignableContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#objectLiteral.
    def visitObjectLiteral(self, ctx: JavaScriptParser.ObjectLiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#FunctionDecl.
    def visitFunctionDecl(self, ctx: JavaScriptParser.FunctionDeclContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#AnoymousFunctionDecl.
    def visitAnoymousFunctionDecl(self, ctx: JavaScriptParser.AnoymousFunctionDeclContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#ArrowFunction.
    def visitArrowFunction(self, ctx: JavaScriptParser.ArrowFunctionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#arrowFunctionParameters.
    def visitArrowFunctionParameters(self, ctx: JavaScriptParser.ArrowFunctionParametersContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#arrowFunctionBody.
    def visitArrowFunctionBody(self, ctx: JavaScriptParser.ArrowFunctionBodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#assignmentOperator.
    def visitAssignmentOperator(self, ctx: JavaScriptParser.AssignmentOperatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#literal.
    def visitLiteral(self, ctx: JavaScriptParser.LiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#numericLiteral.
    def visitNumericLiteral(self, ctx: JavaScriptParser.NumericLiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#bigintLiteral.
    def visitBigintLiteral(self, ctx: JavaScriptParser.BigintLiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#getter.
    def visitGetter(self, ctx: JavaScriptParser.GetterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#setter.
    def visitSetter(self, ctx: JavaScriptParser.SetterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#identifierName.
    def visitIdentifierName(self, ctx: JavaScriptParser.IdentifierNameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#identifier.
    def visitIdentifier(self, ctx: JavaScriptParser.IdentifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#reservedWord.
    def visitReservedWord(self, ctx: JavaScriptParser.ReservedWordContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#keyword.
    def visitKeyword(self, ctx: JavaScriptParser.KeywordContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#let.
    def visitLet(self, ctx: JavaScriptParser.LetContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by JavaScriptParser#eos.
    def visitEos(self, ctx: JavaScriptParser.EosContext):
        return self.visitChildren(ctx)


del JavaScriptParser
