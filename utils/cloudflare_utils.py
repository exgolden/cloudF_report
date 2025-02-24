"""
 V2 functions neccesary to run the Cloudflare API
"""
__version__ = "2.0.0"
import os
from datetime import datetime, timedelta
import requests

# Temporary settings and imports
import dotenv as env
env.load_dotenv()
TOKEN = os.getenv("CF_API_TOKEN")
ID = os.getenv("ACCOUNT_ID")
if not TOKEN or not ID:
    raise ValueError("No token or account ID found in configuration")

# General module
def range_generator(leq_date: str, periods: int) -> dict:
    """
    Generates the end date for the query by sbstracting a specified number of periods from the start date.
    Args:
        start_date (str): Start of the date range (ISO 8601 format).
        periods (int): NUmber f periods after the start_date (days to substract)
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
            "geq_date": start.strftime("%Y-%m-%dT00:00:00Z")
        }
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: '{leq_date}'. Use ISO 8601 format 'YYYY-MM-DD'."
        ) from e
    
def execute_query(query: str, variables: dict):
    """
    Execute GraphQL query.
    Args: 
        token (str): API token for authorization.
        query (str): GraphQL query string.
        variables (dict): Variables for the query.
    """
    token = TOKEN 
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers = headers, json = payload)
    if response.status_code == 200:
       return response.json() 
    else:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")

# Stats module
def get_requests_per_location(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total number of requests per country for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing countries as keys and their respective request counts as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetRequestsLocations($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    locationTotals: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
                        limit: 10,
                        orderBy: [sum_requests_DESC]
                    ) {
                        sum {
                            requests
                        }
                        dimensions {
                            clientCountryName
                        }
                    }
                }
            }
        }
    """
    variables = {
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        }
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("locationTotals"):
            raise ValueError("No location data available in the response.")
        location_totals = accounts[0]["locationTotals"]
        results = {
            item["dimensions"]["clientCountryName"]: item["sum"]["requests"]
            for item in location_totals
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_requests(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total number of requests per day for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and their respective request counts as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetRequests($zoneTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $zoneTag}) {
                    requestsTotals: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
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
        "zoneTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        }
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("requestsTotals"):
            raise ValueError("No request data available in the response.")
        request_totals = accounts[0]["requestsTotals"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["requests"]
            for item in request_totals
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_bandwidth_per_location(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total bandwidth per country for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format ("YYYY-MM-DD").
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing countries as keys and their respective bandwidth (in bytes) as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetBandwidthLocations($accountTag: String, $filter: Filter, $limit: Int) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    locationTotals: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter, 
                        limit: $limit, 
                        orderBy: [sum_bytes_DESC]
                    ) {
                        sum {
                            bytes
                        }
                        dimensions {
                            clientCountryName
                        }
                    }
                }
            }
        }
    """
    variables = {
        "accountTag": zone_tag,
        "limit": 10,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("locationTotals"):
            raise ValueError("No bandwidth data available in the response.")
        location_totals = accounts[0]["locationTotals"]
        results = {
            item["dimensions"]["clientCountryName"]: item["sum"]["bytes"]
            for item in location_totals
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_bandwidth(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total bandwidth per day for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format ("YYYY-MM-DD").
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and their respective bandwidth (in bytes) as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetBandwidth($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    bandwidthTotals: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        }
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("bandwidthTotals"):
            raise ValueError("No bandwidth data available in the response.")
        bandwidth_totals = accounts[0]["bandwidthTotals"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["bytes"]
            for item in bandwidth_totals
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_visits(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total number of visits per day for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format ("YYYY-MM-DD").
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and their respective visit counts as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetVisits($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    statsOverTime: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
                        limit: 2000
                    ) {
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        }
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("statsOverTime"):
            raise ValueError("No visit data available in the response.")
        stats_over_time = accounts[0]["statsOverTime"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["visits"]
            for item in stats_over_time
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_views(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total number of page views per day for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format ("YYYY-MM-DD").
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and their respective page view counts as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetPageViews($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    statsOverTime: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
                        limit: 2000
                    ) {
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        }
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("statsOverTime"):
            raise ValueError("No page view data available in the response.")
        stats_over_time = accounts[0]["statsOverTime"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["pageViews"]
            for item in stats_over_time
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

# Network module
def get_http_versions(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the HTTP client versions used for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing HTTP client versions as keys and their respective request counts as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetHttpProtocols($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    httpProtocols: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
                        limit: 5,
                        orderBy: [sum_requests_DESC]
                    ) {
                        sum {
                            requests
                        }
                        dimensions {
                            metric: clientRequestHTTPProtocol
                        }
                    }
                }
            }
        }
    """
    variables = {
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("httpProtocols"):
            raise ValueError("No HTTP protocols data available in the response.")
        http_protocols = accounts[0]["httpProtocols"]
        results = {
            item["dimensions"]["metric"]: item["sum"]["requests"]
            for item in http_protocols
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_ssl_traffic(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the traffic served over SSL for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing SSL protocols as keys and their respective request counts as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetSSLVersions($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    sslVersions: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
                        limit: 5
                    ) {
                        sum {
                            requests
                        }
                        dimensions {
                            metric: clientSSLProtocol
                        }
                    }
                }
            }
        }
    """
    variables = {
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("sslVersions"):
            raise ValueError("No SSL versions data available in the response.")
        ssl_versions = accounts[0]["sslVersions"]
        results = {
            item["dimensions"]["metric"]: item["sum"]["requests"]
            for item in ssl_versions
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_content_type(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the top types of content served for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing content types as keys and their respective request counts as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetTopContentTypes($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    contentTypes: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
                        limit: 5,
                        orderBy: [sum_requests_DESC]
                    ) {
                        sum {
                            requests
                        }
                        dimensions {
                            metric: edgeResponseContentTypeName
                        }
                    }
                }
            }
        }
    """
    variables = {
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("contentTypes"):
            raise ValueError("No content type data available in the response.")
        content_types = accounts[0]["contentTypes"]
        results = {
            item["dimensions"]["metric"]: item["sum"]["requests"]
            for item in content_types
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_cached_requests(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total number of cached requests for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and the number of cached requests as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetCachedRequests($accountTag: String, $filter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    cachedRequestsOverTime: httpRequestsOverviewAdaptiveGroups(
                        filter: $filter,
                        limit: 2000
                    ) {
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("cachedRequestsOverTime"):
            raise ValueError("No cached requests data available in the response.")
        cached_requests = accounts[0]["cachedRequestsOverTime"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["cachedRequests"]
            for item in cached_requests
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_cached_bandwidth(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total amount of cached bandwidth for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and the amount of cached bandwidth (in bytes) as values.
    """
    range_generated = range_generator(leq_date, periods)
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("cachedBandwidthOverTime"):
            raise ValueError("No cached bandwidth data available in the response.")
        cached_bandwidth = accounts[0]["cachedBandwidthOverTime"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["cachedBytes"]
            for item in cached_bandwidth
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_encrypted_requests(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total amount of encrypted requests for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and the number of encrypted requests as values.
    """
    range_generated = range_generator(leq_date, periods)
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("encryptedRequestsOverTime"):
            raise ValueError("No encrypted request data available in the response.")
        encrypted_requests = accounts[0]["encryptedRequestsOverTime"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["requests"]
            for item in encrypted_requests
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

def get_encrypted_bandwidth(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total amount of encrypted bandwidth for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and the total encrypted bandwidth (in bytes) as values.
    """
    range_generated = range_generator(leq_date, periods)
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("encryptedBandwidthOverTime"):
            raise ValueError("No encrypted bandwidth data available in the response.")
        encrypted_bandwidth = accounts[0]["encryptedBandwidthOverTime"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["bytes"]
            for item in encrypted_bandwidth
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")

# Error module
def get_fourxx_errors(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total amount of 4xx errors for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and the total 4xx errors as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetErrorTotals($accountTag: String, $filter: Filter, $errorFilter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    errorStats: httpRequestsOverviewAdaptiveGroups(
                        filter: {AND: [$filter, $errorFilter]},
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
        "errorFilter": {
            "edgeResponseStatus_geq": 400,
            "edgeResponseStatus_lt": 500,
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("errorStats"):
            raise ValueError("No 4xx error data available in the response.")
        error_stats = accounts[0]["errorStats"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["requests"]
            for item in error_stats
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response for 4xx errors: {e}") 

def get_fivexx_errors(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total amount of 5xx errors for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and the total 5xx errors as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetErrorTotals($accountTag: String, $filter: Filter, $errorFilter: Filter) {
            viewer {
                accounts(filter: {accountTag: $accountTag}) {
                    errorStats: httpRequestsOverviewAdaptiveGroups(
                        filter: {AND: [$filter, $errorFilter]},
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
        "accountTag": zone_tag,
        "filter": {
            "datetime_geq": range_generated["geq_date"],
            "datetime_leq": range_generated["leq_date"],
        },
        "errorFilter": {
            "edgeResponseStatus_geq": 500,
            "edgeResponseStatus_lt": 600,
        },
    }
    response = execute_query(query, variables)
    try:
        accounts = response["data"]["viewer"]["accounts"]
        if not accounts or not accounts[0].get("errorStats"):
            raise ValueError("No 5xx error data available in the response.")
        error_stats = accounts[0]["errorStats"]
        results = {
            item["dimensions"]["timestamp"]: item["sum"]["requests"]
            for item in error_stats
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response for 5xx errors: {e}")

#TODO Refactor these three functionsdef get_accounts(token: str):
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



# General module
# print(range_generator("2024-12-16", 7))
# Stats module
# print(get_requests_per_location(ID, "2024-12-16", 7))
# print(get_requests(ID, "2024-12-16", 7))
# print(get_bandwidth_per_location(ID, "2024-12-16", 7))
# print(get_bandwidth(ID, "2024-12-16", 7))
# print(get_visits(ID, "2024-12-16", 7))
# print(get_views(ID, "2024-12-16", 7))
# Network module
# print(get_http_versions(ID, "2024-12-16", 7))
# print(get_ssl_traffic(ID, "2024-12-16", 7))
# print(get_content_type(ID, "2024-12-16", 7))
# Cache module
# print(get_cached_requests(ID, "2024-12-16", 7))
# print(get_cached_bandwidth(ID, "2024-12-16", 7))
# Security module
# print(get_encrypted_requests(ID, "2024-12-16", 7))
# print(get_encrypted_bandwidth(ID, "2024-12-16", 7))
# Errors module
# print(get_fourxx_errors(ID, "2024-12-16", 7))
# print(get_fivexx_errors(ID, "2024-12-16", 7))
