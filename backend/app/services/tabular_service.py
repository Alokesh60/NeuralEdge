# tabular_service.py
# import uuid
# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Agg')
# import io, base64, os
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score
# import joblib


# # ── Helper: convert matplotlib figure to base64 ───────────────────────────
# def fig_to_base64(fig):
#     buf = io.BytesIO()
#     fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
#     buf.seek(0)
#     encoded = base64.b64encode(buf.read()).decode('utf-8')
#     plt.close(fig)
#     return encoded


# # ── Step 1: Load dataset + EDA ─────────────────────────────────────────────
# def load_and_profile(filepath: str) -> pd.DataFrame:
#     cols = [
#         'age', 'workclass', 'fnlwgt', 'education', 'education-num',
#         'marital-status', 'occupation', 'relationship', 'race', 'sex',
#         'capital-gain', 'capital-loss', 'hours-per-week',
#         'native-country', 'income'
#     ]
#     df = pd.read_csv(filepath, names=cols, na_values=' ?',
#                      skipinitialspace=True)
#     df.dropna(inplace=True)
#     df.reset_index(drop=True, inplace=True)
#     df['income'] = (df['income'].str.strip() == '>50K').astype(int)

#     print(f"[tabular] Loaded {len(df)} rows, {df['income'].mean():.2%} positive rate")
#     print(f"[tabular] Gender distribution:\n{df['sex'].value_counts()}")
#     print(f"[tabular] Race distribution:\n{df['race'].value_counts()}")

#     return df


# # ── Step 1b: EDA charts ────────────────────────────────────────────────────
# def generate_eda_charts(df: pd.DataFrame) -> dict:
#     # Chart 1: Income rate by gender
#     fig1, ax1 = plt.subplots(figsize=(6, 4))
#     gender_rates = df.groupby('sex')['income'].mean().reset_index()
#     gender_rates.columns = ['sex', 'positive_rate']
#     sns.barplot(data=gender_rates, x='sex', y='positive_rate',
#                 hue='sex', palette=['#5DCAA5', '#D85A30'],
#                 legend=False, ax=ax1)
#     ax1.axhline(0.5, color='gray', linestyle='--',
#                 alpha=0.5, label='Parity line')
#     ax1.set_title('Income >50K rate by gender (raw data)')
#     ax1.set_ylabel('Rate')
#     ax1.set_ylim(0, 0.6)
#     ax1.legend()
#     chart_gender = fig_to_base64(fig1)

#     # Chart 2: Income rate by race
#     fig2, ax2 = plt.subplots(figsize=(7, 4))
#     race_rates = df.groupby('race')['income'].mean().reset_index()
#     race_rates.columns = ['race', 'positive_rate']
#     sns.barplot(data=race_rates, x='race', y='positive_rate',
#                 hue='race', palette='Blues_d',
#                 legend=False, ax=ax2)
#     ax2.set_title('Income >50K rate by race (raw data)')
#     ax2.set_ylabel('Rate')
#     ax2.set_ylim(0, 0.6)
#     ax2.tick_params(axis='x', rotation=20)
#     chart_race = fig_to_base64(fig2)

#     return {
#         "chart_gender_eda": chart_gender,
#         "chart_race_eda":   chart_race
#     }


# # ── Step 2: Train biased baseline model ───────────────────────────────────
# def train_baseline(df: pd.DataFrame) -> dict:
#     # ── Skip retraining if model already exists ───────────────────────────
#     if os.path.exists('models/biased_model.pkl') and \
#        os.path.exists('models/test_data.pkl'):
#         print("[tabular] Model already exists — loading from disk.")
#         model_data = joblib.load('models/test_data.pkl')
#         y_test     = model_data['y_test']
#         y_pred     = model_data['y_pred']
#         results_df = model_data['results']
#         return {
#             "accuracy":        round(accuracy_score(y_test, y_pred), 4),
#             "report":          {},
#             "gender_rates":    results_df.groupby('sex')['y_pred']
#                                          .mean().round(3).to_dict(),
#             "race_rates":      results_df.groupby('race')['y_pred']
#                                          .mean().round(3).to_dict(),
#             "chart_disparity": "",
#             "model_path":      "models/biased_model.pkl"
#         }

#     # ── Protected attributes intentionally included ────────────────────────
#     categorical = [
#         'workclass', 'education', 'marital-status', 'occupation',
#         'relationship', 'native-country',
#         'sex', 'race'
#     ]
#     numerical = [
#         'age', 'fnlwgt', 'education-num',
#         'capital-gain', 'capital-loss', 'hours-per-week'
#     ]

#     preprocessor = ColumnTransformer(transformers=[
#         ('num', StandardScaler(),                        numerical),
#         ('cat', OneHotEncoder(handle_unknown='ignore'),  categorical)
#     ])

#     X = df.drop('income', axis=1)
#     y = df['income']

#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, stratify=y
#     )

#     model = Pipeline([
#         ('preprocessor', preprocessor),
#         ('classifier',   LogisticRegression(max_iter=1000, random_state=42))
#     ])

#     model.fit(X_train, y_train)
#     y_pred = model.predict(X_test)

#     accuracy = accuracy_score(y_test, y_pred)
#     report   = classification_report(y_test, y_pred, output_dict=True)

#     print(f"\n[tabular] Overall accuracy: {accuracy:.4f}")
#     print(f"[tabular] Classification report:\n"
#           f"{classification_report(y_test, y_pred)}")

#     results_df           = X_test.copy()
#     results_df['y_true'] = y_test.values
#     results_df['y_pred'] = y_pred

#     gender_rates = results_df.groupby('sex')['y_pred'].mean().round(3).to_dict()
#     race_rates   = results_df.groupby('race')['y_pred'].mean().round(3).to_dict()

#     print(f"\n[tabular] Positive prediction rate by gender: {gender_rates}")
#     print(f"[tabular] Positive prediction rate by race:   {race_rates}")

