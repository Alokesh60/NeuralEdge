import React, { useState } from "react";

const NLPSidebar = ({ onRun, loading }) => {
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

  const benchmarks = [
    { id: "winobias", label: "WinoBias" },
    { id: "sentiment", label: "Sentiment" },
    { id: "toxicity", label: "Toxicity" },
  ];

  const [selectedModel, setSelectedModel] = useState(models[0]);
  // State to track multiple selected benchmarks
  const [selectedBenchmarks, setSelectedBenchmarks] = useState([
    "winobias",
    "sentiment",
    "toxicity",
  ]);

  const toggleBenchmark = (id) => {
    setSelectedBenchmarks(
      (prev) =>
        prev.includes(id)
          ? prev.filter((item) => item !== id) // Remove if already there
          : [...prev, id], // Add if not there
    );
  };

  const handleRun = () => {
    // We pass both the model and the selected tests to the parent
    onRun(selectedModel.id, selectedBenchmarks);
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <span className="card-label">Step 1 — Select Model</span>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            marginTop: "10px",
          }}
        >
          {models.map((model) => (
            <button
              key={model.id}
              onClick={() => setSelectedModel(model)}
              className={`nlp-model-chip chip ${selectedModel.id === model.id ? "active" : ""}`}
            >
              🤗 {model.name}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <span className="card-label">Step 2 — Bias Tests</span>
        <p
          style={{
            fontSize: "0.7rem",
            color: "var(--text-muted)",
            fontWeight: 600,
            marginTop: "10px",
          }}
        >
          ACTIVE BENCHMARKS (Select one or more)
        </p>
        <div
          className="chip-group"
          style={{
            marginBottom: "1rem",
            display: "flex",
            flexWrap: "wrap",
            gap: "8px",
          }}
        >
          {benchmarks.map((b) => (
            <div
              key={b.id}
              onClick={() => toggleBenchmark(b.id)}
              className={`chip ${selectedBenchmarks.includes(b.id) ? "active" : ""}`}
              style={{ cursor: "pointer", userSelect: "none" }}
            >
              {b.label}
            </div>
          ))}
        </div>

        <button
          className="btn-run"
          onClick={handleRun}
          disabled={loading || selectedBenchmarks.length === 0}
          style={{ width: "100%" }}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="spinning">⚙️</span> Auditing...
            </span>
          ) : (
            "▶ Run NLP Audit"
          )}
        </button>

        {selectedBenchmarks.length === 0 && (
          <p
            style={{
              color: "var(--danger)",
              fontSize: "0.7rem",
              marginTop: "8px",
              textAlign: "center",
            }}
          >
            Please select at least one benchmark.
          </p>
        )}
      </div>
    </div>
  );
};

export default NLPSidebar;
