import uuid
import pandas as pd
import numpy as np
import os, tempfile, shutil, json
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
from typing import Optional, Dict, Any, List, Tuple

# -------------------- JSON Safety --------------------
def sanitize_for_json(obj):
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(i) for i in obj]
    else:
        return obj

# -------------------- Schema --------------------
def infer_schema(df, target_col, sensitive_cols):
    numerical = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical = df.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in [target_col] + sensitive_cols:
        if col in numerical: numerical.remove(col)
        if col in categorical: categorical.remove(col)
    return numerical, categorical

def get_model_by_name(name):
    if name == "randomforest":
        return RandomForestClassifier(n_estimators=100)
    return LogisticRegression(max_iter=1000)

# -------------------- Load --------------------
def load_and_profile(path, target):
    df = pd.read_csv(path)
    df.dropna(subset=[target], inplace=True)

    if df[target].dtype == "object":
        df[target] = LabelEncoder().fit_transform(df[target])

    print(f"[tabular] rows={len(df)}, positive_rate={df[target].mean():.2%}")
    return df

# -------------------- Training --------------------
def train_model(df, target, sensitive, num, cat, model_choice):
    X = df.drop(columns=[target])
    y = df[target]

    pre = ColumnTransformer([
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat)
    ])

    model = get_model_by_name(model_choice)

    pipe = Pipeline([
        ("preprocessor", pre),
        ("model", model)
    ])

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y)

    pipe.fit(Xtr, ytr)
    pred = pipe.predict(Xte)

    joblib.dump({"X_test": Xte, "y_test": yte, "y_pred": pred}, "models/test.pkl")
    joblib.dump(pipe, "models/model.pkl")

    return accuracy_score(yte, pred), Xte, yte, pred

# -------------------- Fairness --------------------
def compute_metrics(target, sensitive, privileged):
    from aif360.datasets import BinaryLabelDataset
    from aif360.metrics import ClassificationMetric

    data = joblib.load("models/test.pkl")
    X = data["X_test"]
    y = data["y_test"]
    pred = data["y_pred"]

    sens = sensitive[0]
    le = LabelEncoder()
    X[sens] = le.fit_transform(X[sens])

    priv = le.transform([privileged[sens]])[0]
    unpriv = 1 - priv

    df = pd.DataFrame({sens: X[sens], target: y})

    actual = BinaryLabelDataset(
        df=df,
        label_names=[target],
        protected_attribute_names=[sens],
        privileged_protected_attributes=[[priv]]
    )

    pred_ds = actual.copy()
    pred_ds.labels = pred.reshape(-1, 1)

    metric = ClassificationMetric(
        actual, pred_ds,
        unprivileged_groups=[{sens: unpriv}],
        privileged_groups=[{sens: priv}]
    )

    di = metric.disparate_impact()

    return {
        "disparate_impact": round(di, 4),
        "verdict": "FAIL" if di < 0.8 else "PASS"
    }

# -------------------- SHAP --------------------
def explain_shap(sample_size=None):
    import shap

    pipe = joblib.load("models/model.pkl")
    data = joblib.load("models/test.pkl")

    X = data["X_test"]

    if sample_size and len(X) > sample_size:
        X = X.sample(sample_size)

    pre = pipe.named_steps["preprocessor"]
    model = pipe.named_steps["model"]

    Xp = pre.transform(X)

    explainer = shap.Explainer(model, Xp)
    values = explainer(Xp)

    importance = np.abs(values.values).mean(axis=0)

    return {
        "top_features": sorted(
            [{"feature": f, "importance": float(i)} for f, i in zip(pre.get_feature_names_out(), importance)],
            key=lambda x: x["importance"],
            reverse=True
        )[:10]
    }

# -------------------- MAIN --------------------
async def run_tabular_audit(
    file,
    target_col,
    sensitive_cols,
    privileged_groups,
    model_choice="logistic",
    shap_sample_size=None
):

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        path = tmp.name

    try:
        df = load_and_profile(path, target_col)

        num, cat = infer_schema(df, target_col, sensitive_cols)

        acc, Xte, yte, pred = train_model(
            df, target_col, sensitive_cols, num, cat, model_choice
        )

        metrics = compute_metrics(target_col, sensitive_cols, privileged_groups)

        shap_res = explain_shap(shap_sample_size)

    finally:
        os.unlink(path)

    return sanitize_for_json({
        "request_id": str(uuid.uuid4()),
        "accuracy": round(acc, 4),
        "metrics": metrics,
        "top_features": shap_res["top_features"],
        "status": "success"
    })