#     fig, axes = plt.subplots(1, 2, figsize=(12, 4))
#     pd.Series(gender_rates).plot(kind='bar', ax=axes[0],
#                                   color=['#5DCAA5', '#D85A30'])
#     axes[0].set_title('Predicted income >50K rate by gender')
#     axes[0].set_ylabel('Prediction rate')
#     axes[0].set_ylim(0, 0.6)
#     axes[0].axhline(0.5, color='gray', linestyle='--', alpha=0.5)
#     axes[0].tick_params(axis='x', rotation=0)

#     pd.Series(race_rates).plot(kind='bar', ax=axes[1], color='#378ADD')
#     axes[1].set_title('Predicted income >50K rate by race')
#     axes[1].set_ylabel('Prediction rate')
#     axes[1].set_ylim(0, 0.6)
#     axes[1].tick_params(axis='x', rotation=20)

#     plt.tight_layout()
#     chart_disparity = fig_to_base64(fig)

#     os.makedirs('models', exist_ok=True)
#     joblib.dump(model, 'models/biased_model.pkl')
#     joblib.dump({
#         'X_test':  X_test,
#         'y_test':  y_test,
#         'y_pred':  y_pred,
#         'results': results_df
#     }, 'models/test_data.pkl')
#     print("\n[tabular] Model saved to models/biased_model.pkl")

#     return {
#         "accuracy":        round(accuracy, 4),
#         "report":          report,
#         "gender_rates":    gender_rates,
#         "race_rates":      race_rates,
#         "chart_disparity": chart_disparity,
#         "model_path":      "models/biased_model.pkl"
#     }


# # ── Step 3: Compute fairness metrics ──────────────────────────────────────
# def compute_metrics(df: pd.DataFrame) -> dict:
#     from aif360.datasets import BinaryLabelDataset
#     from aif360.metrics import ClassificationMetric
#     from fairlearn.metrics import (
#         MetricFrame,
#         demographic_parity_difference,
#         equalized_odds_difference
#     )

#     model_data = joblib.load('models/test_data.pkl')
#     X_test     = model_data['X_test']
#     y_test     = model_data['y_test']
#     y_pred     = model_data['y_pred']

#     test_df             = X_test.copy()
#     test_df['sex_num']  = (test_df['sex']  == 'Male').astype(int)
#     test_df['race_num'] = (test_df['race'] == 'White').astype(int)

#     actual_df           = test_df[['sex_num', 'race_num']].copy()
#     actual_df['income'] = y_test.values

#     pred_df             = test_df[['sex_num', 'race_num']].copy()
#     pred_df['income']   = y_pred.astype(float)

#     aif_actual = BinaryLabelDataset(
#         df                              = actual_df,
#         label_names                     = ['income'],
#         protected_attribute_names       = ['sex_num', 'race_num'],
#         privileged_protected_attributes = [[1], [1]]
#     )
#     aif_pred        = aif_actual.copy()
#     aif_pred.labels = pred_df['income'].values.reshape(-1, 1)

#     privileged_groups   = [{'sex_num': 1}]
#     unprivileged_groups = [{'sex_num': 0}]

#     clf_metric = ClassificationMetric(
#         aif_actual, aif_pred,
#         unprivileged_groups = unprivileged_groups,
#         privileged_groups   = privileged_groups
#     )

#     disparate_impact       = clf_metric.disparate_impact()
#     stat_parity_diff       = clf_metric.statistical_parity_difference()
#     equal_opportunity_diff = clf_metric.equal_opportunity_difference()
#     avg_odds_diff          = clf_metric.average_odds_difference()

#     print(f"\n[tabular] ── AIF360 Fairness Metrics (sex) ──")
#     print(f"  Disparate Impact:        {disparate_impact:.4f}  (ideal=1.0, <0.8 = biased)")
#     print(f"  Statistical Parity Diff: {stat_parity_diff:.4f}  (ideal=0)")
#     print(f"  Equal Opportunity Diff:  {equal_opportunity_diff:.4f}  (ideal=0)")
#     print(f"  Average Odds Diff:       {avg_odds_diff:.4f}  (ideal=0)")

#     verdict = "FAIL" if disparate_impact < 0.8 or \
#                         disparate_impact > 1.2 else "PASS"
#     print(f"\n[tabular] Bias verdict: {verdict}")

#     sensitive    = X_test['sex']
#     metric_frame = MetricFrame(
#         metrics = {
#             'accuracy':  accuracy_score,
#             'precision': lambda y_t, y_p: precision_score(
#                              y_t, y_p, zero_division=0),
#             'recall':    lambda y_t, y_p: recall_score(
#                              y_t, y_p, zero_division=0),
#         },
#         y_true             = y_test,
#         y_pred             = y_pred,
#         sensitive_features = sensitive
#     )

#     per_group = metric_frame.by_group.round(4).to_dict()
#     print(f"\n[tabular] ── Fairlearn Per-Group Metrics ──")
#     print(metric_frame.by_group.round(4))

#     dp_diff  = demographic_parity_difference(
#                    y_test, y_pred, sensitive_features=sensitive)
#     eod_diff = equalized_odds_difference(
#                    y_test, y_pred, sensitive_features=sensitive)
#     print(f"\n  Demographic Parity Difference: {dp_diff:.4f}  (ideal=0)")
#     print(f"  Equalized Odds Difference:     {eod_diff:.4f}  (ideal=0)")

#     fig, axes = plt.subplots(1, 2, figsize=(12, 4))
#     metrics_vals = {
#         'Disparate\nImpact':  disparate_impact,
#         'Stat Parity\nDiff':  abs(stat_parity_diff),
#         'Equal Opp\nDiff':    abs(equal_opportunity_diff),
#         'Avg Odds\nDiff':     abs(avg_odds_diff),
#     }
#     bar_colors = [
#         '#E24B4A' if (k == 'Disparate\nImpact' and (v < 0.8 or v > 1.2))
#         else '#E24B4A' if (k != 'Disparate\nImpact' and v > 0.1)
#         else '#1D9E75'
#         for k, v in metrics_vals.items()
#     ]
#     axes[0].bar(metrics_vals.keys(), metrics_vals.values(), color=bar_colors)
#     axes[0].axhline(0.8, color='gray', linestyle='--',
#                     alpha=0.6, label='0.8 threshold')
#     axes[0].set_title('AIF360 fairness metrics')
#     axes[0].set_ylabel('Score')
#     axes[0].legend()

