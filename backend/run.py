import os

# ── Force ALL HuggingFace / PyTorch cache to E drive ──────────────────────────
# This must happen before uvicorn (and therefore before any transformers import).
# Without this, HF defaults to C:\Users\<user>\.cache\huggingface which fills C drive.
_HF_CACHE = r"C:\Users\USER\.cache\huggingface"
os.environ.setdefault("HF_HOME",            _HF_CACHE)
os.environ.setdefault("TRANSFORMERS_CACHE",  os.path.join(_HF_CACHE, "hub"))
os.environ.setdefault("HF_DATASETS_CACHE",   os.path.join(_HF_CACHE, "datasets"))
os.environ.setdefault("TORCH_HOME",          os.path.join(_HF_CACHE, "torch"))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
