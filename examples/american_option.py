import time
from datetime import datetime, timedelta, timezone

import qox

fdm_config = qox.FdmConfig(nodes=500, time_steps=5)
config = qox.Config().add_policy(
    qox.InstrumentPolicy().american().put().fdm(fdm_config)
)

expiry = datetime.now(timezone.utc) + timedelta(days=365)
stock_option = qox.StockOption(
    100.0, expiry, qox.OptionType.Put, qox.ExerciseStyle.American
)

market_frame = qox.OptionMarketFrame(
    spot=95.0,
    rate_curve=qox.RateCurve.continuous(0.05, qox.DayCountConvention.Act365Fixed),
    vol_surface=qox.VolSurface.flat(0.2, qox.DayCountConvention.Act365Fixed),
)

start_time = time.perf_counter()
result = stock_option.valuation().market(market_frame).config(config).compute()
end_time = time.perf_counter()

duration = end_time - start_time

if duration >= 0.001:
    formatted_latency = f"{duration * 1000:.2f} ms"
else:
    formatted_latency = f"{duration * 1000000:.0f} \u03bcs"

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
