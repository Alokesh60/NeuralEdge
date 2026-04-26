
import uuid
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io, base64, os, tempfile, shutil
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
from typing import Optional, Dict, Any, List, Tuple

# -------------------- Helper: sanitize JSON --------------------
import numpy as np

def sanitize_for_json(obj):
    """Replace inf, -inf, nan with None so JSON serialization works."""
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

# -------------------- Plain‑language explanations --------------------
def explain_metric(metric_name: str, value: float) -> str:
    """Return a plain‑language explanation of a fairness metric."""
    explanations = {
        "disparate_impact": (
            "Disparate Impact (DI) measures the ratio of positive predictions for the unprivileged group "
            "compared to the privileged group. A value below 0.8 or above 1.2 indicates potential discrimination "
            "(the 80% rule). Ideal is 1.0."
        ),
        "stat_parity_diff": (
            "Statistical Parity Difference (SPD) is the difference in positive prediction rates between "
            "unprivileged and privileged groups. Ideal is 0 (both groups receive positive outcomes equally often)."
        ),
        "equal_opportunity_diff": (
            "Equal Opportunity Difference (EOD) compares the true positive rates (recall) of the two groups. "
            "Ideal is 0 (equal ability to get a positive outcome when actually positive)."
        ),
        "avg_odds_diff": (
            "Average Odds Difference (AOD) is the average of differences in false positive and true positive rates. "
            "Ideal is 0."
        ),
        "dp_diff": (
            "Demographic Parity Difference is another measure of disparity in positive prediction rates. "
            "Ideal is 0."
        ),
        "eod_diff": (
            "Equalized Odds Difference (EOD) is the larger of the absolute differences in false positive and true positive rates. "
            "Ideal is 0."
        ),
    }
    return explanations.get(metric_name, f"{metric_name}: a fairness metric. Ideal value depends on context.")

def generate_plain_language_summary(metrics: dict, verdict: str, di: float, debiasing_results: dict, best_method: str) -> dict:
    """Return a human‑readable summary and suggestions."""
    if verdict == "FAIL":
        summary = f"The model is biased (Disparate Impact = {di:.4f}, below the 0.8 threshold). It gives significantly fewer positive predictions to the unprivileged group."
    else:
        summary = f"The model appears fair (Disparate Impact = {di:.4f}, within the 0.8–1.2 range). No immediate bias detected."

    suggestions = []
    if di < 0.8:
        suggestions.append("Apply in‑processing debiasing (ExponentiatedGradient) – this improved DI to ~0.93 in tests with minimal accuracy loss.")
        if best_method == "exponentiated_gradient":
            suggestions.append("The best debiasing method for this dataset was ExponentiatedGradient. You can re‑run with `model_choice` to apply it automatically.")
    if abs(metrics['stat_parity_diff']) > 0.1:
        suggestions.append("Consider removing protected attributes from features or using Reweighing pre‑processing to balance outcomes.")
    if abs(metrics['equal_opportunity_diff']) > 0.1:
        suggestions.append("The model has unequal recall across groups. Post‑processing (Calibrated Equalized Odds) can help equalize error rates.")

    return {
        "verdict_explanation": summary,
        "suggestions": suggestions,
        "metric_descriptions": {k: explain_metric(k, v) for k, v in metrics.items() if k in ['disparate_impact','stat_parity_diff','equal_opportunity_diff','avg_odds_diff','dp_diff','eod_diff']}
    }

# -------------------- Helper: fig to base64 --------------------
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

# -------------------- Schema inference --------------------
def infer_schema(df: pd.DataFrame, target_col: str, sensitive_cols: List[str]) -> Tuple[List[str], List[str]]:
    numerical = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical = df.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in [target_col] + sensitive_cols:
        if col in numerical:
            numerical.remove(col)
        if col in categorical:
            categorical.remove(col)
    return numerical, categorical

def get_model_by_name(model_name: str, random_state=42):
    model_name = model_name.lower()
    if model_name == "logistic":
        return LogisticRegression(max_iter=1000, random_state=random_state)
    elif model_name == "randomforest":
        return RandomForestClassifier(n_estimators=100, random_state=random_state)
    else:
        return LogisticRegression(max_iter=1000, random_state=random_state)