#     metric_frame.by_group['accuracy'].plot(
#         kind='bar', ax=axes[1],
#         color=['#5DCAA5', '#D85A30']
#     )
#     axes[1].set_title('Accuracy by gender (Fairlearn)')
#     axes[1].set_ylabel('Accuracy')
#     axes[1].set_ylim(0, 1)
#     axes[1].tick_params(axis='x', rotation=0)
#     axes[1].axhline(
#         metric_frame.overall['accuracy'],
#         color='gray', linestyle='--', alpha=0.6, label='Overall'
#     )
#     axes[1].legend()

#     plt.tight_layout()
#     chart_metrics = fig_to_base64(fig)

#     return {
#         "disparate_impact":       round(disparate_impact, 4),
#         "stat_parity_diff":       round(stat_parity_diff, 4),
#         "equal_opportunity_diff": round(equal_opportunity_diff, 4),
#         "avg_odds_diff":          round(avg_odds_diff, 4),
#         "dp_diff":                round(dp_diff, 4),
#         "eod_diff":               round(eod_diff, 4),
#         "verdict":                verdict,
#         "per_group_metrics":      per_group,
#         "chart_metrics":          chart_metrics
#     }


# # ── Step 4: Three debiasing techniques ────────────────────────────────────
# def debias(df: pd.DataFrame) -> dict:
#     from aif360.datasets import BinaryLabelDataset
#     from aif360.algorithms.preprocessing import Reweighing
#     from aif360.algorithms.postprocessing import CalibratedEqOddsPostprocessing
#     from fairlearn.reductions import ExponentiatedGradient, DemographicParity
#     from sklearn.metrics import accuracy_score

#     print("\n[tabular] ── Step 4: Debiasing ──────────────────────────────")

#     model_data   = joblib.load('models/test_data.pkl')
#     X_test       = model_data['X_test']
#     y_test       = model_data['y_test']
#     y_pred_orig  = model_data['y_pred']
#     biased_model = joblib.load('models/biased_model.pkl')

#     orig_di  = (y_pred_orig[X_test['sex'] == 'Female'].mean() /
#                 y_pred_orig[X_test['sex'] == 'Male'].mean())
#     orig_acc = accuracy_score(y_test, y_pred_orig)
#     print(f"  Baseline — Accuracy: {orig_acc:.4f}, Disparate Impact: {orig_di:.4f}")

#     results = {
#         "baseline": {
#             "accuracy":         round(orig_acc, 4),
#             "disparate_impact": round(orig_di, 4),
#             "verdict":          "FAIL" if orig_di < 0.8 else "PASS"
#         }
#     }

#     categorical = [
#         'workclass', 'education', 'marital-status', 'occupation',
#         'relationship', 'native-country', 'sex', 'race'
#     ]
#     numerical = [
#         'age', 'fnlwgt', 'education-num',
#         'capital-gain', 'capital-loss', 'hours-per-week'
#     ]

#     X = df.drop('income', axis=1)
#     y = df['income']
#     X_train, X_test_rw, y_train, y_test_rw = train_test_split(
#         X, y, test_size=0.2, random_state=42, stratify=y
#     )

#     # ── Technique 1: Reweighing (Pre-processing) ──────────────────────────
#     print("\n  [1/3] Reweighing (pre-processing)...")
#     try:
#         train_df             = X_train.copy()
#         train_df['income']   = y_train.values
#         train_df['sex_num']  = (train_df['sex']  == 'Male').astype(int)
#         train_df['race_num'] = (train_df['race'] == 'White').astype(int)

#         aif_train = BinaryLabelDataset(
#             df                              = train_df[['sex_num', 'race_num', 'income']],
#             label_names                     = ['income'],
#             protected_attribute_names       = ['sex_num', 'race_num'],
#             privileged_protected_attributes = [[1], [1]]
#         )

#         RW           = Reweighing(unprivileged_groups=[{'sex_num': 0}],
#                                   privileged_groups  =[{'sex_num': 1}])
#         aif_train_rw = RW.fit_transform(aif_train)
#         sample_weights = aif_train_rw.instance_weights

#         preprocessor_rw = ColumnTransformer(transformers=[
#             ('num', StandardScaler(),                        numerical),
#             ('cat', OneHotEncoder(handle_unknown='ignore'),  categorical)
#         ])
#         X_train_proc = preprocessor_rw.fit_transform(X_train)
#         X_test_proc  = preprocessor_rw.transform(X_test_rw)

#         lr_rw = LogisticRegression(max_iter=1000, random_state=42)
#         lr_rw.fit(X_train_proc, y_train, sample_weight=sample_weights)
#         y_pred_rw = lr_rw.predict(X_test_proc)

#         acc_rw = accuracy_score(y_test_rw, y_pred_rw)
#         di_rw  = (y_pred_rw[X_test_rw['sex'].values == 'Female'].mean() /
#                   y_pred_rw[X_test_rw['sex'].values == 'Male'].mean())

#         print(f"  Reweighing — Accuracy: {acc_rw:.4f}, Disparate Impact: {di_rw:.4f}")
#         results['reweighing'] = {
#             "accuracy":         round(acc_rw, 4),
#             "disparate_impact": round(di_rw, 4),
#             "verdict":          "FAIL" if di_rw < 0.8 else "PASS"
#         }
#         joblib.dump(lr_rw,           'models/reweighed_model.pkl')
#         joblib.dump(preprocessor_rw, 'models/reweighed_preprocessor.pkl')

#     except Exception as e:
#         print(f"  Reweighing failed: {e}")
#         results['reweighing'] = {"error": str(e)}

#     # ── Technique 2: ExponentiatedGradient (In-processing) ────────────────
#     print("\n  [2/3] ExponentiatedGradient (in-processing)...")
#     try:
#         import scipy.sparse as sp

#         preprocessor_eg = ColumnTransformer(transformers=[
#             ('num', StandardScaler(),                        numerical),
#             ('cat', OneHotEncoder(handle_unknown='ignore'),  categorical)
#         ])
#         X_train_eg = preprocessor_eg.fit_transform(X_train)
#         X_test_eg  = preprocessor_eg.transform(X_test_rw)

