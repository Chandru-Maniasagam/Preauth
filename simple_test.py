import requests

# Test the API endpoint
url = "https://preauth-11.onrender.com/api/v1/claims/"
headers = {
    "X-Hospital-ID": "HOSP_001",
    "X-User-ID": "test_user",
    "X-User-Name": "Test User"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
