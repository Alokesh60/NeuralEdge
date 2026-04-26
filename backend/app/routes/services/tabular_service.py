import uuid
import pandas as pd
import numpy as np
import os, tempfile, shutil
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# -------------------- In-memory model store (replaces disk models/) --------------------
# Render's filesystem is ephemeral — never write model artifacts to disk between
# train and inference within the same request. Store them in memory instead.
_model_store: dict = {}


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
        if col in numerical:
            numerical.remove(col)
        if col in categorical:
            categorical.remove(col)

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

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    pipe.fit(Xtr, ytr)
    pred = pipe.predict(Xte)

    # FIX: return everything in memory instead of writing to disk.
    # Render's filesystem resets on every deploy/restart, so models/ would be lost.
    artifacts = {
        "pipe": pipe,
        "X_test": Xte,
        "y_test": yte,
        "y_pred": pred,
    }

    return accuracy_score(yte, pred), artifacts


# -------------------- Lightweight Fairness --------------------
def compute_metrics(X, y, pred, sensitive_col, privileged_value):
    df = X.copy()
    df["y_true"] = y
    df["y_pred"] = pred

    groups = df.groupby(sensitive_col)

    rates = {}
    for g, data in groups:
        positive_rate = data["y_pred"].mean()
        rates[g] = positive_rate

    priv_rate = rates.get(privileged_value, 0)
    unpriv_rates = [v for k, v in rates.items() if k != privileged_value]

    if not unpriv_rates:
        di = 1.0
    else:
        di = min(unpriv_rates) / (priv_rate + 1e-6)

    return {
        "disparate_impact": round(di, 4),
        "verdict": "FAIL" if di < 0.8 else "PASS",
        "group_rates": rates
    }


# -------------------- SHAP (Optimized) --------------------
def explain_shap(model, X, preprocessor, sample_size=100):
    import shap
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression

    if len(X) > sample_size:
        X = X.sample(sample_size, random_state=42)

    X_processed = preprocessor.transform(X)

    if isinstance(model, RandomForestClassifier):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_processed)
        values = shap_values[1] if isinstance(shap_values, list) else shap_values

    elif isinstance(model, LogisticRegression):
        explainer = shap.LinearExplainer(model, X_processed)
        values = explainer(X_processed).values

    else:
        raise ValueError("Unsupported model for SHAP")

    importance = np.abs(values).mean(axis=0)

    return sorted(
        [{"feature": f, "importance": float(i)}
         for f, i in zip(preprocessor.get_feature_names_out(), importance)],
        key=lambda x: x["importance"],
        reverse=True
    )[:10]


# -------------------- MAIN --------------------
async def run_tabular_audit(
    file,
    target_col,
    sensitive_cols,
    privileged_groups,
    model_choice="logistic",
    model_file=None,        # kept for API compatibility with /flexible endpoint
    preprocessor_file=None, # kept for API compatibility with /flexible endpoint
    shap_sample_size=100
):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        path = tmp.name

    try:
        df = load_and_profile(path, target_col)

        num, cat = infer_schema(df, target_col, sensitive_cols)

        # FIX: train_model now returns artifacts dict instead of writing to disk
        acc, artifacts = train_model(
            df, target_col, sensitive_cols, num, cat, model_choice
        )

        pipe      = artifacts["pipe"]
        X_test    = artifacts["X_test"]
        y_test    = artifacts["y_test"]
        y_pred    = artifacts["y_pred"]

        model = pipe.named_steps["model"]
        pre   = pipe.named_steps["preprocessor"]

        # Fairness
        sensitive_col    = sensitive_cols[0]
        privileged_value = privileged_groups[sensitive_col]

        metrics = compute_metrics(
            X_test, y_test, y_pred,
            sensitive_col, privileged_value
        )

        # SHAP
        top_features = explain_shap(
            model, X_test, pre, shap_sample_size
        )

    finally:
        os.unlink(path)

    return sanitize_for_json({
        "request_id": str(uuid.uuid4()),
        "accuracy": round(acc, 4),
        "metrics": metrics,
        "top_features": top_features,
        "status": "success"
    })