// auditPdfExport.js
// Drop this into: src/utils/auditPdfExport.js
// Dependencies: npm install jspdf jspdf-autotable

import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

// ─── Brand colors (matching AuditPro UI) ────────────────────────────────────
const COLOR = {
  indigo:      [63,  81, 181],   // primary brand
  indigoDark:  [40,  53, 147],
  indigoLight: [197, 202, 233],
  green:       [46,  125, 50],
  greenLight:  [232, 245, 233],
  red:         [198, 40,  40],
  redLight:    [255, 235, 238],
  amber:       [245, 124, 0],
  amberLight:  [255, 243, 224],
  gray900:     [18,  18,  18],
  gray700:     [97,  97,  97],
  gray500:     [158, 158, 158],
  gray200:     [238, 238, 238],
  gray100:     [245, 245, 245],
  white:       [255, 255, 255],
};

// ─── Helpers ─────────────────────────────────────────────────────────────────
const rgb = (arr) => ({ r: arr[0], g: arr[1], b: arr[2] });

function setFill(doc, color) {
  doc.setFillColor(...color);
}
function setTextColor(doc, color) {
  doc.setTextColor(...color);
}
function setDrawColor(doc, color) {
  doc.setDrawColor(...color);
}

function labelBadge(doc, x, y, text, bgColor, textColor = COLOR.white) {
  const padding = 3;
  const textW = doc.getTextWidth(text);
  const badgeW = textW + padding * 2;
  setFill(doc, bgColor);
  doc.roundedRect(x, y - 4.5, badgeW, 6.5, 1.5, 1.5, "F");
  setTextColor(doc, textColor);
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text(text, x + padding, y);
}

function sectionHeader(doc, y, title) {
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  setTextColor(doc, COLOR.gray500);
  doc.text(title.toUpperCase(), 20, y);
  setDrawColor(doc, COLOR.gray200);
  doc.setLineWidth(0.3);
  doc.line(20, y + 2, 190, y + 2);
  return y + 8;
}

function card(doc, x, y, w, h, borderColor = null) {
  setFill(doc, COLOR.white);
  doc.roundedRect(x, y, w, h, 3, 3, "F");
  if (borderColor) {
    setDrawColor(doc, borderColor);
    doc.setLineWidth(0.5);
    doc.roundedRect(x, y, w, h, 3, 3, "S");
  } else {
    setDrawColor(doc, COLOR.gray200);
    doc.setLineWidth(0.3);
    doc.roundedRect(x, y, w, h, 3, 3, "S");
  }
}

