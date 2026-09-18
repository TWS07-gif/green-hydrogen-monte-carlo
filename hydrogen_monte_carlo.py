"""
Teesside Green Hydrogen — Bayesian MCMC Financial Model (v2, realism-checked)
==============================================================================
Two-stage analysis:
  Stage 1 — Metropolis-Hastings MCMC samples the posterior over four
            economic parameters (strike price, gilt rate, CPI, market
            parity price), given a Gaussian likelihood against an
            observed grey-hydrogen parity benchmark.
  Stage 2 — Posterior draws feed a forward simulation of the 15-year
            HPBM two-way CfD cashflow, including a bounded two-regime
            clawback model, producing a full NPV distribution.

All inputs are sourced and dated in README.md (two sources each where
available). Numpy + Matplotlib only; seeded, so results reproduce.
"""

import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# 1. BASE PARAMETERS
# =====================================================================
SEED = 42
N_CHAINS = 4
N_SAMPLES = 25_000            # retained draws per chain (post-thinning)
N_BURNIN = 5_000              # discarded warm-up iterations per chain
THIN = 5                      # keep every 5th post-burnin draw
PROPOSAL_SD = np.array([6.0, 0.004, 0.006, 4.5])  # MH step sizes

# --- Fleet & CapEx ----------------------------------------------------
NUM_UNITS = 20
CAPACITY_PER_UNIT_MW = 475                     # 9.5 GW total
ELECTROLYSER_CAPEX_PER_KW = 1_500              # GBP/kW installed (see README:
                                               # EUR ~1,700-2,300/kW Western
                                               # alkaline, USD 900-1,500 Chinese
                                               # PEM; midpoint assumed for a
                                               # 2030s GW-scale UK build)
CAPEX_PER_UNIT = CAPACITY_PER_UNIT_MW * 1_000 * ELECTROLYSER_CAPEX_PER_KW
TOTAL_CAPEX = NUM_UNITS * CAPEX_PER_UNIT       # ~£14.25B

# --- Energy -----------------------------------------------------------
CAPACITY_GW = NUM_UNITS * CAPACITY_PER_UNIT_MW / 1_000
# Dogger Bank-class 55% load factor; sensitivity band 45-60%.
CF_MIN, CF_MODE, CF_MAX = 0.45, 0.50, 0.60
CAPACITY_FACTOR = CF_MODE                      # central case
ANNUAL_VOLUME_MWH = CAPACITY_GW * 1e3 * 8_760 * CAPACITY_FACTOR  # 41.61 TWh
VOLUME_CAP_PCT = 0.75                          # LCHA allocation cap
CAPPED_VOLUME_MWH = ANNUAL_VOLUME_MWH * VOLUME_CAP_PCT

SUPPORT_PERIOD_YEARS = 15

# --- Carbon -----------------------------------------------------------
CARBON_PRICE_PER_TONNE = 49.41                 # UK ETS 2026 determination
CO2_PER_KG_H2 = 10.0                           # unabated SMR displacement
                                               # (IEA, The Future of Hydrogen)
ELECTROLYSER_KWH_PER_KG = 50.0
INDUSTRIAL_OFFTAKE_TWH = 5.0                   # TWh/yr earmarked to displace
                                               # unabated SMR grey H2 on
                                               # Teesside (redistribution of
                                               # existing industrial demand).
                                               # Carbon revenue is credited on
                                               # this displaced volume only —
                                               # crediting the full 832 kt
                                               # output would double-count
                                               # hydrogen that is simply
                                               # supplying new demand.

# --- Likelihood observation ------------------------------------------
Y_OBS_MARKET = 52.0        # observed grey-H2 parity (£/MWh)
MARKET_SIGMA = 8.0         # observation noise (£/MWh)