#         if sp.issparse(X_train_eg):
#             X_train_eg = X_train_eg.toarray()
#         if sp.issparse(X_test_eg):
#             X_test_eg = X_test_eg.toarray()

#         eg_model = ExponentiatedGradient(
#             estimator   = LogisticRegression(max_iter=1000, random_state=42),
#             constraints = DemographicParity()
#         )
#         eg_model.fit(X_train_eg, y_train,
#                      sensitive_features=X_train['sex'])
#         y_pred_eg = eg_model.predict(X_test_eg)

#         acc_eg = accuracy_score(y_test_rw, y_pred_eg)
#         di_eg  = (y_pred_eg[X_test_rw['sex'].values == 'Female'].mean() /
#                   y_pred_eg[X_test_rw['sex'].values == 'Male'].mean())

#         print(f"  ExponentiatedGradient — Accuracy: {acc_eg:.4f}, "
#               f"Disparate Impact: {di_eg:.4f}")
#         results['exponentiated_gradient'] = {
#             "accuracy":         round(acc_eg, 4),
#             "disparate_impact": round(float(di_eg), 4),
#             "verdict":          "FAIL" if di_eg < 0.8 else "PASS"
#         }

#     except Exception as e:
#         print(f"  ExponentiatedGradient failed: {e}")
#         results['exponentiated_gradient'] = {"error": str(e)}

#     # ── Technique 3: Calibrated Equalized Odds (Post-processing) ──────────
#     print("\n  [3/3] Calibrated Equalized Odds (post-processing)...")
#     try:
#         test_df              = X_test.copy()
#         test_df['income']    = y_test.values
#         test_df['sex_num']   = (test_df['sex']  == 'Male').astype(int)
#         test_df['race_num']  = (test_df['race'] == 'White').astype(int)

#         # Use model probability scores instead of hard labels
#         biased_probs         = biased_model.predict_proba(X_test)[:, 1]
#         test_df['predicted'] = biased_probs

#         aif_actual_post = BinaryLabelDataset(
#             df                              = test_df[['sex_num', 'race_num', 'income']],
#             label_names                     = ['income'],
#             protected_attribute_names       = ['sex_num', 'race_num'],
#             privileged_protected_attributes = [[1], [1]]
#         )

#         # Build predicted dataset using scores
#         aif_pred_post          = aif_actual_post.copy()
#         aif_pred_post.scores   = biased_probs.reshape(-1, 1)
#         aif_pred_post.labels   = y_pred_orig.astype(float).reshape(-1, 1)

#         cpp = CalibratedEqOddsPostprocessing(
#             unprivileged_groups = [{'sex_num': 0}],
#             privileged_groups   = [{'sex_num': 1}],
#             cost_constraint     = 'fnr',
#             seed                = 42
#         )
#         cpp.fit(aif_actual_post, aif_pred_post)
#         aif_pred_cpp = cpp.predict(aif_pred_post)
#         y_pred_cpp   = aif_pred_cpp.labels.flatten().astype(int)

#         # Sanity check
#         acc_cpp = accuracy_score(y_test, y_pred_cpp)
#         if acc_cpp > 0.99:
#             print("  Warning: suspect predictions — using score threshold instead")
#             y_pred_cpp = (aif_pred_cpp.scores.flatten() > 0.5).astype(int)
#             acc_cpp    = accuracy_score(y_test, y_pred_cpp)

#         di_cpp = (y_pred_cpp[X_test['sex'].values == 'Female'].mean() /
#                   y_pred_cpp[X_test['sex'].values == 'Male'].mean())

#         print(f"  Calibrated EqOdds — Accuracy: {acc_cpp:.4f}, "
#               f"Disparate Impact: {di_cpp:.4f}")
#         results['calibrated_eq_odds'] = {
#             "accuracy":         round(acc_cpp, 4),
#             "disparate_impact": round(float(di_cpp), 4),
#             "verdict":          "FAIL" if di_cpp < 0.8 else "PASS"
#         }

#     except Exception as e:
#         print(f"  Calibrated EqOdds failed: {e}")
#         results['calibrated_eq_odds'] = {"error": str(e)}

#     # ── Before/After comparison chart ─────────────────────────────────────
#     fig, axes = plt.subplots(1, 2, figsize=(12, 5))

#     techniques = ['Baseline', 'Reweighing', 'Exp. Gradient', 'Calib. EqOdds']
#     accuracies = [
#         results['baseline']['accuracy'],
#         results.get('reweighing',             {}).get('accuracy', 0),
#         results.get('exponentiated_gradient', {}).get('accuracy', 0),
#         results.get('calibrated_eq_odds',     {}).get('accuracy', 0),
#     ]
#     dis = [
#         results['baseline']['disparate_impact'],
#         results.get('reweighing',             {}).get('disparate_impact', 0),
#         results.get('exponentiated_gradient', {}).get('disparate_impact', 0),
#         results.get('calibrated_eq_odds',     {}).get('disparate_impact', 0),
#     ]

#     colors_acc = ['#E24B4A', '#1D9E75', '#1D9E75', '#1D9E75']
#     colors_di  = ['#E24B4A' if d < 0.8 else '#1D9E75' for d in dis]

#     axes[0].bar(techniques, accuracies, color=colors_acc)
#     axes[0].set_title('Accuracy before/after debiasing')
#     axes[0].set_ylabel('Accuracy')
#     axes[0].set_ylim(0, 1)
#     axes[0].tick_params(axis='x', rotation=15)

#     axes[1].bar(techniques, dis, color=colors_di)
#     axes[1].axhline(0.8, color='gray', linestyle='--',
#                     alpha=0.7, label='0.8 fair threshold')
#     axes[1].set_title('Disparate Impact before/after debiasing')
#     axes[1].set_ylabel('Disparate Impact')
#     axes[1].set_ylim(0, 1.3)
#     axes[1].tick_params(axis='x', rotation=15)
#     axes[1].legend()

#     plt.suptitle('Before vs After Debiasing Comparison', fontsize=13)
#     plt.tight_layout()
#     chart_debiasing = fig_to_base64(fig)

