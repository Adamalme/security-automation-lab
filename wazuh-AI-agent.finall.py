import json
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

OPENAI_API_KEY = "***REMOVED***"


client = OpenAI(
    api_key=OPENAI_API_KEY
)



# ==========================================================
# Wazuh API
# ==========================================================

WAZUH_URL = "https://192.168.56.102:55000"

WAZUH_USER = "wazuh-wui"

WAZUH_PASS = "Wazuh1234!"



# ==========================================================
# OpenSearch Indexer
# ==========================================================

INDEXER_URL = "https://192.168.56.102:9200"

INDEXER_USER = "admin"

INDEXER_PASS = "4puttnSmAD4KH0cVM*WfkF7CXnGBHbUp"



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


    return json.loads(

        response.choices[0].message.content

    )



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


        results.append(

            {

                "alert":alert,

                "AI_analysis":analysis

            }

        )


    save_report(results)



if __name__=="__main__":

    main()