# --- Two-regime market model (BOUNDED clawback realism fix) -----------
CRISIS_PROB = 0.15               # P(energy-crisis year)
CRISIS_MULT_LOGMU = np.log(3.0)  # median crisis price = 3x parity
CRISIS_MULT_LOGSIGMA = 0.5
CRISIS_MULT_CAP = 6.0            # hard cap: crisis price <= 6x parity
                                 # (mirrors 2022 EU gas spike: TTF peaked
                                 # ~4-6x the 2019 median)


# =====================================================================
# 2. PRIORS (triangular; theta = strike, gilt, cpi, market_parity)
# =====================================================================
PRIORS = {
    "strike": (220.0, 241.0, 260.0),   # £/MWh — HAR1 weighted avg £241
    "gilt":   (0.045, 0.0534, 0.065),  # 10-yr gilt, Sep 2026 ~5.3-5.4%
    "cpi":    (0.015, 0.020, 0.035),   # inflation
    "market": (35.0, 52.0, 75.0),      # £/MWh — grey H2 parity
}
PRIOR_ORDER = ["strike", "gilt", "cpi", "market"]


def triangular_logpdf(x, lo, mode, hi):
    """log of the triangular density at x (0 outside support)."""
    if x < lo or x > hi or mode <= lo or mode >= hi:
        return -np.inf
    if x <= mode:
        f = 2.0 * (x - lo) / ((hi - lo) * (mode - lo))
    else:
        f = 2.0 * (hi - x) / ((hi - lo) * (hi - mode))
    return np.log(f) if f > 0 else -np.inf


def log_prior(theta):
    lp = 0.0
    for name, x in zip(PRIOR_ORDER, theta):
        lp += triangular_logpdf(x, *PRIORS[name])
    return lp


# =====================================================================
# 3. LIKELIHOOD
#    The parity benchmark informs the market-price parameter. Policy
#    parameters (strike, gilt, CPI) are prior-driven: they are set by
#    negotiation and macro conditions, not by the market observation.
# =====================================================================
def log_likelihood(theta):
    market = theta[3]
    resid = Y_OBS_MARKET - market
    return -0.5 * (resid / MARKET_SIGMA) ** 2


def log_posterior(theta):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta)


# =====================================================================
# 4. METROPOLIS-HASTINGS SAMPLER
# =====================================================================
def metropolis_hastings(n_samples, n_burnin, thin, seed):
    """Random-walk MH. Returns (samples, post-burnin acceptance rate)."""
    rng = np.random.default_rng(seed)
    theta = np.array([PRIORS[p][1] for p in PRIOR_ORDER])  # start at modes
    log_p = log_posterior(theta)

    n_iter = n_burnin + n_samples * thin
    kept = np.empty((n_samples, theta.size))
    n_prop_post = 0
    n_acc_post = 0
    k = 0
    for i in range(n_iter):
        proposal = theta + rng.normal(0.0, PROPOSAL_SD)
        log_p_new = log_posterior(proposal)
        accept = np.log(rng.random()) < log_p_new - log_p
        if accept:
            theta, log_p = proposal, log_p_new
        if i >= n_burnin:
            n_prop_post += 1
            n_acc_post += accept
            if (i - n_burnin) % thin == 0:
                kept[k] = theta
                k += 1
    return kept, n_acc_post / n_prop_post


def gelman_rubin(chains):
    """R-hat: pooled vs within-chain variance ratio. ~1.0 = converged."""
    chains = np.asarray(chains)                  # (m, n, dim)
    m, n, _ = chains.shape
    chain_means = chains.mean(axis=1)            # (m, dim)
    W = chains.var(axis=1, ddof=1).mean(axis=0)  # within-chain variance
    B = n * chain_means.var(axis=0, ddof=1)      # between-chain variance
    var_hat = (n - 1) / n * W + B / n
    return np.sqrt(var_hat / W)


def _autocorr(x):
    """FFT-based autocorrelation function of a 1-D series."""
    n = len(x)
    x = x - x.mean()
    f = np.fft.fft(x, 2 * n)
    acf = np.fft.ifft(f * np.conj(f)).real[:n]
    return acf / acf[0]