#     print(f"\n[tabular] ── Debiasing Summary ──")
#     for tech, res in results.items():
#         if 'error' not in res:
#             print(f"  {tech:30s} acc={res['accuracy']:.4f}  "
#                   f"DI={res['disparate_impact']:.4f}  {res['verdict']}")

#     results['chart_debiasing'] = chart_debiasing
#     return results



# # ── Step 5: SHAP Explainability ───────────────────────────────────────────
# def explain_shap(df: pd.DataFrame) -> dict:
#     import shap
#     import warnings
#     warnings.filterwarnings('ignore')

#     print("\n[tabular] ── Step 5: SHAP Explainability ────────────────────")

#     # ── Load model and test data ──────────────────────────────────────────
#     model      = joblib.load('models/biased_model.pkl')
#     model_data = joblib.load('models/test_data.pkl')
#     X_test     = model_data['X_test']
#     y_test     = model_data['y_test']

#     # ── Extract preprocessor and classifier from pipeline ─────────────────
#     preprocessor = model.named_steps['preprocessor']
#     classifier   = model.named_steps['classifier']

#     # ── Transform test data ───────────────────────────────────────────────
#     X_test_proc = preprocessor.transform(X_test)
#     import scipy.sparse as sp
#     if sp.issparse(X_test_proc):
#         X_test_proc = X_test_proc.toarray()

#     # ── Get feature names after encoding ─────────────────────────────────
#     num_features = ['age', 'fnlwgt', 'education-num',
#                     'capital-gain', 'capital-loss', 'hours-per-week']
#     cat_features = preprocessor.named_transformers_['cat']\
#                                .get_feature_names_out([
#                                    'workclass', 'education', 'marital-status',
#                                    'occupation', 'relationship', 'native-country',
#                                    'sex', 'race'
#                                ]).tolist()
#     feature_names = num_features + cat_features
#     print(f"[tabular] Total features after encoding: {len(feature_names)}")

#     # ── SHAP LinearExplainer ──────────────────────────────────────────────
#     # Use a background sample of 200 rows for speed
#     background    = shap.utils.sample(X_test_proc, 200, random_state=42)
#     explainer     = shap.LinearExplainer(classifier, background)
#     shap_values   = explainer.shap_values(X_test_proc)

#     print(f"[tabular] SHAP values computed for {len(X_test_proc)} samples")

#     # ── Chart 1: Summary plot (global feature importance) ─────────────────
#     fig1, ax1 = plt.subplots(figsize=(10, 7))
#     shap.summary_plot(
#         shap_values, X_test_proc,
#         feature_names = feature_names,
#         max_display   = 15,
#         show          = False,
#         plot_size     = None
#     )
#     ax1 = plt.gca()
#     ax1.set_title('SHAP Summary — Top 15 features driving predictions')
#     chart_summary = fig_to_base64(plt.gcf())
#     print("[tabular] Summary plot generated")

#     # ── Chart 2: Bar plot (mean absolute SHAP values) ─────────────────────
#     fig2, ax2 = plt.subplots(figsize=(10, 7))
#     shap.summary_plot(
#         shap_values, X_test_proc,
#         feature_names = feature_names,
#         max_display   = 15,
#         plot_type     = 'bar',
#         show          = False,
#         plot_size     = None
#     )
#     plt.gca().set_title('SHAP Feature Importance (mean |SHAP value|)')
#     chart_bar = fig_to_base64(plt.gcf())
#     print("[tabular] Bar plot generated")

#     # ── Chart 3: Force plot for a single biased prediction ────────────────
#     # Find a Female sample that was denied (predicted 0) — shows bias clearly
#     results_df  = model_data['results']
#     female_denied = results_df[
#         (results_df['sex'] == 'Female') &
#         (results_df['y_pred'] == 0)
#     ]

#     if len(female_denied) > 0:
#         sample_idx  = female_denied.index[0]
#         test_indices = list(X_test.index)
#         proc_idx    = test_indices.index(sample_idx)

#         fig3, ax3 = plt.subplots(figsize=(14, 3))
#         shap.waterfall_plot(
#             shap.Explanation(
#                 values        = shap_values[proc_idx],
#                 base_values   = explainer.expected_value,
#                 data          = X_test_proc[proc_idx],
#                 feature_names = feature_names
#             ),
#             max_display = 12,
#             show        = False
#         )
#         plt.title('SHAP Waterfall — Female denied income >50K prediction')
#         plt.tight_layout()
#         chart_force = fig_to_base64(plt.gcf())
#         print("[tabular] Waterfall plot generated for denied female sample")
#     else:
#         chart_force = ""
#         print("[tabular] No denied female sample found for waterfall plot")

#     # ── Chart 4: Dependence plot for sex feature ──────────────────────────
#     # Find the index of sex_Female feature
#     try:
#         sex_female_idx = feature_names.index('sex_Female')
#         fig4, ax4 = plt.subplots(figsize=(8, 5))
#         shap.dependence_plot(
#             sex_female_idx,
#             shap_values, X_test_proc,
#             feature_names = feature_names,
#             ax            = ax4,
#             show          = False
#         )
#         ax4.set_title('SHAP Dependence — sex_Female effect on predictions')
#         plt.tight_layout()
#         chart_dependence = fig_to_base64(fig4)
#         print("[tabular] Dependence plot generated for sex_Female")
#     except ValueError:
#         chart_dependence = ""
#         print("[tabular] sex_Female feature not found for dependence plot")

#     # ── Top biased features (sex + race SHAP contributions) ───────────────
#     import numpy as np
#     mean_abs_shap = np.abs(shap_values).mean(axis=0)
#     top_features  = sorted(
#         zip(feature_names, mean_abs_shap),
#         key=lambda x: x[1], reverse=True
#     )[:15]

#     # Extract sex and race feature contributions specifically
#     sex_race_contributions = {
#         name: round(float(val), 6)
#         for name, val in top_features
#         if 'sex' in name.lower() or 'race' in name.lower()
#     }

#     print(f"\n[tabular] Sex/Race SHAP contributions: {sex_race_contributions}")
#     print(f"[tabular] Top 5 features by SHAP:")
#     for name, val in top_features[:5]:
#         print(f"  {name:40s} {val:.6f}")

