# 🛡️ SafetySense AI Auditor

**Enterprise-Grade HSE Compliance & Personal Protective Equipment (PPE) Detection System**
> **Engineered by Rushikesh Naik (Data Analyst / AI Developer)**

---

## 📖 Overview

**SafetySense AI Auditor** is a high-reliability, automated computer vision application built to streamline Health, Safety, and Environment (HSE) site compliance inspections. 

By leveraging the cutting-edge **Google Gemini 3 Flash** multimodal architecture, this system analyzes worksite imagery in real-time. It validates the active usage of mandatory field gear—such as hard hats (helmets), high-visibility vests, and protective gloves—while diagnosing hidden structural risks, open hazards, or house-keeping discrepancies.

Unlike fragile text-parsing wrappers, this production-ready application uses native API **Structured Outputs** via Pydantic schemas, guaranteeing zero-fail JSON data transmission directly into an enterprise metrics interface.

---

## ✨ Key Features

* **📷 Multimodal Computer Vision Engine:** Captures, optimizes, and processes site photographic assets instantly using advanced visual sequence alignment.
* **🦺 Rigorous PPE Validation:** Cross-references field workers against strict compliance baselines (detecting presence/absence of hard hats, high-vis vests, hand protection, and boots).
* **⚠️ Active Hazard Diagnosis:** Identifies site vulnerabilities including unmitigated structural openings, trip hazards, and heavy machinery proximity risks.
* **🛡️ Zero-Fail Structured Outputs:** Enforces a rigid JSON data schema (`status`, `score`, `finding`) using Pydantic, bypassing error-prone Regex parsing completely.
* **⚡ High-Efficiency Optimization:** Automatically downscales uploaded high-resolution mobile/field assets to a strict `1920px` boundary layer to optimize network payload handling and minimize API latency.
* **📊 Clean Operational Metrics:** Renders real-time native pass/fail alert notification layouts alongside high-visibility numeric index scorecards.
* **📥 One-Click Offline Manifest Export:** Instantly generates and packages text-based compliance manifests complete with localized timestamps for legacy reporting pipelines.

---