def effective_sample_size(chains):
    """ESS via Geyer initial-positive-pair truncation of the IACT."""
    chains = np.asarray(chains)
    m, n, d = chains.shape
    ess = np.empty(d)
    for k in range(d):
        acf_avg = np.zeros(n)
        for c in range(m):
            acf_avg += _autocorr(chains[c, :, k])
        acf_avg /= m
        tau = 1.0
        for t in range(1, n - 1, 2):
            pair = acf_avg[t] + acf_avg[t + 1]
            if pair < 0:
                break
            tau += 2.0 * pair
        ess[k] = m * n / tau
    return ess


# =====================================================================
# 5. RUN SAMPLER
# =====================================================================
print("=" * 62)
print(" TEESSIDE GREEN HYDROGEN — MCMC (Metropolis-Hastings)")
print("=" * 62)

chain_seeds = [SEED + i for i in range(N_CHAINS)]
results = [metropolis_hastings(N_SAMPLES, N_BURNIN, THIN, s)
           for s in chain_seeds]

samples_per_chain = [r[0] for r in results]
accept_rates = [r[1] for r in results]
all_samples = np.stack(samples_per_chain)      # (m, n, dim)

rhat = gelman_rubin(all_samples)
ess = effective_sample_size(all_samples)
flat = all_samples.reshape(-1, all_samples.shape[-1])

print(f"\nChains: {N_CHAINS} x {N_SAMPLES:,} draws "
      f"(burn-in {N_BURNIN:,}, thin {THIN})")
print(f"Acceptance rates: {[f'{a:.3f}' for a in accept_rates]}")
print(f"R-hat (strike, gilt, cpi, market): {np.round(rhat, 4).tolist()}")
print(f"ESS   (strike, gilt, cpi, market): {ess.astype(int).tolist()}")

# =====================================================================
# 6. POSTERIOR PREDICTIVE: 15-year CfD cashflow + clawback
# =====================================================================
strike_post, gilt_post, cpi_post, market_post = flat.T

# Capacity-factor uncertainty propagated through the volume term.
cf_draw = np.random.default_rng(SEED + 7).triangular(
    CF_MIN, CF_MODE, CF_MAX, size=flat.shape[0]
)
annual_volume_draw = CAPACITY_GW * 1e3 * 8_760 * cf_draw
capped_volume_draw = annual_volume_draw * VOLUME_CAP_PCT

# Subsidy rate: strike minus gilt-discounted market (README formula).
subsidy_rate = strike_post * gilt_post / (1 + gilt_post)
year1_outflow = capped_volume_draw * subsidy_rate

# 15-year cashflow, CPI-escalated and gilt-discounted.
years = np.arange(1, SUPPORT_PERIOD_YEARS + 1)
cpi_factors = (1 + cpi_post[:, None]) ** (years - 1)
annual_outflow = year1_outflow[:, None] * cpi_factors
discount = (1 + gilt_post[:, None]) ** years
npv_gross = (annual_outflow / discount).sum(axis=1)
nominal_total = annual_outflow.sum(axis=1)

# --- Clawback (two-way CfD, bounded) ----------------------------------
# Market price per year follows a two-regime model:
#   parity regime:  noisy draw around the posterior parity price
#   crisis regime:  parity x lognormal multiplier, HARD-CAPPED at 6x
#                   parity to reflect observed energy-crisis dynamics
#                   (2022 TTF gas peaked ~4-6x the pre-crisis median).
# When market > strike, the operator pays the excess back to Treasury.
rng = np.random.default_rng(SEED + 999)
n_draws = flat.shape[0]
is_crisis = rng.random((n_draws, SUPPORT_PERIOD_YEARS)) < CRISIS_PROB
parity_noise = rng.normal(
    market_post[:, None], MARKET_SIGMA, (n_draws, SUPPORT_PERIOD_YEARS)
)
crisis_mult = rng.lognormal(
    CRISIS_MULT_LOGMU, CRISIS_MULT_LOGSIGMA, (n_draws, SUPPORT_PERIOD_YEARS)
)
crisis_mult = np.minimum(crisis_mult, CRISIS_MULT_CAP)
market_year = np.where(is_crisis, parity_noise * crisis_mult, parity_noise)

