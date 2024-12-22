"""
Store all the functions neccesary to run the Cloudflare API
"""

import json
import os
import re
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
    # Modify the date to bring the days starting from start to end
    periods -= 1
    try:
        start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
        end = start - timedelta(days=periods)
        return end.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: {start_date}. Use ISO 8601 format 'YYYY-MM-DDTHH:MM:SSZ'"
        ) from e


# %% Network module
# 4xx or 5xx errors
def get_error_totals(
    token: str, account_tag: str, error_type: int, leq_date: str, periods: int
):
    """
    Get the total amount of 4xx or 5xx errors for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        error_type (int): Specifies the range of error to retrieve, 4xx or 5xx,
        only admits 4 or 5 as values.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # TODO: Change the name of the query
    # TODO: The data is not ordered.
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
        $errorFilter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    errorStats: httpRequestsOverviewAdaptiveGroups(filter:
                    {AND: [$filter, $errorFilter,]},
                        limit: 2000
                        # orderBy: date, orderDirection:desc
                        ) {
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
        "errorFilter": {
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
            pre_results = data["data"]["viewer"]["accounts"][0]["errorStats"]
            results = {
                item["dimensions"]["timestamp"]: item["sum"]["requests"]
                for item in pre_results
            }
            print(results)
        print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")


# %% Stats module
# Requests per country
def get_requests_per_location(
    token: str, account_tag: str, leq_date: str, periods: int
):
    """
    Get the total number of request per country for the period
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).

    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetRequestsLocations {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    locationTotals: httpRequestsOverviewAdaptiveGroups(filter:
                    $filter, limit: 10, orderBy: [sum_requests_DESC]) {
                        sum {
                            requests
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
        "accountTag": account_tag,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
        },
    }
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            pre_results = data["data"]["viewer"]["accounts"][0]["locationTotals"]
            results = {
                item["dimensions"]["clientCountryName"]: item["sum"]["requests"]
                for item in pre_results
            }
            print(results)
        else:
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")


# Total bandwidth
def get_bandwidth(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the total bandwidth for the period
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).

    """
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetBandwidthPerDay($accountTag: String, $filter: Filter, $limit: Int) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    bandwidthTotals: httpRequestsOverviewAdaptiveGroups(
                    filter: $filter, 
                    limit: $limit
                    ) {
                        sum {
                            bytes
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
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
        },
    }
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            pre_results = data["data"]["viewer"]["accounts"][0]["bandwidthTotals"]
            results = {
                item["dimensions"]["timestamp"]: item["sum"]["bytes"]
                for item in pre_results
            }
            print(results)
        else:
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")


# Total requests
def get_requests(token: str, account_tag: str, limit: int, leq_date: str, periods: int):
    """
    Get the total number of requests per day for the period.

    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
        periods (int): Number of days in the range.

    Returns:
        dict: A dictionary with dates as keys and the number of requests as values.
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)

    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetRequestsPerDay($accountTag: String, $filter: Filter, $limit: Int) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    requestsTotals: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter, 
                        limit: $limit
                    ) {
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
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
        },
    }
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=payload)

    # Parse the response
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            pre_results = data["data"]["viewer"]["accounts"][0]["requestsTotals"]
            results = {
                item["dimensions"]["timestamp"]: item["sum"]["requests"]
                for item in pre_results
            }
            print(results)
        else:
            print(f"Error: {data.get('errors', 'Unknown error')}")
            return {}
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")
        return {}


