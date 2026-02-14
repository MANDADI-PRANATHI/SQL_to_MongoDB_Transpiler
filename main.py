import sys
import os
from sql_to_mongo_transpiler.lexer.sql_lexer import get_lexer, LexerError
from sql_to_mongo_transpiler.parser.sql_parser import get_parser
from sql_to_mongo_transpiler.semantic.semantic_analyzer import SemanticAnalyzer, SemanticError
from sql_to_mongo_transpiler.schema_loader import load_schema, SchemaError

DEFAULT_SCHEMA_PATH = "schema.json"

def run_lexer(sql):
    print(f"\n[Lexer Output] Processing: {sql}")
    lexer = get_lexer()
    try:
        tokens = lexer.tokenize(sql)
        for token in tokens:
            print(f"Token(type='{token.type}', value='{token.value}')")
    except LexerError as e:
        print(f"Lexical Error: {e.message} at line {e.line}, column {e.column}")
    except Exception as e:
        print(f"Error: {e}")

def run_parser(sql):
    print(f"\n[Parser Output] Processing: {sql}")
    parser = get_parser()
    try:
        ast = parser.parse(sql)
        print(ast)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def get_user_schema():
    print("\nSchema Options:")
    print("1. Use default schema (schema.json)")
    print("2. Load custom schema file")
    
    choice = input("Enter choice: ").strip()

    if choice == '1':
        schema_path = DEFAULT_SCHEMA_PATH
        # Check if default schema exists
        if not os.path.exists(schema_path):
             print(f"Schema Error: Default schema file '{schema_path}' not found.")
             return None
    elif choice == '2':
        schema_path = input("Enter path to schema JSON file: ").strip()
    else:
        print("Invalid choice. Returning to main menu.")
        return None

    try:
        schema = load_schema(schema_path)
        print("Schema loaded successfully.")
        return schema
    except SchemaError as e:
        print(f"Schema Error: {e}")
        return None
    except Exception as e:
        print(f"Schema Error: {e}")
        return None

from sql_to_mongo_transpiler.codegen.mongodb_generator import MongoDBGenerator

def run_full_pipeline(sql, schema):
    print(f"\n[Full Pipeline] Processing: {sql}")
    parser = get_parser()
    analyzer = SemanticAnalyzer(schema)
    generator = MongoDBGenerator()
    
    try:
        # 1. Parse
        ast = parser.parse(sql)
        
        # 2. Semantic Analysis
        analyzer.validate_query(ast)
        
        print("Query is semantically valid.")
        
        # 3. Code Generation
        mongo_query = generator.generate(ast)
        print("MongoDB Query:")
        print(mongo_query)
        
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except SemanticError as e:
        print(f"Semantic Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def print_menu():
    print("\n" + "="*40)
    print(" SQL to MongoDB Transpiler - Phase Tester")
    print("="*40)
    print("1. Lexical Analysis (Tokens)")
    print("2. Syntax Analysis (AST)")
    print("3. Full Pipeline (Lexer + Parser + Semantic)")
    print("4. Exit")
    print("="*40)

def main():
    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        if choice == '1':
            sql = input("\nEnter SQL Query: ").strip()
            if sql:
                run_lexer(sql)
            else:
                print("Error: Empty input")
        elif choice == '2':
            sql = input("\nEnter SQL Query: ").strip()
            if sql:
                run_parser(sql)
            else:
                print("Error: Empty input")
        elif choice == '3':
            # Ask for schema first
            schema = get_user_schema()
            if schema:
                sql = input("\nEnter SQL Query: ").strip()
                if sql:
                    run_full_pipeline(sql, schema)
                else:
                    print("Error: Empty input")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
