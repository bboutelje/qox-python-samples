# QoX Python Examples

**QoX** is a fast and accurate library written in Rust, and designed to work in production environments. These samples demonstrate its performance and ease of use.

---

## 🚀 Support the R&D
**[❤ Sponsor QoX on GitHub](https://github.com/sponsors/bboutelje)**

Sponsorship funds the R&D of this project. The base Python implementation will always remain free.

> *Note: Sponsorship is for patronage only. It does not include technical support, consulting, or access to private source code.*

---

## 🚀 Get Started Instantly

The easiest way to explore these examples is via **Google Colab**. No installation required.

| Example | Notebook | Interactive Demo |
| :--- | :--- | :--- |
| **Quickstart Guide** | [`quickstart.ipynb`](./notebooks/quickstart.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/bboutelje/qox-python-samples/blob/main/notebooks/quickstart.ipynb) |

## 🛠 Local Installation

If you are a developer and want to run these scripts on your own machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/bboutelje/qox-python-samples.git](https://github.com/bboutelje/qox-python-samples.git)
   cd qox-python-samples

## 🏎 Performance: QoX vs. QuantLib

This benchmark compares American Put pricing using Finite Difference Methods (FDM). 

**Result:** So far, QoX achieves at least a **10x speedup** over QuantLib for any given accuracy level.

| Steps | QL Latency | QL Error | QoX Latency | QoX Error |
| :--- | :--- | :--- | :--- | :--- |
| 5 | 1.08 ms | 1.57e-01 | **196.2 μs** | 1.53e-02 |
| 10 | 1.93 ms | 6.10e-02 | **449.5 μs** | 4.20e-03 |
| 25 | 2.25 ms | 2.77e-02 | **884.2 μs** | 2.30e-03 |
| 50 | 3.27 ms | 1.39e-02 | **1.49 ms** | 2.00e-03 |
| 100 | 5.16 ms | 6.82e-03 | **2.72 ms** | 2.40e-04 |
| 250 | 13.69 ms | 2.83e-03 | **7.46 ms** | 4.88e-04 |
| 500 | 24.83 ms | 1.43e-03 | **14.67 ms** | 2.99e-04 |
| 1000 | 44.84 ms | 7.10e-04 | **27.35 ms** | 1.04e-04 |
| 2000 | 90.09 ms | 3.48e-04 | **56.16 ms** | 2.34e-05 |

![FDM Convergence Graph](./benchmarks/fdm_convergence.png)

### 📊 Methodology Note
This is a baseline comparison using single-run (cold start) latencies. While it lacks a formal warm-up phase, the data sufficiently demonstrates the fundamental performance disparity between the two solvers.
  
---

**This is just the baseline; further optimizations are in progress.**

## 🗺️ Roadmap

**v0.1.0**
* Core FDM library.
* American exercise condition.
* Baseline performance benchmarks.

**v0.2.0**
* Support for discrete dividends.

**v0.3.0**
* Implied Volatility (IV) solvers.

**Immediate Future**
* Yield curve framework.
* Volatility surfaces.
* Support for Business/252 day count.
* Full coverage of Black-Scholes based equity vol desk requirements.

*Note: Near term projected path; subject to change.*
