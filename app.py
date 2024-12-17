"""
Get basic CloudFlare analytics using the plain API
"""

import json
import os

import dotenv as env
import requests

env.load_dotenv()
TOKEN = os.getenv("CF_API_TOKEN")
ID = os.getenv("ACCOUNT_ID")
if not TOKEN or not ID:
    raise ValueError("No token or account ID found in configuration")


def get_analtics(account_id: str, token: str):
    """
    Get dashboard analytics for a given account
    """
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/rum/site_info/list"
    )
    # url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/analytics/dashboard"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(data)
            # totals = data["result"]["totals"]
            # print("Basic Analytics:")
            # print(f"Requests: {totals['requests']}")
            # print(f"Bandwidth: {totals['bandwidth']} bytes")
            # print(f"Threats: {totals['threats']}")
            # print(f"Uniques: {totals['uniques']}")
        else:
            print(f"API Error: {data['errors']}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")


def get_accounts(token: str):
    """
    Get basic data on accounts
    """
    url = "https://api.cloudflare.com/client/v4/accounts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print("Accounts: ")
            for account in data["result"]:
                print(f"Name: {account['name']}, ID: {account['id']}")
        else:
            print(f"API Error: {data['errors']}")
    else:
        print(f"HTTP Error: {response.status_code} - {response.text}")


def get_http_request(token: str, account_id: str):
    """
    Get http request from an account
    """
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query RequestsAndDataTransferByHostname($zoneTag: string, $filter:filter) {
    viewer {
      zones(filter: {zoneTag: $zoneTag}) {
        httpRequestsAdaptiveGroups(limit: 10, filter: $filter) {
          sum {
            visits
            edgeResponseBytes
          }
          dimensions {
            datetimeHour
          }
        }
      }
    }
  }
    """
    variables = {
        "zoneTag": account_id,
        "filter": {
            "datetime_geq": "2024-12-01T11:00:00Z",
            "datetime_lt": "2024-12-10T12:00:00Z",
            "clientRequestHTTPHost": "flexware.mx",
            "requestSource": "eyeball",
        },
    }
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


def get_zones(token: str):
    """
    Get the zones and their id's
    """
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("Zones:")
            for zone in data.get("result", []):
                print(f"- Name: {zone['name']}, ID: {zone['id']}")
        else:
            print(f"API Error: {data.get('errors')}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")


def get_http_version_used(token: str, account_id: str):
    """
    Retrieve the http version used by the client
    """
    # TODO: Add the dates as a variable
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetHttpProtocols {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    total: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: 1) {
                        sum {
                            requests
                            __typename
                        }
                        __typename
                    }
                httpProtocols: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: 5, orderBy: [sum_requests_DESC]) {
                    sum {
                        requests
                        __typename
                    }
                    dimensions {
                        metric: clientRequestHTTPProtocol
                        __typename
                    }
                    __typename
                }
                __typename
                }
                __typename
            }
        }
    """
    variables = {
        "accountTag": account_id,
        "filter": {
            "datetime_geq": "2024-12-09T22:58:00Z",
            "datetime_leq": "2024-12-16T22:58:00Z",
        },
    }
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


def get_locations(token: str, account_id: str, limit: int):
    """
    Get number of requests and bandwidth grouped by country
    """
    # TODO: Add dates as variables
    # TODO: Add limit as a variable
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetLocations {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    locationTotals: httpRequestsOverviewAdaptiveGroups(filter:
                    $filter, limit: $limit, orderBy: [sum_requests_DESC]) {
                        sum {
                            requests
                            bytes
                            __typename
                        }
                        dimensions {
                          clientCountryName
                          __typename
                        }
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
    """
    variables = {
        "accountTag": account_id,
        "limit": limit,
        "filter": {
            "datetime_geq": "2024-12-09T22:58:00Z",
            "datetime_leq": "2024-12-16T22:58:00Z",
        },
    }
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


def get_account_settings(token: str, account_id: str):
    """
    Get basic stats from the acocunt
    """
    # TODO: Add dates as variables
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetAccountSettings($accountTag: string) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    settings {
                        httpRequestsOverviewAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        httpRequestsAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        advancedDnsProtectionNetworkAnalyticsAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        dosdNetworkAnalyticsAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        dosdAttackAnalyticsGroups {
                            ...AccountSettings
                            __typename
                        }
                        firewallEventsAdaptive {
                            ...AccountSettings
                            __typename
                        }
                        firewallEventsAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        flowtrackdNetworkAnalyticsAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        magicTransitNetworkAnalyticsAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        magicTransitTunnelTrafficAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        magicFirewallNetworkAnalyticsAdaptiveGroups {
                           ...AccountSettings
                           __typename
                        }
                        spectrumNetworkAnalyticsAdaptiveGroups {
                            ...AccountSettings
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
        fragment AccountSettings on Settings {
            availableFields
            enabled
            maxDuration
            maxNumberOfFields
            maxPageSize
            notOlderThan
            __typename
        }
    """
    variables = {
        "accountTag": account_id,
        "filter": {
            "datetime_geq": "2024-12-09T22:58:00Z",
            "datetime_leq": "2024-12-16T22:58:00Z",
        },
    }
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


# 4xx errors
def get_error_totals(token: str, account_tag: str, error_type: int):
    """
    Get the total amount of 4xx errors for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        error_type (int): Specifies the range of error to retrieve, 4xx or 5xx,
        only admits 4 or 5 as values.
        start_date (str): Start of datetime range (ISO 8601 format).
        end_date (str): End of datetime range (ISO 8601 format).
    """
    # TODO: Modify the dates to only work with a starting time and the the
    # number of days to retrieve
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
            "datetime_geq": "2024-12-10T00:00:00Z",
            "datetime_leq": "2024-12-16T22:58:00Z",
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


get_error_totals(TOKEN, ID, 5)

# get_account_settings(TOKEN, ID)
# get_locations(TOKEN, ID, 10)
# get_http_version_used(TOKEN, "fc17bc8e7dccdfa1c5e9fc17df9b78f5")
##get_zones(TOKEN)
# get_analtics("fc17bc8e7dccdfa1c5e9fc17df9b78f5", TOKEN)
# get_accounts(TOKEN)
# get_http_request(TOKEN, "f59279c6958c57bb391e93c8dba8965a")