# Bandwidth per country
def get_bandwidth_per_location(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the total bandwidth per country for the period
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).

    """
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetRequestsLocations {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    locationTotals: httpRequestsOverviewAdaptiveGroups(filter:
                    $filter, limit: $limit, orderBy: [sum_requests_DESC]) {
                        sum {
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
        "accountTag": account_tag,
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
        },
    }
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            pre_results = data["data"]["viewer"]["accounts"][0]["locationTotals"]
            results = {
                item["dimensions"]["clientCountryName"]: item["sum"]["bytes"]
                for item in pre_results
            }
            print(results)
        else:
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")


def get_visits_total(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the total number of visits for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetVisits ($accountTag: String, $filter: Filter, $limit: Int) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    statsOverTime: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: $limit) {
                        sum {
                            visits
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
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
        },
    }
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            pre_results = data["data"]["viewer"]["accounts"][0]["statsOverTime"]
            results = {
                item["dimensions"]["timestamp"]: item["sum"]["visits"]
                for item in pre_results
            }
            print(results)
        else:
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")


def get_page_views_total(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the total number of page views for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetPageViews($accountTag: String, $filter: Filter, $limit: Int) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    statsOverTime: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: $limit) {
                        sum {
                            pageViews
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
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
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


# %% Network module
# Client http version
def get_http_versions(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the http client version used.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
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
        "accountTag": account_tag,
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
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


# SSL Traffic
def get_ssl_traffic(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the traffic served over SSL.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query SSLVersionsQuery {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    total: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: 1) {
                        sum {
                            requests
                            __typename
                        }
                        __typename
                    }
                    sslVersions: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: 5) {
                        sum {
                            requests
                            __typename
                        }
                        dimensions {
                            metric: clientSSLProtocol
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
        "accountTag": account_tag,
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
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


# Top content types
def get_content_type(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the top type of content served for the period
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # TODO: Chech why are there two limits in this function
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetTopContentTypes {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    total: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: 1) {
                        sum {
                            requests
                            __typename
                        }
                       __typename
                    }
                    contentTypes: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: 5, orderBy: [sum_requests_DESC]) {
                        sum {
                            requests
                            __typename
                        }
                        dimensions {
                            metric: edgeResponseContentTypeName
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
        "accountTag": account_tag,
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
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


# %% Cache module
# Cached requests
def get_cached_requests(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the total of cached requests for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetCachedRequests($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    cachedRequestsOverTime: httpRequestsOverviewAdaptiveGroups(filter: $filter, limit: 2000) {
                        sum {
                            cachedRequests
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
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
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


# Cached bandwidth
def get_cached_bandwidth(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the total amount of cached badwidth for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetCachedBandwidth($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    cachedBandwidthOverTime: httpRequestsOverviewAdaptiveGroups(
                    filter: $filter, 
                    limit: 2000
                    ) {
                        sum {
                          cachedBytes
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
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
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


# %% Security module
# Encrypted requests
def get_encrypted_requests(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the total amount of encrypted requests for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetEncryptedRequests($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    encryptedRequestsOverTime: httpRequestsOverviewAdaptiveGroups(
                    filter: {AND: [$filter, {edgeResponseStatus_lt: 600}]}, 
                    limit: 2000
                    ) {
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
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
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


# Encrypted bandwidth
def get_encrypted_bandwidth(
    token: str, account_tag: str, limit: int, leq_date: str, periods: int
):
    """
    Get the total amount of encrypted bandwidth for the period.
    Args:
        token (str): API Token to make requests.
        account_tag (str): Unique identifier for the Cloudflare account.
        limit (int): Maximum number of entries to return.
        leq_date (str): Less or equal date for the range (ISO 8601 format).
    """
    # Date generation
    geq_date = geq_generator(leq_date, periods)
    # Query construction
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    query = """
        query GetEncryptedBandwidth($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    encryptedBandwidthOverTime: httpRequestsOverviewAdaptiveGroups(
                    filter: {AND: [$filter, {edgeResponseStatus_lt: 600}]}, 
                    limit: 2000
                ) {
                    sum {
                        bytes
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
        "limit": limit,
        "filter": {
            "datetime_geq": geq_date,
            "datetime_leq": leq_date,
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


# get_encrypted_bandwidth(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_encrypted_requests(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_cached_bandwidth(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_cached_requests(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_content_type(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_http_versions(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_bandwidth(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_page_views_total(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_bandwidth_per_location(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_requests_per_location(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_error_totals(TOKEN, ID, 4, "2024-12-16T22:58:00Z", 7)
#
