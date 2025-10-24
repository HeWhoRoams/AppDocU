
# SQL Pattern Definitions

_Dialect scope: Patterns below cover T-SQL, PL/SQL, PostgreSQL, MySQL/MariaDB, and SQLite. Other dialects may require additional cues._

## Entrypoints Detection
- **Stored procedures**: `CREATE PROCEDURE`, `CREATE FUNCTION`, `CREATE TRIGGER` statements
- **Views**: `CREATE VIEW` statements that may be called by applications
- **Database functions**: User-defined functions, scalar functions, table-valued functions
- **Batch scripts**: `BEGIN/END` blocks, transaction blocks that contain business logic

## IO Operations Detection
- **Database reads**: `SELECT` statements, `WITH` clauses, `JOIN` operations, subqueries
- **Database writes**: `INSERT`, `UPDATE`, `DELETE` statements, `MERGE` operations
- **Schema operations**: `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE` statements
- **Transaction operations**: `BEGIN TRANSACTION`, `COMMIT`, `ROLLBACK` statements
- **Cursor operations**: `DECLARE CURSOR`, `OPEN CURSOR`, `FETCH` operations

## Error Detection
- **Exception handling**: `TRY/CATCH` blocks in T-SQL, `EXCEPTION` blocks in PL/SQL, `EXCEPTION` blocks and `RAISE` in PostgreSQL, `SIGNAL`/`RESIGNAL` in MySQL/MariaDB, `RAISE` in SQLite triggers
- **Error conditions**: `RAISERROR` statements, `THROW` in T-SQL, `RAISE` in PostgreSQL and SQLite, `SIGNAL`/`RESIGNAL` in MySQL/MariaDB
- **Constraint violations**: Foreign key, check constraint, unique constraint patterns

## Tests Detection
- **Test data**: `INSERT` statements in test schemas, test data setup scripts
- **Validation queries**: `SELECT` statements with assertions, count validations
- **Mock data**: Test-specific table names, temporary tables for testing

## Confidence Defaults
- **High confidence**: Explicit DML statements (`SELECT`, `INSERT`, `UPDATE`, `DELETE`), DDL operations
- **Medium confidence**: Complex queries, stored procedure calls, function invocations
- **Low confidence**: Comments, documentation queries, example code

## SQL Pattern Cues
- **Statement types**: DML, DDL, DCL statement identification
- **Table references**: `FROM` clauses, table names, schema qualifications
- **Parameter usage**: `@parameter` patterns, `?` placeholders, bound variables
- **Function calls**: Built-in functions, user-defined functions, aggregate functions
- **Join patterns**: Inner, outer, cross join identification and relationships
