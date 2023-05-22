from opentripGetPlaces import getMongoDbCollection
import json

#https://opentripmap.io/catalog


def getAllPlaces():
    collection = getMongoDbCollection()
    result = collection.find()
    return result


def existedCategories() -> set:
    places = getAllPlaces()
    categories = set()

    for place in places:
        kinds_str = place['kinds']
        kinds_arr = kinds_str.split(',')
        categories.update(kinds_arr)

    return categories


def getMainCategories(only_in_db = True):
    catalog_path = "jsons/catalog_en.json"
    with open(catalog_path, "r", encoding="utf-8") as catalog_file:
        categories = json.load(catalog_file)

    categories = categories["children"][0]["children"]

    categories_at_level = []
    for category in categories:
        categories_at_level.append(category["name"])

    if only_in_db:
        existed_categories = existedCategories()

        for category in categories_at_level:
            if category not in existed_categories:
                categories_at_level.remove(category)

    return categories_at_level


def thirdLevelCategories(only_in_db= True):
    main_categories = getMainCategories(only_in_db)

    catalog_path = "jsons/catalog_en.json"
    with open(catalog_path, "r", encoding="utf-8") as catalog_file:
        categories = json.load(catalog_file)

    categories = categories["children"][0]["children"]

    result = []

    for m_category in categories:
        if m_category["name"] in main_categories:
            child_categories = m_category["children"]
            for ch_category in child_categories:
                result.append(ch_category["name"])

    if only_in_db:
        existed_categories = existedCategories()
        for category in result:
            if category not in existed_categories:
                result.remove(category)

    print(result)
    return result


print(len(thirdLevelCategories(True)))
