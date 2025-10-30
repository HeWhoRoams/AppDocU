using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.Extensions.Logging;
using DocTool.Models;

namespace DocTool.Analysis;

public class RoslynAnalyzer
{
    private readonly ILogger _logger;
    private readonly AstInspector _astInspector;
    private readonly DependencyResolver _dependencyResolver;
    
    public RoslynAnalyzer(ILogger logger)
    {
        _logger = logger;
        _astInspector = new AstInspector(logger);
        _dependencyResolver = new DependencyResolver(logger);
    }
    
    public async Task<CodeArtifact> AnalyzeFileAsync(string filePath)
    {
        _logger.LogDebug("Reading file: {FilePath}", filePath);
        
        var sourceCode = await File.ReadAllTextAsync(filePath);
        
        // Parse syntax tree
        var syntaxTree = CSharpSyntaxTree.ParseText(sourceCode, path: filePath);
        
        // Check for parse errors
        var diagnostics = syntaxTree.GetDiagnostics();
        var errors = diagnostics.Where(d => d.Severity == DiagnosticSeverity.Error).ToList();
        
        if (errors.Any())
        {
            _logger.LogError("File contains {ErrorCount} compilation errors", errors.Count);
            foreach (var error in errors)
            {
                _logger.LogError("  {Error}", error.GetMessage());
            }
            throw new InvalidOperationException($"File contains {errors.Count} compilation errors");
        }
        
        // Get root node
        var root = await syntaxTree.GetRootAsync();
        
        // Extract namespace
        var namespaceDecl = root.DescendantNodes()
            .OfType<BaseNamespaceDeclarationSyntax>()
            .FirstOrDefault();
        
        var namespaceName = namespaceDecl?.Name.ToString() ?? string.Empty;
        
        // Extract classes
        var classes = _astInspector.ExtractClasses(root);
        
        // Extract using directives
        var dependencies = _dependencyResolver.ExtractDependencies(root);
        
        // Build artifact
        var artifact = new CodeArtifact
        {
            FilePath = Path.GetRelativePath(Directory.GetCurrentDirectory(), filePath),
            Namespace = namespaceName,
            Classes = classes,
            Dependencies = dependencies,
            LinesOfCode = sourceCode.Split('\n').Length
        };
        
        _logger.LogInformation("Extracted {ClassCount} classes from {FilePath}", 
            classes.Count, artifact.FilePath);
        
        return artifact;
    }
}
