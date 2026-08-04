import json
import requests
from groq import Groq
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================================
# CONFIGURATION
# ==========================================================

GROQ_API_KEY = "***REMOVED***"

# If running on the Wazuh server:
WAZUH_URL = "https://127.0.0.1:55000"

# If running from Windows to your VM, use instead:
# WAZUH_URL = "https://192.168.56.101:55000"

WAZUH_USER = "wazuh-wui"
WAZUH_PASS = "iA5bX5B6jT+KT5*oXrXQjPnuZNMa0kb"
import urllib3
urllib3.disable_warnings()

WAZUH_URL = "https://192.168.56.101:55000"
USERNAME = "wazuh-wui"
PASSWORD = "iA5bX5B6jT+KT5*oXrXQjPnuZNMa0kb*"

def get_token():
    response = requests.post(
        f"{WAZUH_URL}/security/user/authenticate",
        auth=(USERNAME, PASSWORD),
        verify=False
    )
    return response.json()['data']['token']

def get_agents(token):
    response = requests.get(
        f"{WAZUH_URL}/agents",
        headers={"Authorization": f"Bearer {token}"},
        verify=False
    )
    return response.json()

# Main
token = get_token()
print("Token received successfully!")

agents = get_agents(token)
print(agents)

print("fin.")import requests
import urllib3
urllib3.disable_warnings()

WAZUH_URL = "https://192.168.56.101:55000"
USERNAME = "wazuh-wui"
PASSWORD = "wazuh-wui"

def get_token():
    response = requests.post(
        f"{WAZUH_URL}/security/user/authenticate",
        auth=(USERNAME, PASSWORD),
        verify=False
    )
    return response.json()['data']['token']

def get_agents(token):
    response = requests.get(
        f"{WAZUH_URL}/agents",
        headers={"Authorization": f"Bearer {token}"},
        verify=False
    )
    return response.json()

# Main
token = get_token()
print("Token received successfully!")

agents = get_agents(token)
print(agents)

print("fin.")import requests
import urllib3
urllib3.disable_warnings()

WAZUH_URL = "https://192.168.56.101:55000"
USERNAME = "wazuh-wui"
PASSWORD = "wazuh-wui"

def get_token():
    response = requests.post(
        f"{WAZUH_URL}/security/user/authenticate",
        auth=(USERNAME, PASSWORD),
        verify=False
    )
    return response.json()['data']['token']

def get_agents(token):
    response = requests.get(
        f"{WAZUH_URL}/agents",
        headers={"Authorization": f"Bearer {token}"},
        verify=False
    )
    return response.json()

# Main
token = get_token()
print("Token received successfully!")

agents = get_agents(token)
print(agents)

print("fin.")import requests
import urllib3
urllib3.disable_warnings()

WAZUH_URL = "https://192.168.56.101:55000"
USERNAME = "wazuh-wui"
PASSWORD = "wazuh-wui"

def get_token():
    response = requests.post(
        f"{WAZUH_URL}/security/user/authenticate",
        auth=(USERNAME, PASSWORD),
        verify=False
    )
    return response.json()['data']['token']

def get_agents(token):
    response = requests.get(
        f"{WAZUH_URL}/agents",
        headers={"Authorization": f"Bearer {token}"},
        verify=False
    )
    return response.json()

# Main
token = get_token()
print("Token received successfully!")

agents = get_agents(token)
print(agents)

print("fin.")"

client = Groq(api_key=GROQ_API_KEY)

# ==========================================================
# WAZUH API
# ==========================================================

def get_wazuh_token():
    try:
        response = requests.post(
            f"{WAZUH_URL}/security/user/authenticate",
            auth=(WAZUH_USER, WAZUH_PASS),
            verify=False,
            timeout=10
        )

        print("Authentication Status:", response.status_code)

        if response.status_code != 200:
            print(response.text)
            raise Exception("Authentication failed.")

        data = response.json()

        if "data" not in data or "token" not in data["data"]:
            raise Exception("Token not found in API response.")

        return data["data"]["token"]

    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Unable to connect to Wazuh API at {WAZUH_URL}\n"
            "Verify the IP address, port 55000, and that the Wazuh Manager is running."
        )


def get_wazuh_alerts(token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{WAZUH_URL}/manager/logs",
        headers=headers,
        params={"limit": 5},
        verify=False,
        timeout=10
    )

    print("Alerts Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return []

    data = response.json()

    if "data" in data and "affected_items" in data["data"]:
        return data["data"]["affected_items"]

    return []

# ==========================================================
# AI TOOL
# ==========================================================

security_analysis_tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_security_alert",
            "description": "Analyze a security alert.",
            "parameters": {
                "type": "object",
                "properties": {
                    "is_threat": {
                        "type": "boolean"
                    },
                    "severity": {
                        "type": "string"
                    },
                    "verdict": {
                        "type": "string"
                    },
                    "action": {
                        "type": "string"
                    },
                    "explanation": {
                        "type": "string"
                    }
                },
                "required": [
                    "is_threat",
                    "severity",
                    "verdict",
                    "action",
                    "explanation"
                ]
            }
        }
    }
]

def analyze_alert_with_ai(alert):

    alert_text = f"""
Rule: {alert.get('rule', {}).get('description', 'Unknown')}
Level: {alert.get('rule', {}).get('level', 0)}
Agent: {alert.get('agent', {}).get('name', 'Unknown')}
Timestamp: {alert.get('timestamp', 'Unknown')}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": alert_text
            }
        ],
        tools=security_analysis_tools,
        tool_choice="required"
    )

    return json.loads(
        response.choices[0].message.tool_calls[0].function.arguments
    )

# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 50)
    print("🔐 Wazuh AI Security Analyzer")
    print("=" * 50)

    try:

        print("Connecting to Wazuh...")

        token = get_wazuh_token()

        print("✅ Connected Successfully")

        print("\nFetching latest alerts...")

        alerts = get_wazuh_alerts(token)

        if not alerts:
            print("No alerts found.")
            return

        print(f"\nFound {len(alerts)} alerts.")

        for alert in alerts:

            print("\n" + "=" * 50)

            print("Rule:",
                  alert.get("rule", {}).get("description", "Unknown"))

            print("Level:",
                  alert.get("rule", {}).get("level", 0))

            analysis = analyze_alert_with_ai(alert)

            print("Threat:", analysis["is_threat"])
            print("Verdict:", analysis["verdict"])
            print("Severity:", analysis["severity"])
            print("Action:", analysis["action"])
            print("Explanation:", analysis["explanation"])

    except Exception as e:
        print("\nERROR")
        print(e)

    print("\nFinished.")

if __name__ == "__main__":
    main()