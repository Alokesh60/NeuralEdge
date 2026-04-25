import React from "react";

const TabNav = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: "tabular", label: "📊 Tabular / ML" },
    { id: "nlp", label: "💬 NLP / LLM" },
    { id: "cv", label: "👁 Computer Vision" },
  ];

  return (
    <div
      className="nav-tabs"
      style={{
        display: "flex",
        background: "#e2e8f0",
        padding: "4px",
        borderRadius: "10px",
        width: "fit-content",
        marginBottom: "2rem",
      }}
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={`tab ${activeTab === tab.id ? "active" : ""}`}
          onClick={() => onTabChange(tab.id)}
          style={{
            padding: "8px 20px",
            border: "none",
            background: activeTab === tab.id ? "var(--surface)" : "transparent",
            borderRadius: "7px",
            fontWeight: 500,
            color:
              activeTab === tab.id ? "var(--primary)" : "var(--text-muted)",
            cursor: "pointer",
            transition: "all 0.2s",
            fontSize: "0.9rem",
            boxShadow: activeTab === tab.id ? "var(--shadow)" : "none",
          }}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export default TabNav;
