import os
import requests as r
import sys
import time
import ujson as json

from met_office.met_office_classes import *
from met_office.mock import MockResponse
from met_office.wifi import connect_to_wifi


os.chdir('met_office')
secrets_file: str = '.secrets.json'
with open(secrets_file) as f:
    secrets = f.read()
secrets_json: dict = json.loads(secrets)

api_key: str | None = secrets_json['api_key']
if not api_key or api_key is None:
    raise AttributeError('api_key environment variable must be defined')

latitude = 51.821400
longitude = 1.282080

frequency = "hourly"

connect_to_wifi()

url = f'https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/{frequency}?latitude={latitude}&longitude={longitude}'
headers = {'apikey': api_key, 'accept': 'application/json'}

filename = 'data.json'

print(f"Getting {frequency} forecast from the Met Office...")

use_mock: bool = True

if use_mock:
    resp = MockResponse()
else:
    resp = r.get(url, headers=headers)

status_code = resp.status_code
text = resp.text
# print(text)

# If data download failed, exit progam
if status_code != 200:
    print(f"Failed to get data! Response returned status code {status_code}")
    sys.exit(1)

print(f'\nSuccessfully got {"mock " if use_mock else ""}data!\n')

# Write downloaded data to a JSON file
data = resp.text
data_dict = json.loads(data)
# print(f'data type: {type(data)}')
# print(f'data_dict type: {type(data_dict)}')

keys = list(data_dict.keys())
print(f'keys: {keys}')
print(f'Number of features: {len(data_dict['features'])}')

f = open(filename, 'w')
f.write(data)
f.close()

print(f"\nSaved forecast data to {filename}")

print(f'\nFiles now on drive: {os.listdir()}')
