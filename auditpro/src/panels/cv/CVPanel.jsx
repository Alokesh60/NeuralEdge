import React, { useState } from "react";

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
      const res = await fetch("http://127.0.0.1:8000/scan", {
        method: "POST",
        body: formData,
      });

      const result = await res.json();
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
              {loading ? "🔄 Scanning..." : "▶ Scan CV"}
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
          <div className="animate-in">
            {/* Prediction */}
            <div className="card">
              <span className="card-label">Prediction</span>

              <h2>{data.prediction}</h2>

              <p>
                Confidence:{" "}
                <strong>{(data.confidence * 100).toFixed(2)}%</strong>
              </p>

              {/* Progress bar */}
              <div style={{ marginTop: "10px" }}>
                <div
                  style={{
                    height: "8px",
                    background: "#e5e7eb",
                    borderRadius: "10px",
                  }}
                >
                  <div
                    style={{
                      width: `${data.confidence * 100}%`,
                      height: "100%",
                      background: "#4f46e5",
                      borderRadius: "10px",
                    }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Probabilities */}
            <div className="card">
              <span className="card-label">Class Probabilities</span>

              <p>Male: {data.probabilities?.Male}</p>
              <p>Female: {data.probabilities?.Female}</p>
            </div>

            {/* Bias */}
            <div className="card">
              <span className="card-label">Bias Assessment</span>

              <div
                style={{
                  padding: "6px 12px",
                  borderRadius: "20px",
                  display: "inline-block",
                  fontWeight: "600",
                  background:
                    data.bias_risk === "high"
                      ? "#fee2e2"
                      : data.bias_risk === "medium"
                        ? "#fef3c7"
                        : "#dcfce7",
                  color:
                    data.bias_risk === "high"
                      ? "#b91c1c"
                      : data.bias_risk === "medium"
                        ? "#92400e"
                        : "#065f46",
                }}
              >
                {data.bias_risk?.toUpperCase()}
              </div>

              <p style={{ marginTop: "10px" }}>Risk Score: {data.risk_score}</p>
            </div>

            {/* Heatmap */}
            <div className="card">
              <span className="card-label">🔥 Model Attention</span>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "10px",
                }}
              >
                <img
                  src={preview}
                  alt="original"
                  style={{ width: "100%", borderRadius: "8px" }}
                />

                {data.heatmap_base64 ? (
                  <img
                    src={`data:image/png;base64,${data.heatmap_base64}`}
                    alt="heatmap"
                    style={{ width: "100%", borderRadius: "8px" }}
                  />
                ) : (
                  <p>No heatmap available</p>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default CVPanel;