// ─── PAGE 1: Cover ────────────────────────────────────────────────────────────
function drawCover(doc, auditData) {
  const { model, timestamp, overallBiasScore, verdict, benchmarks } = auditData;

  // Header bar
  setFill(doc, COLOR.indigoDark);
  doc.rect(0, 0, 210, 52, "F");

  // Accent strip
  setFill(doc, COLOR.indigo);
  doc.rect(0, 52, 210, 4, "F");

  // Logo mark — scales icon
  setFill(doc, [255, 255, 255, 0.15]);
  doc.circle(185, 26, 18, "F");
  setTextColor(doc, COLOR.white);
  doc.setFontSize(22);
  doc.setFont("helvetica", "bold");
  doc.text("⚖", 178, 32);

  // Brand
  setTextColor(doc, COLOR.white);
  doc.setFontSize(26);
  doc.setFont("helvetica", "bold");
  doc.text("AuditPro", 20, 25);
  doc.setFontSize(11);
  doc.setFont("helvetica", "normal");
  setTextColor(doc, COLOR.indigoLight);
  doc.text("Analytics · NLP Fairness Audit Report", 20, 34);

  doc.setFontSize(8);
  setTextColor(doc, COLOR.indigoLight);
  doc.text(`Generated: ${new Date(timestamp).toLocaleString()}`, 20, 44);
  doc.text(`Model: ${model}`, 100, 44);

  // ── Verdict card ─────────────────────────────────────────────────────────
  const verdictColor = verdict === "PASS" ? COLOR.green : COLOR.red;
  const verdictBg    = verdict === "PASS" ? COLOR.greenLight : COLOR.redLight;
  card(doc, 20, 64, 170, 38, verdictColor);

  setFill(doc, verdictBg);
  doc.roundedRect(20, 64, 170, 38, 3, 3, "F");

  doc.setFontSize(9);
  doc.setFont("helvetica", "bold");
  setTextColor(doc, verdictColor);
  doc.text("AUDIT VERDICT", 30, 75);

  doc.setFontSize(20);
  doc.text(`Model Audit: ${verdict === "PASS" ? "Passed" : "Failed"}`, 30, 88);

  const reasonText = verdict === "FAIL"
    ? `Toxicity disparity gap ${benchmarks?.toxicity?.gap?.toFixed(3) ?? "—"} exceeds 0.05 threshold`
    : "All fairness thresholds met across tested demographics";
  doc.setFontSize(8);
  doc.setFont("helvetica", "normal");
  setTextColor(doc, COLOR.gray700);
  doc.text(reasonText, 30, 96);

  // ── 4 KPI boxes ──────────────────────────────────────────────────────────
  const kpis = [
    { label: "Overall Bias Score", value: `${(overallBiasScore * 100).toFixed(1)}%`, color: overallBiasScore > 0.3 ? COLOR.red : COLOR.amber },
    { label: "WinoBias Gap",       value: (benchmarks?.winobias?.gap ?? 0).toFixed(3), color: (benchmarks?.winobias?.gap ?? 0) > 0.05 ? COLOR.red : COLOR.green },
    { label: "Sentiment Gap",      value: (benchmarks?.sentiment?.gap ?? 0).toFixed(3), color: (benchmarks?.sentiment?.gap ?? 0) > 0.05 ? COLOR.red : COLOR.green },
    { label: "Toxicity Gap",       value: (benchmarks?.toxicity?.gap ?? 0).toFixed(4), color: (benchmarks?.toxicity?.gap ?? 0) > 0.05 ? COLOR.red : COLOR.green },
  ];

  kpis.forEach((kpi, i) => {
    const x = 20 + i * 43;
    card(doc, x, 112, 40, 28);
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    setTextColor(doc, kpi.color);
    doc.text(kpi.value, x + 20, 126, { align: "center" });
    doc.setFontSize(7);
    doc.setFont("helvetica", "normal");
    setTextColor(doc, COLOR.gray500);
    doc.text(kpi.label, x + 20, 133, { align: "center" });
  });

  return 150;
}

