// ExportAuditButton.jsx
// Drop into: src/components/ExportAuditButton.jsx
// Usage: <ExportAuditButton auditData={auditData} disabled={!auditComplete} />

import { useState } from "react";
import { generateAuditPdf } from "../utils/auditPdfExport";

export default function ExportAuditButton({ auditData, disabled = false }) {
  const [state, setState] = useState("idle"); // "idle" | "generating" | "done" | "error"

  async function handleExport() {
    if (!auditData || disabled) return;
    setState("generating");
    try {
      // Small delay so the loading state renders before the PDF blocks the main thread
      await new Promise((r) => setTimeout(r, 80));
      generateAuditPdf(auditData);
      setState("done");
      setTimeout(() => setState("idle"), 2500);
    } catch (err) {
      console.error("PDF export failed:", err);
      setState("error");
      setTimeout(() => setState("idle"), 3000);
    }
  }

  const label = {
    idle:       "Export Audit Report",
    generating: "Generating PDF…",
    done:       "Report Downloaded ✓",
    error:      "Export Failed — Retry",
  }[state];

  const icon = {
    idle:       <DownloadIcon />,
    generating: <SpinnerIcon />,
    done:       <CheckIcon />,
    error:      <ErrorIcon />,
  }[state];

  const baseStyle = {
    display:        "inline-flex",
    alignItems:     "center",
    gap:            "8px",
    padding:        "10px 20px",
    borderRadius:   "8px",
    fontSize:       "14px",
    fontWeight:     "600",
    fontFamily:     "inherit",
    cursor:         disabled || state === "generating" ? "not-allowed" : "pointer",
    border:         "none",
    transition:     "all 0.2s ease",
    letterSpacing:  "0.01em",
    whiteSpace:     "nowrap",
  };

  const stateStyle = {
    idle: {
      background:  "linear-gradient(135deg, #3F51B5, #283593)",
      color:       "#fff",
      boxShadow:   "0 2px 8px rgba(63,81,181,0.35)",
    },
    generating: {
      background: "#e8eaf6",
      color:      "#3F51B5",
      boxShadow:  "none",
    },
    done: {
      background: "linear-gradient(135deg, #2E7D32, #1B5E20)",
      color:      "#fff",
      boxShadow:  "0 2px 8px rgba(46,125,50,0.35)",
    },
    error: {
      background: "linear-gradient(135deg, #c62828, #b71c1c)",
      color:      "#fff",
      boxShadow:  "0 2px 8px rgba(198,40,40,0.35)",
    },
  }[state];

  const disabledOverride = disabled
    ? { opacity: 0.45, boxShadow: "none", background: "#e0e0e0", color: "#9e9e9e" }
    : {};

  return (
    <button
      onClick={handleExport}
      disabled={disabled || state === "generating"}
      style={{ ...baseStyle, ...stateStyle, ...disabledOverride }}
      title={disabled ? "Run an audit first to export the report" : "Download PDF audit report"}
    >
      {icon}
      {label}
    </button>
  );
}

// ─── Icons ────────────────────────────────────────────────────────────────────

function DownloadIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

function SpinnerIcon() {
  return (
    <svg
      width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.2"
      strokeLinecap="round" strokeLinejoin="round"
      style={{ animation: "spin 0.8s linear infinite" }}
    >
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}