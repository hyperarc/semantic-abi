import pytest as pytest

from semanticabi.common.expression.ExpressionEvaluator import ExpressionEvaluator


@pytest.mark.parametrize('expression,expected_value', [
    ("(-1 + 2**2) * 3", 9),
    ("1 + 2 * 3", 7),
    ("1 + 2 - 3", 0),
    (".5", 0.5),
    ("1 + .5 + 0.25", 1.75),
    ("2 * 3 * 4", 24),
    ("1 - -2", 3),
    ("1 - 2 + 3", 2),
    ("2 ** 3 ** 2", 512),
    ("'foo'", 'foo'),
    ("'foo' || 'bar'", 'foobar'),
])
def test_eval_expr(expression: str, expected_value: any):
    evaluator = ExpressionEvaluator(expression)
    assert evaluator.evaluate({}) == expected_value


def test_eval_expr_with_vars():
    evaluator = ExpressionEvaluator("-1 * a")
    variables = {'a': 2}
    assert evaluator.evaluate(variables) == -2


def test_eval_expr_multiple_vars():
    evaluator = ExpressionEvaluator("-1 * a + b")
    variables = {'a': 2, 'b': 3}
    assert evaluator.evaluate(variables) == 1


def test_eval_expr_missing_var():
    evaluator = ExpressionEvaluator("-1 * a + b")
    variables = {'a': 2}
    with pytest.raises(Exception) as e:
        evaluator.evaluate(variables)

    assert str(e.value) == 'Unknown variable: b'
