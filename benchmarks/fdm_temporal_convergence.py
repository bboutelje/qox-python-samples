import time
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.ticker as ticker
import QuantLib as ql

import qox

# --- ADJUSTABLE INPUTS ---
SPOT = 95.0
STRIKE = 100.0
VOL = 0.20
RATE = 0.05
DIV = 0.0

# Synchronized Timing
VALUATION_TIME = datetime(2025, 9, 25, 17, 0, tzinfo=timezone.utc)
EXPIRY_TIME = datetime(2026, 9, 25, 17, 0, tzinfo=timezone.utc)

QUANTLIB_DAMPING_STEPS = 0


# --- UTILS ---
def dt_to_ql(dt):
    """Converts python datetime to QuantLib Date."""
    return ql.Date(dt.day, dt.month, dt.year)


# --- QUANTLIB SETUP ---
def setup_ql_american_put(time_steps, grid_points=1000):
    ql_val_date = dt_to_ql(VALUATION_TIME)
    ql_exp_date = dt_to_ql(EXPIRY_TIME)

    ql.Settings.instance().evaluationDate = ql_val_date
    calendar = ql.NullCalendar()
    day_count = ql.Actual365Fixed()

    underlying = ql.QuoteHandle(ql.SimpleQuote(SPOT))
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_val_date, RATE, day_count))
    dividend_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(ql_val_date, DIV, day_count)
    )
    vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql_val_date, calendar, VOL, day_count)
    )

    process = ql.BlackScholesMertonProcess(underlying, dividend_ts, yield_ts, vol_ts)
    payoff = ql.PlainVanillaPayoff(ql.Option.Put, STRIKE)
    exercise = ql.AmericanExercise(ql_val_date, ql_exp_date)
    option = ql.VanillaOption(payoff, exercise)

    engine = ql.FdBlackScholesVanillaEngine(
        process,
        time_steps,
        grid_points,
        QUANTLIB_DAMPING_STEPS,
        ql.FdmSchemeDesc.CrankNicolson(),
    )
    option.setPricingEngine(engine)
    return option


# --- REFERENCE CALCULATION (QuantLib) ---
print("Calculating QuantLib Reference...")
ref_ql = setup_ql_american_put(time_steps=20000, grid_points=2000)
TRUE_PRICE = ref_ql.NPV()
print(f"QuantLib Reference Price: {TRUE_PRICE:.6f}")

# --- BENCHMARKING ---
steps_range = [5, 10, 25, 50, 100, 250, 500, 1000, 2000]
ql_times, ql_errors = [], []
qox_times, qox_errors = [], []

# QOX Market Setup
market_frame = qox.OptionMarketFrame(
    spot=SPOT,
    rate_curve=qox.RateCurve.continuous(RATE, qox.DayCountConvention.ACT_365_FIXED),
    vol_surface=qox.VolSurface.flat(VOL, qox.DayCountConvention.ACT_365_FIXED),
)
stock_option = qox.VanillaOption(
    STRIKE, EXPIRY_TIME, qox.OptionType.Put, qox.ExerciseStyle.American
)

print(
    f"\n{'Steps':>6} | {'QL Latency':>12} | {'QL Error':>10} | {'QoX Latency':>12} | {'QoX Error':>10}"
)
print("-" * 66)

for ts in steps_range:
    # 1. QuantLib Run
    opt_ql = setup_ql_american_put(time_steps=ts)
    start_ql = time.perf_counter()
    p_ql = opt_ql.NPV()
    dur_ql = time.perf_counter() - start_ql
    err_ql = abs(p_ql - TRUE_PRICE)

    ql_times.append(dur_ql)
    ql_errors.append(err_ql)

    # 2. QoX Run
    fdm_config = qox.FdmConfig(nodes=1000, time_steps=ts)
    config = qox.Config().add_policy(
        qox.InstrumentPolicy().american().put().fdm(fdm_config)
    )

    start_qox = time.perf_counter()
    res_qox = (
        stock_option.valuation()
        .at(VALUATION_TIME)
        .config(config)
        .market(market_frame)
        .compute()
    )
    dur_qox = time.perf_counter() - start_qox
    err_qox = abs(res_qox.price - TRUE_PRICE)

    qox_times.append(dur_qox)
    qox_errors.append(err_qox)

    # --- LATENCY FORMATTING ---
    def format_latency(seconds):
        if seconds < 0.001:
            return f"{seconds * 1000000:7.1f} \u03bcs"
        return f"{seconds * 1000:7.2f} ms"

    print(
        f"{ts:6d} | {format_latency(dur_ql):>12} | {err_ql:10.2e} | "
        f"{format_latency(dur_qox):>12} | {err_qox:10.2e}"
    )

# --- PLOTTING ---
plt.figure(figsize=(10, 6))
ax = plt.gca()

ax.loglog(ql_times, ql_errors, "o-", label="QuantLib (FDM)", color="#1f77b4", alpha=0.7)
ax.loglog(qox_times, qox_errors, "s-", label="QoX (FDM)", color="#ff7f0e", linewidth=2)

# Axis Formatting
ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
formatter = ax.xaxis.get_major_formatter()
if isinstance(formatter, mticker.ScalarFormatter):
    formatter.set_scientific(False)
ax.grid(True, which="both", ls="-", alpha=0.3)

plt.xlabel("Execution Time (seconds)")
plt.ylabel("Absolute Error (vs QuantLib reference price)")
plt.title("Performance Comparison: QoX vs. QuantLib")
plt.legend()
plt.tight_layout()

plt.savefig("fdm_convergence.png", dpi=300)
print("\nGraph saved as 'fdm_convergence.png'")

plt.show()
