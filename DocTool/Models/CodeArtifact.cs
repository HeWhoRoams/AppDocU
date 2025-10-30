using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace DocTool.Models;

public class CodeArtifact
{
    [JsonPropertyName("file_path")]
    public string FilePath { get; set; } = string.Empty;
    
    [JsonPropertyName("namespace")]
    public string Namespace { get; set; } = string.Empty;
    
    [JsonPropertyName("classes")]
    public List<ClassInfo> Classes { get; set; } = new();
    
    [JsonPropertyName("dependencies")]
    public List<DependencyInfo> Dependencies { get; set; } = new();
    
    [JsonPropertyName("lines_of_code")]
    public int LinesOfCode { get; set; }
    
    [JsonPropertyName("analysis_timestamp")]
    public DateTime AnalysisTimestamp { get; set; } = DateTime.UtcNow;
}

public class ClassInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("modifiers")]
    public string Modifiers { get; set; } = string.Empty;
    
    [JsonPropertyName("base_types")]
    public List<string> BaseTypes { get; set; } = new();
    
    [JsonPropertyName("methods")]
    public List<MethodInfo> Methods { get; set; } = new();
    
    [JsonPropertyName("properties")]
    public List<PropertyInfo> Properties { get; set; } = new();
    
    [JsonPropertyName("fields")]
    public List<FieldInfo> Fields { get; set; } = new();
    
    [JsonPropertyName("summary")]
    public string Summary { get; set; } = string.Empty;
    
    [JsonPropertyName("is_abstract")]
    public bool IsAbstract { get; set; }
    
    [JsonPropertyName("is_static")]
    public bool IsStatic { get; set; }
    
    [JsonPropertyName("is_sealed")]
    public bool IsSealed { get; set; }
}

public class MethodInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("return_type")]
    public string ReturnType { get; set; } = string.Empty;
    
    [JsonPropertyName("parameters")]
    public List<ParameterInfo> Parameters { get; set; } = new();
    
    [JsonPropertyName("modifiers")]
    public string Modifiers { get; set; } = string.Empty;
    
    [JsonPropertyName("summary")]
    public string Summary { get; set; } = string.Empty;
    
    [JsonPropertyName("is_async")]
    public bool IsAsync { get; set; }
    
    [JsonPropertyName("is_static")]
    public bool IsStatic { get; set; }
    
    [JsonPropertyName("is_virtual")]
    public bool IsVirtual { get; set; }
    
    [JsonPropertyName("is_override")]
    public bool IsOverride { get; set; }
    
    [JsonPropertyName("cyclomatic_complexity")]
    public int CyclomaticComplexity { get; set; }
}

public class ParameterInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;
    
    [JsonPropertyName("has_default_value")]
    public bool HasDefaultValue { get; set; }
    
    [JsonPropertyName("default_value")]
    public string? DefaultValue { get; set; }
}

public class PropertyInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;
    
    [JsonPropertyName("modifiers")]
    public string Modifiers { get; set; } = string.Empty;
    
    [JsonPropertyName("has_getter")]
    public bool HasGetter { get; set; }
    
    [JsonPropertyName("has_setter")]
    public bool HasSetter { get; set; }
    
    [JsonPropertyName("summary")]
    public string Summary { get; set; } = string.Empty;
}

public class FieldInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;
    
    [JsonPropertyName("modifiers")]
    public string Modifiers { get; set; } = string.Empty;
    
    [JsonPropertyName("is_readonly")]
    public bool IsReadOnly { get; set; }
    
    [JsonPropertyName("is_const")]
    public bool IsConst { get; set; }
}

public class DependencyInfo
{
    [JsonPropertyName("namespace")]
    public string Namespace { get; set; } = string.Empty;
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;
    
    [JsonPropertyName("is_alias")]
    public bool IsAlias { get; set; }
    
    [JsonPropertyName("alias_name")]
    public string? AliasName { get; set; }
}
