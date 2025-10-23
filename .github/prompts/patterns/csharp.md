# Pattern Pack — C# / ASP.NET Core

Use these heuristics when mapping C# services:

## Entry Points
- `Program.cs` with `CreateHostBuilder` or `WebApplication.CreateBuilder`.
- `Startup.cs` with `Configure`/`ConfigureServices`.

## Web Endpoints
- Controllers: classes ending with `Controller`, decorated with `[ApiController]`, `[Route]`.
- Minimal APIs: `app.MapGet|Post|Put|Delete(...)`.

## Dependency Injection
- Look at `builder.Services.Add*` and `services.Add*` for registrations.
- Map interface → implementation lifetimes (Singleton/Scoped/Transient).

## Data/Storage
- EF Core: `DbContext` subclasses, `OnModelCreating`, connection strings in `appsettings*.json`.
- Dapper: `IDbConnection` usage.

## AuthN/Z
- `AddAuthentication`, `AddAuthorization`, `UseAuthentication`, `UseAuthorization`.
- Look for `[Authorize]` attributes or absence thereof on controllers.

## Config
- `IConfiguration` access, `options pattern` (`services.Configure<TOptions>`).

## Tests
- xUnit/NUnit/MSTest projects (`*.Tests.csproj`).
- Behavior: method names, Arrange/Act/Assert blocks.

## Security Smells (Quick)
- Hardcoded secrets (`new SymmetricSecurityKey("...")`, `RSAParameters` inline).
- Insecure HTTP clients: `HttpClientHandler { ServerCertificateCustomValidationCallback = ... }`
- Missing auth attributes on public endpoints.
