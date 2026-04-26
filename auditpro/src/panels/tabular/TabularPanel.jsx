import React, { useState } from "react";
import TabularResults from "./TabularResults";
import { useAudit } from "../../hooks/useAudit";

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
  const { data: results, loading, error, executeTabular } = useAudit();

  const handleRunAudit = async (e) => {
    e.preventDefault();

    // Hoisting fix: define these before any reads/logic
    const form = e.target;
    const formData = new FormData();

    const csvFile = form.csvFile?.files?.[0];
    if (!csvFile) {
      alert("Please upload a CSV file.");
      return;
    }

    // Validate JSON and sanitize before appending
    const privValuesRaw = form.privilegedValues.value;
    let privValuesSanitized = privValuesRaw;
    try {
      const parsed = JSON.parse(privValuesRaw);
      privValuesSanitized = JSON.stringify(parsed);
    } catch (err) {
      alert('Privileged Group must be valid JSON like {"sex": "Male"}');
      return;
    }

    // SHAP sample size: backend expects a non-null integer to init SHAP explainer.
    // If empty, default to 20; if invalid, block submission.
    const shapRaw = `${form.shapSampleSize?.value ?? ""}`.trim();
    const shapFinal = shapRaw === "" ? "20" : shapRaw;
    const shapSampleSizeInt = Number.parseInt(shapFinal, 10);
    if (!Number.isFinite(shapSampleSizeInt) || shapSampleSizeInt <= 0) {
      alert("SHAP Sample Size must be a positive integer (e.g., 20).");
      return;
    }

    // 1. Mandatory Dataset & Metadata
    formData.append("file", csvFile);
    formData.append("target_column", form.targetColumn.value);
    formData.append("sensitive_columns", form.sensitiveColumn.value); // plural key required by FastAPI
    formData.append("privileged_values", privValuesSanitized);

    // Value alignment: always send model_choice (backend expects it),
    // even when model_file / preprocessor_file are provided (it will be ignored server-side).
    formData.append("model_choice", form.modelChoice.value || "logistic");

    // 2. Pretrained Mode Files (Optional)
    if (form.modelFile.files[0]) {
      formData.append("model_file", form.modelFile.files[0]);
    }
    if (form.preprocessorFile.files[0]) {
      formData.append("preprocessor_file", form.preprocessorFile.files[0]);
    }

    // Backend key is snake_case
    formData.append("shap_sample_size", String(shapSampleSizeInt));

    try {
      await executeTabular(formData);
    } catch (error) {
      alert(error?.message || "Tabular audit failed.");
    }
  };

  return (
    <div className="dashboard tabular-container flex gap-6 p-4">
      <aside className="sidebar card w-1/3 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
        <form onSubmit={handleRunAudit} className="space-y-4">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
            1. Upload & Configure
          </span>

          <div className="form-group flex flex-col gap-1">
            <label className="text-sm font-semibold">CSV Dataset</label>
            <input
              type="file"
              name="csvFile"
              accept=".csv"
              required
              className="text-sm"
            />
          </div>

          <div className="form-group flex flex-col gap-1">
            <label className="text-sm font-semibold">Target Column</label>
            <input
              type="text"
              name="targetColumn"
              placeholder="e.g. income"
              className="border p-2 rounded text-sm"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="form-group flex flex-col gap-1">
              <label className="text-sm font-semibold">Sensitive Col</label>
              <input
                type="text"
                name="sensitiveColumn"
                placeholder="sex"
                className="border p-2 rounded text-sm"
                required
              />
            </div>
            <div className="form-group flex flex-col gap-1">
              <label className="text-sm font-semibold">Privileged Group</label>
              <input
                type="text"
                name="privilegedValues"
                placeholder='{"sex":"Male"}'
                className="border p-2 rounded text-sm"
                required
              />
            </div>
          </div>

          <span className="text-xs font-bold text-slate-400 uppercase tracking-widest block mt-4">
            2. Model Selection
          </span>
          <div className="form-group flex flex-col gap-1">
            <label className="text-sm font-semibold">Base Architecture</label>
            <select name="modelChoice" className="border p-2 rounded text-sm">
              <option value="logistic">Logistic Regression</option>
              <option value="randomforest">Random Forest</option>
            </select>
          </div>

          <div className="form-group border-t pt-4 border-slate-100 flex flex-col gap-1">
            <label className="text-sm font-bold text-indigo-600">
              Pretrained Model (.pkl)
            </label>
            <input
              type="file"
              name="modelFile"
              accept=".pkl"
              className="text-xs"
            />
          </div>
          <div className="form-group flex flex-col gap-1">
            <label className="text-sm font-bold text-indigo-600">
              Preprocessor (.pkl)
            </label>
            <input
              type="file"
              name="preprocessorFile"
              accept=".pkl"
              className="text-xs"
            />
          </div>

          <div className="form-group flex flex-col gap-1 mt-2">
            <label className="text-sm font-semibold text-slate-600">
              SHAP Sample Size (Optional)
            </label>
            <input
              type="number"
              name="shapSampleSize"
              placeholder="e.g. 20"
              className="border p-2 rounded text-sm"
              defaultValue={20}
              min={1}
            />
            <p className="text-[10px] text-slate-400 italic">
              Leaving this empty may cause a 400 error on some backends.
            </p>
          </div>

          <button
            type="submit"
            className="w-full bg-indigo-600 text-white font-bold py-3 rounded-lg hover:bg-indigo-700 disabled:bg-slate-300 transition-colors"
            disabled={loading}
          >
            {loading ? "⏳ Processing..." : "🚀 Run Tabular Audit"}
          </button>
        </form>
      </aside>

      <main className="results-area w-2/3">
        {error && (
          <div className="api-status-error" style={{ marginBottom: "1rem", padding: "0.75rem 1rem", borderRadius: "var(--radius-md)" }}>
            {error}
          </div>
        )}
        {results ? <TabularResults data={results} /> : <TabularIdle />}
      </main>
    </div>
  );
};

export default TabularPanel;
