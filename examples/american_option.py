import time
from datetime import datetime
from zoneinfo import ZoneInfo

import qox

n = 100
fdm_config = qox.FdmConfig(
    grid_nodes=1000,
    time_steps=100,
    grid_std_devs=4.0,
    transform=qox.TransformConfig.sinh(0.3),
)
config = qox.Config().add_policy(qox.InstrumentPolicy().american().fdm(fdm_config))

ny_tz = ZoneInfo("America/New_York")
valuation_time = datetime(2025, 9, 15, 17, 0, tzinfo=ny_tz)
expiry = datetime(2025, 10, 4, 23, 0, tzinfo=ny_tz)
vanilla_option = qox.VanillaOption(
    100.0, expiry, qox.OptionType.Put, qox.ExerciseStyle.American
)

div_schedule = qox.DividendSchedule(
    [
        (datetime(2025, 12, 15, 0, 0, tzinfo=ny_tz), 1.25),
        (datetime(2026, 3, 15, 0, 0, tzinfo=ny_tz), 1.25),
        (datetime(2026, 6, 15, 0, 0, tzinfo=ny_tz), 1.25),
    ]
)
# div_schedule = None

market_frame = qox.OptionMarketFrame(
    spot=92.2,
    rate_curve=qox.RateCurve.continuous(0.05, qox.DayCountConvention.ACT_365_FIXED),
    vol_surface=qox.VolSurface.flat(0.2, qox.DayCountConvention.ACT_365_FIXED),
    # dividends=div_schedule,
    # borrow_curve=qox.RateCurve.continuous(0.00, qox.DayCountConvention.ACT_365_FIXED),
)
result = (
    vanilla_option.valuation()
    .at(valuation_time)
    .market(market_frame)
    .config(config)
    .compute()
)

start_time = time.perf_counter()
for _ in range(n):
    result = (
        vanilla_option.valuation()
        .at(valuation_time)
        .market(market_frame)
        .config(config)
        .compute()
    )
end_time = time.perf_counter()

duration = (end_time - start_time) / n

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
