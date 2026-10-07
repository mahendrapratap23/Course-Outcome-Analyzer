"""
Attainment Engine for Course Outcome Achievement Analyzer
Pure computational functions without web dependencies.
Compliant with NBA/NAAC Outcome-Based Education (OBE) guidelines.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

def compute_student_co_scores(marks_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes percentage score for each student per CO.
    Returns DataFrame indexed by student_id with CO columns containing percentage (0-100).
    """
    grouped = marks_df.groupby(["student_id", "co"]).agg({
        "marks_obtained": "sum",
        "max_marks": "sum"
    }).reset_index()
    
    grouped["pct_score"] = (grouped["marks_obtained"] / grouped["max_marks"]) * 100.0
    pivot_df = grouped.pivot(index="student_id", columns="co", values="pct_score").fillna(0.0)
    return pivot_df

def co_attainment(marks_df: pd.DataFrame, threshold: float = 60.0) -> Dict[str, float]:
    """
    Direct attainment calculation:
    Percentage of students scoring >= threshold% in each CO.
    """
    student_scores = compute_student_co_scores(marks_df)
    total_students = len(student_scores)
    
    if total_students == 0:
        return {}
        
    attainment = {}
    for co in student_scores.columns:
        students_passed = (student_scores[co] >= threshold).sum()
        pct = round(float((students_passed / total_students) * 100.0), 2)
        attainment[co] = pct
        
    return attainment

def level(pct: float) -> int:
    """
    NBA 3-tier attainment level classification:
    Level 3: >= 70%
    Level 2: 60% - 69.99%
    Level 1: 50% - 59.99%
    Level 0: < 50%
    """
    if pct >= 70.0:
        return 3
    elif pct >= 60.0:
        return 2
    elif pct >= 50.0:
        return 1
    return 0

def compute_indirect_attainment(survey_df: pd.DataFrame) -> Dict[str, float]:
    """
    Indirect attainment from 1-5 Likert exit survey.
    Calculates percentage equivalent: (mean_score / 5.0) * 100.
    """
    co_cols = [c for c in survey_df.columns if c.startswith("CO")]
    indirect = {}
    for co in co_cols:
        mean_val = float(survey_df[co].mean())
        # Convert 1-5 scale to percentage (e.g. 5 -> 100%, 3 -> 60%)
        indirect[co] = round((mean_val / 5.0) * 100.0, 2)
    return indirect

def final_co(direct_pct: float, indirect_pct: float, w_direct: float = 0.8) -> float:
    """
    Weighted combination of direct and indirect attainment.
    Standard NBA weight: 80% Direct Assessment + 20% Indirect (Exit Survey).
    """
    w_indirect = 1.0 - w_direct
    val = (w_direct * direct_pct) + (w_indirect * indirect_pct)
    return round(float(val), 2)

def po_attainment(co_levels: Dict[str, Any], co_po_matrix: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Weighted-average roll-up of CO attainment into Program Outcomes (PO1-PO6).
    PO_attainment = Sum(CO_attainment * Weight) / Sum(Weight for non-zero weights)
    
    co_levels can be either level ints (0-3) or percentages. We compute both.
    """
    po_cols = [c for c in co_po_matrix.columns if c.startswith("PO")]
    results = {}
    
    matrix = co_po_matrix.set_index("co")
    
    for po in po_cols:
        weighted_level_sum = 0.0
        weighted_pct_sum = 0.0
        total_weight = 0.0
        
        for co, row in matrix.iterrows():
            weight = float(row[po])
            if weight > 0 and co in co_levels:
                total_weight += weight
                co_val = co_levels[co]
                
                # Check if co_val is dict or float
                if isinstance(co_val, dict):
                    lvl = co_val.get("level", 0)
                    pct = co_val.get("final_pct", 0.0)
                elif isinstance(co_val, (int, float)):
                    lvl = level(co_val) if co_val > 3 else co_val
                    pct = co_val if co_val > 3 else co_val * (100.0 / 3.0)
                else:
                    lvl = 0
                    pct = 0.0
                    
                weighted_level_sum += lvl * weight
                weighted_pct_sum += pct * weight
                
        if total_weight > 0:
            avg_level = round(weighted_level_sum / total_weight, 2)
            avg_pct = round(weighted_pct_sum / total_weight, 2)
        else:
            avg_level = 0.0
            avg_pct = 0.0
            
        results[po] = {
            "level": avg_level,
            "percentage": avg_pct,
            "total_weight": total_weight
        }
        
    return results

def weak_students(
    marks_df: pd.DataFrame,
    threshold: float = 60.0,
    min_cos: int = 2,
    students_df: Optional[pd.DataFrame] = None
) -> List[Dict[str, Any]]:
    """
    Identifies students scoring below the threshold in at least min_cos Course Outcomes.
    Returns list of records with student ID, name, roll_no, weak COs list, and average score.
    """
    student_scores = compute_student_co_scores(marks_df)
    
    # Map student details if provided
    student_meta = {}
    if students_df is not None:
        for _, row in students_df.iterrows():
            student_meta[row["student_id"]] = {
                "name": row.get("name", "Student " + str(row["student_id"])),
                "roll_no": row.get("roll_no", "")
            }
            
    at_risk_list = []
    
    for s_id, scores in student_scores.iterrows():
        weak_cos = [co for co, val in scores.items() if val < threshold]
        
        if len(weak_cos) >= min_cos:
            meta = student_meta.get(s_id, {"name": f"Student {s_id}", "roll_no": s_id})
            avg_score = round(float(scores.mean()), 1)
            
            # Detailed scores dict
            detailed = {co: round(float(val), 1) for co, val in scores.items()}
            
            at_risk_list.append({
                "student_id": s_id,
                "name": meta["name"],
                "roll_no": meta["roll_no"],
                "weak_cos": weak_cos,
                "weak_count": len(weak_cos),
                "avg_score": avg_score,
                "co_scores": detailed
            })
            
    # Sort descending by weak count, then ascending by average score
    at_risk_list.sort(key=lambda x: (-x["weak_count"], x["avg_score"]))
    return at_risk_list

def score_distribution(marks_df: pd.DataFrame, co: str) -> Dict[str, Any]:
    """
    Computes histogram distribution for a specific Course Outcome.
    Standard academic score bins: 0-20%, 20-40%, 40-60%, 60-80%, 80-100%.
    """
    student_scores = compute_student_co_scores(marks_df)
    
    if co not in student_scores.columns:
        return {"co": co, "bins": [], "counts": [], "average": 0.0}
        
    scores = student_scores[co].values
    
    bin_labels = ["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"]
    bins_edges = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0]
    
    counts, _ = np.histogram(scores, bins=bins_edges)
    
    return {
        "co": co,
        "bins": bin_labels,
        "counts": [int(c) for c in counts],
        "average": round(float(np.mean(scores)), 1),
        "min": round(float(np.min(scores)), 1),
        "max": round(float(np.max(scores)), 1),
        "total_students": len(scores)
    }
