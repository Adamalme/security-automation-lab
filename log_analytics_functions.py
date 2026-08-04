
import os
import json
import logging
import requests
import urllib3

from dotenv import load_dotenv
from groq import Groq

from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError
)


# ==========================================================
# Disable SSL warnings
# ==========================================================

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()


# ==========================================================
# Configuration
# ==========================================================


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


if not GROQ_API_KEY:

    raise Exception(
        "Missing GROQ_API_KEY. Create .env file."
    )



WAZUH_URL = "https://192.168.56.101:55000"

WAZUH_USER = "wazuh-wui"

WAZUH_PASS = "wazuh-wui"


ALERT_LIMIT = 10



client = Groq(
    api_key=GROQ_API_KEY
)



# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)



# ==========================================================
# Wazuh Authentication
# ==========================================================


def get_wazuh_token():


    try:


        response = requests.post(


            f"{WAZUH_URL}/security/user/authenticate",


            auth=(

                WAZUH_USER,

                WAZUH_PASS

            ),


            verify=False,


            timeout=15

        )



        response.raise_for_status()



        token = response.json()["data"]["token"]



        logging.info(
            "Wazuh authentication successful"
        )



        return token




    except Timeout:


        raise Exception(
            "Wazuh API timeout"
        )



    except ConnectionError:


        raise Exception(
            "Cannot connect to Wazuh API"
        )



    except HTTPError as e:


        raise Exception(
            f"Wazuh login failed: {e}"
        )




# ==========================================================
# Retrieve Wazuh Alerts
# ==========================================================


def get_wazuh_alerts(token):


    headers = {


        "Authorization":

        f"Bearer {token}"

    }



    response = requests.get(



        f"{WAZUH_URL}/alerts",



        headers=headers,



        params={

            "limit": ALERT_LIMIT,

            "sort": "-timestamp"

        },



        verify=False,



        timeout=20

    )



    response.raise_for_status()



    data = response.json()



    alerts = (

        data

        .get("data", {})

        .get("affected_items", [])

    )



    logging.info(

        f"Retrieved {len(alerts)} Wazuh alerts"

    )



    return alerts





# ==========================================================
# AI Security Analysis
# ==========================================================


def analyze_alert_with_ai(alert):



    rule = alert.get(

        "rule",

        {}

    )


    agent = alert.get(

        "agent",

        {}

    )



    prompt = f"""

You are a Senior SOC Analyst.


Analyze this Wazuh security event.



Rule ID:

{rule.get('id')}



Event:

{rule.get('description')}



Severity:

{rule.get('level')}



Agent:

{agent.get('name')}



Timestamp:

{alert.get('timestamp')}



Provide:

- Threat assessment

- Severity

- Explanation

- Recommended response

- MITRE ATT&CK technique if applicable

"""



    response = client.chat.completions.create(


        model="llama-3.3-70b-versatile",


        messages=[


            {

                "role": "user",

                "content": prompt

            }


        ]

    )



    return response.choices[0].message.content





# ==========================================================
# Main Program
# ==========================================================


def main():



    print("=" * 60)

    print(
        "WAZUH AI SECURITY ANALYZER"
    )

    print("=" * 60)



    try:



        token = get_wazuh_token()



        alerts = get_wazuh_alerts(token)




        if not alerts:



            print(
                "No alerts found"
            )

            return





        results = []




        for alert in alerts:



            print("\n")

            print("=" * 60)



            rule = alert.get(

                "rule",

                {}

            )



            agent = alert.get(

                "agent",

                {}

            )



            print(

                "Rule ID:",

                rule.get("id")

            )


            print(

                "Event:",

                rule.get("description")

            )



            print(

                "Level:",

                rule.get("level")

            )



            print(

                "Agent:",

                agent.get("name")

            )



            print(

                "Timestamp:",

                alert.get("timestamp")

            )



            print("\nAI ANALYSIS")

            print("-" * 40)




            analysis = analyze_alert_with_ai(alert)



            print(analysis)



            results.append({


                "event": alert,


                "analysis": analysis


            })





        with open(

            "analysis.json",

            "w"

        ) as file:



            json.dump(

                results,

                file,

                indent=4

            )



        print(

            "\nSaved results to analysis.json"

        )





    except Exception as e:



        logging.error(e)





if __name__ == "__main__":


    main()