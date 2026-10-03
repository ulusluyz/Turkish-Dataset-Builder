import os
import json
import yaml
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dataset_cleaner.pipeline import ProcessingPipeline

app = FastAPI(title="NEXT LLM Dataset Cleaner & Quality Control")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

pipeline_instance = None

def get_default_config():
    config_path = os.path.join(os.getcwd(), "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/analyze")
async def analyze_endpoint(input_dir: str = Form(...)):
    config = get_default_config()
    pipe = ProcessingPipeline(input_dir, "/tmp/dummy_out", config)
    results = pipe.run_analyze()
    return JSONResponse(results)

@app.post("/api/build")
async def build_endpoint(input_dir: str = Form(...), output_dir: str = Form(...)):
    global pipeline_instance
    config = get_default_config()
    pipeline_instance = ProcessingPipeline(input_dir, output_dir, config)
    stats = pipeline_instance.run_build()
    return JSONResponse(stats)

@app.get("/api/status")
async def status_endpoint():
    if pipeline_instance:
        return JSONResponse(pipeline_instance.stats)
    return JSONResponse({"status": "idle"})
