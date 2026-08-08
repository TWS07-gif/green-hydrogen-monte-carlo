# green-hydrogen-monte-carlo
monte carlo for my proposed business project
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TWS07-gif/green-hydrogen-monte-carlo/blob/main/hydrogen_monte_carlo.py)

# Teesside Green Hydrogen Production: Monte Carlo & Financial Valuation Model

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_GITHUB_USERNAME/green-hydrogen-monte-carlo/blob/main/hydrogen_monte_carlo.py)

This repository contains a quantitative financial model and Monte Carlo simulation analyzing the public sector cost, private returns, and financial viability of a **9.5 GW scale Green Hydrogen Deployment (20x 475 MW electrolysers)** in Teesside, UK.

The evaluation models the **Hydrogen Production Business Model (HPBM)** operating via a **Two-Way Contract for Difference (CfD)** under the **Low Carbon Hydrogen Agreement (LCHA)** over a 15-year support window.

---

##  EXECUTIVE SUMMARY

* **Total Fleet Scale:** 9.5 GW total capacity across 20 units (475 MW average capacity per unit).
* **Total CapEx:** £2.80 Billion (£140M per 475 MW unit).
* **Annual Energy Output:** 55.3 TWh / annum (55,300,000 MWh).
* **Base Subsidy Rate:** £9.58 / MWh (Derived from Strike Price vs. UK Gilt-adjusted market price).
* **Gross Government Support Outflow (Year 1):** £397.33 Million (at 75% volume allocation cap).
* **15-Year Nominal Government Outflow:** £6.87 Billion (factoring 2.0% annual CPI compounding).
* **Net Present Value (NPV) to Government:** £4.56 Billion (discounted at 5.34% Risk-Free Rate).
* **Carbon Offset Revenue Potential:** £74.12 Million / year raised via UK ETS Carbon Pricing.

---

##  MECHANICS: HYDROGEN PRODUCTION BUSINESS MODEL (HPBM)

The project utilizes a **Two-Way Contract for Difference (CfD)** between the UK Government and private facility operators under the **Low Carbon Hydrogen Agreement (LCHA)**:

1. **Risk Allocation:**
   * **Private Sector:** Bears 100% of construction, capital expenditure, and operational risk.
   * **Government:** Bears 100% of the market/off-take price volatility risk.
2. **Pricing Structure:**
   * **Agreed Strike Price:** £241.00 / MWh (covers production cost + agreed private return margin).
   * **End-User Market Price:** £52.00 / MWh (pegged to grey/fossil hydrogen market parity).
   * **Clawback Provision:** If the market price exceeds the Strike Price during the 15-year period, excess profits are returned directly to the UK Treasury.
3. **Infrastructure Enabling:**
   * Teesside Development Corporation removes site barriers by offering pre-approved industrial land, pipeline connections, and expedited planning permission.

---

##  FINANCIAL MODELING & SUBSIDY CALCULATIONS

### 1. Base Subsidy Rate (£/MWh)
$$\text{Expected Market Price} = \frac{\text{Strike Price}}{1 + \text{Gilt Rate}} = \frac{£189.00}{1.0534} = £179.42/\text{MWh}$$

$$\text{Base Subsidy Rate} = £189.00 - £179.42 = £9.58/\text{MWh}$$

### 2. Year 1 Gross Government Outflow
$$\text{Capped Annual Volume} = 55,300,000\text{ MWh} \times 75\% = 41,475,000\text{ MWh}$$

$$\text{Year 1 Outflow} = 41,475,000\text{ MWh} \times £9.58/\text{MWh} = \mathbf{£397,330,500.00}$$

### 3. 15-Year Nominal Support Outflow (2.0% CPI Compounding)
$$\text{Nominal Outflow} = \sum_{t=1}^{15} \left[ £397,330,500 \times (1 + 0.02)^{t-1} \right] = \mathbf{£6,871,201,990.02}$$

### 4. Government Net Present Value (NPV)
$$\text{NPV} = \sum_{t=1}^{15} \left[ \frac{£397,330,500 \times (1.02)^{t-1}}{(1 + 0.0534)^t} \right] = \mathbf{£4,559,295,342.32}$$

---

##  KEY PROJECT ASSUMPTIONS

