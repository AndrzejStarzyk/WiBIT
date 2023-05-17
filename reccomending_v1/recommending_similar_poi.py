
import opentripmaps_categories as cat
import opentripmap_api as api

if __name__ == "__main__":
    categories = cat.get_categories()
    places = api.get_places()

    data_dict = {
        "category": [],
        "place": []}

