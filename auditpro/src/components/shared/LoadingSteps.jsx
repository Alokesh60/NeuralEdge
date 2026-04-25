import React, { useEffect, useMemo, useRef, useState } from "react";

const DEFAULT_INTERVAL_MS = 4000;

const statusIcon = {
  waiting: "⏳",
  running: (
    <span className="pulsing" aria-hidden="true">
      ⚙️
    </span>
  ),
  done: "✅",
};

const LoadingSteps = ({
  title = "Running NLP Bias Audit…",
  steps,
  active = true,
  intervalMs = DEFAULT_INTERVAL_MS,
  showFirstRunInfo = true,
}) => {
  const safeSteps = useMemo(() => (Array.isArray(steps) ? steps : []), [steps]);
  const [runningIndex, setRunningIndex] = useState(0);
  const timerRef = useRef(null);
  const runningIndexRef = useRef(0);

  useEffect(() => {
    runningIndexRef.current = runningIndex;
  }, [runningIndex]);

  useEffect(() => {
    if (!active) return undefined;
    if (safeSteps.length === 0) return undefined;

    runningIndexRef.current = 0;

    const advance = () => {
      timerRef.current = setTimeout(() => {
        if (runningIndexRef.current >= safeSteps.length - 1) return;
        setRunningIndex(runningIndexRef.current + 1);
        advance();
      }, intervalMs);
    };

    advance();

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [active, intervalMs, safeSteps.length]);

  if (safeSteps.length === 0) return null;

  return (
    <div className="card" style={{ padding: "2rem 1.75rem" }}>
      <p
        style={{
          fontWeight: 700,
          fontSize: "1rem",
          marginBottom: "1.25rem",
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <span className="spinning" aria-hidden="true">
          ⚙️
        </span>
        {title}
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {safeSteps.map((step, index) => {
          const status =
            index < runningIndex
              ? "done"
              : index === runningIndex
                ? "running"
                : "waiting";

          const rowClass =
            status === "running"
              ? "nlp-step-row running"
              : status === "done"
                ? "nlp-step-row done"
                : "nlp-step-row";

          return (
            <div key={step.id} className={rowClass}>
              <span className="step-status">{statusIcon[status]}</span>
              <div>
                <div style={{ fontWeight: 600, fontSize: "0.85rem" }}>
                  {step.title}
                </div>
                <div
                  style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}
                >
                  {step.description}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {showFirstRunInfo && (
        <div
          style={{
            marginTop: "1.5rem",
            padding: "0.75rem 1rem",
            background: "var(--bg)",
            borderRadius: "var(--radius-md)",
            fontSize: "0.78rem",
            color: "var(--text-muted)",
            lineHeight: 1.55,
          }}
        >
          ⚡ <strong>First run</strong> downloads and warms model weights
          (~30–90s). <strong>Subsequent calls</strong> for the same model +
          configuration are served from server cache instantly.
        </div>
      )}
    </div>
  );
};

export default LoadingSteps;
