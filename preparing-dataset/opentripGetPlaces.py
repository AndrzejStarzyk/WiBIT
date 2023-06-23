import requests
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from keysAndPasswords import opentripmap_key, mongodb_password


base_url = 'https://api.opentripmap.com/0.1/en/'


def splitToPieces(n: int, rng: tuple):
    stop = rng[1]
    start = rng[0]
    rng_length = stop - start
    step = rng_length / n
    curr = start

    results = [start]

    for i in range(n):
        curr += step
        results.append(curr)

    return results


def getPlcaesUrl(lon, lat, form='json') -> str:
    kind = 'interesting_places'
    places_url = f"{base_url}places/bbox?lon_min={str(lon[0])}&lon_max={str(lon[1])}&lat_min={str(lat[0])}&lat_max={str(lat[1])}" \
                 f"&kinds={kind}&format={form}&apikey={opentripmap_key}"

    return places_url


def getDetailsUrl(xid) -> str:
    details_url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}?apikey={opentripmap_key}"
    return details_url


def apiRequest(url: str) -> dict:
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    return response_dict


def splitGrid(lon_range, lat_range, pieces: int = 2):
    lon_ranges = splitToPieces(pieces, lon_range)
    lat_ranges = splitToPieces(pieces, lat_range)

    print(lat_ranges)
    print(lon_ranges)

    map_grid = []

    for i in range(pieces):
        lon_piece = (lon_ranges[i], lon_ranges[i + 1])
        for j in range(pieces):
            lat_piece = (lat_ranges[j], lat_ranges[j + 1])
            num_url = getPlcaesUrl(lon_piece, lat_piece, 'count')
            print(num_url)
            num = apiRequest(num_url)['count']
            map_grid.append({'lon': lon_piece,
                             'lat': lat_piece,
                             'count': num})

    for part in map_grid:
        if part['count'] > 500:
            elm = part
            map_grid.remove(part)
            new_grid = splitGrid(elm['lon'], elm['lat'])
            map_grid += new_grid

    return map_grid


def getGrid():
    lon = (19.80, 20.25)
    lat = (49.97, 50.12)
    grid = splitGrid(lon, lat, 4)

    total = 0
    for row in grid:
        print(row)
        total += row['count']

    print(total)

    file_path = "jsons/grid.json"
    with open(file_path, "w") as json_file:
        json.dump(grid, json_file)


def saveAllXIDs():
    grid_file = "jsons/grid.json"
    with open(grid_file, "r") as json_file:
        grid = json.load(json_file)

    xids = []
    for piece in grid:
        url = getPlcaesUrl(piece['lon'], piece['lat'])
        places = apiRequest(url)
        for place in places:
            xid = place['xid']
            if xid not in xids:
                xids.append(place['xid'])

    print(len(xids))

    xids_file = "jsons/xids.json"
    with open(xids_file, "w") as json_file:
        json.dump(xids, json_file)


def getMongoDbCollection():
    uri = f"mongodb+srv://mikolaj:{mongodb_password}@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client["wibit"]
    collection = db["cracow-attractions"]

    return collection


def getDetails(start_idx: int = 0, stop_idx: int = -1):
    collection = getMongoDbCollection()

    xids_path = "jsons/xids.json"
    with open(xids_path, "r") as xids_file:
        xids_json = json.load(xids_file)

    xids = xids_json[start_idx: stop_idx]
    print(xids)
    print(len(xids))

    places_details_path = f'jsons/details/places_{start_idx}_{start_idx+len(xids)}.json'
    places_details = []
    for xid in xids:
        url = getDetailsUrl(xid)
        single_place = apiRequest(url)
        places_details.append(single_place)

    # result = collection.insert_many(places_details)
    # print(result.inserted_ids)

    with open(places_details_path, "w") as places_details_file:
        json.dump(places_details, places_details_file)


# getDetails()

