import time
from datetime import datetime
from zoneinfo import ZoneInfo

import qox

fdm_config = qox.FdmConfig(grid_nodes=100, time_steps=5)
config = qox.Config().add_policy(qox.InstrumentPolicy().american().fdm(fdm_config))

ny_tz = ZoneInfo("America/New_York")
valuation_time = datetime(2025, 9, 15, 17, 0, tzinfo=ny_tz)
expiry = datetime(2026, 9, 15, 17, 0, tzinfo=ny_tz)
vanilla_option = qox.VanillaOption(
    100.0, expiry, qox.OptionType.Put, qox.ExerciseStyle.American
)
option_price = 11.0

div_schedule = qox.DividendSchedule(
    [
        (datetime(2025, 12, 15, 0, 0, tzinfo=ny_tz), 1.25),
        (datetime(2026, 3, 15, 0, 0, tzinfo=ny_tz), 1.25),
        (datetime(2026, 6, 15, 0, 0, tzinfo=ny_tz), 1.25),
        (datetime(2026, 9, 15, 0, 0, tzinfo=ny_tz), 1.25),
    ]
)
div_schedule = None

market_frame = qox.OptionMarketFrame(
    spot=95.0,
    rate_curve=qox.RateCurve.continuous(0.05, qox.DayCountConvention.ACT_365_FIXED),
    vol_surface=qox.VolSurface.flat(0.2, qox.DayCountConvention.ACT_365_FIXED),
    dividends=div_schedule,
    # borrow_curve=qox.RateCurve.continuous(0.00, qox.DayCountConvention.ACT_365_FIXED),
)

implied_vol = (
    vanilla_option.implied_vol()
    .at(valuation_time)
    .market(market_frame)
    .price(option_price)
    .config(config)
    .calculate()
)

start_time = time.perf_counter()
implied_vol = (
    vanilla_option.implied_vol()
    .at(valuation_time)
    .market(market_frame)
    .price(option_price)
    .config(config)
    .calculate()
)

end_time = time.perf_counter()

duration = end_time - start_time

if duration >= 0.001:
    formatted_latency = f"{duration * 1000:.2f} ms"
else:
    formatted_latency = f"{duration * 1000000:.1f} \u03bcs"

print(f"Implied vol: {implied_vol * 100.0:.4f}")
print(f"Latency: {formatted_latency}")
print("-" * 20)

market_frame.vol_surface = qox.VolSurface.flat(
    implied_vol, qox.DayCountConvention.ACT_365_FIXED
)

result = vanilla_option.valuation().at(valuation_time).market(market_frame).compute()

print(f"Price: {result.price:.4f}")

print("-" * 20)
print("Greeks:")
print(f"  Delta: {result.greeks.delta:.5f}")
print(f"  Gamma: {result.greeks.gamma:.5f}")
print(f"  Theta: {result.greeks.theta:.5f}")
if result.greeks.vega is not None:
    print(f"  Vega:  {result.greeks.vega:.5f}")
if result.greeks.rho is not None:
    print(f"  Rho:   {result.greeks.rho:.5f}")
