using System;
using System.CommandLine;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using DocTool.Analysis;
using DocTool.Output;
using Microsoft.Extensions.Logging;

namespace DocTool.Commands;

public static class AnalyzeFileCommand
{
    public static Command Create(ILogger logger)
    {
        var fileOption = new Option<FileInfo>(
            name: "--file",
            description: "Path to C# file to analyze"
        ) { IsRequired = true };
        
        var outputOption = new Option<FileInfo>(
            name: "--output",
            description: "Output path for JSON artifact"
        ) { IsRequired = true };
        
        var command = new Command("analyze-file", "Analyze a single C# file")
        {
            fileOption,
            outputOption
        };
        
        command.SetHandler(async (file, output) =>
        {
            try
            {
                await ExecuteAsync(file, output, logger);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Command execution failed");
                Environment.Exit(1);
            }
        }, fileOption, outputOption);
        
        return command;
    }
    
    private static async Task ExecuteAsync(FileInfo file, FileInfo output, ILogger logger)
    {
        logger.LogInformation("Starting analysis of file: {FilePath}", file.FullName);
        
        if (!file.Exists)
        {
            logger.LogError("File not found: {FilePath}", file.FullName);
            Environment.Exit(2);
        }
        
        var analyzer = new RoslynAnalyzer(logger);
        var artifact = await analyzer.AnalyzeFileAsync(file.FullName);
        
        var generator = new ArtifactGenerator(logger);
        await generator.WriteArtifactAsync(artifact, output.FullName);
        
        logger.LogInformation("Analysis complete. Artifact written to: {OutputPath}", output.FullName);
        
        var response = new
        {
            status = "success",
            artifacts = new[] { artifact },
            errors = Array.Empty<string>(),
            warnings = Array.Empty<string>()
        };
        
        Console.WriteLine(JsonSerializer.Serialize(response, new JsonSerializerOptions
        {
            WriteIndented = false
        }));
        
        Environment.Exit(0);
    }
}
