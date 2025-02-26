# Cloudflare Report Application

The Cloudflare Reports Application automates the generation of detailed reports
based on Cloudflare analytics.
It provides metrics on network performance, security, caching efficiency, and error tracking.
Presented in an easy-to-understand format.
Below is an overview of the custom-made libraries that uses:

- **general_utils**: Basic tools used for cloudflare_utils.
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
- Security threats missing
- Attacsk blocked metric ⚠️
- New section: DNS Analytics:
  - Queries by source
  - Query name
  - Response Code
  - Record type
  - Source IP
  - Destination IP
  No se de donde saca esto
- New section: Security Events:
  - Action taken
  - Country
  - IP address
  - Rule
  - Host
  - Path
  No se de donde saca esto
- Revisar que el leq date siVy contenga todos los datos del ultimo dia

## Issues
- cloudflare_utilities is still missing security threats, performance and firewall metrics.
- No metadata db.
- No testing.
- Noting is integrated, everything is manually done.

## API Functionalities:

- Network:

  - Client HTTP version used: get_http_versions: Http client version used. ✅
  - Traffic served over SSL: get_ssl_traffic: Traffic served over SSL. ✅
  - Top content types: get_content_type: Content type served. ✅

- Errors:

  - 4xx errors: get_error_totals: Total of 4xx errors. ✅
  - 5xx errorss: get_error_totals: Total of 5xx errors. ✅
  - 5xx error rate: WILL NOT BE IMPLEMENTED. 🛑
  - 4xx error rate: WILL NOT BE IMPLEMENTED. 🛑


- Cache:

  - Cached requests: get_cached_requests: Total of cached requests. ✅
  - Cached bandwidth: get_cached_bandwidth: Total amount of cached badwidth. ✅
  - Cached bandwidth rate: WILL NOT BE IMPLEMENTED. 🛑
  - Cached request rate: WILL NOT BE IMPLEMENTED. 🛑

- Security:

  - Encrypted requests: get_encrypted_requests: Total of encrypted requests. ✅
  - Encrypted bandwidth: get_encrypted_bandwidth: Total of encrypted bandw. ✅
  - Encrypted requests rate: WILL NOT BE IMPLEMENTED. 🛑
  - Encrypted bandwidth rate: WILL NOT BE IMPLEMENTED. 🛑

- Stats:

  - Requests for top 10 countries: get_requests_per_location: Total of request per country. ✅
  - Bandwidth for top 10 countries: get_bandwidth_per_location: Bandwidth per country. ✅
  - Visits: get_vistits_totals: Total of visits. ✅
  - Page views: get_page_views_totals: Total number of page views. ✅
  - Requests: get_requests: Total number of requests. ✅
  - Bandwidth: get_bandwidth: Total bandwidth. ✅
  - Unique visitors: ⚠️

- General functions:

  - Date generator: geq_generator: Generates the end date for the query. ✅
  - Query executor execute_query: Executes the querys. ✅
  - Get Accounts get_accounts: Acc/ID associated to the Cloudflare instance. ✅
  - Get Zones get_zones: Zones/ID associated to the Cloudflare instance. ✅
  - Get account settings get_account_settings: WILL NOT BE IMPLEMENTED   🛑
  - Percentage geneator: WILL NOT BE IMPLEMENTED 🛑

## PDF Desing

**HTTP Traffic**
Visión general del tráfico HTTP. Facilita la identificación de patrones de tráfico, la eficiencia del caché y la distribución de visitantes únicos por país, ayudando a optimizar el rendimiento y la capacidad de respuesta de la infraestructura.

  - Total Requests as stat
  - Cached Requests as stat
  - Uncached Requests as stat
  - 7/30d graph for both cached & uncached requests.

  - Total bandiwdth as stat
  - Cached bandiwdth as stat
  - Uncached bandwidth as stat
  - 7/30d graph for both cached & uncached bandwidth.

  - Total unique visitors as stat
  - Maximum unique visitors per day as stat
  - Minimum unique visitors per day as stat
  - 7/30d graph for unique visitors
  - Top 5 traffic countries & list

**Performance**
Evalúa el desempeño de la red en términos de eficiencia y optimización del tráfico mediante cache. Esta información es clave para mejorar la velocidad de carga y la experiencia del usuario.

  - Bandwidth served as stat
  - Bandwidth saved as stat (% and total)
  - SSL requests served as stat
  - Attacks Blocked as stat
  - HTTP Client version (top 2) as pie chart
  - Content type served *Must show how many files it delivered for everyting* as bar chart. ⚠️

**Security Events**
Muestra las amenazas detectadas en la red, país de origen y tipo de ataque más. Asi como la actividad de bots/crawlers, ayudando a reforzar la seguridad y minimizar riesgos de tráfico malicioso.
  - Total threats as stat along with the top country
  - Top threat as stat
  - Top crawlers/bot as list
