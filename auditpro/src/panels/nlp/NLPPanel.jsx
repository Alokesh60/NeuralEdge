import React from "react";
import NLPSidebar from "./NLPSidebar";
import NLPResults from "./NLPResults";
import { useAudit } from "../../hooks/useAudit";

const NLPPanel = () => {
  const { data, loading, error, executeNlp } = useAudit();

  return (
    <div className="panel dashboard active">
      <aside>
        <NLPSidebar onRun={executeNlp} loading={loading} />
      </aside>
      <main>
        {loading && (
          <div className="card pulsing text-center">
            ⚙️ Running NLP Audit...
          </div>
        )}
        {error && <div className="api-status-error">{error}</div>}
        {data ? <NLPResults data={data} /> : !loading && <IdleState />}
      </main>
    </div>
  );
};

const IdleState = () => (
  <div className="card text-center" style={{ padding: "3rem" }}>
    <div style={{ fontSize: "3rem" }}>💬</div>
    <h3>NLP Fairness Suite</h3>
    <p>Select a model to begin evaluation.</p>
  </div>
);

export default NLPPanel;
