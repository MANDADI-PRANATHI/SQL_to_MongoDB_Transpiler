import ply.yacc as yacc
from sql_to_mongo_transpiler.lexer.sql_lexer import SqlLexer
from sql_to_mongo_transpiler.ast.nodes import SelectQuery, LogicalCondition, Comparison

class SqlParser:
    def __init__(self):
        self.lexer = SqlLexer()
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)

    # Precedence rules
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
    )

    def p_query(self, p):
        '''query : SELECT select_list FROM IDENTIFIER where_clause_opt SEMICOLON'''
        p[0] = SelectQuery(columns=p[2], table=p[4], where=p[5])

    def p_select_list_star(self, p):
        '''select_list : STAR'''
        p[0] = ['*']

    def p_select_list_columns(self, p):
        '''select_list : column_list'''
        p[0] = p[1]

    def p_column_list_single(self, p):
        '''column_list : IDENTIFIER'''
        p[0] = [p[1]]

    def p_column_list_multi(self, p):
        '''column_list : column_list COMMA IDENTIFIER'''
        p[0] = p[1] + [p[3]]

    def p_where_clause_opt(self, p):
        '''where_clause_opt : WHERE condition
                            | empty'''
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = None

    def p_condition_visual(self, p):
        '''condition : condition AND condition
                     | condition OR condition'''
        p[0] = LogicalCondition(left=p[1], operator=p[2], right=p[3])

    def p_condition_comparison(self, p):
        '''condition : comparison'''
        p[0] = p[1]

    def p_comparison(self, p):
        '''comparison : IDENTIFIER operator literal'''
        p[0] = Comparison(identifier=p[1], operator=p[2], value=p[3])

    def p_operator(self, p):
        '''operator : EQ
                    | NE
                    | GT
                    | LT
                    | GE
                    | LE'''
        p[0] = p[1]

    def p_literal_number(self, p):
        '''literal : NUMBER'''
        p[0] = p[1]

    def p_literal_string(self, p):
        '''literal : STRING'''
        p[0] = p[1]

    def p_empty(self, p):
        '''empty :'''
        pass

    def p_error(self, p):
        if p:
            raise SyntaxError(f"Syntax error at '{p.value}', line {p.lineno}")
        else:
            raise SyntaxError("Syntax error at EOF")

    def parse(self, data):
        return self.parser.parse(data, lexer=self.lexer.lexer)

# Helper function
def get_parser():
    return SqlParser()
