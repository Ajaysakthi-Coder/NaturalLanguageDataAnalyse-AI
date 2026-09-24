from google import genai

client = genai.Client(api_key="AQ.Ab8RN6Ka9BgEQX13HXSRJqBj_EyGu-BDot6FeFZzoEAytmxMJw")

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="Say hello and tell me you are ready to help with data analysis."
)

print(response.text)
