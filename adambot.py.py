from openai import OpenAI

client = OpenAI(api_key="your-api-key-here")

# This list is the "memory"
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant called AdamBot."}
]

print("🤖 AdamBot is ready! Type 'quit' to exit.\n")

while True:
    # Get user input
    prompt = input("You: ")
    
    if prompt.lower() == "quit":
        print("AdamBot: Goodbye!")
        break

    # Add user message to memory
    conversation_history.append({
        "role": "user",
        "content": prompt
    })

    # Send full conversation history
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history
    )

    # Get the reply
    answer = response.choices[0].message.content

    # Add AI reply to memory too
    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    print(f"\nAdamBot: {answer}\n")