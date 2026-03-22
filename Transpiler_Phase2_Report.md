# SQL to MongoDB Query Transpiler: Phase 2 Report

## 1. Work Done So Far (New Additions Section)
Building upon the previous components—namely Lexical Analysis, Syntax Analysis, AST generation, Semantic Analysis, and standard MongoDB query generation using `.find()`—the transpiler has been significantly extended. In this stage, the following features have been successfully implemented:
- **Aggregate Functions**: Support for `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX`.
- **GROUP BY Clause**: Grouping records based on one or more columns.
- **HAVING Clause**: Post-aggregation filtering.
- **ORDER BY Clause**: Sorting result sets in ascending (`ASC`) or descending (`DESC`) order.
- **LIMIT Clause**: Restricting the total number of returned documents.
- **Combined Pipeline**: Seamless integration of `GROUP BY`, `HAVING`, `ORDER BY`, and `LIMIT` features to handle complex queries simultaneously.
- **Additional Enhancements**: Support for **multiple `GROUP BY` columns**, allowing results to be aggregated over compound criteria. *(Note: Features such as `OFFSET`, nested aggregations, and column aliasing via `AS` were not implemented in this phase and are logged for future iterations.)*

## 2. Implementation Details
The transpiler's core modules were carefully updated to accommodate the new grammar rules and AST structures. 

### 2.1 AST Changes
To parse and represent the new query components, the parser logic was expanded to encompass the following new AST nodes and attributes:
- **`Aggregate` Node**: Represents aggregate functions within the abstract syntax tree. It stores the `func` (e.g., `COUNT`, `SUM`) and the corresponding `column` argument.
- **`OrderByItem` Node**: Encapsulates an individual column and its sorting `direction` (`ASC` or `DESC`).
- **`SelectQuery` Enhancements**: The base `SelectQuery` node was extended with optional attributes:
    - `group_by`: A list of strings representing the columns to group by.
    - `having`: An `ASTNode` (like `LogicalCondition` or `Comparison`) applied for aggregating filtering.
    - `order_by`: A list of `OrderByItem` instances representing the sorting sequence.
    - `limit`: An integer denoting the cap on the results returned.

### 2.2 Semantic Analysis Updates
The semantic rules for query validation were fortified:
1. **GROUP BY Enforcement**: Any column listed in the `SELECT` clause that is not enclosed within an aggregate function must be explicitly stated in the `GROUP BY` clause.
2. **HAVING Pre-requisite**: A semantic validation explicitly checks that a `HAVING` clause is strictly accompanied by a `GROUP BY` clause. If left missing, the transpiler accurately halts by throwing a `SemanticError`.
3. **Aggregate Scoping**: Function validations confirm that columns wrapped inside aggregate handlers (except `COUNT(*)`) exist within the established sub-schema parameters.

### 2.3 MongoDB Aggregation Pipeline
Due to the constraints of `db.collection.find()`, queries involving aggregates or `GROUP BY` clauses necessitate the usage of MongoDB's Aggregation Framework. The transpiler was modified to intelligently swap out standard `.find()` for `db.collection.aggregate([...])`. The query conditions dynamically sequence into specialized stages such as `$match`, `$group`, `$sort`, and `$limit`.

## 3. Mapping Rules (SQL → MongoDB)
The translation behavior constructs the MongoDB query stage-by-stage based on SQL clauses:

| SQL Construct | MongoDB Equivalent | Notes |
| --- | --- | --- |
| `GROUP BY col` | `$group: { _id: "$col" }` | For multiple columns, maps to `{ _id: { col1: "$col1", col2: "$col2" } }` |
| `COUNT(*)` | `{ "count": { $sum: 1 } }` | Accurately counts matching documents per group. |
| `COUNT(col)` | `{ "count_col": { $sum: { $cond: [...] } } }` | Validates non-null values for numeric aggregation. |
| `SUM(col)` | `{ "sum_col": { $sum: "$col" } }` | Accumulates numeric values identically. |
| `AVG(col)` | `{ "avg_col": { $avg: "$col" } }` | Averages values inside grouped keys. |
| `MIN(col)` | `{ "min_col": { $min: "$col" } }` | Extracts literal minimum per field. |
| `MAX(col)` | `{ "max_col": { $max: "$col" } }` | Extracts literal maximum per field. |
| `HAVING cond` | `$match` (Post-`$group`) | Implemented as a subsequent `$match` stage traversing aggregates. |
| `ORDER BY` | `$sort` | Values set to `1` for `ASC`, `-1` for `DESC`. |
| `LIMIT n` | `$limit` | Simply caps array lengths. |

## 4. Test Cases with Expected Outputs

### 🔹 TC-A: Basic Aggregate
**Listing 1: Input SQL**
```sql
SELECT COUNT(*) FROM users;
```
**MongoDB Output:**
```javascript
db.users.aggregate([
  { '$group': { '_id': null, 'count': { '$sum': 1 } } }
])
```

### 🔹 TC-B: GROUP BY
**Listing 2: Input SQL**
```sql
SELECT city, COUNT(*) FROM users GROUP BY city;
```
**MongoDB Output:**
```javascript
db.users.aggregate([
  { '$group': { '_id': '$city', 'count': { '$sum': 1 } } }
])
```

