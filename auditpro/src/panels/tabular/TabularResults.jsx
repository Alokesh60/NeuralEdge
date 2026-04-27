import React, { useMemo, useEffect, useRef } from "react";
import { VerdictBanner } from "../../components/shared/VerdictBanner";

const safeJson = (value) => {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
};

// ── Disparate Impact Gauge ──────────────────────────────────────────────────
const DiGauge = ({ value }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !Number.isFinite(value)) return;

    const loadChart = () => {
      if (!window.Chart) {
        setTimeout(loadChart, 100);
        return;
      }
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }

      const clamped = Math.min(Math.max(value, 0), 2);
      const filled = clamped;
      const remaining = 2 - clamped;
      const color =
        value >= 0.8 ? "#10b981" : value >= 0.6 ? "#f59e0b" : "#ef4444";

      chartRef.current = new window.Chart(canvasRef.current, {
        type: "doughnut",
        data: {
          datasets: [
            {
              data: [filled, remaining],
              backgroundColor: [color, "#f1f5f9"],
              borderWidth: 0,
              circumference: 180,
              rotation: 270,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "72%",
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
        },
      });
    };

    loadChart();
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [value]);

  const label = value >= 0.8 ? "PASS" : value >= 0.6 ? "BORDERLINE" : "FAIL";
  const labelColor =
    value >= 0.8 ? "#10b981" : value >= 0.6 ? "#f59e0b" : "#ef4444";

  return (
    <div
      style={{
        position: "relative",
        height: "160px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <canvas
        ref={canvasRef}
        role="img"
        aria-label={`Disparate impact gauge showing ${value.toFixed(3)}, threshold is 0.8`}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
        }}
      />
      <div style={{ position: "absolute", bottom: "8px", textAlign: "center" }}>
        <div
          style={{
            fontSize: "1.5rem",
            fontWeight: 700,
            color: labelColor,
            fontFamily: "JetBrains Mono, monospace",
          }}
        >
          {value.toFixed(3)}
        </div>
        <div
          style={{
            fontSize: "0.7rem",
            fontWeight: 700,
            color: labelColor,
            letterSpacing: "0.05em",
          }}
        >
          {label}
        </div>
        <div
          style={{
            fontSize: "0.65rem",
            color: "var(--text-muted, #64748b)",
            marginTop: "2px",
          }}
        >
          threshold ≥ 0.8
        </div>
      </div>
    </div>
  );
};

// ── Group Rates Bar Chart ───────────────────────────────────────────────────
const GroupRatesChart = ({ groupRates }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const entries = Object.entries(groupRates || {});

  useEffect(() => {
    if (!canvasRef.current || !entries.length) return;

    const loadChart = () => {
      if (!window.Chart) {
        setTimeout(loadChart, 100);
        return;
      }
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }

      const labels = entries.map(([k]) => k);
      const values = entries.map(([, v]) => Number(v));
      const colors = values.map((_, i) => (i === 0 ? "#ef4444" : "#4f46e5"));

      chartRef.current = new window.Chart(canvasRef.current, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Positive outcome rate",
              data: values,
              backgroundColor: colors,
              borderRadius: 6,
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` Rate: ${ctx.parsed.y.toFixed(3)}`,
              },
            },
          },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 12 } } },
            y: {
              beginAtZero: true,
              max: Math.min(1, Math.max(...values) * 1.3),
              ticks: {
                font: { size: 11 },
                callback: (v) => v.toFixed(2),
              },
              grid: { color: "#f1f5f9" },
            },
          },
        },
      });
    };

    loadChart();
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [JSON.stringify(entries)]);

  return (
    <div
      style={{
        position: "relative",
        height: `${Math.max(entries.length * 52 + 60, 160)}px`,
      }}
    >
      <canvas
        ref={canvasRef}
        role="img"
        aria-label={`Bar chart comparing positive outcome rates across demographic groups: ${entries.map(([k, v]) => `${k}: ${Number(v).toFixed(3)}`).join(", ")}`}
      />
    </div>
  );
};

// ── Feature Importance Horizontal Bar Chart ─────────────────────────────────
const FeatureChart = ({ features }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !features.length) return;

    const loadChart = () => {
      if (!window.Chart) {
        setTimeout(loadChart, 100);
        return;
      }
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }

      const top = [...features].slice(0, 10).reverse();
      const labels = top.map((r) => String(r.feature ?? ""));
      const values = top.map((r) => Number(r.importance));

      chartRef.current = new window.Chart(canvasRef.current, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Importance",
              data: values,
              backgroundColor: "#4f46e5",
              borderRadius: 4,
              borderWidth: 0,
            },
          ],
        },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: { label: (ctx) => ` ${ctx.parsed.x.toFixed(4)}` },
            },
          },
          scales: {
            x: {
              beginAtZero: true,
              ticks: { font: { size: 11 }, callback: (v) => v.toFixed(2) },
              grid: { color: "#f1f5f9" },
            },
            y: {
              ticks: {
                font: { family: "JetBrains Mono, monospace", size: 11 },
                autoSkip: false,
              },
              grid: { display: false },
            },
          },
        },
      });
    };

    loadChart();
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [JSON.stringify(features)]);

  return (
    <div
      style={{
        position: "relative",
        height: `${features.slice(0, 10).length * 40 + 60}px`,
      }}
    >
      <canvas
        ref={canvasRef}
        role="img"
        aria-label={`Horizontal bar chart of top feature importances`}
      />
    </div>
  );
};

