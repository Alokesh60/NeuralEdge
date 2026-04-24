import React, { useEffect, useRef } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Users } from "lucide-react";

const GroupComparisonChart = ({ groups }) => {
  const chartData = groups.map((group) => ({
    name: group.group_name,
    score: group.metrics?.score || 0,
    ...group.metrics,
  }));

  const getBarColor = (score) => {
    if (score < 0.3) return "#10b981"; // green
    if (score < 0.6) return "#f59e0b"; // yellow
    return "#ef4444"; // red
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      return (
        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="font-semibold text-slate-900 dark:text-white mb-2">
            {label}
          </p>
          <p className="text-sm">
            <span className="font-medium">Bias Score:</span>{" "}
            <span
              className={
                dataPoint.score > 0.6
                  ? "text-red-600"
                  : dataPoint.score > 0.3
                    ? "text-yellow-600"
                    : "text-green-600"
              }
            >
              {(dataPoint.score * 100).toFixed(1)}%
            </span>
          </p>
          {Object.entries(dataPoint).map(([key, value]) => {
            if (
              key !== "name" &&
              key !== "score" &&
              typeof value === "number"
            ) {
              return (
                <p key={key} className="text-xs text-slate-500 mt-1">
                  {key}: {value.toFixed(3)}
                </p>
              );
            }
            return null;
          })}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-card rounded-xl p-6 h-full">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
          <Users className="w-5 h-5 text-indigo-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold">Group Comparison</h3>
          <p className="text-xs text-slate-500">
            Higher score indicates more bias toward that group
          </p>
        </div>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={350}>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e2e8f0"
              className="dark:stroke-slate-700"
            />
            <XAxis
              dataKey="name"
              tick={{ fill: "#64748b", fontSize: 12 }}
              angle={chartData.length > 4 ? -15 : 0}
              textAnchor={chartData.length > 4 ? "end" : "middle"}
              height={60}
            />
            <YAxis
              tick={{ fill: "#64748b", fontSize: 12 }}
              domain={[0, 1]}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              label={{
                value: "Bias Score",
                angle: -90,
                position: "insideLeft",
                fill: "#64748b",
                fontSize: 12,
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar
              dataKey="score"
              name="Bias Score"
              fill="#8884d8"
              radius={[8, 8, 0, 0]}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="flex flex-col items-center justify-center h-64 text-slate-400">
          <Users className="w-12 h-12 mb-3 opacity-50" />
          <p>No group data available</p>
        </div>
      )}

      {/* Legend */}
      <div className="flex justify-center gap-4 mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-xs">Low Bias (&lt;30%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <span className="text-xs">Moderate (30-60%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <span className="text-xs">High (&gt;60%)</span>
        </div>
      </div>
    </div>
  );
};

export default GroupComparisonChart;
