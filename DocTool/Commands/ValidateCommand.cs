using System;
using System.CommandLine;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.Extensions.Logging;

namespace DocTool.Commands;

public static class ValidateCommand
{
    public static Command Create(ILogger logger)
    {
        var fileOption = new Option<FileInfo>(
            name: "--file",
            description: "Path to C# file to validate"
        ) { IsRequired = true };
        
        var command = new Command("validate", "Validate C# syntax without full analysis")
        {
            fileOption
        };
        
        command.SetHandler(async (file) =>
        {
            try
            {
                await ExecuteAsync(file, logger);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Validation failed");
                Environment.Exit(1);
            }
        }, fileOption);
        
        return command;
    }
    
    private static async Task ExecuteAsync(FileInfo file, ILogger logger)
    {
        logger.LogInformation("Validating file: {FilePath}", file.FullName);
        
        if (!file.Exists)
        {
            logger.LogError("File not found: {FilePath}", file.FullName);
            Environment.Exit(2);
        }
        
        var sourceCode = await File.ReadAllTextAsync(file.FullName);
        var syntaxTree = CSharpSyntaxTree.ParseText(sourceCode);
        var diagnostics = syntaxTree.GetDiagnostics();
        
        var errors = diagnostics.Where(d => d.Severity == Microsoft.CodeAnalysis.DiagnosticSeverity.Error).ToList();
        
        if (errors.Any())
        {
            logger.LogError("Found {ErrorCount} syntax errors", errors.Count);
            foreach (var error in errors)
            {
                logger.LogError("  Line {Line}: {Message}", error.Location.GetLineSpan().StartLinePosition.Line + 1, error.GetMessage());
            }
            Environment.Exit(3);
        }
        
        logger.LogInformation("Validation passed: No syntax errors found");
        Console.WriteLine("{\"status\":\"valid\",\"errors\":0}");
        Environment.Exit(0);
    }
}
