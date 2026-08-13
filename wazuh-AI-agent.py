import hashlib
import json
import os
import re
import requests
import urllib3
from datetime import datetime
from openai import OpenAI


urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


# ==========================================================
# OpenAI
# ==========================================================

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)



# ==========================================================
# Wazuh API
# ==========================================================

WAZUH_URL = "https://192.168.56.102:55000"

WAZUH_USER = "wazuh-wui"

WAZUH_PASS = os.environ["WAZUH_PASS"]



# ==========================================================
# OpenSearch Indexer
# ==========================================================

INDEXER_URL = "https://192.168.56.102:9200"

INDEXER_USER = "admin"

INDEXER_PASS = os.environ["INDEXER_PASS"]



# ==========================================================
# Test OpenSearch
# ==========================================================

def test_indexer():

    print("\nTesting OpenSearch connection...")


    try:

        response = requests.get(

            INDEXER_URL,

            auth=(INDEXER_USER, INDEXER_PASS),

            verify=False,

            timeout=10

        )


        print(
            "OpenSearch Status:",
            response.status_code
        )


        if response.status_code != 200:

            raise Exception(response.text)


        print("✅ OpenSearch Connected")


    except Exception as e:

        print(
            "❌ OpenSearch Error:",
            e
        )

        exit()



# ==========================================================
# Authenticate Wazuh API
# ==========================================================

def get_wazuh_token():

    response = requests.post(

        f"{WAZUH_URL}/security/user/authenticate",

        auth=(

            WAZUH_USER,

            WAZUH_PASS

        ),

        verify=False,

        timeout=10

    )


    print(
        "Wazuh API Status:",
        response.status_code
    )


    if response.status_code != 200:

        raise Exception(response.text)


    return response.json()["data"]["token"]



# ==========================================================
# Pull Alerts
# ==========================================================

def get_dashboard_alerts():
    query = {
        "size":25,
        "sort":[
            {
                "@timestamp":{
                    "order":"desc"
                }
            }
        ]
    }        

              
    response = requests.get(
        f"{INDEXER_URL}/wazuh-alerts-*/_search",

        auth=(

            INDEXER_USER,

            INDEXER_PASS

        ),

        json=query,

        headers={

            "Content-Type":"application/json"

        },

        verify=False,

        timeout=30

    )


    print(

        "Indexer Query Status:",

        response.status_code

    )



    if response.status_code != 200:

        print(response.text)

        return []



    data=response.json()


    alerts=[]


    for hit in data["hits"]["hits"]:

        alerts.append(
            hit["_source"]
        )


    return alerts



# ==========================================================
# AI Analyst
# ==========================================================

def analyze_alert(alert):


    rule = alert.get(
        "rule",
        {}
    )


    agent = alert.get(
        "agent",
        {}
    )


    prompt=f"""

You are a Senior SOC Analyst.

Analyze this Wazuh alert.

Rule:
{rule.get('description')}

Level:
{rule.get('level')}

Agent:
{agent.get('name')}

IP:
{agent.get('ip')}

Time:
{alert.get('@timestamp')}


Return JSON:

{{
"severity":"",
"incident_type":"",
"mitre_attack":"",
"risk_score":0,
"recommended_action":"",
"analysis":""
}}

"""


    response=client.chat.completions.create(

        model="gpt-4.1",

        messages=[

            {

                "role":"system",

                "content":
                "You are a cybersecurity analyst."

            },

            {

                "role":"user",

                "content":prompt

            }

        ],


        response_format={

            "type":"json_object"

        }


    )


    raw_content = response.choices[0].message.content


    # Some AI responses can come back malformed/truncated.
    # This prevents one bad response from crashing the entire run.
    try:

        return json.loads(raw_content)

    except json.JSONDecodeError as e:

        print(

            f"⚠️ JSON parsing failed for this alert: {e}"

        )

        return {

            "severity": "Unknown",

            "incident_type": "Parsing Error",

            "mitre_attack": "",

            "risk_score": 0,

            "recommended_action": "Manual review required - AI response could not be parsed.",

            "analysis": "The AI model returned malformed JSON for this alert. Raw response could not be parsed automatically."

        }



# ==========================================================
# Normalize Alert (AI Threat Inbox schema)
# ==========================================================

def normalize_alert(raw_alert: dict, source_agent_name: str, source_agent_ip: str, event_timestamp: str) -> dict:
    """
    Takes the raw GPT output and reshapes it into a consistent schema
    for storage, filtering, and future dashboard/search use.
    """
    severity = str(raw_alert.get("severity", "")).strip().capitalize()

    mitre_raw = raw_alert.get("mitre_attack", "")
    if isinstance(mitre_raw, list):
        mitre_text = " ".join(str(item) for item in mitre_raw)
    elif mitre_raw and str(mitre_raw).lower() != "none":
        mitre_text = str(mitre_raw)
    else:
        mitre_text = ""
    mitre_techniques = re.findall(r"T\d{4}(?:\.\d{3})?", mitre_text)

    return {
        "timestamp": event_timestamp,
        "agent_name": source_agent_name,
        "agent_ip": source_agent_ip,
        "severity": severity,
        "incident_type": raw_alert.get("incident_type", "Unknown"),
        "mitre_techniques": mitre_techniques,
        "risk_score": raw_alert.get("risk_score", 0),
        "recommended_action": raw_alert.get("recommended_action", ""),
        "analysis": raw_alert.get("analysis", ""),
        "processed_at": datetime.utcnow().isoformat() + "Z"
    }



