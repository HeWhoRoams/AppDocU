# Generic Pattern Definitions

## Entrypoints Detection
- **Main functions**: `main()` functions, entry point methods, initialization code
- **Configuration loading**: Configuration file reading, environment variable usage
- **Service startup**: Application initialization, server startup patterns
- **Command line args**: `argv` processing, argument parsing, option handling

## IO Operations Detection
- **File operations**: File read/write patterns, stream operations, file system calls
- **Network calls**: HTTP requests, socket operations, network communication
- **Database operations**: Generic database connection patterns, query execution
- **External API calls**: Third-party service integration patterns, web service calls
- **Message queues**: Publish/subscribe patterns, queue operations, event systems

## Error Detection
- **Exception handling**: Try/catch patterns, error handling blocks, exception classes
- **Error logging**: Logging calls, error message generation, error tracking
- **Validation**: Input validation, error checking, defensive programming patterns

## Tests Detection
- **Test functions**: Test method naming patterns, test class structures
- **Assertions**: Assertion statements, validation calls, test verification
- **Mocking**: Mock object creation, stub patterns, test double usage
- **Test setup**: Test initialization, fixture setup, test environment preparation

## Confidence Defaults
- **High confidence**: Explicit IO operations, clear API calls, obvious entry points
- **Medium confidence**: Function calls with context, inferred operations, pattern matching
- **Low confidence**: Comments, variable assignments, ambiguous method calls

## General Pattern Cues
- **Function/method calls**: Call expressions, method invocations, function usage
- **Variable assignments**: Variable declarations, assignments, value tracking
- **Control flow**: Conditional statements, loops, branching logic
- **Import/include statements**: Dependency declarations, module imports, includes
- **Comments and documentation**: Comment patterns, documentation strings, code notes
