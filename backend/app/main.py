# main.py — no changes needed, already correct.
# Included here just so you have the full picture.
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.routes import tabular
# from app.routes import combined   # uncomment when you wire NLP/CV via HTTP


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="NeuralEdge — AI Bias Auditor",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(tabular.router)
# app.include_router(combined.router)   # uncomment when ready


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return """
    <html>
        <head><title>NeuralEdge Dashboard</title></head>
        <body>
            <h1>NeuralEdge Bias Auditor</h1>
            <p>Backend is running successfully 🚀</p>
        </body>
    </html>
    """

@app.get("/")
def health():
    return {"status": "alive"}