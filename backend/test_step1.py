


# """
# Test script for the flexible tabular bias auditor.
# Runs a full audit on the UCI Adult dataset using the flexible endpoint logic.
# """

# import os
# import base64
# import urllib.request
# import pandas as pd
# from app.services.tabular_service import (
#     load_and_profile,
#     generate_eda_charts,
#     train_or_load_baseline,
#     compute_metrics,
#     debias,
#     explain_shap,
#     infer_schema
# )

# # ========== Configuration ==========
# DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
# RAW_DATA_FILE = "adult.data"
# HEADER_DATA_FILE = "adult_100.csv"

# TARGET_COL = "income"
# SENSITIVE_COLS = ["sex"]
# PRIVILEGED_GROUPS = {"sex": "Male"}
# MODEL_CHOICE = "logistic"   # or "randomforest"
# # ===================================

# def ensure_header_dataset():
#     """Convert adult.data (no header) to adult_with_header.csv (with header)."""
#     if os.path.exists(HEADER_DATA_FILE):
#         print(f"Header dataset already exists: {HEADER_DATA_FILE}")
#         return HEADER_DATA_FILE

#     if not os.path.exists(RAW_DATA_FILE):
#         print("Downloading raw dataset...")
#         urllib.request.urlretrieve(DATASET_URL, RAW_DATA_FILE)
#         print("Download complete.")

#     print("Converting to header CSV...")
#     cols = [
#         'age', 'workclass', 'fnlwgt', 'education', 'education-num',
#         'marital-status', 'occupation', 'relationship', 'race', 'sex',
#         'capital-gain', 'capital-loss', 'hours-per-week',
#         'native-country', 'income'
#     ]
#     df = pd.read_csv(RAW_DATA_FILE, names=cols, na_values=' ?', skipinitialspace=True)
#     df.dropna(inplace=True)
#     df.reset_index(drop=True, inplace=True)
#     df['income'] = (df['income'].str.strip() == '>50K').astype(int)
#     df.to_csv(HEADER_DATA_FILE, index=False)
#     print(f"Saved {HEADER_DATA_FILE} with {len(df)} rows.")
#     return HEADER_DATA_FILE

# def test_full_pipeline():
#     print("\n" + "="*60)
#     print("TESTING FLEXIBLE TABULAR BIAS AUDITOR")
#     print("="*60)

#     # Prepare dataset
#     csv_path = ensure_header_dataset()

#     # Load data
#     df = load_and_profile(csv_path, TARGET_COL)
#     print(f"Loaded {len(df)} rows, positive rate = {df[TARGET_COL].mean():.2%}")

#     # Infer schema
#     numerical, categorical = infer_schema(df, TARGET_COL, SENSITIVE_COLS)
#     print(f"Numerical features: {numerical}")
#     print(f"Categorical features: {categorical}")

#     # EDA charts
#     eda_charts = generate_eda_charts(df, TARGET_COL, SENSITIVE_COLS)
#     print("EDA charts generated.")

#     # Train baseline (or use pretrained – here we train from scratch)
#     baseline = train_or_load_baseline(
#         df, TARGET_COL, SENSITIVE_COLS, numerical, categorical,
#         MODEL_CHOICE, model_file=None, preprocessor_file=None
#     )
#     print(f"Baseline accuracy: {baseline['accuracy']}")
#     print(f"Group rates: {baseline['group_rates']}")

#     # Fairness metrics
#     metrics = compute_metrics(TARGET_COL, SENSITIVE_COLS, PRIVILEGED_GROUPS)
#     print(f"\nDisparate Impact: {metrics['disparate_impact']} -> Verdict: {metrics['verdict']}")
#     print(f"Statistical Parity Diff: {metrics['stat_parity_diff']}")
#     print(f"Equal Opportunity Diff: {metrics['equal_opportunity_diff']}")

#     # Debiasing
#     is_pretrained = baseline.get("pretrained", False)
#     debiasing_results = debias(
#         df, TARGET_COL, SENSITIVE_COLS, PRIVILEGED_GROUPS,
#         numerical, categorical, MODEL_CHOICE, is_pretrained
#     )
#     print("\nDebiasing results:")
#     for tech, res in debiasing_results.items():
#         if tech in ['chart_debiasing', 'note']:
#             continue
#         if 'error' in res:
#             print(f"  {tech}: ERROR - {res['error']}")
#         else:
#             print(f"  {tech}: acc={res['accuracy']}, DI={res['disparate_impact']}, {res['verdict']}")

#     # SHAP explainability
#     shap_results = explain_shap(TARGET_COL, SENSITIVE_COLS,sample_size=None)
#     print("\nTop 5 SHAP features:")
#     for feat in shap_results['top_features'][:5]:
#         print(f"  {feat['feature']:40s} importance={feat['importance']:.6f}")
#     print(f"Sex/Race contributions: {shap_results['sex_race_contributions']}")

#     # Save all charts as PNG files
#     all_charts = {
#         **eda_charts,
#         "disparity": baseline['chart_disparity'],
#         "metrics": metrics['chart_metrics'],
#         "debiasing": debiasing_results.get('chart_debiasing', ''),
#         "shap_summary": shap_results['chart_shap_summary'],
#         "shap_bar": shap_results['chart_shap_bar'],
#         "shap_force": shap_results['chart_shap_force'],
#         "shap_dependence": shap_results['chart_shap_dependence'],
#     }
#     saved = 0
#     for name, b64 in all_charts.items():
#         if not b64:
#             continue
#         path = f"test_{name}.png"
#         with open(path, "wb") as f:
#             f.write(base64.b64decode(b64))
#         print(f"Saved {path}")
#         saved += 1
#     print(f"\nSaved {saved} chart images.")

