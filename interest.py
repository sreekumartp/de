"""Interest and growth calculations."""

from __future__ import annotations

import math


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


def emi(
    principal: float,
    rate: float,
    years: float,
    *,
    payments_per_year: float = 12,
) -> float:
    """
    Returns the equated instalment that repays a loan over a fixed term.

    Every instalment is the same size, is paid at the end of its period, and
    covers the interest accrued that period plus enough of the principal that
    the final payment clears the balance exactly.

    Args:
        principal:
            The amount borrowed. Zero returns a zero payment.

        rate:
            The nominal annual interest rate as a fraction, not a percentage:
            8% is 0.08. Zero is allowed and simply splits the principal evenly
            across the payments.

        years:
            The length of the loan. Need not be a whole number, but must be
            positive: a loan with no payments has no instalment.

        payments_per_year:
            How many instalments are paid per year, which is also how often
            interest is compounded. Defaults to 12, the monthly schedule the
            term "EMI" normally implies. Use 4 for quarterly, 1 for annually.

    Returns:
        The amount due each period. This is an exact float, not rounded to
        cents; rounding for display is left to the caller. Multiply by the
        number of payments and subtract ``principal`` to get the total
        interest paid over the life of the loan.

    Raises:
        ValueError:
            If ``years`` or ``payments_per_year`` is not positive, or if a
            single period's interest would exceed the entire balance. The last
            case means a periodic rate at or below -100%, for which no
            repayment schedule exists.

    Examples:
        >>> round(emi(100000, 0.08, 10), 2)
        1213.28
        >>> round(emi(250000, 0.06, 30), 2)
        1498.88
        >>> emi(1200, 0, 1)
        100.0
        >>> round(emi(10000, 0.10, 3, payments_per_year=1), 2)
        4021.15
    """
    if years <= 0:
        raise ValueError(f"years must be positive; got {years!r}")
    if payments_per_year <= 0:
        raise ValueError(f"payments_per_year must be positive; got {payments_per_year!r}")

    periodic_rate = rate / payments_per_year
    # At exactly -100% per period the debt is wiped out by the interest term
    # and the formula below divides by zero; below that it goes complex, the
    # same trap ``compound`` guards against. Neither describes a real loan.
    if periodic_rate <= -1:
        raise ValueError(
            f"rate {rate!r} over {payments_per_year!r} periods per year wipes out the "
            f"full balance each period"
        )

    payments = payments_per_year * years

    # An interest-free loan is just the principal split evenly. It needs its
    # own branch because the general formula below is 0/0 at a zero rate.
    if periodic_rate == 0:
        return principal / payments

    # The textbook form is ``P * r * (1 + r)**n / ((1 + r)**n - 1)``. This is
    # the algebraically identical ``P * r / (1 - (1 + r)**-n)``, computed with
    # log1p/expm1 so that the near-cancellation in the denominator stays
    # accurate at the small periodic rates that real loans actually use —
    # writing ``(1 + r)**n - 1`` directly loses significant digits there.
    discount = -math.expm1(-payments * math.log1p(periodic_rate))
    return principal * periodic_rate / discount
