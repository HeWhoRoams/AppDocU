using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using DocTool.Models;

namespace DocTool.Output;

public class ArtifactGenerator
{
    private readonly ILogger _logger;
    private readonly JsonSerializerOptions _jsonOptions;
    
    public ArtifactGenerator(ILogger logger)
    {
        _logger = logger;
        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }
    
    public async Task WriteArtifactAsync(CodeArtifact artifact, string outputPath)
    {
        _logger.LogDebug("Writing artifact to: {OutputPath}", outputPath);
        
        var directory = Path.GetDirectoryName(outputPath);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }
        
        var json = JsonSerializer.Serialize(artifact, _jsonOptions);
        await File.WriteAllTextAsync(outputPath, json);
        
        _logger.LogInformation("Artifact written successfully: {Size} bytes", json.Length);
    }
}
