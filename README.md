# Legal News Foreclosure Scraper

This script scrapes foreclosure notices from legalnews.com for Kent County. It utilizes session-based authentication and form submission to search for and collect foreclosure data.

## Features

- Login to legalnews.com using environment variables for credentials
- Search for foreclosure notices in Kent County within a specified date range
- Extract detailed information from each foreclosure notice
- Save results in both CSV and JSON formats

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory with your credentials:
   ```
   USER_NAME=your_email@example.com
   PASSWORD=your_password
   ```
3. Run the script:
   ```
   python requests-sessions.py
   ```

## Usage

When running the script, you will be prompted to enter:
- Start date for the search (MM/DD/YYYY format)
- End date for the search (MM/DD/YYYY format)

The script will then:
1. Log in to legalnews.com
2. Navigate to the Public Notices section
3. Search for foreclosures in Kent County within the specified date range
4. Scrape details from each foreclosure notice
5. Save the results to both CSV and JSON files

## Output

- `foreclosures.csv`: CSV file containing all scraped foreclosure data
- `foreclosures.json`: JSON file containing the same data in JSON format
- `search_response.html`: Debug file containing the HTML of the search results page 
- Automated login to LegalNews.com
- Search for foreclosure notices in Kent County
- Scrape foreclosure details including addresses, names, and descriptions
- Process data using Groq AI to extract structured information
- Export to JSON and CSV formats