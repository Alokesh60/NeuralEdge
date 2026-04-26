import React from "react";

const NLPIdle = () => {
  return (
    <div>
      <div className="card" style={{ padding: "2.5rem 2rem", textAlign: "center" }}>
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>💬</div>
        <h3 style={{ fontWeight: 700, fontSize: "1.1rem", marginBottom: "0.5rem" }}>
          NLP Fairness Audit Suite
        </h3>
        <p
          style={{
            color: "var(--text-muted)",
            fontSize: "0.875rem",
            maxWidth: 440,
            margin: "0 auto 2rem",
            lineHeight: 1.65,
          }}
        >
          Select a language model and run three complementary, peer-reviewed bias
          benchmarks to surface gender stereotyping, sentiment inequity, and toxicity
          disparity across demographic groups.
        </p>

        <div className="nlp-idle-cards">
          <div className="nlp-idle-mini">
            <div style={{ fontSize: "1.4rem", marginBottom: 6 }}>⚖️</div>
            <div style={{ fontWeight: 700, fontSize: "0.82rem", marginBottom: 4 }}>
              WinoBias
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", lineHeight: 1.45 }}>
              Pronoun prediction in occupational coreference chains
            </div>
          </div>
          <div className="nlp-idle-mini">
            <div style={{ fontSize: "1.4rem", marginBottom: 6 }}>📊</div>
            <div style={{ fontWeight: 700, fontSize: "0.82rem", marginBottom: 4 }}>
              Sentiment Parity
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", lineHeight: 1.45 }}>
              Equal scoring across demographic groups using neutral templates
            </div>
          </div>
          <div className="nlp-idle-mini">
            <div style={{ fontSize: "1.4rem", marginBottom: 6 }}>🚨</div>
            <div style={{ fontWeight: 700, fontSize: "0.82rem", marginBottom: 4 }}>
              Toxicity Disparity
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", lineHeight: 1.45 }}>
              Detoxify flagging rate on neutral group-mention sentences
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NLPIdle;

