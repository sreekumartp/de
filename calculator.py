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


def compound(
    principal: float,
    rate: float,
    years: float,
    *,
    compounds_per_year: float = 1,
) -> float:
    """Grow a principal at a fixed interest rate and return the final amount.

    Interest is compounded ``compounds_per_year`` times per year, so the result
    is ``principal * (1 + rate / n) ** (n * years)``.

    Args:
        principal: The starting amount. May be negative to model a debt.
        rate: The nominal annual interest rate as a fraction, not a
            percentage: 5% is ``0.05``. A negative rate models depreciation.
        years: The number of years to compound over. Need not be a whole
            number; ``0`` returns the principal unchanged.
        compounds_per_year: How many times per year interest is applied — 1
            for annual, 12 for monthly, 365 for daily. Need not divide evenly
            into ``years``.

    Returns:
        The final amount, including the principal. Subtract ``principal`` to
        get the interest earned. This is an exact float, not rounded to cents;
        rounding for display is left to the caller.

    Raises:
        ValueError: If ``years`` is negative, if ``compounds_per_year`` is not
            positive, or if ``rate`` is so negative that a period wipes out
            more than the whole balance (``rate / compounds_per_year < -1``),
            which would flip the sign of the principal on every period.

    >>> round(compound(1000, 0.05, 10), 2)
    1628.89
    >>> round(compound(1000, 0.05, 10, compounds_per_year=12), 2)
    1647.01
    >>> compound(1000, 0.05, 0)
    1000.0
    >>> round(compound(1000, -0.10, 3), 2)
    729.0
    """
    if years < 0:
        raise ValueError(f"years must not be negative; got {years!r}")
    if compounds_per_year <= 0:
        raise ValueError(f"compounds_per_year must be positive; got {compounds_per_year!r}")

    periodic_rate = rate / compounds_per_year
    # Below -100% per period the growth factor goes negative, and raising a
    # negative base to a fractional exponent is a complex number (which Python
    # returns silently, rather than raising). Reject it here so the caller gets
    # a clear error instead of a complex result or an oscillating sign.
    if periodic_rate < -1:
        raise ValueError(
            f"rate {rate!r} over {compounds_per_year!r} periods per year loses more than "
            f"the full balance each period"
        )

    return principal * (1 + periodic_rate) ** (compounds_per_year * years)


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
