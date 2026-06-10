import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import QuantLib as ql

import qox

ny_tz = ZoneInfo("America/New_York")
valuation_time = datetime(2025, 9, 15, 0, 0, tzinfo=ny_tz)
expiry_dt = datetime(2026, 9, 15, 0, 0, tzinfo=ny_tz)
spot = 100.0
strike = 100.0
vol = 0.2
rate = 0.05
nodes = 100
time_steps = 10
QOX_OPTION_TYPE = qox.OptionType.Put
QL_OPTION_TYPE = ql.Option.Put

# Dividend Data
div_data = [
    (datetime(2025, 12, 15, 0, 0, tzinfo=ny_tz), 1.25),
    (datetime(2026, 3, 15, 0, 0, tzinfo=ny_tz), 1.25),
    (datetime(2026, 6, 15, 0, 0, tzinfo=ny_tz), 1.25),
]

# --- 1. QOX EXECUTION ---
fdm_config = qox.FdmConfig(grid_nodes=nodes, time_steps=time_steps)
config = qox.Config().add_policy(qox.InstrumentPolicy().american().fdm(fdm_config))
vanilla_option = qox.VanillaOption(
    strike, expiry_dt, QOX_OPTION_TYPE, qox.ExerciseStyle.American
)
div_schedule = qox.DividendSchedule(div_data)
# div_schedule = None

market_frame = qox.OptionMarketFrame(
    spot=spot,
    rate_curve=qox.RateCurve.continuous(rate, qox.DayCountConvention.ACT_365_FIXED),
    vol_surface=qox.VolSurface.flat(vol, qox.DayCountConvention.ACT_365_FIXED),
    dividends=div_schedule,
)

# Warm up
vanilla_option.valuation().at(valuation_time).market(market_frame).config(
    config
).compute()

start_qox = time.perf_counter()
res_qox = (
    vanilla_option.valuation()
    .at(valuation_time)
    .market(market_frame)
    .config(config)
    .compute()
)
qox_lat = (time.perf_counter() - start_qox) * 1000

# --- 2. QUANTLIB EXECUTION ---
calendar = ql.UnitedStates(ql.UnitedStates.Settlement)
day_count = ql.Actual365Fixed()

ql_val_date = ql.Date(valuation_time.day, valuation_time.month, valuation_time.year)
ql.Settings.instance().evaluationDate = ql_val_date

spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_val_date, rate, day_count))
flat_vol = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(ql_val_date, calendar, vol, day_count)
)

dividends = [
    ql.FixedDividend(d[1], ql.Date(d[0].day, d[0].month, d[0].year)) for d in div_data
]
# dividends = None

payoff = ql.PlainVanillaPayoff(QL_OPTION_TYPE, strike)
exercise = ql.AmericanExercise(
    ql_val_date, ql.Date(expiry_dt.day, expiry_dt.month, expiry_dt.year)
)

# Correct class for discrete dividends in SWIG Python
ql_option = ql.VanillaOption(payoff, exercise)

process = ql.BlackScholesProcess(spot_handle, flat_ts, flat_vol)
tr_bdf2_scheme = ql.FdmSchemeDesc.TrBDF2()

engine = ql.FdBlackScholesVanillaEngine(
    process, dividends, time_steps, nodes, 0, tr_bdf2_scheme
)
ql_option.setPricingEngine(engine)

start_ql = time.perf_counter()
ql_price = ql_option.NPV()
ql_delta = ql_option.delta()
ql_gamma = ql_option.gamma()
ql_theta = ql_option.theta()
ql_lat = (time.perf_counter() - start_ql) * 1000

# --- 3. TABULATION ---
results = {
    "Metric": ["Price", "Delta", "Gamma", "Theta", "Latency (ms)"],
    "Qox": [
        f"{res_qox.price:.5f}",
        f"{res_qox.greeks.delta:.5f}",
        f"{res_qox.greeks.gamma:.5f}",
        f"{res_qox.greeks.theta:.5f}",
        f"{qox_lat:.3f}",
    ],
    "QuantLib": [
        f"{ql_price:.5f}",
        f"{ql_delta:.5f}",
        f"{ql_gamma:.5f}",
        f"{ql_theta:.5f}",
        f"{ql_lat:.3f}",
    ],
}

df = pd.DataFrame(results)
print("\nFDM COMPARISON: AMERICAN PUT")
print("=" * 50)
print(df.to_string(index=False))
print("=" * 50)