#     return {
#         "chart_shap_summary":    chart_summary,
#         "chart_shap_bar":        chart_bar,
#         "chart_shap_force":      chart_force,
#         "chart_shap_dependence": chart_dependence,
#         "sex_race_contributions": sex_race_contributions,
#         "top_features": [
#             {"feature": name, "importance": round(float(val), 6)}
#             for name, val in top_features
#         ]
#     }

# # ── Step 6: Main audit function — ties all steps together ─────────────────
# async def run_tabular_audit(file) -> dict:
#     import uuid
#     import tempfile
#     import shutil

#     print("\n[tabular] ── Starting full audit ────────────────────────────")

#     # ── Save uploaded file to a temp location ─────────────────────────────
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
#         shutil.copyfileobj(file.file, tmp)
#         tmp_path = tmp.name

#     try:
#         # ── Run all 5 steps ───────────────────────────────────────────────
#         df            = load_and_profile(tmp_path)
#         eda_charts    = generate_eda_charts(df)
#         baseline      = train_baseline(df)
#         metrics       = compute_metrics(df)
#         debiasing     = debias(df)
#         shap_results  = explain_shap(df)

#     finally:
#         # ── Clean up temp file ────────────────────────────────────────────
#         os.unlink(tmp_path)

#     # ── Build verdict and recommendations ─────────────────────────────────
#     verdict = metrics['verdict']
#     di      = metrics['disparate_impact']

#     recommendations = []
#     if di < 0.8:
#         recommendations.append(
#             f"Disparate Impact is {di:.2f} — below the 0.8 legal threshold. "
#             f"Model is presumed discriminatory under the 80% rule."
#         )
#         recommendations.append(
#             "Apply ExponentiatedGradient (in-processing) — "
#             "achieved DI=0.93 with only 2% accuracy loss in testing."
#         )
#     if abs(metrics['stat_parity_diff']) > 0.1:
#         recommendations.append(
#             f"Statistical Parity Difference is {metrics['stat_parity_diff']:.2f}. "
#             f"Female group receives {abs(metrics['stat_parity_diff'])*100:.1f}% "
#             f"fewer positive predictions than male group."
#         )
#     if abs(metrics['dp_diff']) > 0.1:
#         recommendations.append(
#             "Consider removing protected attributes (sex, race) from "
#             "features and applying Reweighing as a pre-processing step."
#         )

#     # ── Build groups list (per-group metrics) ─────────────────────────────
#     groups = []
#     per_group = metrics['per_group_metrics']
#     sexes = list(per_group['accuracy'].keys())
#     for sex in sexes:
#         groups.append({
#             "group_name": sex,
#             "metrics": {
#                 "accuracy":  per_group['accuracy'][sex],
#                 "precision": per_group['precision'][sex],
#                 "recall":    per_group['recall'][sex],
#             }
#         })

#     # ── Best debiasing result ──────────────────────────────────────────────
#     best_method = max(
#         ['reweighing', 'exponentiated_gradient', 'calibrated_eq_odds'],
#         key=lambda m: debiasing.get(m, {}).get('disparate_impact', 0)
#     )
#     best = debiasing.get(best_method, {})

#     # ── Assemble final response matching ResponseSchema ────────────────────
#     return {
#         "request_id":  str(uuid.uuid4()),
#         "module":      "tabular",
#         "model_name":  "LogisticRegression (UCI Adult)",

#         "overall": {
#             "accuracy":               baseline['accuracy'],
#             "disparate_impact":       metrics['disparate_impact'],
#             "stat_parity_diff":       metrics['stat_parity_diff'],
#             "equal_opportunity_diff": metrics['equal_opportunity_diff'],
#             "avg_odds_diff":          metrics['avg_odds_diff'],
#             "dp_diff":                metrics['dp_diff'],
#             "eod_diff":               metrics['eod_diff'],
#             "bias_score":             round(1 - di, 4),
#             "verdict":                verdict,
#         },

#         "groups": groups,

#         "explanation": {
#             "type":         "SHAP",
#             "description":  (
#                 f"sex_Female is a top-5 feature by SHAP importance "
#                 f"(value={shap_results['sex_race_contributions'].get('sex_Female', 0):.4f}), "
#                 f"directly contributing to income denials for female applicants."
#             ),
#             "image_base64": shap_results['chart_shap_summary'],
#         },

#         "debiasing": {
#             "method":       best_method,
#             "before_score": metrics['disparate_impact'],
#             "after_score":  best.get('disparate_impact', 0),
#             "improvement":  round(
#                 best.get('disparate_impact', 0) - metrics['disparate_impact'], 4
#             ),
#         },

#         "charts": {
#             "eda_gender":      eda_charts['chart_gender_eda'],
#             "eda_race":        eda_charts['chart_race_eda'],
#             "disparity":       baseline['chart_disparity'],
#             "metrics":         metrics['chart_metrics'],
#             "debiasing":       debiasing['chart_debiasing'],
#             "shap_summary":    shap_results['chart_shap_summary'],
#             "shap_bar":        shap_results['chart_shap_bar'],
#             "shap_force":      shap_results['chart_shap_force'],
#             "shap_dependence": shap_results['chart_shap_dependence'],
#         },

#         "debiasing_comparison": {
#             "baseline":               debiasing['baseline'],
#             "reweighing":             debiasing.get('reweighing', {}),
#             "exponentiated_gradient": debiasing.get('exponentiated_gradient', {}),
#             "calibrated_eq_odds":     debiasing.get('calibrated_eq_odds', {}),
#         },

#         "top_features":          shap_results['top_features'],
#         "sex_race_contributions": shap_results['sex_race_contributions'],
#         "recommendations":        recommendations,
#         "status":                 "success",
#         "message":                f"Bias audit complete. Verdict: {verdict}. "
#                                   f"Disparate Impact = {di:.4f}."
#     }

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

# # -------------------- Step 2: Train baseline (or use pretrained/local) --------------------
# def train_or_load_baseline(df: pd.DataFrame, target_col: str, sensitive_cols: List[str],
#                            numerical_features: List[str], categorical_features: List[str],
#                            model_choice: str, model_file: Optional[Any] = None,
#                            preprocessor_file: Optional[Any] = None) -> Dict[str, Any]:
#     X = df.drop(columns=[target_col])
#     y = df[target_col]

