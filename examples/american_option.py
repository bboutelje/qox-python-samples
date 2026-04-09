import time
from datetime import datetime
from zoneinfo import ZoneInfo

import qox

fdm_config = qox.FdmConfig(nodes=500, time_steps=5)
config = qox.Config().add_policy(
    qox.InstrumentPolicy().american().put().fdm(fdm_config)
)  # .fdm(fdm_config))

ny_tz = ZoneInfo("America/New_York")
valuation_time = datetime(2025, 9, 25, 17, 0, tzinfo=ny_tz)
expiry = datetime(2026, 9, 25, 17, 0, tzinfo=ny_tz)
stock_option = qox.VanillaOption(
    100.0, expiry, qox.OptionType.Call, qox.ExerciseStyle.American
)

market_frame = qox.OptionMarketFrame(
    spot=105.0,
    rate_curve=qox.RateCurve.continuous(0.05, qox.DayCountConvention.Act365Fixed),
    vol_surface=qox.VolSurface.flat(0.2, qox.DayCountConvention.Act365Fixed),
)
result = stock_option.valuation().market(market_frame).compute()

start_time = time.perf_counter()
result = stock_option.valuation().market(market_frame).compute()
end_time = time.perf_counter()

duration = end_time - start_time

if duration >= 0.001:
    formatted_latency = f"{duration * 1000:.2f} ms"
else:
    formatted_latency = f"{duration * 1000000:.1f} \u03bcs"

print(f"Price: {result.price:.4f}")
print(f"Latency: {formatted_latency}")
print("-" * 20)
print("Greeks:")
print(f"  Delta: {result.greeks.delta:.5f}")
print(f"  Gamma: {result.greeks.gamma:.5f}")
print(f"  Theta: {result.greeks.theta:.5f}")
if result.greeks.vega is not None:
    print(f"  Vega:  {result.greeks.vega:.5f}")
if result.greeks.rho is not None:
    print(f"  Rho:   {result.greeks.rho:.5f}")


import time
from datetime import datetime
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import qox

# 1. LOAD QUANTLIB DATA
try:
    ql_data = np.load("ql_data.npz")
    ql_times = ql_data["times"]
    ql_errors = ql_data["errors"]
except FileNotFoundError:
    print("Error: ql_data.npz not found. Run the QuantLib script first!")
    exit()

# 2. QOX BENCHMARK SETUP
ny_tz = ZoneInfo("America/New_York")
valuation_time = datetime(2025, 9, 25, 17, 0, tzinfo=ny_tz)
expiry = datetime(2026, 9, 25, 17, 0, tzinfo=ny_tz)

# Market Data (Matching the QL setup: Spot 100, Strike 100)
market_frame = qox.OptionMarketFrame(
    spot=100.0,
    rate_curve=qox.RateCurve.continuous(0.05, qox.DayCountConvention.Act365Fixed),
    vol_surface=qox.VolSurface.flat(0.2, qox.DayCountConvention.Act365Fixed),
)

# Reference Price for Error (using the same 'true' value from QL for parity)
# If you don't have the QL ref_price handy, we'll use a high-res QOX run
true_price = 6.0904  # Standard American Put (100/100/20%/5%/1y)

qox_times = []
qox_errors = []
time_steps_range = [2, 5, 10, 25, 50, 100, 250, 500]

print(f"{'Steps':>6} | {'Latency':>12} | {'Error':>10}")
print("-" * 35)

for ts in time_steps_range:
    # Configure FDM for this step count
    fdm_config = qox.FdmConfig(nodes=1000, time_steps=ts)
    config = qox.Config().add_policy(
        qox.InstrumentPolicy().american().put().fdm(fdm_config)
    )

    stock_option = qox.VanillaOption(
        100.0, expiry, qox.OptionType.Put, qox.ExerciseStyle.American
    )

    # Warm-up run
    _ = stock_option.valuation(config).market(market_frame).compute()

    # Timing Loop (10,000 iterations for microsecond precision)
    iters = 10000
    start = time.perf_counter()
    for _ in range(iters):
        res = stock_option.valuation(config).market(market_frame).compute()
    end = time.perf_counter()

    avg_duration = (end - start) / iters
    error = abs(res.price - true_price)

    qox_times.append(avg_duration)
    qox_errors.append(error)

    label = (
        f"{avg_duration * 1000000:.1f} \u03bcs"
        if avg_duration < 0.001
        else f"{avg_duration * 1000:.2f} ms"
    )
    print(f"{ts:6d} | {label:>12} | {error:10.2e}")

# 3. THE SUPERIMPOSED PLOT
plt.figure(figsize=(12, 7))
ax = plt.gca()

# Plot QuantLib
ax.loglog(
    ql_times, ql_errors, "o-", label="QuantLib (C++ / SWIG)", color="#1f77b4", alpha=0.6
)

# Plot QOX
ax.loglog(
    qox_times, qox_errors, "s-", label="QOX (Optimized)", color="#ff7f0e", linewidth=2
)

# --- AXIS SCALING ---
# Widen to see the 100x gap clearly
ax.set_xlim(1e-5, 1e-2)

# Format Time Axis
ax.xaxis.set_major_locator(ticker.LogLocator(base=10.0, numticks=10))
ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
ax.xaxis.get_major_formatter().set_scientific(False)

# Formatting
ax.grid(True, which="major", ls="-", alpha=0.5)
ax.grid(True, which="minor", ls=":", alpha=0.2)
plt.xlabel("Execution Time (seconds)")
plt.ylabel("Absolute Error")
plt.title("Performance Comparison: QOX vs. QuantLib")
plt.legend()

plt.tight_layout()
plt.show()
