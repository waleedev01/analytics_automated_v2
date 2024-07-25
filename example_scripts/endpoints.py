import requests

# URL endpoint for fetching required parameters
endpoints_url = 'http://127.0.0.1:8000/analytics_automated/endpoints'

# Make GET request to fetch the required parameters
endpoints_response = requests.get(endpoints_url)

# Print the raw response content to debug
print("Raw response content:")
print(endpoints_response.text)

# Try to parse the response as JSON and print it
try:
    endpoints_json = endpoints_response.json()
    print("JSON response content:")
    print(endpoints_json)
except ValueError as e:
    print("Failed to parse JSON response:", e)