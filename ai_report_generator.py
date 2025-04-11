import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from fpdf import FPDF
from io import BytesIO
import matplotlib.ticker as ticker
from datetime import datetime
import smtplib
from email.message import EmailMessage
from openai import OpenAI
import re

# App title
st.set_page_config(page_title="AI Business Report Generator", layout="wide")
st.title("📊 AI Business Report Generator (for CA Firms & SMEs)")

# Upload logo
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Logo_OpenAI.svg/1200px-Logo_OpenAI.svg.png", width=150)

# Email input (optional)
email = st.sidebar.text_input("Enter your email to receive the report (optional)")

# Upload CSV or Excel file
uploaded_file = st.file_uploader("Upload your financial Excel/CSV file")

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    df.columns = df.columns.str.strip().str.lower()

    st.subheader("📁 Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    sales_col = next((col for col in df.columns if col in ['revenue', 'sales', 'turnover']), None)
    expense_col = next((col for col in df.columns if col in ['expenses', 'costs', 'expenditure']), None)
    date_col = next((col for col in df.columns if 'date' in col), None)

    if all([sales_col, expense_col, date_col]):
        total_revenue = df[sales_col].sum()
        total_expenses = df[expense_col].sum()
        profit = total_revenue - total_expenses

        st.subheader("📈 Key Financial Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
        col2.metric("Total Expenses", f"₹{total_expenses:,.0f}")
        col3.metric("Net Profit", f"₹{profit:,.0f}")

        df[date_col] = pd.to_datetime(df[date_col])
        df_sorted = df.sort_values(by=date_col)
        df_grouped = df_sorted.groupby(date_col).sum().reset_index()

        st.subheader("📅 Revenue Over Time")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df_grouped[date_col], df_grouped[sales_col], marker='o', linestyle='-', color='blue')
        ax.set_xlabel("Date")
        ax.set_ylabel("Revenue")
        ax.set_title("Revenue Trend")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'₹{int(x):,}'))

        max_idx = df_grouped[sales_col].idxmax()
        min_idx = df_grouped[sales_col].idxmin()
        ax.plot(df_grouped[date_col][max_idx], df_grouped[sales_col][max_idx], 'go', label='Max')
        ax.plot(df_grouped[date_col][min_idx], df_grouped[sales_col][min_idx], 'ro', label='Min')
        ax.annotate('⬆ Max', (df_grouped[date_col][max_idx], df_grouped[sales_col][max_idx]),
                    textcoords="offset points", xytext=(0,10), ha='center', color='green')
        ax.annotate('⬇ Min', (df_grouped[date_col][min_idx], df_grouped[sales_col][min_idx]),
                    textcoords="offset points", xytext=(0,-15), ha='center', color='red')
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        ax.legend()

        st.pyplot(fig)

        st.subheader("🧠 AI-Generated Business Summary")

        prompt = f"""
        Analyze this financial data:
        - Total Revenue: ₹{total_revenue}
        - Total Expenses: ₹{total_expenses}
        - Net Profit: ₹{profit}
        Write a professional summary for a CA or SME business owner. Include financial health, performance, and any suggestions.
        """

        summary = ""
        with st.spinner("Generating summary..."):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a financial analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300
                )
                summary = response.choices[0].message.content.strip()
                st.success("✅ Summary generated successfully!")
                st.write(summary)

            except Exception as e:
                st.error(f"⚠️ Failed to generate summary: {e}")

        st.subheader("📄 Download Report as PDF")
        if st.button("Generate PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font("ArialUnicode", "", "ArialUnicodeMS.ttf", uni=True)
            pdf.set_font("ArialUnicode", size=12)
            pdf.set_title("AI Business Report")
            pdf.cell(200, 10, txt="AI Business Report", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(0, 10, txt=f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Total Revenue: ₹{total_revenue:,.0f}\nTotal Expenses: ₹{total_expenses:,.0f}\nNet Profit: ₹{profit:,.0f}")
            pdf.ln(5)
            pdf.set_font("ArialUnicode", style='B', size=12)
            pdf.cell(0, 10, txt="Summary:", ln=True)
            pdf.set_font("ArialUnicode", size=12)

            clean_summary = re.sub(r'[^\x00-\x7F]+', '', summary)
            pdf.multi_cell(0, 10, txt=clean_summary)

            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            st.download_button(
                label="📥 Download PDF",
                data=pdf_output,
                file_name="business_report.pdf",
                mime="application/pdf"
            )

            if email:
                with st.spinner("Sending email..."):
                    try:
                        msg = EmailMessage()
                        msg['Subject'] = 'Your AI Business Report'
                        msg['From'] = 'your_email@example.com'
                        msg['To'] = email
                        msg.set_content('Attached is your requested business report.')
                        msg.add_attachment(pdf_output.read(), maintype='application', subtype='pdf', filename='business_report.pdf')

                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login('your_email@example.com', 'your_app_password')
                            smtp.send_message(msg)
                        st.success("✅ Report emailed successfully!")
                    except Exception as e:
                        st.warning("Email sending failed. Check SMTP settings.")
                        st.text(str(e))

        st.markdown("---")
        st.markdown("Developed with ❤️ by adhavan | Contact: you@example.com")
    else:
        st.warning("⚠️ Your file must have columns like 'Date', 'Revenue', and 'Expenses' (or similar names like 'Sales', 'Costs').")
