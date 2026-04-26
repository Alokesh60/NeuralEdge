export const BASE_URL_BACKEND = "https://your-render-url";
export const BASE_URL_NLP = "https://your-hf-space-url";

export const auditApi = {
  // NLP Route
  runNlpAudit: async ({ modelName, benchmarks, demographicGroups } = {}) => {
    const response = await fetch(`${BASE_URL_NLP}/audit/nlp/`, {
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
    const response = await fetch(`${BASE_URL_BACKEND}/audit/tabular/flexible`, {
      method: "POST",
      body: formData, // Automatic boundary for multipart/form-data
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
};
