# API Keys: https://platform.openai.com/settings/organization/api-keys
# Billing:  https://platform.openai.com/settings/organization/billimport jso

import json
from groq import Groq

client = Groq(api_key="***REMOVED***")

prompt = "Give me only a JSON schema blueprint for a pineapple. Use string, array, number as value types. Valid JSON only. No extra text."

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)

answer = response.choices[0].message.content
answer = answer.strip()
answer = answer.replace("```json", "").replace("```", "")
answer = answer.strip()

print("RAW ANSWER:", answer)
parsed = json.loads(answer)

print("Title:", parsed["title"])
print("Type:", parsed["type"])
print("Properties:", parsed["properties"])
print("\nFull Schema:")
print(answer)
print("fin")

