# SQL to MongoDB Transpiler
Convert SQL queries into MongoDB queries automatically.

---
## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [1. Running from Source Code (For Developers)](#1-running-from-source-code-for-developers)
- [2. Using the Transpiler Directly (For End-Users)](#2-using-the-transpiler-directly-for-end-users)
- [Testing](#testing)
- [Example Queries](#example-queries)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)
- [License / Author](#license--author)

---


## Project Overview

The **SQL to MongoDB Transpiler** is a robust tool designed to seamlessly translate SQL queries into MongoDB query language (MQL).

*   **Problem Solved:** Transitioning from relational databases to NoSQL document stores often requires rewriting massive volumes of SQL code. This parser and transpiler automate that process, reducing migration risks and engineering overhead.
*   **Why It's Useful:** Developers familiar with SQL can interact with MongoDB using familiar syntax, bridging the knowledge gap between relational and document-based paradigms.
*   **Architecture:** The project employs a traditional compiler design pattern with Lexical Analysis (using PLY), Semantic Analysis against a provided JSON schema, and Code Generation, complete with Query Optimization.

---

## Features

The transpiler supports a powerful subset of SQL tailored for document querying and aggregation:

*   **Core Queries:** `SELECT` queries with support for specific columns and `*`
*   **Filtering:** `WHERE` conditions supporting logical operators (`AND`, `OR`) and comparisons (`=`, `!=`, `<`, `>`, `<=`, `>=`)
*   **Sorting & Limits:** `ORDER BY` and `LIMIT` implementation
*   **Grouping:** `GROUP BY` and `HAVING` filters
*   **Advanced Aggregations:**
    *   `COUNT`
    *   `SUM`
    *   `AVG`
    *   `MIN`
    *   `MAX`
*   **Joins:** `JOIN` support implicitly converting to MongoDB `$lookup` stages
*   **Multi-Query:** Batch execution and multiple query support via `;` separation
*   **Multi-line SQL:** Native support for multiline raw queries and comments
*   **Error Handling:** Structural and Semantic syntax validation yielding precise error contexts
*   **Query Optimization:**
    *   `OR` → `IN` optimization
    *   Range comparison simplification
    *   `AND` merge optimizations

---

## Tech Stack

*   **Python 3.7+**: Core programming language
*   **PLY (Python Lex-Yacc)**: Lexical scanning and parsing
*   **FastAPI & Uvicorn**: Lightweight backend for the Web UI transpilation API
*   **Flask & Gunicorn**: Backend for the testing and verification correctness tool
*   **HTML / CSS / JS**: Web interfaces using Jinja2 patterns
*   **PostgreSQL**: Benchmark relational database via `psycopg2`
*   **MongoDB**: Benchmark document database via `pymongo`
*   **pytest**: Unit testing and integration suite

---

## Folder Structure

```
sql2mongo/       # Core transpiler package (Lexer, Parser, AST, Generator)
webapp/          # FastAPI-based Web UI for transpiling SQL natively 
tests/           # Pytest suite with ~40 test cases covering parsing/joins/optimizations
db/              # Database initialization and setup scripts
app.py           # Verification and Correctness Tool comparing DB outputs
Features         # Supported SQL mapping documentation
```

---

## 1. Running from Source Code (For Developers)

If you intend to modify the core engine, perform tests, or run the components locally from the codebase, follow these steps.

### Installation

**1. Clone the Repository**
```bash
git clone https://github.com/MANDADI-PRANATHI/SQL_to_MongoDB_Transpiler.git
cd SQL_to_MongoDB_Transpiler
```

**2. Setup Virtual Environment (Optional but Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
pip install -e .
```

### Component Usage

**Core CLI Script:**
Execute the transpiler script acting as a module:
```bash
python -m sql2mongo.cli --schema schema.json --query "SELECT * FROM users;"
```

**Web App Interface:**
Run the FastAPI-based Web UI locally from source:
```bash
python -m uvicorn webapp.main:app --reload
```

**Verification / Correctness Tool:**
Launch the Flask side-by-side test laboratory to verify translations against actual PostgreSQL and MongoDB instances:
```bash
python app.py
```

---

## 2. Using the Transpiler Directly (For End-Users)

If you do not want to interact with the raw source code, you can use our hosted tools directly or install the standalone CLI pip package into any Python environment.

### Pip Package Interface

The Transpiler can be installed securely into any Python ecosystem as a standalone module.

**Installation:**
```bash
pip install sql2mongo
```

**Help Command:**
```bash
sql2mongo --help
```

**Basic Usage Context:**
You can pass a raw SQL string or provide a path to a `.sql` file:
```bash
# Using a raw SQL string
sql2mongo --schema schema.json --query "SELECT name, age FROM users WHERE age > 18;"

# Using a .sql file
sql2mongo --schema schema.json --query path/to/query.sql
```

**Interactive Shell:**
Drop into a REPL environment by passing the `shell` command: 
```bash
sql2mongo shell --schema schema.json
```

Within the interactive shell, you can view or switch your current schema on the fly:
```bash
sql2mongo> :show schema
Current schema: schema.json

sql2mongo> :set schema path/to/new_schema.json
Schema updated to: path/to/new_schema.json
```

### Hosted Web UI

We provide an intuitive hosted front-end to utilize the transpiler directly from your browser.
1. Open the Web App URL.
2. Upload your database `schema.json`.
3. Enter standard SQL syntax in the editor.
4. View the strictly formatted MongoDB Query Language outputs instantly.

**Web App URL:** `https://sql2mongo-webapp.onrender.com` 

### Hosted Verification / Correctness Tool

To guarantee equivalency without running the source, navigate to the Web Verification environment. This interface allows you to parse your SQL query and visually compare standard relational database outputs alongside MongoDB outputs to confirm translation correctness.

**Verification Tool URL:** `https://sql2mongo-v1.onrender.com` 

---

## Testing

The application maintains stability utilizing a `pytest` suite ensuring robust compilation stability. Tests cover node-generation, complex joins, sub-aggregations, pipeline optimizations, and error capturing loops.

To execute the ~40 suite test cases, run:

```bash
pytest tests/test_transpiler_full.py -vv
```

---

## Example Queries

### Simple Selection

**SQL:**
```sql
SELECT name, city FROM users WHERE age >= 21;
```

**MongoDB:**
```json
db.users.find({ age: { $gte: 21 } }, { name: 1, city: 1 })
```

### Aggregation Framework Output

**SQL:**
```sql
SELECT users.name, orders.amount FROM users JOIN orders ON users.id = orders.user_id WHERE orders.amount > 100;
```

**MongoDB:**
```json
db.users.aggregate([{'$match': {'orders.amount': {'$gt': 100}}}, {'$lookup': {'from': 'orders', 'localField': 'id', 'foreignField': 'user_id', 'as': 'orders'}}, {'$unwind': '$orders'}, {'$addFields': {'amount': '$orders.amount'}}, {'$project': {'name': 1, 'amount': 1}}])
```

---

## Deployment

The project supports the following deployment contexts:

1.  **Pip Package**: Core engine module can be built and deployed securely into any Python ecosystem.
2.  **Web UI Deployment**: Native stateless logic via `FastAPI` + `Uvicorn` ready.
3.  **Verification Tool Deployment**: Flask application with `gunicorn.conf.py` and `Procfile.txt` included for PaaS providers (e.g. Heroku, Render).

---


