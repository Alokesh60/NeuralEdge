const BASE_URL = "http://localhost:8000";

export const auditApi = {
  // NLP Route
  runNlpAudit: async (modelName) => {
    const response = await fetch(`${BASE_URL}/audit/nlp/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_name: modelName }),
    });
    return response.json();
  },

  // Tabular Route (Flexible)
  runTabularAudit: async (formData) => {
    const response = await fetch(`${BASE_URL}/audit/tabular/flexible`, {
      method: "POST",
      body: formData, // Automatic boundary for multipart/form-data
    });
    return response.json();
  },
};
