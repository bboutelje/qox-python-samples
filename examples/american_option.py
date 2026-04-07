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
