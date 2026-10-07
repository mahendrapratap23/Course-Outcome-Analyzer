---
name: insight-writer
description: Generates actionable academic remediation recommendations, local LLM executive reports with zero-failure fallback, and natural language QA parsing.
---

# Insight Writer

Analyzes attainment gaps against institution target benchmarks and synthesizes pedagogical remediation plans.

## Capabilities
1. **`rule_based_insights(attainment, target=60)`**:
   - For Course Outcomes under target: identifies attainment gap %, diagnoses primary instructional bottleneck, and prescribes 3 concrete intervention steps (e.g. remedial problem-solving workshops, targeted practice sets, assessment blueprint redesign, peer mentoring).
   - For Course Outcomes meeting/exceeding target: generates commendation and enrichment advice.
2. **`llm_report(summary)`**:
   - Asynchronously or synchronously attempts Ollama call (`http://localhost:11434`, llama3/phi3, strict 5s timeout).
   - Automatically and silently falls back to a formatted multi-section rule-based faculty report on ANY connection or model error.
3. **`answer_question(question, data)`**:
   - Fast semantic and keyword parsing for common faculty queries ("weakest CO", "who needs help in CO3", "overall attainment", "which POs are below target").
   - Synthesizes clear, data-grounded responses instantly.
