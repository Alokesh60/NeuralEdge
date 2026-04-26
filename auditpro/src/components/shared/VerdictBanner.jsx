export const VerdictBanner = ({ overall }) => {
  const isPass = overall.verdict === "PASS";
  return (
    <div className={`verdict-banner ${isPass ? "pass" : ""}`}>
      <div>
        <p className="verdict-title">Model Audit: {overall.verdict}</p>
        <p className="verdict-sub">{overall.verdict_message}</p>
      </div>
      <div className="severity-badge">{overall.severity || "INFO"}</div>
    </div>
  );
};
