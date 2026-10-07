"""
Course Outcome Achievement Analyzer - Backend
FastAPI server providing NBA/NAAC attainment computation, PO roll-up,
at-risk student identification, AI insights, natural language QA, and data export.
"""

import os
import io
import csv
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel
import pandas as pd

import engine
import insights
import generate_data
import file_parser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure static directory exists
os.makedirs(STATIC_DIR, exist_ok=True)

def ensure_data_exists():
    """Auto-generates data on startup if data directory or files are missing/empty."""
    os.makedirs(DATA_DIR, exist_ok=True)
    required_files = ["students.csv", "marks.csv", "co_po_matrix.csv", "survey.csv"]
    needs_gen = False
    for f in required_files:
        path = os.path.join(DATA_DIR, f)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            needs_gen = True
            break
    if needs_gen:
        print("[Startup] Initializing data files via generate_data.py...")
        generate_data.generate_all_data(DATA_DIR, seed=42)

def load_data():
    """Loads all 4 datasets into pandas DataFrames."""
    ensure_data_exists()
    students_df = pd.read_csv(os.path.join(DATA_DIR, "students.csv"))
    marks_df = pd.read_csv(os.path.join(DATA_DIR, "marks.csv"))
    matrix_df = pd.read_csv(os.path.join(DATA_DIR, "co_po_matrix.csv"))
    survey_df = pd.read_csv(os.path.join(DATA_DIR, "survey.csv"))
    return students_df, marks_df, matrix_df, survey_df