### 🔹 TC-C: SUM
**Listing 3: Input SQL**
```sql
SELECT city, SUM(age) FROM users GROUP BY city;
```
**MongoDB Output:**
```javascript
db.users.aggregate([
  { '$group': { '_id': '$city', 'sum_age': { '$sum': '$age' } } }
])
```

### 🔹 TC-D: AVG
**Listing 4: Input SQL**
```sql
SELECT city, AVG(age) FROM users GROUP BY city;
```
**MongoDB Output:**
```javascript
db.users.aggregate([
  { '$group': { '_id': '$city', 'avg_age': { '$avg': '$age' } } }
])
```

### 🔹 TC-E: HAVING
**Listing 5: Input SQL**
```sql
SELECT city, COUNT(*) FROM users GROUP BY city HAVING COUNT(*) > 2;
```
**MongoDB Output:**
```javascript
db.users.aggregate([
  { '$group': { '_id': '$city', 'count': { '$sum': 1 } } },
  { '$match': { 'count': { '$gt': 2 } } }
])
```

### 🔹 TC-F: ORDER BY
**Listing 6: Input SQL**
```sql
SELECT name, age FROM users ORDER BY age DESC;
```
**MongoDB Output:**
```javascript
db.users.find({}, { name: 1, age: 1 }).sort({ age: -1 })
```
*(Observation: Query safely uses .find().sort() without entering the heavier .aggregate() pipeline)*

### 🔹 TC-G: LIMIT
**Listing 7: Input SQL**
```sql
SELECT name FROM users LIMIT 5;
```
**MongoDB Output:**
```javascript
db.users.find({}, { name: 1 }).limit(5)
```

### 🔹 TC-H: GROUP BY + ORDER BY + LIMIT
**Listing 8: Input SQL**
```sql
SELECT city, COUNT(*) FROM users GROUP BY city ORDER BY COUNT(*) DESC LIMIT 3;
```
**MongoDB Output:**
```javascript
db.users.aggregate([
  { '$group': { '_id': '$city', 'count': { '$sum': 1 } } },
  { '$sort': { 'count': -1 } },
  { '$limit': 3 }
])
```

### 🔹 TC-I: GROUP BY + HAVING + ORDER BY
**Listing 9: Input SQL**
```sql
SELECT city, SUM(age) FROM users GROUP BY city HAVING SUM(age) > 100 ORDER BY SUM(age) DESC;
```
**MongoDB Output:**
```javascript
db.users.aggregate([
  { '$group': { '_id': '$city', 'sum_age': { '$sum': '$age' } } },
  { '$match': { 'sum_age': { '$gt': 100 } } },
  { '$sort': { 'sum_age': -1 } }
])
```

### 🔹 TC-J: Edge Cases
**Listing 10: Input SQL**
```sql
SELECT name, COUNT(*) FROM users;
```
**Expected Output:** SemanticError (`Column 'name' must appear in GROUP BY or be aggregated`)

**Listing 11: Input SQL**
```sql
SELECT city, COUNT(*) FROM users GROUP BY invalid_col;
```
**Expected Output:** SemanticError (`Column 'invalid_col' does not exist in table 'users'`)

**Listing 12: Input SQL**
```sql
SELECT city FROM users HAVING COUNT(*) > 5;
```
**Expected Output:** SemanticError (`HAVING clause requires GROUP BY`)

**Listing 13: Input SQL (Multiple GROUP BY Addition)**
```sql
SELECT city, role, COUNT(*) FROM users GROUP BY city, role;
```
**Expected Output:** 
```javascript
db.users.aggregate([
  { '$group': { '_id': { 'city': '$city', 'role': '$role' }, 'count': { '$sum': 1 } } }
])
```

## 5. Integration into Pipeline
A definitive decision logic governs the generator's pipeline implementation strategy. Inside the code generation phase (`MongoDBGenerator`), the transpiler evaluates two primary flags via `self._has_aggregate(ast)`:
- Whether the query `SELECT` constraints possess any explicit `Aggregate` components.
- Whether a `GROUP BY` clause is present in the parsed `SelectQuery` AST node.

If either of these criteria equals true, the transpiler intelligently constructs the query utilizing MongoDB’s `.aggregate([...])` framework, subsequently executing procedural stages to sequence `$match` (from WHERE), `$group`, `$match` (from HAVING), `$sort`, and `$limit`. If standard relational columns populate the `SELECT` list, it falls back to parsing a standard `.find(filter, projection)` statement coupled with matching `.sort()` and `.limit()` chain functions.

## 6. Deviations
- **Offset/Skip Constraints**: Although the `offset` parameter is present in `ast/nodes.py`, the SQL `LIMIT ___ OFFSET ___` grammar is not actively parsed by the rules inside `sql_parser.py`.
- **Nested Aggregations**: Recursive aggregate compositions (e.g., `SUM(COUNT(*))`) are not recognized by the `aggregate_expr` syntax rules and thus remain unsupported.
- **Projection Renaming (Aliases)**: The alias binding syntax (`SELECT col AS AliasName`) has not been modeled inside the underlying lexer and YACC AST parser logic yet.

## 7. Planned Work
For future development cycles, priority extensions could include:
1. Extending parser grammar and translation layers for the `OFFSET` instruction to map into `$skip`.
2. Integration resolving variable alias declarations (`AS`) projecting into customized MongoDB response identifiers using `$project`.
3. Extended parsing for relational `JOIN` functions to natively resolve nested MongoDB sub-documents (`$lookup` syntax implementation).
