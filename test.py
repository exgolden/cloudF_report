"""
Testing
"""
from utils.image_v2 import line_graph
from tests.test_data import TEST_FOUR_ERRORS, TEST_BYTES  
# line_graph(TEST_FOUR_ERRORS, "./assets/general_stats/test_graph")
line_graph(TEST_BYTES, "./assets/general_stats/test_bytes_graph",data_type="bytes")






# # Temporal imports
# import dotenv as env
#
# from cloudflare_lib import *
#
# env.load_dotenv()
# TOKEN = os.getenv("CF_API_TOKEN")
# ID = os.getenv("ACCOUNT_ID")
# if not TOKEN or not ID:
#     raise ValueError("No token or account ID found in configuration")
#

# get_encrypted_bandwidth(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_encrypted_requests(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_cached_bandwidth(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_cached_requests(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_content_type(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_http_versions(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_bandwidth(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_page_views_total(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_visits_total(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_bandwidth_per_location(TOKEN, ID, 10, "2024-12-16T22:58:00Z", 7)
# get_requests_per_location(TOKEN, ID, "2024-12-16T22:58:00Z", 7)
# get_error_totals(TOKEN, ID, 5, "2024-12-16T22:58:00Z", 7)
# get_requests(TOKEN, ID, 4, "2024-12-16T22:58:00Z", 7)
# get_ssl_traffic(TOKEN, ID, 4, "2024-12-16T22:58:00Z", 7)
