"""The unique layer: WHY + WHEN + SEGMENT + ACTION + CLV-at-risk, exported for Power BI."""
import pathlib, pandas as pd, numpy as np, joblib
ROOT = pathlib.Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT/"data/Telco-Customer-Churn.csv")
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
FEATURES = ["gender","SeniorCitizen","Partner","Dependents","tenure","PhoneService","MultipleLines",
 "InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV",
 "StreamingMovies","Contract","PaperlessBilling","PaymentMethod","MonthlyCharges","TotalCharges"]
model = joblib.load(ROOT/"outputs/churn_model.joblib")
df["churn_probability"] = np.round(model.predict_proba(df[FEATURES])[:,1],3)

def reason(r):
    if r.Contract=="Month-to-month": return "Month-to-month contract (no lock-in)"
    if r.InternetService=="Fiber optic" and r.MonthlyCharges>85: return "High fiber bill — price pain"
    if r.TechSupport=="No" and r.InternetService!="No": return "No tech support when issues hit"
    if r.tenure<=6: return "New customer — never built a habit"
    if r.PaymentMethod=="Electronic check": return "Electronic check — manual payment friction"
    if r.OnlineSecurity=="No" and r.InternetService!="No": return "No online security add-on (low stickiness)"
    if r.PaperlessBilling=="Yes" and r.MonthlyCharges>90: return "High monthly charges"
    return "Low engagement / low stickiness"

def risk_window(r):
    if r.churn_probability>=0.7 and r.tenure<=12: return "Critical — next 30 days"
    if r.churn_probability>=0.5: return "Near — 1 to 3 months"
    if r.churn_probability>=0.3: return "Watch — 3 to 6 months"
    return "Distant — 6+ months"

def segment(r):
    # Explainable proxy-uplift logic (see INTERVIEW_NOTES.md for honesty note)
    price_sens = (r.MonthlyCharges>70) + (r.Contract=="Month-to-month") + (r.PaymentMethod=="Electronic check")
    loyalty = (r.tenure>24) + (r.Contract!="Month-to-month") + (r.TechSupport=="Yes")
    p=r.churn_probability
    if p>=0.80: return "Lost Causes"                      # too far gone — a discount rarely reverses this
    if p>=0.40 and price_sens>=1: return "Persuadables"    # at risk AND a price/offer lever exists
    if p>=0.40: return "Lost Causes"                       # at risk but no price lever — product/exit issue
    if loyalty>=2: return "Sure Things"                    # low risk + loyal signals
    return "Sleeping Dogs"                                 # low risk but not loyal — don't poke them with promos

ACTIONS={"Persuadables":"Offer 15% off x 3 months + free Tech Support trial",
 "Sure Things":"No discount — thank-you note + loyalty points",
 "Lost Causes":"Exit survey only — do not spend retention budget",
 "Sleeping Dogs":"Leave alone — no promo contact (risk of waking them up)"}
EXPECTED_MONTHS={"Month-to-month":8,"One year":14,"Two year":22}

df["top_reason"]=df.apply(reason,axis=1)
df["risk_window"]=df.apply(risk_window,axis=1)
df["risk_band"]=pd.cut(df.churn_probability,[0,.3,.6,1.01],labels=["Low","Medium","High"])
df["segment"]=df.apply(segment,axis=1)
df["recommended_action"]=df.segment.map(ACTIONS)
df["expected_remaining_months"]=df.Contract.map(EXPECTED_MONTHS)
df["clv_at_risk"]=np.round(df.MonthlyCharges*df.expected_remaining_months*df.churn_probability,2)
df["offer_cost"]=np.where(df.segment=="Persuadables", np.round(df.MonthlyCharges*0.15*3,2), 0)
df["net_save_value"]=np.round(np.where(df.segment=="Persuadables", df.clv_at_risk*0.25 - df.offer_cost, 0),2)
df["tenure_group"]=pd.cut(df.tenure,[-1,6,12,24,48,100],labels=["0-6 mo","7-12 mo","1-2 yr","2-4 yr","4+ yr"])
df["ChurnFlag"]=(df.Churn=="Yes").astype(int)

out=df[["customerID","gender","SeniorCitizen","Partner","Dependents","tenure","tenure_group","Contract",
 "InternetService","TechSupport","OnlineSecurity","PaymentMethod","PaperlessBilling","MonthlyCharges","TotalCharges",
 "Churn","ChurnFlag","churn_probability","risk_band","risk_window","top_reason","segment","recommended_action",
 "expected_remaining_months","clv_at_risk","offer_cost","net_save_value"]]
out.to_csv(ROOT/"outputs/powerbi_customers.csv",index=False)
out.groupby("segment").agg(customers=("customerID","count"),revenue_at_risk=("clv_at_risk","sum"),
  avg_prob=("churn_probability","mean")).round(2).reset_index().to_csv(ROOT/"outputs/powerbi_summary_by_segment.csv",index=False)
out.groupby("top_reason").agg(customers=("customerID","count"),revenue_at_risk=("clv_at_risk","sum")).round(2).reset_index().sort_values("customers",ascending=False).to_csv(ROOT/"outputs/powerbi_summary_by_reason.csv",index=False)
print(out.segment.value_counts()); print("Revenue at risk: $",round(out.clv_at_risk.sum()))
print("Persuadable net save value: $",round(out[out.segment=='Persuadables'].net_save_value.sum()))
print("Saved outputs/powerbi_customers.csv rows:",len(out))
