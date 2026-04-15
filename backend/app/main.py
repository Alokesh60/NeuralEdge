from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.routes import tabular, nlp, cv, combined
from app.services import nlp_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    nlp_service.load_models()
    yield


app = FastAPI(
    title="NeuralEdge — AI Bias Auditor",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tabular.router)
app.include_router(nlp.router)
app.include_router(cv.router)
app.include_router(combined.router)


# Dashboard (clean version — keep this one)
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