# NeuralEdge Suite — AuditPro 🧭⚖️

**AuditPro** is an **AI Bias Auditor** within the **NeuralEdge** suite—built to help teams *measure, explain, and communicate* fairness risks in machine-learning systems. It pairs a **FastAPI** backend for running ethical benchmarks with a **React (Vite)** frontend that turns raw bias metrics into judge-friendly visual narratives.

---

## ✨ Key Features

- **Multi-modal auditing** (NLP, Tabular, CV) for broad model coverage
- **Dynamic benchmarking** to run standardized bias evaluations on demand
- **Visual explainability** with explainers such as **SHAP** (tabular) and **Grad-CAM** (CV)
- **Real-world impact analysis** focused on affected groups, disparity patterns, and actionable insights
- **Non-technical-friendly dashboard** designed for quick scoring and confident decision-making

## 🧪 Current Benchmarks (NLP)

- **WinoBias** (coreference / gender bias)
- **Sentiment Parity** (group sentiment consistency)
- **Toxicity** (harmful language detection)

## 🧰 Technical Stack

**Frontend**
- React.js + Vite
- Lucide-React (icons)
- CSS3 (custom variables / theming)

**Backend**
- FastAPI (Python)
- Transformers (Hugging Face)
- Detoxify
- Matplotlib (bias chart generation)

---

## 🗂️ Frontend Folder Structure (React)

The production UI lives in `auditpro/`.

```text
auditpro/
└─ src/
   ├─ api/         # API client (backend integration)
   ├─ components/  # Shared layout, sidebar, results UI
   ├─ hooks/       # Custom logic for fetching audits
   └─ panels/      # Specialized views
      ├─ nlp/      # NLP auditing views
      ├─ tabular/  # Tabular auditing views
      └─ cv/       # Computer vision auditing views
```

---

## ⚙️ Setup & Installation

### Backend (FastAPI)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Alternative (project runner):

```powershell
python .\run.py
```

### Frontend (React + Vite)

```powershell
cd auditpro
npm install
npm run dev
```

---

## 🔁 UI Transition (Prototype → Production)

The UI was evolved from a **monolithic prototype (`index.html`)** into a **component-based React architecture** inside `auditpro/`. This improved performance, reuse, and scalability—making it easier to add new audits, panels, and judge-friendly visual explanations without rewriting the entire interface.

## 🤝 Team Contribution (My Role)

I served as the **Full Stack Developer for the UI/UX layer**, implementing:

- The **entire React UI logic** (layout, panels, interactions, and visual hierarchy)
- A clean **bridge between FastAPI audit outputs and frontend visualization**, translating bias metrics into clear, non-technical storytelling for judges
- A modular architecture (`api/`, `hooks/`, `components/`, `panels/`) that keeps the product maintainable as audits expand across NLP, tabular, and CV domains
