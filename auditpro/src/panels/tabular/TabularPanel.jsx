import React, { useEffect, useState } from "react";
import TabularSidebar from "./TabularSidebar";
import TabularResults from "./TabularResults";
import { useAudit } from "../../hooks/useAudit";

const TabularIdle = () => (
  <div className="card" style={{ textAlign: "center", padding: "40px" }}>
    <h3 style={{ fontWeight: 700, marginBottom: "8px" }}>Tabular Data Audit</h3>
    <p style={{ color: "var(--text-muted, #64748b)" }}>
      Upload a CSV dataset, choose sensitive attributes, and run a fairness
      audit.
    </p>
  </div>
);

const LoadingState = ({ showWarmup }) => {
  return (
    <div className="card" style={{ textAlign: "center", padding: "40px" }}>
      <div className="spinner"></div>
      <p style={{ marginTop: "10px", fontWeight: 600 }}>
        Running tabular bias audit...
      </p>
      {showWarmup && (
        <p style={{ marginTop: "6px", color: "var(--text-muted, #64748b)" }}>
          Backend warming up, please wait...
        </p>
      )}
    </div>
  );
};

const TabularPanel = () => {
  const { data, loading, error, executeTabular, reset } = useAudit();
  const [showWarmup, setShowWarmup] = useState(false);
  const [lastRequest, setLastRequest] = useState(null);

  useEffect(() => {
    if (!loading) {
      setShowWarmup(false);
      return;
    }

    const t = setTimeout(() => setShowWarmup(true), 8000);
    return () => clearTimeout(t);
  }, [loading]);

  const runAudit = async (formData) => {
    setLastRequest(formData);
    setShowWarmup(false);
    reset();

    try {
      await executeTabular(formData);
    } catch {
      // error state is handled by useAudit
    }
  };

  const retry = async () => {
    if (!lastRequest) return;
    await runAudit(lastRequest);
  };

  return (
    <div className="panel dashboard active">
      <aside>
        <TabularSidebar loading={loading} onRun={runAudit} onReset={reset} />
      </aside>

      <main>
        {!data && !loading && !error && <TabularIdle />}
        {loading && <LoadingState showWarmup={showWarmup} />}

        {!loading && error && (
          <div className="card" style={{ textAlign: "center", padding: "20px" }}>
            <p style={{ color: "var(--danger, #ef4444)", fontWeight: 600 }}>
              ⚠ {error}
            </p>
            <button
              className="btn-run"
              style={{ marginTop: "12px" }}
              onClick={retry}
              disabled={!lastRequest || loading}
            >
              Retry
            </button>
          </div>
        )}

        {!loading && data && <TabularResults data={data} />}
      </main>
    </div>
  );
};

export default TabularPanel;
