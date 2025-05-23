import requests
import sys

# Test the local running application
base_url = "http://127.0.0.1:5000"

try:
    print("Testing connection to application...")
    response = requests.get(base_url)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text[:100]}...")  # Display the first 100 chars
except requests.exceptions.ConnectionError:
    print("ERROR: Failed to connect to the application. Make sure it's running.")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)

print("\nTesting endpoints that might cause internal server errors:")

endpoints = [
    "/",
    "/login",
    "/register",
    "/profile",
    "/admin",
    "/translate",
    "/suggest"
]

for endpoint in endpoints:
    try:
        url = base_url + endpoint
        print(f"\nTesting {url}...")
        
        # Use GET for most endpoints, POST for API endpoints
        if endpoint in ["/translate", "/suggest"]:
            response = requests.post(url, data={"word": "test"})
        else:
            response = requests.get(url)
            
        print(f"Status code: {response.status_code}")
        if response.status_code >= 500:
            print("INTERNAL SERVER ERROR detected!")
            print(f"Response: {response.text[:200]}...")  # Show more of the error
    except Exception as e:
        print(f"ERROR accessing {endpoint}: {str(e)}") 