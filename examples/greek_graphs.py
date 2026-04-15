from datetime import datetime
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import numpy as np

import qox

# 1. Setup the core Instrument and Configuration
ny_tz = ZoneInfo("America/New_York")
valuation_time = datetime(2025, 9, 25, 17, 0, tzinfo=ny_tz)
expiry = datetime(2026, 9, 25, 17, 0, tzinfo=ny_tz)

# Define an American Put Option with Strike 100
vanilla_option = qox.VanillaOption(
    100.0, expiry, qox.OptionType.Put, qox.ExerciseStyle.American
)

# Configuration for Finite Difference Method (FDM)
time_steps = 50
fdm_config = qox.FdmConfig(nodes=1000, time_steps=time_steps)
config = qox.Config().add_policy(
    qox.InstrumentPolicy().american().put().fdm(fdm_config)
)

# 2. Define the range of Spot Prices to analyze
spot_prices = np.linspace(50.0, 150.0, 50)  # From $50 to $150
thetas = []
gammas = []

# 3. Loop through spots and compute Theta
for s in spot_prices:
    market_frame = qox.OptionMarketFrame(
        spot=s,
        rate_curve=qox.RateCurve.continuous(0.05, qox.DayCountConvention.ACT_365_FIXED),
        vol_surface=qox.VolSurface.flat(0.2, qox.DayCountConvention.ACT_365_FIXED),
    )

    result = (
        vanilla_option.valuation()
        .at(valuation_time)
        .market(market_frame)
        .config(config)
        .compute()
    )

    thetas.append(result.greeks.theta)
    gammas.append(result.greeks.gamma)

# --- Window 1: Theta ---
plt.figure(1, figsize=(10, 6))  # Explicitly naming this Figure 1
plt.plot(spot_prices, thetas, label="Theta", color="firebrick", linewidth=2)
plt.title("Option Theta vs. Spot Price", fontsize=14)
plt.xlabel("Spot Price", fontsize=12)
plt.ylabel("Theta", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.7)
plt.axvline(x=100, color="black", linestyle=":", label="Strike Price (100)")
plt.legend()

# --- Window 2: Gamma ---
plt.figure(2, figsize=(10, 6))  # Explicitly naming this Figure 2
plt.plot(spot_prices, gammas, label="Gamma", color="forestgreen", linewidth=2)
plt.title("Option Gamma vs. Spot Price", fontsize=14)
plt.xlabel("Spot Price", fontsize=12)
plt.ylabel("Gamma", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.7)
plt.axvline(x=100, color="black", linestyle=":", label="Strike Price (100)")
plt.legend()

# This single call opens both windows at once
plt.show()
