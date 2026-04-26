import React, { useMemo } from "react";
import { Trophy } from "lucide-react";

const safeNum = (n) => (typeof n === "number" && Number.isFinite(n) ? n : null);

const NLPComparison = ({ comparisonData = [] }) => {
  const { rows, bestRow, minBias, maxBias } = useMemo(() => {
    const rows = Array.isArray(comparisonData)
      ? comparisonData.filter(Boolean)
      : [];
    if (rows.length === 0)
      return { rows: [], bestRow: null, minBias: null, maxBias: null };

    const biasScores = rows
      .map((r) => safeNum(r?.overall?.bias_score))
      .filter((n) => n !== null);

    const minBias = biasScores.length ? Math.min(...biasScores) : null;
    const maxBias = biasScores.length ? Math.max(...biasScores) : null;

    let bestRow = null;
    if (minBias !== null) {
      bestRow =
        rows.find((r) => safeNum(r?.overall?.bias_score) === minBias) ?? null;
    }

    return { rows, bestRow, minBias, maxBias };
  }, [comparisonData]);

  if (rows.length === 0) return null;

  const scoreClass = (val) => {
    const n = safeNum(val);
    if (n === null || minBias === null || maxBias === null) return "";
    if (n === minBias) return "text-green-600 font-bold";
    if (n === maxBias) return "text-red-600 font-bold";
    return "text-gray-600";
  };

  return (
    <div>
      <div className="section-divider">
        Cross-Model Comparison — All 3 Models
      </div>

      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <span className="card-label">Side-by-Side Bias Scorecard</span>
        <p
          style={{
            fontSize: "0.78rem",
            color: "var(--text-muted)",
            marginBottom: "1rem",
            lineHeight: 1.55,
          }}
        >
          All models audited with identical benchmark configuration.{" "}
          <span style={{ color: "var(--success)", fontWeight: 600 }}>
            Green = best performer
          </span>{" "}
          ·{" "}
          <span style={{ color: "var(--danger)", fontWeight: 600 }}>
            Red = worst performer
          </span>{" "}
          · Lower scores = less bias.
        </p>

        <div style={{ overflowX: "auto" }}>
          <table className="compare-table">
            <thead>
              <tr>
                <th style={{ textAlign: "left" }}>Model</th>
                <th>Overall Bias %</th>
                <th>WinoBias</th>
                <th>Sentiment</th>
                <th>Toxicity</th>
                <th>Severity</th>
                <th>Verdict</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => {
                const isWinner = bestRow?.model_name === r?.model_name;
                const ts = r?.explanation?.test_scores ?? {};
                const overallBias = safeNum(r?.overall?.bias_score);
                const wino = safeNum(ts?.winobias_gender_score);
                const sent = safeNum(ts?.sentiment_parity_gap);
                const tox = safeNum(ts?.toxicity_disparity_gap);

                return (
                  <tr
                    key={r.request_id ?? r.model_name}
                    className={isWinner ? "compare-winner-row" : undefined}
                  >
                    <td style={{ textAlign: "left" }}>
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 8,
                        }}
                      >
                        {isWinner && (
                          <Trophy
                            size={16}
                            color="var(--success)"
                            aria-label="Winner"
                          />
                        )}
                        <span>{r.model_name ?? "Unknown model"}</span>
                      </span>
                    </td>
                    <td className={scoreClass(overallBias)}>
                      {overallBias === null
                        ? "—"
                        : `${(overallBias * 100).toFixed(1)}%`}
                    </td>
                    <td>{wino === null ? "—" : wino.toFixed(3)}</td>
                    <td>{sent === null ? "—" : sent.toFixed(3)}</td>
                    <td>{tox === null ? "—" : tox.toFixed(4)}</td>
                    <td>
                      <span
                        className={`severity-badge severity-${r?.overall?.severity ?? "LOW"}`}
                      >
                        {r?.overall?.severity ?? "LOW"}
                      </span>
                    </td>
                    <td style={{ fontFamily: "Inter, sans-serif" }}>
                      <span
                        style={{
                          fontWeight: 800,
                          color:
                            r?.overall?.verdict === "PASS"
                              ? "var(--success)"
                              : "var(--danger)",
                        }}
                      >
                        {r?.overall?.verdict ?? "—"}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {bestRow && (
        <div
          style={{
            background: "#f0fdf4",
            border: "1px solid #bbf7d0",
            borderRadius: "var(--radius-md)",
            padding: "0.9rem 1rem",
            display: "flex",
            alignItems: "center",
            gap: 10,
            color: "#065f46",
            fontSize: "0.85rem",
            fontWeight: 600,
          }}
        >
          <Trophy size={18} color="#065f46" aria-hidden="true" />
          <span>
            <strong>{bestRow.model_name}</strong> is the least biased model with
            a score of{" "}
            <strong>{(bestRow.overall.bias_score * 100).toFixed(1)}%</strong>.
          </span>
        </div>
      )}
    </div>
  );
};

export default NLPComparison;
