from sql_to_mongo_transpiler.ast.nodes import SelectQuery, LogicalCondition, Comparison

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self, schema):
        self.schema = schema

    def validate_query(self, ast):
        if isinstance(ast, SelectQuery):
            self.validate_select(ast)
        else:
            raise SemanticError(f"Unsupported query type: {type(ast)}")

    def validate_select(self, node: SelectQuery):
        # 1. Validate Table Exists
        table_name = node.table
        if table_name not in self.schema:
            raise SemanticError(f"Table '{table_name}' does not exist")

        # 2. Validate Columns
        self.validate_columns(node.columns, table_name)

        # 3. Validate WHERE Clause
        if node.where:
            self.validate_condition(node.where, table_name)

    def validate_columns(self, columns, table_name):
        table_schema = self.schema[table_name]
        
        # Handle 'SELECT *'
        if columns == ['*']:
            return

        # Check for duplicates
        if len(columns) != len(set(columns)):
            seen = set()
            for col in columns:
                if col in seen:
                    raise SemanticError(f"Duplicate column '{col}' in SELECT list")
                seen.add(col)

        # Check existence
        for col in columns:
            if col not in table_schema:
                raise SemanticError(f"Column '{col}' does not exist in table '{table_name}'")

    def validate_condition(self, node, table_name):
        if isinstance(node, LogicalCondition):
            self.validate_condition(node.left, table_name)
            self.validate_condition(node.right, table_name)
        elif isinstance(node, Comparison):
            self.validate_comparison(node, table_name)

    def validate_comparison(self, node: Comparison, table_name):
        col_name = node.identifier
        table_schema = self.schema[table_name]

        # Check column existence
        if col_name not in table_schema:
            raise SemanticError(f"Column '{col_name}' does not exist in table '{table_name}'")

        # Type checking
        expected_type = table_schema[col_name]
        actual_value = node.value
        
        # Determine actual type
        if isinstance(actual_value, int):
            actual_type = 'int'
        elif isinstance(actual_value, str):
            actual_type = 'string'
        else:
            actual_type = 'unknown'

        if expected_type != actual_type:
            raise SemanticError(
                f"Type mismatch for column '{col_name}'. Expected {expected_type} but got {actual_type}."
            )
