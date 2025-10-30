using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.Extensions.Logging;
using DocTool.Models;

namespace DocTool.Analysis;

public class AstInspector
{
    private readonly ILogger _logger;
    
    public AstInspector(ILogger logger)
    {
        _logger = logger;
    }
    
    public List<ClassInfo> ExtractClasses(SyntaxNode root)
    {
        var classes = new List<ClassInfo>();
        
        var classDeclarations = root.DescendantNodes()
            .OfType<ClassDeclarationSyntax>();
        
        foreach (var classDecl in classDeclarations)
        {
            _logger.LogDebug("Processing class: {ClassName}", classDecl.Identifier.Text);
            
            var classInfo = new ClassInfo
            {
                Name = classDecl.Identifier.Text,
                Modifiers = classDecl.Modifiers.ToString(),
                BaseTypes = ExtractBaseTypes(classDecl),
                Methods = ExtractMethods(classDecl),
                Properties = ExtractProperties(classDecl),
                Fields = ExtractFields(classDecl),
                Summary = ExtractXmlDocSummary(classDecl),
                IsAbstract = classDecl.Modifiers.Any(m => m.Text == "abstract"),
                IsStatic = classDecl.Modifiers.Any(m => m.Text == "static"),
                IsSealed = classDecl.Modifiers.Any(m => m.Text == "sealed")
            };
            
            classes.Add(classInfo);
        }
        
        return classes;
    }
    
    private List<string> ExtractBaseTypes(ClassDeclarationSyntax classDecl)
    {
        if (classDecl.BaseList == null)
            return new List<string>();
        
        return classDecl.BaseList.Types
            .Select(t => t.Type.ToString())
            .ToList();
    }
    
    private List<MethodInfo> ExtractMethods(ClassDeclarationSyntax classDecl)
    {
        var methods = new List<MethodInfo>();
        
        var methodDeclarations = classDecl.Members
            .OfType<MethodDeclarationSyntax>();
        
        foreach (var methodDecl in methodDeclarations)
        {
            var methodInfo = new MethodInfo
            {
                Name = methodDecl.Identifier.Text,
                ReturnType = methodDecl.ReturnType.ToString(),
                Parameters = ExtractParameters(methodDecl.ParameterList),
                Modifiers = methodDecl.Modifiers.ToString(),
                Summary = ExtractXmlDocSummary(methodDecl),
                IsAsync = methodDecl.Modifiers.Any(m => m.Text == "async"),
                IsStatic = methodDecl.Modifiers.Any(m => m.Text == "static"),
                IsVirtual = methodDecl.Modifiers.Any(m => m.Text == "virtual"),
                IsOverride = methodDecl.Modifiers.Any(m => m.Text == "override"),
                CyclomaticComplexity = CalculateCyclomaticComplexity(methodDecl)
            };
            
            methods.Add(methodInfo);
        }
        
        return methods;
    }
    
    private List<ParameterInfo> ExtractParameters(ParameterListSyntax parameterList)
    {
        return parameterList.Parameters.Select(p => new ParameterInfo
        {
            Name = p.Identifier.Text,
            Type = p.Type?.ToString() ?? "var",
            HasDefaultValue = p.Default != null,
            DefaultValue = p.Default?.Value.ToString()
        }).ToList();
    }
    
    private List<PropertyInfo> ExtractProperties(ClassDeclarationSyntax classDecl)
    {
        var properties = new List<PropertyInfo>();
        
        var propertyDeclarations = classDecl.Members
            .OfType<PropertyDeclarationSyntax>();
        
        foreach (var propDecl in propertyDeclarations)
        {
            var propertyInfo = new PropertyInfo
            {
                Name = propDecl.Identifier.Text,
                Type = propDecl.Type.ToString(),
                Modifiers = propDecl.Modifiers.ToString(),
                HasGetter = propDecl.AccessorList?.Accessors.Any(a => a.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.GetAccessorDeclaration)) ?? false,
                HasSetter = propDecl.AccessorList?.Accessors.Any(a => a.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.SetAccessorDeclaration)) ?? false,
                Summary = ExtractXmlDocSummary(propDecl)
            };
            
            properties.Add(propertyInfo);
        }
        
        return properties;
    }
    
    private List<FieldInfo> ExtractFields(ClassDeclarationSyntax classDecl)
    {
        var fields = new List<FieldInfo>();
        
        var fieldDeclarations = classDecl.Members
            .OfType<FieldDeclarationSyntax>();
        
        foreach (var fieldDecl in fieldDeclarations)
        {
            foreach (var variable in fieldDecl.Declaration.Variables)
            {
                var fieldInfo = new FieldInfo
                {
                    Name = variable.Identifier.Text,
                    Type = fieldDecl.Declaration.Type.ToString(),
                    Modifiers = fieldDecl.Modifiers.ToString(),
                    IsReadOnly = fieldDecl.Modifiers.Any(m => m.Text == "readonly"),
                    IsConst = fieldDecl.Modifiers.Any(m => m.Text == "const")
                };
                
                fields.Add(fieldInfo);
            }
        }
        
        return fields;
    }
    
    private string ExtractXmlDocSummary(SyntaxNode node)
    {
        var trivia = node.GetLeadingTrivia()
            .Where(t => t.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.SingleLineDocumentationCommentTrivia) ||
                       t.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.MultiLineDocumentationCommentTrivia))
            .FirstOrDefault();
        
        if (trivia == default)
            return string.Empty;
        
        var xml = trivia.GetStructure();
        var summaryElement = xml?.DescendantNodes()
            .OfType<Microsoft.CodeAnalysis.CSharp.Syntax.XmlElementSyntax>()
            .FirstOrDefault(e => e.StartTag.Name.ToString() == "summary");
        
        if (summaryElement == null)
            return string.Empty;
        
        var content = string.Join(" ", summaryElement.Content
            .OfType<Microsoft.CodeAnalysis.CSharp.Syntax.XmlTextSyntax>()
            .SelectMany(t => t.TextTokens)
            .Select(t => t.Text.Trim()))
            .Trim();
        
        return content;
    }
    
    private int CalculateCyclomaticComplexity(MethodDeclarationSyntax methodDecl)
    {
        int complexity = 1;
        
        if (methodDecl.Body == null)
            return complexity;
        
        var decisionNodes = methodDecl.Body.DescendantNodes()
            .Where(n => 
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.IfStatement) ||
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.WhileStatement) ||
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.ForStatement) ||
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.ForEachStatement) ||
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.CaseSwitchLabel) ||
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.CatchClause) ||
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.ConditionalExpression) ||
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.LogicalAndExpression) ||
                n.IsKind(Microsoft.CodeAnalysis.CSharp.SyntaxKind.LogicalOrExpression)
            );
        
        complexity += decisionNodes.Count();
        
        return complexity;
    }
}
