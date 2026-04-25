import { useState } from "react";
import { auditApi } from "../api/client";

export const useAudit = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const executeNlp = async (modelName) => {
    setLoading(true);
    setError(null);
    try {
      const result = await auditApi.runNlpAudit(modelName);
      setData(result);
    } catch (err) {
      setError("Backend connection failed.");
    } finally {
      setLoading(false);
    }
  };

  const executeTabular = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const result = await auditApi.runTabularAudit(formData);
      setData(result);
    } catch (err) {
      setError("Tabular audit failed.");
    } finally {
      setLoading(false);
    }
  };

  return {
    data,
    loading,
    error,
    executeNlp,
    executeTabular,
    reset: () => setData(null),
  };
};
