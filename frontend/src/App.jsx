import React, { useState } from "react";
import { Toaster, toast } from "react-hot-toast";
import { Shield, Play, Sun, Moon, Download, Brain } from "lucide-react";
import AuditDashboard from "./components/AuditDashboard";
import { runAudit } from "./services/api";

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState("bert-base-uncased");

  const models = [
    "bert-base-uncased",
    "roberta-base",
    "distilbert-base-uncased",
  ];

  const handleAudit = async () => {
    setLoading(true);
    toast.loading("Running AI bias audit...", { id: "audit" });

    try {
      const data = await runAudit(selectedModel);
      setAuditData(data);
      toast.success("Audit completed successfully!", { id: "audit" });

      if (data.overall?.verdict === "FAIL") {
        toast.error(
          `⚠️ Model FAILED bias test - Score: ${data.overall.bias_score}`,
          { duration: 5000 },
        );
      } else {
        toast.success(
          `✅ Model PASSED bias test - Score: ${data.overall.bias_score}`,
          { duration: 5000 },
        );
      }
    } catch (error) {
      console.error("Audit failed:", error);
      toast.error(
        "Failed to run audit. Make sure backend is running on port 8000",
        { id: "audit" },
      );
    } finally {
      setLoading(false);
    }
  };

  const exportReport = () => {
    if (!auditData) {
      toast.error("No audit data to export");
      return;
    }

    const report = {
      timestamp: new Date().toISOString(),
      model: auditData.model_name,
      verdict: auditData.overall?.verdict,
      biasScore: auditData.overall?.bias_score,
      groups: auditData.groups,
      recommendations: auditData.recommendations,
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bias-audit-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Report exported!");
  };

  return (
    <div
      className={`min-h-screen transition-all duration-300 ${darkMode ? "dark" : ""}`}
    >
      <Toaster position="top-right" />

      {/* Animated Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-2000"></div>
      </div>

      {/* Header */}
      <header className="glass-card border-b sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold gradient-text">NeuralEdge</h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  AI Bias Auditor • Fairness Intelligence
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>

              <button
                onClick={handleAudit}
                disabled={loading}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold flex items-center gap-2 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                Run Audit
              </button>

              {auditData && (
                <button
                  onClick={exportReport}
                  className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                >
                  <Download className="w-5 h-5" />
                </button>
              )}

              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                {darkMode ? (
                  <Sun className="w-5 h-5" />
                ) : (
                  <Moon className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {!auditData && !loading && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
            <div className="glass-card rounded-2xl p-12 text-center max-w-2xl">
              <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                <Brain className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-3xl font-bold mb-4">
                Ready to Audit AI Fairness
              </h2>
              <p className="text-slate-600 dark:text-slate-300 mb-8">
                Click "Run Audit" to analyze the selected model for demographic
                bias.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
                <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-2">
                    <svg
                      className="w-4 h-4 text-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      ></path>
                    </svg>
                  </div>
                  <h3 className="font-semibold mb-1">Bias Detection</h3>
                  <p className="text-xs text-slate-500">
                    Advanced metrics for fairness evaluation
                  </p>
                </div>
                <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-2">
                    <svg
                      className="w-4 h-4 text-purple-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                      ></path>
                    </svg>
                  </div>
                  <h3 className="font-semibold mb-1">Group Analysis</h3>
                  <p className="text-xs text-slate-500">
                    Demographic parity & equal opportunity
                  </p>
                </div>
                <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mb-2">
                    <svg
                      className="w-4 h-4 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      ></path>
                    </svg>
                  </div>
                  <h3 className="font-semibold mb-1">Recommendations</h3>
                  <p className="text-xs text-slate-500">
                    Actionable debiasing strategies
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <Brain className="w-8 h-8 text-blue-600 animate-pulse" />
              </div>
            </div>
            <p className="mt-6 text-lg font-medium text-slate-600 dark:text-slate-300">
              Analyzing model fairness...
            </p>
            <p className="text-sm text-slate-400 mt-2">
              This may take a few moments
            </p>
          </div>
        )}

        {auditData && !loading && <AuditDashboard data={auditData} />}
      </main>
    </div>
  );
}

export default App;
