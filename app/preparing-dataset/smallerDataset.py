from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import CollectionInvalid
import googlemaps
from keysAndPasswords import mongodb_password, mongodb_user, gmaps_key


def connectMongoDb():
    uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client["wibit"]
    return db


def getMongoDbCollection(collection_name: str, db):
    try:
        db.create_collection(collection_name)
    except CollectionInvalid:
        print(f"Collection {collection_name} already exists.")
    else:
        print(f"Collection {collection_name} created.")

    collection = db[collection_name]
    return collection


def countReviewsForPlace(place_name: str) -> (int, object):
    input_text = f"{place_name}, Kraków"
    try:
        gmaps = googlemaps.Client(key=gmaps_key)

        result = gmaps.find_place(
            input=input_text,
            input_type='textquery',
            fields=['place_id']
        )

    except:
        print("ERROR! ", place_name)
        return 0, None

    if len(result['candidates']) == 0:
        return 0, None

    place_id = result['candidates'][0]['place_id']
    place_details = gmaps.place(place_id=place_id, fields=['name', 'rating', 'user_ratings_total', 'opening_hours'])

    reviews_count = place_details['result'].get('user_ratings_total', 0)
    opening_hours_exist = 'opening_hours' in place_details['result']

    if not opening_hours_exist:
        return -reviews_count, None

    return reviews_count, place_details['result']['opening_hours']['periods']


def saveOnlyPopularPlaces():
    database = connectMongoDb()
    old_collection = getMongoDbCollection("cracow-attractions", database)
    new_collection = getMongoDbCollection("cracow-attractions-popular", database)

    popular_places = []

    all_places = old_collection.find({})

    for place in all_places:
        reviews_number, opening_hours = countReviewsForPlace(place['name'])
        if reviews_number > 100:
            print(place['rate'], " ----> ", place['name'], " : ", reviews_number)
            place['opening_hours'] = opening_hours
            place['gmaps_reviews'] = reviews_number
            popular_places.append(place)

    print(' |||| TOTAL Number of places: ', len(popular_places))
    new_collection.insert_many(popular_places)


def removePlacesWithSameName():
    database = connectMongoDb()
    collection = getMongoDbCollection("cracow-attractions-popular", database)
    all_places = collection.find({})

    for place in all_places:
        query = {'name': place['name']}
        same_name_places = collection.find(query)
        if len(list(same_name_places)) > 1:
            collection.delete_many(query)


def splitCategories():
    database = connectMongoDb()
    collection = getMongoDbCollection("cracow-attractions-popular", database)
    all_places = collection.find({})

    for place in all_places:
        place['kinds'] = place['kinds'].split(',')
        collection.replace_one({'_id': place['_id']}, place, upsert=True)


def findUnclassified():
    database = connectMongoDb()
    collection = getMongoDbCollection("cracow-attractions-popular", database)
    all_places = collection.find({})

    for place in all_places:
        if 'unclassified_objects' in place['kinds']:
            print(place['name'])


def deleteStrangePlaces():
    database = connectMongoDb()
    collection = getMongoDbCollection("cracow-attractions-popular", database)
    names_to_delete = ["Mundżaki chińskie",
                       "Tapiry i strusie nandu",
                       "Zebry Chapmana",
                       "Małpy",
                       "Egzotarium",
                       "Kondory",
                       "Żyrafy",
                       "Żurawie mandżurskie",
                       "Daniele, jelenie Barasinga",
                       "Nocny pawilon",
                       "Flamingi",
                       "Pazurzatki",
                       "Kangury, strusie emu",
                       "Liban quarry",
                       "shooting academy",
                       "Lem's maze",
                       "optics",
                       "Magnetism",
                       "Mechanics",
                       "trampoliny",
                       "gyroscope",
                       "SEPECAT Jaguar",
                       "Balon",
                       "Locked Up",
                       "PKO Bank Polski,"
                       "Nóż"]

    for name in names_to_delete:
        collection.delete_one({"name": name})


deleteStrangePlaces()
