"""A small arithmetic calculator."""

from __future__ import annotations

import operator

_OPERATIONS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "%": operator.mod,
}


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
