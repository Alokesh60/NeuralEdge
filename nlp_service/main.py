from fastapi import FastAPI
from nlp import router
from nlp_service import load_models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.on_event("startup")
def startup():
    load_models()

app.include_router(router)

# @app.get("/")
# def health():
#     return {"status": "nlp service running"}

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     allow_credentials=True,
# )