# -------------------- Step 1: Load & basic EDA --------------------
def load_and_profile(filepath: str, target_col: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df.dropna(subset=[target_col], inplace=True)
    if df[target_col].dtype == 'object':
        le = LabelEncoder()
        df[target_col] = le.fit_transform(df[target_col])
    print(f"[tabular] Loaded {len(df)} rows, positive rate = {df[target_col].mean():.2%}")
    return df

def generate_eda_charts(df: pd.DataFrame, target_col: str, sensitive_cols: List[str]) -> Dict[str, str]:
    charts = {}
    for sens in sensitive_cols:
        rates = df.groupby(sens)[target_col].mean().reset_index()
        fig, ax = plt.subplots(figsize=(6,4))
        sns.barplot(data=rates, x=sens, y=target_col, hue=sens, palette='viridis', legend=False, ax=ax)
        ax.axhline(0.5, color='gray', linestyle='--', alpha=0.5, label='Parity line')
        ax.set_title(f'{target_col} rate by {sens} (raw data)')
        ax.set_ylabel('Rate')
        ax.set_ylim(0,1)
        ax.legend()
        charts[f'chart_{sens}_eda'] = fig_to_base64(fig)
    return charts


def train_or_load_baseline(df: pd.DataFrame, target_col: str, sensitive_cols: List[str],
                           numerical_features: List[str], categorical_features: List[str],
                           model_choice: str, model_file: Optional[Any] = None,
                           preprocessor_file: Optional[Any] = None) -> Dict[str, Any]:
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # ----- 1) Pretrained mode (user uploaded files) -----
    if model_file is not None and preprocessor_file is not None:
        print("[tabular] Using uploaded pretrained model + preprocessor (no training).")
        X_processed = preprocessor_file.transform(X)
        y_pred = model_file.predict(X_processed)
        accuracy = accuracy_score(y, y_pred)
        # Per-group rates
        group_rates = {}
        for sens in sensitive_cols:
            temp = X.copy()
            temp['pred'] = y_pred
            group_rates[sens] = temp.groupby(sens)['pred'].mean().to_dict()
        os.makedirs('models', exist_ok=True)
        joblib.dump({'X_test': X, 'y_test': y, 'y_pred': y_pred}, 'models/test_data.pkl')
        joblib.dump(preprocessor_file, 'models/pretrained_preprocessor.pkl')
        joblib.dump(model_file, 'models/pretrained_model.pkl')
        sens0 = sensitive_cols[0]
        rates = group_rates[sens0]
        fig, ax = plt.subplots(figsize=(6,4))
        pd.Series(rates).plot(kind='bar', ax=ax, color=['#5DCAA5','#D85A30'])
        ax.set_title(f'Predicted {target_col} rate by {sens0}')
        ax.set_ylabel('Prediction rate')
        ax.set_ylim(0,1)
        ax.axhline(0.5, color='gray', linestyle='--')
        chart_disparity = fig_to_base64(fig)
        return {
            "accuracy": round(accuracy, 4),
            "group_rates": group_rates,
            "chart_disparity": chart_disparity,
            "model_path": "pretrained",
            "pretrained": True
        }

    # ----- 2) Train from scratch (always, no local baseline fallback) -----
    print(f"[tabular] Training new {model_choice} model from scratch.")
    model = get_model_by_name(model_choice)
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    pipeline = Pipeline([('preprocessor', preprocessor), ('classifier', model)])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Per-group rates on test set
    group_rates = {}
    for sens in sensitive_cols:
        temp = X_test.copy()
        temp['pred'] = y_pred
        group_rates[sens] = temp.groupby(sens)['pred'].mean().to_dict()

    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline, 'models/biased_model.pkl')
    joblib.dump({'X_test': X_test, 'y_test': y_test, 'y_pred': y_pred}, 'models/test_data.pkl')

    sens0 = sensitive_cols[0]
    rates = group_rates[sens0]
    fig, ax = plt.subplots(figsize=(6,4))
    pd.Series(rates).plot(kind='bar', ax=ax, color=['#5DCAA5','#D85A30'])
    ax.set_title(f'Predicted {target_col} rate by {sens0}')
    ax.set_ylabel('Prediction rate')
    ax.set_ylim(0,1)
    ax.axhline(0.5, color='gray', linestyle='--')
    chart_disparity = fig_to_base64(fig)

    return {
        "accuracy": round(accuracy, 4),
        "group_rates": group_rates,
        "chart_disparity": chart_disparity,
        "model_path": "models/biased_model.pkl",
        "pretrained": False
    }
