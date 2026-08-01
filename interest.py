"""Interest and growth calculations."""

from __future__ import annotations


def compound(
    principal: float,
    rate: float,
    years: float,
    *,
    compounds_per_year: float = 1,
) -> float:
    """
    Grows a principal at a fixed interest rate and returns the final amount.

    Interest is compounded ``compounds_per_year`` times per year, so the
    result is ``principal * (1 + rate / n) ** (n * years)``.

    Args:
        principal:
            The starting amount. May be negative to model a debt.

        rate:
            The nominal annual interest rate as a fraction, not a percentage:
            5% is 0.05. A negative rate models depreciation.

        years:
            The number of years to compound over. Need not be a whole number.
            Zero returns the principal unchanged.

        compounds_per_year:
            How many times per year interest is applied. Any positive number
            is accepted, and it need not divide evenly into ``years``. Common
            values:

            1
                annually (the default)
            4
                quarterly
            12
                monthly
            365
                daily

    Returns:
        The final amount, including the principal. Subtract ``principal`` to
        get the interest earned. This is an exact float, not rounded to cents;
        rounding for display is left to the caller.

    Raises:
        ValueError:
            If ``years`` is negative, if ``compounds_per_year`` is not
            positive, or if a single period would lose more than the entire
            balance. The last case means a periodic rate below -100%, which
            would flip the sign of the principal on every period.

    Examples:
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