// ── Main Component ──────────────────────────────────────────────────────────
const TabularResults = ({ data }) => {
  const accuracy = Number(data?.accuracy);
  const metrics = data?.metrics ?? {};
  const disparateImpact = Number(metrics?.disparate_impact);
  const verdict = String(metrics?.verdict || "INFO").toUpperCase();
  const groupRates = metrics?.group_rates ?? {};
  const topFeatures = Array.isArray(data?.top_features)
    ? data.top_features
    : [];

  const bannerOverall = useMemo(() => {
    const diText = Number.isFinite(disparateImpact)
      ? `Disparate impact: ${disparateImpact.toFixed(3)}`
      : "Disparate impact: N/A";
    const accText = Number.isFinite(accuracy)
      ? `Accuracy: ${(accuracy * 100).toFixed(1)}%`
      : "Accuracy: N/A";
    return {
      verdict: verdict === "PASS" || verdict === "FAIL" ? verdict : "INFO",
      verdict_message: `${diText} | ${accText}`,
      severity:
        verdict === "FAIL" ? "HIGH" : verdict === "PASS" ? "LOW" : "INFO",
    };
  }, [accuracy, disparateImpact, verdict]);

  const rateEntries = Object.entries(groupRates || {});

  const looksUnexpected =
    !Number.isFinite(accuracy) &&
    !Number.isFinite(disparateImpact) &&
    !topFeatures.length &&
    !rateEntries.length;

  // Load Chart.js once
  useEffect(() => {
    if (window.Chart) return;
    const script = document.createElement("script");
    script.src =
      "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js";
    script.async = true;
    document.head.appendChild(script);
  }, []);

  if (looksUnexpected) {
    return (
      <div className="animate-in">
        <div className="card" style={{ marginTop: "12px" }}>
          <span className="card-label">Unexpected Response</span>
          <p style={{ color: "var(--text-muted, #64748b)", marginTop: "6px" }}>
            The tabular backend returned an unexpected shape. Raw payload:
          </p>
          <pre
            style={{
              marginTop: "10px",
              padding: "12px",
              border: "1px solid var(--border, #e2e8f0)",
              borderRadius: "8px",
              overflow: "auto",
              maxHeight: "320px",
              whiteSpace: "pre-wrap",
              fontSize: "0.78rem",
            }}
          >
            {safeJson(data)}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div
      className="animate-in"
      style={{ display: "flex", flexDirection: "column", gap: "16px" }}
    >
      <VerdictBanner overall={bannerOverall} />

      {/* ── Summary + Gauge row ── */}
      <div
        className="card"
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 220px",
          gap: "24px",
          alignItems: "center",
        }}
      >
        <div>
          <span className="card-label">Summary</span>
          <div
            style={{
              display: "flex",
              gap: "10px",
              flexWrap: "wrap",
              marginTop: "10px",
            }}
          >
            <div className="chip">
              Accuracy:{" "}
              <strong>
                {Number.isFinite(accuracy)
                  ? `${(accuracy * 100).toFixed(1)}%`
                  : "N/A"}
              </strong>
            </div>
            <div className="chip">
              Disparate Impact:{" "}
              <strong>
                {Number.isFinite(disparateImpact)
                  ? disparateImpact.toFixed(3)
                  : "N/A"}
              </strong>
            </div>
            <div className={`chip ${verdict === "PASS" ? "active" : ""}`}>
              Verdict: <strong>{verdict}</strong>
            </div>
          </div>
          <p
            style={{
              marginTop: "12px",
              fontSize: "0.8rem",
              color: "var(--text-muted, #64748b)",
              lineHeight: 1.6,
            }}
          >
            Disparate impact measures the ratio of positive outcome rates
            between unprivileged and privileged groups. A value below 0.8
            indicates potential bias (the 4/5ths rule).
          </p>
        </div>
        <div>
          <p
            style={{
              fontSize: "0.7rem",
              fontWeight: 700,
              color: "var(--text-muted, #64748b)",
              textAlign: "center",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              marginBottom: "4px",
            }}
          >
            Disparate Impact
          </p>
          {Number.isFinite(disparateImpact) ? (
            <DiGauge value={disparateImpact} />
          ) : (
            <p
              style={{
                textAlign: "center",
                color: "var(--text-muted, #64748b)",
                padding: "40px 0",
              }}
            >
              N/A
            </p>
          )}
        </div>
      </div>

      {/* ── Group Rates Chart ── */}
      {rateEntries.length > 0 && (
        <div className="card">
          <span className="card-label">Group Rates</span>
          <p
            style={{
              fontSize: "0.78rem",
              color: "var(--text-muted, #64748b)",
              margin: "4px 0 12px",
            }}
          >
            Positive outcome rate per demographic group
          </p>
          <GroupRatesChart groupRates={groupRates} />
        </div>
      )}

      {/* ── Feature Importance Chart ── */}
      {topFeatures.length > 0 && (
        <div className="card">
          <span className="card-label">
            Feature Importance (Top {Math.min(topFeatures.length, 10)})
          </span>
          <p
            style={{
              fontSize: "0.78rem",
              color: "var(--text-muted, #64748b)",
              margin: "4px 0 12px",
            }}
          >
            SHAP-based feature contributions to model predictions
          </p>
          <FeatureChart features={topFeatures} />
        </div>
      )}
    </div>
  );
};

export default TabularResults;
