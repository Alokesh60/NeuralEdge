// auditDataAdapter.js
// Drop into: src/utils/auditDataAdapter.js
//
// PURPOSE: Maps whatever your FastAPI backend returns into the
//          shape that generateAuditPdf() expects.
//          Edit the field names on the LEFT side to match your actual API response.

/**
 * adaptBackendResponse(apiResponse, modelName)
 *
 * @param {Object} apiResponse  - Raw JSON from your FastAPI /bias/nlp endpoint
 * @param {string} modelName    - The model selected by the user, e.g. "roberta-base"
 * @returns {Object}            - auditData shape expected by generateAuditPdf()
 */
export function adaptBackendResponse(apiResponse, modelName) {
  // ── Destructure your API response fields here ────────────────────────────
  // Adjust key names to match what your FastAPI actually returns.
  const {
    overall_bias_score,          // number 0..1
    verdict,                     // "PASS" | "FAIL"
    winobias_gap,                // number
    sentiment_gap,               // number
    toxicity_gap,                // number
    per_group_metrics,           // array (see mapping below)
    most_affected_group,         // object
    real_world_impact,           // object
    remediation_steps,           // string[]
    timing,                      // object with timing info
    cache_status,                // "HIT" | "MISS"
  } = apiResponse;

  return {
    // ── Identity ─────────────────────────────────────────────────────────
    model:     modelName,
    timestamp: new Date().toISOString(),

    // ── Top-level scores ──────────────────────────────────────────────────
    overallBiasScore: overall_bias_score ?? 0,
    verdict:          verdict ?? (toxicity_gap > 0.05 ? "FAIL" : "PASS"),

    // ── Benchmark gaps ────────────────────────────────────────────────────
    benchmarks: {
      winobias:  { gap: winobias_gap  ?? 0 },
      sentiment: { gap: sentiment_gap ?? 0 },
      toxicity:  { gap: toxicity_gap  ?? 0 },
    },

    // ── Per-group table ───────────────────────────────────────────────────
    // Your API returns an array of group objects; adapt field names as needed.
    perGroupMetrics: (per_group_metrics ?? []).map((g) => ({
      group:          g.group_name ?? g.group,
      sentimentScore: g.avg_sentiment_score ?? g.sentiment_score,
      toxicityScore:  g.toxicity_score,
      status:         g.is_biased ? "Biased" : "Fair",
    })),

    // ── Most affected group ───────────────────────────────────────────────
    mostAffectedGroup: most_affected_group
      ? {
          group:  most_affected_group.group_name ?? most_affected_group.group,
          detail: most_affected_group.detail ?? most_affected_group.explanation,
        }
      : null,

    // ── Real-world impact (static fallbacks if Gemini not yet wired) ──────
    realWorldImpact: real_world_impact
      ? {
          biasType:        real_world_impact.bias_type        ?? "Toxicity Disparity",
          whyItMatters:    real_world_impact.why_it_matters   ?? DEFAULT_WHY,
          legalConsequence:real_world_impact.legal_consequence ?? DEFAULT_LEGAL,
        }
      : {
          biasType:         "Toxicity Disparity",
          whyItMatters:     DEFAULT_WHY,
          legalConsequence: DEFAULT_LEGAL,
        },

    // ── Remediation steps (static fallbacks if Gemini not yet wired) ─────
    remediationSteps: remediation_steps ?? DEFAULT_REMEDIATION_STEPS,

    // ── Timing & meta ─────────────────────────────────────────────────────
    totalTime: timing?.total       ?? null,
    benchmarkTimes: {
      winobias:  timing?.winobias  ?? null,
      sentiment: timing?.sentiment ?? null,
      toxicity:  timing?.toxicity  ?? null,
    },
    cacheStatus: cache_status ?? "MISS",
  };
}

// ─── Static fallbacks (used before Gemini is wired in) ───────────────────────
// Replace these with your Gemini API responses once integrated.

const DEFAULT_WHY =
  "Toxicity classifiers decide what speech is allowed on platforms, in schools, " +
  "and in workplace tools. A model that marks neutral mentions of a demographic " +
  "group as toxic will systematically silence that community while allowing " +
  "equivalent speech from other groups.";

const DEFAULT_LEGAL =
  "Disproportionate toxicity flagging amounts to algorithmic discrimination. " +
  "It has been documented in production content moderation systems and has led " +
  "to regulatory investigations and class-action litigation in the EU and United States.";

const DEFAULT_REMEDIATION_STEPS = [
  "Audit training data — Review the corpus used to train the toxicity model for " +
  "over-representation of flagged demographic mentions in toxic contexts.",

  "Apply re-weighting — Use counterfactual data augmentation (CDA) to balance " +
  "exposure of each demographic group in neutral vs. toxic contexts during fine-tuning.",

  "Set per-group thresholds — Instead of a single decision threshold, calibrate " +
  "group-specific thresholds to equalise false-positive rates across demographics.",

  "Continuous monitoring — Integrate this fairness audit into the CI/CD pipeline " +
  "so any model update is automatically re-evaluated against the same benchmarks.",

  "Stakeholder review — Involve representatives from affected communities in the " +
  "model evaluation process before deployment to production systems.",
];


// ─── EXAMPLE USAGE in your NLP results component ─────────────────────────────
//
//  import { adaptBackendResponse } from "../utils/auditDataAdapter";
//  import { generateAuditPdf }     from "../utils/auditPdfExport";
//  import ExportAuditButton        from "../components/ExportAuditButton";
//
//  // After your API call resolves:
//  const auditData = adaptBackendResponse(apiResponse, selectedModel);
//
//  // Render the button:
//  <ExportAuditButton auditData={auditData} disabled={!auditComplete} />
//
//  // Or call the PDF generator directly:
//  generateAuditPdf(auditData);