<div align="center">

<img src="https://img.shields.io/badge/Google%20Solution%20Challenge-2026-4285F4?style=for-the-badge&logo=google&logoColor=white" />
<img src="https://img.shields.io/badge/Build%20with%20AI-Round%20Closes%20Apr%2028-34A853?style=for-the-badge" />
<img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" />

<br /><br />

```
███╗   ██╗███████╗██╗   ██╗██████╗  █████╗ ██╗     ███████╗██████╗  ██████╗ ███████╗
████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝ ██╔════╝
██╔██╗ ██║█████╗  ██║   ██║██████╔╝███████║██║     █████╗  ██║  ██║██║  ███╗█████╗  
██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██╔══██║██║     ██╔══╝  ██║  ██║██║   ██║██╔══╝  
██║ ╚████║███████╗╚██████╔╝██║  ██║██║  ██║███████╗███████╗██████╔╝╚██████╔╝███████╗
╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝
```

# **AuditPro — AI Bias Auditor**
### *Measure. Explain. Communicate. Fairness in AI.*

<br />

> **NeuralEdge** is a multi-modal AI fairness auditing suite that detects, visualizes, and communicates bias across **NLP**, **Tabular**, and **Computer Vision** models — turning raw metrics into judge-ready narratives.

<br />

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![HuggingFace](https://img.shields.io/badge/🤗%20Transformers-yellow?style=flat-square)](https://huggingface.co/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainability-red?style=flat-square)](https://shap.readthedocs.io/)
[![Vite](https://img.shields.io/badge/Vite-B73BFE?style=flat-square&logo=vite&logoColor=FFD62E)](https://vitejs.dev/)

</div>

---

## 🌍 The Problem We're Solving

AI systems are increasingly used in high-stakes decisions — hiring, lending, healthcare, and law enforcement. Yet most teams lack accessible tools to **audit their models for bias** before deployment. Biased AI can silently discriminate against groups based on gender, race, age, or other protected attributes.

**NeuralEdge / AuditPro** bridges this gap: a unified, modality-aware bias auditing platform that not only *detects* bias, but *explains* it visually and *communicates* it to non-technical stakeholders, judges, and regulators.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Multi-Modal Auditing** | Bias detection across NLP, Tabular, and Computer Vision models in one platform |
| 📊 **Dynamic Benchmarking** | Run standardized fairness evaluations on demand with live results |
| 🧠 **Visual Explainability** | SHAP for tabular models · Grad-CAM for CV models |
| ⚖️ **Real-World Impact Analysis** | Highlights affected groups, disparity patterns, and actionable remediation |
| 🖥️ **Judge-Friendly Dashboard** | Non-technical narrative UI — built for humans, not just data scientists |
| 🔗 **Microservices Architecture** | Modular services (NLP · CV · Tabular) that scale and deploy independently |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        NeuralEdge Suite                         │
│                                                                 │
│   ┌──────────────────────────────────────────────────────┐      │
│   │              React + Vite Frontend (auditpro/)        │      │
│   │   ┌──────────┐  ┌───────────┐  ┌──────────────────┐  │      │
│   │   │ NLP Panel│  │Tabular    │  │  CV Panel        │  │      │
│   │   │ (Swapnil)│  │Panel      │  │  (Kaustabh)      │  │      │
│   │   │          │  │(Sayan)    │  │                  │  │      │
│   │   └────┬─────┘  └─────┬─────┘  └────────┬─────────┘  │      │
│   │        └──────────────┴─────────────────┘             │      │
│   │                       │  API Layer (api/, hooks/)     │      │
│   └───────────────────────┼──────────────────────────────┘      │
│                            │ HTTP / REST                         │
│   ┌───────────────────────▼──────────────────────────────┐      │
│   │              FastAPI Services Layer                   │      │
│   │  ┌──────────────┐ ┌─────────────┐ ┌───────────────┐  │      │
│   │  │  nlp_service │ │  backend/   │ │  cv_service   │  │      │
│   │  │  (Swapnil)   │ │  (Sayan)    │ │  (Kaustabh)   │  │      │
│   │  │              │ │  [Tabular]  │ │               │  │      │
│   │  └──────────────┘ └─────────────┘ └───────────────┘  │      │
│   └──────────────────────────────────────────────────────┘      │
│                   ↑ Integrated & Presented by Alakesh            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
NeuralEdge/
│
├── auditpro/                          # 🎨 React Frontend (Alakesh)
│   └── src/
│       ├── api/                       # Backend API client & request layer
│       ├── components/                # Shared UI: Layout, Sidebar, Results cards
│       ├── hooks/                     # Custom React hooks for fetching audit data
│       └── panels/
│           ├── nlp/                   # NLP audit views & visualizations
│           ├── tabular/               # Tabular bias audit panels
│           └── cv/                   # Computer Vision audit panels
│
├── backend/                           # 📋 Tabular Bias Service (Sayan)
│   └── app/
│       └── main.py                    # Tabular fairness API — SHAP, disparity metrics
│
├── nlp_service/                       # 💬 NLP Bias Module (Swapnil)
│   │                                  # WinoBias · Sentiment Parity · Toxicity Detection
│   └── ...                            # HuggingFace Transformers, Detoxify pipelines
│
├── cv_service/                        # 👁️ Computer Vision Bias Module (Kaustabh)
│   │                                  # Grad-CAM explainability · Demographic fairness
│   └── ...                            # FairFace model integration, PyTorch
│
├── fairface_test_images/              # 🖼️ CV Test Dataset (Kaustabh)
│   └── ...                            # Sample images for CV fairness benchmarking
│
├── fairness_model.pth                 # 🧩 Pretrained fairness model weights (Kaustabh)
├── project.ipynb                      # 📓 Research & Exploration Notebook
├── Untitled.ipynb                     # 📓 Scratch/experiment notebook
├── package.json                       # Node.js dependencies (frontend tooling)
├── .gitignore
└── README.md
```

> **Note:** Tabular bias logic (Sayan's contribution) lives in the `backend/` folder — the core tabular service with SHAP explainability and disparity metrics. It is surfaced via `auditpro/src/panels/tabular/` in the frontend (Alokesh's integration work).

---

## 🧰 Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| **React.js + Vite** | Component-based SPA, fast HMR dev server |
| **CSS3 (custom variables)** | Theming, dark/light mode support |
| **Lucide-React** | Consistent icon system |

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI (Python)** | High-performance async REST API |
| **Uvicorn** | ASGI server |
| **HuggingFace Transformers** | Pre-trained NLP models for bias benchmarks |
| **Detoxify** | Toxicity detection in text |
| **SHAP** | Model-agnostic explainability for tabular data |
| **Grad-CAM** | Gradient-weighted class activation maps (CV) |
| **PyTorch** | Deep learning framework (CV models) |
| **Matplotlib** | Bias chart generation (server-rendered) |
| **Pandas / Scikit-learn** | Tabular data processing & fairness metrics |

---

## 🧪 Bias Benchmarks

### 💬 NLP (Swapnil)
| Benchmark | What It Detects |
|---|---|
| **WinoBias** | Coreference resolution gender bias |
| **Sentiment Parity** | Inconsistent sentiment across demographic groups |
| **Toxicity** | Harmful or offensive language targeting groups |

### 📋 Tabular (Sayan)
| Benchmark | What It Detects |
|---|---|
| **Demographic Parity** | Equal positive prediction rates across groups |
| **Equal Opportunity** | True positive rate fairness |
| **SHAP Feature Attribution** | Which features drive discriminatory predictions |

### 👁️ Computer Vision (Kaustabh)
| Benchmark | What It Detects |
|---|---|
| **FairFace Evaluation** | Demographic bias in face recognition |
| **Grad-CAM Analysis** | Visual explanation of model attention regions |
| **Accuracy Disparity** | Performance gaps across racial/gender groups |

---

## 👥 Team Contributions

<table>
<tr>
<td align="center" width="25%">

### 🔵 Sayan
**Tabular Bias Analysis**

Designed and implemented the tabular fairness auditing pipeline. Built statistical disparity metrics (demographic parity, equal opportunity) and integrated SHAP-based feature attribution to explain which input features drive biased predictions in structured datasets.

**Owns:** `backend/` (tabular service) · SHAP integration · Fairness metric computation

</td>
<td align="center" width="25%">

### 🟢 Kaustabh
**Computer Vision Bias**

Built the CV bias detection module leveraging FairFace for demographic fairness evaluation. Implemented Grad-CAM visual explainability to highlight attention regions contributing to biased classifications. Managed pretrained model weights and test image datasets.

**Owns:** `cv_service/` · `fairface_test_images/` · `fairness_model.pth` · Grad-CAM pipeline

</td>
<td align="center" width="25%">

### 🟡 Swapnil
**NLP Bias Detection**

Developed the NLP auditing pipeline using HuggingFace Transformers. Implemented WinoBias for gender coreference bias, Sentiment Parity evaluation across demographic groups, and Detoxify-powered toxicity detection. Built the NLP API endpoints consumed by the frontend.

**Owns:** `nlp_service/` · HuggingFace pipelines · Detoxify integration · NLP benchmarks

</td>
<td align="center" width="25%">

### 🔴 Alakesh
**Integration & UI/UX**

Architected the full-stack integration layer — unified all three services under a single FastAPI gateway and built the entire React frontend from prototype to production. Designed the judge-friendly dashboard that translates raw bias metrics into clear visual narratives accessible to non-technical audiences.

**Owns:** `auditpro/` · React UI · API integration · System architecture & presentation

</td>
</tr>
</table>

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- pip & npm

### 1. Clone the Repository
```bash
git clone https://github.com/Alokesh60/NeuralEdge.git
cd NeuralEdge
```

### 2. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

> Alternative (project runner script):
> ```bash
> python run.py
> ```

Backend will be running at `http://localhost:8000`  
Swagger docs available at `http://localhost:8000/docs`

### 3. Frontend Setup (React + Vite)
```bash
cd auditpro
npm install
npm run dev
```

Frontend will be running at `http://localhost:5173`

---

## 🔁 Design Decisions

### Prototype → Production UI
The UI was intentionally evolved from a **monolithic `index.html` prototype** into a **component-based React architecture** inside `auditpro/`. This shift enabled:
- **Reusable panels** per modality (NLP, Tabular, CV) without code duplication
- **Separation of concerns** between data-fetching (hooks), layout (components), and views (panels)
- **Scalability** — new audit types can be added by creating a new panel without touching existing code

### Microservice Philosophy
Each bias domain (NLP, Tabular, CV) is encapsulated in its own service directory. The `backend/` acts as an orchestration layer, allowing individual services to be developed, tested, and deployed independently.

---

## 🗺️ Roadmap

- [ ] Add batch audit support (upload dataset → full bias report)
- [ ] PDF/HTML report export for regulatory submission
- [ ] Bias remediation suggestions (not just detection)
- [ ] Support for audio/speech bias detection
- [ ] GitHub Actions CI/CD pipeline
- [ ] Docker Compose for one-command deployment

---

## 📄 License

This project was built for the **Google Solution Challenge 2026 — Build with AI** hackathon.

---

<div align="center">

**Built with ❤️ by Team NeuralEdge**  
*Sayan · Kaustabh · Swapnil · Alakesh*

*Making AI fairer, one audit at a time.*

</div>
