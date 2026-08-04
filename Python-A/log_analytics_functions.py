from datetime import timedelta
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from groq import Groq
import pandas as pd

# ==========================================================
# Azure Log Analytics Settings
# ==========================================================

LOG_ANALYTICS_WORKSPACE_ID = "60c7f53e-249a-4077-b68e-55a4ae877d7c"

# ==========================================================
# Groq API Key
# Replace with your NEW Groq API key
# ==========================================================

GROQ_API_KEY = "***REMOVED***"

client_groq = Groq(
    api_key=GROQ_API_KEY
)

# ==========================================================
# Azure Authentication
# ==========================================================

log_analytics_client = LogsQueryClient(
    credential=DefaultAzureCredential()
)

# ==========================================================
# Tables to Query
# ==========================================================

TABLES = [
    "DeviceLogonEvents",
    "AzureNetworkAnalytics_CL",
    "AzureActivity",
    "SigninLogs"
]

FIELDS = {

    "DeviceLogonEvents":
        "TimeGenerated, AccountName, DeviceName, ActionType, RemoteIP, RemoteDeviceName",

    "AzureNetworkAnalytics_CL":
        "TimeGenerated, FlowType_s, SrcPublicIPs_s, DestIP_s, DestPort_d, VM_s, AllowedInFlows_d, AllowedOutFlows_d, DeniedInFlows_d, DeniedOutFlows_d",

    "AzureActivity":
        "TimeGenerated, OperationNameValue, ActivityStatusValue, ResourceGroup, Caller, CallerIpAddress, Category",

    "SigninLogs":
        "TimeGenerated, UserPrincipalName, OperationName, Category, ResultSignature, ResultDescription, AppDisplayName, IPAddress, LocationDetails"

}

HOURS_AGO = 1

# ==========================================================
# Query Function
# ==========================================================

def query_log_analytics(client, workspace_id, table, fields, hours):

    if table == "AzureNetworkAnalytics_CL":

        kql_query = f"""
        {table}
        | where FlowType_s == "MaliciousFlow"
        | project {fields}
        """

    else:

        kql_query = f"""
        {table}
        | project {fields}
        """

    print("\n" + "=" * 80)
    print(f"Running Query Against {table}")
    print("=" * 80)
    print(kql_query)

    try:

        response = client.query_workspace(
            workspace_id=workspace_id,
            query=kql_query,
            timespan=timedelta(hours=hours)
        )

    except Exception as e:

        print(f"Query failed for {table}")
        print(e)
        return None

    if not response.tables:
        return None

    return response.tables[0]

# ==========================================================
# Main Loop
# ==========================================================

for table_name in TABLES:

    print("\n")
    print("=" * 80)
    print(f"Checking {table_name}")
    print("=" * 80)

    results = query_log_analytics(
        client=log_analytics_client,
        workspace_id=LOG_ANALYTICS_WORKSPACE_ID,
        table=table_name,
        fields=FIELDS[table_name],
        hours=HOURS_AGO
    )

    if results is None:
        print("No results.")
        continue

    if len(results.rows) == 0:
        print("No data returned.")
        continue

    df = pd.DataFrame(
        results.rows,
        columns=results.columns
    )

    if "TimeGenerated" in df.columns:

        df["TimeGenerated"] = pd.to_datetime(
            df["TimeGenerated"]
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

    records = df.to_csv(index=False)

    print("\nReturned Logs")
    print("=" * 80)
    print(records)

    # ======================================================
    # Send Logs to Groq AI
    # ======================================================

    prompt = f"""
You are a Senior SOC Analyst.

Analyze the following Azure Log Analytics data.

Provide:

1. Executive Summary

2. Suspicious Activity

3. Severity
   - Low
   - Medium
   - High
   - Critical

4. MITRE ATT&CK Techniques

5. Indicators of Compromise

6. Recommended Investigation Steps

7. Recommended Remediation

8. Explain why each event is suspicious.

Azure Logs:

{records}
"""

    print("\nSending logs to Groq AI...\n")

    try:

        response = client_groq.chat.completions.create(

            model="llama-3.3-70b-versatile",

            temperature=0.2,

            messages=[

                {
                    "role": "system",
                    "content": "You are an expert SOC Analyst."
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        )

        print("=" * 80)
        print("AI SECURITY ANALYSIS")
        print("=" * 80)
        print(response.choices[0].message.content)

    except Exception as e:

        print("Groq API Error")
        print(e)

print("\nFinished!")