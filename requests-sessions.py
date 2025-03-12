import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    "UserName": os.getenv("USER_NAME"),
    "Password": os.getenv("PASSWORD"),
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
    
    # Step 6: Navigate to Public Notices page
    public_notices_url = f"{base_url}/Home/PublicNotices"
    print(f"Navigating to Public Notices at {public_notices_url}...")
    public_notices_page = session.get(public_notices_url, headers=headers)
    print(f"Public Notices page status code: {public_notices_page.status_code}")
    
    # Step 7: Get the search form token
    search_soup = BeautifulSoup(public_notices_page.text, 'html.parser')
    search_token_input = search_soup.find('input', {'name': '__RequestVerificationToken'})
    search_token = search_token_input['value'] if search_token_input else None
    
    # Examine the county dropdown to understand its structure
    county_dropdown = search_soup.find('select', {'id': 'drpcounty'})
    if county_dropdown:
        print("Found county dropdown")
        kent_option = None
        for option in county_dropdown.find_all('option'):
            if option.text.strip() == 'Kent':
                kent_option = option
                print(f"Found Kent option: {option}")
                print(f"Kent option value: {option.get('value', 'Kent')}")
                break
    
    # Ask user for date range
    start_date = input("Enter start date (MM/DD/YYYY): ")
    end_date = input("Enter end date (MM/DD/YYYY): ")
    
    # Convert dates to the format expected by the website
    try:
        start_date_obj = datetime.strptime(start_date, "%m/%d/%Y")
        end_date_obj = datetime.strptime(end_date, "%m/%d/%Y")
        formatted_start_date = start_date_obj.strftime("%Y-%m-%d")
        formatted_end_date = end_date_obj.strftime("%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Using empty dates.")
        formatted_start_date = ""
        formatted_end_date = ""
    
    # Step 8: Prepare search form data
    search_data = {
        "action": "search",
        "search": "",
        "__RequestVerificationToken": search_token,
        "foreclosurePrevention": "false",
        "probates": "false",
        "vehicleAbandonment": "false",
        "other": "false",
        "drpproximity": "county",
        "drpcounty": "Kent",
        "city": "",
        "zip": "",
        "first_date_published": formatted_start_date,
        "first_date_published_thru": formatted_end_date,
        "last_date_published": "",
        "last_date_published_thru": "",
        "published_sale_date": "",
        "published_sale_date_thru": "",
        "nameOfNotice": "",
        "addressOfNotice": "",
        "attorney": "",
        "fileNumber": "",
        "internalId": "",
        "advancedSearchResults": "1",
        "proximity": "county",
        "county": "Kent"
    }
    
    # We can't have duplicate keys in a Python dictionary, so we need to handle the form data differently
    # Create a list of tuples for the form data to preserve duplicate keys
    form_data = []
    
    # Add all the regular fields
    for key, value in search_data.items():
        # Special handling for drpcounty to ensure Kent is selected
        if key == 'drpcounty':
            # Make sure we're using the correct value for Kent
            form_data.append((key, 'Kent'))
        else:
            form_data.append((key, value))
    
    # Add the special checkbox fields
    # For "foreclosures", we want it checked (true)
    form_data.append(("foreclosures", "true"))
    form_data.append(("foreclosures", "false"))
    
    # For other checkboxes, we want them unchecked (only false)
    form_data.append(("foreclosurePrevention", "false"))
    form_data.append(("probates", "false"))
    form_data.append(("vehicleAbandonment", "false"))
    form_data.append(("other", "false"))
    
    # Print the search data for debugging
    print("Search form data:", form_data)
    
    # Step 9: Submit the search form
    print("Submitting search form...")
    
    # Update headers to include referer
    search_headers = headers.copy()
    search_headers['Referer'] = public_notices_url
    search_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    # Submit the search form
    search_response = session.post(public_notices_url, data=form_data, headers=search_headers)
    print(f"Search response status code: {search_response.status_code}")
    
    # Debug: Save the search response to a file for inspection
    with open("search_response.html", "w", encoding="utf-8") as f:
        f.write(search_response.text)
    print("Saved search response to search_response.html for inspection")
    
    # Create a list to store all foreclosure data
    all_foreclosures = []
    
    # Function to scrape foreclosure details
    def scrape_foreclosure_details(detail_url, foreclosure_number):
        print(f"Scraping Foreclosure {foreclosure_number}: {detail_url}")
        detail_page = session.get(detail_url, headers=headers)
        
        if detail_page.status_code == 200:
            detail_soup = BeautifulSoup(detail_page.text, 'html.parser')
            
            # Extract the metadata (published dates)
            meta_dates = detail_soup.find('p', {'class': 'meta'})
            published_dates = meta_dates.text if meta_dates else "No dates found"
            
            # Extract the address
            address_elem = detail_soup.find_all('p', {'class': 'meta'})
            address = address_elem[1].text if len(address_elem) > 1 else "No address found"
            
            # Extract the name
            name_elem = detail_soup.find_all('p', {'class': 'meta'})
            name = name_elem[2].text if len(name_elem) > 2 else "No name found"
            
            # Extract the description
            description_elem = detail_soup.find('div', {'id': 'noticeDescription'})
            description = description_elem.text.strip() if description_elem else "No description found"
            
            # Create a dictionary for this foreclosure
            foreclosure_data = {
                "foreclosure_number": foreclosure_number,
                "published_dates": published_dates,
                "address": address,
                "name": name,
                "description": description,
                "url": detail_url
            }
            
            return foreclosure_data
        else:
            print(f"Failed to access detail page: {detail_url}")
            return None
    
    # Function to process a page of results
    def process_results_page(page_content, current_page, foreclosure_count):
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Find the result items - based on the image, we need to look for different HTML structure
        result_items = []
        
        # First try the div.result-item approach
        div_results = soup.find_all('div', {'class': 'result-item'})
        if div_results:
            result_items = div_results
        else:
            # If that doesn't work, try to find the results in the format shown in the image
            # Look for links with foreclosure addresses
            links = soup.find_all('a')
            for link in links:
                # Check if this is a foreclosure link (has href to PublicNoticesDetails)
                href = link.get('href', '')
                if '/Home/PublicNoticesDetails/' in href:
                    result_items.append(link.parent)  # Add the parent element containing the link
        
        print(f"Found {len(result_items)} results on page {current_page}")
        
        # Process each result item
        for item in result_items:
            # Find the link to the detail page
            link = item.find('a')
            if link and link.get('href'):
                # Construct the full URL
                href = link.get('href')
                if href.startswith('/'):
                    detail_url = base_url + href
                else:
                    detail_url = base_url + '/' + href
                
                # Scrape the foreclosure details
                foreclosure_data = scrape_foreclosure_details(detail_url, foreclosure_count)
                if foreclosure_data:
                    all_foreclosures.append(foreclosure_data)
                    foreclosure_count += 1
                
                # Add a small delay to avoid overloading the server
                time.sleep(1)
        
        return foreclosure_count
    
    # Debug: Check if we got any results
    soup = BeautifulSoup(search_response.text, 'html.parser')
    
    # Based on the image, the pagination might be different
    pagination = soup.find('div', {'id': 'pagination'})
    if not pagination:
        # Try alternative ways to find pagination info
        pagination_text = soup.find(text=lambda t: t and 'results found' in t)
        if pagination_text:
            pagination = pagination_text.parent
    
    if pagination:
        results_text = pagination.get_text()
        print(f"Pagination text: {results_text}")
        if 'results found' in results_text:
            print("Results found in pagination text")
    else:
        print("No pagination div found, might indicate no results or different page structure")
    
    # Start with page 1
    current_page = 1
    foreclosure_count = 1
    more_pages = True
    
    while more_pages:
        print(f"Processing page {current_page}...")
        
        # If it's the first page, we already have the content from the search response
        if current_page == 1:
            page_content = search_response.text
        else:
            # Otherwise, fetch the next page
            next_page_url = f"{public_notices_url}?page={current_page}"
            page_response = session.get(next_page_url, headers=headers)
            page_content = page_response.text
        
        # Process the current page
        foreclosure_count = process_results_page(page_content, current_page, foreclosure_count)
        
        # Check if there's a next page
        soup = BeautifulSoup(page_content, 'html.parser')
        pagination = soup.find('div', {'id': 'pagination'})
        
        # If we can't find pagination div, try alternative methods
        if not pagination:
            # Look for text containing "Page X of Y"
            page_text = soup.find(text=lambda t: t and 'Page' in t and 'of' in t)
            if page_text:
                pagination = page_text.parent
        
        # Debug pagination
        if pagination:
            print(f"Pagination text: {pagination.get_text()}")
        
        if pagination:
            # Try different ways to find the next link
            next_link = pagination.find('a', text=lambda t: t and ('≫' in t or 'Next' in t))
            if not next_link:
                next_link = pagination.find('a', string=lambda s: s and ('Next' in s or '>' in s))
            
            if next_link:
                print(f"Found next link: {next_link['href']}")
                current_page += 1
            else:
                print("No next link found")
                more_pages = False
        else:
            print("No pagination found")
            more_pages = False
    
    # Save the data to CSV
    csv_filename = "foreclosures.csv"
    print(f"Saving data to {csv_filename}...")
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['foreclosure_number', 'published_dates', 'address', 'name', 'description', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for foreclosure in all_foreclosures:
            writer.writerow(foreclosure)
    
    # Save the data to JSON
    json_filename = "foreclosures.json"
    print(f"Saving data to {json_filename}...")
    
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_foreclosures, jsonfile, indent=4)
    
    print(f"Scraping completed. Scraped {len(all_foreclosures)} foreclosures.")
    
else:
    print("Login failed!")
    print(f"Response text: {login_response.text[:500]}")  # Print first 500 chars of response



