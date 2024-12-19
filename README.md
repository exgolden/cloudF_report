# cloudF_report

Obtain a report with general analytics of CloudFlare

## Issues

- Sometimes the API returns totals for everyday in the period and sometimes it
  returns data for the whole period, for example get_requests &
  get_requests_per_location gives me data for the whole period, not for teach day
  iin the period. Maybe I can set a parameter in the function, initially it will
  return data for each day, if this patameter is acticates, then it will return
  the totals. I can also forget about request for everyday if only a per weekend
  or month analysis is required.
- Normalize documentation.

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
  - Cached request rate
  - Cached bandwidth
  - Cached bandwidth rate

- Security:

  - Encrypted requests
  - Encrypted requests rate
  - Encrypted bandwidth
  - Encrypted bandwidth rate

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

## Testing

1. Add a test to check the error type in get_error_totals
