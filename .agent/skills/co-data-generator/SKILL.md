---
name: co-data-generator
description: Generates reproducible sample academic data (students, assessment marks, CO-PO mapping matrix, and exit survey) with deliberate CO attainment variance.
---

# Course Outcome Data Generator

This skill defines the generation of synthetic, realistic academic data adhering to NBA/NAAC outcome-based education benchmarks.

## Data Structure
All datasets are stored in `data/`:
1. `students.csv`: 60 students (`student_id`, `name`, `roll_no`).
2. `marks.csv`: Granular assessment records (`student_id`, `assessment`, `co`, `marks_obtained`, `max_marks`) across Quiz, Midterm, Assignment, and Final exam.
3. `co_po_matrix.csv`: Mapping matrix of 5 COs (CO1-CO5) to 6 POs (PO1-PO6) with strength ratings (0 = None, 1 = Low, 2 = Medium, 3 = High).
4. `survey.csv`: Indirect course-exit survey responses with 1-5 Likert scale ratings for each CO.

## Key Generation Rules
- Seed is locked to `42` for reproducibility.
- **CO1** is intentionally high performing (>80% attainment).
- **CO3** is intentionally weak (~48% attainment) to showcase at-risk student intervention and remediation recommendations.
- Other COs (CO2, CO4, CO5) vary between 62% and 75%.
- Script executes automatically on backend initialization if `data/` is missing or empty.
