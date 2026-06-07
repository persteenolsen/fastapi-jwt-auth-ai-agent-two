# tools/calculator.py
import ast
import operator
from typing import Any, Dict


class SafeEval(ast.NodeVisitor):
    """
    Safely evaluate arithmetic expressions only.
    No variables, no function calls.
    """

    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }

    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numbers allowed")

        if isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            op = type(node.op)

            if op not in self.allowed_operators:
                raise ValueError("Operator not allowed")

            return self.allowed_operators[op](left, right)

        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -self.visit(node.operand)
            return self.visit(node.operand)

        raise ValueError("Invalid expression")


def calculator_tool(query: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(query, mode="eval")
        result = SafeEval().visit(tree)

        return {
            "success": True,
            "source": "calculator",
            "expression": query,
            "result": result,
        }

    except Exception as e:
        return {
            "success": False,
            "source": "calculator",
            "content": str(e),
        }