strike_year = strike_post[:, None] * cpi_factors   # strike escalates w/ CPI
clawback_year = np.maximum(market_year - strike_year, 0.0) * capped_volume_draw[:, None]
clawback_pv = (clawback_year / discount).sum(axis=1)
npv_net = npv_gross - clawback_pv

# --- Carbon offset revenue -------------------------------------------
# Credited only on the industrial offtake volume that actually displaces
# unabated SMR hydrogen (INDUSTRIAL_OFFTAKE_TWH); a 0.85-1.15 triangular
# factor captures realisation risk on the displacement commitment.
industrial_h2_kg = INDUSTRIAL_OFFTAKE_TWH * 1e9 / ELECTROLYSER_KWH_PER_KG
co2_avoided = industrial_h2_kg * CO2_PER_KG_H2 / 1_000   # tonnes/yr
carbon_vol = co2_avoided * rng.triangular(0.85, 1.0, 1.15, size=n_draws)
carbon_revenue = carbon_vol * CARBON_PRICE_PER_TONNE

# =====================================================================
# 7. SUMMARY
# =====================================================================
def pct(x, q):
    return np.percentile(x, q)


# Deterministic base case (all params at prior modes) for reference.
base_theta = np.array([PRIORS[p][1] for p in PRIOR_ORDER])
base_subsidy = base_theta[0] * base_theta[1] / (1 + base_theta[1])
base_npv = sum(
    CAPPED_VOLUME_MWH * base_subsidy * (1 + base_theta[2]) ** (t - 1)
    / (1 + base_theta[1]) ** t
    for t in years
)

print("\n" + "-" * 62)
print(" POSTERIOR SUMMARY (95% credible intervals)")
print("-" * 62)
for j, name in enumerate(PRIOR_ORDER):
    lo, hi = pct(flat[:, j], 2.5), pct(flat[:, j], 97.5)
    unit = "%" if name in ("gilt", "cpi") else "£/MWh"
    scale = 100 if unit == "%" else 1
    print(f" {name:>7}: {flat[:, j].mean() * scale:8.2f} {unit}  "
          f"[{lo * scale:.2f}, {hi * scale:.2f}]")
print("-" * 62)
print(" FORWARD SIMULATION (posterior predictive)")
print("-" * 62)
print(f" Mean subsidy rate:          £{subsidy_rate.mean():.2f} / MWh")
print(f" Mean Year-1 gross outflow:  £{year1_outflow.mean() / 1e6:.2f} Million")
print(f" Mean 15-yr nominal total:   £{nominal_total.mean() / 1e9:.3f} Billion")
print(f" Mean Govt NPV (gross):      £{npv_gross.mean() / 1e9:.3f} Billion")
print(f" Mean Govt NPV (net clawback): £{npv_net.mean() / 1e9:.3f} Billion")
print(f" P10 NPV (downside):         £{pct(npv_net, 10) / 1e9:.3f} Billion")
print(f" P90 NPV (upside):           £{pct(npv_net, 90) / 1e9:.3f} Billion")
print(f" P(clawback in any given year): {(clawback_year > 0).mean() * 100:.2f}%")
print(f" P(clawback event in 15 yrs): {(clawback_pv > 0).mean() * 100:.1f}%")
print(f" Mean annual carbon revenue: £{carbon_revenue.mean() / 1e6:.2f} Million/yr")
print("-" * 62)
print(f" Fleet CapEx:                £{TOTAL_CAPEX / 1e9:.1f} Billion "
      f"(£{ELECTROLYSER_CAPEX_PER_KW}/kW installed)")
