# 📊 AI-Powered Visualization Maker (Stable Edition)

An enterprise-ready, interactive self-service data engineering and visualization application built with **Streamlit**, **Plotly**, and **Groq LLM**.
This application acts as an automated analytics layer, enabling technical generalists and analysts to transition instantly from multi-sheet raw files to pristine dashboards, automated aggregation pipelines, and deep-dive conversational AI insights.

---

## 🚀 Core Features

### 📋 1. Advanced Data Engineering Sandbox
* **Dynamic Multi-Sheet Loading:** Safely ingests local CSV or multi-tab Excel (`.xlsx`) books into localized memory mapping structures.
* **Smart Inner Join Core:** Automatically identifies common primary/foreign key columns across disjoint datasets and enables one-click inner merges (`pd.merge`).
* **Aggregation/Group-By Builder:** Implements a declarative SQL-like data transformation workbench right in the UI (`sum`, `mean`, `count`, `min`, `max`).
* **Refined Data Export:** Clean export pathways to download completely transformed, inner-joined, or filtered states back into standardized CSV files.

### 📊 2. High-Performance Visual Canvas (Power BI / Tableau Sizing)
* **Two Operating Canvas Workflows:**
  1. **Executive Auto-Dashboard:** Instantly deploys a beautifully configured, multi-variable 2x2 report plane (Distribution, Composition, Segment Comparison, and Correlation).
  2. **Custom Layout Builder:** Allows an on-demand checklist rendering of **12 professional chart matrix configurations** (including Box Plots, Funnel Pipelines, Radar Webs, and Sunburst Hierarchical Wheels).
* **Pixel-Perfect Alignment:** Locked aspect ratios (`height=380`) mirror enterprise BI interfaces for consistent layouts across any data type.
* **On-the-Fly Conditional Formatting:** Interactive color-mapping injections highlighting targets above or below variable thresholds (e.g., Teal for High, Coral for Low).
* **Dynamic Metric ribbons:** Top-level dynamic KPI scorecards displaying continuous sums and transactional row scales.

### 🚨 3. Statistical Profiling & Outlier Scanning
* **Sigma Outlier Detector:** Evaluates targeted numerical parameters to spot rows running outside $2\sigma$ (Standard Deviations) from historical means, instantly exposing tracking spikes or data anomalies.

### 🤖 4. Context-Aware AI Analyst
* **Groq Llama 3.3 Engine:** Integrated chat window bound to an expert data analyst persona.
* **Defensive Token Consumption:** Automatically converts top-tier records of the parsed data matrix into structured context frames to feed deep analytical reasoning without overloading text window constraints.

---

## 🛠️ Architecture & Tech Stack

* **Front-End & State Controls:** Streamlit (Wide Layout Framework)
* **Data Processing Layer:** Pandas / NumPy
* **Visualization Engine:** Plotly Express Grid Rendering
* **AI Engine:** Groq API SDK (`llama-3.3-70b-versatile`)
* **File Processing Core:** OpenPyXL

---

## 📂 Project Structure

```text
