from groq import Groq

client = Groq(api_key="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")

models = client.models.list()
for m in models.data:
    print(m.id)
