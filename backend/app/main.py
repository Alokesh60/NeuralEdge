# from fastapi import FastAPI
# from app.routes import tabular, nlp, cv, combined

# app = FastAPI(title="AI Bias Auditor")

# app.include_router(tabular.router)
# app.include_router(nlp.router)
# app.include_router(cv.router)
# app.include_router(combined.router)


# from fastapi.responses import HTMLResponse

# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard():
#     return """
#     <!DOCTYPE html>
#     <html>
#     <head><title>Bias Auditor Dashboard</title></head>
#     <body>
#         <h1>NeuralEdge Bias Auditor</h1>
#         <input type="file" id="csv" accept=".csv">
#         <button onclick="audit()">Run Audit</button>
#         <div id="results"></div>
#         <script>
#             async function audit() {
#                 const file = document.getElementById('csv').files[0];
#                 if (!file) return;
#                 const formData = new FormData();
#                 formData.append('file', file);
#                 formData.append('target_column', 'income');
#                 formData.append('sensitive_columns', 'sex');
#                 formData.append('privileged_values', '{"sex":"Male"}');
#                 formData.append('model_choice', 'logistic');
#                 const res = await fetch('/audit/tabular/flexible', { method: 'POST', body: formData });
#                 const data = await res.json();
#                 const div = document.getElementById('results');
#                 div.innerHTML = '<h2>Metrics</h2><pre>' + JSON.stringify(data.overall, null, 2) + '</pre><h2>Charts</h2>';
#                 for (const [name, b64] of Object.entries(data.charts)) {
#                     if (b64) {
#                         const img = document.createElement('img');
#                         img.src = `data:image/png;base64,${b64}`;
#                         img.style.maxWidth = '500px';
#                         img.style.margin = '10px';
#                         div.appendChild(img);
#                     }
#                 }
#             }
#         </script>
#     </body>
#     </html>
#     """



from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.routes import tabular, nlp, cv, combined

# Create the FastAPI app FIRST
app = FastAPI(title="AI Bias Auditor")

# Include routers
app.include_router(tabular.router)
app.include_router(nlp.router)
app.include_router(cv.router)
app.include_router(combined.router)

