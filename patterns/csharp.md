# C# Pattern Definitions

## Entrypoints Detection
- **HTTP Controllers**: Classes inheriting `Controller` or `ControllerBase`, methods with `[HttpGet]`, `[HttpPost]`, etc.
- **Web API**: `ApiController`, methods with HTTP verb attributes
- **SignalR**: `Hub` classes, `OnConnectedAsync()`, `OnDisconnectedAsync()`
- **Background services**: `BackgroundService`, `IHostedService` implementations
- **Console apps**: `Main()` method, `ICommand` implementations
- **WCF services**: `[ServiceContract]`, `[OperationContract]` attributes

## IO Operations Detection
- **Database reads**: `SqlCommand.ExecuteReader()`, `DbContext.FindAsync()`, `LINQ` queries, `SqlDataReader.Read()`
- **Database writes**: `SqlCommand.ExecuteNonQuery()`, `DbContext.SaveChanges()`, `INSERT/UPDATE/DELETE` operations
- **API calls**: `HttpClient.GetAsync()`, `HttpClient.PostAsync()`, `WebRequest`, `RestClient` calls
- **File reads**: `File.ReadAllText()`, `StreamReader`, `FileStream` with read mode
- **File writes**: `File.WriteAllText()`, `StreamWriter`, `FileStream` with write mode
- **Event emission**: `EventHubClient`, `ServiceBusSender`, `RabbitMQ` publish calls
- **Message queues**: `SendMessage()`, `Publish()`, `Enqueue()` operations

## Error Detection
- **Exception handling**: `try/catch` blocks, `throw` statements, custom exception classes
- **Error patterns**: `throw new`, error logging with `ILogger.LogError()`, `EventLog.WriteEntry()`

## Tests Detection
- **Test methods**: `[TestMethod]`, `[Fact]`, `[Theory]`, methods with `Test` attribute
- **Test classes**: Classes with `[TestClass]`, `NUnit` test fixtures
- **Assertions**: `Assert.AreEqual()`, `Assert.IsTrue()`, `Xunit` assertions
- **Mocking**: `Mock<T>`, `Moq` usage, `NSubstitute` patterns

## Confidence Defaults
- **High confidence**: Explicit SQL commands, HTTP client calls, file operations with clear mode
- **Medium confidence**: Generic method calls, inferred database operations through ORMs
- **Low confidence**: Comments, variable assignments without clear context

## AST/Reflection Cues
- **Method definitions**: Method signatures with attributes and parameters
- **Class declarations**: Inheritance patterns, interface implementations
- **Attribute usage**: Custom and built-in attributes for behavior detection
- **Using statements**: Namespace imports for dependency mapping
