import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq

st.set_page_config(page_title="Schema-Agnostic Data Analyst", layout="centered")
st.title("📊 Ask Your Spreadsheet Anything")
st.caption("Upload any CSV. Ask questions in plain English. No fixed column names required.")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]

def ask_ai(prompt):
    last_error = None
    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            continue
    raise Exception(f"All models failed. Last error: {last_error}")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Preview:")
    st.dataframe(df.head())

    columns = list(df.columns)
    question = st.text_input("Ask a question about this data")

    if st.button("Get Answer") and question:
        with st.spinner("Thinking..."):
            prompt = f"""
You are a data analyst. The dataframe is called df.
Its columns are: {columns}
Write ONE line of pandas code (no explanation, just the code) to answer this question:
{question}
Only return the code. Do not use markdown, do not add ```python.
"""
            generated_code = ask_ai(prompt).strip()

            try:
                result = eval(generated_code)
                st.subheader("Answer")
                st.write(result)

                if hasattr(result, 'plot'):
                    fig, ax = plt.subplots()
                    result.plot(kind='bar', ax=ax)
                    plt.title(question)
                    plt.tight_layout()
                    st.pyplot(fig)

                explain_prompt = f"""
This pandas code was run: {generated_code}
It answered this question: {question}
In one simple sentence, explain what calculation was performed. No technical jargon.
"""
                explanation = ask_ai(explain_prompt)
                st.subheader("Explanation")
                st.write(explanation)

            except Exception as e:
                st.subheader("Answer")
                st.warning("I can't answer that — the data doesn't have enough information for it.")
                st.caption(f"Reason: {str(e)[:150]}")

        with st.expander("See generated code (debug)"):
            st.code(generated_code)