# Then define the dashboard route
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeuralEdge – Bias Auditor Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fb; margin: 0; padding: 20px; color: #1e293b; }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 { font-size: 2rem; margin-bottom: 0.5rem; color: #0f172a; }
            .subtitle { color: #475569; margin-bottom: 2rem; border-left: 4px solid #3b82f6; padding-left: 1rem; }
            .card { background: white; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 2rem; }
            .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; align-items: end; }
            .form-group { display: flex; flex-direction: column; gap: 0.5rem; }
            label { font-weight: 600; font-size: 0.9rem; color: #334155; }
            input, select { padding: 0.6rem 0.8rem; border: 1px solid #cbd5e1; border-radius: 0.5rem; font-size: 0.9rem; }
            input:focus, select:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.2); }
            button { background: #3b82f6; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; }
            button:hover { background: #2563eb; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
            .metric-card { background: #f8fafc; border-radius: 0.75rem; padding: 1rem; text-align: center; border: 1px solid #e2e8f0; }
            .metric-value { font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0; }
            .verdict-fail { color: #dc2626; }
            .verdict-pass { color: #10b981; }
            .chart-container { display: flex; flex-wrap: wrap; gap: 1.5rem; justify-content: center; }
            .chart-card { background: #ffffff; border-radius: 0.75rem; border: 1px solid #e2e8f0; overflow: hidden; width: calc(50% - 1rem); min-width: 300px; }
            .chart-card h3 { background: #f1f5f9; margin: 0; padding: 0.75rem 1rem; font-size: 1rem; border-bottom: 1px solid #e2e8f0; }
            .chart-card img { width: 100%; height: auto; display: block; }
            .recommendations { background: #fefce8; border-left: 4px solid #eab308; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; }
            .error { background: #fee2e2; border-left: 4px solid #ef4444; padding: 1rem; border-radius: 0.5rem; color: #991b1b; }
            .loading { text-align: center; padding: 2rem; color: #3b82f6; }
            @media (max-width: 768px) { .chart-card { width: 100%; } }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 NeuralEdge – Universal AI Bias Auditor</h1>
            <div class="subtitle">Upload any CSV, detect and mitigate bias in ML models</div>

            <div class="card">
                <h2>📤 1. Upload Dataset & Configure</h2>
                <div class="form-grid">
                    <div class="form-group"><label>CSV File (with header)</label><input type="file" id="fileInput" accept=".csv"></div>
                    <div class="form-group"><label>Target Column</label><input type="text" id="targetColumn" placeholder="e.g., income"></div>
                    <div class="form-group"><label>Sensitive Column</label><input type="text" id="sensitiveColumns" placeholder="e.g., sex"></div>
                    <div class="form-group"><label>Privileged Group (JSON)</label><input type="text" id="privilegedValues" placeholder='{"sex":"Male"}'></div>
                    <div class="form-group"><label>Model Choice</label><select id="modelChoice"><option value="logistic">Logistic Regression</option><option value="randomforest">Random Forest</option></select></div>
                    <div class="form-group"><label>Pretrained Model (.pkl)</label><input type="file" id="modelFile" accept=".pkl"></div>
                    <div class="form-group"><label>Pretrained Preprocessor (.pkl)</label><input type="file" id="preprocessorFile" accept=".pkl"></div>
                    <div class="form-group"><label>SHAP Sample Size</label><input type="number" id="shapSampleSize" placeholder="optional"></div>
                    <div class="form-group"><button id="auditBtn">🚀 Run Audit</button></div>
                </div>
            </div>

            <div id="results" style="display: none;">
                <div class="card"><h2>📊 Overall Metrics</h2><div class="metrics-grid" id="metricsGrid"></div><div id="verdictBadge"></div><div id="recommendations" class="recommendations"></div></div>
                <div class="card"><h2>👥 Per‑Group Performance</h2><div id="groupsTable"></div></div>
                <div class="card"><h2>📈 Visualizations</h2><div class="chart-container" id="chartsContainer"></div></div>
                <div class="card"><h2>🔍 Debiasing Comparison</h2><div id="debiasingComparison"></div></div>
                <div class="card"><h2>📝 Explanation</h2><div id="explanationSummary"></div></div>
            </div>
        </div>

        <script>
            const auditBtn = document.getElementById('auditBtn');
            const resultsDiv = document.getElementById('results');
            auditBtn.addEventListener('click', async () => {
                const file = document.getElementById('fileInput').files[0];
                if (!file) { alert('Select a CSV file'); return; }
                const target = document.getElementById('targetColumn').value.trim();
                const sensitive = document.getElementById('sensitiveColumns').value.trim();
                const priv = document.getElementById('privilegedValues').value.trim();
                if (!target || !sensitive || !priv) { alert('Fill target, sensitive, and privileged values'); return; }
                const formData = new FormData();
                formData.append('file', file);
                formData.append('target_column', target);
                formData.append('sensitive_columns', sensitive);
                formData.append('privileged_values', priv);
                formData.append('model_choice', document.getElementById('modelChoice').value);
                const modelFile = document.getElementById('modelFile').files[0];
                if (modelFile) formData.append('model_file', modelFile);
                const preprocFile = document.getElementById('preprocessorFile').files[0];
                if (preprocFile) formData.append('preprocessor_file', preprocFile);
                const shapSize = document.getElementById('shapSampleSize').value;
                if (shapSize) formData.append('shap_sample_size', shapSize);
                resultsDiv.style.display = 'block';
                document.getElementById('metricsGrid').innerHTML = '<div class="loading">⏳ Running audit...</div>';
                try {
                    const resp = await fetch('/audit/tabular/flexible', { method: 'POST', body: formData });
                    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                    const data = await resp.json();
                    displayResults(data);
                } catch(e) {
                    document.getElementById('metricsGrid').innerHTML = `<div class="error">❌ Error: ${e.message}</div>`;
                }
            });

            function displayResults(data) {
                const overall = data.overall;
                const verdictClass = overall.verdict === 'FAIL' ? 'verdict-fail' : 'verdict-pass';
                const metricsHtml = `
                    <div class="metric-card"><div class="metric-value">${overall.accuracy.toFixed(4)}</div><div>Accuracy</div></div>
                    <div class="metric-card"><div class="metric-value">${overall.disparate_impact.toFixed(4)}</div><div>Disparate Impact</div></div>
                    <div class="metric-card"><div class="metric-value">${overall.stat_parity_diff.toFixed(4)}</div><div>Stat. Parity Diff</div></div>
                    <div class="metric-card"><div class="metric-value">${overall.equal_opportunity_diff !== null ? overall.equal_opportunity_diff.toFixed(4) : 'N/A'}</div><div>Equal Opp. Diff</div></div>
                    <div class="metric-card"><div class="metric-value ${verdictClass}">${overall.verdict}</div><div>Verdict</div></div>
                `;
                document.getElementById('metricsGrid').innerHTML = metricsHtml;
                document.getElementById('verdictBadge').innerHTML = `<span class="${verdictClass}" style="font-size:1.2rem;">Verdict: ${overall.verdict}</span>`;
                const recs = data.recommendations || [];
                document.getElementById('recommendations').innerHTML = `<strong>💡 Recommendations:</strong>${recs.length ? `<ul>${recs.map(r=>`<li>${r}</li>`).join('')}</ul>` : '<p>None</p>'}`;
                const groups = data.groups || [];
                let groupsHtml = '<table style="width:100%; border-collapse: collapse;"><tr><th>Group</th><th>Accuracy</th><th>Precision</th><th>Recall</th></tr>';
                for (const g of groups) groupsHtml += `<tr><td>${g.group_name}</td><td>${g.metrics.accuracy?.toFixed(4) || '-'}</td><td>${g.metrics.precision?.toFixed(4) || '-'}</td><td>${g.metrics.recall?.toFixed(4) || '-'}</td></tr>`;
                groupsHtml += '</table>';
                document.getElementById('groupsTable').innerHTML = groupsHtml;
                const charts = data.charts || {};
                const chartNames = { 'eda_gender':'EDA Gender','eda_race':'EDA Race','disparity':'Disparity','metrics':'Fairness Metrics','debiasing':'Debiasing','shap_summary':'SHAP Summary','shap_bar':'SHAP Bar','shap_force':'SHAP Force','shap_dependence':'SHAP Dependence' };
                let chartsHtml = '';
                for (const [k, b64] of Object.entries(charts)) if(b64) chartsHtml += `<div class="chart-card"><h3>${chartNames[k]||k}</h3><img src="data:image/png;base64,${b64}"></div>`;
                document.getElementById('chartsContainer').innerHTML = chartsHtml || '<p>No charts.</p>';
                const debComp = data.debiasing_comparison || {};
                let debHtml = '<table style="width:100%;"><tr><th>Method</th><th>Accuracy</th><th>DI</th><th>Verdict</th></tr>';
                for (const [m, v] of Object.entries(debComp)) if(v.accuracy!==undefined) debHtml += `<tr><td>${m}</td><td>${v.accuracy.toFixed(4)}</td><td>${v.disparate_impact?.toFixed(4)||'N/A'}</td><td>${v.verdict||'N/A'}</td></tr>`;
                debHtml += '</table>';
                document.getElementById('debiasingComparison').innerHTML = debHtml;
                const expl = data.explanation_summary || {};
                let explHtml = '';
                if(expl.verdict_explanation) explHtml += `<p><strong>📌 Verdict Explanation:</strong> ${expl.verdict_explanation}</p>`;
                if(expl.suggestions?.length) explHtml += `<p><strong>🛠️ Suggestions:</strong></p><ul>${expl.suggestions.map(s=>`<li>${s}</li>`).join('')}</ul>`;
                if(expl.metric_descriptions) explHtml += `<details><summary>📖 Metric Descriptions</summary><ul>${Object.entries(expl.metric_descriptions).map(([k,d])=>`<li><strong>${k}:</strong> ${d}</li>`).join('')}</ul></details>`;
                document.getElementById('explanationSummary').innerHTML = explHtml || '<p>No explanation.</p>';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)