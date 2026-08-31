import network
import os
import sys
import time
import ujson
import requests as r

from met_office_classes import *
from mock import MockResponse


def connect_to_wifi() -> None:
    ssid = 'Yφ'
    password = '03j23@PPMwz'

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 10
    print('Connecting to Wi-Fi...')
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('\t- Waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('Connected to Wi-Fi\n')


apikey = "eyJ4NXQjUzI1NiI6Ik5XVTVZakUxTkRjeVl6a3hZbUl4TkdSaFpqSmpOV1l6T1dGaE9XWXpNMk0yTWpRek5USm1OVEE0TXpOaU9EaG1NVFJqWVdNellXUm1ZalUyTTJJeVpBPT0iLCJraWQiOiJnYXRld2F5X2NlcnRpZmljYXRlX2FsaWFzIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYifQ==.eyJzdWIiOiJ3ZWFzZG93bjk5QGdtYWlsLmNvbUBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6IndlYXNkb3duOTlAZ21haWwuY29tIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJzaXRlX3NwZWNpZmljLWJkYzYyZDRhLWRhZDAtNDA3ZS04NjIxLWM2Mjg4N2JjMDVmOSIsImlkIjo2MDM1MSwidXVpZCI6IjJhMjcyYWNiLTczMzQtNDQ4Ny04ZWEwLTQ0NzM0YmVhZDRiOSJ9LCJpc3MiOiJodHRwczpcL1wvYXBpLW1hbmFnZXIuYXBpLW1hbmFnZW1lbnQubWV0b2ZmaWNlLmNsb3VkOjQ0M1wvb2F1dGgyXC90b2tlbiIsInRpZXJJbmZvIjp7IndkaF9zaXRlX3NwZWNpZmljX2ZyZWUiOnsidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsImdyYXBoUUxNYXhDb21wbGV4aXR5IjowLCJncmFwaFFMTWF4RGVwdGgiOjAsInN0b3BPblF1b3RhUmVhY2giOnRydWUsInNwaWtlQXJyZXN0TGltaXQiOjAsInNwaWtlQXJyZXN0VW5pdCI6InNlYyJ9fSwia2V5dHlwZSI6IlBST0RVQ1RJT04iLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJTaXRlU3BlY2lmaWNGb3JlY2FzdCIsImNvbnRleHQiOiJcL3NpdGVzcGVjaWZpY1wvdjAiLCJwdWJsaXNoZXIiOiJKYWd1YXJfQ0kiLCJ2ZXJzaW9uIjoidjAiLCJzdWJzY3JpcHRpb25UaWVyIjoid2RoX3NpdGVfc3BlY2lmaWNfZnJlZSJ9XSwidG9rZW5fdHlwZSI6ImFwaUtleSIsImlhdCI6MTc4NzYwNzQ2MSwianRpIjoiNDI1NzhjNjQtYWM1YS00NGM5LWJhOTctNTc4ZWI2NzNjN2YwIn0=.Z7A5YE3zMgcjzXg4XMWid29HLRTlo1mKDE_yKQnY4dGD61hGST9kBWj7CQZ__yu7TyAKThsP9Up5OpMhUBsoSlS88tNc4F6dqOEl7jYg9nK9FOi3-79QpZreeVNAAPBImsOf9fMxFW7MSl7Co9lxJa4xEuJ5mXxtSpN865NwDs0DLmsKAOUduFNgvF3giB-wseHNikVAo9CuAG_aQMlO-dFmdAugqm6o1ydCJtGF_xVXTslcSSBlK82XWQNTnopkM412oUoeHi_Ys3nLRhS9eyWgH29S3Wkgfk1duUrFO4Lo-PEjCQv7aEjB6jqrz-JBCc1HGS3-DgrltdvzHo9CUg=="

latitude = 51.821400
longitude = 1.282080

frequency = "hourly"

connect_to_wifi()

url = f"https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/{frequency}?latitude={latitude}&longitude={longitude}"
headers = {"apikey": apikey, "accept": "application/json"}

filename = "data.json"

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
data_dict = ujson.loads(data)
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
