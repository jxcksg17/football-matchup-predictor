<div align="center">

# ⚽ MatchPulse
### *Quantitative Football Outcome & Probability Simulation Engine*

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![JavaScript](https://img.shields.io/badge/ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)

<p align="center">
  A statistical modeling platform that discards black-box machine learning in favor of <b>Bivariate Poisson Goal Modeling</b>, <b>Dixon-Coles Low-Score Shrinkage</b>, and <b>Dynamic Elo Strength Tracking</b>.
</p>

[Explore Documentation](#-mathematical-architecture) • [Quickstart Guide](#-quickstart) • [API Reference](#-api-endpoints)

---

</div>

## 📌 Key Highlights

* **Dynamic Elo Rating System**: Calibrates inter-confederation and league imbalances with tournament-weighted K-factors and home ground scaling[span_0](start_span)[span_0](end_span).
* **Bivariate Poisson Distribution**: Generates goal distribution parameter sets ($\lambda_{\text{home}}, \lambda_{\text{away}}$) to simulate 0-0 through 6-6 scoreline probability matrices[span_1](start_span)[span_1](end_span).
* **Dixon-Coles Draw Correction**: Applies parameter $\rho$ adjustments on low-scoring permutations to prevent statistical draw-compression bugs[span_2](start_span)[span_2](end_span).
* **Multi-Scope Coverage**: Built-in support for **International Matches** and European **Club Competitions** (Premier League, La Liga)[span_3](start_span)[span_3](end_span).
* **Glassmorphic Analytical UI**: Dark-mode frontend rendering real-time outcome gauges, expected goals ($xG$), and joint probability distributions[span_4](start_span)[span_4](end_span).

---

## 🧮 Mathematical Architecture

MatchPulse determines match probabilities through a multi-stage quantitative pipeline:


### 1. Expected Goals ($\lambda$) Formulation
$$\lambda_{\text{Home}} = \mu \times 10^{\alpha (\text{Elo}_{\text{Home}} + \text{Adv} - \text{Elo}_{\text{Away}}) / 400}$$
$$\lambda_{\text{Away}} = \mu \times 10^{-\alpha (\text{Elo}_{\text{Home}} + \text{Adv} - \text{Elo}_{\text{Away}}) / 400}$$

### 2. Joint Probability Grid
$$P(X=x, Y=y) = \frac{\lambda_{\text{Home}}^x e^{-\lambda_{\text{Home}}}}{x!} \times \frac{\lambda_{\text{Away}}^y e^{-\lambda_{\text{Away}}}}{y!} \times \tau_{\rho}(x, y)$$

*(Where $\tau_{\rho}(x, y)$ applies the Dixon-Coles adjustment for low scorelines $x, y \le 1$).*

---
