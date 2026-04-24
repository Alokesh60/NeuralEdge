import React from "react";
import TabularSidebar from "./TabularSidebar";
import TabularResults from "./TabularResults";
import { useAudit } from "../../hooks/useAudit";

const TabularPanel = () => {
  // Pull logic from our custom hook
  const { data, loading, error, executeTabular } = useAudit();

  return (
    <div className="panel dashboard active">
      <aside>
        {/* Pass the executeTabular function to the sidebar */}
        <TabularSidebar onRun={executeTabular} loading={loading} />
      </aside>
      <main>
        {/* State Handling */}
        {loading && (
          <div className="card text-center py-10">
            <span className="spinning" style={{ fontSize: "2rem" }}>
              ⚙️
            </span>
            <p className="mt-4 font-bold">
              Calculating SHAP values & Fairness Metrics...
            </p>
          </div>
        )}

        {error && <div className="api-status-error">{error}</div>}

        {/* Show results if data exists, otherwise show the idle state */}
        {data ? (
          <TabularResults data={data} />
        ) : (
          !loading && (
            <div className="card text-center" style={{ padding: "4rem 2rem" }}>
              <div style={{ fontSize: "3.5rem", marginBottom: "1rem" }}>📊</div>
              <h3 style={{ fontWeight: 700 }}>Tabular Bias Auditor</h3>
              <p className="text-muted">
                Upload a CSV and define your target column to begin the audit.
              </p>
            </div>
          )
        )}
      </main>
    </div>
  );
};

export default TabularPanel;
