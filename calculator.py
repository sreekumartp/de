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

# Trig functions are unary, so they cannot live in _OPERATIONS (which is
# dispatched as ``func(left, right)``). They get their own table and their own
# entry point, ``calculate_trig``.
_TRIG_OPERATIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
}

# Functions that return an angle rather than consuming one; the ``degrees``
# flag converts their result instead of their argument. Kept as an explicit set
# rather than an ``op.startswith("a")`` test, which would wrongly classify
# future entries such as ``atan2`` (consumes no angle, returns one but takes two
# arguments) or ``abs``.
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
        # ``from None`` hides the internal KeyError, so a caller who passed a
        # bad name sees only the ValueError naming the valid options. Mirrors
        # the lookup in ``calculate``.
        supported = ", ".join(sorted(_TRIG_OPERATIONS))
        raise ValueError(f"unsupported function {op!r}; expected one of: {supported}") from None

    # The ``degrees`` flag applies to whichever side of the call is an angle,
    # and that differs by direction: sin/cos/tan take an angle and return a
    # ratio, while asin/acos/atan take a ratio and return an angle. So convert
    # the input for the forward functions and the output for the inverse ones —
    # never both, or the conversion would cancel itself out.
    inverse = op in _INVERSE_TRIG
    if degrees and not inverse:
        value = math.radians(value)

    # A domain error here (asin/acos outside [-1, 1]) is deliberately left to
    # propagate as math's own ValueError, matching how ``calculate`` lets
    # ZeroDivisionError through rather than repackaging it.
    result = func(value)

    if degrees and inverse:
        result = math.degrees(result)
    return result
