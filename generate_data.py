"""
Data Generator for Course Outcome Achievement Analyzer
Generates reproducible academic datasets with deliberate CO3 weakness (~48%) and strong CO1 (~83%).
Seed: 42
"""

import os
import random
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Shaurya", "Atharv", "Advik", "Pranav", "Advaith", "Dhruv", "Kabir", "Rudra", "Rohan", "Ananya",
    "Diya", "Saanvi", "Ira", "Aadhya", "Aarohi", "Anushka", "Myra", "Avani", "Navya", "Riya",
    "Pari", "Ahana", "Tanvi", "Prisha", "Isha", "Kavya", "Tara", "Anika", "Meera", "Pooja",
    "Rahul", "Siddharth", "Vikram", "Neha", "Priya", "Sneha", "Kunal", "Amit", "Varun", "Deepak",
    "Manish", "Gaurav", "Harsh", "Akash", "Swati", "Shreya", "Nidhi", "Simran", "Preeti", "Kriti"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Iyer", "Rao", "Reddy", "Nair", "Mehta", "Joshi", "Gupta",
    "Kumar", "Singh", "Chopra", "Malhotra", "Deshmukh", "Kulkarni", "Bose", "Chatterjee", "Banerjee", "Das"
]

def generate_students(n=60):
    """Generates 60 unique student records (id, name, roll_no)."""
    students = []
    for i in range(1, n + 1):
        s_id = f"S{i:02d}"
        first = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        last = LAST_NAMES[((i - 1) * 3) % len(LAST_NAMES)]
        name = f"{first} {last}"
        roll_no = f"CS2024-{i:03d}"
        students.append({"student_id": s_id, "name": name, "roll_no": roll_no})
    return pd.DataFrame(students)

def generate_marks(students_df):
    """
    Generates assessment marks across Quiz, Midterm, Assignment, and Final exam.
    CO1: strong (~83% attainment >= 60%)
    CO2: good (~68% attainment >= 60%)
    CO3: deliberately weak (~48% attainment >= 60%)
    CO4: solid (~72% attainment >= 60%)
    CO5: solid (~75% attainment >= 60%)
    """
    assessments = [
        ("Quiz", 10),
        ("Midterm", 25),
        ("Assignment", 15),
        ("Final", 50)
    ]
    cos = ["CO1", "CO2", "CO3", "CO4", "CO5"]
    
    # Target distribution of student skill per CO
    # CO3 is designed so ~29 students score >= 60% (48.3% attainment)
    records = []
    
    # Pre-assign baseline proficiencies for each student
    # Base capability (normal distribution)
    base_ability = np.random.normal(loc=0.65, scale=0.15, size=len(students_df))
    base_ability = np.clip(base_ability, 0.25, 0.95)
    
    # Sort students by ability so some are consistently struggling (at-risk)
    sorted_indices = np.argsort(base_ability)
    
    for idx, row in students_df.iterrows():
        s_id = row["student_id"]
        rank = np.where(sorted_indices == idx)[0][0]
        
        # CO-specific target percentage for this student
        # CO1: High attainment across the cohort
        co1_pct = np.clip(0.55 + 0.35 * (rank / len(students_df)) + np.random.normal(0, 0.05), 0.35, 0.98)
        
        # CO2: Normal attainment
        co2_pct = np.clip(0.40 + 0.45 * (rank / len(students_df)) + np.random.normal(0, 0.06), 0.25, 0.96)
        
        # CO3: Deliberately weak! Top 48% pass threshold (approx ranks 31-59)
        # Ranks 0 to 30 will score below 60%
        if rank < 31: # 31 students below threshold (~51.7% failing threshold -> 48.3% passing)
            co3_pct = np.clip(0.32 + 0.25 * (rank / 31.0) + np.random.normal(0, 0.03), 0.20, 0.58)
        else:
            co3_pct = np.clip(0.61 + 0.30 * ((rank - 31) / 29.0) + np.random.normal(0, 0.03), 0.60, 0.95)
            
        # CO4: Good attainment (~72%)
        co4_pct = np.clip(0.42 + 0.46 * (rank / len(students_df)) + np.random.normal(0, 0.05), 0.28, 0.96)
        
        # CO5: Good attainment (~75%)
        co5_pct = np.clip(0.45 + 0.45 * (rank / len(students_df)) + np.random.normal(0, 0.05), 0.30, 0.97)
        
        co_pcts = {
            "CO1": co1_pct,
            "CO2": co2_pct,
            "CO3": co3_pct,
            "CO4": co4_pct,
            "CO5": co5_pct
        }
        
        for assess_name, max_m in assessments:
            for co in cos:
                target_pct = co_pcts[co]
                # Small per-assessment variance
                actual_pct = np.clip(target_pct + np.random.normal(0, 0.04), 0.05, 1.0)
                obtained = round(actual_pct * max_m, 1)
                # Ensure it does not exceed max_marks
                obtained = min(obtained, float(max_m))
                records.append({
                    "student_id": s_id,
                    "assessment": assess_name,
                    "co": co,
                    "marks_obtained": obtained,
                    "max_marks": max_m
                })
                
    return pd.DataFrame(records)