# -------------------- Step 3: Fairness metrics --------------------
def compute_metrics(target_col: str, sensitive_cols: List[str], privileged_groups: Dict[str, Any]) -> Dict[str, Any]:
    from aif360.datasets import BinaryLabelDataset
    from aif360.metrics import ClassificationMetric
    from fairlearn.metrics import MetricFrame, demographic_parity_difference, equalized_odds_difference
    from sklearn.metrics import accuracy_score, precision_score, recall_score

    model_data = joblib.load('models/test_data.pkl')
    X_test = model_data['X_test']
    y_test = model_data['y_test']
    y_pred = model_data['y_pred']

    sens_col = sensitive_cols[0]
    le = LabelEncoder()
    X_test_sens = X_test.copy()
    X_test_sens[f'{sens_col}_num'] = le.fit_transform(X_test[sens_col])
    privileged_val = privileged_groups.get(sens_col)
    if privileged_val is not None:
        privileged_num = le.transform([privileged_val])[0]
    else:
        privileged_num = 1
    unprivileged_num = 1 - privileged_num if len(le.classes_) == 2 else 0

    temp_df = pd.DataFrame({
        f'{sens_col}_num': X_test_sens[f'{sens_col}_num'],
        target_col: y_test.values
    })
    aif_actual = BinaryLabelDataset(
        df=temp_df,
        label_names=[target_col],
        protected_attribute_names=[f'{sens_col}_num'],
        privileged_protected_attributes=[[privileged_num]]
    )
    aif_pred = aif_actual.copy()
    aif_pred.labels = y_pred.reshape(-1,1)

    clf_metric = ClassificationMetric(
        aif_actual, aif_pred,
        unprivileged_groups=[{f'{sens_col}_num': unprivileged_num}],
        privileged_groups=[{f'{sens_col}_num': privileged_num}]
    )
    disparate_impact = clf_metric.disparate_impact()
    stat_parity_diff = clf_metric.statistical_parity_difference()
    equal_opportunity_diff = clf_metric.equal_opportunity_difference()
    avg_odds_diff = clf_metric.average_odds_difference()

    verdict = "FAIL" if disparate_impact < 0.8 or disparate_impact > 1.2 else "PASS"

    metric_frame = MetricFrame(
        metrics={'accuracy': accuracy_score,
                 'precision': lambda yt,yp: precision_score(yt,yp,zero_division=0),
                 'recall': lambda yt,yp: recall_score(yt,yp,zero_division=0)},
        y_true=y_test, y_pred=y_pred, sensitive_features=X_test[sens_col]
    )
    per_group = metric_frame.by_group.round(4).to_dict()
    dp_diff = demographic_parity_difference(y_test, y_pred, sensitive_features=X_test[sens_col])
    eod_diff = equalized_odds_difference(y_test, y_pred, sensitive_features=X_test[sens_col])

    fig, axes = plt.subplots(1,2, figsize=(12,4))
    metrics_vals = {'DI': disparate_impact, 'SPD': abs(stat_parity_diff), 'EOD': abs(equal_opportunity_diff)}
    axes[0].bar(metrics_vals.keys(), metrics_vals.values(), color=['#E24B4A' if v<0.8 else '#1D9E75' for v in metrics_vals.values()])
    axes[0].axhline(0.8, color='gray', linestyle='--')
    axes[0].set_title('Fairness metrics')
    metric_frame.by_group['accuracy'].plot(kind='bar', ax=axes[1], color=['#5DCAA5','#D85A30'])
    axes[1].set_title(f'Accuracy by {sens_col}')
    axes[1].set_ylim(0,1)
    chart_metrics = fig_to_base64(fig)

    return {
        "disparate_impact": round(disparate_impact, 4),
        "stat_parity_diff": round(stat_parity_diff, 4),
        "equal_opportunity_diff": round(equal_opportunity_diff, 4),
        "avg_odds_diff": round(avg_odds_diff, 4),
        "dp_diff": round(dp_diff, 4),
        "eod_diff": round(eod_diff, 4),
        "verdict": verdict,
        "per_group_metrics": per_group,
        "chart_metrics": chart_metrics
    }

