from datetime import datetime, timezone

import QuantLib as ql

import qox

# --- Parameters ---
spot_price = 100.0
strike = 100.0
rate = 0.05
vol = 0.2
ql_option_type = ql.Option.Call
qox_option_type = qox.OptionType.Call

# --- 1. QuantLib Setup (Analytic Benchmark & FDM) ---
ql_eval_date = ql.Date(14, ql.September, 2026)
ql.Settings.instance().evaluationDate = ql_eval_date
ql_expiry_date = ql.Date(15, ql.September, 2026)
day_count = ql.Actual365Fixed()

payoff = ql.PlainVanillaPayoff(ql_option_type, strike)
exercise = ql.EuropeanExercise(ql_expiry_date)
ql_option = ql.VanillaOption(payoff, exercise)

spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_eval_date, rate, day_count))
flat_vol = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(ql_eval_date, ql.NullCalendar(), vol, day_count)
)
flat_div_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_eval_date, 0.0, day_count))
bs_process = ql.BlackScholesMertonProcess(spot_handle, flat_div_ts, flat_ts, flat_vol)

# QL Analytic (The Benchmark)
ql_option.setPricingEngine(ql.AnalyticEuropeanEngine(bs_process))
ql_an = {
    "Price": ql_option.NPV(),
    "Delta": ql_option.delta(),
    "Gamma": ql_option.gamma(),
    "Theta": ql_option.theta(),
}

# QL FDM
fdm_engine = ql.FdBlackScholesVanillaEngine(
    bs_process, None, 100, 1000, 0, ql.FdmSchemeDesc.TrBDF2()
)
ql_option.setPricingEngine(fdm_engine)
ql_fdm = {
    "Price": ql_option.NPV(),
    "Delta": ql_option.delta(),
    "Gamma": ql_option.gamma(),
    "Theta": ql_option.theta(),
}

# --- 2. Qox Setup (FDM) ---
eval_dt = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
exp_dt = datetime(2026, 9, 15, 0, 0, tzinfo=timezone.utc)

market_frame = qox.OptionMarketFrame(
    spot=spot_price,
    rate_curve=qox.RateCurve.continuous(rate, qox.DayCountConvention.ACT_365_FIXED),
    vol_surface=qox.VolSurface.flat(vol, qox.DayCountConvention.ACT_365_FIXED),
)
fdm_config = qox.FdmConfig(grid_nodes=1000, time_steps=100, grid_std_devs=6.0)
config = qox.Config().add_policy(qox.InstrumentPolicy().european().fdm(fdm_config))
qox_opt = qox.VanillaOption(strike, exp_dt, qox_option_type, qox.ExerciseStyle.European)

qox_res = qox_opt.valuation().at(eval_dt).market(market_frame).config(config).compute()
qox_fdm = {
    "Price": qox_res.price,
    "Delta": qox_res.greeks.delta,
    "Gamma": qox_res.greeks.gamma,
    "Theta": qox_res.greeks.theta,
}

# --- 3. Print Comparison Table ---
header = f"{'Metric':<10} | {'QL Analytic':>12} | {'QL FDM':>12} | {'% Dev (QL)':>12} | {'Qox FDM':>12} | {'% Dev (Qox)':>12}"
print(header)
print("-" * len(header))

for m in ["Price", "Delta", "Gamma", "Theta"]:
    bench = ql_an[m]
    ql_val = ql_fdm[m]
    qox_val = qox_fdm[m]

    ql_dev = abs(100.0 * (ql_val / bench - 1.0)) if bench != 0 else 0
    qox_dev = abs(100.0 * (qox_val / bench - 1.0)) if bench != 0 else 0

    print(
        f"{m:<10} | {bench:>12.6f} | {ql_val:>12.6f} | {ql_dev:>11.4f}% | {qox_val:>12.6f} | {qox_dev:>11.4f}%"
    )
