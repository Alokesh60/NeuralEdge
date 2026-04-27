// src/api/client.js

const NLP_BASE = "https://alakesh60-auditpro-nlp.hf.space";
const TABULAR_BASE = "https://neuraledge.onrender.com";
const CV_BASE = "https://alakesh60-auditpro-cv.hf.space";

export const auditApi = {
  // NLP Route
  runNlpAudit: async ({ modelName, benchmarks, demographicGroups } = {}) => {
    const response = await fetch(`${NLP_BASE}/audit/nlp/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model_name: modelName,
        benchmarks,
        demographic_groups: demographicGroups,
      }),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const msg =
        (data && (data.message || data.detail)) ||
        response.statusText ||
        "Request failed";
      throw new Error(msg);
    }
    return data;
  },

  // Tabular Route (Flexible)
  runTabularAudit: async (formData) => {
    const response = await fetch(`${TABULAR_BASE}/audit/tabular/flexible`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const detail = data?.detail ?? data?.message ?? data;
      const msg =
        typeof detail === "string"
          ? detail
          : detail
            ? JSON.stringify(detail)
            : response.statusText || "Request failed";
      throw new Error(msg);
    }
    return data;
  },

  // CV Route
  runCvAudit: async (imageFile) => {
    const formData = new FormData();
    formData.append("file", imageFile);
    const response = await fetch(`${CV_BASE}/audit/cv/`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const msg =
        (data && (data.message || data.detail)) ||
        response.statusText ||
        "CV request failed";
      throw new Error(msg);
    }
    return data;
  },
};
