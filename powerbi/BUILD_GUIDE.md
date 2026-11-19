# Power BI Build Guide — ~35 minutes, no guesswork

Prereq: Run `python src/train.py && python src/predict_and_segment.py` first.
In Power BI Desktop: **Get Data > Text/CSV > `outputs/powerbi_customers.csv` > Load.**
Import theme: **View > Themes > Browse for themes > `powerbi-theme.json`**.

---

## Page 1 — Executive Churn Command Centre (rename page to `Executive`)

Top row — 4 Card visuals:
1. `Total Customers`  2. `Churn Rate %`  3. `Revenue at Risk` (Format: Currency, 0 decimals)  4. `Persuadables Count`

Charts:
- **Clustered bar:** Axis `Contract`, Values `Churn Rate %` — sort descending. *Story: month-to-month churns ~14x more than 2-year.*
- **Clustered bar:** Axis `InternetService`, Values `Churn Rate %`
- **Donut:** Legend `risk_band`, Values `Total Customers`
- **Line:** Axis `tenure_group`, Values `Churn Rate %`. *Story: danger is in the first year.*
- **Stacked bar:** Axis `segment`, Values `Revenue at Risk`

Slicers (top or left rail): `Contract`, `InternetService`, `segment`

First create all measures from `DAX_measures.dax` before building cards.

## Page 2 — Rescue List

- **Table visual** (this is the deliverable a retention team actually uses):
  Columns in order: `customerID`, `segment`, `churn_probability` (%), `risk_window`, `top_reason`, `recommended_action`, `clv_at_risk`, `net_save_value`
- Filter the table (Visual-level filter): `segment` = Persuadables only
- Sort: `net_save_value` descending. Conditional formatting: data bars on `clv_at_risk`, colour scale on `churn_probability` (green→red)
- Add a Card above it: `Persuadable Revenue at Risk`
- Slicers: `risk_window`, `Contract`, `top_reason`

**Screenshot this page for LinkedIn / your portfolio.** It's the most original page.

## Page 3 — Retention ROI Simulator ★

1. **Modelling > New Parameter > What If:** Name `DiscountPct`, 0–30, increment 1, default 10 → OK (adds a slider automatically)
2. Repeat: Name `SaveRatePct`, 5–60, increment 5, default 25
3. Add measures from the ROI section of `DAX_measures.dax`
4. Cards: `Intervention Cost`, `Revenue Saved`, `Net ROI`, `ROI %`
5. Big comparison bar: `Intervention Cost` vs `Cost If You Target EVERYONE`, and a Card: `Money Wasted on Non-Persuadables`
6. Text box (Insert > Text box): *"We only offer discounts to Persuadables. Sure Things stay anyway, Lost Causes leave anyway, Sleeping Dogs get annoyed. Targeting everyone costs more and saves less."*

Demo script: drag DiscountPct from 10% → 25% and watch Net ROI fall. That 10-second demo wins interviews.

## Publish / Show Off
- File > Publish to Power BI service (optional), or just export each page as PNG for GitHub README + LinkedIn.
- In GitHub README, put Page 2 screenshot first — not Page 1. Everyone shows KPI dashboards; nobody shows an action list.
