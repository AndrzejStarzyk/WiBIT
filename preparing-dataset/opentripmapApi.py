import requests
import json
from keysAndPasswords import opentripmap_key

# https://opentripmap.io/docs

base_url = 'https://api.opentripmap.com/0.1/en/'

city = 'Cracow'
url = f"https://api.opentripmap.com/0.1/en/places/geoname?name={city}&apikey={opentripmap_key}"
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

response_dict = json.loads(response.text)
print(response_dict)

radius = 3000
limit = 500  # this is maximum
url = f"https://api.opentripmap.com/0.1/en/places/radius?radius={str(radius)}" \
      f"&lon={response_dict['lon']}&lat={response_dict['lat']}&format=json&limit={limit}&apikey={opentripmap_key}"

places_response = requests.get(url, headers=headers)
places_dict = json.loads(places_response.text)
print("Found places: ", len(places_dict))
print(places_dict[0])


xid = places_dict[0]['xid']
url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}?apikey={opentripmap_key}"

details_response = requests.get(url, headers=headers)
details_dict = json.loads(details_response.text)
print(details_dict)


