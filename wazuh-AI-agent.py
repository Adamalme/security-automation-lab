import json
import requests
from groq import Groq
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── CONFIG ───────────────────────────────
GROQ_API_KEY = "paste-new-groq-key-here"
WAZUH_URL    = "https://192.168.56.102:55000"
WAZUH_USER   = "wazuh-wui"
WAZUH_PASS   = "i47xa+Eiudz1l.BzhGE1?ADiL71hYd?F"
# ──────────────────────────────────────────

client = Groq(api_key="***REMOVED***")

def get_wazuh_token():
    response = requests.post(
        f"{"https://192.168.56.102:55000"}/security/user/authenticate",
        auth=("wazuh-wui","i47xa+Eiudz1l.BzhGE1?ADiL71hYd?F"),
        verify=False
    )
    print("Status:", response.status_code)
    if response.status_code != 200:
        raise Exception(f"Wazuh login failed ({response.status_code})")
    data = response.json()
    if "data" not in data:
        raise Exception(f"Unexpected response: {data}")
    return data["data"]["token"]

def get_wazuh_alerts(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{"https://192.168.56.102:55000"}/manager/logs",
        headers=headers,
        verify=False,
        params={"limit": 5}
    )
    
    print("Alerts Status:", response.status_code)
    data = response.json()
    print("Alerts Response:", data)
    
    if "data" in data and "affected_items" in data["data"]:
        return data["data"]["affected_items"]
    elif "data" in data:
        return data["data"]
    else:
        return []
security_analysis_tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_security_alert",
            "description": (
                "Analyze a security alert and determine "
                "if it is a real threat or false positive. "
                "Be concise and direct."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "is_threat": {
                        "type": "boolean",
                        "description": "True if real threat, False if false positive"
                    },
                    "severity": {
                        "type": "string",
                        "description": "critical, high, medium or low"
                    },
                    "verdict": {
                        "type": "string",
                        "description": "Real Threat or False Positive"
                    },
                    "action": {
                        "type": "string",
                        "description": "Recommended action to take"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Brief explanation of the finding"
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
    Analyze this security alert:
    Rule: {alert.get('rule', {}).get('description', 'Unknown')}
    Level: {alert.get('rule', {}).get('level', 0)}
    Agent: {alert.get('agent', {}).get('name', 'Unknown')}
    Timestamp: {alert.get('timestamp', 'Unknown')}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": alert_text}],
        tools=security_analysis_tools,
        tool_choice="required"
    )
    result = response.choices[0].message.tool_calls[0]
    return json.loads(result.function.arguments)

def main():
    print("🔐 Wazuh AI Security Analyzer")
    print("=" * 40)

    try:
        print("Connecting to Wazuh...")
        token = get_wazuh_token()
        print("✅ Connected to Wazuh!\n")

        print("Fetching latest alerts...")
        alerts = get_wazuh_alerts(token)
        
        if not alerts:
            print("No alerts found!")
            return
            
        print(f"✅ Found {len(alerts)} alerts\n")
        print("=" * 40)

        for alert in alerts:
            rule_desc = alert.get('rule', {}).get('description', 'Unknown')
            rule_level = alert.get('rule', {}).get('level', 0)

            print(f"\n📋 Alert: {rule_desc}")
            print(f"⚠️  Level: {rule_level}")

            analysis = analyze_alert_with_ai(alert)

            if analysis["is_threat"]:
                print(f"🚨 VERDICT: {analysis['verdict']}")
            else:
                print(f"✅ VERDICT: {analysis['verdict']}")

            print(f"📊 Severity:    {analysis['severity']}")
            print(f"💡 Action:      {analysis['action']}")
            print(f"📝 Explanation: {analysis['explanation']}")
            print("-" * 40)

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\nfin.")

main()