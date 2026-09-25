# QoX Python Examples

**QoX** is a finite difference quant library, written in Rust, with an unpublished numerical algorithm for American options. The samples provided in this repository demonstrate its performance. The current version (0.2.1) handles discrete dividends and implied volatility. 

The repository also provides a script which plots gamma and theta which are smooth sufficiently far from the exercise boundary depending on the chosen granularity. It works for vol greater than 10%, and it is untested for negative rates and high dividend yield. It assumes your hardware supports FMA3. Part of the working Rust code can be viewed in the qox-fdm repository.

---

## Consulting

*Inquire about consulting: **qox.library [at] gmail.com***

Other projects:

Pricing Black-Scholes at least 3x faster than the COS method, applicable to other stochastic processes. Robust across volatilities and time to expiry, even where the COS method requires more terms.

Sub-microsecond discrete dividend handling for European options.

Sub-microsecond American option pricing in development.

Sub-microsecond option calibration in development.

---

## Google Colab

| Example | Notebook | Interactive Demo |
| :--- | :--- | :--- |
| **Quickstart Guide** | [`quickstart.ipynb`](./notebooks/quickstart.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/bboutelje/qox-python-samples/blob/main/notebooks/quickstart.ipynb) |

## Local Installation

Run `pip install qox`.

---

## Performance: QoX vs. QuantLib

This benchmark compares American put pricing using the finite difference method where QoX achieves at least a 50x speedup over QuantLib to get the same accuracy for a 1 year ATM American option with the right parameters. This was done without SIMD and on one core.

![FDM Convergence Graph](./benchmarks/fdm_convergence.png)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

For commercial licensing, custom terms, or general enquiries, please email **qox.library [at] gmail.com***.