### Technical & Production Assumptions
* **Electrolyser Efficiency / Energy Intensity:** 50 kWh / kg H₂ (33.3 kWh/kg LHV baseline).
* **Wind Power Integration:** 55% average offshore wind capacity factor; 100% of offshore wind output dedicated to hydrogen production.
* **Teesside Wind Fleet Allocation:** 10% of total regional Teesside offshore wind generation earmarked for the plant.
* **Volume Floor & Allocation Cap:** 75% minimum volume support cap under LCHA rules.

### Macroeconomic & Market Assumptions
* **Inflation Rate:** 2.0% annual CPI compounding.
* **Discount Rate:** 5.34% Risk-Free Rate (aligned with 10-Year UK Gilt Yields).
* **UK ETS Carbon Price:** £49.41 / tonne CO₂e ([UK ETS 2026 Civil Penalty Determination](https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-price-for-use-in-civil-penalties-2026)).
* **Avoided Emissions:**
  * $5\text{ TWh} = 5,000,000,000\text{ kWh}$
  * $5,000,000,000\text{ kWh} / 33.3\text{ kWh/kg} = 150,000,000\text{ kg H}_2$
  * $150,000,000\text{ kg H}_2 \times 10\text{ kg CO}_2\text{ offset} = 1,500,000\text{ tonnes CO}_2$
  * **Annual Carbon Revenue:** $1,500,000\text{ tonnes} \times £49.41 = \mathbf{£74,115,000/\text{year}}$

---

##  ECONOMIC JUSTIFICATION & PUBLIC FINANCE IMPACT

* **Budgetary Impact:** The 15-year subsidy represents **~0.5% of the UK annual national budget (2025 baseline)** ([OBR Public Finances](https://obr.uk/forecasts-in-depth/brief-guides-and-explainers/public-finances/)).
* **Replacing Energy Relief Subsidies:** The UK historically allocated £7B+ subsidizing energy-intensive industries facing high power bills ([Gov.uk Energy Relief Scheme](https://www.gov.uk/government/news/government-cuts-electricity-bill-for-10000-manufacturers-in-boost-for-uk-competitiveness)). Transitioning industrial manufacturing to locally produced Teesside green hydrogen provides long-term energy security without requiring ongoing emergency state relief interventions.
* **Socioeconomic Benefits:** Accelerates private capital investment into the Teesside industrial cluster, boosting local highly-skilled employment, regional wage scales, and technical human capital.

---

##  DATA SOURCES & REFERENCES

1. [World Hydrogen Leaders - UK Green Hydrogen Subsidy Agreements](https://www.worldhydrogenleaders.com/subsidy-agreements-signed-for-10-uk-green-hydrogen-projects)
2. [Hargreaves Lansdown - UK Gilt Yields & Bond Prices](https://www.hl.co.uk/shares/corporate-bonds-gilts/bond-prices/uk-gilts)
3. [ScienceDirect - Green Hydrogen Production Cost Models](https://www.sciencedirect.com/science/article/pii/S1750583623000749)
4. [Solar Panels for Factories - UK Electricity Price Forecast 2026-2030](https://solarpanelsforfactories.co.uk/blog/uk-electricity-price-forecast-2026-2030-factories/)
5. [Reuters - Large-Scale Electrolyser Deployment Benchmarks](https://www.reuters.com/business/energy/vng-start-test-operations-30-mw-electrolyser-q3-2025-2025-04-02/)
6. [UK Gov - Hydrogen Production Business Model (HPBM)](https://www.gov.uk/government/publications/hydrogen-production-business-model)
7. [Low Carbon Contracts Company (LCCC) - Low Carbon Hydrogen Scheme](https://www.lowcarboncontracts.uk/our-schemes/low-carbon-hydrogen/)
8. [S&P Global - HAR1 Green Hydrogen Contracts](https://www.spglobal.com/energy/en/news-research/latest-news/energy-transition/121224-uk-offers-first-green-hydrogen-production-contracts-to-har1-projects)
9. [Office for Budget Responsibility - Public Finances Datasets](https://obr.uk/forecasts-in-depth/brief-guides-and-explainers/public-finances/)
10. [UK Gov - UK ETS Carbon Price Civil Penalties 2026](https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-price-for-use-in-civil-penalties-2026)
