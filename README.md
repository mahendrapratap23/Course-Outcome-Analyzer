<div align="center">

# 🎓 Course Outcome Achievement Analyzer
### **NBA &bull; NAAC Outcome-Based Education (OBE) Attainment Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  <b>Automates direct & indirect Course Outcome (CO) attainment calculation, Program Outcome (PO) roll-up, at-risk student intervention, and AI-powered faculty remediation roadmaps.</b>
</p>

[Quickstart](#-quickstart-guide) •
[Features](#-key-features) •
[Universal File Ingestion](#-universal-dataset-ingestion) •
[OBE Mathematics](#-mathematical-formulation) •
[API Reference](#-api-documentation) •
[Demo Script](#-2-minute-evaluation-demo)

---

</div>

## 🌟 Highlights

- **📂 Universal Drag-and-Drop Ingestion**: Drop **any dataset** anywhere onto the screen — `.pdf`, `.xlsx`, `.xls`, `.csv`, `.tsv`, or `.txt`.
- **⚡ Live 300ms Recalibration**: Dynamic sliders for Passing Threshold, Target Benchmark, and Direct/Indirect weights with instant cohort recomputation.
- **📈 Visual Attainment Analytics**: High-impact Bar Charts with benchmark target lines, Score Distribution Histograms, and a color-graded **CO-PO Correlation Heatmap**.
- **🎯 Proactive At-Risk Detection**: Automatically filters students underperforming in $\ge 2$ Course Outcomes with searchable, sortable rosters.
- **💡 Actionable Faculty Recommendations**: Pinpoints diagnostic root causes (Bloom's taxonomy bottlenecks) and provides 3-step intervention checklists.
- **🤖 Built-in Faculty AI Assistant**: Zero-crash local LLM (Ollama) integration with automatic rule-based fallback for executive reports and real-time QA.
- **📥 One-Click Export**: Download official evaluation reports (Markdown) and raw accreditation datasets (CSV).

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/mahendrapratap23/Course-Outcome-Analyzer.git
cd Course-Outcome-Analyzer
```

### 2. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Launch the Server
```bash
uvicorn main:app --reload
```
Navigate to **[http://localhost:8000](http://localhost:8000)** in your browser.

> *(If `/data` is empty, synthetic NBA benchmark data with 60 students is automatically generated on first launch).*

---

## 📂 Universal Dataset Ingestion

The platform features an intelligent, fault-tolerant parser (`file_parser.py`) that normalizes **any dataset structure** without manual reformatting:

| Format | Description | Parser Engine |
| :--- | :--- | :--- |
| **PDF (`.pdf`)** | Scanned/digital marks statements, question paper registers, scorecards | `pypdf` |
| **Excel (`.xlsx`, `.xls`)** | Multi-sheet faculty gradebooks, CIE sheets, semester marks spreadsheets | `openpyxl` |
| **Delimited (`.csv`, `.tsv`, `.txt`)** | Comma, tab, or semicolon separated marks tables | `pandas` |

### 🧠 Auto-Detection & Adaptive Mapping
- Auto-detects student identifiers (`Student ID`, `Roll No`, `USN`, `Name`).
- Detects arbitrary numeric columns (e.g. `Math`, `Physics`, `Quiz1`, `Midterm`) and maps them to outcome competencies.
- Auto-scales varying score ranges ($0–1$, $0–10$, $0–25$, $0–100$) into canonical percentage metrics.

---

## 📐 Mathematical Formulation (NBA / NAAC Tier-I/II)

### 1. Direct Attainment Percentage
For each Course Outcome $CO_i$ across all student aggregate assessment scores:

$$\text{Direct Attainment } (CO_i) = \left( \frac{\sum [ \text{Student Score} \ge \text{Threshold} ]}{\text{Total Students}} \right) \times 100$$

### 2. NBA 3-Tier Attainment Level
$$\text{Level}(P) = \begin{cases} 
3 & \text{if } P \ge 70\% \\ 
2 & \text{if } 60\% \le P < 70\% \\ 
1 & \text{if } 50\% \le P < 60\% \\ 
0 & \text{if } P < 50\% 
\end{cases}$$

### 3. Final Combined CO Attainment
Combines direct examination marks ($w_{\text{direct}}$, default $0.80$) with indirect exit surveys ($0.20$):

$$\text{Final Attainment} = (w_{\text{direct}} \times \text{Direct Pct}) + ((1 - w_{\text{direct}}) \times \text{Survey Pct})$$

### 4. Program Outcome (PO) Roll-Up
Weighted average roll-up based on the $5 \times 6$ CO-PO mapping matrix ($W \in \{0, 1, 2, 3\}$):

$$\text{PO}_j = \frac{\sum_{i=1}^{5} \left( \text{CO}_i \text{ Level} \times W_{i,j} \right)}{\sum_{i=1}^{5} W_{i,j} \quad (\text{where } W_{i,j} > 0)}$$

---

## 🧭 2-Minute Evaluation Demo

1. **Dashboard & KPIs (0:00 - 0:30)**:
   - Notice **CO1** attains **89.1%** (Green / Met) while **CO3** exhibits a critical deficit at **49.86%** (Red / Below Target).
   - Observe the **CO-PO Correlation Matrix**: See how `CO3`'s deficit pulls down `PO1`, `PO2`, and `PO3` due to its high correlation weight (3).
2. **Live Simulation Sliders (0:30 - 0:50)**:
   - Move the **Passing Threshold** slider from 60% down to 50%: observe instant 300ms debounced live recalculation turning CO3 green.
3. **At-Risk Students (0:50 - 1:15)**:
   - Switch to the **Students Needing Support** tab. Filter or sort by weak count to inspect students requiring urgent academic intervention.
4. **Action Plan & Executive Report (1:15 - 1:40)**:
   - Check the **Simple Action Plan** tab for diagnostic root causes and 3-step remediation checklists.
   - Click **Synthesize 1-Page Report** for an audit-ready executive evaluation.
5. **Universal Drag & Drop & Assistant (1:40 - 2:00)**:
   - Drag any `.xlsx`, `.pdf`, or `.csv` over the window to watch the entire dashboard recalculate.
   - Use the **Ask Questions (AI)** tab to query *"Which CO is weakest?"* or *"Who needs help in CO3?"*.

---

## 🔌 API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the single-page responsive application (`static/index.html`) |
| `POST` | `/api/upload` | Universal upload endpoint supporting `.pdf`, `.xlsx`, `.xls`, `.csv` |
| `GET` | `/api/summary` | Real-time KPIs: overall attainment, meeting counts, at-risk count |
| `GET` | `/api/attainment` | Per-CO direct %, indirect %, final %, NBA level, and deficit gap |
| `GET` | `/api/po` | Program Outcome roll-up values and mapping matrix weights |
| `GET` | `/api/distribution`| Score histogram bins for specified outcome (`?co=CO3`) |
| `GET` | `/api/at-risk` | Filtered list of students failing $\ge 2$ Course Outcomes |
| `GET` | `/api/insights` | Diagnostic root causes and 3-step remediation checklists |
| `POST` | `/api/ai-report` | 1-page executive evaluation synthesis (Ollama / rule fallback) |
| `POST` | `/api/chat` | Natural language question answering grounded in cohort records |
| `GET` | `/api/export/csv` | Download complete NBA calculation sheet as `.csv` |
| `GET` | `/api/export/report`| Download executive accreditation evaluation report as `.md` |
| `POST` | `/api/regenerate` | Restores the canonical 60-student benchmark dataset |

---

## 📁 Repository Structure

```text
Course-Outcome-Analyzer/
├── main.py                 # FastAPI backend, routing, and upload lifecycle
├── engine.py               # Pure-function mathematical OBE calculation engine
├── insights.py             # Diagnostic root-cause analysis, LLM report, & QA engine
├── file_parser.py          # Universal parser for PDF, Excel, and CSV datasets
├── generate_data.py        # Reproducible benchmark dataset generator (seed=42)
├── static/
│   └── index.html          # Single-page UI (Tailwind, Chart.js, Lucide Icons)
├── data/                   # Canonical CSV datasets (auto-created on startup)
│   ├── students.csv        # 60 student profiles
│   ├── marks.csv           # 1,200 granular assessment records
│   ├── co_po_matrix.csv    # 5x6 CO-PO correlation matrix
│   └── survey.csv          # Indirect course-exit survey responses
├── requirements.txt        # Production dependencies
└── README.md               # Documentation & Evaluation Guide
```

---

## 🛡️ Reliability & Zero-Crash Architecture

- **Ollama LLM Fallback**: If local Ollama (`http://localhost:11434`) is offline or times out (5s), the app silently falls back to a deterministic rule-based evaluation report.
- **Fault-Tolerant Data Ingestion**: Unstructured or partially complete files are automatically sanitized without crashing the server.
- **Zero Heavy Build Tooling**: Runs entirely on Python + FastAPI with lightweight CDN frontend dependencies.

---

<div align="center">
  <sub>Built for faculty, academic coordinators, and accreditation committees. MIT Licensed.</sub>
</div>
