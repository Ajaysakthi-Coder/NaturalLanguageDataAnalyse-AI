import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq

# Initialize conversational memory
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Schema-Agnostic Data Analyst", layout="wide") # changed to wide for tabs
st.title("📊 Ask Your Spreadsheet Anything")
st.caption("Upload any CSV. Ask questions in plain English. No fixed column names required.")

# --- HACKATHON RAW API KEY ---
client = Groq(api_key="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")

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
    # Load the file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    with st.expander("📁 View Data Preview", expanded=False):
        st.dataframe(df.head(10))

    # BONUS FEATURE: Anomaly Auto-Flagging
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

    st.write("---")
    columns = list(df.columns)
    question = st.text_input("Ask a detailed question about this data")

    if st.button("Analyze") and question:
        with st.spinner("Analyzing schema, generating code, and auditing logic..."):
            
            # 1. Build conversation history for context
            history_text = "\n".join([f"User: {m['q']}\nAI: {m['a']}" for m in st.session_state.messages[-3:]])
            
            # 2. UPGRADED PROMPT: Allow multi-line, force structured logic
            code_prompt = f"""
You are a senior data analyst. The dataframe is called `df`.
Its exact columns are: {columns}

Previous conversation context:
{history_text}

Write Python pandas code to answer this NEW question: {question}

RULES FOR THE CODE:
1. You may use MULTIPLE LINES of code. Use intermediate variables for readability.
2. The final answer MUST be stored in a variable called `final_result`.
3. Handle missing values (NaN) gracefully if they affect the calculation.
4. Do not use print() statements.
5. Return ONLY the python code, no markdown, no explanations.
"""
            generated_code = ask_ai(code_prompt).strip()
            # Clean up markdown if the LLM adds it anyway
            if generated_code.startswith("```python"):
                generated_code = generated_code[9:-3]
            elif generated_code.startswith("```"):
                generated_code = generated_code[3:-3]

            # 3. Execute the code safely
            local_vars = {"df": df, "pd": pd}
            try:
                exec(generated_code, globals(), local_vars)
                result = local_vars.get("final_result", "Error: Variable `final_result` not found.")
            except Exception as e:
                result = f"Execution Error: {str(e)}"

            # 4. UPGRADED PROMPT: Detailed, step-by-step explainability
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
Explain in 1-2 sentences which columns you chose to use and why. Mention any assumptions you had to make (e.g., assuming 'Lifetime_Value' means total revenue).

### 🔍 Step-by-Step Calculation
Give a numbered list of exactly what the code did. Be specific. 
Example:
1. Filtered rows to keep only 'North America' region.
2. Grouped the data by 'Most_Frequent_Category'.
3. Calculated the average of 'Average_Order_Value'.
4. Sorted the results from highest to lowest.

### 📝 The Answer
State the final answer simply in one sentence. If it is a list or table, summarize the top findings.
"""
            explanation = ask_ai(explain_prompt)

            # 5. Display Results in Professional Tabs
            st.write("---")
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Answer & Chart", "🧠 Explanation", "🛠️ Generated Code", "📋 Raw Data Used"])

            with tab1:
                st.subheader("Final Result")
                st.write(result)
                
                # Generate chart if the result is a Series or DataFrame
                if hasattr(result, 'plot'):
                    fig, ax = plt.subplots(figsize=(10, 5))
                    result.plot(kind='bar', ax=ax)
                    plt.title(question)
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)

            with tab2:
                st.markdown(explanation)

            with tab3:
                st.code(generated_code, language="python")

            with tab4:
                st.caption("This is the exact data that was passed into the AI's calculation.")
                st.dataframe(df)

            # Save to memory
            st.session_state.messages.append({"q": question, "a": f"Result: {result}. Explanation: {explanation}"})

    # Clear Memory Button
    if st.button("Clear Conversation Memory"):
        st.session_state.messages = []
        st.rerun()
