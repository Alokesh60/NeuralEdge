import React, { useState } from "react";

const NLPSidebar = ({
  onRun,
  onCompare,
  loading,
  comparisonComplete,
  apiStatus,
}) => {
  const models = [
    {
      id: "bert-base-uncased",
      name: "bert-base-uncased",
      info: "110M params · BERT · Pre-trained on BookCorpus & Wikipedia",
    },
    {
      id: "roberta-base",
      name: "roberta-base",
      info: "125M params · RoBERTa · Robust optimized BERT variant",
    },
    {
      id: "distilbert-base-uncased",
      name: "distilbert-base-uncased",
      info: "66M params · DistilBERT · 40% smaller, 97% of BERT quality",
    },
  ];

  const demographics = [
    { id: "Gender", label: "Gender" },
    { id: "Race", label: "Race" },
    { id: "Religion", label: "Religion" },
  ];

  const benchmarks = [
    { id: "winobias", label: "WinoBias" },
    { id: "sentiment", label: "Sentiment Parity" },
    { id: "toxicity", label: "Toxicity" },
  ];

  const [selectedModel, setSelectedModel] = useState(models[0]);
  const [selectedBenchmarks, setSelectedBenchmarks] = useState([
    "winobias",
    "sentiment",
    "toxicity",
  ]);
  const [selectedDemographics, setSelectedDemographics] = useState([
    "Gender",
    "Race",
    "Religion",
  ]);

  const selectedModelInfo = selectedModel?.info ?? "";

  const toggleWithGuard = (setState) => (id) => {
    setState((prev) => {
      const exists = prev.includes(id);
      if (exists) return prev.length > 1 ? prev.filter((x) => x !== id) : prev;
      return [...prev, id];
    });
  };

  const toggleBenchmark = toggleWithGuard(setSelectedBenchmarks);
  const toggleDemographic = toggleWithGuard(setSelectedDemographics);

  const canRun =
    !loading && selectedBenchmarks.length > 0 && selectedDemographics.length > 0;

  const handleRun = () => {
    onRun?.(selectedModel.id, selectedBenchmarks, selectedDemographics);
  };

  const handleCompare = () => {
    onCompare?.({
      benchmarks: selectedBenchmarks,
      demographicGroups: selectedDemographics,
    });
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div className="card" style={{ marginBottom: 0 }}>
        <span className="card-label">Step 1 — Select Model</span>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {models.map((model) => (
            <button
              key={model.id}
              type="button"
              onClick={() => setSelectedModel(model)}
              className={`nlp-model-chip chip ${selectedModel.id === model.id ? "active" : ""}`}
            >
              🤗 {model.name}
            </button>
          ))}
        </div>

        <div
          style={{
            marginTop: "0.75rem",
            padding: "0.625rem 0.875rem",
            background: "var(--primary-light)",
            borderRadius: "var(--radius-md)",
            fontSize: "0.73rem",
            color: "var(--primary)",
            fontWeight: 500,
            lineHeight: 1.5,
          }}
        >
          {selectedModelInfo}
        </div>
      </div>

      <div className="card" style={{ marginBottom: 0 }}>
        <span className="card-label">Step 2 — Demographic Groups</span>
        <p
          style={{
            fontSize: "0.72rem",
            color: "var(--text-muted)",
            marginBottom: "0.5rem",
            fontWeight: 600,
          }}
        >
          DEMOGRAPHIC GROUPS
        </p>
        <div className="chip-group" style={{ marginBottom: 0 }}>
          {demographics.map((d) => (
            <div
              key={d.id}
              role="button"
              tabIndex={0}
              onClick={() => toggleDemographic(d.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") toggleDemographic(d.id);
              }}
              className={`chip ${selectedDemographics.includes(d.id) ? "active" : ""}`}
              style={{ cursor: "pointer", userSelect: "none" }}
            >
              {d.label}
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginBottom: 0 }}>
        <span className="card-label">Step 3 — Bias Tests</span>
        <p
          style={{
            fontSize: "0.72rem",
            color: "var(--text-muted)",
            marginBottom: "0.5rem",
            fontWeight: 600,
          }}
        >
          ACTIVE BENCHMARKS
        </p>
        <div className="chip-group" style={{ marginBottom: "1rem" }}>
          {benchmarks.map((b) => (
            <div
              key={b.id}
              role="button"
              tabIndex={0}
              onClick={() => toggleBenchmark(b.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") toggleBenchmark(b.id);
              }}
              className={`chip ${selectedBenchmarks.includes(b.id) ? "active" : ""}`}
              style={{ cursor: "pointer", userSelect: "none" }}
            >
              {b.label}
            </div>
          ))}
        </div>

        <button
          type="button"
          className="btn-run"
          onClick={handleRun}
          disabled={!canRun}
        >
          {loading ? (
            <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
              <span className="spinning" aria-hidden="true">
                ⚙️
              </span>
              Auditing…
            </span>
          ) : (
            "▶ Run NLP Audit"
          )}
        </button>

        <button
          type="button"
          className="btn-compare"
          onClick={handleCompare}
          disabled={!canRun}
        >
          ⚖ Compare All 3 Models
        </button>

        {apiStatus?.message && (
          <div
            className={
              apiStatus.type === "success"
                ? "api-status-success"
                : apiStatus.type === "error"
                  ? "api-status-error"
                  : "api-status-info"
            }
            style={{
              marginTop: "0.875rem",
              padding: "0.5rem 0.875rem",
              borderRadius: "var(--radius-md)",
              fontSize: "0.75rem",
              fontWeight: 500,
            }}
          >
            {apiStatus.message}
          </div>
        )}

        {comparisonComplete && (
          <div
            className="api-status-success"
            style={{
              marginTop: "0.875rem",
              padding: "0.5rem 0.875rem",
              borderRadius: "var(--radius-md)",
              fontSize: "0.75rem",
              fontWeight: 500,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <input type="checkbox" checked readOnly /> Comparison complete — all 3
            models audited
          </div>
        )}
      </div>
    </div>
  );
};

export default NLPSidebar;
