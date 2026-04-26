import React from "react";
import TabularResults from "./TabularResults";
import { useAudit } from "../../hooks/useAudit";

/* ===== Loading State ===== */
const LoadingState = () => (
  <div className="card p-12 text-center flex flex-col items-center gap-4">
    {/* Controlled spinner */}
    <div className="spinner-icon">⚙️</div>

    <p className="font-semibold text-slate-600 animate-pulse">
      Running Tabular Bias Audit...
    </p>
  </div>
);

/* ===== Idle State ===== */
const TabularIdle = () => (
  <div className="idle-state p-10 text-center">
    <div className="text-4xl mb-4">📊</div>
    <h3 className="font-bold text-lg">Tabular Data Audit</h3>
    <p className="text-slate-500">
      Upload your dataset and configure the audit parameters to get started.
    </p>
  </div>
);

const TabularPanel = () => {
  const { data: results, loading, executeTabular } = useAudit();

  const handleRunAudit = async (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData();

    const csvFile = form.csvFile?.files?.[0];
    if (!csvFile) {
      alert("Please upload a CSV file.");
      return;
    }

    // Validate JSON
    let privValuesSanitized = form.privilegedValues.value;
    try {
      privValuesSanitized = JSON.stringify(
        JSON.parse(form.privilegedValues.value),
      );
    } catch {
      alert('Privileged Group must be valid JSON like {"gender": "Male"}');
      return;
    }

    // SHAP validation
    const shapVal = form.shapSampleSize?.value || "20";
    const shapInt = parseInt(shapVal);
    if (!Number.isFinite(shapInt) || shapInt <= 0) {
      alert("SHAP Sample Size must be a positive number");
      return;
    }

    // Append fields
    formData.append("file", csvFile);
    formData.append("target_column", form.targetColumn.value);
    formData.append("sensitive_columns", form.sensitiveColumn.value);
    formData.append("privileged_values", privValuesSanitized);
    formData.append("model_choice", form.modelChoice.value || "logistic");

    if (form.modelFile.files[0]) {
      formData.append("model_file", form.modelFile.files[0]);
    }

    if (form.preprocessorFile.files[0]) {
      formData.append("preprocessor_file", form.preprocessorFile.files[0]);
    }

    formData.append("shap_sample_size", shapInt);

    try {
      await executeTabular(formData);
    } catch (err) {
      alert("Tabular audit failed.");
    }
  };

  return (
    <div className="dashboard-layout">
      {/* ===== SIDEBAR ===== */}
      <aside className="sidebar">
        <div className="card sidebar-card">
          <form onSubmit={handleRunAudit} className="space-y-6">
            {/* ===== DATASET ===== */}
            <div className="section">
              <div className="card-label">📁 Dataset</div>

              <div className="form-group">
                <label>CSV Dataset</label>
                <input
                  type="file"
                  name="csvFile"
                  accept=".csv"
                  required
                  className="file-upload"
                />
              </div>
            </div>

            {/* ===== CONFIG ===== */}
            <div className="section">
              <div className="card-label">⚙️ Configuration</div>

              <div className="form-group">
                <label>Target Column</label>
                <input
                  type="text"
                  name="targetColumn"
                  placeholder="e.g. hired"
                  required
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label>Sensitive Column</label>
                <input
                  type="text"
                  name="sensitiveColumn"
                  placeholder="gender"
                  required
                  className="input-field"
                />
                <p className="helper-text">e.g. gender, race</p>
              </div>

              <div className="form-group">
                <label>Privileged Group</label>
                <input
                  type="text"
                  name="privilegedValues"
                  placeholder='{"gender":"Male"}'
                  required
                  className="input-field"
                />
                <p className="helper-text">JSON format</p>
              </div>
            </div>

            {/* ===== MODEL ===== */}
            <div className="section">
              <div className="card-label">🧠 Model</div>

              <div className="form-group">
                <label>Base Architecture</label>
                <select name="modelChoice" className="input-field">
                  <option value="logistic">Logistic Regression</option>
                  <option value="randomforest">Random Forest</option>
                </select>
              </div>

              <div className="form-group">
                <label>Pretrained Model (.pkl)</label>
                <input
                  type="file"
                  name="modelFile"
                  accept=".pkl"
                  className="file-upload"
                />
              </div>

              <div className="form-group">
                <label>Preprocessor (.pkl)</label>
                <input
                  type="file"
                  name="preprocessorFile"
                  accept=".pkl"
                  className="file-upload"
                />
              </div>

              <div className="form-group">
                <label>SHAP Sample Size</label>
                <input
                  type="number"
                  name="shapSampleSize"
                  defaultValue={20}
                  className="input-field"
                />
              </div>
            </div>

            {/* ===== BUTTON ===== */}
            <button type="submit" className="btn-run w-full" disabled={loading}>
              {loading ? "⏳ Running..." : "🚀 Run Audit"}
            </button>
          </form>
        </div>
      </aside>

      {/* ===== MAIN ===== */}
      <main className="main-content">
        {loading ? (
          <LoadingState />
        ) : results ? (
          <TabularResults data={results} />
        ) : (
          <TabularIdle />
        )}
      </main>
    </div>
  );
};

export default TabularPanel;
