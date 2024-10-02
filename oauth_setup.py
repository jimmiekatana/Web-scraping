import requests
import time
import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Yelp API constants
API_KEY = '8Yki4n0EU0b05SxATonb7tCfByRcZk78Dq_bTKz0ABR-1MtXV3BI3ry8mfyGMj0cjDYcjqtsBC0Opb8LmzL7Grn3Gct346twQoQasWEgiT0SlfHWWyXQ_ear4df3ZnYx'
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'
SEARCH_LIMIT = 10

# Google Sheets API constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1ZedCHIKgl0PzMZ2HLDoPX5zAV37lu7HdRjfXbZaoC6M'
RANGE_NAME = 'Sheet1!A1'  # Adjust as needed

def get_google_sheets_service():
    creds = None
    client_secret_file = 'C:/Users/dell/Data Scraping/client_secret.json'
    
    if not os.path.exists(client_secret_file):
        raise FileNotFoundError(f"The file {client_secret_file} was not found.")

    try:
        with open(client_secret_file, 'r') as f:
            client_config = json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"The file {client_secret_file} is not a valid JSON file.")

    if 'installed' not in client_config and 'web' not in client_config:
        raise ValueError("The client secret file is not in the correct format.")

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        except Exception as e:
            print(f"An error occurred while setting up the OAuth flow: {str(e)}")
            raise

    try:
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"An error occurred while building the Google Sheets service: {str(e)}")
        raise

def yelp_request(host, path, api_key, url_params=None, max_retries=3):
    url_params = url_params or {}
    url = f'{host}{path}'
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    for attempt in range(max_retries):
        try:
            response = requests.request('GET', url, headers=headers, params=url_params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Too Many Requests
                print(f"Rate limit reached. Waiting before retry. Attempt {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Error {response.status_code}: {response.text}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying... Attempt {attempt + 2}/{max_retries}")
                time.sleep(2 ** attempt)
            else:
                print("Max retries reached. Giving up.")
                break
    return {"error": {"code": "MAX_RETRIES_REACHED", "description": "Max retries reached without successful response"}}

def search(api_key, location):
    url_params = {
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    response = yelp_request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)
    print(f"Yelp API Response for {location}: {json.dumps(response, indent=2)}")
    return response

def get_business(api_key, business_id):
    business_path = BUSINESS_PATH + business_id
    return yelp_request(API_HOST, business_path, api_key)

def main():
    locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL']  # Add more locations as needed
    
    try:
        sheets_service = get_google_sheets_service()
        sheet = sheets_service.spreadsheets()

        # Prepare the header row
        header = ['Name', 'Address', 'Phone Number', 'Website URL', 'Rating', 'Number of reviews', 
                  'Business Description', 'Business Hours', 'Business Categories', 'Service Area']
        values = [header]

        for location in locations:
            print(f"Searching in {location}")
            response = search(API_KEY, location)
            businesses = response.get('businesses')

            if not businesses:
                print(f"No businesses found in {location}. Full response: {json.dumps(response, indent=2)}")
                continue

            for business in businesses:
                business_id = business['id']
                print(f"Fetching details for {business['name']}")
                
                business_details = get_business(API_KEY, business_id)
                
                if 'error' in business_details:
                    print(f"Error fetching details for {business['name']}: {business_details['error']}")
                    continue

                row = [
                    business_details.get('name'),
                    ', '.join(business_details.get('location', {}).get('display_address', [])),
                    business_details.get('phone'),
                    business_details.get('url'),
                    str(business_details.get('rating')),
                    str(business_details.get('review_count')),
                    '',  # Business Description (not available in API)
                    str(business_details.get('hours', [])),
                    ', '.join([category['title'] for category in business_details.get('categories', [])]),
                    business_details.get('service_area', {}).get('name', '')
                ]
                values.append(row)
                
                time.sleep(1)  # To avoid hitting rate limits

        # Update Google Sheet
        body = {'values': values}
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
            valueInputOption='USER_ENTERED', body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()