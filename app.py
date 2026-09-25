import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq
import re
if "messages" not in st.session_state:
    st.session_state.messages = []
st.set_page_config(page_title="Schema-Agnostic Data Analyst", layout="wide")
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

def clean_code(raw_code):
    """Reliably strips markdown fences regardless of trailing whitespace/newlines."""
    cleaned = re.sub(r"^```(?:python)?\s*\n?|\n?```\s*$", "", raw_code.strip())
    return cleaned.strip()

def detect_anomalies(df):
    """TIER 2 FEATURE: Flags statistical outliers in numeric columns."""
    anomalies = []
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        mean = df[col].mean()
        std = df[col].std()
        if std == 0 or pd.isna(std):
            continue
        outliers = df[(df[col] - mean).abs() > 3 * std]
        for idx, row in outliers.iterrows():
            anomalies.append(
                f"Row {idx}: **{col}** = {row[col]:,.0f} — unusually far from average ({mean:,.0f})"
            )
    return anomalies

def generate_suggested_questions(columns, df):
    """TIER 1 FEATURE: AI suggests example questions based on actual columns."""
    numeric_cols = list(df.select_dtypes(include='number').columns)
    categorical_cols = list(df.select_dtypes(include='object').columns)
    prompt = f"""
Given a dataset with these columns: {columns}
Numeric columns: {numeric_cols}
Categorical columns: {categorical_cols}

Suggest exactly 4 short, natural business questions a user might ask about this data.
Return ONLY the 4 questions, one per line, no numbering, no extra text.
"""
    try:
        response = ask_ai(prompt)
        questions = [q.strip("- ").strip() for q in response.strip().split("\n") if q.strip()]
        return questions[:4]
    except Exception:
        return []

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    with st.expander("📁 View Data Preview", expanded=False):
        st.dataframe(df.head(10))

    # Data Quality Checks
    st.subheader("🚨 Auto-Detected Data Quality Checks")
    missing = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()
    col1, col2 = st.columns(2)
    with col1:
        if missing > 0:
            st.warning(f"Found {missing} missing values.")
        else:
            st.success("No missing values.")
    with col2:
        if duplicates > 0:
            st.warning(f"Found {duplicates} duplicate rows.")
        else:
            st.success("No duplicate rows.")

    # TIER 2 FEATURE: Anomaly Detection
    anomalies = detect_anomalies(df)
    if anomalies:
        with st.expander(f"⚠️ {len(anomalies)} unusual value(s) detected — click to review", expanded=False):
            for a in anomalies:
                st.markdown(f"- {a}")

    st.write("---")

    # TIER 1 FEATURE: Suggested Questions
    if "suggestions" not in st.session_state or st.session_state.get("suggestions_file") != uploaded_file.name:
        with st.spinner("Preparing suggested questions..."):
            st.session_state.suggestions = generate_suggested_questions(list(df.columns), df)
            st.session_state.suggestions_file = uploaded_file.name

    if st.session_state.suggestions:
        st.write("**💡 Try asking:**")
        cols = st.columns(len(st.session_state.suggestions))
        for i, sq in enumerate(st.session_state.suggestions):
            if cols[i].button(sq, key=f"suggestion_{i}"):
                st.session_state.pending_question = sq

    columns = list(df.columns)
    default_question = st.session_state.pop("pending_question", "")
    question = st.text_input("Ask a detailed question about this data", value=default_question)

    if st.button("Analyze") and question:
        with st.spinner("Analyzing schema, generating code, and auditing logic..."):

            # TIER 1 FEATURE: Stronger follow-up resolution
            history_text = "\n".join([f"User: {m['q']}\nAI: {m['a']}" for m in st.session_state.messages[-3:]])

            code_prompt = f"""
You are a senior data analyst. The dataframe is called `df`.
Its exact columns are: {columns}

Previous conversation context (use this to resolve references like "it", "that", "the previous one", "instead"):
{history_text if history_text else "No previous questions yet."}

Write Python pandas code to answer this NEW question: {question}
If the question refers to a previous answer (e.g. "what about the lowest instead"), resolve that reference using the conversation context above before writing code.

RULES FOR THE CODE:
1. You may use MULTIPLE LINES of code. Use intermediate variables for readability.
2. The final answer MUST be stored in a variable called `final_result`.
3. Handle missing values (NaN) gracefully if they affect the calculation.
4. Do not use print() statements.
5. Return ONLY the python code, no markdown, no explanations.
"""
            generated_code = clean_code(ask_ai(code_prompt))

            local_vars = {"df": df, "pd": pd}
            execution_failed = False
            try:
                exec(generated_code, globals(), local_vars)
                result = local_vars.get("final_result", None)
                if result is None:
                    execution_failed = True
                    result = "The generated code didn't produce a usable answer."
            except Exception as e:
                execution_failed = True
                result = f"I can't answer that — the data doesn't have enough information for it. (Reason: {str(e)[:150]})"

            # TIER 1 FEATURE: Confidence indicator
            confidence_prompt = f"""
Question: {question}
Columns available: {columns}
Code written: {generated_code}
Did answering this question require ASSUMING what a column means (e.g. guessing "Revenue" means total sales), 
or was it a DIRECT calculation using clearly-named columns?
Answer with exactly one word: DIRECT or ASSUMED.
"""
            try:
                confidence = ask_ai(confidence_prompt).strip().upper()
                confidence = "ASSUMED" if "ASSUM" in confidence else "DIRECT"
            except Exception:
                confidence = "DIRECT"

            explanation = None
            if not execution_failed:
                explain_prompt = f"""
You are a data analyst explaining your work to a non-technical CEO.
The user asked: '{question}'
The dataframe columns are: {columns}

You wrote and executed this code:
{generated_code}

The result was:
{result}

Write a response in Markdown format with EXACTLY these three sections:

### 🧠 Logic & Assumptions
Explain in 1-2 sentences which columns you chose to use and why. Mention any assumptions you had to make.

### 🔍 Step-by-Step Calculation
Give a numbered list of exactly what the code did.

### 📝 The Answer
State the final answer simply in one sentence.
"""
                explanation = ask_ai(explain_prompt)

            st.write("---")

            if execution_failed:
                st.subheader("Answer")
                st.error(result)
            else:
                badge = "🟢 Directly calculated" if confidence == "DIRECT" else "🟡 Required some assumptions"
                st.caption(badge)

                tab1, tab2 = st.tabs(["📊 Answer & Chart", "🧠 Explanation"])

                with tab1:
                    st.subheader("Final Result")
                    st.write(result)

                    if hasattr(result, 'plot'):
                        fig, ax = plt.subplots(figsize=(10, 5))
                        result.plot(kind='bar', ax=ax)
                        plt.title(question)
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        st.pyplot(fig)

                with tab2:
                    st.markdown(explanation)

                # TIER 2 FEATURE: Export the analysis
                export_text = f"Question: {question}\n\nAnswer: {result}\n\n{explanation}"
                st.download_button(
                    "⬇️ Download this analysis",
                    data=export_text,
                    file_name="analysis.txt",
                    mime="text/plain"
                )

                with st.expander("🛠️ Technical details (for judges/developers)"):
                    st.caption("Generated pandas code:")
                    st.code(generated_code, language="python")
                    st.caption("Raw data used:")
                    st.dataframe(df)

            st.session_state.messages.append({
                "q": question,
                "a": f"Result: {result}." + (f" Explanation: {explanation}" if explanation else "")
            })

    if st.button("Clear Conversation Memory"):
        st.session_state.messages = []
        st.session_state.pop("suggestions", None)
        st.rerun()
