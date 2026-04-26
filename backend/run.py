import os
import uvicorn

# FIX: The original file hardcoded Windows paths like C:\Users\USER\.cache\huggingface
# which crashes on Render (Linux). Those lines are removed entirely.
# NLP and CV are deployed separately to Hugging Face, so there is nothing
# HuggingFace/PyTorch related to configure in this backend.

# FIX: Render injects $PORT dynamically. host must be 0.0.0.0 (not 127.0.0.1)
# so Render's health checker and proxy can reach the app.
# NOTE: Render does NOT use run.py — it uses the Procfile start command.
# This file is kept for local development only.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)