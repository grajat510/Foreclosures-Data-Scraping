import requests
from bs4 import BeautifulSoup

# Create a session object to maintain cookies
session = requests.Session()

# Set headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Base URL
base_url = "https://legalnews.com"

# Step 1: Visit the login page to get the anti-forgery token
login_page_url = f"{base_url}/Home/Login"
print(f"Visiting login page at {login_page_url}...")
login_page = session.get(login_page_url, headers=headers)
print(f"Login page status code: {login_page.status_code}")

# Step 2: Parse the login page to extract the token
soup = BeautifulSoup(login_page.text, 'html.parser')
token_input = soup.find('input', {'name': '__RequestVerificationToken'})
token = token_input['value'] if token_input else None
print(f"Extracted token: {token}")

# Step 3: Prepare the login payload
payload = {
    "UserName": "mikerossgrandrapidsrealty@gmail.com",
    "Password": "password",
    "__RequestVerificationToken": token
}

# Step 4: Submit the login form
login_url = f"{base_url}/Home/ValidateUser"
print(f"Sending login request to {login_url}...")
login_response = session.post(login_url, data=payload, headers=headers)
print(f"Login response status code: {login_response.status_code}")

# Step 5: Check if login was successful
if login_response.status_code == 200:
    print("Login successful!")
    
    # Example: Access a secure page
    secure_page_url = f"{base_url}/Detroit/Search"  # Replace with the actual secure page you want to access
    print(f"Accessing secure page at {secure_page_url}...")
    secure_page = session.get(secure_page_url, headers=headers)
    print(f"Secure page status code: {secure_page.status_code}")
    
    # Optional: Save the secure page content to a file
    # with open("secure_page.html", "w", encoding="utf-8") as f:
    #     f.write(secure_page.text)
    # print("Secure page content saved to secure_page.html")
    
    # Example: Parse and extract data from the secure page
    secure_soup = BeautifulSoup(secure_page.text, 'html.parser')
    page_title = secure_soup.title.text if secure_soup.title else "No title found"
    print(f"Secure page title: {page_title}")
    
    # You can add more code here to extract specific data from the secure page
    
else:
    print("Login failed!")
    print(f"Response text: {login_response.text[:500]}")  # Print first 500 chars of response



