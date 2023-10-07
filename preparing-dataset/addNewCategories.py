from opentripGetPlaces import getPlcaesUrl, getDetailsUrl, apiRequest
from smallerDataset import connectMongoDb, getMongoDbCollection, countReviewsForPlace


def otherCategories(categories_list: list[str]):
    lon = (19.80, 20.25)
    lat = (49.97, 50.12)

    xids = set()

    for category in categories_list:
        url = getPlcaesUrl(lon, lat, category)
        places = apiRequest(url)
        for place in places:
            xid = place['xid']
            if xid not in xids:
                xids.add(place['xid'])

    return xids


def saveOtherCategories(save=False):
    amusements_cats = ['amusement_parks', 'ferris_wheels', 'water_parks', 'miniature_parks', 'baths_and_saunas']
    sport_cats = ['climbing', 'stadiums', 'winter_sports']

    xids = otherCategories(amusements_cats)
    xids.update(otherCategories(sport_cats))

    print('New attractions number:', len(xids))

    popular_places = []

    for xid in xids:
        url = getDetailsUrl(xid)
        place = apiRequest(url)
        kinds_str = place['kinds']
        place['kinds'] = kinds_str.split(',')
        name = place['name']
        reviews_number, opening_hours = countReviewsForPlace(name)

        print(place['rate'], " ----> ", place['name'], " : ", reviews_number)

        if reviews_number > 100:
            place['opening_hours'] = opening_hours
            place['gmaps_reviews'] = reviews_number
            popular_places.append(place)

    print("Popular num: ", len(popular_places))

    if save:
        db = connectMongoDb()
        collection = getMongoDbCollection("cracow-new-attractions", db)
        collection.insert_many(popular_places)


saveOtherCategories()