print(f" Annual H2 output:           "
      f"{ANNUAL_VOLUME_MWH * 1000 / ELECTROLYSER_KWH_PER_KG / 1e9:.2f} Mt/yr")
print(f" Deterministic base case NPV (modes): £{base_npv / 1e9:.3f} Billion")
print("=" * 62)

# =====================================================================
# 8. VISUALISATION
# =====================================================================
fig, axes = plt.subplots(2, 2, figsize=(13, 9))

# (a) NPV histogram, gross vs net of clawback
ax = axes[0, 0]
ax.hist(npv_gross / 1e9, bins=60, alpha=0.55, color="#1f77b4",
        edgecolor="black", label="Gross (no clawback)")
ax.hist(npv_net / 1e9, bins=60, alpha=0.55, color="#d62728",
        edgecolor="black", label="Net (with clawback)")
ax.axvline(base_npv / 1e9, color="green", ls=":", lw=2,
           label=f"Base case (£{base_npv / 1e9:.2f}B)")
ax.set_title("Government NPV — Effect of Two-Way CfD Clawback")
ax.set_xlabel("NPV (£ Billions)")
ax.set_ylabel("Frequency")
ax.legend()

# (b) Trace plot — market parity, chain 1
ax = axes[0, 1]
ax.plot(samples_per_chain[0][:, 3], lw=0.4, alpha=0.6)
ax.axhline(market_post.mean(), color="red", ls="--", lw=1.5)
ax.set_title(f"Trace: Market Parity (chain 1), R-hat={rhat[3]:.4f}")
ax.set_xlabel("Draw")
ax.set_ylabel("Parity Price (£/MWh)")

# (c) Posterior vs prior — market parity (the data-updated parameter)
ax = axes[1, 0]
ax.hist(market_post, bins=60, density=True, alpha=0.6, color="#2ca02c",
        edgecolor="black", label="Posterior")
lo, mode, hi = PRIORS["market"]
xs = np.linspace(lo, hi, 300)
prior_pdf = np.where(
    xs <= mode,
    2 * (xs - lo) / ((hi - lo) * (mode - lo)),
    2 * (hi - xs) / ((hi - lo) * (hi - mode)),
)
ax.plot(xs, prior_pdf, "k--", lw=2, label="Prior")
ax.axvline(Y_OBS_MARKET, color="orange", ls=":", lw=2,
           label=f"Observation (£{Y_OBS_MARKET:.0f})")
ax.set_title(f"Bayesian Updating: Market Parity (ESS={ess[3]:.0f})")
ax.set_xlabel("Parity Price (£/MWh)")
ax.set_ylabel("Density")
ax.legend()

# (d) NPV histogram (net), with percentiles
ax = axes[1, 1]
ax.hist(npv_net / 1e9, bins=60, color="#1f77b4", edgecolor="black",
        alpha=0.75)
ax.axvline(npv_net.mean() / 1e9, color="red", ls="--", lw=2,
           label=f"Mean (£{npv_net.mean() / 1e9:.2f}B)")
ax.axvline(pct(npv_net, 10) / 1e9, color="orange", ls=":", lw=2,
           label=f"P10 (£{pct(npv_net, 10) / 1e9:.2f}B)")
ax.axvline(pct(npv_net, 90) / 1e9, color="green", ls=":", lw=2,
           label=f"P90 (£{pct(npv_net, 90) / 1e9:.2f}B)")
ax.set_title("Posterior Predictive NPV (net of clawback)")
ax.set_xlabel("NPV (£ Billions)")
ax.set_ylabel("Frequency")
ax.legend()

plt.suptitle("Teesside Green Hydrogen — Bayesian MCMC Model",
             fontsize=13, y=0.995)
plt.tight_layout()
plt.savefig("mcmc_diagnostics.png", dpi=300, bbox_inches="tight")
print("\nSaved 2x2 diagnostic figure as 'mcmc_diagnostics.png'")
