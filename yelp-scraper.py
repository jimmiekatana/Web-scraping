import requests
import os
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Constants
YELP_API_KEY = 'Y8Yki4n0EU0b05SxATonb7tCfByRcZk78Dq_bTKz0ABR-1MtXV3BI3ry8mfyGMj0cjDYcjqtsBC0Opb8LmzL7Grn3Gct346twQoQasWEgiT0SlfHWWyXQ_ear4df3ZnYx'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1ZedCHIKgl0PzMZ2HLDoPX5zAV37lu7HdRjfXbZaoC6M'
RANGE_NAME = 'Sheet1!A1'

# Yelp API URL
YELP_API_URL = 'https://api.yelp.com/v3/businesses/search'

# Function to authenticate with Google Sheets API
def get_google_sheets_service():
    creds = None
    client_secret_file = 'client_secret.json'
    
    # Check if we already have valid credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no (or invalid) credentials, authorize user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('sheets', 'v4', credentials=creds)

# Function to search for businesses using Yelp API
def search_yelp(term, location, limit=10):
    headers = {
        'Authorization': f'Bearer {YELP_API_KEY}'
    }
    
    params = {
        'term': term,
        'location': location,
        'limit': limit
    }
    
    response = requests.get(YELP_API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# Function to format Yelp data for the Google Sheets
def format_yelp_data(yelp_response):
    businesses = yelp_response.get('businesses', [])
    formatted_data = []

    for biz in businesses:
        row = [
            biz.get('name', ''),
            ', '.join(biz['location'].get('display_address', [])),
            biz.get('display_phone', ''),
            biz.get('url', ''),
            biz.get('rating', ''),
            biz.get('review_count', ''),
            biz.get('alias', ''),  # Business description
            'Hours not available',  # Business hours (requires additional API call, not included in this script)
            'Email not available',  # Yelp API doesn't provide email
            ', '.join([cat['title'] for cat in biz.get('categories', [])]),
            'Service area not available',  # Not in Yelp API
            'Year not available',  # Yelp API doesn't provide opening year
            ', '.join(biz.get('photos', [])),  # Yelp API provides up to 3 photos
            'Payment method not available',  # Not in Yelp API
            'Owner not available',  # Not in Yelp API
            'Fax not available',  # Not in Yelp API
            'Alternate phone not available',  # Not in Yelp API
            'Products/services not available',  # Not in Yelp API
            'Company size not available',  # Not in Yelp API
            biz.get('review_count', ''),
            'Facebook not available',  # Not in Yelp API
            'Twitter not available',  # Not in Yelp API
            'Instagram not available',  # Not in Yelp API
            'Youtube not available',  # Not in Yelp API
            'Linkedin not available'  # Not in Yelp API
        ]
        formatted_data.append(row)

    return formatted_data

# Function to update Google Sheets with the formatted Yelp data
def update_google_sheet(service, data):
    sheet = service.spreadsheets()

    # Create the header for the new spreadsheet format
    header = [
        'Name', 'Address', 'Phone Number', 'Website URL', 'Rating', 'Number of reviews',
        'Business Description', 'Business Hours', 'Business Email', 'Business Categories',
        'Service Area', 'Business Opening Year', 'Business Photos(1 to 10)', 'Payment Method',
        'Owner Name', 'Fax Number', 'Alternate Phone Numbers', 'Products and Services',
        'Company Size', 'No. of reviews', 'Facebook Link', 'Twitter Link', 'Instagram Link',
        'Youtube Link', 'Linkedin Link'
    ]

    values = [header] + data

    # Update Google Sheets with the formatted data
    body = {'values': values}
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()
    
    print(f"{result.get('updatedCells')} cells updated.")

def main():
    service = get_google_sheets_service()

    # Search Yelp for businesses (example: Carpet Cleaning in Los Angeles)
    term = 'Carpet Cleaning'
    location = 'Los Angeles, CA'
    
    yelp_response = search_yelp(term, location)
    
    if yelp_response:
        # Format the data
        formatted_data = format_yelp_data(yelp_response)
        
        # Update Google Sheets with the formatted business data
        update_google_sheet(service, formatted_data)

if __name__ == "__main__":
    main()
