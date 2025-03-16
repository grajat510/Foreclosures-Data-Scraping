# Legal News Foreclosure Scraper

This script scrapes foreclosure notices from legalnews.com for any county in Michigan. It utilizes session-based authentication and form submission to search for and collect foreclosure data.

## Features

- Login to legalnews.com using environment variables for credentials
- Search for foreclosure notices in any Michigan county within a specified date range
- Interactive county selection from a complete list of Michigan counties
- Extract detailed information from each foreclosure notice
- Save results in both CSV and JSON formats
- Process data using Groq AI to extract structured information

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory with your credentials:
   ```
   USER_NAME=your_email@example.com
   PASSWORD=your_password
   GROQ_API_KEY=your_groq_api_key  # For AI data processing
   ```

3. Run the script:
   ```
   python requests-sessions.py
   ```

## Usage

When running the script, you will be prompted to:
1. Select a county from the displayed list (1-84)
2. Enter start date for the search (MM/DD/YYYY format)
3. Enter end date for the search (MM/DD/YYYY format)

The script will then:
1. Log in to legalnews.com
2. Navigate to the Public Notices section
3. Search for foreclosures in the selected county within the specified date range
4. Scrape details from each foreclosure notice
5. Process the data using Groq AI to extract structured information
6. Save the results to both CSV and JSON files

## Available Counties

The script will display a numbered list of available counties when run. For reference, here's the complete list:

1. All Counties
2. Alcona
3. Alger
4. Allegan
5. Alpena
6. Antrim
7. Arenac
8. Baraga
9. Barry
10. Bay
11. Benzie
12. Berrien
13. Branch
14. Calhoun
15. Cass
16. Charlevoix
17. Cheboygan
18. Chippewa
19. Clare
20. Clinton
21. Crawford
22. Delta
23. Dickinson
24. Eaton
25. Emmet
26. Genesee
27. Gladwin
28. Gogebic
29. Grand Traverse
30. Gratiot
31. Hillsdale
32. Houghton
33. Huron
34. Ingham
35. Ionia
36. Iosco
37. Iron
38. Isabella
39. Jackson
40. Kalamazoo
41. Kalkaska
42. Kent
43. Keweenaw
44. Lake
45. Lapeer
46. Leelanau
47. Lenawee
48. Livingston
49. Luce
50. Mackinac
51. Macomb
52. Manistee
53. Marquette
54. Mason
55. Mecosta
56. Menominee
57. Midland
58. Missaukee
59. Monroe
60. Montcalm
61. Montmorency
62. Muskegon
63. Newaygo
64. Oakland
65. Oceana
66. Ogemaw
67. Ontonagon
68. Osceola
69. Oscoda
70. Otsego
71. Ottawa
72. Presque Isle
73. Roscommon
74. Saginaw
75. Saint Clair
76. Saint Joseph
77. Sanilac
78. Schoolcraft
79. Shiawassee
80. Tuscola
81. Van Buren
82. Washtenaw
83. Wayne
84. Wexford

## Output

- `foreclosures.csv`: CSV file containing all scraped foreclosure data with basic fields
- `foreclosures_processed.csv`: CSV file containing AI-processed structured data with detailed fields
- `foreclosures.json`: JSON file containing all foreclosure data
- `search_response.html`: Debug file containing the HTML of the search results page

## Notes

- When searching with "All Counties" option, be aware that results may be very large for wide date ranges
- For best results, use date ranges in the past where foreclosure notices would have been published
- The script includes debugging information to help troubleshoot any issues