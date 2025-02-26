"""
V1 General functions
"""

__version__ = "1.0.0"
from datetime import datetime, timedelta

import requests


def range_generator(leq_date: str, periods: int) -> dict:
    """
    Generates the end date for the query by sbstracting a specified number of periods from the start date.
    Args:
        start_date (str): Start of the date range (ISO 8601 format).
        periods (int): Num. of periods after the start_date (days to substract)
    Returns:
        dict: A dictionary with:
            - "leq_date": The end date of the range in ISO 8601 format with time appended as "23:59:59Z".
            - "geq_date": The start date of the range in ISO 8601 format with time appended as "00:00:00Z".
    Raises:
        ValueError: If the start_date format is invalid or periods in negative
    """
    if periods < 0:
        raise ValueError("Periods must be a non-negative integer.")
    days_to_subtract = periods - 1
    try:
        end = datetime.strptime(leq_date, "%Y-%m-%d")
        start = end - timedelta(days=days_to_subtract)
        return {
            "leq_date": end.strftime("%Y-%m-%dT23:59:59Z"),
            "geq_date": start.strftime("%Y-%m-%dT00:00:00Z"),
        }
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: '{leq_date}'. Use ISO 8601 format 'YYYY-MM-DD'."
        ) from e


def execute_query(token: str, query: str, variables: dict) -> None:
    """
    Execute GraphQL query.
    Args:
        token (str): API token for authorization.
        query (str): GraphQL query string.
        variables (dict): Variables for the query.
    """
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")


def get_accounts(token: str) -> dict:
    """
    Retrieve basic information for all Cloudflare accounts accessible with the provided token.
    Args:
        token (str): API token for authorization.
    Returns:
        dict: A dictionary containing account names as keys and their respective IDs as values.
    Raises:
        Exception: If the HTTP request fails or the API returns errors.
    """
    url = "https://api.cloudflare.com/client/v4/accounts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")
    data = response.json()
    if not data.get("success"):
        raise Exception(f"API Error: {data.get('errors')}")
    results = {account["name"]: account["id"] for account in data["result"]}
    return results


def get_zones(token: str) -> dict:
    """
    Retrieve zone names and their corresponding IDs from Cloudflare.
    Args:
        token (str): API token for authorization.
    Returns:
        dict: A dictionary with zone names as keys and their respective IDs as values.
    Raises:
        Exception: If the HTTP request fails or the Cloudflare API returns errors.
    """
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")
    data = response.json()
    if not data.get("success"):
        raise Exception(f"API Error: {data.get('errors')}")
    results = {zone["name"]: zone["id"] for zone in data.get("result", [])}
    return results


# def get_account_settings(token: str, account_id: str):
#     """
#     Get basic stats from the acocunt
#     """
#     # TODO: Add dates as variables
#     url = "https://api.cloudflare.com/client/v4/graphql"
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#     }
#     query = """
#         query GetAccountSettings($accountTag: string) {
#             viewer {
#                 accounts(filter: {accountTag: $accountTag}) {
#                     settings {
#                         httpRequestsOverviewAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         httpRequestsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         advancedDnsProtectionNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         dosdNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         dosdAttackAnalyticsGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         firewallEventsAdaptive {
#                             ...AccountSettings
#                             __typename
#                         }
#                         firewallEventsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         flowtrackdNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         magicTransitNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         magicTransitTunnelTrafficAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         magicFirewallNetworkAnalyticsAdaptiveGroups {
#                            ...AccountSettings
#                            __typename
#                         }
#                         spectrumNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         __typename
#                     }
#                     __typename
#                 }
#                 __typename
#             }
#         }
#         fragment AccountSettings on Settings {
#             availableFields
#             enabled
#             maxDuration
#             maxNumberOfFields
#             maxPageSize
#             notOlderThan
#             __typename
#         }
#     """
#     variables = {
#         "accountTag": account_id,
#         "filter": {
#             "datetime_geq": "2024-12-09T22:58:00Z",
#             "datetime_leq": "2024-12-16T22:58:00Z",
#         },
#     }
#     payload = {"query": query, "variables": variables}
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code == 200:
#         data = response.json()
#         if data.get("data"):
#             print(json.dumps(data, indent=2))
#         else:
#             print(f"Error: {data.get('errors', 'Unknown error')}")
#     else:
#         print(f"HTTP Error {response.status_code}: {response.text}")
