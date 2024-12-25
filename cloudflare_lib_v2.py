"""
 V2 functions neccesary to run the Cloudflare API
"""

import json
import os
from datetime import datetime, timedelta
import requests

# Temporary settings and imports
import dotenv as env
env.load_dotenv()
TOKEN = os.getenv("CF_API_TOKEN")
ID = os.getenv("ACCOUNT_ID")
if not TOKEN or not ID:
    raise valueError("No token or account ID found in configuration")

# Date Generator
def geq_generator(start_date: str, periods: int):
    """
    Generates the end date for the query by sbstracting a specified number of periods from the start date.
    Args:
        start_date (str): Start of the date range (ISO 8601 format).
        periods (int): NUmber f periods after the start_date (days to substract)
    Returns:
        str: Greater or equal date for the range (ISO 8601 format).
    Raises:
        ValueError: If the start_date format is invalid or periods in negative
    """
    #TODO The date generator takes time as part of the start_date. This is not neccesary
    if periods < 0:
        raise valueError("Periods must be a non-negative integer.")
    days_to_subtract = periods - 1
    try:
        start = datetime.strptime(start_date,  "%Y-%m-%dT%H:%M:%SZ")
        end = start - timedelta( "%Y-%m-%dT%H:%M:%SZ")
        return end.strftime( "%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        raise valueError( f"Invalid date format: '{start_date}'. Use ISO 8601 format 'YYYY-MM-DDTHH:MM:SSZ'."
        ) from e






