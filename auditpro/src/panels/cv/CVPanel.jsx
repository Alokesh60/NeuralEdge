import React, { useState } from "react";
import "./CVPanel.css";

const CVPanel = () => {
  const [fileName, setFileName] = useState("Upload Image");
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [file, setFile] = useState(null);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please upload a valid image!");
      return;
    }

    setFile(file);
    setFileName(file.name);
    setPreview(URL.createObjectURL(file));
    setData(null); // Clear previous results on new upload
  };

  const handleScan = async () => {
    if (!file) {
      alert("Upload an image first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("view", "json");

    setLoading(true);
    setData(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/audit/cv/", {
        method: "POST",
        body: formData,
      });

      const result = await res.json();
      if (!res.ok) {
        throw new Error("API failed");
      }

      console.log(result);
      setData(result);
    } catch (err) {
      console.error(err);
      alert("Backend error");
    }

    setLoading(false);
  };

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

          {/* Preview */}
          {preview && (
            <img
              src={preview}
              alt="preview"
              style={{
                width: "100%",
                marginTop: "10px",
                borderRadius: "8px",
              }}
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

          {/* How it works */}
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
        {/* BEFORE UPLOAD */}
        {!data && !loading && (
          <div
            className="card"
            style={{ textAlign: "center", padding: "40px" }}
          >
            <h3>👁 AI-Powered CV Bias Scanner</h3>

            <p style={{ color: "#64748b", marginTop: "10px" }}>
              Upload an image to analyze prediction, bias risk, and model
              attention.
            </p>

            <div style={{ marginTop: "20px", fontSize: "14px" }}>
              ✔ AI Prediction <br />
              ✔ Bias Detection <br />✔ Grad-CAM Visualization
            </div>
          </div>
        )}

        {/* LOADING */}
        {loading && (
          <div className="card" style={{ textAlign: "center" }}>
            <div className="spinner"></div>
            <p style={{ marginTop: "10px", fontWeight: "600" }}>
              🔍 Processing CV with AI...
            </p>
          </div>
        )}

        {/* RESULTS */}
        {!loading && data && (
          <div className="animate-in results-grid">
            {/* Prediction */}
            <div className="card premium-card prediction-card">
              <span className="card-label">Prediction</span>

              <div className="flex-between">
                <h2 className="verdict-text">{data.overall?.verdict}</h2>

                <span
                  className={`badge pulse-badge verdict-${
                    data.overall?.verdict === "FAIL" ? "fail" : "pass"
                  }`}
                >
                  {data.overall?.verdict}
                </span>
              </div>

              <p className="metric">
                Accuracy:{" "}
                <strong>{`${(Number(data.overall?.accuracy) || 0) * (100).toFixed(2) ?? "0.00"}%`}</strong>
              </p>

              {/* Animated progress */}
              <div className="progress">
                <div
                  className="progress-fill accuracy"
                  style={{
                    width: `${Math.min(Math.max((Number(data.overall?.accuracy) || 0) * 100, 0), 100)}%`,
                  }}
                ></div>
              </div>
            </div>

            {/* Probabilities */}

            {/* Bias */}
            <div className="card premium-card bias-card">
              <span className="card-label">Bias Analysis</span>

              <p className="bias-note">
                Bias level indicator (higher = more unfair)
              </p>

              <div className="bias-container">
                <div className="bias-score">
                  {Number(data.overall?.bias_score) ?? 0}
                </div>

                <div className="bias-meta">
                  <p className="metric-label">Bias Score</p>
                  <p className="metric-sub">Lower is better (fairer model)</p>
                </div>
              </div>

              {/* Bias meter */}
              <div className="progress">
                <div
                  className="progress-fill bias"
                  style={{
                    width: `${Math.min(Math.max((Number(data.overall?.bias_score) || 0) * 100, 0), 100)}%`,
                  }}
                ></div>
              </div>
            </div>

            <div className="card insight-box">
              <span className="card-label">💡 AI Insight</span>

              <p className="insight-text">
                The model shows{" "}
                <strong>{Number(data.overall?.bias_score) ?? 0}</strong> bias
                score, indicating potential unfairness across demographic
                groups.
              </p>

              <p className="recommendation">
                Recommendation:{" "}
                <span className="recommendation-highlight">
                  {data.recommendations?.[0] || "Improve dataset balance"}
                </span>
              </p>
            </div>

            {/* Heatmap */}
            <div className="card premium-card heatmap-card">
              <span className="card-label">🔥 Model Attention</span>

              <div className="image-grid">
                <div>
                  <p className="img-label">Original</p>
                  <img src={preview} alt="Uploaded CV" className="img-box" />
                </div>

                <div>
                  <p className="img-label">Grad-CAM</p>
                  {data.explanation?.image_base64 ? (
                    <img
                      src={`data:image/png;base64,${data.explanation.image_base64}`}
                      className="img-box"
                    />
                  ) : (
                    <div className="no-heatmap-box">
                      <h4>⚠️ Grad-CAM not generated</h4>
                      <p className="sub">
                        Explanation model not enabled in this demo
                      </p>
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
