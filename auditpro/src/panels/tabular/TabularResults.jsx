import React, { useState } from "react";
import { VerdictBanner } from "../../components/shared/VerdictBanner";

const TabularResults = ({ data }) => {
  const { overall, charts, debiasing, explanation_summary } = data;

  // 🔥 Zoom state
  const [zoomImg, setZoomImg] = useState(null);

  return (
    <div className="animate-in">
      <VerdictBanner overall={overall} />

      {/* Accuracy & Bias Stats */}
      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-val">{(overall.accuracy * 100).toFixed(1)}%</div>
          <div className="stat-label">Model Accuracy</div>
        </div>

        <div className="stat-box">
          <div className="stat-val" style={{ color: "var(--danger)" }}>
            {overall.disparate_impact.toFixed(3)}
          </div>
          <div className="stat-label">Disparate Impact</div>
        </div>
      </div>

      {/* SHAP & Metrics Charts */}
      <div className="chart-container">
        <div className="card">
          <span className="card-label">Feature Importance (SHAP Summary)</span>

          {charts.shap_summary && (
            <img
              src={`data:image/png;base64,${charts.shap_summary}`}
              className="nlp-chart-img clickable"
              onClick={() =>
                setZoomImg(`data:image/png;base64,${charts.shap_summary}`)
              }
            />
          )}
        </div>

        <div className="card">
          <span className="card-label">Fairness Metrics Delta</span>

          {charts.metrics && (
            <img
              src={`data:image/png;base64,${charts.metrics}`}
              className="nlp-chart-img clickable"
              onClick={() =>
                setZoomImg(`data:image/png;base64,${charts.metrics}`)
              }
            />
          )}
        </div>
      </div>

      {/* Debiasing Comparison */}
      <div className="card" style={{ marginTop: "1.5rem" }}>
        <span className="card-label">
          Debiasing Strategy: {debiasing.method}
        </span>

        <div className="compare-row">
          <span className="compare-label">Baseline DI</span>

          <span className="compare-before">
            {debiasing.before_score.toFixed(3)}
          </span>

          <span className="compare-arrow">→</span>

          <span className="compare-after">
            {debiasing.after_score.toFixed(3)}
          </span>

          <span className="compare-delta">
            ▲ +{Math.round(debiasing.improvement * 100)}%
          </span>
        </div>

        {explanation_summary && (
          <div className="success-box" style={{ marginTop: "1rem" }}>
            {explanation_summary.verdict_explanation}
          </div>
        )}
      </div>

      {/* 🔥 IMAGE ZOOM MODAL */}
      {zoomImg && (
        <div className="image-modal" onClick={() => setZoomImg(null)}>
          <div
            className="image-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <span className="close-btn" onClick={() => setZoomImg(null)}>
              ✖
            </span>

            <img src={zoomImg} alt="Zoomed chart" />
          </div>
        </div>
      )}
    </div>
  );
};

export default TabularResults;
