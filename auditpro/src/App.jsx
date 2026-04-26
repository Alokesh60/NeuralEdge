import React, { useState } from "react";
import Header from "./components/layout/Header";
import TabNav from "./components/layout/TabNav";
import NLPPanel from "./panels/nlp/NLPPanel";
import TabularPanel from "./panels/tabular/TabularPanel";
import CVPanel from "./panels/cv/CVPanel";
import { Toaster } from "react-hot-toast";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("nlp");

  return (
    <div className="app-wrapper">
      <Header />
      <div className="container">
        <div className="nav-tabs">
          <button
            className={`tab ${activeTab === "tabular" ? "active" : ""}`}
            onClick={() => setActiveTab("tabular")}
          >
            📊 Tabular
          </button>
          <button
            className={`tab ${activeTab === "nlp" ? "active" : ""}`}
            onClick={() => setActiveTab("nlp")}
          >
            💬 NLP
          </button>
          <button
            className={`tab ${activeTab === "cv" ? "active" : ""}`}
            onClick={() => setActiveTab("cv")}
          >
            👁 Vision
          </button>
        </div>

        {activeTab === "nlp" && <NLPPanel />}
        {activeTab === "tabular" && <TabularPanel />}
        {activeTab === "cv" && <CVPanel />}
      </div>
    </div>
  );
}

export default App;
