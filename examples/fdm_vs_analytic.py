import time
from datetime import datetime
from zoneinfo import ZoneInfo

import qox

ny_tz = ZoneInfo("America/New_York")
spot = 95.0
strike = 100.0
valuation_time = datetime(2025, 9, 25, 17, 0, tzinfo=ny_tz)
expiry = datetime(2026, 9, 25, 17, 0, tzinfo=ny_tz)
rate = 0.05
vol = 0.2
option_type = qox.OptionType.Call
exercise_style = qox.ExerciseStyle.European


# 1. Setup
fdm_config = qox.FdmConfig(nodes=500, time_steps=5, grid_std_devs=6.0)
config = qox.Config().add_policy(qox.InstrumentPolicy().european().fdm(fdm_config))

# expiry = datetime.now(timezone.utc) + timedelta(days=1)
stock_option = qox.StockOption(strike, expiry, option_type, exercise_style)

market_frame = qox.OptionMarketFrame(
    spot=spot,
    rate_curve=qox.RateCurve.continuous(rate, qox.DayCountConvention.Act365Fixed),
    vol_surface=qox.VolSurface.flat(vol, qox.DayCountConvention.Act365Fixed),
)

# 2. Compute FDM
start_time = time.perf_counter()
fdm_result = stock_option.valuation().at().market(market_frame).config(config).compute()
duration = time.perf_counter() - start_time

# 3. Compute Analytic
analytic_result = (
    stock_option.valuation().at(valuation_time).market(market_frame).compute()
)

# 4. Print results
print(f"Time taken: {duration * 1000000:.0f} \u03bcs")
print(f"\n{'Metric':<12} | {'FDM':>15} | {'Analytic':>15} | {'% Dev':>15}")
print("-" * 67)

metrics = [
    ("Price", fdm_result.price, analytic_result.price),
    ("Delta", fdm_result.greeks.delta, analytic_result.greeks.delta),
    ("Gamma", fdm_result.greeks.gamma, analytic_result.greeks.gamma),
    ("Theta", fdm_result.greeks.theta, analytic_result.greeks.theta),
]

for label, fdm_val, analytic_val in metrics:
    dev = abs(100.0 * (fdm_val / analytic_val - 1.0))
    print(f"{label:<12} | {fdm_val:>15.8f} | {analytic_val:>15.8f} | {dev:>13.4f} %")