def generate_co_po_matrix():
    """
    Standard NBA 5 COs x 6 POs mapping matrix.
    Values: 0 (No correlation), 1 (Low), 2 (Medium), 3 (High).
    """
    matrix_data = [
        {"co": "CO1", "PO1": 3, "PO2": 2, "PO3": 1, "PO4": 0, "PO5": 0, "PO6": 1},
        {"co": "CO2", "PO1": 2, "PO2": 3, "PO3": 2, "PO4": 1, "PO5": 1, "PO6": 0},
        {"co": "CO3", "PO1": 3, "PO2": 3, "PO3": 3, "PO4": 2, "PO5": 1, "PO6": 0}, # Key analytical/design outcome
        {"co": "CO4", "PO1": 1, "PO2": 2, "PO3": 3, "PO4": 3, "PO5": 2, "PO6": 1},
        {"co": "CO5", "PO1": 1, "PO2": 1, "PO3": 2, "PO4": 2, "PO5": 3, "PO6": 2},
    ]
    return pd.DataFrame(matrix_data)

def generate_survey(students_df):
    """
    Course-exit survey: indirect attainment on 1-5 Likert scale.
    Reflects student perception, with CO3 noticeably lower.
    """
    surveys = []
    for idx, row in students_df.iterrows():
        s_id = row["student_id"]
        # CO1 high satisfaction (4.2 mean)
        co1 = int(np.clip(np.random.choice([4, 5], p=[0.4, 0.6]), 1, 5))
        # CO2 moderate (3.7 mean)
        co2 = int(np.clip(np.random.choice([3, 4, 5], p=[0.3, 0.5, 0.2]), 1, 5))
        # CO3 lower satisfaction reflecting difficulty (2.8 mean)
        co3 = int(np.clip(np.random.choice([2, 3, 4], p=[0.4, 0.45, 0.15]), 1, 5))
        # CO4 good (3.8 mean)
        co4 = int(np.clip(np.random.choice([3, 4, 5], p=[0.25, 0.55, 0.2]), 1, 5))
        # CO5 good (3.9 mean)
        co5 = int(np.clip(np.random.choice([3, 4, 5], p=[0.2, 0.5, 0.3]), 1, 5))
        
        surveys.append({
            "student_id": s_id,
            "CO1": co1,
            "CO2": co2,
            "CO3": co3,
            "CO4": co4,
            "CO5": co5
        })
    return pd.DataFrame(surveys)

def generate_all_data(output_dir=DATA_DIR, seed=42):
    """Generates all 4 CSV datasets and saves them in output_dir."""
    np.random.seed(seed)
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    students_df = generate_students(60)
    marks_df = generate_marks(students_df)
    matrix_df = generate_co_po_matrix()
    survey_df = generate_survey(students_df)
    
    students_path = os.path.join(output_dir, "students.csv")
    marks_path = os.path.join(output_dir, "marks.csv")
    matrix_path = os.path.join(output_dir, "co_po_matrix.csv")
    survey_path = os.path.join(output_dir, "survey.csv")
    
    students_df.to_csv(students_path, index=False)
    marks_df.to_csv(marks_path, index=False)
    matrix_df.to_csv(matrix_path, index=False)
    survey_df.to_csv(survey_path, index=False)
    
    print(f"[Data Generator] Successfully generated 4 CSV datasets in: {output_dir}")
    return students_df, marks_df, matrix_df, survey_df

if __name__ == "__main__":
    generate_all_data()
