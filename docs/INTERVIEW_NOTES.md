# Interview Notes — How to Talk About Churn Rescue OS

## 2-minute pitch (memorise the structure, not the words)

"Most churn projects stop at a probability. I asked what a retention team does on Monday morning. So I built three layers on top of the model: one, a reason code for every customer, so a manager knows *why*; two, a risk window, so they know *when* to act; and three, a segmentation based on uplift thinking — Persuadables, Sure Things, Lost Causes, Sleeping Dogs — because giving a discount to someone who would stay anyway is just burning margin. Each customer gets a CLV-at-risk and a net save value. Then in Power BI, the third page is a What-If simulator: change the discount percentage and it shows whether the retention campaign actually makes money. That last part is what turned it from a model into a decision tool."

## Traps & honest answers

**"Is your segmentation a real uplift model?"**
"No — it's a proxy using probability, price sensitivity and loyalty signals. A true uplift model needs randomised treatment/control data from a real campaign. I built the proxy to demonstrate the framework, and I'd validate it with an A/B test in production." *(This answer impresses more than faking it.)*

**"Why Logistic Regression / Random Forest and not XGBoost?"**
"I compared them on PR-AUC and F1, not just accuracy, because churn is imbalanced (~27%). I kept the simpler model if it was close, because the reason codes need to be explainable." *(Check your metrics.json before the interview and adjust this answer to the actual winner.)*

**"Accuracy is only ~80%, is that bad?"**
"Accuracy is the wrong metric here. A model that catches 70% of churners in the Persuadable segment, ranked by net save value, makes more money than a 90%-accurate model with no action layer."

**"How is CLV calculated?"**
"MonthlyCharges × expected remaining months, where expected months depends on contract type. It's an estimate — a production version would use survival analysis."

**"What would you do with more data?"**
"Add usage/behaviour events and support-ticket sentiment, run a real uplift model on campaign data, and add survival analysis for the risk window instead of a rule-based window."

## Numbers to know cold (from YOUR outputs/metrics.json)
Dataset size, churn rate, your model's Precision / Recall / F1 / PR-AUC, total Revenue at Risk, Persuadables count, and the Money Wasted on Non-Persuadables figure from Page 3. Write them here after your run: _______________
