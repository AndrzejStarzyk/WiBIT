from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class OpenTripMapDbProvider:
    def __init__(self):
        self.places = []
        self.places_fetched = False
        self.uri = f"mongodb+srv://andrzej:passwordas@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"
        self.collection = None

    def fetch_places(self):
        client = MongoClient(self.uri, server_api=ServerApi('1'))

        try:
            client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        db = client["wibit"]
        collection = db["cracow-attractions"]
        self.places = collection.find()

        self.places_fetched = True

    def get_places(self):
        if not self.places_fetched:
            self.fetch_places()
        return self.places


if __name__ == "__main__":
    provider = OpenTripMapDbProvider()
    print(provider.get_places()[0])
