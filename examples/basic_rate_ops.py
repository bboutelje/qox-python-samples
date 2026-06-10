import qox

rate = qox.InterestRate(
    0.05, qox.Compounding.continuous(), qox.DayCountConvention.ACT_365_FIXED
)

flat_rate = qox.RateCurve.flat(rate)
flat_df = rate.discount_factor(1)

cts_rate = qox.RateCurve.continuous(0.05, qox.DayCountConvention.ACT_365_FIXED)
cts_df = cts_rate.discount_factor(1)

assert flat_df == cts_df

# Headers
print(f"{'':<20} | {'Discount factor':<12}")
print("-" * 50)

# Data rows
print(f"{'Flat rate':<20} | {flat_df:<12}")
print(f"{'Continuous rate':<20} | {cts_df:<12}")
