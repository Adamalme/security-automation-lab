# Azure Monitor Security Log Automation <img width="474" height="182" alt="image" src="https://github.com/user-attachments/assets/325c2fbb-e23a-48c0-b5f1-b449f9b2a5c0" />


## What This Does
Python script that queries Azure Log Analytics workspace <img width="4343" height="2218" alt="image" src="https://github.com/user-attachments/assets/3da2256f-10d2-4976-9a1a-321d018d2dfd" />

for real-time security events using KQL queries.

## Data Collected
- Username and Principal Name
- Logon Activity Type and Action Type
- Source IP Address and Location
- Timestamp of events

## Tools Used
- Python 3
- Azure Monitor Query SDK
- Azure Identity SDK
- Pandas
- KQL (Kusto Query Language)

## Requirements
pip install azure-monitor-query azure-identity pandas

## Setup
1. Install Azure CLI
2. Run: az login
3. Add your Workspace ID
4. Run: python log_analytics.py