# ==========================================================
# Push Normalized Alert to OpenSearch (AI Threat Inbox)
# ==========================================================

AI_THREAT_INBOX_INDEX = "ai-threat-inbox-alerts"


def ensure_ai_threat_inbox_index():
    """
    Creates the ai-threat-inbox-alerts index with an explicit mapping
    if it doesn't already exist yet, so fields like risk_score and
    mitre_techniques get proper types instead of relying on
    OpenSearch's dynamic mapping guesses.
    """
    check = requests.head(
        f"{INDEXER_URL}/{AI_THREAT_INBOX_INDEX}",
        auth=(INDEXER_USER, INDEXER_PASS),
        verify=False,
        timeout=10
    )

    if check.status_code == 200:
        return

    mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "agent_name": {"type": "keyword"},
                "agent_ip": {"type": "keyword"},
                "severity": {"type": "keyword"},
                "incident_type": {"type": "keyword"},
                "mitre_techniques": {"type": "keyword"},
                "risk_score": {"type": "integer"},
                "recommended_action": {"type": "text"},
                "analysis": {"type": "text"},
                "processed_at": {"type": "date"}
            }
        }
    }

    response = requests.put(
        f"{INDEXER_URL}/{AI_THREAT_INBOX_INDEX}",
        auth=(INDEXER_USER, INDEXER_PASS),
        json=mapping,
        headers={"Content-Type": "application/json"},
        verify=False,
        timeout=10
    )

    if response.status_code not in (200, 201):
        print(f"⚠️ Failed to create {AI_THREAT_INBOX_INDEX} index: {response.status_code} {response.text}")
    else:
        print(f"✅ Created OpenSearch index: {AI_THREAT_INBOX_INDEX}")



def build_alert_doc_id(normalized_alert: dict) -> str:
    """
    Deterministic document ID derived from the alert timestamp + agent
    name, so re-indexing the same alert overwrites/updates the
    existing document instead of creating a duplicate.
    """
    key = f"{normalized_alert.get('timestamp', '')}|{normalized_alert.get('agent_name', '')}"

    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def index_alert_to_opensearch(normalized_alert: dict) -> bool:
    """
    Pushes a single normalized alert into the ai-threat-inbox-alerts
    OpenSearch index so it's searchable/dashboardable, in addition to
    the local JSON report. Uses a deterministic doc ID so re-running
    the script updates existing alerts instead of duplicating them.
    """
    try:
        doc_id = build_alert_doc_id(normalized_alert)

        response = requests.put(
            f"{INDEXER_URL}/{AI_THREAT_INBOX_INDEX}/_doc/{doc_id}",
            auth=(INDEXER_USER, INDEXER_PASS),
            json=normalized_alert,
            headers={"Content-Type": "application/json"},
            verify=False,
            timeout=10
        )

        if response.status_code not in (200, 201):
            print(f"⚠️ Failed to index alert into OpenSearch: {response.status_code} {response.text}")
            return False

        return True

    except Exception as e:
        print(f"❌ OpenSearch indexing error: {e}")
        return False



# ==========================================================
# Save Report
# ==========================================================

def save_report(results):


    filename=(

        "wazuh_ai_report_"

        +

        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        +

        ".json"

    )


    with open(filename,"w") as f:

        json.dump(

            results,

            f,

            indent=4

        )


    print(

        "\nReport saved:",

        filename

    )



# ==========================================================
# Main
# ==========================================================

def main():


    print("="*70)

    print(
        "🔐 Wazuh + OpenAI SOC Automation"
    )

    print("="*70)



    test_indexer()


    ensure_ai_threat_inbox_index()



    print(
        "\nAuthenticating Wazuh..."
    )


    get_wazuh_token()


    print(
        "✅ Wazuh API Connected"
    )



    print(
        "\nPulling Alerts..."
    )


    alerts=get_dashboard_alerts()



    print(

        f"Found {len(alerts)} alerts"

    )


    if not alerts:

        return



    results=[]



    for alert in alerts:


        print("\n------------------------")


        analysis=analyze_alert(alert)



        print(
            json.dumps(
                analysis,
                indent=4
            )
        )


        # Pull the fields needed for normalization from the raw alert
        agent = alert.get("agent", {})
        agent_name = agent.get("name", "Unknown")
        agent_ip = agent.get("ip", "Unknown")
        event_timestamp = alert.get("@timestamp", "")


        # Build the clean, consistent Threat Inbox record
        normalized = normalize_alert(
            raw_alert=analysis,
            source_agent_name=agent_name,
            source_agent_ip=agent_ip,
            event_timestamp=event_timestamp
        )


        # Push into the AI Threat Inbox OpenSearch index
        indexed = index_alert_to_opensearch(normalized)

        print(
            "✅ Indexed to OpenSearch" if indexed else "⚠️ Not indexed (see error above)"
        )


        results.append(normalized)



    save_report(results)



if __name__=="__main__":

    main()