// ─── PAGE 1 continued: Benchmark methodology ──────────────────────────────
function drawMethodology(doc, y, auditData) {
  y = sectionHeader(doc, y, "Benchmark Methodology");

  const benchmarks = [
    {
      title: "Test 1 — Gender Stereotype · WinoBias Coreference",
      icon: "⚖",
      color: COLOR.indigo,
      description:
        "Probes a fill-mask model on sentence pairs where gender-stereotypical occupational roles " +
        "(doctor, nurse, engineer) require pronoun resolution. A perfectly unbiased model predicts " +
        "stereotypical and anti-stereotypical pronouns with equal probability, yielding a gap of 0.00.",
      result: auditData.benchmarks?.winobias,
      threshold: 0.05,
    },
    {
      title: "Test 2 — Sentiment Bias · Counterfactual Sentiment Parity",
      icon: "📊",
      color: [56, 142, 60],
      description:
        "Feeds 5 semantically neutral templates to a sentiment classifier, substituting each across " +
        "6 demographic group names (White, Black, Asian, Latino, Muslim, Hindu). A fair model assigns " +
        "equal positive sentiment scores to all groups — the maximum difference is the gap.",
      result: auditData.benchmarks?.sentiment,
      threshold: 0.05,
    },
    {
      title: "Test 3 — Toxicity Bias · Disparity Analysis",
      icon: "🚨",
      color: COLOR.red,
      description:
        "Scores 6 structurally identical sentences that differ only in the demographic group name " +
        "using Hanu & Unitary's Detoxify model. Because sentences are neutral by construction, any " +
        "toxicity score > 0.05 is attributable solely to the model's prior associations with that group.",
      result: auditData.benchmarks?.toxicity,
      threshold: 0.05,
    },
  ];

  benchmarks.forEach((b) => {
    const passed = (b.result?.gap ?? 0) <= b.threshold;
    const cardColor = passed ? COLOR.greenLight : COLOR.redLight;
    const borderColor = passed ? COLOR.green : COLOR.red;

    card(doc, 20, y, 170, 32, borderColor);
    setFill(doc, cardColor);
    doc.roundedRect(20, y, 170, 32, 3, 3, "F");

    // Left accent bar
    setFill(doc, borderColor);
    doc.rect(20, y, 3, 32, "F");

    doc.setFontSize(8);
    doc.setFont("helvetica", "bold");
    setTextColor(doc, borderColor);
    doc.text(b.title, 28, y + 8);

    doc.setFontSize(7);
    doc.setFont("helvetica", "normal");
    setTextColor(doc, COLOR.gray700);
    const lines = doc.splitTextToSize(b.description, 125);
    doc.text(lines, 28, y + 14);

    // Gap value box (right side)
    const gapVal = b.result?.gap?.toFixed(4) ?? "N/A";
    doc.setFontSize(13);
    doc.setFont("helvetica", "bold");
    setTextColor(doc, borderColor);
    doc.text(gapVal, 178, y + 14, { align: "right" });
    doc.setFontSize(7);
    doc.setFont("helvetica", "normal");
    setTextColor(doc, COLOR.gray500);
    doc.text("gap", 178, y + 19, { align: "right" });

    labelBadge(
      doc, 158, y + 27,
      passed ? "PASS" : "FAIL",
      passed ? COLOR.green : COLOR.red
    );

    y += 38;
  });

  return y;
}

// ─── PAGE 2: Per-group metrics table ─────────────────────────────────────────
function drawGroupTable(doc, auditData) {
  doc.addPage();
  let y = 20;
  y = sectionHeader(doc, y, "Per-Group Metrics");

  const groups = auditData.perGroupMetrics ?? [];

  autoTable(doc, {
    startY: y,
    margin: { left: 20, right: 20 },
    head: [["Demographic Group", "Avg Sentiment Score", "Toxicity Score", "Status"]],
    body: groups.map((g) => [
      g.group,
      g.sentimentScore?.toFixed(4) ?? "—",
      g.toxicityScore?.toFixed(4) ?? "—",
      g.status,
    ]),
    headStyles: {
      fillColor: COLOR.indigoDark,
      textColor: COLOR.white,
      fontStyle: "bold",
      fontSize: 8,
    },
    bodyStyles: { fontSize: 8, textColor: COLOR.gray900 },
    alternateRowStyles: { fillColor: COLOR.gray100 },
    columnStyles: {
      0: { fontStyle: "bold", cellWidth: 50 },
      1: { halign: "center", cellWidth: 45 },
      2: { halign: "center", cellWidth: 45 },
      3: { halign: "center", cellWidth: 30 },
    },
    didDrawCell: (data) => {
      if (data.column.index === 3 && data.section === "body") {
        const val = data.cell.raw;
        const isBiased = val === "Biased";
        const color = isBiased ? COLOR.red : COLOR.green;
        const bg    = isBiased ? COLOR.redLight : COLOR.greenLight;

        const { x, y: cy, width, height } = data.cell;
        setFill(doc, bg);
        doc.roundedRect(x + 4, cy + 2, width - 8, height - 4, 2, 2, "F");
        doc.setFontSize(7);
        doc.setFont("helvetica", "bold");
        setTextColor(doc, color);
        doc.text(val, x + width / 2, cy + height / 2 + 1, { align: "center" });
      }
    },
  });

  y = doc.lastAutoTable.finalY + 14;

  // ── Most Affected Group highlight ─────────────────────────────────────────
  const worst = auditData.mostAffectedGroup;
  if (worst) {
    y = sectionHeader(doc, y, "Highest-Risk Group Identified");

    setFill(doc, COLOR.amberLight);
    doc.roundedRect(20, y, 170, 34, 3, 3, "F");
    setDrawColor(doc, COLOR.amber);
    doc.setLineWidth(0.5);
    doc.roundedRect(20, y, 170, 34, 3, 3, "S");

    // Left accent
    setFill(doc, COLOR.amber);
    doc.rect(20, y, 3, 34, "F");

    doc.setFontSize(9);
    doc.setFont("helvetica", "bold");
    setTextColor(doc, COLOR.amber);
    doc.text("🎯  " + worst.group, 28, y + 10);

    doc.setFontSize(7.5);
    doc.setFont("helvetica", "normal");
    setTextColor(doc, COLOR.gray700);
    const detail = doc.splitTextToSize(worst.detail, 155);
    doc.text(detail, 28, y + 18);

    y += 44;
  }

  return y;
}

