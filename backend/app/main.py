from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import tabular, nlp, cv, combined
from app.services import nlp_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup — loads all models into memory
    nlp_service.load_models()
    yield
    # Runs on shutdown — cleanup if needed

app = FastAPI(title="NeuralEdge — AI Bias Auditor", lifespan=lifespan)

# Allow the standalone frontend (file:// or localhost) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # tighten to specific origin before production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tabular.router)
app.include_router(nlp.router)
app.include_router(cv.router)
app.include_router(combined.router)