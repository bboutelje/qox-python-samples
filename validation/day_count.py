from datetime import date, datetime, timezone

import pytest
import QuantLib as ql

import qox


def to_ql_date(d: date):
    # QuantLib ql.Date handles both date and datetime objects
    return ql.Date(d.day, d.month, d.year)


def get_ql_convention(convention: qox.DayCountConvention):
    """Maps qox conventions to QuantLib objects."""
    if convention == qox.DayCountConvention.Thirty360.ISDA:
        # ql.Thirty360.BondBasis matches the '183' reference values
        # for February end-of-month logic in your Rust tests.
        return ql.Thirty360(ql.Thirty360.BondBasis)
    elif convention == qox.DayCountConvention.ActActISDA:
        return ql.ActualActual(ql.ActualActual.ISDA)
    elif convention == qox.DayCountConvention.Act360:
        return ql.Actual360()
    elif convention == qox.DayCountConvention.Act365Fixed:
        return ql.Actual365Fixed()
    raise ValueError("Unsupported convention")


## --- Tests ---


@pytest.mark.parametrize(
    "start_dt, end_dt",
    [
        (date(2024, 1, 31), date(2024, 2, 28)),  # thirty360_us_start_is_31
        (date(2024, 1, 31), date(2024, 3, 31)),  # thirty360_us_end_is_31
        (date(2006, 8, 31), date(2007, 2, 28)),  # Reference Case 1
        (date(2006, 8, 31), date(2007, 2, 27)),  # Reference Case 2
        (date(2007, 2, 28), date(2007, 8, 31)),  # Reference Case 3
        (date(2006, 2, 28), date(2006, 8, 31)),  # Reference Case 4
    ],
)
def test_thirty360_us_parity(start_dt, end_dt):
    """Validates Thirty/360 US day counts against QuantLib."""
    convention = qox.DayCountConvention.Thirty360.ISDA

    # Qox calculation
    qox_days = qox.PeriodCalculator.days_between(start_dt, end_dt, convention)

    # QuantLib calculation
    ql_convention = get_ql_convention(convention)
    ql_days = ql_convention.dayCount(to_ql_date(start_dt), to_ql_date(end_dt))

    assert qox_days == ql_days, (
        f"Failed at {start_dt} to {end_dt}. Qox: {qox_days}, QL: {ql_days}"
    )


def test_act_act_isda_parity():
    """Validates Act/Act ISDA year fraction against QuantLib."""
    # Attach timezone.utc to satisfy the PyO3 conversion to DateTime<Utc>
    start_dt = datetime(1999, 7, 1, tzinfo=timezone.utc)
    end_dt = datetime(2000, 7, 1, tzinfo=timezone.utc)

    # Qox calculation
    qox_yf = qox.PeriodCalculator.year_fraction(
        start_dt, end_dt, qox.DayCountConvention.ActActISDA
    )

    # QuantLib calculation
    ql_convention = get_ql_convention(qox.DayCountConvention.ActActISDA)
    ql_yf = ql_convention.yearFraction(to_ql_date(start_dt), to_ql_date(end_dt))

    # Using 1e-12 tolerance as per your Rust test
    assert abs(qox_yf - ql_yf) < 1e-12, (
        f"Year fraction mismatch. Qox: {qox_yf}, QL: {ql_yf}"
    )
