import React, { useMemo } from "react";
import { VerdictBanner } from "../../components/shared/VerdictBanner";

const safeJson = (value) => {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
};

const TabularResults = ({ data }) => {
  const accuracy = Number(data?.accuracy);
  const metrics = data?.metrics ?? {};
  const disparateImpact = Number(metrics?.disparate_impact);
  const verdict = String(metrics?.verdict || "INFO").toUpperCase();
  const groupRates = metrics?.group_rates ?? {};
  const topFeatures = Array.isArray(data?.top_features) ? data.top_features : [];

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
      severity: verdict === "FAIL" ? "HIGH" : verdict === "PASS" ? "LOW" : "INFO",
    };
  }, [accuracy, disparateImpact, verdict]);

  const rateEntries = Object.entries(groupRates || {});

  const looksUnexpected =
    !Number.isFinite(accuracy) &&
    !Number.isFinite(disparateImpact) &&
    !topFeatures.length &&
    !rateEntries.length;

  return (
    <div className="animate-in">
      <VerdictBanner overall={bannerOverall} />

      {looksUnexpected ? (
        <div className="card" style={{ marginTop: "12px" }}>
          <span className="card-label">Unexpected Response</span>
          <p style={{ color: "var(--text-muted, #64748b)", marginTop: "6px" }}>
            The tabular backend returned an unexpected shape. Raw payload:
          </p>
          <pre
            style={{
              marginTop: "10px",
              padding: "12px",
              border: "1px solid var(--border, rgba(255,255,255,0.08))",
              borderRadius: "var(--radius-md, 12px)",
              overflow: "auto",
              maxHeight: "320px",
              whiteSpace: "pre-wrap",
            }}
          >
            {safeJson(data)}
          </pre>
        </div>
      ) : (
        <>
          <div className="card" style={{ marginTop: "12px" }}>
            <span className="card-label">Summary</span>
            <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
              <div className="chip">
                Accuracy:{" "}
                <strong>
                  {Number.isFinite(accuracy) ? `${(accuracy * 100).toFixed(1)}%` : "N/A"}
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
          </div>

          <div className="card" style={{ marginTop: "12px" }}>
            <span className="card-label">Group Rates</span>
            {rateEntries.length ? (
              <div style={{ marginTop: "10px", display: "grid", gap: "8px" }}>
                {rateEntries.map(([group, rate]) => (
                  <div
                    key={group}
                    className="chip"
                    style={{ display: "flex", justifyContent: "space-between" }}
                  >
                    <span>{group}</span>
                    <strong>
                      {Number.isFinite(Number(rate))
                        ? Number(rate).toFixed(3)
                        : "N/A"}
                    </strong>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ marginTop: "8px", color: "var(--text-muted, #64748b)" }}>
                No group rates returned.
              </p>
            )}
          </div>

          <div className="card" style={{ marginTop: "12px" }}>
            <span className="card-label">Feature Importance (Top 10)</span>
            {topFeatures.length ? (
              <div style={{ marginTop: "10px", overflow: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ textAlign: "left" }}>
                      <th style={{ padding: "8px 6px" }}>Feature</th>
                      <th style={{ padding: "8px 6px" }}>Importance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topFeatures.map((row, idx) => (
                      <tr
                        key={`${row?.feature ?? "feature"}-${idx}`}
                        style={{
                          borderTop:
                            "1px solid var(--border, rgba(255,255,255,0.08))",
                        }}
                      >
                        <td style={{ padding: "8px 6px" }}>
                          <code>{String(row?.feature ?? "N/A")}</code>
                        </td>
                        <td style={{ padding: "8px 6px" }}>
                          {Number.isFinite(Number(row?.importance))
                            ? Number(row.importance).toFixed(6)
                            : "N/A"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p style={{ marginTop: "8px", color: "var(--text-muted, #64748b)" }}>
                No feature importance returned (SHAP may be unavailable or disabled).
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default TabularResults;
