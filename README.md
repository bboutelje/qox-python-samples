# QoX Python Examples

This directory contains sample implementations using the QoX library. You can run these locally or instantly in the cloud via Google Colab.

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

## 🏎 Benchmarks: QoX vs. QuantLib

This is a head-to-head convergence test for American Put pricing (FDM). 

| Steps | QL Latency | QL Error | QoX Latency | QoX Error |
| :--- | :--- | :--- | :--- | :--- |
| **5** | 1.23 ms | 1.43e-01 | **212.8 μs** | **1.53e-02** |
| **50** | 4.33 ms | 1.52e-02 | **1.62 ms** | **2.00e-03** |
| **1000** | 50.64 ms | 7.44e-04 | **30.20 ms** | **1.03e-04** |

### The Reality:
* **Microsecond Floor:** QoX hits the board in **$<250\mu s$**. Legacy engines are often stuck in the millisecond range before they even return a price.
* **Efficiency:** QoX at **50 steps** is more accurate than QuantLib at **500 steps**—and it gets there **21x faster**.
* **Stability:** No "damping" hacks or scheme-switching required. The math is just tighter.

**And this is just the beginning.**

> Run the benchmark: [`benchmarks/fdm_temporal_convergence.py`](./benchmarks/fdm_temporal_convergence.py)
