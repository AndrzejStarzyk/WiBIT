from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from pymongo.server_api import ServerApi
from models.constants import MONGODB_LOGIN, MONGODB_PASSWORD


class MongoUtils:
    def __init__(self):
        self.mongo_client = None
        self.mongo_database = None
        self.mongo_database_attractions = None

    def get_db(self):
        if self.mongo_client is None:
            self.connect_to_db()
        if self.mongo_database is None:
            self.mongo_database = self.mongo_client["wibit"]
        return self.mongo_database

    def get_db_attractions(self):
        if self.mongo_client is None:
            self.connect_to_db()
        if self.mongo_database_attractions is None:
            self.mongo_database_attractions = self.mongo_client["wibit_attractions"]
        return self.mongo_database_attractions

    def get_client(self):
        if self.mongo_client is None:
            self.connect_to_db()

        return self.mongo_client

    def connect_to_db(self):
        uri = f"mongodb+srv://{MONGODB_LOGIN}:{MONGODB_PASSWORD}@wibit.4d0e5vs.mongodb.net/?retryWrites=true&w=majority"

        self.mongo_client = MongoClient(uri, server_api=ServerApi('1'))

        try:
            self.mongo_client.admin.command('ping')
        except Exception as e:
            print(f"EXCEPTION while connecting mongodb atlas: {e}")

    def get_collection(self, collection_name):
        self.get_db()
        try:
            self.mongo_database.create_collection(collection_name)
        except CollectionInvalid:
            print(f"Collection {collection_name} already exists.")
        else:
            print(f"Collection {collection_name} created.")

        collection = self.mongo_database[collection_name]
        return collection

    def get_collection_attractions(self, collection_name):
        self.get_db_attractions()
        try:
            self.mongo_database_attractions.create_collection(collection_name)
        except CollectionInvalid:
            print(f"Collection {collection_name} already exists.")
        else:
            print(f"Collection {collection_name} created.")

        collection = self.mongo_database_attractions[collection_name]
        return collection


mu = MongoUtils()
mu.connect_to_db()
