from groq import Groq
import pandas as pd
import matplotlib.pyplot as plt

client = Groq(api_key="gsk_SSDz2zovIVGaVdqoLcjbbWGdyb3FYvNsLdSd1VyhRcuexGASowpY2")

# Try these in order — whichever your key has access t
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
        MODELS = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "gemma2-9b-it"]
        except Exception as e:
            last_error = e
            print(f"[{model_name}] failed: {str(e)[:80]}")
            continue
    raise Exception(f"All models failed. Last error: {last_error}")

df = pd.read_csv("supermarket.csv")
columns = list(df.columns)

question = input("Ask a question about the data: ")

prompt = f"""
You are a data analyst. The dataframe is called df.
Its columns are: {columns}
Write ONE line of pandas code (no explanation, just the code) to answer this question:
{question}
Only return the code. Do not use markdown, do not add ```python.
"""

generated_code = ask_ai(prompt).strip()
print("AI wrote this code:")
print(generated_code)

result = eval(generated_code)
print("\nAnswer:")
print(result)

if hasattr(result, 'plot'):
    result.plot(kind='bar')
    plt.title(question)
    plt.tight_layout()
    plt.savefig("chart.png")
    print("Chart saved as chart.png")

explain_prompt = f"""
This pandas code was run: {generated_code}
It answered this question: {question}
In one simple sentence, explain what calculation was performed. No technical jargon.
"""
explanation = ask_ai(explain_prompt)
print("\nExplanation:")
print(explanation)
