import io
import pandas as pd
from fastapi.responses import StreamingResponse
from fastapi import UploadFile, File, Form
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, condecimal
from typing import Optional
import logging
from tagging import tag_ads
from dotenv import load_dotenv
from utils import *
import joblib
import google.generativeai as genai
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or "your_api_key_here")

# ---------- App & CORS ----------
app = FastAPI(title="Ad CTR Optimizer Backend")

# In production, replace "*" with your GitHub Pages origin, e.g.:
# allow_origins=["https://yourusername.github.io"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routes: root & health ----------


@app.get("/", include_in_schema=False)
def root():
    return JSONResponse(
        {"ok": True, "msg": "Backend is running. See /docs and POST /generate."}
    )
    # Or redirect:
    # return RedirectResponse(url="/docs")


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

# ---------- Request / Response Models ----------


class GenerateReq(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    # current CTR as a fraction (e.g., 0.025 for 2.5%)
    # accepts Decimal; use float(req.current_ctr)
    current_ctr: condecimal(ge=0, le=1)


class GenerateResp(BaseModel):
    new_title: str
    new_description: str
    probability_higher_ctr: float  # 0..1


# ---------- Startup: load model once ----------
logger = logging.getLogger("uvicorn")


@app.on_event("startup")
async def startup():
    global MODEL
    # MODEL = load_your_model()
    MODEL = object()  # placeholder
    logger.info("Backend starting; model loaded.")

# ---------- Utility ----------


def clamp(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: max(0, limit - 1)].rstrip() + "…"

# ---------- Main endpoint ----------


@app.post("/generate", response_model=GenerateResp)
async def generate(req: GenerateReq):
    # Convert Decimal to float if needed
    current_ctr = float(req.current_ctr)

    # TODO: Replace this block with your real model call
    # new_title, new_description, prob = MODEL.predict(req.title, req.description, current_ctr)
    new_title = f"{req.title} — Improved"
    new_description = (req.description + " Try it now.").strip()

    # Dummy probability for demo; replace with your calibrated estimate (0..1)
    probability_higher_ctr = 0.73

    return GenerateResp(
        new_title=new_title,
        new_description=new_description,
        probability_higher_ctr=probability_higher_ctr,
    )


@app.post('/optimize-file')
async def optimize_file(
    title: str = Form(''),
    description: str = Form(''),
    current_ctr: float = Form(0.0),  # fraction 0..1
    file: UploadFile = File(...),
):

    # 1) Load the uploaded file into a DataFrame (sync is fine inside async handler)
    if file.filename.lower().endswith('.csv'):
        df = pd.read_csv(file.file)
    else:
        df = pd.read_excel(file.file)

    # 2) Tag the ads using the pure helper
    df = await tag_ads(df)

    # 3) Train a Decision Tree Regressor
    result = train_tree_and_best_path(
        df,
        ctr_col=None,              # auto-detects "ctr"/"CTR"/"current_ctr" if None
        max_depth=4,
        min_samples_leaf=20
    )
    rule_path = result["best_leaf_rule_path"]
    result_payload = generate_and_rank_ad(
        title,
        description,
        rule_path,
        generate_ad_with_gemini
    )
    return result_payload
