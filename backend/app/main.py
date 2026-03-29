from fastapi import FastAPI
from app.routes import tabular, nlp, cv, combined

app = FastAPI(title="AI Bias Auditor")

app.include_router(tabular.router)
app.include_router(nlp.router)
app.include_router(cv.router)
app.include_router(combined.router)