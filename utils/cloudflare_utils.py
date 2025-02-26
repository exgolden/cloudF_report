"""
V3 functions neccesary to run the Cloudflare API
"""

# TODO: Revisar que el leq date si contenga todos los datos del ultimo dia
# Stats Module
#   get_requests_per_location() ✅
#   get_requests() ✅
#   get_bandwdth_per_location() ✅
#   get_bandwidth() ✅
#   get_visits() ✅
#   get_views() ✅
# Network Module
#   get_http_versions() ✅
#   get_ssl_traffic() ✅
#   get_content_type() ✅
#   get_cached_requests() ✅
#   get_cached_bandwidth() ✅
# Security Module
#   get_encrypted_bandwidth() ✅
#   get_encrypted_requests() ✅
# Error Module
#   get_fourxx_errors() ✅
#   get_fivexx_errors() ✅
#
__version__ = "3.0.0"
import os

# Temporary settings and imports
import dotenv as env
from general_utils import execute_query, range_generator

env.load_dotenv()
TOKEN = os.getenv("CF_API_TOKEN")
ATDAC_ID = os.getenv("ATDAC_ID")
FLEX_ID = os.getenv("FLEX_ID")
ID = os.getenv("ACCOUNT_ID")
if not TOKEN:
    raise ValueError("No token found in configuration")


# Stats Module
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
        query GetZoneRequests($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        limit: 1000
                        filter: {date_geq: $since, date_leq: $until}
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            requests
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No request data available in the response.")
        request_totals = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["requests"]
            for item in request_totals
        }
        return results
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")


def get_requests_per_location(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetRequestsLocations($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        sum {
                            countryMap {
                                clientCountryName
                                requests
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No location data available in the response.")
        location_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in location_totals:
            for country in daily["sum"]["countryMap"]:
                country_name = country["clientCountryName"]
                requests = country["requests"]
                results[country_name] = results.get(country_name, 0) + requests
        sorted_results = dict(
            sorted(results.items(), key=lambda item: item[1], reverse=True)[:10]
        )
        return sorted_results
    except (KeyError, IndexError, TypeError) as e:
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
        query GetZoneBandwidth($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        limit: 1000,
                        filter: {date_geq: $since, date_leq: $until}
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            bytes
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No bandwidth data available in the response.")
        bandwidth_totals = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["bytes"]
            for item in bandwidth_totals
        }
        return results
    except (KeyError, IndexError, TypeError) as e:
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
        query GetBandwidthLocations($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        sum {
                            countryMap {
                                clientCountryName
                                bytes
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No bandwidth data available in the response.")
        location_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in location_totals:
            for country in daily["sum"]["countryMap"]:
                country_name = country["clientCountryName"]
                bandwidth = country["bytes"]
                results[country_name] = results.get(country_name, 0) + bandwidth
        sorted_results = dict(
            sorted(results.items(), key=lambda item: item[1], reverse=True)[:10]
        )
        return sorted_results
    except (KeyError, IndexError, TypeError) as e:
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
        query GetZoneVisits($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        limit: 1000,
                        filter: {date_geq: $since, date_leq: $until}
                    ) {
                        dimensions {
                            date
                        }
                        uniq {
                            uniques
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No visit data available in the response.")
        visit_totals = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["uniq"]["uniques"] for item in visit_totals
        }
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_views(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetZonePageViews($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        limit: 1000,
                        filter: {date_geq: $since, date_leq: $until}
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            pageViews
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No page view data available in the response.")
        view_totals = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["pageViews"] for item in view_totals
        }
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


# Network Module
def get_http_versions(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetHttpProtocols($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            clientHTTPVersionMap {
                                requests
                                clientHTTPProtocol
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No HTTP protocols data available in the response.")
        protocol_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in protocol_totals:
            for protocol in daily["sum"]["clientHTTPVersionMap"]:
                proto = protocol["clientHTTPProtocol"]
                req_count = protocol["requests"]
                results[proto] = results.get(proto, 0) + req_count
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_ssl_traffic(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetSSLTraffic($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        sum {
                            clientSSLMap {
                                requests
                                clientSSLProtocol
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No SSL data available in the response.")
        ssl_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in ssl_totals:
            for protocol in daily["sum"]["clientSSLMap"]:
                ssl_proto = protocol["clientSSLProtocol"]
                requests = protocol["requests"]
                results[ssl_proto] = results.get(ssl_proto, 0) + requests
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_content_type(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetContentTypes($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        sum {
                            contentTypeMap {
                                requests
                                edgeResponseContentTypeName
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No content type data available in the response.")
        content_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in content_totals:
            for content in daily["sum"]["contentTypeMap"]:
                content_type = content["edgeResponseContentTypeName"]
                requests = content["requests"]
                results[content_type] = results.get(content_type, 0) + requests
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_cached_requests(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetCachedRequests($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            cachedRequests
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No cached requests data available in the response.")
        cached_requests = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["cachedRequests"]
            for item in cached_requests
        }
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_cached_bandwidth(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetCachedBandwidth($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            cachedBytes
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No cached bandwidth data available in the response.")
        cached_bandwidth = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["cachedBytes"]
            for item in cached_bandwidth
        }
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


# Security Module
def get_encrypted_bandwidth(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetEncryptedBandwidth($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            encryptedBytes
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No encrypted bandwidth data available in the response.")
        encrypted_bandwidth = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["encryptedBytes"]
            for item in encrypted_bandwidth
        }
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_encrypted_requests(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetEncryptedRequests($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            encryptedRequests
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No encrypted request data available in the response.")
        encrypted_requests = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["encryptedRequests"]
            for item in encrypted_requests
        }
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


# Error Module
def get_fourxx_errors(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetFourXXErrors($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            responseStatusMap {
                                requests
                                edgeResponseStatus
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No 4xx error data available in the response.")
        error_stats = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in error_stats:
            date = daily["dimensions"]["date"]
            total_4xx = sum(
                status["requests"]
                for status in daily["sum"]["responseStatusMap"]
                if 400 <= int(status["edgeResponseStatus"]) < 500
            )
            results[date] = total_4xx
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response for 4xx errors: {e}")


def get_fivexx_errors(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetFiveXXErrors($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            responseStatusMap {
                                requests
                                edgeResponseStatus
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(TOKEN, query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No 5xx error data available in the response.")
        error_stats = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in error_stats:
            date = daily["dimensions"]["date"]
            total_5xx = sum(
                status["requests"]
                for status in daily["sum"]["responseStatusMap"]
                if 500 <= int(status["edgeResponseStatus"]) < 600
            )
            results[date] = total_5xx
        return results
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response for 5xx errors: {e}")