// ─── PAGE 2 continued: Real-world impact + Remediation ───────────────────────
function drawImpactAndRemediation(doc, y, auditData) {
  const { realWorldImpact, remediationSteps } = auditData;

  if (realWorldImpact) {
    if (y > 220) { doc.addPage(); y = 20; }
    y = sectionHeader(doc, y, "Real-World Impact of Detected Bias");

    card(doc, 20, y, 170, 50, COLOR.red);
    setFill(doc, COLOR.redLight);
    doc.roundedRect(20, y, 170, 50, 3, 3, "F");
    setFill(doc, COLOR.red);
    doc.rect(20, y, 3, 50, "F");

    // Label
    labelBadge(doc, 155, y + 8, "REAL RISK", COLOR.red);

    doc.setFontSize(8.5);
    doc.setFont("helvetica", "bold");
    setTextColor(doc, COLOR.red);
    doc.text("⚠  " + (realWorldImpact.biasType ?? "Toxicity Disparity"), 28, y + 10);

    // Two-column layout
    doc.setFontSize(7.5);
    doc.setFont("helvetica", "bold");
    setTextColor(doc, COLOR.gray700);
    doc.text("📌  Why It Matters", 28, y + 20);
    doc.text("🏛  Legal & Social Consequence", 105, y + 20);

    doc.setFont("helvetica", "normal");
    const whyLines = doc.splitTextToSize(realWorldImpact.whyItMatters ?? "", 70);
    doc.text(whyLines, 28, y + 27);

    const legalLines = doc.splitTextToSize(realWorldImpact.legalConsequence ?? "", 70);
    doc.text(legalLines, 105, y + 27);

    y += 60;
  }

  if (remediationSteps?.length) {
    if (y > 220) { doc.addPage(); y = 20; }
    y = sectionHeader(doc, y, "Actionable Remediation Steps");

    remediationSteps.forEach((step, i) => {
      if (y > 260) { doc.addPage(); y = 20; }
      card(doc, 20, y, 170, 22);

      // Number badge
      setFill(doc, COLOR.indigo);
      doc.circle(28, y + 11, 5, "F");
      doc.setFontSize(8);
      doc.setFont("helvetica", "bold");
      setTextColor(doc, COLOR.white);
      doc.text(String(i + 1), 28, y + 13.5, { align: "center" });

      doc.setFontSize(7.5);
      doc.setFont("helvetica", "normal");
      setTextColor(doc, COLOR.gray900);
      const lines = doc.splitTextToSize(step, 145);
      doc.text(lines, 36, y + 10);

      y += 26;
    });
  }

  return y;
}

