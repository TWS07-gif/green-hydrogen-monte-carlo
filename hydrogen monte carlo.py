import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. BASE PARAMETERS (EXACT READ-ME DATA)
# ==========================================
ITERATIONS = 10_000
np.random.seed(42)

# Fleet Scale & CapEx
NUM_UNITS = 20
CAPACITY_PER_UNIT_MW = 475  # 9.5 GW Total Capacity
CAPEX_PER_UNIT = 140_000_000  # £140M per 475MW unit
TOTAL_CAPEX_BASE = NUM_UNITS * CAPEX_PER_UNIT  # £2.8 Billion

# Energy & Technical Assumptions
ANNUAL_VOLUME_MWH = 55_300_000  # 55.3 TWh total output
VOLUME_CAP_PCT = 0.75  # 75% Allocation Cap
CAPPED_VOLUME_MWH = ANNUAL_VOLUME_MWH * VOLUME_CAP_PCT  # 41,475,000 MWh
ELECTROLYSER_EFFICIENCY_KWH_KG = 50.0  # 50 kWh/kg H2

# Macroeconomic & Policy Inputs
GILT_YIELD_DISCOUNT_RATE = 0.0534  # 5.34% Risk-Free Rate
CPI_INFLATION_RATE = 0.02  # 2.0% Annual Inflation
SUPPORT_PERIOD_YEARS = 15

# Carbon Offset Parameters
CARBON_PRICE_PER_TONNE = 49.41  # UK ETS Price (£/tonne CO2)
BASE_CARBON_TONNES_SAVED = 1_500_000  # Based on 5 TWh industrial offset

# ==========================================
# 2. TRIANGULAR DISTRIBUTIONS (UNCERTAINTY)
# ==========================================
# Strike Price (£/MWh): Min £220, Mode £241, Max £260
strike_price_sim = np.random.triangular(220.0, 241.0, 260.0, size=ITERATIONS)

# Gilt / Discount Rate: Min 4.5%, Mode 5.34%, Max 6.5%
gilt_rate_sim = np.random.triangular(0.045, 0.0534, 0.065, size=ITERATIONS)

# CPI Inflation Rate: Min 1.5%, Mode 2.0%, Max 3.5%
cpi_sim = np.random.triangular(0.015, 0.02, 0.035, size=ITERATIONS)

# Market End Price (£/MWh): Min £35, Mode £52, Max £75
market_price_sim = np.random.triangular(35.0, 52.0, 75.0, size=ITERATIONS)

# Carbon Offset Volume (Tonnes): +/- 15% variance
carbon_vol_sim = np.random.triangular(
    BASE_CARBON_TONNES_SAVED * 0.85,
    BASE_CARBON_TONNES_SAVED,
    BASE_CARBON_TONNES_SAVED * 1.15,
    size=ITERATIONS,
)

# ==========================================
# 3. MONTE CARLO CALCULATIONS
# ==========================================
# Base Subsidy Rate (£/MWh) Calculation per iteration
# Strike Price / (1 + Gilt Rate) vs Base Strike
expected_market_price = strike_price_sim / (1 + gilt_rate_sim)
base_subsidy_rate_sim = strike_price_sim - expected_market_price

# Year 1 Outflow (£)
year_1_outflow_sim = CAPPED_VOLUME_MWH * base_subsidy_rate_sim

# 15-Year Nominal Outflow with CPI Compounding
years = np.arange(1, SUPPORT_PERIOD_YEARS + 1)
# Shape: (ITERATIONS, 15)
cpi_factors = (1 + cpi_sim[:, np.newaxis]) ** (years - 1)
annual_nominal_outflows = year_1_outflow_sim[:, np.newaxis] * cpi_factors
nominal_total_sim = np.sum(annual_nominal_outflows, axis=1)

# Net Present Value (NPV) Calculation
discount_factors = (1 + gilt_rate_sim[:, np.newaxis]) ** years
pv_cash_flows = annual_nominal_outflows / discount_factors
npv_sim = np.sum(pv_cash_flows, axis=1)

# Annual Carbon Tax Revenue Saved (£)
annual_carbon_revenue_sim = carbon_vol_sim * CARBON_PRICE_PER_TONNE

# ==========================================
# 4. STATISTICAL SUMMARY & OUTPUT
# ==========================================
mean_npv = np.mean(npv_sim) / 1e9
p10_npv = np.percentile(npv_sim, 10) / 1e9
p90_npv = np.percentile(npv_sim, 90) / 1e9

mean_nominal = np.mean(nominal_total_sim) / 1e9
mean_year1 = np.mean(year_1_outflow_sim) / 1e6
mean_subsidy_rate = np.mean(base_subsidy_rate_sim)
mean_carbon_rev = np.mean(annual_carbon_revenue_sim) / 1e6

print("==========================================================")
print(" TEESSIDE 9.5GW GREEN HYDROGEN - MONTE CARLO SIMULATION   ")
print("==========================================================")
print(f"Mean Subsidy Rate:                 £{mean_subsidy_rate:.2f} / MWh")
print(f"Mean Year 1 Gross Outflow:          £{mean_year1:.2f} Million")
print(f"Mean 15-Yr Nominal Support Total:  £{mean_nominal:.3f} Billion")
print(f"Mean Govt NPV (Base Case £4.56B):  £{mean_npv:.3f} Billion")
print(f"P10 NPV (Downside Case):            £{p10_npv:.3f} Billion")
print(f"P90 NPV (Upside Case):              £{p90_npv:.3f} Billion")
print(f"Mean Annual Carbon Revenue Raised:  £{mean_carbon_rev:.2f} Million / yr")
print("==========================================================")

# ==========================================
# 5. VISUALIZATION PLOT
# ==========================================
plt.figure(figsize=(10, 5))
plt.hist(npv_sim / 1e9, bins=50, color="#1f77b4", edgecolor="black", alpha=0.75)
plt.axvline(
    mean_npv,
    color="red",
    linestyle="--",
    linewidth=2,
    label=f"Mean NPV (£{mean_npv:.2f}B)",
)
plt.axvline(
    4.559,
    color="green",
    linestyle=":",
    linewidth=2,
    label="README Baseline (£4.56B)",
)
plt.title(
    "Govt Net Present Value (NPV) Distribution - 15-Yr HPBM Support Scheme"
)
plt.xlabel("Net Present Value (£ Billions)")
plt.ylabel("Frequency (Iterations)")
plt.legend()
plt.tight_layout()
plt.savefig("npv_distribution.png", dpi=300)
print("\nHistogram plot saved successfully as 'npv_distribution.png'")
