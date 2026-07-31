"""A small arithmetic calculator."""

from __future__ import annotations

import math
import operator

_OPERATIONS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "%": operator.mod,
}

_TRIG_OPERATIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
}

# Functions that return an angle rather than consuming one; the ``degrees``
# flag converts their result instead of their argument.
_INVERSE_TRIG = frozenset({"asin", "acos", "atan"})


def calculate(left: float, op: str, right: float) -> float:
    """Apply a binary arithmetic operation to two numbers.

    Args:
        left: The left-hand operand.
        op: One of ``+``, ``-``, ``*``, ``/``, ``%``.
        right: The right-hand operand.

    Returns:
        The result of ``left op right``.

    Raises:
        ValueError: If ``op`` is not a supported operator.
        ZeroDivisionError: If ``right`` is zero and ``op`` is ``/`` or ``%``.

    >>> calculate(2, "+", 3)
    5
    >>> calculate(7, "/", 2)
    3.5
    >>> calculate(7, "%", 3)
    1
    >>> calculate(-7, "%", 3)
    2
    """
    try:
        func = _OPERATIONS[op]
    except KeyError:
        supported = ", ".join(sorted(_OPERATIONS))
        raise ValueError(f"unsupported operator {op!r}; expected one of: {supported}") from None
    return func(left, right)


def calculate_trig(op: str, value: float, *, degrees: bool = False) -> float:
    """Apply a trigonometric function to a number.

    Args:
        op: One of ``sin``, ``cos``, ``tan``, ``asin``, ``acos``, ``atan``.
        value: The operand. For ``sin``/``cos``/``tan`` this is an angle;
            for the inverse functions it is a ratio.
        degrees: If true, angles are measured in degrees instead of radians.
            This applies to the argument of ``sin``/``cos``/``tan`` and to the
            return value of ``asin``/``acos``/``atan``.

    Returns:
        The result of ``op(value)``.

    Raises:
        ValueError: If ``op`` is not a supported function, or if ``value`` is
            outside the domain of ``asin``/``acos`` (that is, not in [-1, 1]).

    >>> calculate_trig("sin", 0)
    0.0
    >>> calculate_trig("cos", 0)
    1.0
    >>> calculate_trig("sin", 90, degrees=True)
    1.0
    >>> calculate_trig("atan", 1, degrees=True)
    45.0
    """
    try:
        func = _TRIG_OPERATIONS[op]
    except KeyError:
        supported = ", ".join(sorted(_TRIG_OPERATIONS))
        raise ValueError(f"unsupported function {op!r}; expected one of: {supported}") from None

    inverse = op in _INVERSE_TRIG
    if degrees and not inverse:
        value = math.radians(value)
    result = func(value)
    if degrees and inverse:
        result = math.degrees(result)
    return result
