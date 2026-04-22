# QoX Python Examples

**QoX** is a fast and accurate quant library written in Rust, designed to work in production environments. These samples demonstrate its performance and ease of use.

---

## 🚀 Support the R&D
**[❤ Sponsor QoX on GitHub](https://github.com/sponsors/bboutelje)**

Sponsorship funds the R&D of this project. The base Python implementation will always remain free.  
*Inquire about institutional sponsorship: **qox.library [at] gmail.com***

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

**Result:** QoX achieves up to a **40x** speedup over QuantLib at standard production precision (2 d.p.).

![FDM Convergence Graph](./benchmarks/fdm_convergence.png)

> **Technical Note:** Performance gains are optimized for standard production precision. While price convergence remains robust, please note that the speedup factor and Greek stability may vary near the early exercise boundary. Greek stability will be addressed in a future release.

### 📊 Methodology Note
This is a baseline comparison using single-run (cold start) latencies. While it lacks a formal warm-up phase, the data sufficiently demonstrates the fundamental performance disparity between the two solvers.

---

**This is just the baseline; further optimizations are in progress.**

## 🗺️ Roadmap

**v0.1.0**
* American exercise condition.
* Baseline performance benchmarks.

**v0.2.0**
* Support for discrete dividends.

**v0.3.0**
* Implied volatility solver.

**Other short-term goals**
* Yield curve framework.
* Volatility surfaces.
* Support for Business/252 day count.
* More advanced American options model.

*Note: Near term projected path; subject to change.*