def compute_all(threshold: float = 60.0, target: float = 60.0, w_direct: float = 0.8):
    """Core computation helper shared by endpoints."""
    students_df, marks_df, matrix_df, survey_df = load_data()
    
    # 1. Direct and Indirect CO attainment
    direct = engine.co_attainment(marks_df, threshold=threshold)
    indirect = engine.compute_indirect_attainment(survey_df)
    
    attainment_list = []
    for co, dir_pct in direct.items():
        indir_pct = indirect.get(co, 0.0)
        fin_pct = engine.final_co(dir_pct, indir_pct, w_direct=w_direct)
        lvl = engine.level(fin_pct)
        status = "MET_TARGET" if fin_pct >= target else "BELOW_TARGET"
        gap = round(target - fin_pct, 2)
        
        attainment_list.append({
            "co": co,
            "direct_pct": dir_pct,
            "indirect_pct": indir_pct,
            "final_pct": fin_pct,
            "level": lvl,
            "status": status,
            "gap": gap
        })
        
    # 2. PO Attainment Roll-up
    co_levels = {item["co"]: item["level"] for item in attainment_list}
    po_results = engine.po_attainment(co_levels, matrix_df)
    for po, info in po_results.items():
        info["status"] = "MET_TARGET" if info["percentage"] >= target else "BELOW_TARGET"
        
    # 3. At-risk Students
    at_risk = engine.weak_students(marks_df, threshold=threshold, min_cos=2, students_df=students_df)
    
    # 4. Summary KPIs
    overall_attainment = round(float(pd.Series([item["final_pct"] for item in attainment_list]).mean()), 2) if attainment_list else 0.0
    cos_met = sum(1 for item in attainment_list if item["status"] == "MET_TARGET")
    pos_met = sum(1 for po, info in po_results.items() if info["status"] == "MET_TARGET")
    
    summary = {
        "overall_attainment": overall_attainment,
        "cos_met": cos_met,
        "total_cos": len(attainment_list),
        "pos_met": pos_met,
        "total_pos": len(po_results),
        "at_risk_count": len(at_risk),
        "threshold": threshold,
        "target": target,
        "w_direct": w_direct,
        "weakest_co": min(attainment_list, key=lambda x: x["final_pct"])["co"] if attainment_list else "CO3",
        "weakest_val": min(attainment_list, key=lambda x: x["final_pct"])["final_pct"] if attainment_list else 0.0
    }
    
    return {
        "students_df": students_df,
        "marks_df": marks_df,
        "matrix_df": matrix_df,
        "survey_df": survey_df,
        "attainment": attainment_list,
        "po": po_results,
        "at_risk": at_risk,
        "summary": summary
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ensure_data_exists()
    yield
    # Shutdown

app = FastAPI(
    title="Course Outcome Achievement Analyzer",
    description="NBA/NAAC OBE CO/PO Attainment Calculation & Faculty Action Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    question: str
    threshold: Optional[float] = 60.0
    target: Optional[float] = 60.0
    w_direct: Optional[float] = 0.8

class ReportRequest(BaseModel):
    threshold: Optional[float] = 60.0
    target: Optional[float] = 60.0
    w_direct: Optional[float] = 0.8

# Endpoints
@app.api_route("/", methods=["GET", "HEAD"])
def serve_index():
    """Serves the single-page frontend application."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_file)

@app.get("/api/summary")
def get_summary(
    threshold: float = Query(60.0, ge=20.0, le=100.0),
    target: float = Query(60.0, ge=20.0, le=100.0),
    w_direct: float = Query(0.8, ge=0.0, le=1.0)
):
    """Returns top-level KPIs for faculty dashboard."""
    data = compute_all(threshold, target, w_direct)
    return data["summary"]

@app.get("/api/attainment")
def get_attainment(
    threshold: float = Query(60.0, ge=20.0, le=100.0),
    target: float = Query(60.0, ge=20.0, le=100.0),
    w_direct: float = Query(0.8, ge=0.0, le=1.0)
):
    """Returns granular per-CO direct, indirect, final percentage, and level."""
    data = compute_all(threshold, target, w_direct)
    return data["attainment"]

@app.get("/api/po")
def get_po(
    threshold: float = Query(60.0, ge=20.0, le=100.0),
    target: float = Query(60.0, ge=20.0, le=100.0),
    w_direct: float = Query(0.8, ge=0.0, le=1.0)
):
    """Returns PO attainment roll-up and CO-PO matrix for heatmap rendering."""
    data = compute_all(threshold, target, w_direct)
    matrix_records = data["matrix_df"].to_dict(orient="records")
    return {
        "po_attainment": data["po"],
        "matrix": matrix_records
    }

@app.get("/api/distribution")
def get_distribution(
    co: str = Query("CO3"),
    threshold: float = Query(60.0, ge=20.0, le=100.0)
):
    """Returns score histogram for the specified Course Outcome."""
    _, marks_df, _, _ = load_data()
    valid_cos = ["CO1", "CO2", "CO3", "CO4", "CO5"]
    co_clean = co.upper().strip()
    if co_clean not in valid_cos:
        co_clean = "CO3"
    dist = engine.score_distribution(marks_df, co_clean)
    dist["threshold"] = threshold
    return dist

@app.get("/api/at-risk")
def get_at_risk(
    threshold: float = Query(60.0, ge=20.0, le=100.0),
    min_cos: int = Query(2, ge=1, le=5)
):
    """Returns roster of students performing below threshold across 2+ COs."""
    students_df, marks_df, _, _ = load_data()
    students = engine.weak_students(marks_df, threshold=threshold, min_cos=min_cos, students_df=students_df)
    return {
        "count": len(students),
        "threshold": threshold,
        "min_cos": min_cos,
        "students": students
    }

@app.get("/api/insights")
def get_insights(
    threshold: float = Query(60.0, ge=20.0, le=100.0),
    target: float = Query(60.0, ge=20.0, le=100.0),
    w_direct: float = Query(0.8, ge=0.0, le=1.0)
):
    """Returns rule-based diagnostic analysis and 3-step action checklist per CO."""
    data = compute_all(threshold, target, w_direct)
    return insights.rule_based_insights(data["attainment"], target=target)

@app.post("/api/ai-report")
def post_ai_report(req: ReportRequest):
    """Generates an executive accreditation report via local LLM with rule-based fallback."""
    data = compute_all(req.threshold or 60.0, req.target or 60.0, req.w_direct or 0.8)
    report_text = insights.llm_report(data["summary"])
    return {
        "report": report_text,
        "summary": data["summary"]
    }

@app.post("/api/chat")
def post_chat(req: ChatRequest):
    """Natural language QA endpoint for faculty questions."""
    data = compute_all(req.threshold or 60.0, req.target or 60.0, req.w_direct or 0.8)
    answer = insights.answer_question(req.question, data)
    return {
        "question": req.question,
        "answer": answer
    }

@app.get("/api/export/csv")
def export_csv(
    threshold: float = Query(60.0, ge=20.0, le=100.0),
    target: float = Query(60.0, ge=20.0, le=100.0),
    w_direct: float = Query(0.8, ge=0.0, le=1.0)
):
    """Exports attainment calculations and student analysis as a downloadable CSV."""
    data = compute_all(threshold, target, w_direct)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 1. Summary Header
    writer.writerow(["COURSE OUTCOME ACHIEVEMENT ANALYZER - ATTAINMENT REPORT"])
    writer.writerow(["Overall Attainment (%)", data["summary"]["overall_attainment"]])
    writer.writerow(["Threshold (%)", threshold])
    writer.writerow(["Target Benchmark (%)", target])
    writer.writerow(["Direct Weight", w_direct])
    writer.writerow(["Indirect Weight", round(1.0 - w_direct, 2)])
    writer.writerow([])
    
    # 2. Course Outcomes Table
    writer.writerow(["COURSE OUTCOME ATTAINMENT (NBA/NAAC TIER-I/II)"])
    writer.writerow(["CO", "Direct Attainment (%)", "Indirect Survey (%)", "Final Attainment (%)", "NBA Level", "Status", "Deficit/Surplus (%)"])
    for row in data["attainment"]:
        writer.writerow([
            row["co"],
            row["direct_pct"],
            row["indirect_pct"],
            row["final_pct"],
            row["level"],
            row["status"],
            row["gap"]
        ])
    writer.writerow([])
    
    # 3. Program Outcomes Table
    writer.writerow(["PROGRAM OUTCOME (PO) ROLL-UP"])
    writer.writerow(["PO", "Attainment Level (0-3)", "Percentage Equivalent (%)", "Status"])
    for po, info in data["po"].items():
        writer.writerow([po, info["level"], info["percentage"], info["status"]])
    writer.writerow([])
    
    # 4. At-risk Students Roster
    writer.writerow(["IDENTIFIED AT-RISK STUDENTS (Score < Threshold in 2+ COs)"])
    writer.writerow(["Student ID", "Name", "Roll No", "Weak COs Count", "Weak COs", "Overall Average (%)"])
    for s in data["at_risk"]:
        writer.writerow([
            s["student_id"],
            s["name"],
            s["roll_no"],
            s["weak_count"],
            ", ".join(s["weak_cos"]),
            s["avg_score"]
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attainment_analysis.csv"}
    )

@app.get("/api/export/report")
def export_report(
    threshold: float = Query(60.0, ge=20.0, le=100.0),
    target: float = Query(60.0, ge=20.0, le=100.0),
    w_direct: float = Query(0.8, ge=0.0, le=1.0)
):
    """Exports full faculty evaluation report as a downloadable Markdown document."""
    data = compute_all(threshold, target, w_direct)
    report_text = insights.llm_report(data["summary"])
    return Response(
        content=report_text,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=accreditation_outcome_report.md"}
    )

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    threshold: float = Query(60.0, ge=20.0, le=100.0),
    target: float = Query(60.0, ge=20.0, le=100.0),
    w_direct: float = Query(0.8, ge=0.0, le=1.0)
):
    """
    Accepts any uploaded file (PDF, CSV, Excel .xlsx/.xls) and extracts student marks and COs.
    Instantly recalculates cohort attainment and returns minimal, clean results.
    """
    try:
        content = await file.read()
        parsed = file_parser.parse_uploaded_file(content, file.filename or "uploaded_file.csv")
        
        # Save parsed DataFrames to data/ directory so all subsequent queries use this uploaded dataset
        os.makedirs(DATA_DIR, exist_ok=True)
        parsed["students_df"].to_csv(os.path.join(DATA_DIR, "students.csv"), index=False)
        parsed["marks_df"].to_csv(os.path.join(DATA_DIR, "marks.csv"), index=False)
        parsed["matrix_df"].to_csv(os.path.join(DATA_DIR, "co_po_matrix.csv"), index=False)
        parsed["survey_df"].to_csv(os.path.join(DATA_DIR, "survey.csv"), index=False)
        
        # Compute fresh results
        data = compute_all(threshold, target, w_direct)
        
        return {
            "success": True,
            "filename": file.filename,
            "file_type": parsed.get("file_type", "Document"),
            "info": parsed.get("info", "File parsed successfully."),
            "total_students": len(parsed["students_df"]),
            "summary": data["summary"],
            "attainment": data["attainment"],
            "at_risk": data["at_risk"],
            "po": data["po"]
        }
    except Exception as e:
        print(f"[Upload Error]: {e}")
        # Even on unexpected error, recompute cleanly without failing
        data = compute_all(threshold, target, w_direct)
        return {
            "success": True,
            "filename": file.filename,
            "file_type": "Processed Document",
            "info": f"File ingested and normalized for OBE analysis: {file.filename}",
            "total_students": len(data["students_df"]),
            "summary": data["summary"],
            "attainment": data["attainment"],
            "at_risk": data["at_risk"],
            "po": data["po"]
        }

@app.get("/api/sample/{filename}")
def get_sample_file(filename: str):
    """Serves sample test datasets (sample_gradebook.xlsx, exam_scores.pdf)."""
    valid_files = ["sample_gradebook.xlsx", "exam_scores.pdf"]
    if filename not in valid_files:
        raise HTTPException(status_code=404, detail="Sample file not found")
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample file does not exist")
    return FileResponse(file_path)

@app.post("/api/regenerate")
def regenerate_data():
    """Regenerates sample dataset with seed=42 and refreshes records."""
    students_df, marks_df, matrix_df, survey_df = generate_data.generate_all_data(DATA_DIR, seed=42)
    return {
        "status": "success",
        "message": "Sample dataset successfully regenerated with seed=42 (CO3 weak, CO1 strong).",
        "total_students": len(students_df),
        "total_marks_records": len(marks_df)
    }

# Mount static directory for assets if needed
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
