import os
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ==========================================================
# OpenSearch Indexer
# ==========================================================

INDEXER_URL = "https://192.168.56.102:9200"

INDEXER_USER = "admin"

INDEXER_PASS = os.environ["INDEXER_PASS"]

AI_THREAT_INBOX_INDEX = "ai-threat-inbox-alerts"


# ==========================================================
# Query Helpers
# ==========================================================

def run_search(query):

    response = requests.get(
        f"{INDEXER_URL}/{AI_THREAT_INBOX_INDEX}/_search",
        auth=(INDEXER_USER, INDEXER_PASS),
        json=query,
        headers={"Content-Type": "application/json"},
        verify=False,
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(f"OpenSearch query failed: {response.status_code} {response.text}")

    return response.json()


def get_aggregations():

    query = {
        "size": 0,
        "aggs": {
            "by_severity": {"terms": {"field": "severity", "size": 10}},
            "top_mitre": {"terms": {"field": "mitre_techniques", "size": 5}},
            "top_agents": {"terms": {"field": "agent_name", "size": 5}}
        }
    }

    return run_search(query)["aggregations"]


def get_top_risk_alerts(n=5):

    query = {
        "size": n,
        "sort": [{"risk_score": {"order": "desc"}}],
        "_source": [
            "timestamp", "agent_name", "agent_ip",
            "incident_type", "severity", "risk_score",
            "mitre_techniques"
        ]
    }

    hits = run_search(query)["hits"]["hits"]

    return [hit["_source"] for hit in hits]


# ==========================================================
# Summary
# ==========================================================

def print_summary():

    print("=" * 70)
    print("AI Threat Inbox Summary")
    print("=" * 70)

    aggs = get_aggregations()

    print("\nAlerts by Severity:")
    for bucket in aggs["by_severity"]["buckets"]:
        print(f"  {bucket['key']:<12} {bucket['doc_count']}")

    print("\nTop 5 MITRE Techniques:")
    for bucket in aggs["top_mitre"]["buckets"]:
        print(f"  {bucket['key']:<12} {bucket['doc_count']}")

    print("\nTop Agents by Alert Count:")
    for bucket in aggs["top_agents"]["buckets"]:
        print(f"  {bucket['key']:<20} {bucket['doc_count']}")

    print("\nTop 5 Highest Risk Alerts:")
    top_alerts = get_top_risk_alerts(5)

    if not top_alerts:
        print("  (none)")

    for alert in top_alerts:
        print(
            f"  [{alert.get('risk_score')}] {alert.get('severity')} - "
            f"{alert.get('incident_type')} - agent={alert.get('agent_name')} "
            f"({alert.get('timestamp')})"
        )


def main():

    try:
        print_summary()

    except Exception as e:
        print(f"Error querying OpenSearch: {e}")


if __name__ == "__main__":
    main()