// ─── Footer on every page ────────────────────────────────────────────────────
function drawFooters(doc, auditData) {
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    setFill(doc, COLOR.gray100);
    doc.rect(0, 284, 210, 13, "F");
    setDrawColor(doc, COLOR.gray200);
    doc.setLineWidth(0.3);
    doc.line(0, 284, 210, 284);

    doc.setFontSize(7);
    doc.setFont("helvetica", "normal");
    setTextColor(doc, COLOR.gray500);
    doc.text("AuditPro Analytics · NeuralEdge Bias Detection Platform", 20, 291);
    doc.text(`Page ${i} of ${totalPages}`, 190, 291, { align: "right" });

    if (i === 1) {
      doc.text(`Model: ${auditData.model}  ·  Run time: ${auditData.totalTime ?? "—"}`, 105, 291, { align: "center" });
    }
  }
}

// ─── Audit metadata page (last) ───────────────────────────────────────────────
function drawMetadataPage(doc, auditData) {
  doc.addPage();
  let y = 20;
  y = sectionHeader(doc, y, "Audit Metadata");

  const meta = [
    ["Model",           auditData.model],
    ["Timestamp",       new Date(auditData.timestamp).toLocaleString()],
    ["Total Run Time",  auditData.totalTime ?? "—"],
    ["WinoBias Time",   auditData.benchmarkTimes?.winobias ?? "—"],
    ["Sentiment Time",  auditData.benchmarkTimes?.sentiment ?? "—"],
    ["Toxicity Time",   auditData.benchmarkTimes?.toxicity ?? "—"],
    ["Cache Status",    auditData.cacheStatus ?? "MISS"],
    ["Benchmark Suite", "WinoBias · Sentiment Parity · Toxicity Disparity"],
    ["Demographic Axes","Gender, Race, Religion"],
    ["Platform",        "NeuralEdge · AuditPro Analytics"],
  ];

  autoTable(doc, {
    startY: y,
    margin: { left: 20, right: 20 },
    body: meta,
    bodyStyles: { fontSize: 8 },
    columnStyles: {
      0: { fontStyle: "bold", textColor: COLOR.gray700, cellWidth: 55 },
      1: { textColor: COLOR.gray900 },
    },
    alternateRowStyles: { fillColor: COLOR.gray100 },
  });
}

// ─── PUBLIC API ───────────────────────────────────────────────────────────────
/**
 * generateAuditPdf(auditData)
 *
 * @param {Object} auditData
 * @param {string}  auditData.model            - e.g. "roberta-base"
 * @param {string}  auditData.timestamp        - ISO string
 * @param {number}  auditData.overallBiasScore - 0..1
 * @param {string}  auditData.verdict          - "PASS" | "FAIL"
 * @param {Object}  auditData.benchmarks
 *   @param {Object}  .winobias   { gap: number }
 *   @param {Object}  .sentiment  { gap: number }
 *   @param {Object}  .toxicity   { gap: number }
 * @param {Array}   auditData.perGroupMetrics  - [{ group, sentimentScore, toxicityScore, status }]
 * @param {Object}  auditData.mostAffectedGroup - { group, detail }
 * @param {Object}  auditData.realWorldImpact   - { biasType, whyItMatters, legalConsequence }
 * @param {Array}   auditData.remediationSteps  - string[]
 * @param {string}  auditData.totalTime         - e.g. "8.68s"
 * @param {Object}  auditData.benchmarkTimes    - { winobias, sentiment, toxicity }
 * @param {string}  auditData.cacheStatus       - "HIT" | "MISS"
 */
export function generateAuditPdf(auditData) {
  const doc = new jsPDF({ unit: "mm", format: "a4" });

  // Page 1
  const y1 = drawCover(doc, auditData);
  drawMethodology(doc, y1, auditData);

  // Page 2
  const y2 = drawGroupTable(doc, auditData);
  drawImpactAndRemediation(doc, y2, auditData);

  // Metadata page
  drawMetadataPage(doc, auditData);

  // Footers on all pages
  drawFooters(doc, auditData);

  // Save
  const filename = `AuditPro_${auditData.model}_${new Date(auditData.timestamp)
    .toISOString()
    .slice(0, 10)}.pdf`;
  doc.save(filename);
}