import React from "react";
import { motion } from "framer-motion";
import { Lightbulb, CheckCircle2, AlertCircle } from "lucide-react";

const RecommendationsList = ({ recommendations }) => {
  const getIcon = (index) => {
    if (index === 0) return <AlertCircle className="w-5 h-5 text-red-500" />;
    if (index === recommendations.length - 1)
      return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    return <Lightbulb className="w-5 h-5 text-yellow-500" />;
  };

  return (
    <div className="glass-card rounded-xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
          <Lightbulb className="w-5 h-5 text-yellow-600" />
        </div>
        <h3 className="text-lg font-semibold">Recommendations</h3>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec, index) => (
          <motion.div
            key={index}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg hover:shadow-md transition-shadow"
          >
            {getIcon(index)}
            <p className="text-slate-700 dark:text-slate-300 flex-1">{rec}</p>
            <span className="text-xs text-slate-400">#{index + 1}</span>
          </motion.div>
        ))}
      </div>

      {/* Action Button */}
      <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
        <button className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all">
          Apply Debiasing Techniques
        </button>
      </div>
    </div>
  );
};

export default RecommendationsList;
