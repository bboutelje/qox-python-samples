import sys

if "google.colab" in sys.modules:
    # This runs only in Colab
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "qox", "-q"])

import time
from datetime import datetime, timedelta, timezone

import qox

# 1. Setup
fdm_config = qox.FdmConfig(nodes=50000, time_steps=500, grid_std_devs=6.0)
config = qox.Config().add_policy(qox.InstrumentPolicy().european().fdm(fdm_config))

expiry = datetime.now(timezone.utc) + timedelta(days=1)
stock_option = qox.StockOption(
    100.0, expiry, qox.OptionType.Call, qox.ExerciseStyle.European
)

market_frame = qox.OptionMarketFrame(
    spot=100.0,
    rate_curve=qox.RateCurve.continuous(0.05, qox.DayCountConvention.Act365Fixed),
    vol_surface=qox.VolSurface.flat(0.2, qox.DayCountConvention.Act365Fixed),
)

# 2. Compute FDM
start_time = time.perf_counter()
fdm_result = stock_option.valuation().market(market_frame).config(config).compute()
duration = time.perf_counter() - start_time

# 3. Compute Analytic
analytic_result = stock_option.valuation().market(market_frame).compute()

# 4. Print results
print(f"Time taken: {duration * 1000:.4f} ms")
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
