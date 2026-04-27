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

/** Styled file button that matches the rest of the UI */
const FileUploadButton = ({
  label,
  accept,
  file,
  onChange,
  disabled,
  icon = "📎",
}) => (
  <label
    className="file-upload-btn"
    style={{
      display: "flex",
      alignItems: "center",
      gap: "8px",
      background: "var(--bg2, #f1efe8)",
      border: "1.5px dashed var(--color-border-secondary, rgba(0,0,0,0.2))",
      borderRadius: "8px",
      padding: "8px 12px",
      fontSize: "12px",
      color: "var(--color-text-secondary, #73726c)",
      cursor: disabled ? "not-allowed" : "pointer",
      width: "100%",
      overflow: "hidden",
      opacity: disabled ? 0.5 : 1,
    }}
  >
    <span style={{ fontSize: "14px", flexShrink: 0 }}>{icon}</span>
    <span
      style={{
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
        flex: 1,
      }}
    >
      {file ? file.name : label}
    </span>
    <input
      type="file"
      accept={accept}
      onChange={onChange}
      disabled={disabled}
      style={{ display: "none" }}
    />
  </label>
);

const SectionDivider = () => (
  <hr
    style={{
      border: "none",
      borderTop: "1px solid var(--color-border-tertiary, rgba(0,0,0,0.1))",
      margin: "14px 0",
    }}
  />
);

const FieldLabel = ({ children }) => (
  <label
    style={{
      fontSize: "10px",
      fontWeight: 500,
      letterSpacing: "0.07em",
      color: "var(--color-text-secondary, #73726c)",
      textTransform: "uppercase",
    }}
  >
    {children}
  </label>
);

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

    let privilegedSanitized = config.privileged_values;
    try {
      privilegedSanitized = JSON.stringify(
        JSON.parse(config.privileged_values),
      );
    } catch {
      setLocalError('Privileged Group must be valid JSON like {"sex":"Male"}');
      return;
    }

    // Clamp SHAP between 1 and 20
    let shapInt = Number.parseInt(String(config.shap_sample_size || ""), 10);
    if (!Number.isFinite(shapInt) || shapInt <= 0) {
      setLocalError("SHAP Sample Size must be a positive number.");
      return;
    }
    shapInt = Math.min(shapInt, 20);

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
        {/* ── Dataset ── */}
        <div className="input-group">
          <FieldLabel>CSV Dataset</FieldLabel>
          <FileUploadButton
            label="📂 Upload CSV Dataset"
            accept=".csv,text/csv"
            file={files.dataset}
            onChange={(e) => setFile("dataset", e.target.files?.[0])}
            disabled={loading}
            icon="📂"
          />
        </div>

        <SectionDivider />

        {/* ── Columns ── */}
        <span className="card-label" style={{ display: "block" }}>
          Columns
        </span>

        <div className="input-group">
          <FieldLabel>Target column (label)</FieldLabel>
          <input
            className="chip active w-full"
            value={config.target_column}
            onChange={(e) => setCfg({ target_column: e.target.value })}
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <FieldLabel>Sensitive columns (comma separated)</FieldLabel>
          <input
            className="chip active w-full"
            value={config.sensitive_columns}
            onChange={(e) => setCfg({ sensitive_columns: e.target.value })}
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <FieldLabel>Privileged group (JSON)</FieldLabel>
          <input
            className="chip active w-full"
            value={config.privileged_values}
            onChange={(e) => setCfg({ privileged_values: e.target.value })}
            disabled={loading}
            spellCheck={false}
            placeholder='{"sex": "Male"}'
          />
        </div>

        <SectionDivider />

        {/* ── Model ── */}
        <span className="card-label" style={{ display: "block" }}>
          Model
        </span>

        <div className="input-group">
          <FieldLabel>Base architecture</FieldLabel>
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
          <FieldLabel>Pretrained model (.pkl, optional)</FieldLabel>
          <FileUploadButton
            label="Choose .pkl file..."
            accept=".pkl"
            file={files.model}
            onChange={(e) => setFile("model", e.target.files?.[0])}
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <FieldLabel>Preprocessor (.pkl, optional)</FieldLabel>
          <FileUploadButton
            label="Choose .pkl file..."
            accept=".pkl"
            file={files.preprocessor}
            onChange={(e) => setFile("preprocessor", e.target.files?.[0])}
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <FieldLabel>
            SHAP sample size{" "}
            <span
              style={{
                fontWeight: 400,
                textTransform: "none",
                letterSpacing: 0,
              }}
            >
              (max 20)
            </span>
          </FieldLabel>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <input
              type="number"
              min={1}
              max={20}
              className="chip active"
              style={{ width: "72px", textAlign: "center", flexShrink: 0 }}
              value={config.shap_sample_size}
              onChange={(e) => {
                let v = Number.parseInt(e.target.value, 10);
                if (isNaN(v) || v < 1) v = 1;
                if (v > 20) v = 20;
                setCfg({ shap_sample_size: v });
              }}
              disabled={loading}
            />
            <span
              style={{
                fontSize: "11px",
                color: "var(--color-text-tertiary, #888)",
                lineHeight: 1.4,
              }}
            >
              Samples used for SHAP explainability
            </span>
          </div>
        </div>

        {localError && (
          <div
            style={{
              color: "var(--danger, #ef4444)",
              fontWeight: 600,
              fontSize: "12px",
            }}
          >
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
