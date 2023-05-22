import requests
from keysAndPasswords import tripadvisor_key

# https://tripadvisor-content-api.readme.io/reference/getlocationdetails


'''
url = "https://api.content.tripadvisor.com/api/v1/location/search?key={tripadvisor_key}&searchQuery=muzeum&category=attractions&latLong=50.0617%2C%2019.9367&radius=1000&radiusUnit=m&language=pl"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)

#"location_id": "2248956",
#"name": "Muzeum Krakowa - Rynek Podziemny"

'''
location_id = 2248956
# Muzeum Krakowa - Rynek Podziemny

url = f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details?key={tripadvisor_key}&language=pl&currency=PLN"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)


#https://www.tripadvisor.com/Attraction_Review-g274772-d276748-Reviews-Wawel_Royal_Castle-Krakow_Lesser_Poland_Province_Southern_Poland.html