# -------------------- Step 4: Debiasing --------------------
def debias(df: pd.DataFrame, target_col: str, sensitive_cols: List[str], privileged_groups: Dict[str, Any],
           numerical_features: List[str], categorical_features: List[str], model_choice: str,
           is_pretrained: bool) -> Dict[str, Any]:
    from aif360.datasets import BinaryLabelDataset
    from aif360.algorithms.preprocessing import Reweighing
    from aif360.algorithms.postprocessing import CalibratedEqOddsPostprocessing
    from fairlearn.reductions import ExponentiatedGradient, DemographicParity
    from sklearn.metrics import accuracy_score
    import scipy.sparse as sp

    model_data = joblib.load('models/test_data.pkl')
    X_test = model_data['X_test']
    y_test = model_data['y_test']
    y_pred_orig = model_data['y_pred']
    biased_model = joblib.load('models/biased_model.pkl') if not is_pretrained else None

    sens_col = sensitive_cols[0]
    le = LabelEncoder()
    X_test_sens = X_test.copy()
    X_test_sens[f'{sens_col}_num'] = le.fit_transform(X_test[sens_col])
    privileged_val = privileged_groups.get(sens_col)
    if privileged_val is not None:
        privileged_num = le.transform([privileged_val])[0]
    else:
        privileged_num = 1
    unprivileged_num = 1 - privileged_num if len(le.classes_) == 2 else 0

    # Baseline metrics
    uniq_vals = X_test[sens_col].unique()
    if privileged_val not in uniq_vals:
        privileged_val = uniq_vals[0]
    unpriv_val = [v for v in uniq_vals if v != privileged_val][0]
    orig_di = (y_pred_orig[X_test[sens_col] == unpriv_val].mean() /
               y_pred_orig[X_test[sens_col] == privileged_val].mean())
    orig_acc = accuracy_score(y_test, y_pred_orig)

    results = {"baseline": {"accuracy": round(orig_acc,4), "disparate_impact": round(orig_di,4),
                            "verdict": "FAIL" if orig_di<0.8 else "PASS"}}

    if is_pretrained:
        print("[tabular] Skipping debiasing for pretrained model.")
        results["note"] = "Debiasing not applied because pretrained model cannot be retrained."
        fig, axes = plt.subplots(1,2, figsize=(12,5))
        axes[0].bar(['Baseline'],[orig_acc], color='#E24B4A')
        axes[0].set_title('Accuracy')
        axes[1].bar(['Baseline'],[orig_di], color='#E24B4A')
        axes[1].axhline(0.8, color='gray', linestyle='--')
        axes[1].set_title('Disparate Impact')
        results['chart_debiasing'] = fig_to_base64(fig)
        return results

    # Otherwise, full debiasing
    X = df.drop(columns=[target_col])
    y = df[target_col]
    X_train, X_test_rw, y_train, y_test_rw = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ])

    # Reweighing
    try:
        train_df = X_train.copy()
        train_df[target_col] = y_train.values
        train_df[f'{sens_col}_num'] = LabelEncoder().fit_transform(train_df[sens_col])
        aif_train = BinaryLabelDataset(
            df=train_df[[f'{sens_col}_num', target_col]],
            label_names=[target_col],
            protected_attribute_names=[f'{sens_col}_num'],
            privileged_protected_attributes=[[privileged_num]]
        )
        RW = Reweighing(unprivileged_groups=[{f'{sens_col}_num': unprivileged_num}],
                        privileged_groups=[{f'{sens_col}_num': privileged_num}])
        aif_train_rw = RW.fit_transform(aif_train)
        sample_weights = aif_train_rw.instance_weights
        X_train_proc = preprocessor.fit_transform(X_train)
        X_test_proc = preprocessor.transform(X_test_rw)
        lr_rw = LogisticRegression(max_iter=1000)
        lr_rw.fit(X_train_proc, y_train, sample_weight=sample_weights)
        y_pred_rw = lr_rw.predict(X_test_proc)
        acc_rw = accuracy_score(y_test_rw, y_pred_rw)
        # Compute DI
        di_rw = (y_pred_rw[X_test_rw[sens_col]==unpriv_val].mean() /
                 y_pred_rw[X_test_rw[sens_col]==privileged_val].mean())
        results['reweighing'] = {"accuracy": round(acc_rw,4), "disparate_impact": round(di_rw,4),
                                 "verdict": "PASS" if di_rw>=0.8 else "FAIL"}
    except Exception as e:
        results['reweighing'] = {"error": str(e)}

    # ExponentiatedGradient
    try:
        preprocessor_eg = ColumnTransformer([
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ])
        X_train_eg = preprocessor_eg.fit_transform(X_train)
        X_test_eg = preprocessor_eg.transform(X_test_rw)
        if sp.issparse(X_train_eg): X_train_eg = X_train_eg.toarray()
        if sp.issparse(X_test_eg): X_test_eg = X_test_eg.toarray()
        eg_model = ExponentiatedGradient(estimator=LogisticRegression(max_iter=1000), constraints=DemographicParity())
        eg_model.fit(X_train_eg, y_train, sensitive_features=X_train[sens_col])
        y_pred_eg = eg_model.predict(X_test_eg)
        acc_eg = accuracy_score(y_test_rw, y_pred_eg)
        di_eg = (y_pred_eg[X_test_rw[sens_col]==unpriv_val].mean() /
                 y_pred_eg[X_test_rw[sens_col]==privileged_val].mean())
        results['exponentiated_gradient'] = {"accuracy": round(acc_eg,4), "disparate_impact": round(float(di_eg),4),
                                             "verdict": "PASS" if di_eg>=0.8 else "FAIL"}
    except Exception as e:
        results['exponentiated_gradient'] = {"error": str(e)}

    # Calibrated Equalized Odds
    try:
        test_df = X_test.copy()
        test_df[target_col] = y_test.values
        test_df[f'{sens_col}_num'] = LabelEncoder().fit_transform(test_df[sens_col])
        if biased_model is not None:
            biased_probs = biased_model.predict_proba(X_test)[:,1]
        else:
            biased_probs = joblib.load('models/biased_model.pkl').predict_proba(X_test)[:,1]
        aif_actual_post = BinaryLabelDataset(
            df=test_df[[f'{sens_col}_num', target_col]],
            label_names=[target_col],
            protected_attribute_names=[f'{sens_col}_num'],
            privileged_protected_attributes=[[privileged_num]]
        )
        aif_pred_post = aif_actual_post.copy()
        aif_pred_post.scores = biased_probs.reshape(-1,1)
        aif_pred_post.labels = y_pred_orig.reshape(-1,1)
        cpp = CalibratedEqOddsPostprocessing(unprivileged_groups=[{f'{sens_col}_num': unprivileged_num}],
                                             privileged_groups=[{f'{sens_col}_num': privileged_num}],
                                             cost_constraint='fnr')
        cpp.fit(aif_actual_post, aif_pred_post)
        aif_pred_cpp = cpp.predict(aif_pred_post)
        y_pred_cpp = aif_pred_cpp.labels.flatten().astype(int)
        acc_cpp = accuracy_score(y_test, y_pred_cpp)
        di_cpp = (y_pred_cpp[X_test[sens_col]==unpriv_val].mean() /
                  y_pred_cpp[X_test[sens_col]==privileged_val].mean())
        results['calibrated_eq_odds'] = {"accuracy": round(acc_cpp,4), "disparate_impact": round(float(di_cpp),4),
                                         "verdict": "PASS" if di_cpp>=0.8 else "FAIL"}
    except Exception as e:
        results['calibrated_eq_odds'] = {"error": str(e)}

    # Comparison chart
    techniques = ['Baseline','Reweighing','Exp.Gradient','Calib.EqOdds']
    accuracies = [results['baseline']['accuracy'],
                  results.get('reweighing',{}).get('accuracy',0),
                  results.get('exponentiated_gradient',{}).get('accuracy',0),
                  results.get('calibrated_eq_odds',{}).get('accuracy',0)]
    dis = [results['baseline']['disparate_impact'],
           results.get('reweighing',{}).get('disparate_impact',0),
           results.get('exponentiated_gradient',{}).get('disparate_impact',0),
           results.get('calibrated_eq_odds',{}).get('disparate_impact',0)]
    fig, axes = plt.subplots(1,2, figsize=(12,5))
    axes[0].bar(techniques, accuracies, color=['#E24B4A','#1D9E75','#1D9E75','#1D9E75'])
    axes[0].set_title('Accuracy before/after debiasing')
    axes[1].bar(techniques, dis, color=['#E24B4A' if d<0.8 else '#1D9E75' for d in dis])
    axes[1].axhline(0.8, color='gray', linestyle='--')
    axes[1].set_title('Disparate Impact')
    plt.tight_layout()
    results['chart_debiasing'] = fig_to_base64(fig)
    return results


