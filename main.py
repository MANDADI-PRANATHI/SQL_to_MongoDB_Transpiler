import sys
from sql_to_mongo_transpiler.lexer.sql_lexer import get_lexer, LexerError
from sql_to_mongo_transpiler.parser.sql_parser import get_parser

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

def run_full_pipeline(sql):
    print(f"\n[Full Pipeline] Processing: {sql}")
    # Ideally this would pass AST to next phases, but for now it's just parsing
    parser = get_parser()
    try:
        ast = parser.parse(sql)
        print("AST Generated Successfully:")
        print(ast)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def print_menu():
    print("\n" + "="*40)
    print(" SQL to MongoDB Transpiler - Phase Tester")
    print("="*40)
    print("1. Lexical Analysis (Tokens)")
    print("2. Syntax Analysis (AST)")
    print("3. Full Pipeline (Lexer + Parser)")
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
            sql = input("\nEnter SQL Query: ").strip()
            if sql:
                run_full_pipeline(sql)
            else:
                print("Error: Empty input")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
