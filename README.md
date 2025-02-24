# Cloudflare Report Application

The Cloudflare Reports Application automates the generation of detailed reports
based on Cloudflare analytics.
It provides metrics on network performance, security, caching efficiency, and error tracking.
Presented in an easy-to-understand format.
Below is an overview of the custom-made libraries that uses:

- **cloudflare_utils**: Retrieves raw data from the GraphQL API
  *Currently it does not filter by zone*
- **image_utils**: Creates the graphs used in the final report
  *not the final desing yet*
- **pdf_utils**: Creates the pdf report.
  *not the final design yet, will work on custom design for each client*

## Architecture

The app uses Flask for the backend, with no data persitance *for the moment* and BS for the front.
The main idea behind the app is to query network data from cloudflare and present it to the client
along some useful recommendations, this will be done through email reports and live dashboards.
One current limitation in the free plan is that we can only query data from the last 7 days, so to
bypass that the app does snapshots every day for every client and saves it to a DB, the window data
for each client will depend on its plan, currently the maximum window we offer is 30d.

### DB Design
Currently we have 13 metrics *were missing more* lets say we start with 10 clients,
per Arturo: 80% of them will use the basic plan *7 days* that gives us 1000 rows per week
-that will die each week- and 800

## Milestones

- SMTP functionalities.
- DB for 30-day data storage.
- Live graphs, Grafana?
- Cron job querying.

## Issues

- cloudflare_utilities retrieves data for the whole account.
  You cant retrieve dara for a single zone directly, first you need to query data for the whole org
  and then filter it by zone, so my idea is to set a filter variable and perform querys for every single client,
  the problem is that it would take a lot of request. Maybe theres a way to retrieve all the data
  separated by zone. Requires further investigation.
- cloudflare_utilities is still missing security threats, performance and firewall metrics.
- No metadata db.
- No testing.
- Noting is integrated, everything is manually done.
- New metrics missing

## API Functionalities:

- Network:

  - Client HTTP version used: get_http_versions: Get the http client version used.
  - Traffic served over SSL: get_ssl_traffic: Get the traffic served over SSL.
  - Top content types: get_content_type: Get the top type of content served for the period.

- Errors:

  - 4xx errors: get_error_totals: Get the total amount of 4xx or 5xx errors for the period.
  - 4xx error rate: ** I believe this is just 4xx_request/total_requests **
  - 5xx errorss: get_error_totals: Get the total amount of 4xx or 5xx errors for the period.
  - 5xx error rate: ** I believe this is just 5xx_request/total_requests **

- Cache:

  - Cached requests: get_cached_requests: Get the total of cached requests for the period.
  - Cached request rate: ** I believe this is just cached_requests/total_requests **
  - Cached bandwidth: get_cached_bandwidth: Get the total amount of cached badwidth for the period.
  - Cached bandwidth rate: ** I believe this is just
    cached_badnwidth/total_bandiwdth **

- Security:

  - Encrypted requests: get_encrypted_requests: Get the total amount of encrypted requests for the period.
  - Encrypted requests rate: \*\* I believe this is just encryptes_requests/total_requests
  - Encrypted bandwidth: get_encrypted_bandwidth: Get the total amount of encrypted bandwidth for the period.
  - Encrypted bandwidth rate: ** I believe this is just
    encypted_bandwidth/total_bandiwdth **

- Stats:

  - Requests for top 10 countries: get_requests_per_location: Get the total number of request per country for the period.
  - Bandwidth for top 10 countries: get_bandwidth_per_location: Get the total bandwidth per country for the period.
  - Visits: get_vistits_totals: Get the total number of visits for the period.
  - Page views: get_page_views_totals: Get the total number of page views for the period.
  - Requests: get_requests: Get the total number of page views for the period.
  - Bandwidth:get_bandwidth: Get the total bandwidth for the period

- Auxiliar functions:

  - Date generator: geq_generator: Generates the end date for the query.
  - Percentage geneator: CURRENTLY NOT IMPLEMENTED. It should solve:

        Security:
            - Encrypted requests percentage
            - Encrypted request rate percentage
            - Encrypted bandwidth percentage
            - Encrypted bandwidth rate percentage

        Cache:
            - Cached request percentage
            - Cathed request rate percentage
            - Cached bandwidth percentage
            - Cached bandwidth rate percentage

        Network:
            - 4xx errors percentage
            - 5xx errors percentage

        Stats:
            - Requests percentage
            - Bandwidth percentage
            - Visits percentage
            - Page views percentage

        Errors:
            - 4xx errors percentage
            - 5xx errors percentage
