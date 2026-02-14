# SQL to MongoDB Transpiler

This project is a transpiler that converts SQL queries into MongoDB query language.

## Stage 1: Lexer

In this stage, we implement the Lexer (Tokenizer) using `ply`.

### Supported SQL Subset

- Statements: `SELECT`
- Clauses: `FROM`, `WHERE`
- Operators: `=`, `!=`, `<`, `>`, `<=`, `>=`, `AND`, `OR`
- Literals: Integers, Single-quoted strings

### Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```
