import requests
import json


# https://opentripmap.io/docs

def get_places():
    opentripmap_key = ''

    base_url = 'https://api.opentripmap.com/0.1/en/'

    city = 'Cracow'
    url = f"https://api.opentripmap.com/0.1/en/places/geoname?name={city}&apikey={opentripmap_key}"
    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)

    response_dict = json.loads(response.text)

    radius = 3000
    limit = 500  # this is maximum
    url = f"https://api.opentripmap.com/0.1/en/places/radius?radius={str(radius)}" \
          f"&lon={response_dict['lon']}&lat={response_dict['lat']}&format=json&limit={limit}&apikey={opentripmap_key}"

    places_response = requests.get(url, headers=headers)
    places_dict = json.loads(places_response.text)

    xid = places_dict[0]['xid']
    url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}?apikey={opentripmap_key}"

    details_response = requests.get(url, headers=headers)
    details_dict = json.loads(details_response.text)
    return places_dict
