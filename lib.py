"""
Store all the functions neccesary to run the Cloudflare API
"""

import json
import os
from datetime import datetime, timedelta

# Temporary imports and code
import dotenv as env
import requests

env.load_dotenv()
TOKEN = os.getenv("CF_API_TOKEN")
ID = os.getenv("ACCOUNT_ID")
if not TOKEN or not ID:
    raise ValueError("No token or account ID found in configuration")


# Date generator
def geq_generator(start_date: str, periods: int):
    """
    Generates the end date for the query
    Args:
        start_date (str): Start of the date range (ISO 8601 format)
        periods (int): Number of periods after start_date.
    Returns:
        str: Greater or equal date for the range (ISO 8601 format).
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
        end = start - timedelta(days=periods)
        return end.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: {start_date}. Use ISO 8601 format 'YYYY-MM-DDTHH:MM:SSZ'"
        ) from e


# 4xx or 5xx errors
def get_error_totals(
    token: str, account_tag: str, error_type: int, leq_date: str, periods: int
):
    """
    Get the total amount of 4xx errors for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        error_type (int): Specifies the range of error to retrieve, 4xx or 5xx,
        only admits 4 or 5 as values.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Error type confirmation
    if error_type not in [4, 5]:
        raise ValueError(
            f"Invalid error type: {error_type}. Must be 4 (4xx) or 5 (5xx)."
        )
    if error_type == 4:
        inf_limit = 400
        sup_limit = 500
    else:
        inf_limit = 500
        sup_limit = 600
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetErrorTotals($accountTag: String, $filter: Filter,
        $fourxxFilter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    fourxxOverTime: httpRequestsOverviewAdaptiveGroups(filter:
                    {AND: [$filter, $fourxxFilter,]}, limit: 2000) {
                        sum {
                            requests
                        }
                        dimensions {
                            timestamp: date
                        }
                    }
                }
            }
        }
    """
    variables = {
        "accountTag": account_tag,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
        },
        "fourxxFilter": {
            "edgeResponseStatus_geq": inf_limit,
            "edgeResponseStatus_lt": sup_limit,
        },
    }
    # Query
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")


get_error_totals(TOKEN, ID, 4, "2024-12-16T22:58:00Z", 7)


# end_date("2024-12-16T22:58:00Z", 7)
