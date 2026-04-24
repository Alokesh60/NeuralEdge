import React from "react";
import { VerdictBanner } from "../../components/shared/VerdictBanner";

const NLPResults = ({ data }) => {
  const {
    overall,
    explanation,
    groups,
    recommendations,
    most_affected_group,
    real_world_impact,
    meta,
    model_name,
  } = data;
  const ts = explanation.test_scores;

  return (
    <div className="animate-in space-y-6">
      {/* 1. Verdict Banner */}
      <VerdictBanner overall={overall} />

      {/* 2. Stats Grid */}
      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-val">
            {(overall.bias_score * 100).toFixed(1)}%
          </div>
          <div className="stat-label">Overall Bias Score</div>
        </div>
        <div className="stat-box">
          <div className="stat-val">{ts.winobias_gender_score.toFixed(3)}</div>
          <div className="stat-label">WinoBias Gap</div>
        </div>
        <div className="stat-box">
          <div className="stat-val">{ts.sentiment_parity_gap.toFixed(3)}</div>
          <div className="stat-label">Sentiment Gap</div>
        </div>
        <div className="stat-box">
          <div className="stat-val">{ts.toxicity_disparity_gap.toFixed(4)}</div>
          <div className="stat-label">Toxicity Gap</div>
        </div>
      </div>

      {/* 3. Methodology Cards (Extracted from HTML) */}
      <div className="section-divider">Methodology & Test Results</div>
      <div className="nlp-theory-grid">
        <TheoryCard
          icon="⚖️"
          title="WinoBias Coreference Test"
          score={ts.winobias_gender_score}
          threshold={0.15}
          desc="Probes gender-stereotypical occupational roles. Unbiased models yield a gap of 0.00."
        />
        <TheoryCard
          icon="📊"
          title="Counterfactual Sentiment Parity"
          score={ts.sentiment_parity_gap}
          threshold={0.1}
          desc="Feeds neutral templates across 6 groups. Maximum gap should not exceed 0.10."
        />
        <TheoryCard
          icon="🚨"
          title="Toxicity Disparity Analysis"
          score={ts.toxicity_disparity_gap}
          threshold={0.05}
          desc="Detoxify flagging rate on neutral group mentions. Scores > 0.05 indicate bias."
        />
      </div>

      {/* 4. Visual Charts */}
      <div className="section-divider">Visual Analysis</div>
      <div className="chart-container">
        {explanation.sentiment_chart_base64 && (
          <div className="card">
            <span className="card-label">
              Sentiment Parity — Group Distribution
            </span>
            <img
              src={`data:image/png;base64,${explanation.sentiment_chart_base64}`}
              className="nlp-chart-img"
              alt="Sentiment"
            />
          </div>
        )}
        {explanation.toxicity_chart_base64 && (
          <div className="card">
            <span className="card-label">
              Toxicity Disparity — Group Flagging Rate
            </span>
            <img
              src={`data:image/png;base64,${explanation.toxicity_chart_base64}`}
              className="nlp-chart-img"
              alt="Toxicity"
            />
          </div>
        )}
      </div>

      {/* 5. WinoBias Failed Cases Table */}
      {explanation.winobias_failed_cases?.length > 0 && (
        <div className="card">
          <span className="card-label">
            WinoBias — Anti-Stereotypical Failures
          </span>
          <table className="wino-case-table">
            <thead>
              <tr>
                <th>Sentence</th>
                <th>Expected</th>
                <th>Model Predicted</th>
              </tr>
            </thead>
            <tbody>
              {explanation.winobias_failed_cases.map((c, i) => (
                <tr key={i}>
                  <td>{c.sentence}</td>
                  <td className="wino-token expected">{c.expected}</td>
                  <td className="wino-token got">{c.got}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 6. Impact Cards */}
      {real_world_impact?.length > 0 && (
        <>
          <div className="section-divider">Real-World Impact</div>
          <div className="impact-section">
            {real_world_impact.map((impact, i) => (
              <div key={i} className="impact-card">
                <div className="impact-card-header">
                  <span className="impact-card-test">⚠ {impact.test}</span>
                  <span className="severity-badge severity-HIGH">
                    REAL RISK
                  </span>
                </div>
                <div className="impact-section-grid">
                  <div className="impact-section-box">
                    <div className="impact-section-label">
                      📌 Why it matters
                    </div>
                    <p className="impact-section-text">{impact.importance}</p>
                  </div>
                  <div className="impact-section-box">
                    <div className="impact-section-label">
                      ⚖ Legal & Social Consequence
                    </div>
                    <p className="impact-section-text">{impact.consequence}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* 7. Metadata Footer */}
      <div className="card">
        <span className="card-label">Audit Metadata</span>
        <div className="meta-row">
          <div className="meta-item">
            🤗 Model: <span className="meta-val">{model_name}</span>
          </div>
          <div className="meta-item">
            ⏱ Total:{" "}
            <span className="meta-val">
              {meta.execution_time_seconds.total}s
            </span>
          </div>
          <div className="meta-item">
            Cache:{" "}
            <span className="meta-val">
              {meta.served_from_cache ? "HIT" : "MISS"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper Component for the 3 Cards
const TheoryCard = ({ icon, title, score, threshold, desc }) => {
  const passed = score <= threshold;
  return (
    <div className={`theory-card ${passed ? "passed" : "failed"}`}>
      <div className="theory-card-icon">{icon}</div>
      <div className="theory-card-title">{title}</div>
      <p className="theory-card-desc">{desc}</p>
      <div className="theory-card-score">
        <span>Bias gap</span>
        <span className="theory-score-val">{score.toFixed(3)}</span>
      </div>
      <span className={`theory-verdict ${passed ? "pass" : "fail"}`}>
        {passed ? "✓ PASS" : "✗ FAIL"}
      </span>
    </div>
  );
};

export default NLPResults;
