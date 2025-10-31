using System;
using System.CommandLine;
using System.Threading.Tasks;
using DocTool.Commands;
using DocTool.Logging;
using Microsoft.Extensions.Logging;

namespace DocTool;

public class Program
{
    public static async Task<int> Main(string[] args)
    {
        var logger = StructuredLogger.Create();
        
        var rootCommand = new RootCommand("DocTool - C# Code Analysis Utility");
        
        // Add commands
        rootCommand.AddCommand(AnalyzeFileCommand.Create(logger));
        rootCommand.AddCommand(AnalyzeProjectCommand.Create(logger));
        rootCommand.AddCommand(ValidateCommand.Create(logger));
        
        try
        {
            return await rootCommand.InvokeAsync(args);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Unhandled exception");
            return 1;
        }
    }
}
