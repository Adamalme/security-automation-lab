# API Keys: https://platform.openai.com/settings/organization/api-keys
# Billing:  https://platform.openai.com/settings/organization/billing/overview
from groq import Groq
import logsshort as logs
import tiktoken
import json
from colorama import init, Fore, Style

# Stuff you need: logsshort.py, logslong.py (optional), pip install tiktoken, colorama

init(autoreset=True)

MAX_OUTPUT_TOKENS = 1_000
DEFAULT_MODEL = "llama-3.1-8b-instant"  # gpt-5, gpt-4.1, gpt-5-mini, gpt-4.1-nano
current_model = DEFAULT_MODEL

# Models: https://platform.openai.com/docs/models/compare
models = {
    "llama-3.1-8b-instant": {
        "max_window_tokens": 128000,
        "max_output_tokens": 500,
        "cost_per_million_input": 0.05,
        "cost_per_million_output": 0.08

    }
}

def calculate_chat_cost(prompt_tokens, cost_per_million) -> float:
    cost = (prompt_tokens / 1_000_000) * cost_per_million
    return round(cost, 6)

def count_message_tokens(messages, model: str) -> int:
    """
    Count tokens for chat messages using the actual serialization format
    the API will send to the model.
    """
    # serialize the messages the same way OpenAI client does
    payload = {"model": model, "messages": messages}
    serialized = json.dumps(payload, ensure_ascii=False)

    # handle unsupported models manually
    if model == "gpt-5":
        enc = tiktoken.get_encoding("cl100k_base")
    else:
        # choose encoding that matches the model family
        enc = tiktoken.get_encoding("cl100k_base")

    return len(enc.encode(serialized))

openai_client = Groq(api_key="***REMOVED***")

prompt = f"You are a threat hunter. Any anomalies or potential breaches?\n{logs.security_logs[:500]}"

prompt_messages = [{"role": "user", "content": prompt}]

estimated_prompt_token_count = count_message_tokens(messages=prompt_messages, model=DEFAULT_MODEL)

# We can restrict max output tokens
# max_tokens_used_in_response   = MAX_OUTPUT_TOKENS
max_tokens_used_in_response = MAX_OUTPUT_TOKENS
model_cost_per_million_tokens_input = models[current_model]["cost_per_million_input"]
model_cost_per_million_tokens_output = models[current_model]["cost_per_million_output"]

estimated_chat_cost_input = calculate_chat_cost(
    prompt_tokens=estimated_prompt_token_count,
    cost_per_million=model_cost_per_million_tokens_input
)

estimated_chat_cost_output = calculate_chat_cost(
    prompt_tokens=max_tokens_used_in_response,
    cost_per_million=model_cost_per_million_tokens_output
)

estimated_total_chat_cost = estimated_chat_cost_input + estimated_chat_cost_output

choice = input(
    f"Chat will cost approximately ${estimated_total_chat_cost:.4f}\n"
    "Proceed? (y/n): "
).strip().lower()

if choice != "y":
    print("Aborted.")
    exit(0)

response = openai_client.chat.completions.create(
    model=current_model,
    messages=prompt_messages,
    max_completion_tokens=max_tokens_used_in_response
)

actual_tokens_input = response.usage.prompt_tokens
actual_tokens_output = response.usage.completion_tokens
actual_total_tokens = response.usage.total_tokens

actual_chat_cost_input = calculate_chat_cost(
    prompt_tokens=actual_tokens_input,
    cost_per_million=model_cost_per_million_tokens_input
)

actual_chat_cost_output = calculate_chat_cost(
    prompt_tokens=actual_tokens_output,
    cost_per_million=model_cost_per_million_tokens_output
)

actual_total_chat_cost = actual_chat_cost_input + actual_chat_cost_output

status_cost = (Fore.GREEN + "UNDER" + Style.RESET_ALL) if actual_total_chat_cost <= estimated_total_chat_cost else (Fore.RED + "OVER" + Style.RESET_ALL)
status_tokens_input = (Fore.GREEN + "UNDER" + Style.RESET_ALL) if actual_tokens_input <= estimated_prompt_token_count else (Fore.RED + "OVER" + Style.RESET_ALL)
status_tokens_output = (Fore.GREEN + "UNDER" + Style.RESET_ALL) if actual_tokens_output <= max_tokens_used_in_response else (Fore.RED + "OVER" + Style.RESET_ALL)

print()
print(f"Estimated input tokens:  {estimated_prompt_token_count}")
print(f"Estimated output tokens: {max_tokens_used_in_response}")
print(f"Estimated chat cost:     ${estimated_total_chat_cost:.4f}")
print()
print(f"Actual input tokens:     {actual_tokens_input} [{status_tokens_input}]")
print(f"Actual output tokens:    {actual_tokens_output} [{status_tokens_output}]")
print(f"Actual chat cost:        ${actual_total_chat_cost:.4f} [{status_cost}]")

answer = response.choices[0].message.content

# Remove the comment on print if you want to see the actual threat hunt results
# print(answer)

print("\nfin.")
