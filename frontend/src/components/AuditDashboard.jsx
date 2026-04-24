import React from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Users,
  Lightbulb,
  FileText,
  Activity,
  Shield,
} from "lucide-react";
import BiasScoreCard from "./BiasScoreCard";
import GroupComparisonChart from "./GroupComparisonChart";
import RecommendationsList from "./RecommendationsList";

const AuditDashboard = ({ data }) => {
  const { model_name, overall, groups, explanation, recommendations, status } =
    data;
  const isPass = overall?.verdict === "PASS";
  const biasScore = overall?.bias_score || 0;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header Stats */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <div className="glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-500 dark:text-slate-400">Model</p>
            <Brain className="w-4 h-4 text-blue-500" />
          </div>
          <p className="text-lg font-bold font-mono">{model_name}</p>
        </div>

        <div className="glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-500 dark:text-slate-400">Status</p>
            {isPass ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-red-500" />
            )}
          </div>
          <p
            className={`text-2xl font-bold ${isPass ? "text-green-600" : "text-red-600"}`}
          >
            {overall?.verdict}
          </p>
        </div>

        <div className="glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Bias Metric
            </p>
            <Activity className="w-4 h-4 text-purple-500" />
          </div>
          <p className="text-lg font-semibold">
            {overall?.bias_metric || "Combined Bias"}
          </p>
        </div>

        <div className="glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Groups Analyzed
            </p>
            <Users className="w-4 h-4 text-indigo-500" />
          </div>
          <p className="text-2xl font-bold">{groups?.length || 0}</p>
        </div>
      </motion.div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants}>
          <BiasScoreCard
            score={biasScore}
            verdict={overall?.verdict}
            metricName={overall?.bias_metric}
          />
        </motion.div>

        <motion.div variants={itemVariants}>
          <GroupComparisonChart groups={groups} />
        </motion.div>
      </div>

      {/* Explanation */}
      {explanation && (
        <motion.div
          variants={itemVariants}
          className="glass-card rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold">
              Plain-Language Explanation
            </h3>
          </div>
          <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
            {explanation.description || "No detailed explanation provided"}
          </p>
          {explanation.type && (
            <div className="mt-3 inline-flex items-center gap-2 px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-full text-xs">
              <span className="font-medium">Type:</span> {explanation.type}
            </div>
          )}
          {explanation.image_base64 && (
            <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <img
                src={`data:image/png;base64,${explanation.image_base64}`}
                alt="Bias visualization"
                className="max-w-full h-auto rounded-lg"
              />
            </div>
          )}
        </motion.div>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <motion.div variants={itemVariants}>
          <RecommendationsList recommendations={recommendations} />
        </motion.div>
      )}

      {/* Debiasing Info (if available) */}
      {data.debiasing && (
        <motion.div
          variants={itemVariants}
          className="glass-card rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <Shield className="w-5 h-5 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold">Debiasing Impact</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-slate-500">Method</p>
              <p className="font-semibold">{data.debiasing.method}</p>
            </div>
            <div>
              <p className="text-sm text-slate-500">Before Score</p>
              <p className="font-semibold text-red-600">
                {data.debiasing.before_score.toFixed(3)}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-500">After Score</p>
              <p className="font-semibold text-green-600">
                {data.debiasing.after_score.toFixed(3)}
              </p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
            <p className="text-sm">
              Improvement:{" "}
              <span className="font-bold text-green-600">
                {(data.debiasing.improvement * 100).toFixed(1)}%
              </span>
            </p>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

// Import Brain icon
import { Brain } from "lucide-react";

export default AuditDashboard;
