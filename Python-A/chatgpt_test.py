# API Keys: https://platform.openai.com/settings/organization/api-keys
# Billing:  https://platform.openai.com/setting/organization/billing/overview
from groq import Groq

from groq import Groq

client = Groq(api_key="***REMOVED***")

prompt = "What is the best country? answer in 5 words or less."

full_prompt = [
    {"role": "system", "content": "Answer as if you are a girl working on the street of Kabukicho who is good at making cakes "},
    {"role": "user", "content": "My favorite cake is banana"},
    {"role": "user", "content": "what is the best sushi in tokyo?"}
]

response = client.chat.completions.create(model="llama-3.3-70b-versatile",messages=full_prompt)
                                          

answer = response.choices[0].message.content

print(f"------\n{answer}\n")