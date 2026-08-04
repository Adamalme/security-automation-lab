from groq import Groq
import json

lifestyle_assessment_tools = [
    {
        "type": "function",
        "function": {
            "name": "assess_lifestyle",
            "description": (
                "A lifestyle recommendation for the user based on their favorite food. "
                "If the user's favorite food is sweets or unhealthy food, encourage them to eat healthy. "
                "If their favorite food is something healthy, encourage them to keep going. "
                "Be extremely blunt."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "person_is_healthy": {
                        "type": "boolean",
                        "description": "True if healthy food, False if unhealthy"
                    },
                    "note_to_user": {
                        "type": "string",
                        "description": "Blunt recommendation to user"
                    },
                    "alternate_suggestion": {
                        "type": "string",
                        "description": "Suggest a healthier alternative regardless of if healthy or not"
                    }
                },
                "required": [
                    "person_is_healthy",
                    "note_to_user",
                    "alternate_suggestion"
                ]
            }
        }
    }
]

client = Groq(api_key="***REMOVED***")

prompt = input("🤖 AI Agent: What is your Favorite food:\n")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    tools=lifestyle_assessment_tools,
    tool_choice="required"
)

answer = response.choices[0].message.tool_calls[0]
answer_dict = json.loads(answer.function.arguments)

note_to_user = answer_dict["note_to_user"]
person_is_healthy = answer_dict["person_is_healthy"]
alt_suggestion = answer_dict["alternate_suggestion"]

if person_is_healthy:
    print("Good job ✅✅✅")
    print(note_to_user)

elif not person_is_healthy:
    print("Oh no ❌❌❌")
    print(note_to_user)

print(f"\nNote to User: {note_to_user}")
print(f"\nAlternate Suggestion: {alt_suggestion}")
print("fin.")