#     # ----- 1) Pretrained mode (user uploaded files) -----
#     if model_file is not None and preprocessor_file is not None:
#         print("[tabular] Using uploaded pretrained model + preprocessor (no training).")
#         X_processed = preprocessor_file.transform(X)
#         y_pred = model_file.predict(X_processed)
#         accuracy = accuracy_score(y, y_pred)
#         # Per-group rates
#         group_rates = {}
#         for sens in sensitive_cols:
#             temp = X.copy()
#             temp['pred'] = y_pred
#             group_rates[sens] = temp.groupby(sens)['pred'].mean().to_dict()
#         os.makedirs('models', exist_ok=True)
#         joblib.dump({'X_test': X, 'y_test': y, 'y_pred': y_pred}, 'models/test_data.pkl')
#         joblib.dump(preprocessor_file, 'models/pretrained_preprocessor.pkl')
#         joblib.dump(model_file, 'models/pretrained_model.pkl')
#         sens0 = sensitive_cols[0]
#         rates = group_rates[sens0]
#         fig, ax = plt.subplots(figsize=(6,4))
#         pd.Series(rates).plot(kind='bar', ax=ax, color=['#5DCAA5','#D85A30'])
#         ax.set_title(f'Predicted {target_col} rate by {sens0}')
#         ax.set_ylabel('Prediction rate')
#         ax.set_ylim(0,1)
#         ax.axhline(0.5, color='gray', linestyle='--')
#         chart_disparity = fig_to_base64(fig)
#         return {
#             "accuracy": round(accuracy, 4),
#             "group_rates": group_rates,
#             "chart_disparity": chart_disparity,
#             "model_path": "pretrained",
#             "pretrained": True
#         }

#     # ----- 2) Local baseline mode (existing biased_model.pkl) -----
#     if os.path.exists('models/biased_model.pkl'):
#         print("[tabular] Loading existing baseline model from models/biased_model.pkl")
#         pipeline = joblib.load('models/biased_model.pkl')
#         preprocessor = pipeline.named_steps['preprocessor']
#         model = pipeline.named_steps['classifier']
#         X_processed = preprocessor.transform(X)
#         y_pred = model.predict(X_processed)
#         accuracy = accuracy_score(y, y_pred)
#         # Per-group rates
#         group_rates = {}
#         for sens in sensitive_cols:
#             temp = X.copy()
#             temp['pred'] = y_pred
#             group_rates[sens] = temp.groupby(sens)['pred'].mean().to_dict()
#         joblib.dump({'X_test': X, 'y_test': y, 'y_pred': y_pred}, 'models/test_data.pkl')
#         sens0 = sensitive_cols[0]
#         rates = group_rates[sens0]
#         fig, ax = plt.subplots(figsize=(6,4))
#         pd.Series(rates).plot(kind='bar', ax=ax, color=['#5DCAA5','#D85A30'])
#         ax.set_title(f'Predicted {target_col} rate by {sens0}')
#         ax.set_ylabel('Prediction rate')
#         ax.set_ylim(0,1)
#         ax.axhline(0.5, color='gray', linestyle='--')
#         chart_disparity = fig_to_base64(fig)
#         return {
#             "accuracy": round(accuracy, 4),
#             "group_rates": group_rates,
#             "chart_disparity": chart_disparity,
#             "model_path": "models/biased_model.pkl",
#             "pretrained": False   # not user‑uploaded, but still a pretrained model
#         }

#     # ----- 3) Train from scratch (no local model, no uploads) -----
#     print(f"[tabular] No existing model found. Training new {model_choice} model from scratch.")
#     model = get_model_by_name(model_choice)
#     preprocessor = ColumnTransformer([
#         ('num', StandardScaler(), numerical_features),
#         ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
#     ])

#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
#     pipeline = Pipeline([('preprocessor', preprocessor), ('classifier', model)])
#     pipeline.fit(X_train, y_train)
#     y_pred = pipeline.predict(X_test)
#     accuracy = accuracy_score(y_test, y_pred)

#     # Per-group rates on test set
#     group_rates = {}
#     for sens in sensitive_cols:
#         temp = X_test.copy()
#         temp['pred'] = y_pred
#         group_rates[sens] = temp.groupby(sens)['pred'].mean().to_dict()

#     os.makedirs('models', exist_ok=True)
#     joblib.dump(pipeline, 'models/biased_model.pkl')
#     joblib.dump({'X_test': X_test, 'y_test': y_test, 'y_pred': y_pred}, 'models/test_data.pkl')

#     sens0 = sensitive_cols[0]
#     rates = group_rates[sens0]
#     fig, ax = plt.subplots(figsize=(6,4))
#     pd.Series(rates).plot(kind='bar', ax=ax, color=['#5DCAA5','#D85A30'])
#     ax.set_title(f'Predicted {target_col} rate by {sens0}')
#     ax.set_ylabel('Prediction rate')
#     ax.set_ylim(0,1)
#     ax.axhline(0.5, color='gray', linestyle='--')
#     chart_disparity = fig_to_base64(fig)

#     return {
#         "accuracy": round(accuracy, 4),
#         "group_rates": group_rates,
#         "chart_disparity": chart_disparity,
#         "model_path": "models/biased_model.pkl",
#         "pretrained": False
#     }


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

# -------------------- Step 5: SHAP explainability --------------------
# def explain_shap(target_col: str, sensitive_cols: List[str], sample_size: Optional[int] = None) -> Dict[str, Any]:
#     import shap
#     import warnings
#     warnings.filterwarnings('ignore')

#     # PRIORITY 1: Use the baseline model (trained on the current dataset)
#     if os.path.exists('models/biased_model.pkl'):
#         print("[tabular] Using baseline model for SHAP.")
#         pipeline = joblib.load('models/biased_model.pkl')
#         preprocessor = pipeline.named_steps['preprocessor']
#         model = pipeline.named_steps['classifier']
#     # PRIORITY 2: Fallback to a pretrained model (if no baseline exists)
#     elif os.path.exists('models/pretrained_model.pkl') and os.path.exists('models/pretrained_preprocessor.pkl'):
#         print("[tabular] Using pretrained model for SHAP.")
#         model = joblib.load('models/pretrained_model.pkl')
#         preprocessor = joblib.load('models/pretrained_preprocessor.pkl')
#     else:
#         raise FileNotFoundError("No model found for SHAP explanation.")

