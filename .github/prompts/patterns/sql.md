# Pattern Pack — SQL

## Query Types
- DDL: `CREATE TABLE`, `ALTER`, `DROP`.
- DML: `INSERT`, `UPDATE`, `DELETE`.
- DQL: `SELECT`.

## Relationships
- Foreign keys, `JOIN` patterns, normalization levels.

## Stored Procedures / Functions
- `CREATE PROCEDURE`, `CREATE FUNCTION`, `DECLARE`.

## Security / Performance
- `SELECT *` → anti-pattern.
- Missing `WHERE` clauses on destructive ops.
- Use of dynamic SQL / concatenation.
- Lack of indexes on frequently joined columns.

## Integration Signals
- Referenced by ORMs (migrations, models).
- External connections: DSNs, JDBC, SQLAlchemy URIs.
