import googlemaps
import json
from keysAndPasswords import gmaps_key

# https://github.com/googlemaps/google-maps-services-python
# https://developers.google.com/maps/documentation/places/web-service/overview?hl=en

my_key = gmaps_key
gmaps = googlemaps.Client(key=my_key)

location = (50.0617, 19.9367)
language = "pl-PL"
region = "PL"
radius = 1000

cracow_places = gmaps.places(
            'museum',
            location=location,
            radius=radius,
            region=region,
            language=language,
            type="point_of_interest")

json_formatted_places = json.dumps(cracow_places, indent=2, ensure_ascii=False)

print(json_formatted_places)
for place in cracow_places["results"]:
    print(place["name"])

print("_________________________________________________________")


cracow_places_nearby = gmaps.places_nearby(
            location=location,
            keyword="museum",
            language=language,
            rank_by="distance")

json_formatted_places_nearby = json.dumps(cracow_places_nearby, indent=2, ensure_ascii=False)

#print(json_formatted_places_nearby)
for place in cracow_places_nearby["results"]:
    print(place["name"], " ---> ", place["place_id"])


single_place_details = gmaps.place(
            "ChIJ3Q97Bw5bFkcRjr9Px9GS8L8",
            language=language,
            reviews_no_translations=True,
            reviews_sort="newest"
        )


json_formatted_details = json.dumps(single_place_details, indent=2, ensure_ascii=False)
print(json_formatted_details)