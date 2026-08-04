### Azure Monitor Security Log Automation

---------------------------------------------------------------------------------------------------------------------------------------------------------

## What This Does
Python script that queries Azure Log Analytics workspace 
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
3. Add your Workspace ID to the script
4. Run: python log_analytics.py
