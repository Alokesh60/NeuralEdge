// src/hooks/useAudit.js

import { useState } from "react";
import { auditApi } from "../api/client";

export const useAudit = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const executeNlp = async ({
    modelName,
    benchmarks,
    demographicGroups,
  } = {}) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await auditApi.runNlpAudit({
        modelName,
        benchmarks,
        demographicGroups,
      });
      if (result?.status === "error")
        throw new Error(result?.message || "Audit failed.");
      setData(result);
      return result;
    } catch (err) {
      const msg = err?.message || "Backend connection failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const executeTabular = async (formData) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await auditApi.runTabularAudit(formData);
      if (result?.status === "error")
        throw new Error(result?.message || "Tabular audit failed.");
      setData(result);
      return result;
    } catch (err) {
      const msg = err?.message || "Tabular audit failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const executeCV = async (imageFile) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await auditApi.runCvAudit(imageFile);
      if (result?.status === "error")
        throw new Error(result?.message || "CV audit failed.");
      setData(result);
      return result;
    } catch (err) {
      const msg = err?.message || "CV audit failed.";
      setError(msg);
      throw err;
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
    executeCV,
    reset: () => {
      setData(null);
      setError(null);
    },
  };
};
