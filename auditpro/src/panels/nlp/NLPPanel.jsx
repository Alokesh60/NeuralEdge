import React, { useMemo, useState } from "react";
import NLPSidebar from "./NLPSidebar";
import NLPIdle from "./NLPIdle";
import NLPResults from "./NLPResults";
import NLPComparison from "./NLPComparison";
import LoadingSteps from "../../components/shared/LoadingSteps";
import { useAudit } from "../../hooks/useAudit";
import { auditApi } from "../../api/client";

const DEFAULT_CONFIG = {
  benchmarks: ["winobias", "sentiment", "toxicity"],
  demographicGroups: ["Gender", "Race", "Religion"],
};

const COMPARISON_MODELS = [
  "bert-base-uncased",
  "roberta-base",
  "distilbert-base-uncased",
];

const NLPPanel = () => {
  const { data, loading, error, executeNlp, reset } = useAudit();

  const [viewMode, setViewMode] = useState("idle"); // 'idle' | 'loading' | 'results' | 'comparison'
  const [apiStatus, setApiStatus] = useState(null); // { type: 'info' | 'success' | 'error', message: string }
  const [comparisonData, setComparisonData] = useState(null);
  const [comparisonComplete, setComparisonComplete] = useState(false);
  const [runConfig, setRunConfig] = useState(DEFAULT_CONFIG);

  const loadingSteps = useMemo(() => {
    const stepsById = {
      winobias: {
        id: "winobias",
        title: "WinoBias Gender Stereotype Test",
        description: "12 occupational pronoun prediction pairs on fill-mask model",
      },
      sentiment: {
        id: "sentiment",
        title: "Sentiment Parity Test",
        description:
          "30 demographically-varied sentences scored across selected groups",
      },
      toxicity: {
        id: "toxicity",
        title: "Toxicity Disparity Test",
        description: "Detoxify scoring on neutral group-mention sentences",
      },
    };

    const ordered = ["winobias", "sentiment", "toxicity"];
    return ordered
      .filter((id) => runConfig.benchmarks.includes(id) && stepsById[id])
      .map((id) => stepsById[id]);
  }, [runConfig.benchmarks]);

  const runSingleAudit = async (modelName, benchmarks, demographicGroups) => {
    const cfg = {
      benchmarks: benchmarks?.length ? benchmarks : DEFAULT_CONFIG.benchmarks,
      demographicGroups: demographicGroups?.length
        ? demographicGroups
        : DEFAULT_CONFIG.demographicGroups,
    };

    setRunConfig(cfg);
    setComparisonData(null);
    setComparisonComplete(false);
    setApiStatus({ type: "info", message: "Connecting to audit server…" });
    setViewMode("loading");
    reset();

    try {
      const res = await executeNlp({ modelName, ...cfg });
      setViewMode("results");
      setApiStatus({
        type: "success",
        message: res?.meta?.served_from_cache
          ? `⚡ Served from cache (${modelName})`
          : `✅ Audit complete in ${res?.meta?.execution_time_seconds?.total ?? "?"}s`,
      });
    } catch (e) {
      setViewMode("idle");
      setApiStatus({
        type: "error",
        message: `⚠ Error: ${e?.message ?? "Request failed"}`,
      });
    }
  };

  const runComparison = async ({ benchmarks, demographicGroups }) => {
    const cfg = {
      benchmarks: benchmarks?.length ? benchmarks : DEFAULT_CONFIG.benchmarks,
      demographicGroups: demographicGroups?.length
        ? demographicGroups
        : DEFAULT_CONFIG.demographicGroups,
    };

    setRunConfig(cfg);
    setComparisonComplete(false);
    setComparisonData(null);
    setApiStatus({ type: "info", message: "Starting cross-model comparison…" });
    setViewMode("loading");
    reset();

    const results = [];
    for (let i = 0; i < COMPARISON_MODELS.length; i++) {
      const modelName = COMPARISON_MODELS[i];
      setApiStatus({
        type: "info",
        message: `Auditing ${modelName} (${i + 1}/${COMPARISON_MODELS.length})…`,
      });

      try {
        const res = await auditApi.runNlpAudit({ modelName, ...cfg });
        results.push(res);
      } catch {
        results.push(null);
      }
    }

    setComparisonData(results.filter(Boolean));
    setComparisonComplete(true);
    setViewMode("comparison");
    setApiStatus({
      type: "success",
      message: "✅ Comparison complete — all 3 models audited",
    });
  };

  return (
    <div className="panel dashboard active">
      <aside>
        <NLPSidebar
          loading={loading}
          onRun={runSingleAudit}
          onCompare={runComparison}
          comparisonComplete={comparisonComplete}
          apiStatus={apiStatus}
        />
      </aside>

      <main>
        {viewMode === "idle" && !loading && <NLPIdle />}
        {viewMode === "loading" && <LoadingSteps steps={loadingSteps} />}
        {viewMode === "results" && data && <NLPResults data={data} />}
        {viewMode === "comparison" && comparisonData && (
          <NLPComparison comparisonData={comparisonData} />
        )}
        {error && <div className="api-status-error">{error}</div>}
      </main>
    </div>
  );
};

export default NLPPanel;

