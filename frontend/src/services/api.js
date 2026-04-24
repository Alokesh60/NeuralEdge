import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export const runAudit = async (modelName = "bert-base-uncased") => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/audit/nlp/`,
      {
        model_name: modelName,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
        timeout: 60000, // 60 second timeout for model loading
      },
    );

    if (response.data.status === "error") {
      throw new Error(response.data.message || "Audit failed");
    }

    return response.data;
  } catch (error) {
    if (error.code === "ECONNABORTED") {
      throw new Error(
        "Request timeout - model might be loading for the first time",
      );
    }
    if (error.response) {
      throw new Error(
        error.response.data.message || `Server error: ${error.response.status}`,
      );
    }
    if (error.request) {
      throw new Error(
        "Cannot connect to backend. Make sure FastAPI server is running on port 8000",
      );
    }
    throw error;
  }
};
