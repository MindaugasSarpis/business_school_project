# filepath: /Users/kiprasd/Desktop/StravaProject/Scripts/exchange_token.py
import requests
import json

CLIENT_ID = '141936'
CLIENT_SECRET = 'adce8f2660284a3f44d23e593abedf15b5a84ce4'
AUTHORIZATION_CODE = '35a58324e16094536bbca24b849a689c56a50b0e'  # Replace if needed

response = requests.post(
    url='https://www.strava.com/api/v3/oauth/token',
    data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': AUTHORIZATION_CODE,
        'grant_type': 'authorization_code'
    }
)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(json.dumps(response.json(), indent=4))
else:
    print(json.dumps(response.json(), indent=4))