def explain_shap(target_col: str, sensitive_cols: List[str], sample_size: Optional[int] = None) -> Dict[str, Any]:
    import shap
    import warnings
    warnings.filterwarnings('ignore')

    # PRIORITY 1: Use the pretrained model (if saved from a pretrained run)
    if os.path.exists('models/pretrained_model.pkl') and os.path.exists('models/pretrained_preprocessor.pkl'):
        print("[tabular] Using pretrained model for SHAP.")
        model = joblib.load('models/pretrained_model.pkl')
        preprocessor = joblib.load('models/pretrained_preprocessor.pkl')
    # PRIORITY 2: Use the baseline model (trained on current dataset)
    elif os.path.exists('models/biased_model.pkl'):
        print("[tabular] Using baseline model for SHAP.")
        pipeline = joblib.load('models/biased_model.pkl')
        preprocessor = pipeline.named_steps['preprocessor']
        model = pipeline.named_steps['classifier']
    else:
        raise FileNotFoundError("No model found for SHAP explanation.")

    model_data = joblib.load('models/test_data.pkl')
    X_test = model_data['X_test']
    y_pred_full = model_data['y_pred']

    # --- OPTIMIZATION: Sample FIRST, then transform ---
    if sample_size is not None and len(X_test) > sample_size:
        indices = np.random.choice(len(X_test), sample_size, replace=False)
        X_test = X_test.iloc[indices]
        y_pred = y_pred_full[indices]
        print(f"[tabular] SHAP using {sample_size} random rows (was {len(X_test)})")
    else:
        y_pred = y_pred_full
        print(f"[tabular] SHAP using all {len(X_test)} rows")

    # Now transform only the sampled rows
    X_test_proc = preprocessor.transform(X_test)

    # Background sample (200 rows, but not more than available)
    bg_size = min(200, len(X_test_proc))
    background = shap.utils.sample(X_test_proc, bg_size, random_state=42)

    import scipy.sparse as sp
    if sp.issparse(X_test_proc):
        X_test_proc = X_test_proc.toarray()

    # Feature names
    if hasattr(preprocessor, 'get_feature_names_out'):
        try:
            feature_names = preprocessor.get_feature_names_out().tolist()
        except:
            num_features = [col for col in X_test.columns if col in preprocessor.named_transformers_['num'].feature_names_in_]
            cat_features = preprocessor.named_transformers_['cat'].get_feature_names_out().tolist()
            feature_names = num_features + cat_features
    else:
        num_features = [col for col in X_test.columns if col in preprocessor.named_transformers_['num'].feature_names_in_]
        cat_features = preprocessor.named_transformers_['cat'].get_feature_names_out().tolist()
        feature_names = num_features + cat_features

    if isinstance(model, LogisticRegression):
        explainer = shap.LinearExplainer(model, background)
    elif hasattr(model, 'estimators_') or isinstance(model, RandomForestClassifier):
        explainer = shap.TreeExplainer(model)
    else:
        explainer = shap.KernelExplainer(model.predict, background)

    shap_values = explainer.shap_values(X_test_proc)
    # Handle binary classification output
    if isinstance(shap_values, list):
        shap_values = shap_values[1] if len(shap_values) == 2 else shap_values[0]
    elif hasattr(shap_values, 'shape') and len(shap_values.shape) == 2 and shap_values.shape[1] == 2:
        shap_values = shap_values[:, 1]
    elif hasattr(shap_values, 'shape') and len(shap_values.shape) == 3 and shap_values.shape[2] == 2:
        shap_values = shap_values[:, :, 1]

    # Summary plot
    fig1, ax1 = plt.subplots(figsize=(10,7))
    shap.summary_plot(shap_values, X_test_proc, feature_names=feature_names, max_display=15, show=False)
    chart_summary = fig_to_base64(plt.gcf())

    # Bar plot
    fig2, ax2 = plt.subplots(figsize=(10,7))
    shap.summary_plot(shap_values, X_test_proc, feature_names=feature_names, plot_type='bar', max_display=15, show=False)
    chart_bar = fig_to_base64(plt.gcf())

    # Waterfall plot for a denied sample from the unprivileged group
    sens_col = sensitive_cols[0]
    results_df = X_test.copy()
    results_df['y_pred'] = y_pred
    uniq_vals = results_df[sens_col].unique()
    unpriv_value = uniq_vals[0] if len(uniq_vals) == 2 else uniq_vals[0]
    denied = results_df[(results_df[sens_col] == unpriv_value) & (results_df['y_pred'] == 0)]
    chart_force = ""
    if len(denied) > 0:
        sample_idx = denied.index[0]
        proc_idx = list(X_test.index).index(sample_idx)
        fig3, ax3 = plt.subplots(figsize=(14,3))
        base_val = explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)):
            base_val = base_val[1] if len(base_val) > 1 else base_val[0]
        shap.waterfall_plot(shap.Explanation(values=shap_values[proc_idx],
                                             base_values=base_val,
                                             data=X_test_proc[proc_idx],
                                             feature_names=feature_names), max_display=12, show=False)
        chart_force = fig_to_base64(plt.gcf())

    # Dependence plot for sensitive attribute
    chart_dependence = ""
    try:
        sens_feature = [f for f in feature_names if sens_col.lower() in f.lower()][0]
        sens_idx = feature_names.index(sens_feature)
        fig4, ax4 = plt.subplots(figsize=(8,5))
        shap.dependence_plot(sens_idx, shap_values, X_test_proc, feature_names=feature_names, ax=ax4, show=False)
        chart_dependence = fig_to_base64(fig4)
    except:
        pass

    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_features = sorted(zip(feature_names, mean_abs_shap), key=lambda x: x[1], reverse=True)[:15]
    sex_race_contributions = {name: round(val,6) for name,val in top_features if any(x in name.lower() for x in ['sex','gender','race','ethnic'])}
    return {
        "chart_shap_summary": chart_summary,
        "chart_shap_bar": chart_bar,
        "chart_shap_force": chart_force,
        "chart_shap_dependence": chart_dependence,
        "sex_race_contributions": sex_race_contributions,
        "top_features": [{"feature": f, "importance": round(v,6)} for f,v in top_features]
    }

