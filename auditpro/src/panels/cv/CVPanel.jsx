import React from "react";
import { useAudit } from "../../hooks/useAudit";
import { VerdictBanner } from "../../components/shared/VerdictBanner";

const CVPanel = () => {
  const { data, loading, error, executeTabular } = useAudit(); // Reuse tabular logic for file uploads

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    // Note: Pointing to your /audit/cv/ endpoint
    executeTabular(formData, "/audit/cv/");
  };

  return (
    <div className="panel dashboard active">
      <aside>
        <div className="card">
          <span className="card-label">Step 1 — Image/Archive</span>
          <div className="upload-area">
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".zip,.jpg,.png"
            />
            <p className="file-size text-muted">
              Upload Test Set (FairFace format)
            </p>
          </div>
          <button
            className="btn-run"
            disabled={loading}
            style={{ marginTop: "1rem" }}
          >
            {loading ? "Analyzing Pixels..." : "▶ Run CV Audit"}
          </button>
        </div>
      </aside>

      <main>
        {data && (
          <div className="animate-in">
            <VerdictBanner overall={data.overall} />
            <div className="card">
              <span className="card-label">
                Computer Vision Explanation (Grad-CAM)
              </span>
              {data.explanation.image_base64 ? (
                <img
                  src={`data:image/png;base64,${data.explanation.image_base64}`}
                  className="nlp-chart-img"
                  alt="Saliency Map"
                />
              ) : (
                <div className="warning-box">
                  Visual explanation currently unavailable in demo mode.
                </div>
              )}
              <p className="mt-4 text-sm italic">
                "{data.explanation.description}"
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default CVPanel;
