#!/bin/bash

# Cloudflare API credentials
API_TOKEN="Zk7-FYWeIJX-e1yp24EpN6DcEuRoA7i3vfJZK1te"  # Replace with your actual API token

# Cloudflare API endpoint
CLOUDFLARE_API_URL="https://api.cloudflare.com/client/v4/zones"

# Send request to Cloudflare API and display the response
curl -s -X GET "$CLOUDFLARE_API_URL" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json"