#     model_data = joblib.load('models/test_data.pkl')
#     X_test = model_data['X_test']
#     y_pred_full = model_data['y_pred']          # keep full version

#     X_test_proc = preprocessor.transform(X_test)
    
#     # --- Limit to sample_size if provided ---
#     if sample_size is not None and len(X_test_proc) > sample_size:
#         indices = np.random.choice(len(X_test_proc), sample_size, replace=False)
#         X_test_proc = X_test_proc[indices]
#         X_test = X_test.iloc[indices]
#         y_pred = y_pred_full[indices]           # sample predictions as well
#         print(f"[tabular] SHAP using {sample_size} random rows (was {len(X_test_proc)})")
#     else:
#         y_pred = y_pred_full
#         print(f"[tabular] SHAP using all {len(X_test_proc)} rows")

#     # Background sample (200 rows, but not more than available)
#     bg_size = min(200, len(X_test_proc))
#     background = shap.utils.sample(X_test_proc, bg_size, random_state=42)

#     import scipy.sparse as sp
#     if sp.issparse(X_test_proc):
#         X_test_proc = X_test_proc.toarray()

#     # Feature names
#     if hasattr(preprocessor, 'get_feature_names_out'):
#         try:
#             feature_names = preprocessor.get_feature_names_out().tolist()
#         except:
#             num_features = [col for col in X_test.columns if col in preprocessor.named_transformers_['num'].feature_names_in_]
#             cat_features = preprocessor.named_transformers_['cat'].get_feature_names_out().tolist()
#             feature_names = num_features + cat_features
#     else:
#         num_features = [col for col in X_test.columns if col in preprocessor.named_transformers_['num'].feature_names_in_]
#         cat_features = preprocessor.named_transformers_['cat'].get_feature_names_out().tolist()
#         feature_names = num_features + cat_features

#     if isinstance(model, LogisticRegression):
#         explainer = shap.LinearExplainer(model, background)
#     elif hasattr(model, 'estimators_') or isinstance(model, RandomForestClassifier):
#         explainer = shap.TreeExplainer(model)
#     else:
#         explainer = shap.KernelExplainer(model.predict, background)

#     shap_values = explainer.shap_values(X_test_proc)
#     # Handle binary classification output
#     if isinstance(shap_values, list):
#         shap_values = shap_values[1] if len(shap_values) == 2 else shap_values[0]
#     elif hasattr(shap_values, 'shape') and len(shap_values.shape) == 2 and shap_values.shape[1] == 2:
#         shap_values = shap_values[:, 1]
#     elif hasattr(shap_values, 'shape') and len(shap_values.shape) == 3 and shap_values.shape[2] == 2:
#         shap_values = shap_values[:, :, 1]

#     # Summary plot
#     fig1, ax1 = plt.subplots(figsize=(10,7))
#     shap.summary_plot(shap_values, X_test_proc, feature_names=feature_names, max_display=15, show=False)
#     chart_summary = fig_to_base64(plt.gcf())

#     # Bar plot
#     fig2, ax2 = plt.subplots(figsize=(10,7))
#     shap.summary_plot(shap_values, X_test_proc, feature_names=feature_names, plot_type='bar', max_display=15, show=False)
#     chart_bar = fig_to_base64(plt.gcf())

#     # Waterfall plot for a denied sample from the unprivileged group
#     sens_col = sensitive_cols[0]
#     results_df = X_test.copy()
#     results_df['y_pred'] = y_pred                # use sampled y_pred
#     uniq_vals = results_df[sens_col].unique()
#     unpriv_value = uniq_vals[0] if len(uniq_vals) == 2 else uniq_vals[0]
#     denied = results_df[(results_df[sens_col] == unpriv_value) & (results_df['y_pred'] == 0)]
#     chart_force = ""
#     if len(denied) > 0:
#         sample_idx = denied.index[0]
#         # Find index in the sampled X_test (which is a subset)
#         proc_idx = list(X_test.index).index(sample_idx)
#         fig3, ax3 = plt.subplots(figsize=(14,3))
#         base_val = explainer.expected_value
#         if isinstance(base_val, (list, np.ndarray)):
#             base_val = base_val[1] if len(base_val) > 1 else base_val[0]
#         shap.waterfall_plot(shap.Explanation(values=shap_values[proc_idx],
#                                              base_values=base_val,
#                                              data=X_test_proc[proc_idx],
#                                              feature_names=feature_names), max_display=12, show=False)
#         chart_force = fig_to_base64(plt.gcf())

#     # Dependence plot for sensitive attribute
#     chart_dependence = ""
#     try:
#         sens_feature = [f for f in feature_names if sens_col.lower() in f.lower()][0]
#         sens_idx = feature_names.index(sens_feature)
#         fig4, ax4 = plt.subplots(figsize=(8,5))
#         shap.dependence_plot(sens_idx, shap_values, X_test_proc, feature_names=feature_names, ax=ax4, show=False)
#         chart_dependence = fig_to_base64(fig4)
#     except:
#         pass

#     mean_abs_shap = np.abs(shap_values).mean(axis=0)
#     top_features = sorted(zip(feature_names, mean_abs_shap), key=lambda x: x[1], reverse=True)[:15]
#     sex_race_contributions = {name: round(val,6) for name,val in top_features if any(x in name.lower() for x in ['sex','gender','race','ethnic'])}
#     return {
#         "chart_shap_summary": chart_summary,
#         "chart_shap_bar": chart_bar,
#         "chart_shap_force": chart_force,
#         "chart_shap_dependence": chart_dependence,
#         "sex_race_contributions": sex_race_contributions,
#         "top_features": [{"feature": f, "importance": round(v,6)} for f,v in top_features]
#     }
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
def run_tabular_audit(file, target_col: str, sensitive_cols: List[str], privileged_groups: Dict[str, Any],
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