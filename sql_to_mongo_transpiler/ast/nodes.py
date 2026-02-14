from typing import List, Union, Optional

class ASTNode:
    """Base class for all AST nodes."""
    def __repr__(self):
        return self.__class__.__name__

class Comparison(ASTNode):
    """Represents a comparison: identifier operator literal"""
    def __init__(self, identifier: str, operator: str, value: Union[int, str]):
        self.identifier = identifier
        self.operator = operator
        self.value = value

    def __repr__(self):
        return (f"Comparison(\n"
                f"    identifier='{self.identifier}',\n"
                f"    operator='{self.operator}',\n"
                f"    value={repr(self.value)}\n"
                f")")

class LogicalCondition(ASTNode):
    """Represents a logical condition: condition AND/OR condition"""
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        left_repr = repr(self.left).replace('\n', '\n    ')
        right_repr = repr(self.right).replace('\n', '\n    ')
        return (f"LogicalCondition(\n"
                f"    left={left_repr},\n"
                f"    operator='{self.operator}',\n"
                f"    right={right_repr}\n"
                f")")

class SelectQuery(ASTNode):
    """Represents a SELECT query"""
    def __init__(self, columns: List[str], table: str, where: Optional[ASTNode] = None):
        self.columns = columns
        self.table = table
        self.where = where

    def __repr__(self):
        if self.where:
            where_repr = repr(self.where).replace('\n', '\n    ')
        else:
            where_repr = 'None'
            
        return (f"SelectQuery(\n"
                f"    columns={self.columns},\n"
                f"    table='{self.table}',\n"
                f"    where={where_repr}\n"
                f")")