#     print("\n" + "="*60)
#     print("TEST COMPLETED SUCCESSFULLY")
#     print("="*60)

# if __name__ == "__main__":
#     test_full_pipeline()

import os
import base64
import urllib.request
import pandas as pd
from app.services.tabular_service import (
    load_and_profile,
    generate_eda_charts,
    train_or_load_baseline,
    compute_metrics,
    debias,
    explain_shap,
    infer_schema,
    generate_plain_language_summary   # <-- import the new function
)

# ========== Configuration ==========
DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
RAW_DATA_FILE = "adult.data"
HEADER_DATA_FILE = "adult_with_header.csv"

TARGET_COL = "income"
SENSITIVE_COLS = ["sex"]
PRIVILEGED_GROUPS = {"sex": "Male"}
MODEL_CHOICE = "logistic"   # or "randomforest"
# ===================================

def ensure_header_dataset():
    if os.path.exists(HEADER_DATA_FILE):
        print(f"Header dataset already exists: {HEADER_DATA_FILE}")
        return HEADER_DATA_FILE
    if not os.path.exists(RAW_DATA_FILE):
        print("Downloading raw dataset...")
        urllib.request.urlretrieve(DATASET_URL, RAW_DATA_FILE)
    print("Converting to header CSV...")
    cols = [
        'age','workclass','fnlwgt','education','education-num',
        'marital-status','occupation','relationship','race','sex',
        'capital-gain','capital-loss','hours-per-week','native-country','income'
    ]
    df = pd.read_csv(RAW_DATA_FILE, names=cols, na_values=' ?', skipinitialspace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['income'] = (df['income'].str.strip() == '>50K').astype(int)
    df.to_csv(HEADER_DATA_FILE, index=False)
    print(f"Saved {HEADER_DATA_FILE} with {len(df)} rows.")
    return HEADER_DATA_FILE

def test_full_pipeline():
    print("\n" + "="*60)
    print("TESTING FLEXIBLE TABULAR BIAS AUDITOR")
    print("="*60)

    csv_path = ensure_header_dataset()
    df = load_and_profile(csv_path, TARGET_COL)
    print(f"Loaded {len(df)} rows, positive rate = {df[TARGET_COL].mean():.2%}")

    numerical, categorical = infer_schema(df, TARGET_COL, SENSITIVE_COLS)
    print(f"Numerical features: {numerical}")
    print(f"Categorical features: {categorical}")

    eda_charts = generate_eda_charts(df, TARGET_COL, SENSITIVE_COLS)
    print("EDA charts generated.")

    baseline = train_or_load_baseline(
        df, TARGET_COL, SENSITIVE_COLS, numerical, categorical,
        MODEL_CHOICE, model_file=None, preprocessor_file=None
    )
    print(f"Baseline accuracy: {baseline['accuracy']}")
    print(f"Group rates: {baseline['group_rates']}")

    metrics = compute_metrics(TARGET_COL, SENSITIVE_COLS, PRIVILEGED_GROUPS)
    di = metrics['disparate_impact']
    verdict = metrics['verdict']
    print(f"\nDisparate Impact: {di} -> Verdict: {verdict}")
    print(f"Statistical Parity Diff: {metrics['stat_parity_diff']}")
    print(f"Equal Opportunity Diff: {metrics['equal_opportunity_diff']}")

    is_pretrained = baseline.get("pretrained", False)
    debiasing_results = debias(
        df, TARGET_COL, SENSITIVE_COLS, PRIVILEGED_GROUPS,
        numerical, categorical, MODEL_CHOICE, is_pretrained
    )
    print("\nDebiasing results:")
    for tech, res in debiasing_results.items():
        if tech in ['chart_debiasing', 'note']:
            continue
        if 'error' in res:
            print(f"  {tech}: ERROR - {res['error']}")
        else:
            print(f"  {tech}: acc={res['accuracy']}, DI={res['disparate_impact']}, {res['verdict']}")

    shap_results = explain_shap(TARGET_COL, SENSITIVE_COLS, sample_size=None)
    print("\nTop 5 SHAP features:")
    for feat in shap_results['top_features'][:5]:
        print(f"  {feat['feature']:40s} importance={feat['importance']:.6f}")
    print(f"Sex/Race contributions: {shap_results['sex_race_contributions']}")

    # ----- Plain‑language explanation -----
    best_method = "none"
    if not is_pretrained:
        best_method = max(['reweighing','exponentiated_gradient','calibrated_eq_odds'],
                          key=lambda m: debiasing_results.get(m,{}).get('disparate_impact',0))
    explanation = generate_plain_language_summary(metrics, verdict, di, debiasing_results, best_method)
    print("\n" + "="*60)
    print("PLAIN LANGUAGE EXPLANATION")
    print("="*60)
    print(f"Verdict explanation: {explanation['verdict_explanation']}")
    print("\nSuggestions:")
    for s in explanation['suggestions']:
        print(f"  - {s}")
    print("\nMetric descriptions:")
    for k, desc in explanation['metric_descriptions'].items():
        print(f"  {k}: {desc[:200]}...")

    # Save all charts
    all_charts = {
        **eda_charts,
        "disparity": baseline['chart_disparity'],
        "metrics": metrics['chart_metrics'],
        "debiasing": debiasing_results.get('chart_debiasing', ''),
        "shap_summary": shap_results['chart_shap_summary'],
        "shap_bar": shap_results['chart_shap_bar'],
        "shap_force": shap_results['chart_shap_force'],
        "shap_dependence": shap_results['chart_shap_dependence'],
    }
    saved = 0
    for name, b64 in all_charts.items():
        if not b64:
            continue
        path = f"test_{name}.png"
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"Saved {path}")
        saved += 1
    print(f"\nSaved {saved} chart images.")

    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    test_full_pipeline()

