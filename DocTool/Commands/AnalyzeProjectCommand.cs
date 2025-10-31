using System;
using System.CommandLine;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using DocTool.Analysis;
using DocTool.Output;
using Microsoft.Extensions.Logging;

namespace DocTool.Commands;

public static class AnalyzeProjectCommand
{
    public static Command Create(ILogger logger)
    {
        var projectOption = new Option<DirectoryInfo>(
            name: "--project",
            description: "Path to project directory"
        ) { IsRequired = true };
        
        var outputOption = new Option<FileInfo>(
            name: "--output",
            description: "Output path for JSON artifact"
        ) { IsRequired = true };
        
        var command = new Command("analyze-project", "Analyze all C# files in a project")
        {
            projectOption,
            outputOption
        };
        
        command.SetHandler(async (project, output) =>
        {
            try
            {
                await ExecuteAsync(project, output, logger);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Command execution failed");
                Environment.Exit(1);
            }
        }, projectOption, outputOption);
        
        return command;
    }
    
    private static async Task ExecuteAsync(DirectoryInfo project, FileInfo output, ILogger logger)
    {
        logger.LogInformation("Starting project analysis: {ProjectPath}", project.FullName);
        
        if (!project.Exists)
        {
            logger.LogError("Project directory not found: {ProjectPath}", project.FullName);
            Environment.Exit(2);
        }
        
        var csFiles = project.GetFiles("*.cs", SearchOption.AllDirectories)
            .Where(f => !f.FullName.Contains("\\obj\\") && !f.FullName.Contains("\\bin\\"))
            .ToList();
        
        logger.LogInformation("Found {FileCount} C# files", csFiles.Count);
        
        var analyzer = new RoslynAnalyzer(logger);
        var artifacts = new System.Collections.Generic.List<object>();
        
        foreach (var file in csFiles)
        {
            try
            {
                var artifact = await analyzer.AnalyzeFileAsync(file.FullName);
                artifacts.Add(artifact);
            }
            catch (Exception ex)
            {
                logger.LogWarning(ex, "Failed to analyze file: {FilePath}", file.FullName);
            }
        }
        
        var generator = new ArtifactGenerator(logger);
        var combinedArtifact = new
        {
            project_path = project.FullName,
            file_count = csFiles.Count,
            artifacts = artifacts
        };
        
        var json = JsonSerializer.Serialize(combinedArtifact, new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(output.FullName, json);
        
        logger.LogInformation("Project analysis complete. Artifact written to: {OutputPath}", output.FullName);
        
        Console.WriteLine(JsonSerializer.Serialize(new
        {
            status = "success",
            file_count = csFiles.Count,
            artifacts_count = artifacts.Count
        }));
        
        Environment.Exit(0);
    }
}
