using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.Extensions.Logging;
using DocTool.Models;

namespace DocTool.Analysis;

public class DependencyResolver
{
    private readonly ILogger _logger;
    
    public DependencyResolver(ILogger logger)
    {
        _logger = logger;
    }
    
    public List<DependencyInfo> ExtractDependencies(SyntaxNode root)
    {
        var dependencies = new List<DependencyInfo>();
        
        var usingDirectives = root.DescendantNodes()
            .OfType<UsingDirectiveSyntax>();
        
        foreach (var usingDir in usingDirectives)
        {
            var namespaceName = usingDir.Name?.ToString() ?? string.Empty;
            
            if (string.IsNullOrEmpty(namespaceName))
                continue;
            
            var dependencyInfo = new DependencyInfo
            {
                Namespace = namespaceName,
                Type = ClassifyDependency(namespaceName),
                IsAlias = usingDir.Alias != null,
                AliasName = usingDir.Alias?.Name.ToString()
            };
            
            dependencies.Add(dependencyInfo);
        }
        
        _logger.LogDebug("Extracted {DependencyCount} dependencies", dependencies.Count);
        
        return dependencies;
    }
    
    private string ClassifyDependency(string namespaceName)
    {
        if (namespaceName.StartsWith("System"))
            return "Framework";
        
        if (namespaceName.StartsWith("Microsoft"))
            return "Microsoft";
        
        if (namespaceName.Contains("."))
        {
            var root = namespaceName.Split('.')[0];
            return IsKnownThirdParty(root) ? "ThirdParty" : "Internal";
        }
        
        return "Unknown";
    }
    
    private bool IsKnownThirdParty(string root)
    {
        var knownPackages = new HashSet<string>
        {
            "Newtonsoft", "Dapper", "AutoMapper", "Serilog", 
            "NLog", "FluentValidation", "MediatR", "Polly"
        };
        
        return knownPackages.Contains(root);
    }
}
