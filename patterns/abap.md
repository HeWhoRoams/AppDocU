# ABAP Pattern Definitions

## Entrypoints Detection
- **Report programs**: `REPORT` statements, executable programs with `START-OF-SELECTION`
- **Function modules**: `FUNCTION-POOL`, `FUNCTION` definitions, remote-enabled modules
- **BAPIs**: Business Application Programming Interfaces, `CALL FUNCTION` usage
- **Dialog modules**: `SCREEN` definitions, `PROCESS BEFORE OUTPUT`, `PROCESS AFTER INPUT`
- **Web services**: `SOAP` definitions, `IDoc` processing functions, `RFC` calls
- **Background jobs**: `JOB` scheduling, `SUBMIT` statements for batch processing

## IO Operations Detection
- **Database reads**: `SELECT` statements, `OPEN SQL` operations, `SELECT-OPTIONS`
- **Database writes**: `INSERT`, `UPDATE`, `MODIFY`, `DELETE` statements, `EXEC SQL` calls
- **File operations**: `OPEN DATASET`, `READ DATASET`, `WRITE DATASET` operations
- **API calls**: `CALL FUNCTION`, `CALL METHOD`, `SUBMIT` to external programs
- **IDoc processing**: `IDOC` creation, processing, and status updates
- **RFC calls**: Remote Function Calls, `CALL FUNCTION ... DESTINATION` statements

## Error Detection
- **Exception handling**: `TRY/CATCH` blocks, `CATCH SYSTEM-EXCEPTIONS`, `ON ERROR` statements
- **Message handling**: `MESSAGE` statements, `SY-MSGNO` error checking, `IF SY-SUBRC <> 0`
- **Exception classes**: Custom exception class definitions and usage

## Tests Detection
- **ABAP Unit**: `CLASS ... DEFINITION FOR TESTING`, `METHOD ... FOR TESTING` patterns
- **Test methods**: `SET UP`, `TEAR DOWN`, `CLASS SET UP`, `CLASS TEAR DOWN` methods
- **Assertions**: `cl_aunit_assert=>*` method calls, `ASSERT` statements

## Confidence Defaults
- **High confidence**: Explicit SQL statements, function module calls, RFC destinations
- **Medium confidence**: Method calls, class usage, inferred operations
- **Low confidence**: Comments, documentation, example code

## ABAP Pattern Cues
- **Report structure**: `REPORT`, `DATA` declarations, `START-OF-SELECTION` events
- **Function modules**: `FUNCTION`, `IMPORTING`, `EXPORTING`, `CHANGING`, `TABLES` parameters
- **Class definitions**: `CLASS ... DEFINITION`, `PUBLIC SECTION`, method definitions
- **Event handling**: `AT SELECTION-SCREEN`, `END-OF-SELECTION`, `TOP-OF-PAGE` events
- **Internal tables**: `TYPES`, `DATA` with `OCCURS`, table operations with `APPEND`, `READ TABLE`
- **CDS views**: `DEFINE VIEW`, `ASSOCIATION`, advanced data modeling
- **Annotations**: `@`-prefixed metadata for CDS, OData, and UI definitions
- **Interface/implementation patterns**: `INTERFACE ...`, `CLASS ... IMPLEMENTATION`, inheritance, composition
- **Authorization checks**: `AUTHORITY-CHECK`, `SY-SUBRC` validation
- **Modern logging**: `cl_badi_log`, `LOG-POINT` usage for structured logging
