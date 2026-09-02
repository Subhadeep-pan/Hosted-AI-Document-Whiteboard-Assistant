import ast
import operator

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def get_operator(op):
    func = OPERATORS.get(type(op))
    if not func:
        raise ValueError("Invalid operator")
    return func


def evaluate(node):

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

    if isinstance(node, ast.BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        return get_operator(node.op)(left, right)

    if isinstance(node, ast.UnaryOp):
        value = evaluate(node.operand)
        return get_operator(node.op)(value)

    raise ValueError("Invalid expression")


def calculate(expression):
    try:
        tree = ast.parse(expression, mode="eval")
        return str(evaluate(tree.body))
    except Exception:
        return "Invalid calculation"