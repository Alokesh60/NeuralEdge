import React from "react";
import { motion } from "framer-motion";
import { Gauge, TrendingUp, TrendingDown } from "lucide-react";

const BiasScoreCard = ({ score, verdict, metricName }) => {
  const percentage = score * 100;
  const isPass = verdict === "PASS";

  const getScoreColor = () => {
    if (percentage < 30) return "text-green-600";
    if (percentage < 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getGradientColor = () => {
    if (percentage < 30) return "from-green-500 to-green-600";
    if (percentage < 60) return "from-yellow-500 to-orange-500";
    return "from-red-500 to-red-600";
  };

  return (
    <div className="glass-card rounded-xl p-6 h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <Gauge className="w-5 h-5 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold">Bias Score</h3>
        </div>
        <div
          className={`flex items-center gap-1 ${isPass ? "text-green-600" : "text-red-600"}`}
        >
          {isPass ? (
            <TrendingDown className="w-4 h-4" />
          ) : (
            <TrendingUp className="w-4 h-4" />
          )}
          <span className="text-sm font-medium">{verdict}</span>
        </div>
      </div>

      {/* Gauge Meter */}
      <div className="relative pt-4 pb-8">
        <div className="text-center mb-4">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
            className={`text-5xl font-bold ${getScoreColor()}`}
          >
            {percentage.toFixed(1)}%
          </motion.div>
          <p className="text-sm text-slate-500 mt-1">{metricName}</p>
        </div>

        {/* Progress Bar */}
        <div className="relative h-4 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={`absolute h-full bg-gradient-to-r ${getGradientColor()} rounded-full`}
          />
        </div>

        {/* Scale markers */}
        <div className="flex justify-between mt-2 text-xs text-slate-400">
          <span>Fair (0%)</span>
          <span>Moderate (50%)</span>
          <span>High Bias (100%)</span>
        </div>
      </div>

      {/* Interpretation */}
      <div className="mt-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
        <p className="text-sm">
          {percentage < 30 &&
            "✅ Low bias detected - Model appears fair across demographics"}
          {percentage >= 30 &&
            percentage < 60 &&
            "⚠️ Moderate bias detected - Review affected groups"}
          {percentage >= 60 &&
            "🚨 High bias detected - Immediate debiasing recommended"}
        </p>
      </div>
    </div>
  );
};

export default BiasScoreCard;