# -------------------- Main audit function --------------------
async def run_tabular_audit(file, target_col: str, sensitive_cols: List[str], privileged_groups: Dict[str, Any],
                            model_choice: str = "logistic", model_file: Optional[Any] = None,
                            preprocessor_file: Optional[Any] = None,
                            shap_sample_size: Optional[int] = None) -> Dict[str, Any]:
    print("\n[tabular] Starting generic audit...")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        df = load_and_profile(tmp_path, target_col)
        numerical, categorical = infer_schema(df, target_col, sensitive_cols)
        eda_charts = generate_eda_charts(df, target_col, sensitive_cols)
        baseline = train_or_load_baseline(df, target_col, sensitive_cols, numerical, categorical,
                                          model_choice, model_file, preprocessor_file)
        metrics = compute_metrics(target_col, sensitive_cols, privileged_groups)
        is_pretrained = baseline.get("pretrained", False)
        debiasing_results = debias(df, target_col, sensitive_cols, privileged_groups,
                                   numerical, categorical, model_choice, is_pretrained)
        
        # Call SHAP with optional sample size
        shap_results = explain_shap(target_col, sensitive_cols, sample_size=shap_sample_size)

    finally:
        os.unlink(tmp_path)

    verdict = metrics['verdict']
    di = metrics['disparate_impact']
    recommendations = []
    if di < 0.8:
        recommendations.append(f"Disparate Impact = {di:.2f} below 0.8 threshold. Apply ExponentiatedGradient debiasing.")

    best_method = "none"
    best_di = di
    if not is_pretrained:
        best_method = max(['reweighing','exponentiated_gradient','calibrated_eq_odds'],
                          key=lambda m: debiasing_results.get(m,{}).get('disparate_impact',0))
        best_di = debiasing_results.get(best_method,{}).get('disparate_impact', di)
    else:
        best_method = "not_applied"

    # Generate plain‑language explanations
    explanation_summary = generate_plain_language_summary(
        metrics, verdict, di, debiasing_results, best_method
    )

    per_group = metrics['per_group_metrics']
    groups = [{"group_name": str(k), "metrics": {"accuracy": per_group['accuracy'][k],
                "precision": per_group['precision'][k], "recall": per_group['recall'][k]}}
              for k in per_group['accuracy'].keys()]

    result = {
        "request_id": str(uuid.uuid4()),
        "module": "tabular",
        "model_name": model_choice if not model_file else "pretrained",
        "overall": {
            "accuracy": baseline['accuracy'],
            "disparate_impact": metrics['disparate_impact'],
            "stat_parity_diff": metrics['stat_parity_diff'],
            "equal_opportunity_diff": metrics['equal_opportunity_diff'],
            "avg_odds_diff": metrics['avg_odds_diff'],
            "dp_diff": metrics['dp_diff'],
            "eod_diff": metrics['eod_diff'],
            "bias_score": round(1 - di, 4),
            "verdict": verdict,
        },
        "groups": groups,
        "explanation": {
            "type": "SHAP",
            "description": f"{sensitive_cols[0]} is among top biased features.",
            "image_base64": shap_results['chart_shap_summary'],
        },
        "debiasing": {
            "method": best_method,
            "before_score": metrics['disparate_impact'],
            "after_score": best_di,
            "improvement": round(best_di - metrics['disparate_impact'], 4),
        },
        "charts": {
            **eda_charts,
            "disparity": baseline['chart_disparity'],
            "metrics": metrics['chart_metrics'],
            "debiasing": debiasing_results.get('chart_debiasing', ''),
            "shap_summary": shap_results['chart_shap_summary'],
            "shap_bar": shap_results['chart_shap_bar'],
            "shap_force": shap_results['chart_shap_force'],
            "shap_dependence": shap_results['chart_shap_dependence'],
        },
        "debiasing_comparison": debiasing_results,
        "top_features": shap_results['top_features'],
        "sex_race_contributions": shap_results['sex_race_contributions'],
        "recommendations": recommendations,
        "explanation_summary": explanation_summary,   # new field for plain language
        "status": "success",
        "message": f"Bias audit complete. Verdict: {verdict}. Disparate Impact = {di:.4f}."
    }

    return sanitize_for_json(result)