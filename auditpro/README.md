# AuditPro (Frontend)

AuditPro is an AI bias auditing web app with three audit modules:

- **Tabular** fairness audit (CSV upload)
- **NLP** bias audit (benchmarks + demographic groups)
- **CV** bias audit (image upload + Grad-CAM heatmap)

## Live URL

- Add your deployed Vercel URL here (example: `https://auditpro.vercel.app`)

## Tech Stack

- React 18 + Vite
- Plain CSS / CSS modules (project uses shared utility classes)
- `react-hot-toast` (UI notifications)

## Backend Services

These URLs are hardcoded in `src/api/client.js` (no env vars required):

- Tabular: `https://neuraledge.onrender.com`
- NLP: `https://alakesh60-auditpro-nlp.hf.space`
- CV: `https://alakesh60-auditpro-cv.hf.space`

## Run Locally

From the repo root:

```bash
cd auditpro
npm install
npm run dev
```

Build locally:

```bash
cd auditpro
npm run build
npm run preview
```

## Deploy (Vercel)

- Framework preset: **Vite**
- Root directory: `auditpro/`
- Build command: `npm run build`
- Output directory: `dist`

SPA routing is handled by `vercel.json`.

