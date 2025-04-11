
# 📊 AI Business Report Generator (for CA Firms & SMEs)

This is a Streamlit-powered web app that analyzes financial data (from Excel or CSV files) and generates a business report. It includes AI-generated insights using OpenAI's GPT-3.5 model and allows users to download the analysis as a PDF or receive it via email.

---

## 🚀 Features

- Upload `.csv` or `.xlsx` financial data
- Automatic detection of key columns like **Revenue**, **Expenses**, and **Date**
- Visualizes revenue trends over time
- Calculates **Total Revenue**, **Expenses**, and **Net Profit**
- Uses GPT-3.5 to generate a professional summary
- Exports the analysis to a **PDF**
- Optionally send the PDF to an email address
- Built with ❤️ using **Streamlit**, **Pandas**, **Matplotlib**, **FPDF**, and **OpenAI API**

---

## 📁 How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/adhavannn/ai-report-generator.git
cd ai-report-generator
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Set API Key

Create a `.streamlit/secrets.toml` file with your OpenAI key:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

### 4. Run the App

```bash
streamlit run ai_report_generator.py
```

---

## 🧪 Example Input Format

Your file should have the following (case-insensitive) columns:

- **Date**
- **Revenue** / **Sales** / **Turnover**
- **Expenses** / **Costs** / **Expenditure**

---

## 🛡️ Warning

🚫 **Never push your OpenAI API keys to GitHub** — they can be easily exposed and misused. Always use `.streamlit/secrets.toml` to store secrets locally or use GitHub Actions secrets in production.

---

## 📬 Contact

Developed by [adhavan](mailto:you@example.com)  
Feel free to connect or suggest features!

---
