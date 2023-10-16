import requests
import json


# https://opentripmap.io/docs

class OpenTripMapApiProvider:
    def __init__(self):
        self.places = []
        self.places_fetched = False
        self.opentripmap_key = '5ae2e3f221c38a28845f05b6b5e25b81a769f0d40d1323e54cf91bac'
        self.base_url = 'https://api.opentripmap.com/0.1/en/'
        self.city = 'Cracow'

    def fetch_places(self):
        url = f"https://api.opentripmap.com/0.1/en/places/geoname?name={self.city}&apikey={self.opentripmap_key}"
        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)

        response_dict = json.loads(response.text)

        radius = 3000
        limit = 500  # this is maximum
        url = f"https://api.opentripmap.com/0.1/en/places/radius?radius={str(radius)}" \
              f"&lon={response_dict['lon']}&lat={response_dict['lat']}&format=json&limit={limit}&apikey={self.opentripmap_key}"

        places_response = requests.get(url, headers=headers)
        self.places = json.loads(places_response.text)
        self.places_fetched = True

    def get_places(self):
        if not self.places_fetched:
            self.fetch_places()
        return self.places


if __name__ == "__main__":
    pass
