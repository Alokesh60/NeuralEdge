import React, { useState } from "react";

const TabularSidebar = ({ onRun, loading }) => {
  const [config, setConfig] = useState({
    target_column: "income",
    sensitive_columns: "sex",
    privileged_values: '{"sex": "Male"}',
    model_choice: "logistic",
  });

  const [files, setFiles] = useState({
    dataset: null,
    model: null,
    preprocessor: null,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();

    // Append Files
    if (files.dataset) formData.append("file", files.dataset);
    if (files.model) formData.append("model_file", files.model);
    if (files.preprocessor)
      formData.append("preprocessor_file", files.preprocessor);

    // Append Form Fields
    formData.append("target_column", config.target_column);
    formData.append("sensitive_columns", config.sensitive_columns);
    formData.append("privileged_values", config.privileged_values);
    formData.append("model_choice", config.model_choice);

    onRun(formData);
  };

  return (
    <div className="card">
      <span className="card-label">Step 1 — Data Upload</span>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Dataset Input */}
        <div className="upload-area">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFiles({ ...files, dataset: e.target.files[0] })}
            required
          />
          <p className="file-size text-muted">Primary CSV Dataset</p>
        </div>

        <span
          className="card-label"
          style={{ marginTop: "1rem", display: "block" }}
        >
          Step 2 — Parameters
        </span>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">TARGET COLUMN</label>
          <input
            className="chip active w-full"
            value={config.target_column}
            onChange={(e) =>
              setConfig({ ...config, target_column: e.target.value })
            }
          />
        </div>

        <div className="input-group">
          <label className="text-xs font-bold text-muted">
            SENSITIVE COLS (comma separated)
          </label>
          <input
            className="chip active w-full"
            value={config.sensitive_columns}
            onChange={(e) =>
              setConfig({ ...config, sensitive_columns: e.target.value })
            }
          />
        </div>

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
