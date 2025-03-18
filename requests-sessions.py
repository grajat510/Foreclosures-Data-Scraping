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
    
    # Debug token extraction
    if search_token:
        print(f"Extracted search token: {search_token}")
    else:
        print("Warning: Could not extract search token")
        # Try to find any form with a token
        forms = search_soup.find_all('form')
        for form in forms:
            token_input = form.find('input', {'name': '__RequestVerificationToken'})
            if token_input and token_input.get('value'):
                search_token = token_input.get('value')
                print(f"Found alternative token: {search_token}")
                break
        
        # If still no token, reuse the login token as a fallback
        if not search_token:
            print("Using login token as fallback")
            search_token = token
    
    # Extract all counties from the dropdown
    county_dropdown = search_soup.find('select', {'id': 'drpcounty'})
    counties = []
    counties_values = {}  # Store the values along with the display text
    
    if county_dropdown:
        print("Found county dropdown")
        # First add "All Counties" option if it exists
        all_counties_option = county_dropdown.find('option', {'value': 'all'})
        if all_counties_option:
            counties.append("All Counties")
            counties_values["All Counties"] = "all"  # Store the value "all" for All Counties
        
        # Then add individual counties
        for option in county_dropdown.find_all('option'):
            if option.get('data-isaccess') == "True":
                county_name = option.text.strip()
                counties.append(county_name)
                # Store the value attribute if it exists, otherwise use the text
                counties_values[county_name] = option.get('value', county_name)
        
        print(f"Found {len(counties)} counties")
    else:
        # Fallback list if dropdown not found on the page
        counties = [
            "All Counties", "Alcona", "Alger", "Allegan", "Alpena", "Antrim", "Arenac", "Baraga", 
            "Barry", "Bay", "Benzie", "Berrien", "Branch", "Calhoun", "Cass", "Charlevoix", 
            "Cheboygan", "Chippewa", "Clare", "Clinton", "Crawford", "Delta", "Dickinson", 
            "Eaton", "Emmet", "Genesee", "Gladwin", "Gogebic", "Grand Traverse", "Gratiot", 
            "Hillsdale", "Houghton", "Huron", "Ingham", "Ionia", "Iosco", "Iron", "Isabella", 
            "Jackson", "Kalamazoo", "Kalkaska", "Kent", "Keweenaw", "Lake", "Lapeer", "Leelanau", 
            "Lenawee", "Livingston", "Luce", "Mackinac", "Macomb", "Manistee", "Marquette", 
            "Mason", "Mecosta", "Menominee", "Midland", "Missaukee", "Monroe", "Montcalm", 
            "Montmorency", "Muskegon", "Newaygo", "Oakland", "Oceana", "Ogemaw", "Ontonagon", 
            "Osceola", "Oscoda", "Otsego", "Ottawa", "Presque Isle", "Roscommon", "Saginaw", 
            "Saint Clair", "Saint Joseph", "Sanilac", "Schoolcraft", "Shiawassee", "Tuscola", 
            "Van Buren", "Washtenaw", "Wayne", "Wexford"
        ]
        # Set default values for fallback
        counties_values = {county: county for county in counties}
        counties_values["All Counties"] = "all"  # Special case for All Counties
        print(f"Using fallback county list with {len(counties)} counties")

    # Display county options to user
    print("\nAvailable counties:")
    for i, county in enumerate(counties, 1):
        print(f"{i}. {county}")

    # Get county selection from user
    selected_county_index = 0
    while selected_county_index < 1 or selected_county_index > len(counties):
        try:
            selected_county_index = int(input(f"\nSelect a county (1-{len(counties)}): "))
            if selected_county_index < 1 or selected_county_index > len(counties):
                print(f"Please enter a number between 1 and {len(counties)}")
        except ValueError:
            print("Please enter a valid number")

    selected_county = counties[selected_county_index - 1]
    print(f"Selected county: {selected_county}")
    
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
    county_value = counties_values.get(selected_county, selected_county)
    print(f"Using county value: {county_value} for {selected_county}")
    
    search_data = {
        "action": "search",
        "search": "",
        "__RequestVerificationToken": search_token,
        "foreclosurePrevention": "false",
        "probates": "false",
        "vehicleAbandonment": "false",
        "other": "false",
        "drpproximity": "county",
        "drpcounty": county_value,
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
        "county": county_value
    }
    
    # We can't have duplicate keys in a Python dictionary, so we need to handle the form data differently
    # Create a list of tuples for the form data to preserve duplicate keys
    form_data = []
    
    # Add all the regular fields
    for key, value in search_data.items():
        # Special handling for drpcounty to use selected county value
        if key == 'drpcounty':
            form_data.append((key, county_value))
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
        pagination_text = soup.find(string=lambda t: t and 'results found' in t)
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
            page_text = soup.find(string=lambda t: t and 'Page' in t and 'of' in t)
            if page_text:
                pagination = page_text.parent
        
        # Debug pagination
        if pagination:
            print(f"Pagination text: {pagination.get_text()}")
        
        if pagination:
            # Try different ways to find the next link
            next_link = pagination.find('a', string=lambda t: t and ('≫' in t or 'Next' in t))
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
    
    # Save the data to JSON
    json_filename = "foreclosures.json"
    print(f"Saving data to {json_filename}...")
    
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_foreclosures, jsonfile, indent=4)
    
    print(f"Scraping completed. Scraped {len(all_foreclosures)} foreclosures.")

    #Data Cleaning using Groq
    print("Starting data processing with Groq API...")
    
    # Define helper functions before using them
    # Function to process a single batch with requests
    def process_batch_with_requests(batch, api_key, processed_records):
        import requests
        
        # Define the API URL
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Define the headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Create the payload
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a data extraction expert. Extract structured data from foreclosure notices."},
                {"role": "user", "content": f"""
                Extract the following fields from these foreclosure notices and return as JSON: 
                1) First Name (extracted from the person's name)
                2) Middle Name (extracted from the person's name, can be empty)
                3) Last Name (extracted from the person's name)
                4) Street Address (the full street address)
                5) City
                6) State
                7) Zip
                8) Mortgage or a lien (Condo?)
                9) Sale Date
                10) Amount Due
                11) Redemption Period
                12) Attorney Name
                13) Attorney Address
                14) Attorney phone number (as 'Attorney phone number')
                15) Attorney File #
                16) First date published in Legal News (as 'First date published in Legal News')
                17) Last Date Published in Legal News
                18) Lender/Mortgage company's name
                19) Recorded Date
                
                IMPORTANT: 
                1. Please use EXACTLY these field names in your response.
                2. The original 'Name' field should be split into First Name, Middle Name, and Last Name.
                3. If there is no middle name, return an empty string for Middle Name.
                4. Use 'Street Address' instead of 'Address' for the street address field.
                
                Here's the data: {json.dumps(batch, indent=2)}
                """}
            ],
            "temperature": 0.2,
            "max_tokens": 4000
        }
        
        try:
            # Make the API call
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to parse the response
                try:
                    if '```json' in content:
                        json_str = content.split('```json')[1].split('```')[0].strip()
                        batch_records = json.loads(json_str)
                        processed_records.extend(batch_records)
                    elif '```' in content:
                        json_str = content.split('```')[1].split('```')[0].strip()
                        if json_str.startswith('json'):
                            json_str = json_str[4:].strip()
                        batch_records = json.loads(json_str)
                        processed_records.extend(batch_records)
                    else:
                        try:
                            batch_records = json.loads(content)
                            processed_records.extend(batch_records if isinstance(batch_records, list) else [batch_records])
                        except:
                            print(f"Could not parse response for this batch")
                except Exception as e:
                    print(f"Error parsing response: {str(e)}")
            else:
                print(f"API call failed with status code {response.status_code}")
                print(response.text)
        
        except Exception as e:
            print(f"Error making API request: {str(e)}")

    # Function to process with requests as a fallback for the entire dataset
    def process_with_requests(foreclosure_data, api_key):
        if not api_key:
            print("No API key provided for fallback processing")
            return
            
        import requests
        
        # Define the API URL
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Define the headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        processed_records = []
        
        # Process foreclosures in batches
        batch_size = 5
        for i in range(0, len(foreclosure_data), batch_size):
            batch = foreclosure_data[i:i+batch_size]
            
            # Create the payload
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are a data extraction expert. Extract structured data from foreclosure notices."},
                    {"role": "user", "content": f"""
                    Extract the following fields from these foreclosure notices and return as JSON: 
                    1) First Name (extracted from the person's name)
                    2) Middle Name (extracted from the person's name, can be empty)
                    3) Last Name (extracted from the person's name)
                    4) Street Address (the full street address)
                    5) City
                    6) State
                    7) Zip
                    8) Mortgage or a lien (Condo?)
                    9) Sale Date
                    10) Amount Due
                    11) Redemption Period
                    12) Attorney Name
                    13) Attorney Address
                    14) Attorney phone number (as 'Attorney phone number')
                    15) Attorney File #
                    16) First date published in Legal News (as 'First date published in Legal News')
                    17) Last Date Published in Legal News
                    18) Lender/Mortgage company's name
                    19) Recorded Date
                    
                    IMPORTANT: 
                    1. Please use EXACTLY these field names in your response.
                    2. The original 'Name' field should be split into First Name, Middle Name, and Last Name.
                    3. If there is no middle name, return an empty string for Middle Name.
                    4. Use 'Street Address' instead of 'Address' for the street address field.
                    
                    Here's the data: {json.dumps(batch, indent=2)}
                    """}
                ],
                "temperature": 0.2,
                "max_tokens": 4000
            }
            
            try:
                # Make the API call
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Try to parse the response
                    try:
                        if '```json' in content:
                            json_str = content.split('```json')[1].split('```')[0].strip()
                            batch_records = json.loads(json_str)
                            processed_records.extend(batch_records)
                        elif '```' in content:
                            json_str = content.split('```')[1].split('```')[0].strip()
                            if json_str.startswith('json'):
                                json_str = json_str[4:].strip()
                            batch_records = json.loads(json_str)
                            processed_records.extend(batch_records)
                        else:
                            try:
                                batch_records = json.loads(content)
                                processed_records.extend(batch_records if isinstance(batch_records, list) else [batch_records])
                            except:
                                print(f"Could not parse response for batch {i//batch_size + 1}")
                    except Exception as e:
                        print(f"Error parsing response: {str(e)}")
                else:
                    print(f"API call failed with status code {response.status_code}")
                    print(response.text)
            
            except Exception as e:
                print(f"Error making API request: {str(e)}")
            
            print(f"Processed batch {i//batch_size + 1} of {(len(foreclosure_data)-1)//batch_size + 1}")
            time.sleep(1)
        
        # Save the processed data
        ai_csv_filename = "foreclosures_processed.csv"
        print(f"Saving processed data to {ai_csv_filename}...")
        
        # Define the fields with exactly matching names
        ai_fieldnames = [
            'First Name', 'Middle Name', 'Last Name', 'Street Address', 'City', 'State', 'Zip', 
            'Mortgage or a lien (Condo?)', 'Sale Date', 'Amount Due', 'Redemption Period',
            'Attorney Name', 'Attorney Address', 'Attorney phone number', 'Attorney File #',
            'First date published in Legal News', 'Last Date Published in Legal News',
            'Lender/Mortgage company\'s name', 'Recorded Date'
        ]
        
        with open(ai_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ai_fieldnames)
            writer.writeheader()
            for record in processed_records:
                # Create a new record with standardized field names
                standardized_record = {}
                
                # Handle Name field splitting if Name is present but First/Middle/Last are not
                if 'Name' in record and not ('First Name' in record and 'Last Name' in record):
                    name_parts = record['Name'].split()
                    if len(name_parts) == 1:
                        # Only one name part available
                        standardized_record['First Name'] = name_parts[0]
                        standardized_record['Middle Name'] = ""
                        standardized_record['Last Name'] = ""
                    elif len(name_parts) == 2:
                        # First and Last name
                        standardized_record['First Name'] = name_parts[0]
                        standardized_record['Middle Name'] = ""
                        standardized_record['Last Name'] = name_parts[1]
                    else:
                        # First, Middle (possibly multiple), and Last name
                        standardized_record['First Name'] = name_parts[0]
                        standardized_record['Last Name'] = name_parts[-1]
                        standardized_record['Middle Name'] = " ".join(name_parts[1:-1])
                
                # Handle Address to Street Address conversion
                if 'Address' in record and 'Street Address' not in record:
                    standardized_record['Street Address'] = record['Address']
                
                # Process all other fields
                for field in ai_fieldnames:
                    # Skip already handled fields
                    if field in ['First Name', 'Middle Name', 'Last Name'] and 'Name' in record:
                        continue
                    if field == 'Street Address' and 'Address' in record:
                        continue
                        
                    # Try different variations of field names
                    if field in record:
                        standardized_record[field] = record[field]
                    # Try with lowercase
                    elif field.lower() in {k.lower(): k for k in record}:
                        matching_key = {k.lower(): k for k in record}[field.lower()]
                        standardized_record[field] = record[matching_key]
                    # Handle special cases
                    elif field == 'Attorney phone number' and 'Attorney Phone Number' in record:
                        standardized_record[field] = record['Attorney Phone Number']
                    elif field == 'First date published in Legal News' and 'First Date Published in Legal News' in record:
                        standardized_record[field] = record['First Date Published in Legal News']
                    # Ensure all required fields have a value
                    elif field not in standardized_record:
                        standardized_record[field] = "N/A"
                
                writer.writerow(standardized_record)
        
        print(f"AI processing completed with fallback method. Saved to {ai_csv_filename}")
        
    try:
        from groq import Groq
        
        # Load the foreclosure data
        with open("foreclosures.json", 'r', encoding='utf-8') as f:
            foreclosure_data = json.load(f)
        
        # Initialize Groq client
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            print("GROQ_API_KEY not found in environment variables.")
            raise ValueError("GROQ_API_KEY is required")
        
        # Initialize with the updated Groq client
        client = Groq(api_key=groq_api_key)
        
        # Create processed records list
        processed_records = []
        
        # Process foreclosures in batches to avoid token limits
        batch_size = 5
        for i in range(0, len(foreclosure_data), batch_size):
            batch = foreclosure_data[i:i+batch_size]
            
            # Create a combined prompt with the current batch
            combined_prompt = f"""
            I need to extract structured data from these foreclosure notices. Please parse the following JSON data and extract these fields:
            
            1) First Name (extracted from the person's name)
            2) Middle Name (extracted from the person's name, can be empty)
            3) Last Name (extracted from the person's name)
            4) Street Address (the full street address)
            5) City
            6) State
            7) Zip
            8) Mortgage or a lien (Condo?)
            9) Sale Date
            10) Amount Due
            11) Redemption Period
            12) Attorney Name
            13) Attorney Address
            14) Attorney phone number
            15) Attorney File #
            16) First date published in Legal News
            17) Last Date Published in Legal News
            18) Lender/Mortgage company's name
            19) Recorded Date
            
            Return the data as a JSON array with these fields for each record. If a field cannot be found, use null or N/A.
            
            IMPORTANT: 
            1. Please use EXACTLY these field names in your response.
            2. The original 'Name' field should be split into First Name, Middle Name, and Last Name.
            3. If there is no middle name, return an empty string for Middle Name.
            4. Use 'Street Address' instead of 'Address' for the street address field.
            
            Here is the foreclosure data to parse:
            {json.dumps(batch, indent=2)}
            """
            
            # Make API call to Groq
            try:
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You are a data extraction expert. Extract structured data from foreclosure notices."},
                        {"role": "user", "content": combined_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4000
                )
                
                # Parse the response from Groq
                result = response.choices[0].message.content
                
                # Parse the AI's response to get structured data
                try:
                    # Try to detect if the AI returned JSON
                    if '```json' in result:
                        json_str = result.split('```json')[1].split('```')[0].strip()
                        batch_records = json.loads(json_str)
                        processed_records.extend(batch_records)
                    elif '```' in result:
                        # Try to find any code block
                        json_str = result.split('```')[1].split('```')[0].strip()
                        if json_str.startswith('json'):
                            json_str = json_str[4:].strip()
                        batch_records = json.loads(json_str)
                        processed_records.extend(batch_records)
                    else:
                        # Try to parse the whole response as JSON
                        try:
                            batch_records = json.loads(result)
                            processed_records.extend(batch_records if isinstance(batch_records, list) else [batch_records])
                        except:
                            print(f"Received text response from Groq for batch {i//batch_size + 1}, manual parsing needed.")
                            print(result[:500] + "..." if len(result) > 500 else result)
                except Exception as e:
                    print(f"Error parsing Groq response: {str(e)}")
                    print(result[:500] + "..." if len(result) > 500 else result)
                    
            except Exception as e:
                print(f"Error calling Groq API: {str(e)}")
                # If there's an error with the Groq client, fall back to using requests
                print("Falling back to using requests for this batch...")
                process_batch_with_requests(batch, groq_api_key, processed_records)
            
            print(f"Processed batch {i//batch_size + 1} of {(len(foreclosure_data)-1)//batch_size + 1}")
            time.sleep(1)  # Avoid rate limits
        
        # Save the processed data to CSV with the required fields
        ai_csv_filename = "foreclosures_processed.csv"
        print(f"Saving processed data to {ai_csv_filename}...")
        
        # Define the fields as per the requirements
        ai_fieldnames = [
            'First Name', 'Middle Name', 'Last Name', 'Street Address', 'City', 'State', 'Zip', 
            'Mortgage or a lien (Condo?)', 'Sale Date', 'Amount Due', 'Redemption Period',
            'Attorney Name', 'Attorney Address', 'Attorney phone number', 'Attorney File #',
            'First date published in Legal News', 'Last Date Published in Legal News',
            'Lender/Mortgage company\'s name', 'Recorded Date'
        ]
        
        with open(ai_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ai_fieldnames)
            writer.writeheader()
            for record in processed_records:
                # Create a new record with standardized field names
                standardized_record = {}
                
                # Handle Name field splitting if Name is present but First/Middle/Last are not
                if 'Name' in record and not ('First Name' in record and 'Last Name' in record):
                    name_parts = record['Name'].split()
                    if len(name_parts) == 1:
                        # Only one name part available
                        standardized_record['First Name'] = name_parts[0]
                        standardized_record['Middle Name'] = ""
                        standardized_record['Last Name'] = ""
                    elif len(name_parts) == 2:
                        # First and Last name
                        standardized_record['First Name'] = name_parts[0]
                        standardized_record['Middle Name'] = ""
                        standardized_record['Last Name'] = name_parts[1]
                    else:
                        # First, Middle (possibly multiple), and Last name
                        standardized_record['First Name'] = name_parts[0]
                        standardized_record['Last Name'] = name_parts[-1]
                        standardized_record['Middle Name'] = " ".join(name_parts[1:-1])
                
                # Handle Address to Street Address conversion
                if 'Address' in record and 'Street Address' not in record:
                    standardized_record['Street Address'] = record['Address']
                
                # Process all other fields
                for field in ai_fieldnames:
                    # Skip already handled fields
                    if field in ['First Name', 'Middle Name', 'Last Name'] and 'Name' in record:
                        continue
                    if field == 'Street Address' and 'Address' in record:
                        continue
                        
                    # Try different variations of field names
                    if field in record:
                        standardized_record[field] = record[field]
                    # Try with lowercase
                    elif field.lower() in {k.lower(): k for k in record}:
                        matching_key = {k.lower(): k for k in record}[field.lower()]
                        standardized_record[field] = record[matching_key]
                    # Handle special cases
                    elif field == 'Attorney phone number' and 'Attorney Phone Number' in record:
                        standardized_record[field] = record['Attorney Phone Number']
                    elif field == 'First date published in Legal News' and 'First Date Published in Legal News' in record:
                        standardized_record[field] = record['First Date Published in Legal News']
                    # Ensure all required fields have a value
                    elif field not in standardized_record:
                        standardized_record[field] = "N/A"
                
                writer.writerow(standardized_record)
        
        print(f"AI processing completed. Saved processed data to {ai_csv_filename}")
    
    except ImportError:
        print("Groq package not installed. Install it with: pip install groq")
    except Exception as e:
        print(f"Error during Groq processing: {str(e)}")
        print("Falling back to using direct API calls with requests...")
        process_with_requests(foreclosure_data, os.getenv("GROQ_API_KEY"))

    # Save the original data to CSV
    csv_filename = "foreclosures.csv"
    print(f"Saving original data to {csv_filename}...")
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['foreclosure_number', 'published_dates', 'address', 'name', 'description', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for foreclosure in all_foreclosures:
            writer.writerow(foreclosure)
    
else:
    print("Login failed!")
    print(f"Response text: {login_response.text[:500]}")  # Print first 500 chars of response



