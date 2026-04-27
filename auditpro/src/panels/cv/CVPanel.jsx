import React, { useState } from "react";
import { useAudit } from "../../hooks/useAudit";
import "./CVPanel.css";

const CVPanel = () => {
  const [fileName, setFileName] = useState("Upload Image");
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const { data, loading, error, executeCV, reset } = useAudit();

  const handleFileUpload = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    if (!f.type.startsWith("image/")) {
      alert("Please upload a valid image!");
      return;
    }
    setFile(f);
    setFileName(f.name);
    setPreview(URL.createObjectURL(f));
    reset();
  };

  const handleScan = async () => {
    if (!file) {
      alert("Upload an image first!");
      return;
    }
    try {
      await executeCV(file);
    } catch (err) {
      // error is already set in useAudit
    }
  };

  const confidence = (Number(data?.confidence) || 0) * 100;
  const riskScore = Number(data?.bias_report?.bias_score) || 0;
  const risk = data?.bias_report?.bias_risk?.toLowerCase();
  const heatmapSrc = data?.heatmap_base64
    ? `data:image/jpeg;base64,${data.heatmap_base64}`
    : null;

  return (
    <div className="panel dashboard active">
      {/* ───── SIDEBAR ───── */}
      <aside>
        <div className="card">
          <span className="card-label">Upload CV Image</span>

          <div
            className="upload-area"
            onClick={() => document.getElementById("cvUpload").click()}
            style={{
              padding: "30px",
              border: "2px dashed #cbd5f5",
              borderRadius: "10px",
              textAlign: "center",
              cursor: "pointer",
            }}
          >
            <div style={{ fontSize: "2rem" }}>📤</div>
            <p style={{ fontWeight: "600", marginTop: "10px" }}>
              Click to upload CV image
            </p>
            <p style={{ fontSize: "12px", color: "#64748b" }}>
              JPG, PNG supported
            </p>
            <input
              id="cvUpload"
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              style={{ display: "none" }}
            />
          </div>

          {preview && (
            <img
              src={preview}
              alt="preview"
              style={{ width: "100%", marginTop: "10px", borderRadius: "8px" }}
            />
          )}

          {preview && (
            <button
              className="btn-run"
              onClick={handleScan}
              disabled={loading}
              style={{ marginTop: "10px", width: "100%" }}
            >
              {loading ? "🔄 Scanning..." : data ? "✔ Scanned" : "▶ Scan CV"}
            </button>
          )}

          <div className="card" style={{ marginTop: "1rem" }}>
            <span className="card-label">How it works</span>
            <p style={{ fontSize: "14px", color: "#64748b" }}>
              1. Upload a CV image <br />
              2. AI predicts gender using ResNet50 <br />
              3. Bias risk is calculated <br />
              4. Grad-CAM shows model attention
            </p>
          </div>
        </div>
      </aside>

      {/* ───── MAIN CONTENT ───── */}
      <main>
        <h2 style={{ marginBottom: "10px" }}>🤖 CV Bias Audit Report</h2>
        <p style={{ color: "#64748b", marginBottom: "20px" }}>
          AI-driven fairness evaluation of computer vision model
        </p>

        {!data && !loading && !error && (
          <div
            className="card"
            style={{ textAlign: "center", padding: "40px" }}
          >
            <h3>👁 AI-Powered CV Bias Scanner</h3>
            <p style={{ color: "#64748b", marginTop: "10px" }}>
              Upload an image to analyze prediction, bias risk, and model
              attention.
            </p>
          </div>
        )}

        {loading && (
          <div className="card" style={{ textAlign: "center" }}>
            <div className="spinner"></div>
            <p style={{ marginTop: "10px", fontWeight: "600" }}>
              🔍 Processing CV with AI...
            </p>
          </div>
        )}

        {error && (
          <div
            className="card"
            style={{ textAlign: "center", padding: "20px" }}
          >
            <p style={{ color: "var(--danger, #ef4444)", fontWeight: 600 }}>
              ⚠ {error}
            </p>
          </div>
        )}

        {!loading && data && (
          <div className="animate-in results-grid">
            {/* Bias Risk */}
            <div className="card premium-card prediction-card">
              <span className="card-label">Bias Risk</span>
              <div className="flex-between">
                <h2 className="verdict-text">{risk?.toUpperCase()}</h2>
                <span
                  className={`badge verdict-${risk === "high" ? "fail" : "pass"}`}
                >
                  {risk?.toUpperCase()}
                </span>
              </div>
              <p className="metric">
                Confidence: <strong>{confidence.toFixed(2)}%</strong>
              </p>
              <div className="progress">
                <div
                  className="progress-fill accuracy"
                  style={{ width: `${confidence}%` }}
                ></div>
              </div>
            </div>

            {/* Bias Score */}
            <div className="card premium-card bias-card">
              <span className="card-label">Bias Analysis</span>
              <div className="bias-container">
                <div className="bias-score">{riskScore}</div>
                <div className="bias-meta">
                  <p className="metric-label">Bias Score</p>
                  <p className="metric-sub">Lower is better (fairer model)</p>
                </div>
              </div>
              <div className="progress">
                <div
                  className="progress-fill bias"
                  style={{ width: `${riskScore * 100}%` }}
                ></div>
              </div>
            </div>

            {/* AI Insight */}
            <div className="card insight-box">
              <span className="card-label">💡 AI Insight</span>
              <p className="insight-text">
                The model shows <strong>{riskScore}</strong> bias score,
                indicating potential unfairness.
              </p>
              <p className="recommendation">
                Recommendation:{" "}
                <span className="recommendation-highlight">
                  {data.bias_assessment?.recommendation}
                </span>
              </p>
            </div>

            {/* Heatmap */}
            <div className="card premium-card heatmap-card">
              <span className="card-label">🔥 Model Attention</span>
              <div className="image-grid">
                <div>
                  <p className="img-label">Original</p>
                  <img src={preview} className="img-box" alt="Original" />
                </div>
                <div>
                  <p className="img-label">Grad-CAM</p>
                  {heatmapSrc ? (
                    <img
                      src={heatmapSrc}
                      className="img-box clickable"
                      alt="Heatmap"
                    />
                  ) : (
                    <div className="no-heatmap-box">
                      <h4>⚠️ Grad-CAM not generated</h4>
                      <p className="sub">Backend did not return heatmap</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default CVPanel;
