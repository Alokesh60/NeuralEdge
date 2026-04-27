import React, { useState } from "react";

const DEFAULT_CONFIG = {
  target_column: "income",
  sensitive_columns: "sex",
  privileged_values: '{"sex":"Male"}',
  model_choice: "logistic",
  shap_sample_size: 20,
};

const isLikelyCsv = (file) => {
  if (!file) return false;
  const name = String(file.name || "").toLowerCase();
  return file.type === "text/csv" || name.endsWith(".csv");
};

const TabularSidebar = ({ onRun, onReset, loading }) => {
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [files, setFiles] = useState({
    dataset: null,
    model: null,
    preprocessor: null,
  });
  const [localError, setLocalError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError(null);

    if (!files.dataset) {
      setLocalError("Please upload a CSV file.");
      return;
    }
    if (!isLikelyCsv(files.dataset)) {
      setLocalError("Invalid file type. Please upload a .csv dataset.");
      return;
    }

    // Replace the privileged_values sanitization block in handleSubmit:

    let privilegedSanitized;
    try {
      const parsed = JSON.parse(config.privileged_values);

      // Normalize: wrap any scalar values into arrays
      // e.g. {"sex": "Male"} → {"sex": ["Male"]}
      // e.g. {"sex": ["Male"]} → stays as-is
      const normalized = Object.fromEntries(
        Object.entries(parsed).map(([k, v]) => [k, Array.isArray(v) ? v : [v]]),
      );

      privilegedSanitized = JSON.stringify(normalized);
    } catch {
      setLocalError('Privileged Group must be valid JSON like {"sex":"Male"}');
      return;
    }

    const shapInt = Number.parseInt(String(config.shap_sample_size || ""), 10);
    if (!Number.isFinite(shapInt) || shapInt <= 0) {
      setLocalError("SHAP Sample Size must be a positive number.");
      return;
    }

    const target = String(config.target_column || "").trim();
    const sensitive = String(config.sensitive_columns || "").trim();
    if (!target) {
      setLocalError("Target column is required.");
      return;
    }
    if (!sensitive) {
      setLocalError("Sensitive columns are required.");
      return;
    }

    const formData = new FormData();
    formData.append("file", files.dataset);
    formData.append("target_column", target);
    formData.append("sensitive_columns", sensitive);
    formData.append("privileged_values", privilegedSanitized);
    formData.append("model_choice", config.model_choice || "logistic");

    if (files.model) formData.append("model_file", files.model);
    if (files.preprocessor)
      formData.append("preprocessor_file", files.preprocessor);

    formData.append("shap_sample_size", String(shapInt));

    await onRun?.(formData);
  };

  const setCfg = (patch) => {
    setConfig((prev) => ({ ...prev, ...patch }));
    onReset?.();
  };

  const setFile = (key, file) => {
    setFiles((prev) => ({ ...prev, [key]: file || null }));
    setLocalError(null);
    onReset?.();
  };

  return (
    <div className="card">
      <span className="card-label">Tabular Audit</span>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="upload-area">
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(e) => setFile("dataset", e.target.files?.[0])}
            required
            disabled={loading}
          />
          <p className="file-size text-muted">CSV Dataset</p>
        </div>

        <span
          className="card-label"
          style={{ marginTop: "1rem", display: "block" }}
        >
          Columns
        </span>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">
            TARGET COLUMN (LABEL)
          </label>
          <input
            className="chip active w-full"
            value={config.target_column}
            onChange={(e) => setCfg({ target_column: e.target.value })}
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">
            SENSITIVE COLUMNS (comma separated)
          </label>
          <input
            className="chip active w-full"
            value={config.sensitive_columns}
            onChange={(e) => setCfg({ sensitive_columns: e.target.value })}
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">
            PRIVILEGED GROUP (JSON)
          </label>
          <input
            className="chip active w-full"
            value={config.privileged_values}
            onChange={(e) => setCfg({ privileged_values: e.target.value })}
            disabled={loading}
            spellCheck={false}
            placeholder='{"sex":"Male"}'
          />
        </div>

        <span
          className="card-label"
          style={{ marginTop: "1rem", display: "block" }}
        >
          Model
        </span>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">
            BASE ARCHITECTURE
          </label>
          <select
            className="chip active w-full"
            value={config.model_choice}
            onChange={(e) => setCfg({ model_choice: e.target.value })}
            disabled={loading}
          >
            <option value="logistic">Logistic Regression</option>
            <option value="randomforest">Random Forest</option>
          </select>
        </div>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">
            PRETRAINED MODEL (.pkl, optional)
          </label>
          <input
            type="file"
            accept=".pkl"
            onChange={(e) => setFile("model", e.target.files?.[0])}
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">
            PREPROCESSOR (.pkl, optional)
          </label>
          <input
            type="file"
            accept=".pkl"
            onChange={(e) => setFile("preprocessor", e.target.files?.[0])}
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">
            SHAP SAMPLE SIZE
          </label>
          <input
            type="number"
            min={1}
            className="chip active w-full"
            value={config.shap_sample_size}
            onChange={(e) => setCfg({ shap_sample_size: e.target.value })}
            disabled={loading}
          />
        </div>

        {localError && (
          <div style={{ color: "var(--danger, #ef4444)", fontWeight: 600 }}>
            ⚠ {localError}
          </div>
        )}

        <button
          type="submit"
          className="btn-run"
          disabled={loading || !files.dataset}
        >
          {loading ? "Processing..." : "▶ Run Tabular Audit"}
        </button>
      </form>
    </div>
  );
};

export default TabularSidebar;
