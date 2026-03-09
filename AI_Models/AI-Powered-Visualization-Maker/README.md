# AI-Powered Visualization Maker

Building dashboards usually takes hours of cleaning data and dragging-and-dropping charts. I built this tool to speed up that process by using AI to handle the heavy lifting. This app allows anyone to upload a dataset and get instant, professional-grade insights through an interactive dashboard and an AI-driven chat interface.

## 📊 What this app does
I designed this tool to be a "one-stop shop" for data exploration. Instead of writing complex code to see your data, you can just upload your file and start analyzing.

* **Smart Data Loading:** Supports both CSV and multi-sheet Excel files.
* **Automated Joins:** If you upload multiple sheets, the app helps you join them by detecting common keys and relationship cardinality (1:M, M:1, etc.).
* **Dynamic Dashboarding:** Automatically generates distribution, composition, and correlation charts.
* **AI Data Analyst:** There is a built-in chat window powered by Groq and Llama 3. You can ask it specific questions like "Which order IDs are in the Electronics category?" and it will scan the actual data rows to give you an answer.

## 🛠️ The Tech Stack
I kept the architecture lightweight but powerful:
* **Python** – The core logic.
* **Streamlit** – For the web interface and UI.
* **Plotly** – For the interactive visualizations.
* **Groq & Google Gemini** – To power the data reasoning and structural logic.

## 🚀 How to use it
1. Upload your dataset (Excel or CSV).
2. Use the sidebar to select your visual theme and filter the columns you care about.
3. If you have specific questions, type them into the AI Chat at the bottom to get instant row-level analysis.

## 💡 Why I built this
As a Data Analyst, I wanted to create a bridge between raw data and decision-making. This project was a great way for me to practice integrating Generative AI with traditional BI tools, making data more accessible for people who aren't necessarily "tech-savvy" but need quick answers.
