"""Train churn models, compare LogReg vs RandomForest, save best + metrics.json"""
import json, pathlib
import pandas as pd, numpy as np, joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, accuracy_score

ROOT = pathlib.Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT/"data/Telco-Customer-Churn.csv")
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["ChurnFlag"] = (df["Churn"]=="Yes").astype(int)

FEATURES = ["gender","SeniorCitizen","Partner","Dependents","tenure","PhoneService","MultipleLines",
 "InternetService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV",
 "StreamingMovies","Contract","PaperlessBilling","PaymentMethod","MonthlyCharges","TotalCharges"]
NUM = ["SeniorCitizen","tenure","MonthlyCharges","TotalCharges"]
CAT = [c for c in FEATURES if c not in NUM]

pre = ColumnTransformer([
    ("num", Pipeline([("imp",SimpleImputer(strategy="median")),("sc",StandardScaler())]), NUM),
    ("cat", Pipeline([("imp",SimpleImputer(strategy="most_frequent")),("oh",OneHotEncoder(handle_unknown="ignore"))]), CAT),
])
X,y = df[FEATURES], df["ChurnFlag"]
Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)

results={}
models={"logistic_regression":LogisticRegression(max_iter=1000,class_weight="balanced"),
        "random_forest":RandomForestClassifier(n_estimators=300,random_state=42,class_weight="balanced_subsample",n_jobs=-1)}
best_name,best_f1,best_pipe=None,-1,None
for name,clf in models.items():
    pipe=Pipeline([("pre",pre),("clf",clf)]); pipe.fit(Xtr,ytr)
    p=pipe.predict(Xte); prob=pipe.predict_proba(Xte)[:,1]
    m={"accuracy":round(accuracy_score(yte,p),3),"precision":round(precision_score(yte,p),3),
       "recall":round(recall_score(yte,p),3),"f1":round(f1_score(yte,p),3),
       "roc_auc":round(roc_auc_score(yte,prob),3),"pr_auc":round(average_precision_score(yte,prob),3)}
    results[name]=m; print(name,m)
    if m["f1"]>best_f1: best_f1,best_name,best_pipe=m["f1"],name,pipe

(ROOT/"outputs").mkdir(exist_ok=True)
joblib.dump(best_pipe, ROOT/"outputs/churn_model.joblib")
metrics={"dataset_rows":int(len(df)),"churn_rate_pct":round(float(y.mean()*100),2),
         "best_model":best_name,"models":results,"test_size":len(yte)}
(ROOT/"outputs/metrics.json").write_text(json.dumps(metrics,indent=2))
print("BEST:",best_name); print(json.dumps(metrics,indent=2))
